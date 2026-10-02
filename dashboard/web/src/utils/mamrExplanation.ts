import type { JsonObject, JsonValue, Span } from "../types";

type Layer = "contract" | "call" | "provider" | "reduction" | "gap" | "none";
function isFailure(layer: Layer): boolean {
  return ["contract", "call", "provider", "reduction"].includes(layer);
}
export type AttemptExplanation = {
  attemptId: string;
  identity: string;
  layer: Layer;
  title: string;
  facts: string[];
  nextCheck: string;
  spanId: string | null;
};
export type MamrExplanationModel = {
  title: string;
  attempts: AttemptExplanation[];
  missingEvidence: boolean;
  context: { label: string; value: string }[];
};

function object(value: JsonValue | undefined): JsonObject | null {
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value : null;
}
function evidenceValue(value: JsonValue | undefined): string {
  if (value === true) return "Yes";
  if (value === false) return "No";
  return typeof value === "string" || typeof value === "number" ? String(value) : "Unknown";
}
function id(value: JsonValue | undefined): value is string {
  return typeof value === "string" && /^[a-zA-Z0-9._:/-]{1,300}$/.test(value);
}
function member(value: JsonValue | undefined, choices: string[]): boolean {
  return typeof value === "string" && choices.includes(value);
}
// Link only an exact source receipt, not a similarly named or adjacent span.
function sameValue(a: JsonValue | undefined, b: JsonValue | undefined, depth = 0): boolean {
  if (depth > 16) return false;
  if (a === b) return true;
  const x = object(a), y = object(b);
  if (!x || !y || Object.keys(x).length !== Object.keys(y).length) return false;
  return Object.keys(x).every(key => Object.prototype.hasOwnProperty.call(y, key) && sameValue(x[key], y[key], depth + 1));
}
function validReceipt(r: JsonObject, turn: JsonObject | undefined): boolean {
  return r.version === 1 && r.captureVersion === "mamr-turn-v1" && r.validatorVersion === "turn-envelope/v1" &&
    id(r.attemptId) && id(r.requestId) && id(r.turnId) && id(r.seatId) &&
    member(r.provider, ["openai", "anthropic", "gemini"]) &&
    member(r.phase, ["proposal", "review", "synthesis"]) &&
    Number.isSafeInteger(r.round) && Number(r.round) > 0 &&
    turn !== undefined && turn.id === r.turnId && turn.seatId === r.seatId && turn.phase === r.phase && turn.round === r.round &&
    (r.lifecycle === "started"
      ? r.callStatus === "started" && r.validation === "not_run" && r.providerFinish === "unknown"
      : r.lifecycle === "terminal" && member(r.callStatus, ["returned", "error", "cancelled", "timeout"]) &&
        member(r.validation, ["passed", "rejected", "not_run"]) &&
        member(r.providerFinish, ["completed", "incomplete", "failed", "unknown"]) &&
        (r.callStatus === "returned" || r.validation === "not_run"));
}

function explain(r: JsonObject, turn: JsonObject, spanId: string | null): AttemptExplanation {
  const facts = [
    `Call: ${evidenceValue(r.callStatus)}`,
    `Provider finish: ${evidenceValue(r.providerFinish)} (reason: ${evidenceValue(r.providerReason)})`,
    `Application validation: ${evidenceValue(r.validation)}`,
    `Turn status: ${evidenceValue(turn.status)}`,
    `Format failure recorded: ${evidenceValue(typeof turn.formatFailureObserved === "boolean" ? turn.formatFailureObserved : undefined)}`,
    `State reduction failure recorded: ${evidenceValue(typeof turn.reductionFailureObserved === "boolean" ? turn.reductionFailureObserved : undefined)}`,
  ];
  let layer: Layer = "gap", title = "Gate outcome not recorded";
  let nextCheck = "Check source capture and the local execution log for this attempt; do not infer a provider failure or a free call from missing evidence.";
  if (r.lifecycle === "started") {
    title = "Terminal receipt missing";
    facts.push("Terminal receipt: Missing");
  } else if (r.validation === "rejected") {
    layer = "contract";
    title = "Application contract rejected";
    facts.push(`Validator: ${evidenceValue(r.validatorVersion)} · ${evidenceValue(r.validationCode)} at ${evidenceValue(r.validationPath)}`);
    nextCheck = `Inspect ${evidenceValue(r.validationPath)} against the ${evidenceValue(r.validatorVersion)} schema in the application. Check a locally sanitized output structure; this export omits the actual value and expected type. Do not relax validation or retry automatically.`;
  } else if (r.callStatus !== "returned") {
    layer = "call";
    title = `Call ${evidenceValue(r.callStatus)}`;
    nextCheck = "Inspect the application's request, cancellation/timeout policy and local provider log for this attempt. Call failure alone does not identify a provider or model root cause.";
  } else if (r.providerFinish === "failed" || r.providerFinish === "incomplete") {
    layer = "provider";
    title = `Provider reported ${r.providerFinish}`;
    nextCheck = "Check the reported provider reason and request configuration in the application's local log. A returned response does not prove complete generation; quality and the underlying cause remain unassessed.";
  } else if (r.validation === "passed" && r.providerFinish === "completed") {
    layer = "none";
    title = "Call and envelope gates passed";
    nextCheck = "Review the final artifact against the task's acceptance criteria. Passed capture/contract gates and human approval do not establish answer quality.";
  }
  // These are independent source observations after the receipt, not a model
  // root cause or a relabelling of the receipt's envelope validation.
  if (turn.formatFailureObserved === true && layer !== "contract") {
    title = isFailure(layer) ? `${title} · format failure also recorded` : "Application format failure recorded";
    if (!isFailure(layer)) layer = "contract";
    nextCheck += " Check the application's later artifact-format gate; this turn flag does not identify its validator or cause.";
  }
  if (turn.reductionFailureObserved === true) {
    title = isFailure(layer) ? `${title} · state reduction failure also recorded` : "Application state reduction failed";
    if (!isFailure(layer)) layer = "reduction";
    nextCheck = (layer === "reduction" ? "" : `${nextCheck} `) +
      "Inspect the matching turn and local Canonical State reducer diagnostics in the application. The export records the failure, not its reason or rejected Claim. Do not infer a provider failure, relax validation or retry automatically.";
  }
  if (layer === "none" && (typeof turn.formatFailureObserved !== "boolean" ||
    typeof turn.reductionFailureObserved !== "boolean" || turn.status !== "done")) {
    layer = "gap"; title = "Later application outcome incomplete";
    nextCheck = "Inspect the source turn status and later application gates; passed call/envelope checks do not establish successful state reduction.";
  }
  return { attemptId: String(r.attemptId), identity: `${r.phase} · round ${r.round} · ${r.seatId} · ${r.turnId}`,
    layer, title, facts, nextCheck, spanId };
}

/** View-time facts only: no stored warning, inference of dependency or quality score. */
export function buildMamrExplanation(metadata: JsonObject, spans: Span[]): MamrExplanationModel | null {
  const bundle = object(metadata.mamr);
  if (metadata.source !== "mamr_diagnostic_v1" || bundle?.schemaVersion !== 1 ||
    bundle.kind !== "mamr-ordinary-meeting-diagnostic") return null;
  // Legacy/posthoc/RAG records do not acquire source diagnosis.
  const workflow = object(bundle.workflow) ?? {}, task = object(bundle.taskResult) ?? {};
  const source = object(bundle.sourceEvidence) ?? {};
  const raw = source.state === "recorded" && Array.isArray(source.receipts) && source.receipts.length <= 1024 ? source.receipts : [];
  const turns = Array.isArray(bundle.turns) && bundle.turns.length <= 1024 ? bundle.turns : [];
  const byAttempt = new Map<string, JsonObject[]>();
  const turnAttempts = new Map<string, Set<string>>();
  for (const value of raw) {
    const r = object(value);
    if (r && id(r.turnId) && id(r.attemptId)) {
      const identities = turnAttempts.get(r.turnId) ?? new Set<string>();
      identities.add(r.attemptId); turnAttempts.set(r.turnId, identities);
    }
  }
  const invalidAttempts = new Set<string>();
  let missingEvidence = raw.length === 0 || source.state !== "recorded";
  for (const value of raw) {
    const r = object(value);
    const matches = r ? turns.map(object).filter(t => t && t.id === r.turnId) : [];
    if (!r || matches.length !== 1 || turnAttempts.get(String(r.turnId))?.size !== 1 || !validReceipt(r, matches[0] ?? undefined)) {
      missingEvidence = true;
      if (r && id(r.attemptId)) invalidAttempts.add(r.attemptId);
      continue;
    }
    const key = String(r.attemptId);
    byAttempt.set(key, [...(byAttempt.get(key) ?? []), r]);
  }
  const attempts: AttemptExplanation[] = [];
  for (const receipts of byAttempt.values()) {
    const starts = receipts.filter(r => r.lifecycle === "started"), ends = receipts.filter(r => r.lifecycle === "terminal");
    const r = ends[0] ?? starts[0];
    if (ends.length === 0) missingEvidence = true;
    // Ambiguous identities/duplicates cannot be diagnosed as a known failure.
    if (invalidAttempts.has(String(r.attemptId)) || starts.length > 1 || ends.length > 1 || (starts[0] && ends[0] &&
      ["requestId", "turnId", "seatId", "phase", "round", "startedAt", "provider", "outputLimit", "outputTokenBasis"].some(key => starts[0][key] !== ends[0][key]))) {
      missingEvidence = true;
      continue;
    }
    const matchingSpans = spans.filter(s => s.type === "llm" && s.metadata?.usage_source === "mamr_reported" &&
      sameValue(s.metadata.mamr_receipt, r));
    const turn = turns.map(object).find(t => t?.id === r.turnId)!;
    if (typeof turn.formatFailureObserved !== "boolean" || typeof turn.reductionFailureObserved !== "boolean" ||
      !member(turn.status, ["done", "error", "streaming"])) missingEvidence = true;
    attempts.push(explain(r, turn, matchingSpans.length === 1 ? matchingSpans[0].span_id : null));
  }
  const failures = attempts.filter(a => isFailure(a.layer));
  const gaps = missingEvidence || attempts.some(a => a.layer === "gap");
  const title = failures.length > 0 ? `Observed gate failure · ${failures.length} attempt${failures.length === 1 ? "" : "s"}`
    : gaps ? "Evidence incomplete — failure layer unknown" : "No failure in captured gates — quality not evaluated";
  // Failure first for inspection; array/temporal order is never called a root cause.
  attempts.sort((a, b) => Number(isFailure(b.layer)) - Number(isFailure(a.layer)));
  return { title, attempts, missingEvidence, context: [
    { label: "Workflow", value: `${evidenceValue(workflow.status)} · ${evidenceValue(workflow.phase)}` },
    { label: "Memo present", value: evidenceValue(task.memoPresent) },
    { label: "Human decision", value: evidenceValue(task.humanDecision) },
    { label: "Quality", value: evidenceValue(task.qualityEvaluation) },
  ] };
}
