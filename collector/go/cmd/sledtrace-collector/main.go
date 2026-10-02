package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"sledtrace-collector/internal/api"
	"sledtrace-collector/internal/storage"
)

func main() {
	addr := collectorAddr()
	// Keep the legacy default DB filename so existing local trace data remains visible.
	dbPath := getEnvWithLegacy("SLEDTRACE_DB_PATH", "RAGLENS_DB_PATH", "raglens.db")

	store, err := storage.NewStore(dbPath)
	if err != nil {
		log.Fatalf("failed to initialize storage: %v", err)
	}
	defer store.Close()

	server := api.NewServer(store)

	if dashboardDir := os.Getenv("SLEDTRACE_DASHBOARD_DIR"); dashboardDir != "" {
		if err := checkDashboardDir(dashboardDir); err != nil {
			log.Fatalf("invalid SLEDTRACE_DASHBOARD_DIR: %v", err)
		}
		server.WithDashboard(dashboardDir)
		log.Printf("Serving Dashboard from %s", dashboardDir)
	}

	log.Printf("SledTrace collector listening on %s", addr)
	log.Printf("SQLite database: %s", dbPath)

	if err := http.ListenAndServe(addr, server.Routes()); err != nil {
		log.Fatalf("collector stopped: %v", err)
	}
}

func checkDashboardDir(dir string) error {
	info, err := os.Stat(filepath.Join(dir, "index.html"))
	if err != nil {
		return fmt.Errorf("%s does not contain a built Dashboard index.html: %w", dir, err)
	}
	if info.IsDir() {
		return fmt.Errorf("%s/index.html is a directory", dir)
	}
	return nil
}

func collectorAddr() string {
	return getEnvWithLegacy(
		"SLEDTRACE_COLLECTOR_ADDR",
		"RAGLENS_COLLECTOR_ADDR",
		"127.0.0.1:4319",
	)
}

func getEnvWithLegacy(key string, legacyKey string, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}

	if legacyValue := os.Getenv(legacyKey); legacyValue != "" {
		return legacyValue
	}

	return fallback
}
