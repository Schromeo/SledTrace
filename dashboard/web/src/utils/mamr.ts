import type { JsonObject, JsonValue } from "../types";

function record(value: JsonValue | undefined): JsonObject | null {
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value : null;
}

export function mamrBundle(metadata: JsonObject): JsonObject | null {
  const bundle = record(metadata.mamr);
  return metadata.source === "mamr_diagnostic_v1" && bundle?.schemaVersion === 1 &&
    bundle.kind === "mamr-ordinary-meeting-diagnostic" ? bundle : null;
}

export function mamrRecord(bundle: JsonObject, field: string): JsonObject {
  return record(bundle[field]) ?? {};
}

export function evidenceValue(value: JsonValue | undefined): string {
  if (value === null || value === undefined) return "Unknown";
  if (value === true) return "Yes";
  if (value === false) return "No";
  return typeof value === "string" || typeof value === "number" ? String(value) : "Unknown";
}

export function usageSourceLabel(provenance: string): string {
  if (provenance === "openai_responses") return "OpenAI Responses";
  if (provenance === "mamr_reported") return "MAMR receipt";
  return "Unknown";
}
