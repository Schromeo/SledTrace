import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import { buildUsageLedger } from "../src/utils/usage.ts";
import { mamrBundle, evidenceValue, usageSourceLabel } from "../src/utils/mamr.ts";
import { estimateOpenAITextCost } from "../src/utils/pricing.ts";

test("MAMR fixtures preserve outcome, provenance and unknown/zero in display", async () => {
  for (const name of ["completed", "contract-rejected", "started-only"]) {
    const bundle = JSON.parse(await readFile(new URL(`../../../collector/go/internal/mamr/testdata/${name}.json`, import.meta.url), "utf8"));
    assert.equal(mamrBundle({ source: "mamr_diagnostic_v1", mamr: bundle }), bundle);
    const r = bundle.sourceEvidence.receipts.at(-1);
    const call = buildUsageLedger([{ span_id: "one-attempt", name: "source attempt", type: "llm", status: "unknown", input: {}, metadata: {
      usage_source: "mamr_reported", input_tokens: r.inputTokens.value, output_tokens: r.outputTokens.value,
      reasoning_output_tokens: r.reasoningTokens.value, output_token_basis: r.outputTokenBasis,
    } }]).calls[0];
    assert.equal(call.model, "Unknown model");
    assert.equal(usageSourceLabel(call.provenance), "MAMR receipt");
    assert.equal(estimateOpenAITextCost(call), null);
    assert.equal(bundle.taskResult.qualityEvaluation, "not_evaluated");
    if (name === "contract-rejected") {
      assert.equal(call.outputTokens.value, 0);
      assert.equal(r.callStatus, "returned");
      assert.equal(r.validation, "rejected");
      assert.equal(bundle.workflow.status, "interrupted");
    }
    if (name === "started-only") {
      assert.equal(call.total.kind, "unknown");
      assert.equal(evidenceValue(bundle.outcomeSignals.turnEnvelopeRejectionObserved), "Unknown");
    }
  }
});

test("visible output is not a provider total; old traces do not acquire source evidence", () => {
  const ledger = buildUsageLedger([{ span_id: "one", name: "visible", type: "llm", input: {}, metadata: {
    usage_source: "mamr_reported", input_tokens: 10, output_tokens: 0, output_token_basis: "visible_output",
  } }]);
  assert.equal(ledger.calls[0].total.kind, "unknown");
  assert.equal(ledger.coveredCalls, 0);
  assert.equal(mamrBundle({}), null);
  assert.equal(mamrBundle({ source: "mamr_diagnostic_v1", mamr: { schemaVersion: 2 } }), null);
  assert.equal(evidenceValue(null), "Unknown");
  assert.equal(evidenceValue(0), "0");
  assert.equal(evidenceValue(false), "No");
});
