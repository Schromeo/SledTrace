import assert from "node:assert/strict";
import test from "node:test";
import { parsePairEvidence, comparePair, measurePairRun, isPairTraceDetail, PAIR_FILE_LIMIT } from "../src/utils/pairComparison.ts";
import { buildUsageLedger } from "../src/utils/usage.ts";
import { estimateOpenAITextCost } from "../src/utils/pricing.ts";
import { getTraceDurationMs } from "../src/utils/timing.ts";

function evidence() {
  const run = { traceId: "before", caseId: "case-1", inputRef: "input-1", controlConfigRef: "control-1",
    criteriaVersion: "criteria-v1", appVersion: "before-v1", qualityStatus: "passed", qualityEvidenceRef: "assessment-before" };
  return { schemaVersion: 1, kind: "sledtrace-pair-evidence", provenance: "user_declared", interventionId: "fix-1",
    baseline: run, candidate: { ...run, traceId: "after", appVersion: "after-v1", qualityEvidenceRef: "assessment-after" } };
}
function call(overrides = {}) {
  return { span_id: "llm-1", trace_id: "before", type: "llm", status: "error", name: "attempt", input: { model: "gpt-4.1-mini" }, output: {},
    metadata: { usage_source: "openai_responses", input_tokens: 10, output_tokens: 5, total_tokens: 15,
      cached_input_tokens: 0, cache_write_tokens: 0, reasoning_output_tokens: 0 }, ...overrides };
}
function measure(spans = [call()], duration = 0) {
  const ledger = buildUsageLedger(spans);
  return measurePairRun(ledger, ledger.calls.map(c => estimateOpenAITextCost(c)), duration);
}
test("exact versioned declaration accepts explicit unknowns and manual assessment refs", () => {
  assert.deepEqual(parsePairEvidence(JSON.stringify(evidence())), evidence());
  const b = evidence();
  for (const key of ["caseId", "inputRef", "controlConfigRef", "criteriaVersion", "appVersion"]) b.baseline[key] = null;
  b.baseline.qualityStatus = "not_evaluated"; b.baseline.qualityEvidenceRef = null;
  assert.deepEqual(parsePairEvidence(JSON.stringify(b)), b);
});
test("bad shape, type, version, provenance, quality combinations and self-pair are rejected", () => {
  for (const change of [b => b.schemaVersion = 2, b => b.provenance = "source_verified", b => b.extra = 1,
    b => delete b.baseline.inputRef, b => b.baseline.inputRef = [], b => b.baseline.appVersion = true,
    b => b.baseline.qualityStatus = "approved", b => b.baseline.qualityEvidenceRef = null,
    b => { b.baseline.qualityStatus = "not_evaluated"; }, b => b.candidate.traceId = b.baseline.traceId,
    b => b.candidate.extra = "private-output"]) {
    const b = evidence(); change(b); assert.throws(() => parsePairEvidence(JSON.stringify(b)));
  }
  for (const bad of ["", "null", "[]", "{", "true"]) assert.throws(() => parsePairEvidence(bad));
});
test("bounded UTF-8 file and opaque references reject paths used as content or secret text", () => {
  assert.throws(() => parsePairEvidence(" ".repeat(PAIR_FILE_LIMIT + 1)), /16 KiB/);
  assert.throws(() => parsePairEvidence('"' + "中".repeat(6000) + '"'), /16 KiB/);
  for (const ref of ["", "x".repeat(201), "\nprivate", "a b", "<script>", "a?key=secret", "中", "_first"]) {
    const b = evidence(); b.baseline.inputRef = ref;
    assert.throws(() => parsePairEvidence(JSON.stringify(b)));
  }
  const b = evidence(); b.baseline.inputRef = "a".repeat(200);
  assert.equal(parsePairEvidence(JSON.stringify(b)).baseline.inputRef.length, 200);
});
test("duplicate fields, escaped duplicate aliases and excessive nested values are rejected", () => {
  const text = JSON.stringify(evidence());
  assert.throws(() => parsePairEvidence(text.replace('"schemaVersion":1', '"schemaVersion":2,"schemaVersion":1')), /duplicate/);
  assert.throws(() => parsePairEvidence(text.replace('"inputRef":"input-1"', '"inputRef":null,"input\\u0052ef":"input-1"')), /duplicate/);
  assert.throws(() => parsePairEvidence(text.replace('"inputRef":"input-1"', '"inputRef":[[[[["x"]]]]]')), /nesting/);
});
test("every declared control mismatch is non-comparable and suppresses metric deltas", () => {
  for (const key of ["caseId", "inputRef", "controlConfigRef", "criteriaVersion"]) {
    const b = evidence(); b.candidate[key] = "different";
    const result = comparePair(b, measure(), measure([]));
    assert.equal(result.state, "not_comparable"); assert.match(result.mismatch[0], new RegExp(key));
    assert.equal(result.callsDelta, null); assert.equal(result.tokensDelta, null);
  }
});
test("double-null and missing code version are gaps, not matching controls", () => {
  for (const key of ["caseId", "inputRef", "controlConfigRef", "criteriaVersion", "appVersion"]) {
    const b = evidence(); b.baseline[key] = null; b.candidate[key] = null;
    const result = comparePair(b, measure(), measure());
    assert.equal(result.state, "insufficient"); assert.equal(result.tokensDelta, null);
  }
  const b = evidence(); b.candidate.appVersion = b.baseline.appVersion;
  assert.equal(comparePair(b, measure(), measure()).state, "insufficient");
  b.candidate.caseId = "different"; assert.equal(comparePair(b, measure(), measure()).state, "not_comparable");
});
test("manual quality regression cannot be hidden by cheaper recorded calls", () => {
  const b = evidence(); b.candidate.qualityStatus = "failed";
  const smaller = call(); smaller.metadata = { ...smaller.metadata, input_tokens: 0, output_tokens: 0, total_tokens: 0 };
  const result = comparePair(b, measure(), measure([smaller]));
  assert.equal(result.state, "declared_match"); assert.equal(result.tokensDelta, -15);
  assert.ok(result.usdDelta < 0); assert.match(result.quality, /regression/);
  for (const status of ["not_evaluated", "passed"]) {
    b.candidate.qualityStatus = status;
    assert.match(comparePair(b, measure(), measure()).quality, status === "not_evaluated" ? /not evaluated/ : /require review/);
  }
  b.baseline.qualityStatus = "failed";
  assert.match(comparePair(b, measure(), measure()).quality, /failed to passed/);
  b.candidate.qualityStatus = "failed";
  assert.match(comparePair(b, measure(), measure()).quality, /No successful repair/);
});
test("failed, cancelled, timeout and unresolved LLM attempts remain in observed denominator", () => {
  const spans = ["error", "cancelled", "timeout", "running"].map((status, i) => call({ span_id: `span-${i}`, status }));
  spans.push({ ...call(), type: "tool" });
  const result = measure(spans);
  assert.equal(result.observedCalls, 4); assert.equal(result.coveredCalls, 4); assert.equal(result.knownTokens, 60);
});
test("partial and conflicting usage retain known subtotal, not a complete difference", () => {
  const partial = measure([call(), call({ metadata: {} })]);
  assert.equal(partial.knownTokens, 15); assert.equal(partial.coveredCalls, 1); assert.equal(partial.tokenBasis, null);
  assert.equal(partial.costCoveredCalls, 1); assert.equal(partial.costBasis, null);
  const result = comparePair(evidence(), measure(), partial);
  assert.equal(result.callsDelta, 1); assert.equal(result.tokensDelta, null); assert.equal(result.usdDelta, null);
  const conflict = measure([call({ metadata: { ...call().metadata, total_tokens: 100 } })]);
  assert.equal(conflict.conflictCalls, 1); assert.equal(conflict.knownTokens, null);
  assert.equal(comparePair(evidence(), measure(), conflict).tokensDelta, null);
});
test("provider/visible/mixed/unknown provenance and different total bases are not merged", () => {
  const m = { ...call().metadata, usage_source: "mamr_reported", output_token_basis: "provider_output" };
  for (const metadata of [{ ...m, output_token_basis: "visible_output" }, m, { ...call().metadata, usage_source: "unknown" },
    { ...call().metadata, total_tokens: null }]) {
    assert.equal(comparePair(evidence(), measure(), measure([call({ metadata })])).tokensDelta, null);
  }
  assert.equal(measure([call(), call({ metadata: m })]).tokenBasis, null);
});
test("real measured zero is known while no covered calls and canonical null remain unknown", () => {
  const zero = measure([call({ metadata: { ...call().metadata, input_tokens: 0, output_tokens: 0, total_tokens: 0 } })], 0);
  assert.equal(zero.knownTokens, 0); assert.equal(zero.knownUsd, 0);
  assert.equal(comparePair(evidence(), zero, zero).durationDelta, 0);
  assert.equal(measure([]).knownTokens, null); assert.equal(measure([]).knownUsd, null);
  const duration = getTraceDurationMs({ trace: { duration_ms: null, start_time: "2026-09-29T00:00:00Z", end_time: "2026-09-29T00:01:00Z" } });
  assert.equal(duration, null); assert.equal(comparePair(evidence(), zero, measure([call()], duration)).durationDelta, null);
});
test("price coverage, currency/snapshot basis and unsupported models prevent cost differences", () => {
  const base = measure(), unsupported = measure([call({ input: { model: "Unknown model" } })]);
  assert.equal(unsupported.knownUsd, null); assert.equal(comparePair(evidence(), base, unsupported).usdDelta, null);
  for (const costBasis of [null, "EUR/Standard-text/2026-09-24", "USD/Standard-text/2026-09-25"]) {
    assert.equal(comparePair(evidence(), base, { ...base, costBasis }).usdDelta, null);
  }
});
test("unsafe token aggregate and invalid durations cannot become numeric differences", () => {
  const huge = measure([call({ metadata: { total_tokens: Number.MAX_SAFE_INTEGER } }), call()]);
  assert.equal(huge.knownTokens, null);
  for (const duration of [NaN, Infinity, -1]) assert.equal(measure([call()], duration).durationMs, null);
});
test("malformed, mismatched, duplicate-span and legacy detail boundaries are explicit", () => {
  const detail = { trace: { trace_id: "before", name: "legacy", status: "ok", input: {}, output: { accepted: true }, metadata: {} }, spans: [call()], warnings: [] };
  assert.equal(isPairTraceDetail(detail, "before"), true);
  for (const mutate of [d => d.trace.trace_id = "other", d => d.trace.metadata = [], d => d.spans = null,
    d => d.spans[0].trace_id = "other", d => d.spans[0].input = null, d => d.spans.push(d.spans[0])]) {
    const d = structuredClone(detail); mutate(d); assert.equal(isPairTraceDetail(d, "before"), false);
  }
  const declaration = evidence(); declaration.candidate.qualityStatus = "not_evaluated";
  assert.match(comparePair(declaration, measure(), measure()).quality, /not evaluated/); // accepted does not supply criteria
});
