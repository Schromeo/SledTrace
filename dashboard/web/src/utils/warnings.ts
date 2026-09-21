import type { Warning } from "../types";

export const WARNING_GUIDANCE =
  "Heuristic checks, not a correctness verdict. Text-based rules use English " +
  "patterns and limited domain assumptions; review the evidence in your context.";

export const NO_WARNINGS_MESSAGE =
  "No warnings generated. This does not confirm that the answer is correct.";

export function normalizeWarning(warning: Warning): Warning {
  return {
    ...warning,
    details: warning.details ?? {},
    confidence: hasNumericConfidence(warning.confidence)
      ? warning.confidence
      : null,
    evidence: warning.evidence ?? [],
    diagnostics: warning.diagnostics ?? [],
    signals: warning.signals ?? [],
  };
}

function hasNumericConfidence(
  confidence: Warning["confidence"],
): confidence is number {
  return typeof confidence === "number" && Number.isFinite(confidence);
}

export function hasEnhancedWarning(warning: Warning): boolean {
  // Retain legacy layout selection, but never display this uncalibrated value
  // as a probability. It remains in the payload for compatibility only.
  return Boolean(
    warning.schema_version ||
      warning.title ||
      warning.category ||
      hasNumericConfidence(warning.confidence) ||
      warning.explanation ||
      (warning.evidence?.length ?? 0) > 0,
  );
}
