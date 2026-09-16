package api

import (
	"database/sql"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"
	"strings"

	"sledtrace-collector/internal/models"
	"sledtrace-collector/internal/storage"
	"sledtrace-collector/internal/warnings"
)

type Server struct {
	store *storage.Store
}

func NewServer(store *storage.Store) *Server {
	return &Server{
		store: store,
	}
}

func (s *Server) Routes() http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /health", s.handleHealth)
	mux.HandleFunc("POST /api/traces", s.handlePostTrace)
	mux.HandleFunc("GET /api/traces", s.handleListTraces)
	mux.HandleFunc("GET /api/traces/", s.handleGetTraceDetail)

	return withCORS(withLogging(mux))
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{
		"status":  "ok",
		"service": "sledtrace-collector",
	})
}

func (s *Server) handlePostTrace(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	var payload models.TracePayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		writeJSON(w, http.StatusBadRequest, models.ErrorResponse{
			Error: "invalid JSON payload",
		})
		return
	}

	if err := s.store.SaveTracePayload(r.Context(), payload); err != nil {
		writeJSON(w, http.StatusBadRequest, models.ErrorResponse{
			Error: err.Error(),
		})
		return
	}

	engine := warnings.NewEngine()
	generatedWarnings := engine.Generate(payload)

	if err := s.store.SaveWarnings(r.Context(), generatedWarnings); err != nil {
		writeJSON(w, http.StatusInternalServerError, models.ErrorResponse{
			Error: err.Error(),
		})
		return
	}

	writeJSON(w, http.StatusCreated, models.StoreTraceResponse{
		TraceID:           payload.Trace.TraceID,
		Status:            "stored",
		WarningsGenerated: len(generatedWarnings),
	})
}

func (s *Server) handleListTraces(w http.ResponseWriter, r *http.Request) {
	traces, err := s.store.ListTraces(r.Context())
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, models.ErrorResponse{
			Error: err.Error(),
		})
		return
	}

	writeJSON(w, http.StatusOK, models.TraceListResponse{
		Traces: traces,
	})
}

func (s *Server) handleGetTraceDetail(w http.ResponseWriter, r *http.Request) {
	traceID := strings.TrimPrefix(r.URL.Path, "/api/traces/")
	traceID = strings.TrimSpace(traceID)

	if traceID == "" {
		writeJSON(w, http.StatusBadRequest, models.ErrorResponse{
			Error: "trace id is required",
		})
		return
	}

	detail, err := s.store.GetTraceDetail(r.Context(), traceID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			writeJSON(w, http.StatusNotFound, models.ErrorResponse{
				Error: "trace not found",
			})
			return
		}

		writeJSON(w, http.StatusInternalServerError, models.ErrorResponse{
			Error: err.Error(),
		})
		return
	}

	writeJSON(w, http.StatusOK, detail)
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)

	if err := json.NewEncoder(w).Encode(value); err != nil {
		log.Printf("failed to write JSON response: %v", err)
	}
}

func withLogging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("%s %s", r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

func withCORS(next http.Handler) http.Handler {
	allowedOrigins := configuredAllowedOrigins()

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		origin := r.Header.Get("Origin")
		if origin != "" {
			w.Header().Add("Vary", "Origin")
		}

		if _, allowed := allowedOrigins[origin]; allowed {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func configuredAllowedOrigins() map[string]struct{} {
	configured := os.Getenv("SLEDTRACE_ALLOWED_ORIGINS")
	if strings.TrimSpace(configured) == "" {
		configured = "http://localhost:5173,http://127.0.0.1:5173"
	}

	origins := make(map[string]struct{})
	for _, value := range strings.Split(configured, ",") {
		origin := strings.TrimSpace(value)
		if origin != "" {
			origins[origin] = struct{}{}
		}
	}

	return origins
}
