import type { JsonObject, Span } from "../types";

export type TokenField =
  | { kind: "known"; value: number }
  | { kind: "missing"; value: null }
  | { kind: "invalid"; value: null };

export type CallTotal =
  | {
      kind: "known";
      value: number;
      basis: "recorded_total" | "input_plus_output";
    }
  | { kind: "unknown"; value: null; basis: null }
  | { kind: "conflict"; value: null; basis: null };

export type LlmUsageCall = {
  spanId: string;
  order: number;
  name: string;
  model: string;
  status: string;
  durationMs: number | null;
  inputTokens: TokenField;
  outputTokens: TokenField;
  recordedTotalTokens: TokenField;
  total: CallTotal;
  provenance: "unknown" | "openai_responses";
  cachedInputTokens: TokenField;
  cacheWriteTokens: TokenField;
  reasoningOutputTokens: TokenField;
  usageIssues: string[];
};

export type UsageLedger = {
  calls: LlmUsageCall[];
  observedCalls: number;
  coveredCalls: number;
  knownSubtotal: number;
  conflictCalls: number;
};

export function buildUsageLedger(
  spans: Span[],
  resolveDuration: (span: Span) => number | null = () => null,
): UsageLedger {
  const calls = spans
    .filter((span) => span.type === "llm")
    .map((span, index) =>
      normalizeLlmUsage(span, index + 1, resolveDuration(span)),
    );

  const covered = calls.filter((call) => call.total.kind === "known");

  return {
    calls,
    observedCalls: calls.length,
    coveredCalls: covered.length,
    knownSubtotal: covered.reduce(
      (subtotal, call) => subtotal + (call.total.value ?? 0),
      0,
    ),
    conflictCalls: calls.filter((call) => call.total.kind === "conflict")
      .length,
  };
}

export function formatTokenField(field: TokenField): string {
  if (field.kind === "known") {
    return field.value.toLocaleString("en-US");
  }

  return field.kind === "invalid" ? "Invalid" : "Unknown";
}

export function formatCallTotal(total: CallTotal): string {
  if (total.kind === "known") {
    return total.value.toLocaleString("en-US");
  }

  return total.kind === "conflict" ? "Conflict" : "Unknown";
}

function normalizeLlmUsage(
  span: Span,
  order: number,
  durationMs: number | null,
): LlmUsageCall {
  const inputTokens = readTokenField(span.metadata, "input_tokens");
  const outputTokens = readTokenField(span.metadata, "output_tokens");
  const recordedTotalTokens = readTokenField(span.metadata, "total_tokens");
  const provenance = span.metadata.usage_source === "openai_responses"
    ? "openai_responses" : "unknown";
  const cachedInputTokens = readTokenField(span.metadata, "cached_input_tokens");
  const cacheWriteTokens = readTokenField(span.metadata, "cache_write_tokens");
  const reasoningOutputTokens = readTokenField(span.metadata, "reasoning_output_tokens");
  const usageIssues = provenance === "openai_responses" && Array.isArray(span.metadata.usage_issues)
    ? span.metadata.usage_issues.filter((issue): issue is string => typeof issue === "string")
    : [];
  const providerInvalid = provenance === "openai_responses" && [
    "input_tokens_state", "output_tokens_state", "total_tokens_state",
    "cached_input_tokens_state", "cache_write_tokens_state", "reasoning_output_tokens_state",
  ].some((key) => span.metadata[key] === "invalid");
  const subfieldConflict = provenance === "openai_responses" && (
    usageIssues.length > 0 ||
    (inputTokens.kind === "known" && cachedInputTokens.kind === "known" && cachedInputTokens.value > inputTokens.value) ||
    (outputTokens.kind === "known" && reasoningOutputTokens.kind === "known" && reasoningOutputTokens.value > outputTokens.value) ||
    (inputTokens.kind === "known" && cacheWriteTokens.kind === "known" && cachedInputTokens.kind === "known" &&
      cacheWriteTokens.value + cachedInputTokens.value > inputTokens.value)
  );

  return {
    spanId: span.span_id,
    order,
    name: span.name,
    model: readString(span.input, "model") || "Unknown model",
    status: span.status,
    durationMs,
    inputTokens,
    outputTokens,
    recordedTotalTokens,
    total: subfieldConflict ? { kind: "conflict", value: null, basis: null } : providerInvalid
      ? { kind: "unknown", value: null, basis: null } : resolveCallTotal(
      inputTokens,
      outputTokens,
      recordedTotalTokens,
    ),
    provenance,
    cachedInputTokens,
    cacheWriteTokens,
    reasoningOutputTokens,
    usageIssues,
  };
}

function readTokenField(metadata: JsonObject, key: string): TokenField {
  if (
    !Object.prototype.hasOwnProperty.call(metadata, key) ||
    metadata[key] === null
  ) {
    return { kind: "missing", value: null };
  }

  const raw = metadata[key];

  if (
    typeof raw === "number" &&
    Number.isFinite(raw) &&
    Number.isInteger(raw) &&
    raw >= 0
  ) {
    return { kind: "known", value: raw };
  }

  return { kind: "invalid", value: null };
}

function resolveCallTotal(
  inputTokens: TokenField,
  outputTokens: TokenField,
  recordedTotalTokens: TokenField,
): CallTotal {
  const hasBothComponents =
    inputTokens.kind === "known" && outputTokens.kind === "known";
  const componentTotal = hasBothComponents
    ? inputTokens.value + outputTokens.value
    : null;

  if (recordedTotalTokens.kind === "known") {
    if (
      componentTotal !== null &&
      recordedTotalTokens.value !== componentTotal
    ) {
      return { kind: "conflict", value: null, basis: null };
    }

    return {
      kind: "known",
      value: recordedTotalTokens.value,
      basis: "recorded_total",
    };
  }

  if (componentTotal !== null) {
    return {
      kind: "known",
      value: componentTotal,
      basis: "input_plus_output",
    };
  }

  return { kind: "unknown", value: null, basis: null };
}

function readString(value: JsonObject, key: string): string {
  const raw = value[key];
  return typeof raw === "string" ? raw : "";
}
