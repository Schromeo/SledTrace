import assert from "node:assert/strict";
import test from "node:test";

import {
  hasEnhancedWarning,
  normalizeWarning,
  NO_WARNINGS_MESSAGE,
  WARNING_GUIDANCE,
} from "../src/utils/warnings.ts";

const legacy = {
  warning_id: "warning-legacy",
  trace_id: "trace-test",
  span_id: null,
  type: "conflicting_chunks",
  severity: "high",
  message: "Retrieved policies disagree.",
  created_at: "2026-09-15T12:00:00Z",
};

test("legacy warnings without confidence retain their message and severity", () => {
  const normalized = normalizeWarning(legacy);
  assert.equal(normalized.message, legacy.message);
  assert.equal(normalized.severity, "high");
  assert.equal(normalized.confidence, null);
  assert.deepEqual(normalized.details, {});
  assert.deepEqual(normalized.evidence, []);
  assert.deepEqual(normalized.diagnostics, []);
  assert.deepEqual(normalized.signals, []);
  assert.equal(hasEnhancedWarning(normalized), false);
  assert.equal(Object.hasOwn(legacy, "confidence"), false);
});

test("finite raw confidence preserves legacy enhanced layout without rescaling", () => {
  for (const confidence of [0, 0.75, 0.88, 0.9, 1, 90]) {
    const normalized = normalizeWarning({ ...legacy, confidence });
    assert.equal(normalized.confidence, confidence);
    assert.equal(hasEnhancedWarning(normalized), true);
  }
});

test("missing and malformed confidence is safely normalized", () => {
  for (const confidence of [undefined, null, NaN, Infinity, -Infinity, "90%", {}, []]) {
    const normalized = normalizeWarning({ ...legacy, confidence });
    assert.equal(normalized.confidence, null);
    assert.equal(hasEnhancedWarning(normalized), false);
  }
});

test("evidence and actions survive regardless of confidence validity", () => {
  const evidence = [{ type: "chunk", label: "Current policy", snippet: "30 days" }];
  const details = { answer_value: "14 days", retrieved_value: "30 days" };
  const diagnostics = [{ diagnostic_object_id: "d1", type: "claim", label: "Return window" }];
  const signals = [{ signal_id: "s1", label: "Different return windows" }];
  for (const confidence of [0.9, null, undefined, "invalid"]) {
    const normalized = normalizeWarning({
      ...legacy, confidence, evidence, details, diagnostics, signals,
      title: "Conflicting return windows", category: "retrieval",
      explanation: "Current and legacy policies disagree.",
      recommended_action: "Check which policy applies.",
    });
    assert.equal(hasEnhancedWarning(normalized), true);
    assert.deepEqual(normalized.evidence, evidence);
    assert.deepEqual(normalized.details, details);
    assert.deepEqual(normalized.diagnostics, diagnostics);
    assert.deepEqual(normalized.signals, signals);
    assert.equal(normalized.title, "Conflicting return windows");
    assert.equal(normalized.category, "retrieval");
    assert.equal(normalized.explanation, "Current and legacy policies disagree.");
    assert.equal(normalized.recommended_action, "Check which policy applies.");
  }
});

test("nullable old payload collections remain safe", () => {
  const normalized = normalizeWarning({
    ...legacy, details: null, evidence: null, diagnostics: null, signals: null,
  });
  assert.deepEqual(normalized.details, {});
  assert.deepEqual(normalized.evidence, []);
  assert.deepEqual(normalized.diagnostics, []);
  assert.deepEqual(normalized.signals, []);
});

test("warning guidance states applicability without claiming correctness", () => {
  assert.match(WARNING_GUIDANCE, /Heuristic checks, not a correctness verdict/);
  assert.match(WARNING_GUIDANCE, /English patterns and limited domain assumptions/);
  assert.match(NO_WARNINGS_MESSAGE, /does not confirm that the answer is correct/);
  assert.doesNotMatch(WARNING_GUIDANCE, /\d+%|high confidence/i);
});
