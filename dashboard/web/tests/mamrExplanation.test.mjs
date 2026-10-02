import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import { buildMamrExplanation } from "../src/utils/mamrExplanation.ts";

async function fixture(name) {
  return JSON.parse(await readFile(new URL(`../../../collector/go/internal/mamr/testdata/${name}.json`, import.meta.url), "utf8"));
}
function metadata(bundle) { return { source: "mamr_diagnostic_v1", mamr: bundle }; }
function span(r, key = "span-one") {
  return { span_id: key, type: "llm", metadata: { usage_source: "mamr_reported", mamr_receipt: structuredClone(r) } };
}
function derive(bundle, spans = [span(bundle.sourceEvidence.receipts.at(-1))]) {
  return buildMamrExplanation(metadata(bundle), spans);
}

test("contract rejection identifies the observed gate once and links exact receipt", async () => {
  const b = await fixture("contract-rejected"), r = b.sourceEvidence.receipts.at(-1);
  const d = derive(b);
  assert.equal(d.attempts.length, 1); // start + terminal are not two failures
  assert.equal(d.attempts[0].layer, "contract");
  assert.equal(d.attempts[0].spanId, "span-one");
  assert.match(d.attempts[0].facts.join("\n"), /returned.*\n.*completed.*\n.*rejected/);
  assert.match(d.attempts[0].facts.join("\n"), /invalid_type at card.stance/);
  assert.match(d.attempts[0].nextCheck, /actual value and expected type/);
  assert.equal(d.context.find(x => x.label === "Quality").value, "not_evaluated");
  const reordered = Object.fromEntries(Object.entries(r).reverse());
  assert.equal(derive(b, [span(reordered)]).attempts[0].spanId, "span-one");
});

test("complete and human-approved does not establish quality or repair", async () => {
  const b = await fixture("completed"), d = derive(b);
  assert.match(d.title, /quality not evaluated/);
  assert.equal(d.attempts[0].layer, "none");
  assert.match(d.attempts[0].nextCheck, /do not establish answer quality/);
  assert.equal(d.context.find(x => x.label === "Human decision").value, "approved");
});

test("started-only interruption is an evidence gap, not a failure or active/free call", async () => {
  const b = await fixture("started-only"), d = derive(b);
  assert.equal(d.attempts[0].layer, "gap");
  assert.equal(d.attempts[0].title, "Terminal receipt missing");
  assert.match(d.title, /failure layer unknown/);
  assert.match(d.attempts[0].nextCheck, /do not infer a provider failure or a free call/);
  assert.equal(d.context.find(x => x.label === "Workflow").value, "interrupted · proposal");
});

test("call and provider termination remain separate; no request root cause is invented", async () => {
  for (const status of ["error", "cancelled", "timeout"]) {
    const b = await fixture("completed"), r = b.sourceEvidence.receipts.at(-1);
    r.callStatus = status; r.validation = "not_run"; r.providerFinish = "unknown";
    const a = derive(b).attempts[0];
    assert.equal(a.layer, "call"); assert.equal(a.title, `Call ${status}`);
    assert.match(a.nextCheck, /does not identify a provider or model root cause/);
  }
  for (const finish of ["incomplete", "failed"]) {
    const b = await fixture("completed"), r = b.sourceEvidence.receipts.at(-1);
    r.providerFinish = finish; r.validation = "not_run"; r.providerReason = "output_limit";
    const a = derive(b).attempts[0];
    assert.equal(a.layer, "provider"); assert.match(a.facts.join(" "), /output_limit/);
  }
});

test("passed validator with unknown provider finish cannot be presented as fully passed gates", async () => {
  const b = await fixture("completed"); b.sourceEvidence.receipts.at(-1).providerFinish = "unknown";
  assert.equal(derive(b).attempts[0].layer, "gap");
});

test("duplicate, mismatched, malformed and missing evidence degrades without crashing", async () => {
  for (const mutate of [
    b => b.sourceEvidence.receipts.push(structuredClone(b.sourceEvidence.receipts.at(-1))),
    b => b.sourceEvidence.receipts[0].seatId = "another-seat",
    b => b.sourceEvidence.receipts.at(-1).callStatus = ["returned"],
    b => b.turns = null,
    b => b.sourceEvidence = {},
    b => b.sourceEvidence = { state: "not_recorded", receipts: b.sourceEvidence.receipts },
    b => b.sourceEvidence.receipts = [null, 1, [], {}, { attemptId: "invalid" }],
  ]) {
    const b = await fixture("contract-rejected"); mutate(b);
    const d = derive(b, []);
    assert.equal(d.missingEvidence, true); assert.equal(d.attempts.length, 0);
    assert.match(d.title, /Evidence incomplete/);
  }
});

test("missing/ambiguous or wrong matching span never links an adjacent step", async () => {
  const b = await fixture("contract-rejected"), r = b.sourceEvidence.receipts.at(-1);
  const wrong = structuredClone(r); wrong.turnId = "other-turn";
  for (const spans of [[], [span(wrong)], [span(r), span(r, "span-two")],
    [{ ...span(r), type: "tool" }], [{ ...span(r), metadata: { mamr_receipt: r } }]]) {
    assert.equal(derive(b, spans).attempts[0].spanId, null);
  }
});

test("mixed attempts retain failures, unknowns and passed gates without global success", async () => {
  const b = await fixture("completed"), failed = await fixture("contract-rejected"), started = await fixture("started-only");
  for (const [extra, key] of [[failed, "2"], [started, "3"]]) {
    extra.turns[0].id = `turn-${key}`;
    extra.sourceEvidence.receipts.forEach(r => { r.turnId = `turn-${key}`; r.attemptId = `attempt-${key}`; });
    b.turns.push(...extra.turns); b.sourceEvidence.receipts.push(...extra.sourceEvidence.receipts);
  }
  const d = derive(b, []);
  assert.match(d.title, /Observed gate failure · 1 attempt$/);
  assert.deepEqual(d.attempts.map(a => a.layer), ["contract", "none", "gap"]);
  assert.equal(d.context.find(x => x.label === "Workflow").value, "complete · complete");
  // A previous failed attempt does not imply final workflow interruption.
});

test("legacy posthoc/tool/RAG metadata never acquires source-backed diagnosis", () => {
  for (const m of [{}, { source: "mamr_posthoc" }, { task_id: "agent-task" },
    { source: "mamr_diagnostic_v1", mamr: null }, { source: "mamr_diagnostic_v1", mamr: { schemaVersion: 2 } }]) {
    assert.equal(buildMamrExplanation(m, []), null);
  }
});

test("synthetic passed envelope plus reduction failure retains receipt facts and exact navigation", async () => {
  const b = await fixture("completed");
  b.turns[0].status = "error"; b.turns[0].reductionFailureObserved = true;
  const d = derive(b), a = d.attempts[0];
  assert.equal(a.layer, "reduction");
  assert.equal(a.title, "Application state reduction failed");
  assert.match(d.title, /Observed gate failure · 1 attempt$/);
  assert.match(a.facts.join("\n"), /returned.*\n.*completed.*\n.*passed/);
  assert.ok(a.facts.includes("Turn status: error"));
  assert.ok(a.facts.includes("State reduction failure recorded: Yes"));
  assert.equal(a.spanId, "span-one");
  assert.match(a.nextCheck, /not its reason or rejected Claim/);
  assert.doesNotMatch(a.nextCheck, /unknown_reference|caused by|savings/);
});

test("recovery and approved final memo do not erase the earlier reduction failure", async () => {
  const b = await fixture("completed"), failed = structuredClone(b);
  failed.turns[0].id = "turn-failed"; failed.turns[0].status = "error";
  failed.turns[0].reductionFailureObserved = true;
  failed.sourceEvidence.receipts.forEach(r => { r.turnId = "turn-failed"; r.attemptId = "attempt-failed"; r.requestId = "request-failed"; });
  b.turns.push(...failed.turns); b.sourceEvidence.receipts.push(...failed.sourceEvidence.receipts);
  const d = derive(b, [span(b.sourceEvidence.receipts[1], "recovered"), span(failed.sourceEvidence.receipts[1], "failed")]);
  assert.deepEqual(d.attempts.map(a => a.layer), ["reduction", "none"]);
  assert.equal(d.attempts[0].spanId, "failed");
  assert.equal(d.context.find(x => x.label === "Workflow").value, "complete · complete");
  assert.equal(d.context.find(x => x.label === "Human decision").value, "approved");
  assert.equal(d.context.find(x => x.label === "Quality").value, "not_evaluated");
});

test("additional format/reduction flags do not replace the original observed failure", async () => {
  for (const primary of ["contract", "call", "provider"]) {
    const b = await fixture(primary === "contract" ? "contract-rejected" : "completed");
    const r = b.sourceEvidence.receipts.at(-1);
    if (primary === "call") { r.callStatus = "error"; r.validation = "not_run"; r.providerFinish = "unknown"; }
    if (primary === "provider") { r.providerFinish = "incomplete"; r.validation = "not_run"; }
    b.turns[0].status = "error";
    b.turns[0].formatFailureObserved = true; b.turns[0].reductionFailureObserved = true;
    const d = derive(b), a = d.attempts[0];
    assert.equal(a.layer, primary);
    assert.match(a.title, /state reduction failure also recorded/);
    assert.ok(a.facts.includes("Format failure recorded: Yes"));
    assert.ok(a.facts.includes("State reduction failure recorded: Yes"));
    assert.match(d.title, /1 attempt$/); // multiple flags are not extra calls
  }
  const b = await fixture("completed"); b.turns[0].formatFailureObserved = true; b.turns[0].status = "error";
  const a = derive(b).attempts[0];
  assert.equal(a.layer, "contract");
  assert.equal(a.title, "Application format failure recorded");
  assert.ok(a.facts.includes("Application validation: passed"));
  assert.match(a.nextCheck, /later artifact-format gate/);
});

test("missing flags or error without recorded cause do not imply successful application gates", async () => {
  for (const mutate of [
    t => delete t.reductionFailureObserved,
    t => t.reductionFailureObserved = "true",
    t => t.formatFailureObserved = null,
    t => t.status = "error",
    t => t.status = "streaming",
    t => t.status = "unsupported",
  ]) {
    const b = await fixture("completed"); mutate(b.turns[0]);
    const d = derive(b);
    assert.equal(d.attempts[0].layer, "gap");
    assert.match(d.title, /failure layer unknown/);
    assert.doesNotMatch(d.attempts[0].title, /passed/);
    if (typeof b.turns[0].reductionFailureObserved !== "boolean") {
      assert.ok(d.attempts[0].facts.includes("State reduction failure recorded: Unknown"));
    }
  }
});

test("ambiguous turn or attempt identity cannot attribute a reduction flag", async () => {
  for (const mutate of [
    b => b.turns.push(structuredClone(b.turns[0])),
    b => b.turns[0].seatId = "wrong-seat",
    b => b.sourceEvidence.receipts.push({ ...structuredClone(b.sourceEvidence.receipts[1]), attemptId: "another-attempt" }),
    b => { const t = structuredClone(b.turns[0]); t.id = "other-turn"; b.turns.push(t); b.sourceEvidence.receipts[0].turnId = "other-turn"; },
  ]) {
    const b = await fixture("completed"); b.turns[0].reductionFailureObserved = true; mutate(b);
    const d = derive(b);
    assert.equal(d.missingEvidence, true);
    assert.equal(d.attempts.length, 0);
    assert.match(d.title, /Evidence incomplete/);
  }
});

test("started-only receipt and recorded reduction retain missing terminal as unknown", async () => {
  const b = await fixture("started-only"); b.turns[0].reductionFailureObserved = true; b.turns[0].status = "error";
  const d = derive(b), a = d.attempts[0];
  assert.equal(a.layer, "reduction");
  assert.ok(a.facts.includes("Call: started"));
  assert.equal(d.missingEvidence, true);
  assert.ok(a.facts.includes("Terminal receipt: Missing"));
  assert.ok(a.facts.includes("Provider finish: unknown (reason: unknown)"));
  assert.ok(a.facts.includes("Application validation: not_run"));
  assert.match(a.nextCheck, /not its reason/);
});
