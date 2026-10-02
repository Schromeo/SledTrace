package storage

import (
	"context"
	"errors"
	"testing"

	"sledtrace-collector/internal/models"
)

func importFixture() (models.TracePayload, []models.Warning) {
	traceID := "trace_mamr_fixture"
	spanID := "span_mamr_attempt"
	return models.TracePayload{
			Trace: models.TraceRecord{
				TraceID: traceID, Name: "MAMR ordinary meeting", Status: "error",
				Input: models.JSONMap{}, Output: models.JSONMap{"quality_evaluation": "not_evaluated"},
				Metadata:  models.JSONMap{"source": "mamr-diagnostic-v1"},
				StartedAt: "2026-09-27T12:00:00Z",
			},
			Spans: []models.Span{{
				SpanID: spanID, TraceID: traceID, Type: "llm", Name: "proposal",
				Status: "error", Input: models.JSONMap{},
				Output:    models.JSONMap{"input_tokens": nil, "output_tokens": 0},
				Metadata:  models.JSONMap{"validation": "rejected"},
				StartedAt: "2026-09-27T12:00:00Z",
			}},
		}, []models.Warning{{
			WarningID: "warning_mamr_fixture", TraceID: traceID, SpanID: &spanID,
			Type: "fixture", Severity: "info", Message: "Fixture warning",
			CreatedAt: "2026-09-27T12:00:01Z",
		}}
}

func rowCount(t *testing.T, store *Store, table string) int {
	t.Helper()
	var count int
	if err := store.db.QueryRow("SELECT COUNT(*) FROM " + table).Scan(&count); err != nil {
		t.Fatalf("count %s: %v", table, err)
	}
	return count
}

func TestSaveMAMRImportAtomicDuplicateAndConflict(t *testing.T) {
	ctx := context.Background()
	store, err := NewStore(":memory:")
	if err != nil {
		t.Fatal(err)
	}
	defer store.Close()
	payload, warnings := importFixture()
	created, err := store.SaveMAMRImport(ctx, payload, warnings)
	if err != nil || !created {
		t.Fatalf("initial import created=%v err=%v", created, err)
	}
	detail, err := store.GetTraceDetail(ctx, payload.Trace.TraceID)
	if err != nil {
		t.Fatal(err)
	}
	if len(detail.Spans) != 1 || len(detail.Warnings) != 1 || detail.Spans[0].Output["input_tokens"] != nil || detail.Spans[0].Output["output_tokens"] != float64(0) {
		t.Fatalf("trace/spans/warnings or null versus zero changed: %#v", detail)
	}
	created, err = store.SaveMAMRImport(ctx, payload, warnings)
	if err != nil || created {
		t.Fatalf("duplicate created=%v err=%v", created, err)
	}
	for _, table := range []string{"traces", "spans", "warnings", "mamr_imports"} {
		if got := rowCount(t, store, table); got != 1 {
			t.Fatalf("%s has %d rows after duplicate", table, got)
		}
	}
	changed := payload
	changed.Trace.Name = "Different saved data"
	if _, err := store.SaveMAMRImport(ctx, changed, warnings); !errors.Is(err, ErrImportConflict) {
		t.Fatalf("changed same ID should conflict: %v", err)
	}
	if got := rowCount(t, store, "traces"); got != 1 {
		t.Fatalf("conflict mutated traces: %d", got)
	}
}

func TestSaveMAMRImportRollsBackEveryMidTransactionFailure(t *testing.T) {
	ctx := context.Background()
	for _, tc := range []struct {
		name       string
		breakInput func(*models.TracePayload, *[]models.Warning)
	}{
		{"invalid span", func(p *models.TracePayload, _ *[]models.Warning) { p.Spans[0].TraceID = "wrong-trace" }},
		{"duplicate span", func(p *models.TracePayload, _ *[]models.Warning) { p.Spans = append(p.Spans, p.Spans[0]) }},
		{"invalid warning", func(_ *models.TracePayload, w *[]models.Warning) { (*w)[0].TraceID = "wrong-trace" }},
		{"orphan warning", func(_ *models.TracePayload, w *[]models.Warning) {
			missing := "missing-span"
			(*w)[0].SpanID = &missing
		}},
	} {
		t.Run(tc.name, func(t *testing.T) {
			store, err := NewStore(":memory:")
			if err != nil {
				t.Fatal(err)
			}
			defer store.Close()
			payload, warnings := importFixture()
			tc.breakInput(&payload, &warnings)
			if created, err := store.SaveMAMRImport(ctx, payload, warnings); err == nil || created {
				t.Fatalf("broken import created=%v err=%v", created, err)
			}
			for _, table := range []string{"traces", "spans", "warnings", "mamr_imports"} {
				if got := rowCount(t, store, table); got != 0 {
					t.Fatalf("%s retained %d rows", table, got)
				}
			}
		})
	}
}

func TestSaveMAMRImportNeverClaimsPreexistingTrace(t *testing.T) {
	ctx := context.Background()
	store, err := NewStore(":memory:")
	if err != nil {
		t.Fatal(err)
	}
	defer store.Close()
	payload, warnings := importFixture()
	if err := store.SaveTracePayload(ctx, payload); err != nil {
		t.Fatal(err)
	}
	if _, err := store.SaveMAMRImport(ctx, payload, warnings); !errors.Is(err, ErrImportConflict) {
		t.Fatalf("preexisting generic trace must conflict: %v", err)
	}
	if got := rowCount(t, store, "mamr_imports"); got != 0 {
		t.Fatalf("claimed generic trace: %d", got)
	}
}
