package api

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"sledtrace-collector/internal/storage"
)

func newDashboardTestHandler(t *testing.T, dashboardDir string) http.Handler {
	t.Helper()

	store, err := storage.NewStore(":memory:")
	if err != nil {
		t.Fatalf("create in-memory store: %v", err)
	}
	t.Cleanup(func() { store.Close() })

	server := NewServer(store)
	if dashboardDir != "" {
		server.WithDashboard(dashboardDir)
	}
	return server.Routes()
}

func TestDashboardIsServedAlongsideAPI(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "index.html"), []byte("<title>SledTrace</title>"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(dir, "assets"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "assets", "app.js"), []byte("console.log(1)"), 0o644); err != nil {
		t.Fatal(err)
	}

	handler := newDashboardTestHandler(t, dir)

	cases := []struct {
		path     string
		wantCode int
		wantBody string
	}{
		{"/", http.StatusOK, "<title>SledTrace</title>"},
		{"/assets/app.js", http.StatusOK, "console.log(1)"},
		{"/health", http.StatusOK, "sledtrace-collector"},
		{"/api/traces", http.StatusOK, "traces"},
		{"/missing.js", http.StatusNotFound, ""},
	}

	for _, tc := range cases {
		rec := httptest.NewRecorder()
		handler.ServeHTTP(rec, httptest.NewRequest(http.MethodGet, tc.path, nil))
		if rec.Code != tc.wantCode {
			t.Fatalf("GET %s: expected %d, got %d body=%s", tc.path, tc.wantCode, rec.Code, rec.Body.String())
		}
		if tc.wantBody != "" && !strings.Contains(rec.Body.String(), tc.wantBody) {
			t.Fatalf("GET %s: body %q does not contain %q", tc.path, rec.Body.String(), tc.wantBody)
		}
	}
}

func TestDashboardIsNotServedByDefault(t *testing.T) {
	handler := newDashboardTestHandler(t, "")

	rec := httptest.NewRecorder()
	handler.ServeHTTP(rec, httptest.NewRequest(http.MethodGet, "/", nil))
	if rec.Code != http.StatusNotFound {
		t.Fatalf("expected 404 for / without a Dashboard, got %d", rec.Code)
	}
}
