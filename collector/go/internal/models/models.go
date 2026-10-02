package models

type JSONMap map[string]any

type TracePayload struct {
	Trace TraceRecord `json:"trace"`
	Spans []Span      `json:"spans"`
}

type TraceRecord struct {
	TraceID    string  `json:"trace_id"`
	Name       string  `json:"name"`
	Status     string  `json:"status"`
	Input      JSONMap `json:"input"`
	Output     JSONMap `json:"output"`
	Metadata   JSONMap `json:"metadata"`
	StartedAt  string  `json:"started_at"`
	EndedAt    *string `json:"ended_at"`
	DurationMS *int    `json:"duration_ms"`
}

type Span struct {
	SpanID       string  `json:"span_id"`
	TraceID      string  `json:"trace_id"`
	ParentSpanID *string `json:"parent_span_id"`
	Type         string  `json:"type"`
	Name         string  `json:"name"`
	Status       string  `json:"status"`
	Input        JSONMap `json:"input"`
	Output       JSONMap `json:"output"`
	Metadata     JSONMap `json:"metadata"`
	StartedAt    string  `json:"started_at"`
	EndedAt      *string `json:"ended_at"`
	DurationMS   *int    `json:"duration_ms"`
	Error        JSONMap `json:"error"`
}

type DiagnosticSignal struct {
	SignalID   string  `json:"signal_id"`
	Label      string  `json:"label"`
	Observed   any     `json:"observed,omitempty"`
	Expected   any     `json:"expected,omitempty"`
	Comparator string  `json:"comparator,omitempty"`
	Strength   string  `json:"strength,omitempty"`
	Attributes JSONMap `json:"attributes,omitempty"`
}

type EvidenceItem struct {
	EvidenceID          string   `json:"evidence_id"`
	Type                string   `json:"type"`
	Label               string   `json:"label"`
	SpanID              *string  `json:"span_id,omitempty"`
	ChunkID             *string  `json:"chunk_id,omitempty"`
	Source              *string  `json:"source,omitempty"`
	Snippet             string   `json:"snippet,omitempty"`
	Locator             JSONMap  `json:"locator,omitempty"`
	Attributes          JSONMap  `json:"attributes,omitempty"`
	DiagnosticObjectIDs []string `json:"diagnostic_object_ids,omitempty"`
}

type DiagnosticObject struct {
	DiagnosticObjectID string  `json:"diagnostic_object_id"`
	Type               string  `json:"type"`
	Label              string  `json:"label"`
	SpanID             *string `json:"span_id,omitempty"`
	Text               string  `json:"text,omitempty"`
	Normalized         JSONMap `json:"normalized,omitempty"`
	Attributes         JSONMap `json:"attributes,omitempty"`
}

type Warning struct {
	WarningID         string             `json:"warning_id"`
	TraceID           string             `json:"trace_id"`
	SpanID            *string            `json:"span_id"`
	Type              string             `json:"type"`
	Severity          string             `json:"severity"`
	Message           string             `json:"message"`
	Details           JSONMap            `json:"details"`
	SchemaVersion     *string            `json:"schema_version,omitempty"`
	RuleID            *string            `json:"rule_id,omitempty"`
	RuleVersion       *string            `json:"rule_version,omitempty"`
	Title             *string            `json:"title,omitempty"`
	Category          *string            `json:"category,omitempty"`
	Confidence        *float64           `json:"confidence,omitempty"`
	Explanation       *string            `json:"explanation,omitempty"`
	Evidence          []EvidenceItem     `json:"evidence,omitempty"`
	Diagnostics       []DiagnosticObject `json:"diagnostics,omitempty"`
	Signals           []DiagnosticSignal `json:"signals,omitempty"`
	RecommendedAction *string            `json:"recommended_action,omitempty"`
	CreatedAt         string             `json:"created_at"`
}

type TraceListItem struct {
	TraceID      string `json:"trace_id"`
	Name         string `json:"name"`
	Status       string `json:"status"`
	Query        string `json:"query"`
	Answer       string `json:"answer"`
	DurationMS   *int   `json:"duration_ms"`
	WarningCount int    `json:"warning_count"`
	// HighWarningCount counts warnings of severity high/critical, so the
	// trace list can show the same severity as the detail view.
	HighWarningCount int    `json:"high_warning_count"`
	StartedAt        string `json:"started_at"`
}

type TraceListResponse struct {
	Traces []TraceListItem `json:"traces"`
}

type TraceDetailResponse struct {
	Trace    TraceRecord `json:"trace"`
	Spans    []Span      `json:"spans"`
	Warnings []Warning   `json:"warnings"`
}

type StoreTraceResponse struct {
	TraceID           string `json:"trace_id"`
	Status            string `json:"status"`
	WarningsGenerated int    `json:"warnings_generated"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}
