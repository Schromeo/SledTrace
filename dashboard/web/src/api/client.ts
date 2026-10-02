import type { TraceDetailResponse, TraceListResponse } from "../types";

// An explicitly empty API URL means "same origin": the packaged
// `sledtrace serve` build is served by the collector itself.
export const API_BASE_URL: string =
  import.meta.env.VITE_SLEDTRACE_API_URL ??
  import.meta.env.VITE_RAGLENS_API_URL ??
  "http://localhost:4319";

export const API_DISPLAY_URL: string = API_BASE_URL || window.location.origin;

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
