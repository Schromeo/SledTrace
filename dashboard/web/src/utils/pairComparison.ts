import type { TraceDetailResponse } from "../types";
import type { UsageLedger } from "./usage";
import type { CostEstimate } from "./pricing";

export const PAIR_FILE_LIMIT = 16 * 1024;
export type QualityStatus = "passed" | "failed" | "not_evaluated";
export type PairRun = {
  traceId: string;
  caseId: string | null;
  inputRef: string | null;
  controlConfigRef: string | null;
  criteriaVersion: string | null;
  appVersion: string | null;
  qualityStatus: QualityStatus;
  qualityEvidenceRef: string | null;
};
export type PairEvidence = {
  schemaVersion: 1;
  kind: "sledtrace-pair-evidence";
  provenance: "user_declared";
  interventionId: string;
  baseline: PairRun;
  candidate: PairRun;
};
function object(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
function exact(value: unknown, keys: string[]): value is Record<string, unknown> {
  return object(value) && Object.keys(value).length === keys.length &&
    keys.every(key => Object.prototype.hasOwnProperty.call(value, key));
}
function reference(value: unknown): value is string {
  return typeof value === "string" && /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$/.test(value);
}
// JSON.parse validates grammar; this separate bounded scan rejects duplicate keys,
// including escaped aliases, rather than silently accepting the last declaration.
function rejectDuplicateKeys(text: string) {
  const stack: (Set<string> | null)[] = [];
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === "{" || char === "[") {
      stack.push(char === "{" ? new Set() : null);
      if (stack.length > 4) throw new Error("Pair evidence nesting is unsupported.");
    } else if (char === "}" || char === "]") stack.pop();
    else if (char === '"') {
      const start = i++;
      while (i < text.length) {
        if (text[i] === "\\") i += 2;
        else if (text[i] === '"') break;
        else i++;
      }
      let next = i + 1;
      while (/\s/.test(text[next] ?? "") && next < text.length) next++;
      if (text[next] === ":") {
        const key: string = JSON.parse(text.slice(start, i + 1));
        const keys = stack[stack.length - 1];
        if (keys?.has(key)) throw new Error("Pair evidence contains duplicate fields.");
        keys?.add(key);
      }
    }
  }
}
function run(value: unknown): value is PairRun {
  const controls = ["caseId", "inputRef", "controlConfigRef", "criteriaVersion", "appVersion"];
  if (!exact(value, ["traceId", ...controls, "qualityStatus", "qualityEvidenceRef"]) ||
      !reference(value.traceId) || !controls.every(key => value[key] === null || reference(value[key]))) return false;
  return value.qualityStatus === "not_evaluated" ? value.qualityEvidenceRef === null
    : (value.qualityStatus === "passed" || value.qualityStatus === "failed") && reference(value.qualityEvidenceRef);
}
export function parsePairEvidence(text: string): PairEvidence {
  if (new TextEncoder().encode(text).length > PAIR_FILE_LIMIT) throw new Error("Pair evidence exceeds 16 KiB.");
  let value: unknown;
  try { value = JSON.parse(text); } catch { throw new Error("Pair evidence is not valid JSON."); }
  rejectDuplicateKeys(text);
  if (!exact(value, ["schemaVersion", "kind", "provenance", "interventionId", "baseline", "candidate"]) ||
      value.schemaVersion !== 1 || value.kind !== "sledtrace-pair-evidence" ||
      value.provenance !== "user_declared" || !reference(value.interventionId) ||
      !run(value.baseline) || !run(value.candidate)) throw new Error("Pair evidence has unsupported fields, version or values.");
  if (value.baseline.traceId === value.candidate.traceId) throw new Error("Choose two different trace records; a trace cannot be compared with itself.");
  return value as PairEvidence;
}

// A corrupt detail must not become an empty run or zero usage.
export function isPairTraceDetail(value: unknown, traceId: string): value is TraceDetailResponse {
  if (!object(value) || !object(value.trace) || value.trace.trace_id !== traceId ||
      typeof value.trace.name !== "string" || typeof value.trace.status !== "string" ||
      ![value.trace.input, value.trace.output, value.trace.metadata].every(object) ||
      !Array.isArray(value.spans) || !Array.isArray(value.warnings)) return false;
  const ids = new Set<string>();
  return value.spans.every(span => {
    if (!object(span) || span.trace_id !== traceId || typeof span.span_id !== "string" ||
        !span.span_id || ids.has(span.span_id) || typeof span.type !== "string" ||
        typeof span.name !== "string" || typeof span.status !== "string" ||
        ![span.input, span.output, span.metadata].every(object)) return false;
    ids.add(span.span_id); return true;
  });
}
export type RunMeasurements = {
  observedCalls: number;
  coveredCalls: number;
  conflictCalls: number;
  knownTokens: number | null;
  tokenBasis: string | null;
  costCoveredCalls: number;
  knownUsd: number | null;
  costBasis: string | null;
  durationMs: number | null;
};
export function measurePairRun(ledger: UsageLedger, costs: (CostEstimate | null)[], durationMs: number | null): RunMeasurements {
  const signatures = new Set(ledger.calls.map(call => call.provenance === "unknown" ||
    call.outputTokenBasis === "unknown" || call.total.kind !== "known" ? null
    : `${call.provenance}/${call.outputTokenBasis}/${call.total.basis}`));
  const knownCosts = costs.filter((cost): cost is CostEstimate => cost !== null);
  const priceDates = new Set(knownCosts.map(cost => cost.priceDate));
  const tokenTotal = ledger.knownSubtotal;
  const costTotal = knownCosts.reduce((sum, cost) => sum + cost.usd, 0);
  return {
    observedCalls: ledger.observedCalls, coveredCalls: ledger.coveredCalls, conflictCalls: ledger.conflictCalls,
    knownTokens: ledger.coveredCalls > 0 && Number.isSafeInteger(tokenTotal) ? tokenTotal : null,
    tokenBasis: ledger.observedCalls > 0 && ledger.coveredCalls === ledger.observedCalls &&
      !ledger.conflictCalls && signatures.size === 1 && !signatures.has(null) ? [...signatures][0] : null,
    costCoveredCalls: knownCosts.length,
    knownUsd: knownCosts.length > 0 && Number.isFinite(costTotal) ? costTotal : null,
    costBasis: costs.length === ledger.observedCalls && ledger.observedCalls > 0 &&
      knownCosts.length === ledger.observedCalls && priceDates.size === 1 ? `USD/Standard-text/${[...priceDates][0]}` : null,
    durationMs: durationMs !== null && Number.isFinite(durationMs) && durationMs >= 0 ? durationMs : null,
  };
}
export function comparePair(evidence: PairEvidence, baseline: RunMeasurements, candidate: RunMeasurements) {
  const mismatch: string[] = [], gaps: string[] = [];
  for (const key of ["caseId", "inputRef", "controlConfigRef", "criteriaVersion"] as const) {
    const a = evidence.baseline[key], b = evidence.candidate[key];
    if (a === null || b === null) gaps.push(`${key}: not declared for both runs`);
    else if (a !== b) mismatch.push(`${key}: declarations differ`);
  }
  if (evidence.baseline.appVersion === null || evidence.candidate.appVersion === null) gaps.push("appVersion: not declared for both runs");
  else if (evidence.baseline.appVersion === evidence.candidate.appVersion) gaps.push("appVersion: no distinct code versions declared");
  const state = mismatch.length ? "not_comparable" : gaps.length ? "insufficient" : "declared_match";
  const matched = state === "declared_match";
  const a = evidence.baseline.qualityStatus, b = evidence.candidate.qualityStatus;
  const quality = !matched ? "No improvement verdict: comparison conditions are unresolved."
    : a === "not_evaluated" || b === "not_evaluated" ? "Quality not evaluated for both runs. Lower usage is not evidence of improvement."
    : a === "passed" && b === "failed" ? "Manual assessment shows a regression. Lower usage does not justify keeping this change."
    : a === "failed" && b === "passed" ? "Manual assessment changed from failed to passed. Review the referenced evidence before a keep/revert decision."
    : a === "passed" ? "Both manual assessments passed. Efficiency and the keep/revert decision still require review."
    : "Both manual assessments failed. No successful repair established.";
  function delta(x: number | null, y: number | null, compatible = true) {
    if (!matched || !compatible || x === null || y === null) return null;
    const result = y - x; return Number.isFinite(result) ? result : null;
  }
  return {
    state, mismatch, gaps, quality,
    callsDelta: delta(baseline.observedCalls, candidate.observedCalls),
    tokensDelta: delta(baseline.knownTokens, candidate.knownTokens,
      baseline.tokenBasis !== null && baseline.tokenBasis === candidate.tokenBasis),
    usdDelta: delta(baseline.knownUsd, candidate.knownUsd,
      baseline.costBasis !== null && baseline.costBasis === candidate.costBasis),
    durationDelta: delta(baseline.durationMs, candidate.durationMs),
  };
}
