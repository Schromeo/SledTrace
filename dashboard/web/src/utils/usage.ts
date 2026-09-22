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
  provenance: "unknown";
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
    total: resolveCallTotal(
      inputTokens,
      outputTokens,
      recordedTotalTokens,
    ),
    provenance: "unknown",
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
