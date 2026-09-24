import assert from "node:assert/strict";
import test from "node:test";

import { stepError, taskDisplay } from "../src/utils/taskDisplay.ts";

test("explicit task result outranks intermediate LLM answer", () => {
  assert.deepEqual(taskDisplay({ answer: "draft", task_result: "accepted", accepted: true }), {
    label: "Task result", text: "accepted", accepted: true,
  });
  assert.deepEqual(taskDisplay({ task_result: "failed", accepted: false }), {
    label: "Task result", text: "failed", accepted: false,
  });
});

test("legacy answer and unknown acceptance remain compatible", () => {
  assert.deepEqual(taskDisplay({ answer: "old answer" }), {
    label: "Final answer", text: "old answer", accepted: null,
  });
  assert.equal(taskDisplay({}).text, "");
  assert.equal(taskDisplay({ task_result: "" }).text, "(empty task result)");
  assert.equal(taskDisplay({ task_result: "done", accepted: "yes" }).accepted, null);
});

test("step error tolerates old or incomplete records", () => {
  assert.equal(stepError({ message: "tool unavailable" }), "tool unavailable");
  assert.equal(stepError(null), null);
  assert.equal(stepError({ code: "offline" }), null);
});
