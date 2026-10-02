package storage

import (
	"context"
	"testing"

	"sledtrace-collector/internal/models"
)

func TestListTracesCountsHighSeverityWarnings(t *testing.T) {
	ctx := context.Background()

	store, err := NewStore(":memory:")
	if err != nil {
		t.Fatalf("create in-memory store: %v", err)
	}
	defer store.Close()

	for _, id := range []string{"trace_with_high", "trace_without_warnings"} {
		payload := models.TracePayload{
			Trace: models.TraceRecord{
				TraceID:   id,
				Name:      id,
				Status:    "ok",
				Input:     models.JSONMap{},
				Output:    models.JSONMap{},
				Metadata:  models.JSONMap{},
				StartedAt: "2026-10-02T00:00:00Z",
			},
		}
		if err := store.SaveTracePayload(ctx, payload); err != nil {
			t.Fatalf("save %s: %v", id, err)
		}
	}

	warnings := []models.Warning{
		{WarningID: "w_high", TraceID: "trace_with_high", Type: "numeric_mismatch", Severity: "high", Message: "m", Details: models.JSONMap{}, CreatedAt: "2026-10-02T00:00:01Z"},
		{WarningID: "w_upper", TraceID: "trace_with_high", Type: "custom", Severity: "CRITICAL", Message: "m", Details: models.JSONMap{}, CreatedAt: "2026-10-02T00:00:01Z"},
		{WarningID: "w_plain", TraceID: "trace_with_high", Type: "conflicting_chunks", Severity: "warning", Message: "m", Details: models.JSONMap{}, CreatedAt: "2026-10-02T00:00:01Z"},
	}
	if err := store.SaveWarnings(ctx, warnings); err != nil {
		t.Fatalf("save warnings: %v", err)
	}

	traces, err := store.ListTraces(ctx)
	if err != nil {
		t.Fatalf("list traces: %v", err)
	}

	got := map[string]models.TraceListItem{}
	for _, item := range traces {
		got[item.TraceID] = item
	}

	if item := got["trace_with_high"]; item.WarningCount != 3 || item.HighWarningCount != 2 {
		t.Fatalf("trace_with_high: want 3 warnings / 2 high, got %d / %d", item.WarningCount, item.HighWarningCount)
	}
	if item := got["trace_without_warnings"]; item.WarningCount != 0 || item.HighWarningCount != 0 {
		t.Fatalf("trace_without_warnings: want 0 / 0, got %d / %d", item.WarningCount, item.HighWarningCount)
	}
}
