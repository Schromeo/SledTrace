import type { TraceDetailResponse, TraceListResponse } from "../types";

export const API_BASE_URL =
  import.meta.env.VITE_SLEDTRACE_API_URL ??
  import.meta.env.VITE_RAGLENS_API_URL ??
  "http://localhost:4319";

export class ApiRequestError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    const text = await response.text();
    throw new ApiRequestError(response.status, `Request failed: ${response.status} ${text}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchTraces(): Promise<TraceListResponse> {
  return getJson<TraceListResponse>("/api/traces");
}

export async function fetchTraceDetail(
  traceId: string,
): Promise<TraceDetailResponse> {
  return getJson<TraceDetailResponse>(`/api/traces/${encodeURIComponent(traceId)}`);
}

export async function importMamrFile(file: File): Promise<{ trace_id: string; status: "imported" | "unchanged" }> {
  if (file.size > 1024 * 1024) throw new Error("MeetingRoom diagnostic file exceeds 1 MiB.");
  const response = await fetch(`${API_BASE_URL}/api/imports/mamr`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: await file.text(),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(typeof result.error === "string" ? result.error : "MeetingRoom import failed.");
  return result;
}
