package api

import (
	"errors"
	"mime"
	"net/http"

	"sledtrace-collector/internal/mamr"
	"sledtrace-collector/internal/models"
	"sledtrace-collector/internal/storage"
	"sledtrace-collector/internal/warnings"
)

func (s *Server) handleImportMAMR(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	mediaType, _, err := mime.ParseMediaType(r.Header.Get("Content-Type"))
	if err != nil || mediaType != "application/json" {
		writeJSON(w, http.StatusUnsupportedMediaType, models.ErrorResponse{Error: "MAMR import requires application/json"})
		return
	}
	payload, err := mamr.Parse(r.Body)
	if err != nil {
		status := http.StatusBadRequest
		if errors.Is(err, mamr.ErrTooLarge) {
			status = http.StatusRequestEntityTooLarge
		}
		writeJSON(w, status, models.ErrorResponse{Error: err.Error()})
		return
	}
	generated := warnings.NewEngine().Generate(payload)
	created, err := s.store.SaveMAMRImport(r.Context(), payload, generated)
	if err != nil {
		status, message := http.StatusInternalServerError, "MAMR import could not be stored"
		if errors.Is(err, storage.ErrImportConflict) {
			status, message = http.StatusConflict, "This room already exists with different content. Existing evidence was kept; use the original file or a separate source room."
		}
		writeJSON(w, status, models.ErrorResponse{Error: message})
		return
	}
	status, result := http.StatusCreated, "imported"
	if !created {
		status, result = http.StatusOK, "unchanged"
	}
	writeJSON(w, status, map[string]any{"trace_id": payload.Trace.TraceID, "status": result})
}
