package api

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"sledtrace-collector/internal/mamr"
	"sledtrace-collector/internal/models"
	"sledtrace-collector/internal/storage"
)

func TestMAMRImportReadbackDuplicatesConflictsAndReopen(t *testing.T) {
	for _, name := range []string{"completed", "contract-rejected", "started-only"} {
		t.Run(name, func(t *testing.T) {
			path := filepath.Join(t.TempDir(), "imports.db")
			store, err := storage.NewStore(path)
			if err != nil {
				t.Fatal(err)
			}
			data, err := os.ReadFile("../mamr/testdata/" + name + ".json")
			if err != nil {
				t.Fatal(err)
			}
			handler := NewServer(store).Routes()
			post := func(body []byte) *httptest.ResponseRecorder {
				r := httptest.NewRequest(http.MethodPost, "/api/imports/mamr", bytes.NewReader(body))
				r.Header.Set("Content-Type", "application/json")
				w := httptest.NewRecorder()
				handler.ServeHTTP(w, r)
				return w
			}
			w := post(data)
			if w.Code != 201 {
				t.Fatalf("import: %d %s", w.Code, w.Body)
			}
			var result map[string]string
			_ = json.Unmarshal(w.Body.Bytes(), &result)
			id := result["trace_id"]
			if w = post(data); w.Code != 200 || !strings.Contains(w.Body.String(), "unchanged") {
				t.Fatalf("repeat: %d %s", w.Code, w.Body)
			}
			var changed map[string]any
			_ = json.Unmarshal(data, &changed)
			changed["taskResult"].(map[string]any)["memoPresent"] = false
			if name != "completed" {
				changed["taskResult"].(map[string]any)["memoPresent"] = true
			}
			body, _ := json.Marshal(changed)
			if w = post(body); w.Code != 409 {
				t.Fatalf("conflict: %d %s", w.Code, w.Body)
			}
			changed["SECRET_FIELD"] = "SECRET_VALUE"
			body, _ = json.Marshal(changed)
			if w = post(body); w.Code != 400 || strings.Contains(w.Body.String(), "SECRET") {
				t.Fatalf("private field: %d %s", w.Code, w.Body)
			}
			list, err := store.ListTraces(context.Background())
			if err != nil || len(list) != 1 {
				t.Fatalf("duplicates/partial rows: %v %v", list, err)
			}
			if err = store.Close(); err != nil {
				t.Fatal(err)
			}
			store, err = storage.NewStore(path)
			if err != nil {
				t.Fatal(err)
			}
			defer store.Close()
			handler = NewServer(store).Routes()
			w = httptest.NewRecorder()
			handler.ServeHTTP(w, httptest.NewRequest("GET", "/api/traces/"+id, nil))
			var detail models.TraceDetailResponse
			if w.Code != 200 || json.Unmarshal(w.Body.Bytes(), &detail) != nil || len(detail.Spans) != 1 || len(detail.Warnings) != 0 {
				t.Fatalf("readback: %d %s", w.Code, w.Body)
			}
			if w = post(data); w.Code != 200 {
				t.Fatalf("reopen dedup: %d %s", w.Code, w.Body)
			}
		})
	}
}

func TestMAMRImportFailuresDoNotPersist(t *testing.T) {
	store, err := storage.NewStore(":memory:")
	if err != nil {
		t.Fatal(err)
	}
	defer store.Close()
	handler := NewServer(store).Routes()
	for _, c := range []struct {
		body, contentType string
		status            int
	}{
		{`{"SECRET_FIELD":"SECRET_VALUE"}`, "application/json", 400},
		{strings.Repeat(" ", mamr.MaxBytes+1), "application/json", 413},
		{`{}`, "text/plain", 415},
	} {
		r := httptest.NewRequest("POST", "/api/imports/mamr", strings.NewReader(c.body))
		r.Header.Set("Content-Type", c.contentType)
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, r)
		if w.Code != c.status || strings.Contains(w.Body.String(), "SECRET") {
			t.Fatalf("error: %d %s", w.Code, w.Body)
		}
	}
	list, err := store.ListTraces(context.Background())
	if err != nil || len(list) != 0 {
		t.Fatalf("partial import: %v %v", list, err)
	}
}
