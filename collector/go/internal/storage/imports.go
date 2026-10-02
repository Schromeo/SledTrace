package storage

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"sledtrace-collector/internal/models"
)

// ErrImportConflict means an existing trace ID belongs to different content or
// was written outside this import path. Neither case may overwrite history.
var ErrImportConflict = errors.New("MAMR import trace ID conflicts with existing data")

// SaveMAMRImport stores one mapped room trace, its spans, warnings and receipt in
// one transaction. A repeated identical payload is a no-op. The fingerprint is
// derived from the mapped payload, before warnings receive generated IDs/times.
func (s *Store) SaveMAMRImport(ctx context.Context, payload models.TracePayload, warnings []models.Warning) (bool, error) {
	if payload.Trace.TraceID == "" || payload.Trace.Name == "" || payload.Trace.Status == "" || payload.Trace.StartedAt == "" {
		return false, errors.New("MAMR import trace is incomplete")
	}
	canonical, err := json.Marshal(payload)
	if err != nil {
		return false, fmt.Errorf("marshal MAMR import: %w", err)
	}
	digest := sha256.Sum256(canonical)
	fingerprint := hex.EncodeToString(digest[:])

	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return false, fmt.Errorf("begin MAMR import: %w", err)
	}
	defer func() { _ = tx.Rollback() }()

	var previous string
	err = tx.QueryRowContext(ctx, "SELECT fingerprint FROM mamr_imports WHERE trace_id = ?", payload.Trace.TraceID).Scan(&previous)
	if err == nil {
		if previous != fingerprint {
			return false, ErrImportConflict
		}
		return false, nil
	}
	if !errors.Is(err, sql.ErrNoRows) {
		return false, fmt.Errorf("check MAMR import: %w", err)
	}
	var existing int
	err = tx.QueryRowContext(ctx, "SELECT 1 FROM traces WHERE id = ?", payload.Trace.TraceID).Scan(&existing)
	if err == nil {
		return false, ErrImportConflict
	}
	if !errors.Is(err, sql.ErrNoRows) {
		return false, fmt.Errorf("check trace ID: %w", err)
	}

	now := time.Now().UTC().Format(time.RFC3339Nano)
	input, err := marshalJSON(payload.Trace.Input)
	if err != nil {
		return false, fmt.Errorf("marshal trace input: %w", err)
	}
	output, err := marshalJSON(payload.Trace.Output)
	if err != nil {
		return false, fmt.Errorf("marshal trace output: %w", err)
	}
	metadata, err := marshalJSON(payload.Trace.Metadata)
	if err != nil {
		return false, fmt.Errorf("marshal trace metadata: %w", err)
	}
	_, err = tx.ExecContext(ctx, `INSERT INTO traces
    (id, name, status, input_json, output_json, metadata_json, started_at, ended_at, duration_ms, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, payload.Trace.TraceID, payload.Trace.Name,
		payload.Trace.Status, input, output, metadata, payload.Trace.StartedAt,
		nullableString(payload.Trace.EndedAt), nullableInt(payload.Trace.DurationMS), now)
	if err != nil {
		return false, fmt.Errorf("insert MAMR trace: %w", err)
	}

	spanIDs := make(map[string]struct{}, len(payload.Spans))
	for _, span := range payload.Spans {
		if span.SpanID == "" || span.TraceID != payload.Trace.TraceID || span.Type == "" || span.StartedAt == "" {
			return false, errors.New("MAMR import span is incomplete or has the wrong trace ID")
		}
		spanInput, err := marshalJSON(span.Input)
		if err != nil {
			return false, fmt.Errorf("marshal span input: %w", err)
		}
		spanOutput, err := marshalJSON(span.Output)
		if err != nil {
			return false, fmt.Errorf("marshal span output: %w", err)
		}
		spanMetadata, err := marshalJSON(span.Metadata)
		if err != nil {
			return false, fmt.Errorf("marshal span metadata: %w", err)
		}
		spanError, err := marshalJSON(span.Error)
		if err != nil {
			return false, fmt.Errorf("marshal span error: %w", err)
		}
		_, err = tx.ExecContext(ctx, `INSERT INTO spans
    (id, trace_id, parent_span_id, type, name, status, input_json, output_json, metadata_json,
     started_at, ended_at, duration_ms, error_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, span.SpanID, span.TraceID,
			nullableString(span.ParentSpanID), span.Type, span.Name, span.Status, spanInput,
			spanOutput, spanMetadata, span.StartedAt, nullableString(span.EndedAt),
			nullableInt(span.DurationMS), spanError, now)
		if err != nil {
			return false, fmt.Errorf("insert MAMR span %s: %w", span.SpanID, err)
		}
		spanIDs[span.SpanID] = struct{}{}
	}

	for _, warning := range warnings {
		if warning.WarningID == "" || warning.TraceID != payload.Trace.TraceID || warning.Type == "" ||
			warning.Severity == "" || warning.Message == "" || warning.CreatedAt == "" {
			return false, errors.New("MAMR import warning is incomplete or has the wrong trace ID")
		}
		if warning.SpanID != nil {
			if _, ok := spanIDs[*warning.SpanID]; !ok {
				return false, errors.New("MAMR import warning references a missing span")
			}
		}
		details, err := marshalJSON(warning.Details)
		if err != nil {
			return false, fmt.Errorf("marshal warning details: %w", err)
		}
		evidence, err := marshalJSONArray(warning.Evidence)
		if err != nil {
			return false, fmt.Errorf("marshal warning evidence: %w", err)
		}
		diagnostics, err := marshalJSONArray(warning.Diagnostics)
		if err != nil {
			return false, fmt.Errorf("marshal warning diagnostics: %w", err)
		}
		signals, err := marshalJSONArray(warning.Signals)
		if err != nil {
			return false, fmt.Errorf("marshal warning signals: %w", err)
		}
		_, err = tx.ExecContext(ctx, `INSERT INTO warnings
    (id, trace_id, span_id, type, severity, message, schema_version, rule_id, rule_version,
     title, category, confidence, explanation, details_json, evidence_json, diagnostics_json,
     signals_json, recommended_action, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, warning.WarningID,
			warning.TraceID, nullableString(warning.SpanID), warning.Type, warning.Severity,
			warning.Message, nullableString(warning.SchemaVersion), nullableString(warning.RuleID),
			nullableString(warning.RuleVersion), nullableString(warning.Title),
			nullableString(warning.Category), nullableFloat(warning.Confidence),
			nullableString(warning.Explanation), details, evidence, diagnostics, signals,
			nullableString(warning.RecommendedAction), warning.CreatedAt)
		if err != nil {
			return false, fmt.Errorf("insert MAMR warning %s: %w", warning.WarningID, err)
		}
	}

	_, err = tx.ExecContext(ctx, "INSERT INTO mamr_imports (trace_id, fingerprint) VALUES (?, ?)", payload.Trace.TraceID, fingerprint)
	if err != nil {
		return false, fmt.Errorf("record MAMR import: %w", err)
	}
	if err := tx.Commit(); err != nil {
		return false, fmt.Errorf("commit MAMR import: %w", err)
	}
	return true, nil
}
