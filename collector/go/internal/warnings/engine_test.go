package warnings

import (
	"testing"

	"sledtrace-collector/internal/models"
)

func TestToolOnlyTaskDoesNotGetRetrievalGroundingWarning(t *testing.T) {
	payload := models.TracePayload{
		Trace: models.TraceRecord{
			TraceID: "agent_no_retrieval", Name: "agent", Status: "ok",
			Output: models.JSONMap{"answer": "Refund review: five business days"},
		},
		Spans: []models.Span{{
			SpanID: "tool_1", TraceID: "agent_no_retrieval", Type: "tool",
			Name: "policy_lookup", Status: "ok",
		}},
	}
	if got := NewEngine().Generate(payload); len(got) != 0 {
		t.Fatalf("tool-only trace should have no RAG warnings, got %v", warningTypes(got))
	}

	payload.Spans = append(payload.Spans, models.Span{
		SpanID: "retrieval_1", TraceID: "agent_no_retrieval", Type: "retrieval",
		Name: "search", Status: "ok", Output: models.JSONMap{"chunks": []any{}},
	})
	requireWarningType(t, NewEngine().Generate(payload), TypeNoRetrievedChunks)
}

func TestLowRetrievalScorePreservesLegacyHigherIsBetterBehavior(t *testing.T) {
	payload := basePayload(
		"trace_legacy_low_score",
		"What is the refund policy?",
		[]models.JSONMap{
			chunk("legacy", "The refund policy allows returns.", 0.1, "policy.md"),
		},
		"The refund policy allows returns.",
	)

	requireWarningType(t, NewEngine().Generate(payload), TypeLowRetrievalScore)
}

func TestLowRetrievalScoreUsesDeclaredHigherIsBetterSimilarity(t *testing.T) {
	payload := basePayload(
		"trace_similarity_low_score",
		"What is the refund policy?",
		[]models.JSONMap{
			semanticChunk(
				"similarity",
				"The refund policy allows returns.",
				0.1,
				"similarity",
				"higher_is_better",
			),
		},
		"The refund policy allows returns.",
	)

	requireWarningType(t, NewEngine().Generate(payload), TypeLowRetrievalScore)
}

func TestLowRetrievalScoreSkipsDistanceAndUnknownScores(t *testing.T) {
	testCases := []struct {
		name      string
		scoreType string
		direction string
	}{
		{name: "distance", scoreType: "distance", direction: "lower_is_better"},
		{name: "unknown tuple score", scoreType: "unknown", direction: "unknown"},
		{name: "distance type without direction", scoreType: "distance", direction: ""},
		{name: "custom type without direction", scoreType: "custom_metric", direction: ""},
		{name: "invalid direction", scoreType: "similarity", direction: "sideways"},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			payload := basePayload(
				"trace_non_comparable_score",
				"What is the refund policy?",
				[]models.JSONMap{
					semanticChunk(
						"semantic",
						"The refund policy allows returns.",
						0.1,
						testCase.scoreType,
						testCase.direction,
					),
				},
				"The refund policy allows returns.",
			)

			requireNoWarningType(t, NewEngine().Generate(payload), TypeLowRetrievalScore)
		})
	}
}

func TestLowRetrievalScoreIgnoresDistanceInMixedScores(t *testing.T) {
	payload := basePayload(
		"trace_mixed_score_semantics",
		"What is the refund policy?",
		[]models.JSONMap{
			semanticChunk(
				"distance",
				"The refund policy allows returns.",
				0.99,
				"distance",
				"lower_is_better",
			),
			semanticChunk(
				"similarity",
				"The refund policy allows returns.",
				0.1,
				"similarity",
				"higher_is_better",
			),
		},
		"The refund policy allows returns.",
	)

	warning := requireWarningType(t, NewEngine().Generate(payload), TypeLowRetrievalScore)
	if warning.Details["max_score"] != 0.1 {
		t.Fatalf("expected only comparable similarity score, got %#v", warning.Details)
	}
}

func TestLowRetrievalScoreSupportsHigherIsBetterScoresBelowNegativeOne(t *testing.T) {
	payload := basePayload(
		"trace_negative_dot_product",
		"What is the refund policy?",
		[]models.JSONMap{
			semanticChunk(
				"negative-score",
				"The refund policy allows returns.",
				-2.5,
				"dot_product",
				"higher_is_better",
			),
		},
		"The refund policy allows returns.",
	)

	warning := requireWarningType(t, NewEngine().Generate(payload), TypeLowRetrievalScore)
	if warning.Details["max_score"] != -2.5 {
		t.Fatalf("expected max_score=-2.5, got %#v", warning.Details["max_score"])
	}
}

func TestGenerateNumericMismatchWarning(t *testing.T) {
	payload := basePayload(
		"trace_numeric_mismatch",
		"What is the refund window?",
		[]models.JSONMap{
			chunk("chunk_refund_current", "Customers may request a refund within 30 days of purchase.", 0.93, "refund_policy.md"),
			chunk("chunk_returns_general", "Refund requests must be submitted through the customer support portal.", 0.78, "returns_process.md"),
		},
		"Customers may request a refund within 60 days of purchase.",
	)

	warnings := NewEngine().Generate(payload)

	warning := requireWarningType(t, warnings, TypeNumericMismatch)

	requireStringPtrValue(t, warning.Category, "grounding", "category")
	requireStringPtrValue(t, warning.RuleVersion, "2", "rule_version")

	if warning.Confidence == nil {
		t.Fatalf("expected numeric_mismatch confidence to be set")
	}

	if *warning.Confidence < 0.89 {
		t.Fatalf("expected numeric_mismatch confidence >= 0.89, got %v", *warning.Confidence)
	}

	if len(warning.Evidence) == 0 {
		t.Fatalf("expected numeric_mismatch evidence to be populated")
	}

	if !hasEvidenceType(warning, "numeric_value") {
		t.Fatalf("expected numeric_mismatch to include numeric_value evidence, got %#v", warning.Evidence)
	}

	if warning.Details["answer_value"] != "60 days" {
		t.Fatalf("expected answer_value=60 days, got %#v", warning.Details["answer_value"])
	}

	if warning.Details["retrieved_value"] != "30 days" {
		t.Fatalf("expected retrieved_value=30 days, got %#v", warning.Details["retrieved_value"])
	}
}

func TestNumericMismatchIgnoresElapsedTimeWithinPolicyWindow(t *testing.T) {
	payload := basePayload(
		"trace_numeric_mismatch_elapsed_time",
		"I bought a physical product 20 days ago. Can I still return it?",
		[]models.JSONMap{
			chunk(
				"chunk_refund_current",
				"Customers may return most physical products within 30 days of the purchase date.",
				0.93,
				"refund_policy_current.md",
			),
			chunk(
				"chunk_refund_legacy",
				"Physical products can only be returned within 14 days of the purchase date.",
				0.81,
				"refund_policy_legacy.md",
			),
		},
		"Yes. The current refund policy says customers may return most physical products within 30 days of purchase, so a purchase from 20 days ago is still within the return window.",
	)

	warnings := NewEngine().Generate(payload)

	requireNoWarningType(t, warnings, TypeNumericMismatch)

	// The retrieved context still contains a real current-vs-legacy conflict.
	// That should remain a conflicting_chunks warning.
	requireWarningType(t, warnings, TypeConflictingChunks)
}

func TestNumericMismatchStillDetectsWrongPolicyWindow(t *testing.T) {
	payload := basePayload(
		"trace_numeric_mismatch_wrong_window",
		"How long do customers have to return a physical product?",
		[]models.JSONMap{
			chunk(
				"chunk_refund_current",
				"Customers may return most physical products within 30 days of the purchase date.",
				0.93,
				"refund_policy_current.md",
			),
		},
		"Customers have 45 days to return a physical product.",
	)

	warnings := NewEngine().Generate(payload)

	warning := requireWarningType(t, warnings, TypeNumericMismatch)

	if warning.Details["answer_value"] != "45 days" {
		t.Fatalf("expected answer_value=45 days, got %#v", warning.Details["answer_value"])
	}

	if warning.Details["retrieved_value"] != "30 days" {
		t.Fatalf("expected retrieved_value=30 days, got %#v", warning.Details["retrieved_value"])
	}
}

func TestNumericMismatchDetectsWrongProcessingTimeAgainstRange(t *testing.T) {
	payload := basePayload(
		"trace_numeric_mismatch_processing_time",
		"How long do refunds take to process?",
		[]models.JSONMap{
			chunk(
				"chunk_refund_processing",
				"Refunds are usually processed within 5 to 10 business days after the returned item is received.",
				0.93,
				"refund_policy_current.md",
			),
		},
		"Refunds are usually processed within 2 business days.",
	)

	warnings := NewEngine().Generate(payload)

	warning := requireWarningType(t, warnings, TypeNumericMismatch)

	if warning.Details["answer_value"] != "2 business days" {
		t.Fatalf("expected answer_value=2 business days, got %#v", warning.Details["answer_value"])
	}

	if warning.Details["retrieved_value"] != "5-10 business days" {
		t.Fatalf("expected retrieved_value=5-10 business days, got %#v", warning.Details["retrieved_value"])
	}
}

func TestNumericMismatchIgnoresMatchingNaturalLanguageRange(t *testing.T) {
	payload := basePayload(
		"trace_numeric_mismatch_matching_range",
		"How long do refunds take to process?",
		[]models.JSONMap{
			chunk(
				"chunk_refund_processing",
				"Refunds are usually processed within 5 to 10 business days after the returned item is received.",
				0.93,
				"refund_policy_current.md",
			),
		},
		"Refunds are usually processed within 5 to 10 business days after the returned item is received.",
	)

	warnings := NewEngine().Generate(payload)

	requireNoWarningType(t, warnings, TypeNumericMismatch)
}

func TestConflictingChunksPrefersQueryRelevantProcessingConflict(t *testing.T) {
	payload := basePayload(
		"trace_conflicting_chunks_processing_relevance",
		"How long do refunds usually take to process?",
		[]models.JSONMap{
			chunk(
				"chunk_processing_current",
				"Refunds are usually processed within 5 to 10 business days after the returned item is received by the warehouse.",
				0.91,
				"refund_policy_current.md",
			),
			chunk(
				"chunk_processing_legacy",
				"Refunds are processed within 15 to 20 business days after warehouse inspection.",
				0.88,
				"refund_policy_legacy.md",
			),
			chunk(
				"chunk_return_window_current",
				"Customers may return most physical products within 30 days of the purchase date.",
				0.87,
				"refund_policy_current.md",
			),
			chunk(
				"chunk_return_window_legacy",
				"Physical products can only be returned within 14 days of the purchase date.",
				0.86,
				"refund_policy_legacy.md",
			),
		},
		"Refunds are usually processed within 5 to 10 business days after the returned item is received by the warehouse.",
	)

	warnings := NewEngine().Generate(payload)
	warning := requireWarningType(t, warnings, TypeConflictingChunks)

	values, ok := warning.Details["detected_values"].([]string)
	if !ok {
		t.Fatalf("expected detected_values []string, got %#v", warning.Details["detected_values"])
	}

	if !containsString(values, "5-10 business days") || !containsString(values, "15-20 business days") {
		t.Fatalf("expected detected values to contain processing ranges, got %#v", values)
	}

	if len(values) == 2 && containsString(values, "30 days") && containsString(values, "14 days") {
		t.Fatalf("expected processing conflict to be preferred over return-window conflict, got %#v", values)
	}

	if warning.Details["query_matched_terms"] == nil {
		t.Fatalf("expected query_matched_terms in conflicting_chunks details")
	}

	if warning.Details["relevance_score"] == nil {
		t.Fatalf("expected relevance_score in conflicting_chunks details")
	}
}

func TestConflictingChunksSkipsUnrelatedPhysicalReturnWindowForDigitalQuery(t *testing.T) {
	payload := basePayload(
		"trace_conflicting_chunks_digital_query",
		"Can I get a refund for downloadable software if I never opened it?",
		[]models.JSONMap{
			chunk(
				"chunk_digital_goods",
				"Downloadable software, license keys, digital gift cards, and other digital goods are generally non-refundable after purchase. A refund may be considered only when the digital item was not delivered, the license key was invalid, or a duplicate charge occurred.",
				0.92,
				"digital_goods_policy.md",
			),
			chunk(
				"chunk_return_window_current",
				"Customers may return most physical products within 30 days of the purchase date.",
				0.75,
				"refund_policy_current.md",
			),
			chunk(
				"chunk_return_window_legacy",
				"Physical products can only be returned within 14 days of the purchase date.",
				0.72,
				"refund_policy_legacy.md",
			),
		},
		"Downloadable software is generally non-refundable after purchase. A refund may be considered only when the digital item was not delivered, the license key was invalid, or a duplicate charge occurred.",
	)

	warnings := NewEngine().Generate(payload)

	requireNoWarningType(t, warnings, TypeConflictingChunks)
	requireNoWarningType(t, warnings, TypeNumericMismatch)
	requireNoWarningType(t, warnings, TypeAnswerNotGrounded)
}

func TestConflictingChunksKeepsReturnWindowConflictWhenQueryRelevant(t *testing.T) {
	payload := basePayload(
		"trace_conflicting_chunks_return_window_relevant",
		"How many days do customers have to return a physical product?",
		[]models.JSONMap{
			chunk(
				"chunk_return_window_current",
				"Customers may return most physical products within 30 days of the purchase date.",
				0.93,
				"refund_policy_current.md",
			),
			chunk(
				"chunk_return_window_legacy",
				"Physical products can only be returned within 14 days of the purchase date.",
				0.89,
				"refund_policy_legacy.md",
			),
		},
		"One retrieved refund policy says customers may return most physical products within 30 days. Another archived legacy refund policy says physical products can only be returned within 14 days.",
	)

	warnings := NewEngine().Generate(payload)
	warning := requireWarningType(t, warnings, TypeConflictingChunks)

	values, ok := warning.Details["detected_values"].([]string)
	if !ok {
		t.Fatalf("expected detected_values []string, got %#v", warning.Details["detected_values"])
	}

	if !containsString(values, "30 days") || !containsString(values, "14 days") {
		t.Fatalf("expected detected values to contain 30 days and 14 days, got %#v", values)
	}
}

func TestConflictingChunksSuppressesRefundProcessingConflictForDamagedQuery(t *testing.T) {
	payload := basePayload(
		"trace_conflicting_chunks_damaged_query",
		"My item arrived damaged but I threw away the original box. What should I do?",
		[]models.JSONMap{
			chunk(
				"chunk_damaged_policy",
				"# Damaged Items Policy Customers should report damaged or defective items within 7 days of delivery. A damaged item report should include the order number, a description of the issue, and clear photos of the damaged product and shipping box if available. Original packaging is recommended because it helps the warehouse inspect shipping damage, but support may still review a damaged item claim if the packaging was discarded. If the claim is approved, support may offer a replacement, repair, store credit, or refund.",
				0.93,
				"damaged_items_policy.md",
			),
			chunk(
				"chunk_refund_processing_current",
				"Refunds are usually processed within 5 to 10 business days after the returned item is received by the warehouse.",
				0.82,
				"refund_policy_current.md",
			),
			chunk(
				"chunk_refund_processing_legacy",
				"Refunds are processed within 15 to 20 business days after warehouse inspection.",
				0.79,
				"refund_policy_legacy.md",
			),
		},
		"You should contact support and provide your order number, a description of the damage, and photos if available. Original packaging is recommended, but support may still review the claim if the box was discarded.",
	)

	warnings := NewEngine().Generate(payload)

	requireNoWarningType(t, warnings, TypeConflictingChunks)
	requireNoWarningType(t, warnings, TypeNumericMismatch)
	requireNoWarningType(t, warnings, TypeAnswerNotGrounded)
}

func TestConflictingChunksKeepsRefundProcessingConflictWhenQueryAsksProcessingTime(t *testing.T) {
	payload := basePayload(
		"trace_conflicting_chunks_processing_query",
		"How long do refunds usually take to process?",
		[]models.JSONMap{
			chunk(
				"chunk_refund_processing_current",
				"Refunds are usually processed within 5 to 10 business days after the returned item is received by the warehouse.",
				0.93,
				"refund_policy_current.md",
			),
			chunk(
				"chunk_refund_processing_legacy",
				"Refunds are processed within 15 to 20 business days after warehouse inspection.",
				0.89,
				"refund_policy_legacy.md",
			),
		},
		"Refunds are usually processed within 5 to 10 business days after the returned item is received by the warehouse.",
	)

	warnings := NewEngine().Generate(payload)
	warning := requireWarningType(t, warnings, TypeConflictingChunks)

	values, ok := warning.Details["detected_values"].([]string)
	if !ok {
		t.Fatalf("expected detected_values []string, got %#v", warning.Details["detected_values"])
	}

	if !containsString(values, "5-10 business days") || !containsString(values, "15-20 business days") {
		t.Fatalf("expected detected values to contain processing ranges, got %#v", values)
	}
}

func TestGenerateWeakQueryChunkOverlapWarning(t *testing.T) {
	payload := basePayload(
		"trace_weak_overlap",
		"What is the refund window?",
		[]models.JSONMap{
			chunk("chunk_shipping_standard", "Standard shipping usually takes 5 to 7 business days after an order has shipped.", 0.88, "shipping_policy.md"),
			chunk("chunk_warranty_general", "Warranty coverage applies to manufacturing defects for eligible physical products.", 0.81, "warranty_policy.md"),
		},
		"I could not find enough information in the retrieved context to answer the refund window question.",
	)

	warnings := NewEngine().Generate(payload)

	warning := requireWarningType(t, warnings, TypeWeakQueryChunkOverlap)

	requireStringPtrValue(t, warning.Category, "retrieval", "category")
	requireStringPtrValue(t, warning.RuleVersion, "2", "rule_version")

	if warning.Confidence == nil {
		t.Fatalf("expected weak_query_chunk_overlap confidence to be set")
	}

	if *warning.Confidence < 0.74 {
		t.Fatalf("expected weak_query_chunk_overlap confidence >= 0.74, got %v", *warning.Confidence)
	}

	if len(warning.Evidence) == 0 {
		t.Fatalf("expected weak_query_chunk_overlap evidence to be populated")
	}

	if !hasEvidenceType(warning, "query_text") {
		t.Fatalf("expected weak_query_chunk_overlap to include query_text evidence, got %#v", warning.Evidence)
	}

	if !hasEvidenceType(warning, "overlap_measure") {
		t.Fatalf("expected weak_query_chunk_overlap to include overlap_measure evidence, got %#v", warning.Evidence)
	}

	if warning.Details["best_overlap_ratio"] == nil {
		t.Fatalf("expected best_overlap_ratio in details")
	}
}

func TestGenerateAnswerNotGroundedV2Warning(t *testing.T) {
	payload := basePayload(
		"trace_answer_not_grounded",
		"What is the refund window?",
		[]models.JSONMap{
			chunk("chunk_refund_current", "Customers may request a refund within 30 days of purchase.", 0.93, "refund_policy.md"),
			chunk("chunk_returns_general", "Refund requests must be submitted through the customer support portal.", 0.78, "returns_process.md"),
		},
		"Customers may request a refund within 30 days of purchase. Original shipping fees are refundable.",
	)

	warnings := NewEngine().Generate(payload)

	warning := requireWarningType(t, warnings, TypeAnswerNotGrounded)

	requireStringPtrValue(t, warning.Category, "grounding", "category")
	requireStringPtrValue(t, warning.RuleVersion, "2", "rule_version")
	requireStringPtrValue(t, warning.Title, "Answer contains an unsupported claim", "title")

	if warning.Confidence == nil {
		t.Fatalf("expected answer_not_grounded confidence to be set")
	}

	if *warning.Confidence < 0.79 {
		t.Fatalf("expected answer_not_grounded confidence >= 0.79, got %v", *warning.Confidence)
	}

	if len(warning.Evidence) == 0 {
		t.Fatalf("expected answer_not_grounded evidence to be populated")
	}

	if !hasEvidenceLabel(warning, "Unsupported answer claim") {
		t.Fatalf("expected answer_not_grounded to include unsupported answer claim evidence, got %#v", warning.Evidence)
	}

	if warning.Details["claim"] != "Original shipping fees are refundable." {
		t.Fatalf("expected unsupported claim in details, got %#v", warning.Details["claim"])
	}
}

func TestGenerateConflictingChunksV2Warning(t *testing.T) {
	payload := basePayload(
		"trace_conflicting_chunks",
		"What is the refund window?",
		[]models.JSONMap{
			chunk("chunk_refund_current", "Customers may request a refund within 30 days of purchase.", 0.93, "refund_policy.md"),
			chunk("chunk_refund_legacy", "Customers may request a refund within 60 days of purchase under the legacy refund policy.", 0.89, "legacy_refund_policy.md"),
		},
		"I could not determine a single refund window because the retrieved context is inconsistent.",
	)

	warnings := NewEngine().Generate(payload)

	warning := requireWarningType(t, warnings, TypeConflictingChunks)

	requireStringPtrValue(t, warning.Category, "conflict", "category")
	requireStringPtrValue(t, warning.RuleVersion, "2", "rule_version")
	requireStringPtrValue(t, warning.Title, "Retrieved chunks contain conflicting values", "title")

	if warning.Confidence == nil {
		t.Fatalf("expected conflicting_chunks confidence to be set")
	}

	if *warning.Confidence < 0.87 {
		t.Fatalf("expected conflicting_chunks confidence >= 0.87, got %v", *warning.Confidence)
	}

	if len(warning.Evidence) == 0 {
		t.Fatalf("expected conflicting_chunks evidence to be populated")
	}

	if !hasEvidenceType(warning, "conflict_pair") {
		t.Fatalf("expected conflicting_chunks to include conflict_pair evidence, got %#v", warning.Evidence)
	}

	values, ok := warning.Details["detected_values"].([]string)
	if !ok {
		t.Fatalf("expected detected_values []string, got %#v", warning.Details["detected_values"])
	}

	if len(values) != 2 {
		t.Fatalf("expected two detected values, got %#v", values)
	}

	if !containsString(values, "30 days") || !containsString(values, "60 days") {
		t.Fatalf("expected detected values to contain 30 days and 60 days, got %#v", values)
	}
}

func basePayload(traceID string, query string, chunks []models.JSONMap, answer string) models.TracePayload {
	return models.TracePayload{
		Trace: models.TraceRecord{
			TraceID: traceID,
			Name:    traceID,
			Status:  "ok",
			Input: models.JSONMap{
				"query": query,
			},
			Output: models.JSONMap{
				"answer": answer,
			},
			Metadata:  models.JSONMap{},
			StartedAt: "2026-07-06T00:00:00Z",
		},
		Spans: []models.Span{
			{
				SpanID:  "span_retrieval",
				TraceID: traceID,
				Type:    "retrieval",
				Name:    "test_retrieval",
				Status:  "ok",
				Input: models.JSONMap{
					"query": query,
				},
				Output: models.JSONMap{
					"chunks": chunks,
				},
				Metadata:  models.JSONMap{},
				StartedAt: "2026-07-06T00:00:00Z",
			},
			{
				SpanID:  "span_llm",
				TraceID: traceID,
				Type:    "llm",
				Name:    "test_llm",
				Status:  "ok",
				Input: models.JSONMap{
					"prompt": "Answer the user question using the retrieved context.",
				},
				Output: models.JSONMap{
					"response": answer,
				},
				Metadata:  models.JSONMap{},
				StartedAt: "2026-07-06T00:00:00Z",
			},
		},
	}
}

func chunk(id string, text string, score float64, source string) models.JSONMap {
	return models.JSONMap{
		"id":    id,
		"text":  text,
		"score": score,
		"metadata": models.JSONMap{
			"source": source,
		},
	}
}

func semanticChunk(
	id string,
	text string,
	score float64,
	scoreType string,
	scoreDirection string,
) models.JSONMap {
	result := chunk(id, text, score, "policy.md")
	result["score_type"] = scoreType
	result["score_direction"] = scoreDirection
	return result
}

func requireWarningType(t *testing.T, warnings []models.Warning, warningType string) models.Warning {
	t.Helper()

	for _, warning := range warnings {
		if warning.Type == warningType {
			return warning
		}
	}

	t.Fatalf("expected warning type %q, got warning types %v", warningType, warningTypes(warnings))

	return models.Warning{}
}

func requireNoWarningType(t *testing.T, warnings []models.Warning, warningType string) {
	t.Helper()

	for _, warning := range warnings {
		if warning.Type == warningType {
			t.Fatalf(
				"expected no warning type %q, got warning types %v",
				warningType,
				warningTypes(warnings),
			)
		}
	}
}

func warningTypes(warnings []models.Warning) []string {
	result := make([]string, 0, len(warnings))

	for _, warning := range warnings {
		result = append(result, warning.Type)
	}

	return result
}

func requireStringPtrValue(t *testing.T, actual *string, expected string, fieldName string) {
	t.Helper()

	if actual == nil {
		t.Fatalf("expected %s to be %q, got nil", fieldName, expected)
	}

	if *actual != expected {
		t.Fatalf("expected %s to be %q, got %q", fieldName, expected, *actual)
	}
}

func hasEvidenceType(warning models.Warning, evidenceType string) bool {
	for _, evidence := range warning.Evidence {
		if evidence.Type == evidenceType {
			return true
		}
	}

	return false
}

func hasEvidenceLabel(warning models.Warning, label string) bool {
	for _, evidence := range warning.Evidence {
		if evidence.Label == label {
			return true
		}
	}

	return false
}

func containsString(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}

	return false
}
