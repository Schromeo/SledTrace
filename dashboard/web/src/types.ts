export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonObject
  | JsonValue[];

export type JsonObject = {
  [key: string]: JsonValue;
};

export type TraceListItem = {
  trace_id: string;
  name: string;
  status: string;
  query: string;
  answer: string;
  duration_ms: number | null;
  warning_count: number;
  started_at: string;
};

export type TraceRecord = {
  trace_id: string;
  name: string;
  status: string;
  input: JsonObject;
  output: JsonObject;
  metadata: JsonObject;
  started_at: string;
  ended_at: string | null;
  duration_ms: number | null;
};

export type Span = {
  span_id: string;
  trace_id: string;
  parent_span_id: string | null;
  type: string;
  name: string;
  status: string;
  input: JsonObject;
  output: JsonObject;
  metadata: JsonObject;
  started_at: string;
  ended_at: string | null;
  duration_ms: number | null;
  error: JsonObject | null;
};

export type DiagnosticSignal = {
  signal_id: string;
  label: string;
  observed?: JsonValue;
  expected?: JsonValue;
  comparator?: string;
  strength?: string;
  attributes?: JsonObject;
};

export type EvidenceItem = {
  evidence_id?: string | null;
  type: string;
  label: string;
  span_id?: string | null;
  chunk_id?: string | null;
  source?: string | null;
  snippet?: string | null;
  locator?: JsonObject;
  attributes?: JsonObject;
  diagnostic_object_ids?: string[];
};

export type DiagnosticObject = {
  diagnostic_object_id: string;
  type: string;
  label: string;
  span_id?: string | null;
  text?: string | null;
  normalized?: JsonObject;
  attributes?: JsonObject;
};

export type Warning = {
  warning_id: string;
  trace_id: string;
  span_id: string | null;
  type: string;
  severity: string;
  message: string;
  details: JsonObject;
  schema_version?: string | null;
  rule_id?: string | null;
  rule_version?: string | null;
  title?: string | null;
  category?: string | null;
  confidence?: number | null;
  explanation?: string | null;
  evidence?: EvidenceItem[] | null;
  diagnostics?: DiagnosticObject[] | null;
  signals?: DiagnosticSignal[] | null;
  recommended_action?: string | null;
  created_at: string;
};

export type TraceListResponse = {
  traces: TraceListItem[];
};

export type TraceDetailResponse = {
  trace: TraceRecord;
  spans: Span[];
  warnings: Warning[];
};

export type Chunk = {
  id?: string;
  text?: string;
  score?: number;
  score_type?: string;
  score_direction?: string;
  rank?: number;
  source?: string;
  document_id?: string;
  metadata?: JsonObject;
};
