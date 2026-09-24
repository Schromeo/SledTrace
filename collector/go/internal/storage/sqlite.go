package storage

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"sledtrace-collector/internal/models"

	_ "modernc.org/sqlite"
)

type Store struct {
	db *sql.DB
}

func NewStore(path string) (*Store, error) {
	db, err := sql.Open("sqlite", path)
	if err != nil {
		return nil, fmt.Errorf("open sqlite database: %w", err)
	}

	store := &Store{db: db}

	if err := store.migrate(context.Background()); err != nil {
		_ = db.Close()
		return nil, err
	}

	return store, nil
}

func (s *Store) Close() error {
	return s.db.Close()
}

func (s *Store) migrate(ctx context.Context) error {
	schema := `
CREATE TABLE IF NOT EXISTS traces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    input_json TEXT,
    output_json TEXT,
    metadata_json TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_ms INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS spans (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    parent_span_id TEXT,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    input_json TEXT,
    output_json TEXT,
    metadata_json TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_ms INTEGER,
    error_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(trace_id) REFERENCES traces(id)
);

CREATE TABLE IF NOT EXISTS warnings (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    span_id TEXT,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
	schema_version TEXT,
	rule_id TEXT,
	rule_version TEXT,
	title TEXT,
	category TEXT,
	confidence REAL,
	explanation TEXT,
    details_json TEXT,
	evidence_json TEXT,
	diagnostics_json TEXT,
	signals_json TEXT,
	recommended_action TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(trace_id) REFERENCES traces(id),
    FOREIGN KEY(span_id) REFERENCES spans(id)
);

CREATE INDEX IF NOT EXISTS idx_traces_started_at
ON traces(started_at);

CREATE INDEX IF NOT EXISTS idx_spans_trace_id
ON spans(trace_id);

CREATE INDEX IF NOT EXISTS idx_warnings_trace_id
ON warnings(trace_id);

CREATE INDEX IF NOT EXISTS idx_warnings_span_id
ON warnings(span_id);
`

	_, err := s.db.ExecContext(ctx, schema)
	if err != nil {
		return fmt.Errorf("run sqlite migrations: %w", err)
	}

	if err := s.ensureWarningColumns(ctx); err != nil {
		return err
	}

	return nil
}

func (s *Store) ensureWarningColumns(ctx context.Context) error {
	rows, err := s.db.QueryContext(ctx, `PRAGMA table_info(warnings)`)
	if err != nil {
		return fmt.Errorf("inspect warnings table columns: %w", err)
	}
	defer rows.Close()

	existing := make(map[string]bool)
	for rows.Next() {
		var (
			cid        int
			name       string
			columnType string
			notNull    int
			defaultVal sql.NullString
			pk         int
		)

		if err := rows.Scan(&cid, &name, &columnType, &notNull, &defaultVal, &pk); err != nil {
			return fmt.Errorf("scan warnings table info: %w", err)
		}

		existing[name] = true
	}

	if err := rows.Err(); err != nil {
		return fmt.Errorf("iterate warnings table info: %w", err)
	}

	columns := []struct {
		name string
		typ  string
	}{
		{name: "schema_version", typ: "TEXT"},
		{name: "rule_id", typ: "TEXT"},
		{name: "rule_version", typ: "TEXT"},
		{name: "title", typ: "TEXT"},
		{name: "category", typ: "TEXT"},
		{name: "confidence", typ: "REAL"},
		{name: "explanation", typ: "TEXT"},
		{name: "evidence_json", typ: "TEXT"},
		{name: "diagnostics_json", typ: "TEXT"},
		{name: "signals_json", typ: "TEXT"},
		{name: "recommended_action", typ: "TEXT"},
	}

	for _, column := range columns {
		if existing[column.name] {
			continue
		}

		query := fmt.Sprintf("ALTER TABLE warnings ADD COLUMN %s %s", column.name, column.typ)
		if _, err := s.db.ExecContext(ctx, query); err != nil {
			return fmt.Errorf("add warnings.%s column: %w", column.name, err)
		}
	}

	return nil
}

func (s *Store) SaveTracePayload(ctx context.Context, payload models.TracePayload) error {
	if payload.Trace.TraceID == "" {
		return errors.New("trace.trace_id is required")
	}

	if payload.Trace.Name == "" {
		return errors.New("trace.name is required")
	}

	if payload.Trace.Status == "" {
		return errors.New("trace.status is required")
	}

	if payload.Trace.StartedAt == "" {
		return errors.New("trace.started_at is required")
	}

	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("begin transaction: %w", err)
	}

	defer func() {
		_ = tx.Rollback()
	}()

	now := time.Now().UTC().Format(time.RFC3339Nano)

	inputJSON, err := marshalJSON(payload.Trace.Input)
	if err != nil {
		return fmt.Errorf("marshal trace input: %w", err)
	}

	outputJSON, err := marshalJSON(payload.Trace.Output)
	if err != nil {
		return fmt.Errorf("marshal trace output: %w", err)
	}

	metadataJSON, err := marshalJSON(payload.Trace.Metadata)
	if err != nil {
		return fmt.Errorf("marshal trace metadata: %w", err)
	}

	_, err = tx.ExecContext(
		ctx,
		`
INSERT INTO traces (
    id, name, status, input_json, output_json, metadata_json,
    started_at, ended_at, duration_ms, created_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`,
		payload.Trace.TraceID,
		payload.Trace.Name,
		payload.Trace.Status,
		inputJSON,
		outputJSON,
		metadataJSON,
		payload.Trace.StartedAt,
		nullableString(payload.Trace.EndedAt),
		nullableInt(payload.Trace.DurationMS),
		now,
	)

	if err != nil {
		return fmt.Errorf("insert trace: %w", err)
	}

	for _, span := range payload.Spans {
		if span.SpanID == "" {
			return errors.New("span.span_id is required")
		}

		if span.TraceID == "" {
			return errors.New("span.trace_id is required")
		}

		if span.TraceID != payload.Trace.TraceID {
			return fmt.Errorf("span %s trace_id does not match payload trace_id", span.SpanID)
		}

		inputJSON, err := marshalJSON(span.Input)
		if err != nil {
			return fmt.Errorf("marshal span input: %w", err)
		}

		outputJSON, err := marshalJSON(span.Output)
		if err != nil {
			return fmt.Errorf("marshal span output: %w", err)
		}

		metadataJSON, err := marshalJSON(span.Metadata)
		if err != nil {
			return fmt.Errorf("marshal span metadata: %w", err)
		}

		errorJSON, err := marshalJSON(span.Error)
		if err != nil {
			return fmt.Errorf("marshal span error: %w", err)
		}

		_, err = tx.ExecContext(
			ctx,
			`
INSERT INTO spans (
    id, trace_id, parent_span_id, type, name, status,
    input_json, output_json, metadata_json,
    started_at, ended_at, duration_ms, error_json, created_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`,
			span.SpanID,
			span.TraceID,
			nullableString(span.ParentSpanID),
			span.Type,
			span.Name,
			span.Status,
			inputJSON,
			outputJSON,
			metadataJSON,
			span.StartedAt,
			nullableString(span.EndedAt),
			nullableInt(span.DurationMS),
			errorJSON,
			now,
		)

		if err != nil {
			return fmt.Errorf("insert span %s: %w", span.SpanID, err)
		}
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("commit transaction: %w", err)
	}

	return nil
}

func (s *Store) SaveWarnings(ctx context.Context, warnings []models.Warning) error {
	if len(warnings) == 0 {
		return nil
	}

	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("begin warnings transaction: %w", err)
	}

	defer func() {
		_ = tx.Rollback()
	}()

	stmt, err := tx.PrepareContext(
		ctx,
		`
INSERT INTO warnings (
	id, trace_id, span_id, type, severity, message,
	schema_version, rule_id, rule_version, title, category, confidence, explanation,
	details_json, evidence_json, diagnostics_json, signals_json, recommended_action,
	created_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`,
	)
	if err != nil {
		return fmt.Errorf("prepare insert warning statement: %w", err)
	}

	defer stmt.Close()

	for _, warning := range warnings {
		if warning.WarningID == "" {
			return errors.New("warning.warning_id is required")
		}

		if warning.TraceID == "" {
			return errors.New("warning.trace_id is required")
		}

		if warning.Type == "" {
			return errors.New("warning.type is required")
		}

		if warning.Severity == "" {
			return errors.New("warning.severity is required")
		}

		if warning.Message == "" {
			return errors.New("warning.message is required")
		}

		if warning.CreatedAt == "" {
			return errors.New("warning.created_at is required")
		}

		detailsJSON, err := marshalJSON(warning.Details)
		if err != nil {
			return fmt.Errorf("marshal warning details: %w", err)
		}

		evidenceJSON, err := marshalJSONArray(warning.Evidence)
		if err != nil {
			return fmt.Errorf("marshal warning evidence: %w", err)
		}

		diagnosticsJSON, err := marshalJSONArray(warning.Diagnostics)
		if err != nil {
			return fmt.Errorf("marshal warning diagnostics: %w", err)
		}

		signalsJSON, err := marshalJSONArray(warning.Signals)
		if err != nil {
			return fmt.Errorf("marshal warning signals: %w", err)
		}

		_, err = stmt.ExecContext(
			ctx,
			warning.WarningID,
			warning.TraceID,
			nullableString(warning.SpanID),
			warning.Type,
			warning.Severity,
			warning.Message,
			nullableString(warning.SchemaVersion),
			nullableString(warning.RuleID),
			nullableString(warning.RuleVersion),
			nullableString(warning.Title),
			nullableString(warning.Category),
			nullableFloat(warning.Confidence),
			nullableString(warning.Explanation),
			detailsJSON,
			evidenceJSON,
			diagnosticsJSON,
			signalsJSON,
			nullableString(warning.RecommendedAction),
			warning.CreatedAt,
		)
		if err != nil {
			return fmt.Errorf("insert warning %s: %w", warning.WarningID, err)
		}
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("commit warnings transaction: %w", err)
	}

	return nil
}

func (s *Store) ListTraces(ctx context.Context) ([]models.TraceListItem, error) {
	rows, err := s.db.QueryContext(
		ctx,
		`
SELECT
    t.id,
    t.name,
    t.status,
    t.input_json,
    t.output_json,
    t.duration_ms,
    t.started_at,
    COUNT(w.id) AS warning_count
FROM traces t
LEFT JOIN warnings w ON w.trace_id = t.id
GROUP BY t.id
ORDER BY t.started_at DESC
LIMIT 100
`,
	)

	if err != nil {
		return nil, fmt.Errorf("query traces: %w", err)
	}

	defer rows.Close()

	traces := make([]models.TraceListItem, 0)

	for rows.Next() {
		var (
			id           string
			name         string
			status       string
			inputJSON    sql.NullString
			outputJSON   sql.NullString
			duration     sql.NullInt64
			startedAt    string
			warningCount int
		)

		if err := rows.Scan(
			&id,
			&name,
			&status,
			&inputJSON,
			&outputJSON,
			&duration,
			&startedAt,
			&warningCount,
		); err != nil {
			return nil, fmt.Errorf("scan trace row: %w", err)
		}

		inputMap := parseJSONMap(inputJSON.String)
		outputMap := parseJSONMap(outputJSON.String)

		item := models.TraceListItem{
			TraceID:      id,
			Name:         name,
			Status:       status,
			Query:        stringFromMap(inputMap, "query"),
			Answer:       stringFromMap(outputMap, "answer"),
			DurationMS:   nullableIntFromSQL(duration),
			WarningCount: warningCount,
			StartedAt:    startedAt,
		}

		traces = append(traces, item)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate traces: %w", err)
	}

	return traces, nil
}

func (s *Store) GetTraceDetail(ctx context.Context, traceID string) (*models.TraceDetailResponse, error) {
	trace, err := s.getTrace(ctx, traceID)
	if err != nil {
		return nil, err
	}

	spans, err := s.getSpans(ctx, traceID)
	if err != nil {
		return nil, err
	}

	warnings, err := s.getWarnings(ctx, traceID)
	if err != nil {
		return nil, err
	}

	return &models.TraceDetailResponse{
		Trace:    *trace,
		Spans:    spans,
		Warnings: warnings,
	}, nil
}

func (s *Store) getTrace(ctx context.Context, traceID string) (*models.TraceRecord, error) {
	row := s.db.QueryRowContext(
		ctx,
		`
SELECT
    id, name, status, input_json, output_json, metadata_json,
    started_at, ended_at, duration_ms
FROM traces
WHERE id = ?
`,
		traceID,
	)

	var (
		id           string
		name         string
		status       string
		inputJSON    sql.NullString
		outputJSON   sql.NullString
		metadataJSON sql.NullString
		startedAt    string
		endedAt      sql.NullString
		duration     sql.NullInt64
	)

	if err := row.Scan(
		&id,
		&name,
		&status,
		&inputJSON,
		&outputJSON,
		&metadataJSON,
		&startedAt,
		&endedAt,
		&duration,
	); err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, sql.ErrNoRows
		}

		return nil, fmt.Errorf("scan trace detail: %w", err)
	}

	return &models.TraceRecord{
		TraceID:    id,
		Name:       name,
		Status:     status,
		Input:      parseJSONMap(inputJSON.String),
		Output:     parseJSONMap(outputJSON.String),
		Metadata:   parseJSONMap(metadataJSON.String),
		StartedAt:  startedAt,
		EndedAt:    nullableStringFromSQL(endedAt),
		DurationMS: nullableIntFromSQL(duration),
	}, nil
}

func (s *Store) getSpans(ctx context.Context, traceID string) ([]models.Span, error) {
	rows, err := s.db.QueryContext(
		ctx,
		`
SELECT
    id, trace_id, parent_span_id, type, name, status,
    input_json, output_json, metadata_json,
    started_at, ended_at, duration_ms, error_json
FROM spans
WHERE trace_id = ?
ORDER BY started_at ASC
`,
		traceID,
	)

	if err != nil {
		return nil, fmt.Errorf("query spans: %w", err)
	}

	defer rows.Close()

	spans := make([]models.Span, 0)

	for rows.Next() {
		var (
			id           string
			parentSpanID sql.NullString
			spanTraceID  string
			spanType     string
			name         string
			status       string
			inputJSON    sql.NullString
			outputJSON   sql.NullString
			metadataJSON sql.NullString
			startedAt    string
			endedAt      sql.NullString
			duration     sql.NullInt64
			errorJSON    sql.NullString
		)

		if err := rows.Scan(
			&id,
			&spanTraceID,
			&parentSpanID,
			&spanType,
			&name,
			&status,
			&inputJSON,
			&outputJSON,
			&metadataJSON,
			&startedAt,
			&endedAt,
			&duration,
			&errorJSON,
		); err != nil {
			return nil, fmt.Errorf("scan span: %w", err)
		}

		spans = append(spans, models.Span{
			SpanID:       id,
			TraceID:      spanTraceID,
			ParentSpanID: nullableStringFromSQL(parentSpanID),
			Type:         spanType,
			Name:         name,
			Status:       status,
			Input:        parseJSONMap(inputJSON.String),
			Output:       parseJSONMap(outputJSON.String),
			Metadata:     parseJSONMap(metadataJSON.String),
			StartedAt:    startedAt,
			EndedAt:      nullableStringFromSQL(endedAt),
			DurationMS:   nullableIntFromSQL(duration),
			Error:        parseJSONMap(errorJSON.String),
		})
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate spans: %w", err)
	}

	return spans, nil
}

func (s *Store) getWarnings(ctx context.Context, traceID string) ([]models.Warning, error) {
	rows, err := s.db.QueryContext(
		ctx,
		`
SELECT
	id, trace_id, span_id, type, severity, message,
	schema_version, rule_id, rule_version, title, category,
	CASE WHEN typeof(confidence) IN ('integer', 'real') THEN confidence ELSE NULL END,
	explanation,
	details_json, evidence_json, diagnostics_json, signals_json, recommended_action,
	created_at
FROM warnings
WHERE trace_id = ?
ORDER BY created_at ASC
`,
		traceID,
	)

	if err != nil {
		return nil, fmt.Errorf("query warnings: %w", err)
	}

	defer rows.Close()

	warnings := make([]models.Warning, 0)

	for rows.Next() {
		var (
			id                string
			warningTraceID    string
			spanID            sql.NullString
			warningType       string
			severity          string
			message           string
			schemaVersion     sql.NullString
			ruleID            sql.NullString
			ruleVersion       sql.NullString
			title             sql.NullString
			category          sql.NullString
			confidence        sql.NullFloat64
			explanation       sql.NullString
			detailsJSON       sql.NullString
			evidenceJSON      sql.NullString
			diagnosticsJSON   sql.NullString
			signalsJSON       sql.NullString
			recommendedAction sql.NullString
			createdAt         string
		)

		if err := rows.Scan(
			&id,
			&warningTraceID,
			&spanID,
			&warningType,
			&severity,
			&message,
			&schemaVersion,
			&ruleID,
			&ruleVersion,
			&title,
			&category,
			&confidence,
			&explanation,
			&detailsJSON,
			&evidenceJSON,
			&diagnosticsJSON,
			&signalsJSON,
			&recommendedAction,
			&createdAt,
		); err != nil {
			return nil, fmt.Errorf("scan warning: %w", err)
		}

		warnings = append(warnings, models.Warning{
			WarningID:         id,
			TraceID:           warningTraceID,
			SpanID:            nullableStringFromSQL(spanID),
			Type:              warningType,
			Severity:          severity,
			Message:           message,
			SchemaVersion:     nullableStringFromSQL(schemaVersion),
			RuleID:            nullableStringFromSQL(ruleID),
			RuleVersion:       nullableStringFromSQL(ruleVersion),
			Title:             nullableStringFromSQL(title),
			Category:          nullableStringFromSQL(category),
			Confidence:        nullableFloatFromSQL(confidence),
			Explanation:       nullableStringFromSQL(explanation),
			Details:           parseJSONMap(detailsJSON.String),
			Evidence:          parseJSONArray[models.EvidenceItem](evidenceJSON.String),
			Diagnostics:       parseJSONArray[models.DiagnosticObject](diagnosticsJSON.String),
			Signals:           parseJSONArray[models.DiagnosticSignal](signalsJSON.String),
			RecommendedAction: nullableStringFromSQL(recommendedAction),
			CreatedAt:         createdAt,
		})
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate warnings: %w", err)
	}

	return warnings, nil
}

func marshalJSON(value any) (string, error) {
	if value == nil {
		return "{}", nil
	}

	data, err := json.Marshal(value)
	if err != nil {
		return "", err
	}

	return string(data), nil
}

func marshalJSONArray[T any](value []T) (string, error) {
	if len(value) == 0 {
		return "[]", nil
	}

	data, err := json.Marshal(value)
	if err != nil {
		return "", err
	}

	return string(data), nil
}

func parseJSONMap(raw string) models.JSONMap {
	if raw == "" {
		return models.JSONMap{}
	}

	var result models.JSONMap
	if err := json.Unmarshal([]byte(raw), &result); err != nil {
		return models.JSONMap{}
	}

	if result == nil {
		return models.JSONMap{}
	}

	return result
}

func parseJSONArray[T any](raw string) []T {
	if raw == "" {
		return []T{}
	}

	var result []T
	if err := json.Unmarshal([]byte(raw), &result); err != nil {
		return []T{}
	}

	if result == nil {
		return []T{}
	}

	return result
}

func stringFromMap(value models.JSONMap, key string) string {
	raw, ok := value[key]
	if !ok || raw == nil {
		return ""
	}

	str, ok := raw.(string)
	if !ok {
		return ""
	}

	return str
}

func nullableString(value *string) any {
	if value == nil {
		return nil
	}

	return *value
}

func nullableInt(value *int) any {
	if value == nil {
		return nil
	}

	return *value
}

func nullableFloat(value *float64) any {
	if value == nil {
		return nil
	}

	return *value
}

func nullableStringFromSQL(value sql.NullString) *string {
	if !value.Valid {
		return nil
	}

	return &value.String
}

func nullableIntFromSQL(value sql.NullInt64) *int {
	if !value.Valid {
		return nil
	}

	result := int(value.Int64)
	return &result
}

func nullableFloatFromSQL(value sql.NullFloat64) *float64 {
	if !value.Valid {
		return nil
	}

	result := value.Float64
	return &result
}
