import type { Span, Warning } from "../types";

export const WARNING_GUIDANCE =
  "Heuristic checks, not a correctness verdict. Text-based rules use English " +
  "patterns and limited domain assumptions; review the evidence in your context.";

export const NO_WARNINGS_MESSAGE =
  "No warnings generated. This does not confirm that the answer is correct.";

export function warningGuidanceForSpans(spans: ReadonlyArray<Pick<Span, "type">>): string {
  const hasTool = spans.some((span) => span.type === "tool");
  if (!hasTool) return WARNING_GUIDANCE;

  const hasRetrieval = spans.some((span) => span.type === "retrieval");
  if (!hasRetrieval) {
    return "Tool steps are visible, but no retrieval span was recorded, so " +
      "retrieval-grounding checks do not apply. Agent repeat and efficiency " +
      "checks are not implemented; zero warnings is not a health verdict.";
  }
  return WARNING_GUIDANCE +
    " Retrieval findings do not evaluate tool repetition or Agent efficiency.";
}

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
