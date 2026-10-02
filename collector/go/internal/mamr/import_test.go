package mamr

import (
	"encoding/json"
	"errors"
	"os"
	"reflect"
	"strings"
	"testing"
)

func fixture(t *testing.T, name string) []byte {
	t.Helper()
	data, err := os.ReadFile("testdata/" + name + ".json")
	if err != nil {
		t.Fatal(err)
	}
	return data
}
func object(t *testing.T, name string) map[string]any {
	t.Helper()
	var b map[string]any
	if err := json.Unmarshal(fixture(t, name), &b); err != nil {
		t.Fatal(err)
	}
	return b
}
func receipt(b map[string]any, index int) map[string]any {
	return b["sourceEvidence"].(map[string]any)["receipts"].([]any)[index].(map[string]any)
}
func encode(t *testing.T, b any) string {
	t.Helper()
	data, err := json.Marshal(b)
	if err != nil {
		t.Fatal(err)
	}
	return string(data)
}

func TestSourceFixturesMapFaithfullyOncePerAttempt(t *testing.T) {
	for _, name := range []string{"completed", "contract-rejected", "started-only"} {
		t.Run(name, func(t *testing.T) {
			p, err := Parse(strings.NewReader(string(fixture(t, name))))
			if err != nil {
				t.Fatal(err)
			}
			if len(p.Spans) != 1 {
				t.Fatalf("counted source start/terminal twice: %d", len(p.Spans))
			}
			if encode(t, p.Trace.Metadata["mamr"]) != encode(t, object(t, name)) {
				t.Fatal("source fields changed")
			}
			if p.Trace.DurationMS != nil || p.Trace.EndedAt != nil {
				t.Fatal("invented meeting execution duration/end")
			}
			s := p.Spans[0]
			if len(s.Input) != 0 || len(s.Output) != 0 || s.ParentSpanID != nil {
				t.Fatal("invented model, text or dependency")
			}
			if name == "started-only" {
				if s.Status != "unknown" || s.EndedAt != nil || s.DurationMS != nil || s.Metadata["input_tokens"].(*int64) != nil {
					t.Fatal("missing terminal was fabricated")
				}
			} else if s.Status != "returned" {
				t.Fatal("call return incorrectly equated with contract rejection")
			}
			if name == "contract-rejected" && *s.Metadata["output_tokens"].(*int64) != 0 {
				t.Fatal("reported zero lost")
			}
			again, err := Parse(strings.NewReader(string(fixture(t, name))))
			if err != nil || !reflect.DeepEqual(p, again) {
				t.Fatal("mapping is not deterministic")
			}
		})
	}
}

func TestRejectMalformedPrivateAndContradictoryEvidence(t *testing.T) {
	cases := map[string]func(map[string]any){
		"unsupported version":  func(b map[string]any) { b["schemaVersion"] = 2 },
		"private root field":   func(b map[string]any) { b["SECRET_KEY"] = "SECRET_VALUE" },
		"private nested field": func(b map[string]any) { receipt(b, 1)["configuredModel"] = "SECRET_MODEL" },
		"private path": func(b map[string]any) {
			r := receipt(b, 1)
			r["validation"] = "rejected"
			r["validationCode"] = "invalid_type"
			r["validationPath"] = "card.SECRET_VALUE"
		},
		"unknown code": func(b map[string]any) {
			r := receipt(b, 1)
			r["validation"] = "rejected"
			r["validationCode"] = "SECRET_VALUE"
			r["validationPath"] = "card.stance"
		},
		"missing boolean": func(b map[string]any) { delete(b["taskResult"].(map[string]any), "memoPresent") },
		"null boolean":    func(b map[string]any) { b["taskResult"].(map[string]any)["memoPresent"] = nil },
		"null turns":      func(b map[string]any) { b["turns"] = nil },
		"string token": func(b map[string]any) {
			receipt(b, 1)["inputTokens"] = map[string]any{"value": "10", "source": "reported"}
		},
		"negative token": func(b map[string]any) {
			receipt(b, 1)["inputTokens"] = map[string]any{"value": -1, "source": "reported"}
		},
		"fractional token": func(b map[string]any) {
			receipt(b, 1)["inputTokens"] = map[string]any{"value": 1.5, "source": "reported"}
		},
		"unsafe integer": func(b map[string]any) {
			receipt(b, 1)["inputTokens"] = map[string]any{"value": 9007199254740992, "source": "reported"}
		},
		"unsafe aggregate": func(b map[string]any) {
			receipt(b, 1)["inputTokens"] = map[string]any{"value": 9007199254740991, "source": "reported"}
		},
		"unknown is not reported": func(b map[string]any) {
			receipt(b, 1)["inputTokens"] = map[string]any{"value": nil, "source": "reported"}
		},
		"start has usage": func(b map[string]any) {
			receipt(b, 0)["inputTokens"] = map[string]any{"value": 0, "source": "reported"}
		},
		"terminal lacks time":   func(b map[string]any) { receipt(b, 1)["endedAt"] = nil },
		"reversed time":         func(b map[string]any) { receipt(b, 1)["endedAt"] = "2026-09-26T12:00:00Z" },
		"wrong pair identity":   func(b map[string]any) { receipt(b, 1)["requestId"] = "other" },
		"unknown turn":          func(b map[string]any) { receipt(b, 1)["turnId"] = "other" },
		"wrong seat":            func(b map[string]any) { receipt(b, 1)["seatId"] = "other" },
		"wrong outcome":         func(b map[string]any) { b["outcomeSignals"].(map[string]any)["turnEnvelopeRejectionObserved"] = true },
		"wrong workflow signal": func(b map[string]any) { b["outcomeSignals"].(map[string]any)["meetingInterrupted"] = true },
		"invented quality":      func(b map[string]any) { b["taskResult"].(map[string]any)["qualityEvaluation"] = "passed" },
		"decision mismatch":     func(b map[string]any) { b["outcomeSignals"].(map[string]any)["humanDecision"] = "rejected" },
		"wrong unresolved": func(b map[string]any) {
			b["sourceEvidence"].(map[string]any)["unresolvedAttemptIds"] = []string{"attempt-1"}
		},
		"wrong collection state": func(b map[string]any) { b["sourceEvidence"].(map[string]any)["state"] = "recorded_empty" },
		"duplicate receipt": func(b map[string]any) {
			s := b["sourceEvidence"].(map[string]any)
			s["receipts"] = append(s["receipts"].([]any), receipt(b, 1))
		},
		"terminal before start": func(b map[string]any) {
			s := b["sourceEvidence"].(map[string]any)
			r := s["receipts"].([]any)
			s["receipts"] = []any{r[1], r[0]}
		},
		"duplicate turn":       func(b map[string]any) { turns := b["turns"].([]any); b["turns"] = append(turns, turns[0]) },
		"oversized collection": func(b map[string]any) { b["turns"] = make([]any, maxItems+1) },
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			b := object(t, "completed")
			mutate(b)
			_, err := Parse(strings.NewReader(encode(t, b)))
			if !errors.Is(err, ErrInvalid) || strings.Contains(err.Error(), "SECRET_") {
				t.Fatalf("unsafe acceptance/error: %v", err)
			}
		})
	}
	for _, raw := range []string{
		`{"schemaVersion":1,"schemaVersion":1}`, strings.Replace(string(fixture(t, "completed")), `"schemaVersion"`, `"SchemaVersion"`, 1),
		string(fixture(t, "completed")) + ` {}`, string(fixture(t, "completed")) + ` null`,
		strings.Repeat("[", 20) + strings.Repeat("]", 20), `null`,
		strings.Replace(string(fixture(t, "completed")), `"value": 10`, `"value": 10, "value": 10`, 1),
	} {
		if _, err := Parse(strings.NewReader(raw)); !errors.Is(err, ErrInvalid) {
			t.Fatalf("accepted malformed JSON: %v", err)
		}
	}
	if _, err := Parse(strings.NewReader(strings.Repeat(" ", MaxBytes+1))); !errors.Is(err, ErrTooLarge) {
		t.Fatal(err)
	}
}

func TestMissingCollectionsAndTerminalWithoutStart(t *testing.T) {
	for _, state := range []string{"not_recorded", "recorded_empty"} {
		b := object(t, "completed")
		b["sourceEvidence"] = map[string]any{"state": state, "receipts": []any{}, "unresolvedAttemptIds": []any{}}
		b["outcomeSignals"].(map[string]any)["turnEnvelopeRejectionObserved"] = nil
		p, err := Parse(strings.NewReader(encode(t, b)))
		if err != nil || len(p.Spans) != 0 {
			t.Fatalf("missing evidence: %v", err)
		}
	}
	b := object(t, "completed")
	s := b["sourceEvidence"].(map[string]any)
	s["receipts"] = []any{receipt(b, 1)}
	p, err := Parse(strings.NewReader(encode(t, b)))
	if err != nil || len(p.Spans) != 1 {
		t.Fatalf("terminal-only: %v", err)
	}
}
