import type { TraceDetailResponse, TraceListResponse } from "../types";

export const API_BASE_URL =
  import.meta.env.VITE_SLEDTRACE_API_URL ??
  import.meta.env.VITE_RAGLENS_API_URL ??
  "http://localhost:4319";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed: ${response.status} ${text}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchTraces(): Promise<TraceListResponse> {
  return getJson<TraceListResponse>("/api/traces");
}

export async function fetchTraceDetail(
  traceId: string,
): Promise<TraceDetailResponse> {
  return getJson<TraceDetailResponse>(`/api/traces/${traceId}`);
}
