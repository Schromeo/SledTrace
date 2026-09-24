import type { JsonObject } from "../types";

export function taskDisplay(output: JsonObject): {
  label: string;
  text: string;
  accepted: boolean | null;
} {
  if (typeof output.task_result === "string") {
    return {
      label: "Task result",
      text: output.task_result || "(empty task result)",
      accepted: typeof output.accepted === "boolean" ? output.accepted : null,
    };
  }
  return {
    label: "Final answer",
    text: typeof output.answer === "string" ? output.answer : "",
    accepted: null,
  };
}

export function stepError(error: JsonObject | null): string | null {
  return error && typeof error.message === "string" ? error.message : null;
}
