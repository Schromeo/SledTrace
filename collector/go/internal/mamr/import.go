// Package mamr accepts only the metadata-only ordinary-meeting diagnostic-v1
// projection. It does not accept room records, model text or executable input.
package mamr

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"reflect"
	"regexp"
	"sort"
	"time"

	"sledtrace-collector/internal/models"
)

const MaxBytes = 1 << 20
const maxItems = 1024

var ErrInvalid = errors.New("invalid MAMR diagnostic-v1 bundle; check the documented fields and evidence consistency")
var ErrTooLarge = errors.New("MAMR diagnostic file exceeds 1 MiB")
var safeID = regexp.MustCompile(`^[a-zA-Z0-9._:/-]+$`)
var safePath = regexp.MustCompile(`^(\$|statement|card(\.(stance|thesis|confidence(\.(level|reason))?|questionForChair|recommendedAction|(newClaims|claimUpdates|objections)(\[[0-9]{1,3}\])?))?)$`)

type Bundle struct {
	SchemaVersion  int            `json:"schemaVersion"`
	Kind           string         `json:"kind"`
	Room           Room           `json:"room"`
	Workflow       Workflow       `json:"workflow"`
	TaskResult     TaskResult     `json:"taskResult"`
	OutcomeSignals OutcomeSignals `json:"outcomeSignals"`
	Turns          []Turn         `json:"turns"`
	SourceEvidence SourceEvidence `json:"sourceEvidence"`
}
type Room struct {
	ID        string `json:"id"`
	CreatedAt string `json:"createdAt"`
	UpdatedAt string `json:"updatedAt"`
}
type Workflow struct {
	Stage      string  `json:"stage"`
	Phase      *string `json:"phase"`
	Status     *string `json:"status"`
	Round      *int    `json:"round"`
	StopReason *string `json:"stopReason"`
	UpdatedAt  *string `json:"updatedAt"`
}
type TaskResult struct {
	MemoPresent       bool   `json:"memoPresent"`
	HumanDecision     string `json:"humanDecision"`
	QualityEvaluation string `json:"qualityEvaluation"`
}
type OutcomeSignals struct {
	TurnEnvelopeRejectionObserved *bool  `json:"turnEnvelopeRejectionObserved"`
	MeetingInterrupted            *bool  `json:"meetingInterrupted"`
	HumanDecision                 string `json:"humanDecision"`
	QualityEvaluation             string `json:"qualityEvaluation"`
}
type Turn struct {
	ID                       string `json:"id"`
	SeatID                   string `json:"seatId"`
	Round                    int    `json:"round"`
	Phase                    string `json:"phase"`
	Status                   string `json:"status"`
	FormatFailureObserved    bool   `json:"formatFailureObserved"`
	ReductionFailureObserved bool   `json:"reductionFailureObserved"`
}
type SourceEvidence struct {
	State                string    `json:"state"`
	UnresolvedAttemptIDs []string  `json:"unresolvedAttemptIds"`
	Receipts             []Receipt `json:"receipts"`
}
type Count struct {
	Value  *int64 `json:"value"`
	Source string `json:"source"`
}
type Receipt struct {
	Version          int     `json:"version"`
	CaptureVersion   string  `json:"captureVersion"`
	ValidatorVersion string  `json:"validatorVersion"`
	AttemptID        string  `json:"attemptId"`
	RequestID        string  `json:"requestId"`
	TurnID           string  `json:"turnId"`
	SeatID           string  `json:"seatId"`
	Provider         string  `json:"provider"`
	Phase            string  `json:"phase"`
	Round            int     `json:"round"`
	OutputLimit      int     `json:"outputLimit"`
	Lifecycle        string  `json:"lifecycle"`
	StartedAt        string  `json:"startedAt"`
	EndedAt          *string `json:"endedAt"`
	ElapsedMS        *int    `json:"elapsedMs"`
	CallStatus       string  `json:"callStatus"`
	ProviderFinish   string  `json:"providerFinish"`
	ProviderReason   string  `json:"providerReason"`
	Validation       string  `json:"validation"`
	ValidationCode   *string `json:"validationCode"`
	ValidationPath   *string `json:"validationPath"`
	InputTokens      Count   `json:"inputTokens"`
	OutputTokens     Count   `json:"outputTokens"`
	ReasoningTokens  Count   `json:"reasoningTokens"`
	OutputTokenBasis string  `json:"outputTokenBasis"`
}

func Parse(reader io.Reader) (models.TracePayload, error) {
	data, err := io.ReadAll(io.LimitReader(reader, MaxBytes+1))
	if err != nil {
		return models.TracePayload{}, ErrInvalid
	}
	if len(data) > MaxBytes {
		return models.TracePayload{}, ErrTooLarge
	}
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.UseNumber()
	value, err := readValue(decoder, 0)
	if err != nil || !exactShape(value, reflect.TypeOf(Bundle{})) {
		return models.TracePayload{}, ErrInvalid
	}
	if _, err = decoder.Token(); err != io.EOF {
		return models.TracePayload{}, ErrInvalid
	}
	var bundle Bundle
	if json.Unmarshal(data, &bundle) != nil || !validBundle(bundle) {
		return models.TracePayload{}, ErrInvalid
	}
	return mapBundle(bundle), nil
}

// JSON's default decoder accepts duplicate keys and case-insensitive names.
// This boundary rejects both, as well as missing fields, null collections and
// excessive nesting. Error text never echoes arbitrary keys or values.
func readValue(d *json.Decoder, depth int) (any, error) {
	if depth > 16 {
		return nil, ErrInvalid
	}
	token, err := d.Token()
	if err != nil {
		return nil, ErrInvalid
	}
	switch token {
	case json.Delim('{'):
		result := map[string]any{}
		for d.More() {
			key, err := d.Token()
			if err != nil {
				return nil, ErrInvalid
			}
			name, ok := key.(string)
			if !ok {
				return nil, ErrInvalid
			}
			if _, exists := result[name]; exists {
				return nil, ErrInvalid
			}
			value, err := readValue(d, depth+1)
			if err != nil {
				return nil, err
			}
			result[name] = value
		}
		close, err := d.Token()
		if err != nil || close != json.Delim('}') {
			return nil, ErrInvalid
		}
		return result, nil
	case json.Delim('['):
		result := []any{}
		for d.More() {
			if len(result) >= maxItems {
				return nil, ErrInvalid
			}
			value, err := readValue(d, depth+1)
			if err != nil {
				return nil, err
			}
			result = append(result, value)
		}
		close, err := d.Token()
		if err != nil || close != json.Delim(']') {
			return nil, ErrInvalid
		}
		return result, nil
	default:
		if _, delim := token.(json.Delim); delim {
			return nil, ErrInvalid
		}
		return token, nil
	}
}

func exactShape(value any, typ reflect.Type) bool {
	if typ.Kind() == reflect.Pointer {
		return value == nil || exactShape(value, typ.Elem())
	}
	switch typ.Kind() {
	case reflect.Struct:
		object, ok := value.(map[string]any)
		if !ok || len(object) != typ.NumField() {
			return false
		}
		for i := 0; i < typ.NumField(); i++ {
			field := typ.Field(i)
			v, exists := object[field.Tag.Get("json")]
			if !exists || !exactShape(v, field.Type) {
				return false
			}
		}
		return true
	case reflect.Slice:
		array, ok := value.([]any)
		if !ok {
			return false
		}
		for _, v := range array {
			if !exactShape(v, typ.Elem()) {
				return false
			}
		}
		return true
	case reflect.String:
		_, ok := value.(string)
		return ok
	case reflect.Bool:
		_, ok := value.(bool)
		return ok
	case reflect.Int, reflect.Int64:
		number, ok := value.(json.Number)
		if !ok {
			return false
		}
		_, err := number.Int64()
		return err == nil
	}
	return false
}

func member(value string, choices ...string) bool {
	for _, choice := range choices {
		if value == choice {
			return true
		}
	}
	return false
}
func identifier(value string, limit int) bool {
	return len(value) > 0 && len(value) <= limit && safeID.MatchString(value)
}
func date(value string) bool {
	_, err := time.Parse(time.RFC3339Nano, value)
	return len(value) <= 32 && err == nil
}
func ordered(start, end string) bool {
	a, errA := time.Parse(time.RFC3339Nano, start)
	b, errB := time.Parse(time.RFC3339Nano, end)
	return errA == nil && errB == nil && !b.Before(a)
}
func validCount(c Count) bool {
	return (c.Value == nil && c.Source == "unknown") || (c.Value != nil && *c.Value >= 0 && *c.Value <= 9007199254740991 && c.Source == "reported")
}
func validReceipt(r Receipt) bool {
	if r.Version != 1 || r.CaptureVersion != "mamr-turn-v1" || r.ValidatorVersion != "turn-envelope/v1" ||
		!identifier(r.AttemptID, 80) || !identifier(r.RequestID, 80) || !identifier(r.TurnID, 300) || !identifier(r.SeatID, 120) ||
		!member(r.Provider, "openai", "anthropic", "gemini") || !member(r.Phase, "proposal", "review", "synthesis") ||
		r.Round < 1 || r.Round > 100 || r.OutputLimit < 1 || r.OutputLimit > 100000 || !date(r.StartedAt) ||
		!member(r.ProviderFinish, "completed", "incomplete", "failed", "unknown") ||
		!member(r.ProviderReason, "output_limit", "context_limit", "content_filter", "other", "unknown") ||
		!member(r.Validation, "not_run", "passed", "rejected") || !validCount(r.InputTokens) || !validCount(r.OutputTokens) || !validCount(r.ReasoningTokens) ||
		!member(r.OutputTokenBasis, "provider_output", "visible_output") {
		return false
	}
	if r.Validation == "rejected" {
		if r.ValidationCode == nil || r.ValidationPath == nil || !safePath.MatchString(*r.ValidationPath) ||
			!member(*r.ValidationCode, "output_too_long", "invalid_json", "unsupported_fields", "invalid_type", "missing_field", "empty_string", "string_too_long", "invalid_enum", "too_many_items", "invalid_record", "state_changes_forbidden") {
			return false
		}
	} else if r.ValidationCode != nil || r.ValidationPath != nil {
		return false
	}
	if r.Lifecycle == "started" {
		return r.CallStatus == "started" && r.EndedAt == nil && r.ElapsedMS == nil && r.Validation == "not_run" &&
			r.ProviderFinish == "unknown" && r.ProviderReason == "unknown" && r.InputTokens.Value == nil && r.OutputTokens.Value == nil && r.ReasoningTokens.Value == nil
	}
	return r.Lifecycle == "terminal" && member(r.CallStatus, "returned", "error", "cancelled", "timeout") &&
		r.EndedAt != nil && date(*r.EndedAt) && ordered(r.StartedAt, *r.EndedAt) && r.ElapsedMS != nil && *r.ElapsedMS >= 0 && *r.ElapsedMS <= 9007199254740991 &&
		(r.CallStatus == "returned" || r.Validation == "not_run")
}
func sameAttempt(a, b Receipt) bool {
	return a.AttemptID == b.AttemptID && a.RequestID == b.RequestID && a.TurnID == b.TurnID && a.SeatID == b.SeatID &&
		a.Provider == b.Provider && a.Phase == b.Phase && a.Round == b.Round && a.OutputLimit == b.OutputLimit &&
		a.StartedAt == b.StartedAt && a.OutputTokenBasis == b.OutputTokenBasis
}
func validBundle(b Bundle) bool {
	if b.SchemaVersion != 1 || b.Kind != "mamr-ordinary-meeting-diagnostic" || !identifier(b.Room.ID, 200) ||
		!date(b.Room.CreatedAt) || !date(b.Room.UpdatedAt) || !ordered(b.Room.CreatedAt, b.Room.UpdatedAt) ||
		!member(b.Workflow.Stage, "meeting", "decision") || !member(b.TaskResult.HumanDecision, "waiting", "pending", "approved", "rejected") ||
		b.TaskResult.QualityEvaluation != "not_evaluated" || b.OutcomeSignals.QualityEvaluation != "not_evaluated" ||
		b.OutcomeSignals.HumanDecision != b.TaskResult.HumanDecision {
		return false
	}
	w := b.Workflow
	if w.Status == nil {
		if w.Phase != nil || w.Round != nil || w.StopReason != nil || w.UpdatedAt != nil || b.OutcomeSignals.MeetingInterrupted != nil {
			return false
		}
	} else {
		if !member(*w.Status, "ready", "running", "paused", "interrupted", "complete") || w.Phase == nil ||
			!member(*w.Phase, "proposal", "proposal_checkpoint", "review", "targeted_debate", "review_checkpoint", "synthesis", "human_gate", "complete", "stopped") ||
			w.Round == nil || *w.Round < 1 || *w.Round > 100 || w.UpdatedAt == nil || !date(*w.UpdatedAt) ||
			b.OutcomeSignals.MeetingInterrupted == nil || *b.OutcomeSignals.MeetingInterrupted != (*w.Status == "interrupted") ||
			(w.StopReason != nil && (!member(*w.StopReason, "human", "budget") || *w.Phase != "stopped")) {
			return false
		}
	}
	turns := map[string]Turn{}
	for _, t := range b.Turns {
		if !identifier(t.ID, 300) || !identifier(t.SeatID, 120) || t.Round < 1 || t.Round > 100 ||
			!member(t.Phase, "agenda", "proposal", "review", "synthesis") || !member(t.Status, "streaming", "done", "error") {
			return false
		}
		if _, duplicate := turns[t.ID]; duplicate {
			return false
		}
		turns[t.ID] = t
	}
	source := b.SourceEvidence
	if len(source.Receipts) == 0 {
		return member(source.State, "not_recorded", "recorded_empty") && len(source.UnresolvedAttemptIDs) == 0 && b.OutcomeSignals.TurnEnvelopeRejectionObserved == nil
	}
	if source.State != "recorded" {
		return false
	}
	starts, terminals := map[string]Receipt{}, map[string]Receipt{}
	terminalCount, rejected := 0, false
	var reportedSum int64
	for _, r := range source.Receipts {
		if !validReceipt(r) {
			return false
		}
		// Keep even aggregate display arithmetic inside JSON's safe integer range.
		for _, count := range []Count{r.InputTokens, r.OutputTokens, r.ReasoningTokens} {
			if count.Value != nil {
				if *count.Value > 9007199254740991-reportedSum {
					return false
				}
				reportedSum += *count.Value
			}
		}
		t, exists := turns[r.TurnID]
		if !exists || t.SeatID != r.SeatID || t.Round != r.Round || t.Phase != r.Phase {
			return false
		}
		if r.Lifecycle == "started" {
			if _, exists := starts[r.AttemptID]; exists {
				return false
			}
			if _, exists := terminals[r.AttemptID]; exists {
				return false
			}
			starts[r.AttemptID] = r
		} else {
			if _, exists := terminals[r.AttemptID]; exists {
				return false
			}
			if start, exists := starts[r.AttemptID]; exists && !sameAttempt(start, r) {
				return false
			}
			terminals[r.AttemptID] = r
			terminalCount++
			rejected = rejected || r.Validation == "rejected"
		}
	}
	unresolved := map[string]bool{}
	for id := range starts {
		if _, exists := terminals[id]; !exists {
			unresolved[id] = true
		}
	}
	if len(unresolved) != len(source.UnresolvedAttemptIDs) {
		return false
	}
	for _, id := range source.UnresolvedAttemptIDs {
		if !unresolved[id] {
			return false
		}
		delete(unresolved, id)
	}
	if terminalCount == 0 {
		return b.OutcomeSignals.TurnEnvelopeRejectionObserved == nil
	}
	return b.OutcomeSignals.TurnEnvelopeRejectionObserved != nil && *b.OutcomeSignals.TurnEnvelopeRejectionObserved == rejected
}

func digest(value string) string {
	sum := sha256.Sum256([]byte(value))
	return hex.EncodeToString(sum[:])
}
func jsonMap(value any) models.JSONMap {
	data, _ := json.Marshal(value)
	result := models.JSONMap{}
	_ = json.Unmarshal(data, &result)
	return result
}
func mapBundle(b Bundle) models.TracePayload {
	id := "trace_mamr_" + digest(b.Room.ID)
	status := "unknown"
	if b.Workflow.Status != nil {
		status = *b.Workflow.Status
	}
	payload := models.TracePayload{Trace: models.TraceRecord{
		TraceID: id, Name: "MAMR ordinary meeting", Status: status,
		Input: models.JSONMap{}, Output: models.JSONMap{}, StartedAt: b.Room.CreatedAt,
		Metadata: models.JSONMap{"source": "mamr_diagnostic_v1", "mamr": jsonMap(b)},
	}, Spans: []models.Span{}}
	// Terminal replaces start for counting, while both source receipts remain in
	// trace metadata. A missing terminal is unknown, not an actively running call.
	attempts := map[string]Receipt{}
	for _, r := range b.SourceEvidence.Receipts {
		attempts[r.AttemptID] = r
	}
	ordered := make([]Receipt, 0, len(attempts))
	for _, r := range attempts {
		ordered = append(ordered, r)
	}
	sort.Slice(ordered, func(i, j int) bool {
		a, _ := time.Parse(time.RFC3339Nano, ordered[i].StartedAt)
		z, _ := time.Parse(time.RFC3339Nano, ordered[j].StartedAt)
		if a.Equal(z) {
			return ordered[i].AttemptID < ordered[j].AttemptID
		}
		return a.Before(z)
	})
	for _, r := range ordered {
		status := "unknown"
		if r.Lifecycle == "terminal" {
			status = r.CallStatus
		}
		metadata := models.JSONMap{"mamr_receipt": jsonMap(r), "usage_source": "mamr_reported", "input_tokens": r.InputTokens.Value, "output_tokens": r.OutputTokens.Value, "reasoning_output_tokens": r.ReasoningTokens.Value, "output_token_basis": r.OutputTokenBasis}
		payload.Spans = append(payload.Spans, models.Span{SpanID: "span_mamr_" + digest(b.Room.ID+"\x00"+r.AttemptID), TraceID: id,
			Type: "llm", Name: r.Provider + " / " + r.Phase + " / " + r.SeatID, Status: status, Input: models.JSONMap{}, Output: models.JSONMap{},
			Metadata: metadata, StartedAt: r.StartedAt, EndedAt: r.EndedAt, DurationMS: r.ElapsedMS})
	}
	return payload
}
