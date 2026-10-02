package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCheckDashboardDirRequiresIndex(t *testing.T) {
	dir := t.TempDir()
	if err := checkDashboardDir(dir); err == nil {
		t.Fatal("expected an error for a directory without index.html")
	}

	if err := os.WriteFile(filepath.Join(dir, "index.html"), []byte("ok"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := checkDashboardDir(dir); err != nil {
		t.Fatalf("expected a built Dashboard directory to pass, got %v", err)
	}
}

func TestCollectorAddrDefaultsToLoopback(t *testing.T) {
	t.Setenv("SLEDTRACE_COLLECTOR_ADDR", "")
	t.Setenv("RAGLENS_COLLECTOR_ADDR", "")

	if got := collectorAddr(); got != "127.0.0.1:4319" {
		t.Fatalf("expected loopback default, got %q", got)
	}
}

func TestCollectorAddrPrefersSledTraceEnvironment(t *testing.T) {
	t.Setenv("SLEDTRACE_COLLECTOR_ADDR", "192.0.2.10:4319")
	t.Setenv("RAGLENS_COLLECTOR_ADDR", "192.0.2.20:4319")

	if got := collectorAddr(); got != "192.0.2.10:4319" {
		t.Fatalf("expected preferred address, got %q", got)
	}
}

func TestCollectorAddrRetainsLegacyFallback(t *testing.T) {
	t.Setenv("SLEDTRACE_COLLECTOR_ADDR", "")
	t.Setenv("RAGLENS_COLLECTOR_ADDR", "192.0.2.20:4319")

	if got := collectorAddr(); got != "192.0.2.20:4319" {
		t.Fatalf("expected legacy address, got %q", got)
	}
}
