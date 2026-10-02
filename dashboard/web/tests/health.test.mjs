import assert from "node:assert/strict";
import test from "node:test";

import {
  healthLabel,
  highestSeverity,
  listHealth,
  traceHealth,
} from "../src/utils/health.ts";

test("a failed run outranks any warning", () => {
  assert.equal(traceHealth("error", []), "error");
  assert.equal(traceHealth("error", [{ severity: "high" }]), "error");
  assert.equal(listHealth("error", 0), "error");
});

test("no warnings is clean, never 'correct'", () => {
  assert.equal(traceHealth("ok", []), "clean");
  assert.equal(healthLabel("clean", 0), "No warnings");
});

test("high severity is surfaced", () => {
  const warnings = [{ severity: "warning" }, { severity: "high" }];
  assert.equal(highestSeverity(warnings), "high");
  assert.equal(traceHealth("ok", warnings), "high");
  assert.equal(healthLabel("high", 2), "2 warnings · high severity");
});

test("ordinary and unknown severities count as warnings", () => {
  assert.equal(traceHealth("ok", [{ severity: "warning" }]), "warning");
  assert.equal(traceHealth("ok", [{ severity: "" }]), "warning");
  assert.equal(traceHealth("ok", [{ severity: "low" }]), "warning");
  assert.equal(healthLabel("warning", 1), "1 warning");
});

test("the list uses warning counts, with high severity when known", () => {
  assert.equal(listHealth("ok", 0), "clean");
  assert.equal(listHealth("ok", 3), "warning");
  assert.equal(listHealth("ok", 3, 1), "high");
  assert.equal(listHealth("ok", 3, undefined), "warning"); // older collector
  assert.equal(listHealth("error", 3, 1), "error");
});
