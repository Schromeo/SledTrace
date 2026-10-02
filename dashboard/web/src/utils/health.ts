// How a trace looks at a glance: did the run fail, and how serious are the
// warnings? Warnings are heuristics, so "clean" means "no warnings", never
// "the answer is correct".

export type TraceHealth = "error" | "high" | "warning" | "clean";

const SEVERITY_RANK: Record<string, number> = {
  critical: 3,
  high: 3,
  error: 3,
  medium: 2,
  warning: 2,
  low: 1,
  info: 1,
};

export function severityRank(severity: string | null | undefined): number {
  if (!severity) {
    return 2;
  }
  return SEVERITY_RANK[severity.toLowerCase()] ?? 2;
}

export function highestSeverity(
  warnings: ReadonlyArray<{ severity?: string | null }>,
): string | null {
  let best: string | null = null;
  let bestRank = 0;
  for (const warning of warnings) {
    const rank = severityRank(warning.severity);
    if (rank > bestRank) {
      bestRank = rank;
      best = warning.severity || "warning";
    }
  }
  return best;
}

/** Detail view: execution status plus the most serious warning. */
export function traceHealth(
  status: string,
  warnings: ReadonlyArray<{ severity?: string | null }>,
): TraceHealth {
  if (status === "error") {
    return "error";
  }
  if (warnings.length === 0) {
    return "clean";
  }
  return severityRank(highestSeverity(warnings)) >= 3 ? "high" : "warning";
}

/**
 * List view: uses the warning counts from the list API. Collectors older than
 * 0.8.1 do not send high_warning_count, so it defaults to 0.
 */
export function listHealth(
  status: string,
  warningCount: number,
  highWarningCount = 0,
): TraceHealth {
  if (status === "error") {
    return "error";
  }
  if (highWarningCount > 0) {
    return "high";
  }
  return warningCount > 0 ? "warning" : "clean";
}

export function healthLabel(
  health: TraceHealth,
  warningCount: number,
): string {
  if (health === "error") {
    return warningCount > 0
      ? `Run failed · ${formatWarnings(warningCount)}`
      : "Run failed";
  }
  if (health === "clean") {
    return "No warnings";
  }
  const label = formatWarnings(warningCount);
  return health === "high" ? `${label} · high severity` : label;
}

export function formatWarnings(count: number): string {
  return count === 1 ? "1 warning" : `${count} warnings`;
}
