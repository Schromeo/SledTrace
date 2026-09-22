import assert from "node:assert/strict";
import test from "node:test";

import {
  buildUsageLedger,
  formatCallTotal,
  formatTokenField,
} from "../src/utils/usage.ts";

function span({
  id = "span-1",
  type = "llm",
  model = "model-a",
  metadata = {},
  duration = null,
} = {}) {
  return {
    span_id: id,
    trace_id: "trace-1",
    parent_span_id: null,
    type,
    name: id,
    status: "ok",
    input: model === null ? {} : { model },
    output: {},
    metadata,
    started_at: "2026-09-22T10:00:00Z",
    ended_at: null,
    duration_ms: duration,
    error: null,
  };
}

test("consistent components and recorded total count exactly once", () => {
  const ledger = buildUsageLedger([
    span({ metadata: { input_tokens: 100, output_tokens: 20, total_tokens: 120 } }),
  ]);

  assert.equal(ledger.observedCalls, 1);
  assert.equal(ledger.coveredCalls, 1);
  assert.equal(ledger.knownSubtotal, 120);
  assert.deepEqual(ledger.calls[0].total, {
    kind: "known",
    value: 120,
    basis: "recorded_total",
  });
});

test("total-only usage stays total-only and does not invent a split", () => {
  const ledger = buildUsageLedger([
    span({ metadata: { total_tokens: 75 } }),
  ]);
  const call = ledger.calls[0];

  assert.equal(call.inputTokens.kind, "missing");
  assert.equal(call.outputTokens.kind, "missing");
  assert.equal(call.total.kind, "known");
  assert.equal(call.total.value, 75);
  assert.equal(ledger.knownSubtotal, 75);
});

test("zero is measured usage rather than unknown", () => {
  const ledger = buildUsageLedger([
    span({ metadata: { input_tokens: 0, output_tokens: 0 }, duration: 0 }),
  ], (current) => current.duration_ms);
  const call = ledger.calls[0];

  assert.equal(call.inputTokens.kind, "known");
  assert.equal(call.outputTokens.kind, "known");
  assert.deepEqual(call.total, {
    kind: "known",
    value: 0,
    basis: "input_plus_output",
  });
  assert.equal(call.durationMs, 0);
  assert.equal(ledger.coveredCalls, 1);
});

test("conflicting total is explicit and excluded from subtotal", () => {
  const ledger = buildUsageLedger([
    span({ metadata: { input_tokens: 10, output_tokens: 5, total_tokens: 99 } }),
  ]);

  assert.equal(ledger.calls[0].total.kind, "conflict");
  assert.equal(ledger.conflictCalls, 1);
  assert.equal(ledger.coveredCalls, 0);
  assert.equal(ledger.knownSubtotal, 0);
});

test("valid components can provide a subtotal when recorded total is invalid", () => {
  const ledger = buildUsageLedger([
    span({ metadata: { input_tokens: 8, output_tokens: 2, total_tokens: -1 } }),
  ]);
  const call = ledger.calls[0];

  assert.equal(call.recordedTotalTokens.kind, "invalid");
  assert.deepEqual(call.total, {
    kind: "known",
    value: 10,
    basis: "input_plus_output",
  });
  assert.equal(ledger.knownSubtotal, 10);
});

test("partial, malformed and missing usage remain unknown", () => {
  const ledger = buildUsageLedger([
    span({ id: "partial", metadata: { input_tokens: 12 } }),
    span({ id: "malformed", metadata: { input_tokens: "9", total_tokens: 1.5 } }),
    span({ id: "missing", metadata: {} }),
  ]);

  assert.equal(ledger.observedCalls, 3);
  assert.equal(ledger.coveredCalls, 0);
  assert.equal(ledger.knownSubtotal, 0);
  assert.deepEqual(
    ledger.calls.map((call) => call.total.kind),
    ["unknown", "unknown", "unknown"],
  );
  assert.equal(ledger.calls[1].inputTokens.kind, "invalid");
  assert.equal(ledger.calls[1].recordedTotalTokens.kind, "invalid");
});

test("ledger includes only LLM spans and preserves observed call order", () => {
  const ledger = buildUsageLedger([
    span({ id: "retrieval", type: "retrieval", metadata: { total_tokens: 999 } }),
    span({ id: "first", model: "model-a", metadata: { total_tokens: 10 } }),
    span({ id: "second", model: null, metadata: { total_tokens: 20 } }),
  ]);

  assert.deepEqual(
    ledger.calls.map((call) => [call.order, call.spanId, call.model]),
    [
      [1, "first", "model-a"],
      [2, "second", "Unknown model"],
    ],
  );
  assert.equal(ledger.knownSubtotal, 30);
});

test("formatters distinguish zero, unknown, invalid and conflict", () => {
  assert.equal(formatTokenField({ kind: "known", value: 0 }), "0");
  assert.equal(formatTokenField({ kind: "missing", value: null }), "Unknown");
  assert.equal(formatTokenField({ kind: "invalid", value: null }), "Invalid");
  assert.equal(formatCallTotal({ kind: "conflict", value: null, basis: null }), "Conflict");
});
