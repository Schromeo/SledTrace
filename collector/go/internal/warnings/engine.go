package warnings

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"regexp"
	"sort"
	"strings"
	"time"

	"sledtrace-collector/internal/models"
)

const (
	TypeConflictingChunks     = "conflicting_chunks"
	TypeNoRetrievedChunks     = "no_retrieved_chunks"
	TypeLowRetrievalScore     = "low_retrieval_score"
	TypeWeakQueryChunkOverlap = "weak_query_chunk_overlap"
	TypeDuplicateChunks       = "duplicate_chunks"
	TypeAnswerNotGrounded     = "answer_not_grounded"
	TypeNumericMismatch       = "numeric_mismatch"

	SeverityInfo    = "info"
	SeverityWarning = "warning"
	SeverityError   = "error"

	DefaultLowScoreThreshold = 0.5
)

type Engine struct{}

func NewEngine() *Engine {
	return &Engine{}
}

func (e *Engine) Generate(payload models.TracePayload) []models.Warning {
	result := make([]models.Warning, 0)

	result = append(result, e.detectNoRetrievedChunks(payload)...)
	result = append(result, e.detectLowRetrievalScore(payload)...)
	result = append(result, e.detectWeakQueryChunkOverlap(payload)...)
	result = append(result, e.detectDuplicateChunks(payload)...)
	result = append(result, e.detectConflictingChunks(payload)...)
	result = append(result, e.detectNumericMismatch(payload)...)
	result = append(result, e.detectAnswerNotGrounded(payload)...)

	return enrichWarnings(result)
}

func enrichWarnings(warnings []models.Warning) []models.Warning {
	for i := range warnings {
		applyWarningSchemaV2Defaults(&warnings[i])
	}

	return warnings
}

func applyWarningSchemaV2Defaults(warning *models.Warning) {
	if warning == nil {
		return
	}

	if warning.SchemaVersion == nil {
		warning.SchemaVersion = stringPtr("2")
	}

	if warning.RuleID == nil {
		warning.RuleID = stringPtr(warning.Type)
	}

	if warning.RuleVersion == nil {
		warning.RuleVersion = stringPtr("1")
	}

	if warning.Title == nil {
		warning.Title = stringPtr(defaultWarningTitle(warning.Type))
	}

	if warning.Category == nil {
		warning.Category = stringPtr(defaultWarningCategory(warning.Type))
	}

	if warning.Explanation == nil {
		warning.Explanation = stringPtr(defaultWarningExplanation(*warning))
	}

	if warning.RecommendedAction == nil {
		warning.RecommendedAction = stringPtr(defaultRecommendedAction(warning.Type))
	}

	if len(warning.Signals) == 0 {
		warning.Signals = defaultWarningSignals(*warning)
	}

	if len(warning.Evidence) == 0 {
		warning.Evidence = defaultWarningEvidence(*warning)
	}

	if len(warning.Diagnostics) == 0 {
		warning.Diagnostics = defaultWarningDiagnostics(*warning)
	}
}

func defaultWarningTitle(warningType string) string {
	switch warningType {
	case TypeNoRetrievedChunks:
		return "No retrieved chunks"
	case TypeLowRetrievalScore:
		return "Low retrieval score"
	case TypeWeakQueryChunkOverlap:
		return "Weak query/chunk overlap"
	case TypeDuplicateChunks:
		return "Duplicate retrieved chunks"
	case TypeConflictingChunks:
		return "Conflicting retrieved chunks"
	case TypeAnswerNotGrounded:
		return "Answer may not be grounded"
	case TypeNumericMismatch:
		return "Numeric mismatch between answer and retrieved context"
	default:
		return strings.ReplaceAll(warningType, "_", " ")
	}
}

func defaultWarningCategory(warningType string) string {
	switch warningType {
	case TypeNoRetrievedChunks, TypeLowRetrievalScore, TypeWeakQueryChunkOverlap, TypeDuplicateChunks:
		return "retrieval"
	case TypeConflictingChunks:
		return "conflict"
	case TypeAnswerNotGrounded, TypeNumericMismatch:
		return "grounding"
	default:
		return "diagnostic"
	}
}

func defaultWarningExplanation(warning models.Warning) string {
	if reason, ok := warning.Details["reason"].(string); ok && strings.TrimSpace(reason) != "" {
		return reason
	}

	return warning.Message
}

func defaultRecommendedAction(warningType string) string {
	switch warningType {
	case TypeNoRetrievedChunks:
		return "Inspect the retrieval step and verify that the query, index, and filters can return at least one relevant chunk."
	case TypeLowRetrievalScore:
		return "Inspect query quality and retrieval ranking, then verify that the retriever is surfacing relevant context."
	case TypeWeakQueryChunkOverlap:
		return "Inspect retrieval query construction, chunk content, and ranking because the retrieved text does not appear to cover important query terms."
	case TypeDuplicateChunks:
		return "Inspect chunking and deduplication so repeated context does not crowd out distinct evidence."
	case TypeConflictingChunks:
		return "Inspect source freshness and ranking to determine which retrieved evidence should be trusted."
	case TypeAnswerNotGrounded:
		return "Compare the final answer against the retrieved context and check whether the model used unsupported claims."
	case TypeNumericMismatch:
		return "Compare the final answer against the retrieved chunks and verify whether the model used an outdated or unsupported numeric value."
	default:
		return "Inspect the trace details to understand why this diagnostic was raised."
	}
}

func defaultWarningSignals(warning models.Warning) []models.DiagnosticSignal {
	switch warning.Type {
	case TypeNoRetrievedChunks:
		return []models.DiagnosticSignal{{
			SignalID:   "retrieved_chunk_count_zero",
			Label:      "Retrieval returned zero chunks",
			Observed:   0,
			Expected:   ">0",
			Comparator: "equal",
			Strength:   "strong",
		}}
	case TypeLowRetrievalScore:
		return []models.DiagnosticSignal{{
			SignalID:   "top_retrieval_score_below_threshold",
			Label:      "Top retrieval score is below threshold",
			Observed:   warning.Details["max_score"],
			Expected:   warning.Details["threshold"],
			Comparator: "below_threshold",
			Strength:   "strong",
		}}
	case TypeDuplicateChunks:
		return []models.DiagnosticSignal{{
			SignalID:   "duplicate_chunk_groups_detected",
			Label:      "Duplicate retrieved chunk groups detected",
			Observed:   len(jsonMapSlice(warning.Details["duplicate_groups"])),
			Comparator: "greater_than_zero",
			Strength:   "moderate",
		}}
	case TypeConflictingChunks:
		return []models.DiagnosticSignal{{
			SignalID:   "conflicting_retrieved_values_detected",
			Label:      "Retrieved chunks contain conflicting values",
			Observed:   stringSliceFromAny(warning.Details["detected_values"]),
			Comparator: "multiple_distinct_values",
			Strength:   "strong",
		}}
	case TypeAnswerNotGrounded:
		return []models.DiagnosticSignal{{
			SignalID:   "unsupported_answer_claim_detected",
			Label:      "Answer contains unsupported claim values",
			Observed:   stringSliceFromAny(warning.Details["unsupported_days"]),
			Comparator: "not_present_in_retrieved_context",
			Strength:   "moderate",
		}}
	default:
		return nil
	}
}

func defaultWarningEvidence(warning models.Warning) []models.EvidenceItem {
	switch warning.Type {
	case TypeLowRetrievalScore:
		return []models.EvidenceItem{{
			EvidenceID: newEvidenceID(),
			Type:       "retrieval_stat",
			Label:      "Top retrieval score below configured threshold",
			SpanID:     warning.SpanID,
			Snippet: fmt.Sprintf(
				"max_score=%v threshold=%v",
				warning.Details["max_score"],
				warning.Details["threshold"],
			),
			Attributes: models.JSONMap{
				"max_score": warning.Details["max_score"],
				"threshold": warning.Details["threshold"],
			},
		}}
	case TypeDuplicateChunks:
		groups := jsonMapSlice(warning.Details["duplicate_groups"])
		return []models.EvidenceItem{{
			EvidenceID: newEvidenceID(),
			Type:       "retrieval_stat",
			Label:      "Duplicate retrieved chunk groups",
			Snippet:    fmt.Sprintf("%d duplicate groups detected", len(groups)),
			Attributes: models.JSONMap{
				"duplicate_groups": groups,
			},
		}}
	case TypeConflictingChunks:
		values := stringSliceFromAny(warning.Details["detected_values"])
		return []models.EvidenceItem{{
			EvidenceID: newEvidenceID(),
			Type:       "conflict_pair",
			Label:      "Conflicting values detected in retrieved chunks",
			Snippet:    strings.Join(values, " vs "),
			Attributes: models.JSONMap{
				"detected_values": values,
				"source_chunks":   warning.Details["source_chunks"],
			},
		}}
	case TypeAnswerNotGrounded:
		answer, _ := warning.Details["answer"].(string)
		if strings.TrimSpace(answer) == "" {
			return nil
		}

		return []models.EvidenceItem{{
			EvidenceID: newEvidenceID(),
			Type:       "answer_snippet",
			Label:      "Final answer under review",
			SpanID:     warning.SpanID,
			Snippet:    answer,
		}}
	default:
		return nil
	}
}

func defaultWarningDiagnostics(warning models.Warning) []models.DiagnosticObject {
	switch warning.Type {
	case TypeConflictingChunks:
		values := stringSliceFromAny(warning.Details["detected_values"])
		if len(values) == 0 {
			return nil
		}

		return []models.DiagnosticObject{{
			DiagnosticObjectID: newDiagnosticObjectID(),
			Type:               "conflict_group",
			Label:              "Conflicting retrieved values",
			Normalized: models.JSONMap{
				"values": values,
			},
			Attributes: models.JSONMap{
				"source_chunks": warning.Details["source_chunks"],
			},
		}}
	case TypeAnswerNotGrounded:
		unsupported := stringSliceFromAny(warning.Details["unsupported_days"])
		if len(unsupported) == 0 {
			return nil
		}

		return []models.DiagnosticObject{{
			DiagnosticObjectID: newDiagnosticObjectID(),
			Type:               "numeric_claim",
			Label:              "Unsupported answer values",
			SpanID:             warning.SpanID,
			Text:               strings.Join(unsupported, ", "),
			Normalized: models.JSONMap{
				"unsupported_days": unsupported,
			},
		}}
	default:
		return nil
	}
}

func stringPtr(value string) *string {
	return &value
}

func float64Ptr(value float64) *float64 {
	return &value
}

func stringSliceFromAny(raw any) []string {
	switch values := raw.(type) {
	case []string:
		result := make([]string, 0, len(values))
		for _, value := range values {
			if strings.TrimSpace(value) == "" {
				continue
			}

			result = append(result, value)
		}
		return result
	case []any:
		result := make([]string, 0, len(values))
		for _, value := range values {
			text, ok := value.(string)
			if !ok || strings.TrimSpace(text) == "" {
				continue
			}

			result = append(result, text)
		}
		return result
	default:
		return nil
	}
}

func jsonMapSlice(raw any) []models.JSONMap {
	switch values := raw.(type) {
	case []models.JSONMap:
		result := make([]models.JSONMap, 0, len(values))
		for _, value := range values {
			result = append(result, value)
		}
		return result
	case []map[string]any:
		result := make([]models.JSONMap, 0, len(values))
		for _, value := range values {
			result = append(result, models.JSONMap(value))
		}
		return result
	case []any:
		result := make([]models.JSONMap, 0, len(values))
		for _, value := range values {
			item, ok := value.(map[string]any)
			if !ok {
				continue
			}

			result = append(result, models.JSONMap(item))
		}
		return result
	default:
		return nil
	}
}

func newEvidenceID() string {
	return newPrefixedID("evidence")
}

func newDiagnosticObjectID() string {
	return newPrefixedID("diag")
}

func (e *Engine) detectNoRetrievedChunks(payload models.TracePayload) []models.Warning {
	result := make([]models.Warning, 0)

	for _, span := range payload.Spans {
		if span.Type != "retrieval" {
			continue
		}

		chunks := extractRetrievedChunksFromSpan(span)
		if len(chunks) > 0 {
			continue
		}

		spanID := span.SpanID

		result = append(result, models.Warning{
			WarningID: newWarningID(),
			TraceID:   payload.Trace.TraceID,
			SpanID:    &spanID,
			Type:      TypeNoRetrievedChunks,
			Severity:  SeverityWarning,
			Message:   "Retrieval span returned no chunks.",
			Details: models.JSONMap{
				"rule":      TypeNoRetrievedChunks,
				"span_id":   span.SpanID,
				"span_name": span.Name,
				"reason":    "retrieval span output did not contain any retrieved chunks",
			},
			CreatedAt: time.Now().UTC().Format(time.RFC3339Nano),
		})
	}

	return result
}

func (e *Engine) detectLowRetrievalScore(payload models.TracePayload) []models.Warning {
	result := make([]models.Warning, 0)

	for _, span := range payload.Spans {
		if span.Type != "retrieval" {
			continue
		}

		chunks := extractRetrievedChunksFromSpan(span)
		if len(chunks) == 0 {
			continue
		}

		threshold := getLowScoreThreshold(span)

		scoredChunks := make([]models.JSONMap, 0)
		maxScore := 0.0
		scoredCount := 0

		for _, chunk := range chunks {
			scoreValue := higherIsBetterScore(chunk)
			if scoreValue == nil {
				continue
			}

			score := *scoreValue
			if scoredCount == 0 || score > maxScore {
				maxScore = score
			}
			scoredCount++

			scoredChunks = append(scoredChunks, models.JSONMap{
				"chunk_id": chunk.ChunkID,
				"score":    score,
			})
		}

		// If no score was recorded, skip this rule.
		// Some retrievers do not expose normalized relevance scores.
		if scoredCount == 0 {
			continue
		}

		// MVP rule:
		// If even the best retrieved chunk is below threshold,
		// retrieval quality is probably weak.
		if maxScore >= threshold {
			continue
		}

		spanID := span.SpanID

		result = append(result, models.Warning{
			WarningID: newWarningID(),
			TraceID:   payload.Trace.TraceID,
			SpanID:    &spanID,
			Type:      TypeLowRetrievalScore,
			Severity:  SeverityWarning,
			Message:   "Retrieved chunks have low relevance scores.",
			Details: models.JSONMap{
				"rule":         TypeLowRetrievalScore,
				"span_id":      span.SpanID,
				"span_name":    span.Name,
				"threshold":    threshold,
				"max_score":    maxScore,
				"chunk_scores": scoredChunks,
				"reason":       "highest retrieved chunk score is below threshold",
			},
			CreatedAt: time.Now().UTC().Format(time.RFC3339Nano),
		})
	}

	return result
}

type queryChunkOverlapResult struct {
	Chunk        retrievedChunk
	ChunkRank    int
	MatchedTerms []string
	MissingTerms []string
	OverlapRatio float64
}

func (e *Engine) detectWeakQueryChunkOverlap(payload models.TracePayload) []models.Warning {
	query, querySpanID := extractTraceQuery(payload)
	query = strings.TrimSpace(query)
	if query == "" {
		return nil
	}

	queryTerms := importantQueryTerms(query)
	if len(queryTerms) == 0 {
		return nil
	}

	chunks := extractRetrievedChunks(payload.Spans)
	if len(chunks) == 0 {
		return nil
	}

	topK := 3
	if len(chunks) < topK {
		topK = len(chunks)
	}

	results := make([]queryChunkOverlapResult, 0, topK)
	bestOverlap := 0.0
	totalOverlap := 0.0
	allMatchedTerms := map[string]bool{}

	for i := 0; i < topK; i++ {
		chunk := chunks[i]
		chunkText := strings.TrimSpace(chunk.Text)
		if chunkText == "" {
			continue
		}

		chunkTerms := importantContextTerms(chunkText)
		matchedTerms := sharedContextTerms(queryTerms, chunkTerms)
		missing := missingTerms(queryTerms, matchedTerms)

		overlapRatio := 0.0
		if len(queryTerms) > 0 {
			overlapRatio = float64(len(matchedTerms)) / float64(len(queryTerms))
		}

		for _, term := range matchedTerms {
			allMatchedTerms[term] = true
		}

		if overlapRatio > bestOverlap {
			bestOverlap = overlapRatio
		}

		totalOverlap += overlapRatio

		results = append(results, queryChunkOverlapResult{
			Chunk:        chunk,
			ChunkRank:    i + 1,
			MatchedTerms: matchedTerms,
			MissingTerms: missing,
			OverlapRatio: overlapRatio,
		})
	}

	if len(results) == 0 {
		return nil
	}

	averageOverlap := totalOverlap / float64(len(results))

	overallMissingTerms := make([]string, 0)
	for _, term := range queryTerms {
		if !allMatchedTerms[term] {
			overallMissingTerms = append(overallMissingTerms, term)
		}
	}
	sort.Strings(overallMissingTerms)

	// Conservative first version:
	// only warn when top chunks have very weak average overlap and no strong best match.
	if averageOverlap >= 0.35 || bestOverlap >= 0.5 {
		return nil
	}

	primary := results[0]
	primaryChunkID := primary.Chunk.ChunkID
	primarySpanID := primary.Chunk.SpanID

	queryDiagnosticID := newDiagnosticObjectID()
	overlapDiagnosticID := newDiagnosticObjectID()

	evidence := []models.EvidenceItem{
		{
			EvidenceID: newEvidenceID(),
			Type:       "query_text",
			Label:      "User query terms",
			SpanID:     querySpanID,
			Snippet:    query,
			Attributes: models.JSONMap{
				"query_terms": queryTerms,
			},
			DiagnosticObjectIDs: []string{queryDiagnosticID},
		},
		{
			EvidenceID: newEvidenceID(),
			Type:       "chunk_snippet",
			Label:      "Top retrieved chunk with weak query overlap",
			SpanID:     &primarySpanID,
			ChunkID:    &primaryChunkID,
			Source:     chunkSource(primary.Chunk),
			Snippet:    primary.Chunk.Text,
			Attributes: models.JSONMap{
				"rank":          primary.ChunkRank,
				"score":         nullableScore(primary.Chunk.Score),
				"matched_terms": primary.MatchedTerms,
				"missing_terms": primary.MissingTerms,
				"overlap_ratio": primary.OverlapRatio,
			},
			DiagnosticObjectIDs: []string{overlapDiagnosticID},
		},
		{
			EvidenceID: newEvidenceID(),
			Type:       "overlap_measure",
			Label:      "Query/chunk overlap measurement",
			Snippet: fmt.Sprintf(
				"Top-%d average overlap %.0f%%; best overlap %.0f%%.",
				len(results),
				averageOverlap*100,
				bestOverlap*100,
			),
			Attributes: models.JSONMap{
				"top_k":                 len(results),
				"average_overlap_ratio": averageOverlap,
				"best_overlap_ratio":    bestOverlap,
				"query_terms":           queryTerms,
				"missing_terms":         overallMissingTerms,
			},
		},
	}

	diagnostics := []models.DiagnosticObject{
		{
			DiagnosticObjectID: queryDiagnosticID,
			Type:               "query_term_set",
			Label:              "Important query terms",
			SpanID:             querySpanID,
			Text:               query,
			Normalized: models.JSONMap{
				"terms": queryTerms,
			},
			Attributes: models.JSONMap{
				"source": "query",
			},
		},
		{
			DiagnosticObjectID: overlapDiagnosticID,
			Type:               "overlap_result",
			Label:              "Top retrieved chunk overlap result",
			SpanID:             &primarySpanID,
			Text:               primary.Chunk.Text,
			Normalized: models.JSONMap{
				"matched_terms": primary.MatchedTerms,
				"missing_terms": primary.MissingTerms,
				"overlap_ratio": primary.OverlapRatio,
			},
			Attributes: models.JSONMap{
				"chunk_id": primaryChunkID,
				"rank":     primary.ChunkRank,
				"score":    nullableScore(primary.Chunk.Score),
			},
		},
	}

	signals := []models.DiagnosticSignal{
		{
			SignalID:   "top_k_average_overlap_below_threshold",
			Label:      "Top-k average query/chunk overlap is below threshold",
			Observed:   averageOverlap,
			Expected:   "< 0.35",
			Comparator: "less_than",
			Strength:   "moderate",
			Attributes: models.JSONMap{
				"top_k": len(results),
			},
		},
		{
			SignalID:   "best_overlap_below_threshold",
			Label:      "No retrieved chunk strongly covers the query terms",
			Observed:   bestOverlap,
			Expected:   "< 0.50",
			Comparator: "less_than",
			Strength:   "moderate",
		},
	}

	message := fmt.Sprintf(
		"Retrieved chunks have weak lexical overlap with the query. Missing terms: %s.",
		strings.Join(overallMissingTerms, ", "),
	)

	return []models.Warning{
		{
			WarningID:     newWarningID(),
			TraceID:       payload.Trace.TraceID,
			SpanID:        &primarySpanID,
			Type:          TypeWeakQueryChunkOverlap,
			Severity:      SeverityWarning,
			Message:       message,
			SchemaVersion: stringPtr("2"),
			RuleID:        stringPtr(TypeWeakQueryChunkOverlap),
			RuleVersion:   stringPtr("2"),
			Title:         stringPtr("Retrieved chunks weakly match the query"),
			Category:      stringPtr("retrieval"),
			Confidence:    float64Ptr(0.75),
			Explanation: stringPtr(
				"SledTrace found that the top retrieved chunks have low lexical overlap with important terms from the user query.",
			),
			Details: models.JSONMap{
				"rule":                  TypeWeakQueryChunkOverlap,
				"query":                 query,
				"query_terms":           queryTerms,
				"missing_terms":         overallMissingTerms,
				"average_overlap_ratio": averageOverlap,
				"best_overlap_ratio":    bestOverlap,
				"top_k":                 len(results),
				"reason":                "top retrieved chunks have weak lexical overlap with important query terms",
			},
			Evidence:          evidence,
			Diagnostics:       diagnostics,
			Signals:           signals,
			RecommendedAction: stringPtr("Inspect the retriever query, filters, chunking, and ranking because the retrieved chunks may not address the user's question."),
			CreatedAt:         time.Now().UTC().Format(time.RFC3339Nano),
		},
	}
}

func (e *Engine) detectDuplicateChunks(payload models.TracePayload) []models.Warning {
	chunks := extractRetrievedChunks(payload.Spans)
	if len(chunks) < 2 {
		return nil
	}

	groups := map[string][]retrievedChunk{}

	for _, chunk := range chunks {
		normalized := normalizeChunkText(chunk.Text)
		if normalized == "" {
			continue
		}

		groups[normalized] = append(groups[normalized], chunk)
	}

	duplicateGroups := make([]models.JSONMap, 0)

	for normalizedText, group := range groups {
		if len(group) < 2 {
			continue
		}

		chunkIDs := make([]string, 0, len(group))
		spanIDs := make([]string, 0, len(group))

		for _, chunk := range group {
			chunkIDs = append(chunkIDs, chunk.ChunkID)
			spanIDs = append(spanIDs, chunk.SpanID)
		}

		duplicateGroups = append(duplicateGroups, models.JSONMap{
			"normalized_text": normalizedText,
			"chunk_ids":       chunkIDs,
			"span_ids":        spanIDs,
		})
	}

	if len(duplicateGroups) == 0 {
		return nil
	}

	return []models.Warning{
		{
			WarningID: newWarningID(),
			TraceID:   payload.Trace.TraceID,
			SpanID:    nil,
			Type:      TypeDuplicateChunks,
			Severity:  SeverityWarning,
			Message:   "Retrieved chunks contain duplicate text.",
			Details: models.JSONMap{
				"rule":             TypeDuplicateChunks,
				"duplicate_groups": duplicateGroups,
				"reason":           "multiple retrieved chunks have identical normalized text",
			},
			CreatedAt: time.Now().UTC().Format(time.RFC3339Nano),
		},
	}
}

type chunkNumericFact struct {
	Expression numericExpression
	Chunk      retrievedChunk
	ChunkRank  int
}

type chunkConflictCandidate struct {
	Left               chunkNumericFact
	Right              chunkNumericFact
	LeftTopic          string
	RightTopic         string
	CandidateTopic     string
	SharedTerms        []string
	QueryMatchedTerms  []string
	AnswerMatchedTerms []string
	QueryIntentTopics  []string
	RelevanceScore     float64
}

func (e *Engine) detectConflictingChunks(payload models.TracePayload) []models.Warning {
	chunks := extractRetrievedChunks(payload.Spans)
	if len(chunks) < 2 {
		return nil
	}

	query, _ := extractTraceQuery(payload)
	query = strings.TrimSpace(query)
	queryTerms := importantQueryTerms(query)
	queryIntentTopics := textIntentTopics(query)

	answer, _ := extractFinalAnswer(payload)
	answer = strings.TrimSpace(answer)
	answerTerms := importantContextTerms(answer)

	facts := make([]chunkNumericFact, 0)

	for chunkIndex, chunk := range chunks {
		chunkText := strings.TrimSpace(chunk.Text)
		if chunkText == "" {
			continue
		}

		expressions := extractNumericExpressions(chunkText)
		for _, expression := range expressions {
			facts = append(facts, chunkNumericFact{
				Expression: expression,
				Chunk:      chunk,
				ChunkRank:  chunkIndex + 1,
			})
		}
	}

	if len(facts) < 2 {
		return nil
	}

	candidates := make([]chunkConflictCandidate, 0)

	for i := 0; i < len(facts); i++ {
		for j := i + 1; j < len(facts); j++ {
			left := facts[i]
			right := facts[j]

			if left.Chunk.ChunkID == right.Chunk.ChunkID {
				continue
			}

			if left.Expression.Unit != right.Expression.Unit {
				continue
			}

			if left.Expression.Value == right.Expression.Value {
				continue
			}

			leftTopic := numericExpressionTopic(left.Expression)
			rightTopic := numericExpressionTopic(right.Expression)
			if leftTopic != "" && rightTopic != "" && leftTopic != rightTopic {
				continue
			}

			candidateTopic := mergeNumericExpressionTopics(leftTopic, rightTopic)
			if len(queryIntentTopics) > 0 && candidateTopic != "" && !topicMatchesAnyIntent(candidateTopic, queryIntentTopics) {
				continue
			}

			sharedTerms := sharedContextTerms(left.Expression.ContextTerms, right.Expression.ContextTerms)
			if len(sharedTerms) == 0 {
				continue
			}

			conflictTerms := unionTerms(
				sharedTerms,
				left.Expression.ContextTerms,
				right.Expression.ContextTerms,
			)

			queryMatchedTerms := sharedContextTerms(queryTerms, conflictTerms)
			answerMatchedTerms := sharedContextTerms(answerTerms, conflictTerms)

			relevanceScore := float64(len(queryMatchedTerms)*3 + len(answerMatchedTerms))
			if len(queryMatchedTerms) > 0 {
				relevanceScore += 1.0
			}

			candidate := chunkConflictCandidate{
				Left:               left,
				Right:              right,
				LeftTopic:          leftTopic,
				RightTopic:         rightTopic,
				CandidateTopic:     candidateTopic,
				SharedTerms:        sharedTerms,
				QueryMatchedTerms:  queryMatchedTerms,
				AnswerMatchedTerms: answerMatchedTerms,
				QueryIntentTopics:  queryIntentTopics,
				RelevanceScore:     relevanceScore,
			}

			candidates = append(candidates, candidate)
		}
	}

	if len(candidates) == 0 {
		return nil
	}

	hasQueryRelevantCandidate := false
	if len(queryTerms) > 0 {
		for _, candidate := range candidates {
			if len(candidate.QueryMatchedTerms) > 0 {
				hasQueryRelevantCandidate = true
				break
			}
		}

		// Relevance guard:
		// if query terms exist but none of the numeric conflicts overlap with the query,
		// suppress conflicting_chunks to avoid unrelated numeric-noise warnings.
		if !hasQueryRelevantCandidate {
			return nil
		}
	}

	var best *chunkConflictCandidate
	for _, candidate := range candidates {
		if hasQueryRelevantCandidate && len(candidate.QueryMatchedTerms) == 0 {
			continue
		}

		if best == nil || isBetterChunkConflictCandidate(candidate, *best) {
			selected := candidate
			best = &selected
		}
	}

	if best == nil {
		return nil
	}

	leftValue := best.Left.Expression.Normalized
	rightValue := best.Right.Expression.Normalized
	leftChunkID := best.Left.Chunk.ChunkID
	rightChunkID := best.Right.Chunk.ChunkID
	leftSpanID := best.Left.Chunk.SpanID
	rightSpanID := best.Right.Chunk.SpanID

	leftDiagnosticID := newDiagnosticObjectID()
	rightDiagnosticID := newDiagnosticObjectID()
	conflictDiagnosticID := newDiagnosticObjectID()

	evidence := []models.EvidenceItem{
		{
			EvidenceID: newEvidenceID(),
			Type:       "chunk_snippet",
			Label:      "First conflicting retrieved chunk",
			SpanID:     &leftSpanID,
			ChunkID:    &leftChunkID,
			Source:     chunkSource(best.Left.Chunk),
			Snippet:    best.Left.Expression.Snippet,
			Attributes: models.JSONMap{
				"value":            best.Left.Expression.Value,
				"unit":             best.Left.Expression.Unit,
				"normalized_value": best.Left.Expression.Normalized,
				"topic":            best.LeftTopic,
				"rank":             best.Left.ChunkRank,
				"score":            nullableScore(best.Left.Chunk.Score),
			},
			DiagnosticObjectIDs: []string{leftDiagnosticID, conflictDiagnosticID},
		},
		{
			EvidenceID: newEvidenceID(),
			Type:       "chunk_snippet",
			Label:      "Second conflicting retrieved chunk",
			SpanID:     &rightSpanID,
			ChunkID:    &rightChunkID,
			Source:     chunkSource(best.Right.Chunk),
			Snippet:    best.Right.Expression.Snippet,
			Attributes: models.JSONMap{
				"value":            best.Right.Expression.Value,
				"unit":             best.Right.Expression.Unit,
				"normalized_value": best.Right.Expression.Normalized,
				"topic":            best.RightTopic,
				"rank":             best.Right.ChunkRank,
				"score":            nullableScore(best.Right.Chunk.Score),
			},
			DiagnosticObjectIDs: []string{rightDiagnosticID, conflictDiagnosticID},
		},
		{
			EvidenceID: newEvidenceID(),
			Type:       "conflict_pair",
			Label:      "Conflicting numeric values",
			Snippet: fmt.Sprintf(
				"Retrieved chunks disagree: %s vs %s.",
				leftValue,
				rightValue,
			),
			Attributes: models.JSONMap{
				"left_value":           leftValue,
				"right_value":          rightValue,
				"left_topic":           best.LeftTopic,
				"right_topic":          best.RightTopic,
				"candidate_topic":      best.CandidateTopic,
				"unit":                 best.Left.Expression.Unit,
				"left_chunk_id":        leftChunkID,
				"right_chunk_id":       rightChunkID,
				"shared_terms":         best.SharedTerms,
				"query_matched_terms":  best.QueryMatchedTerms,
				"answer_matched_terms": best.AnswerMatchedTerms,
				"query_intent_topics":  best.QueryIntentTopics,
				"relevance_score":      best.RelevanceScore,
			},
			DiagnosticObjectIDs: []string{conflictDiagnosticID},
		},
	}

	diagnostics := []models.DiagnosticObject{
		{
			DiagnosticObjectID: leftDiagnosticID,
			Type:               "chunk_fact",
			Label:              "First retrieved numeric fact",
			SpanID:             &leftSpanID,
			Text:               best.Left.Expression.Snippet,
			Normalized: models.JSONMap{
				"value":    best.Left.Expression.Value,
				"unit":     best.Left.Expression.Unit,
				"chunk_id": leftChunkID,
			},
			Attributes: models.JSONMap{
				"source": chunkSourceValue(best.Left.Chunk),
				"rank":   best.Left.ChunkRank,
				"score":  nullableScore(best.Left.Chunk.Score),
			},
		},
		{
			DiagnosticObjectID: rightDiagnosticID,
			Type:               "chunk_fact",
			Label:              "Second retrieved numeric fact",
			SpanID:             &rightSpanID,
			Text:               best.Right.Expression.Snippet,
			Normalized: models.JSONMap{
				"value":    best.Right.Expression.Value,
				"unit":     best.Right.Expression.Unit,
				"chunk_id": rightChunkID,
			},
			Attributes: models.JSONMap{
				"source": chunkSourceValue(best.Right.Chunk),
				"rank":   best.Right.ChunkRank,
				"score":  nullableScore(best.Right.Chunk.Score),
			},
		},
		{
			DiagnosticObjectID: conflictDiagnosticID,
			Type:               "conflict_group",
			Label:              "Conflicting retrieved numeric values",
			Normalized: models.JSONMap{
				"values": []string{leftValue, rightValue},
				"unit":   best.Left.Expression.Unit,
			},
			Attributes: models.JSONMap{
				"left_chunk_id":        leftChunkID,
				"right_chunk_id":       rightChunkID,
				"left_topic":           best.LeftTopic,
				"right_topic":          best.RightTopic,
				"candidate_topic":      best.CandidateTopic,
				"shared_terms":         best.SharedTerms,
				"query_matched_terms":  best.QueryMatchedTerms,
				"answer_matched_terms": best.AnswerMatchedTerms,
				"query_intent_topics":  best.QueryIntentTopics,
				"relevance_score":      best.RelevanceScore,
			},
		},
	}

	signals := []models.DiagnosticSignal{
		{
			SignalID:   "same_unit_different_retrieved_values",
			Label:      "Retrieved chunks contain different numeric values with the same unit",
			Observed:   []string{leftValue, rightValue},
			Expected:   "one consistent retrieved value",
			Comparator: "multiple_distinct_values",
			Strength:   "strong",
		},
		{
			SignalID:   "local_context_overlap_between_conflicting_chunks",
			Label:      "Conflicting values appear in similar local context",
			Observed:   strings.Join(best.SharedTerms, ", "),
			Expected:   "at least one shared context term",
			Comparator: "overlap_greater_than_zero",
			Strength:   "moderate",
			Attributes: models.JSONMap{
				"shared_terms": best.SharedTerms,
			},
		},
		{
			SignalID:   "conflict_relevant_to_query",
			Label:      "Selected conflict is relevant to query terms",
			Observed:   len(best.QueryMatchedTerms),
			Expected:   "> 0 when query terms are available",
			Comparator: "query_overlap_count",
			Strength:   "moderate",
			Attributes: models.JSONMap{
				"query_matched_terms":  best.QueryMatchedTerms,
				"answer_matched_terms": best.AnswerMatchedTerms,
				"query_intent_topics":  best.QueryIntentTopics,
				"relevance_score":      best.RelevanceScore,
			},
		},
	}

	message := fmt.Sprintf(
		"Retrieved chunks contain conflicting numeric values: %s vs %s.",
		leftValue,
		rightValue,
	)

	return []models.Warning{
		{
			WarningID:     newWarningID(),
			TraceID:       payload.Trace.TraceID,
			SpanID:        nil,
			Type:          TypeConflictingChunks,
			Severity:      SeverityWarning,
			Message:       message,
			SchemaVersion: stringPtr("2"),
			RuleID:        stringPtr(TypeConflictingChunks),
			RuleVersion:   stringPtr("2"),
			Title:         stringPtr("Retrieved chunks contain conflicting values"),
			Category:      stringPtr("conflict"),
			Confidence:    float64Ptr(0.88),
			Explanation: stringPtr(
				"SledTrace found two retrieved chunks that state different numeric values in similar local context.",
			),
			Details: models.JSONMap{
				"rule":                 TypeConflictingChunks,
				"left_value":           leftValue,
				"right_value":          rightValue,
				"left_topic":           best.LeftTopic,
				"right_topic":          best.RightTopic,
				"candidate_topic":      best.CandidateTopic,
				"detected_values":      []string{leftValue, rightValue},
				"left_chunk_id":        leftChunkID,
				"right_chunk_id":       rightChunkID,
				"shared_terms":         best.SharedTerms,
				"query_matched_terms":  best.QueryMatchedTerms,
				"answer_matched_terms": best.AnswerMatchedTerms,
				"query_intent_topics":  best.QueryIntentTopics,
				"relevance_score":      best.RelevanceScore,
				"reason":               "retrieved chunks contain different numeric values in similar local context",
			},
			Evidence:          evidence,
			Diagnostics:       diagnostics,
			Signals:           signals,
			RecommendedAction: stringPtr("Inspect source freshness, document versioning, and retrieval ranking to decide which retrieved chunk should be trusted."),
			CreatedAt:         time.Now().UTC().Format(time.RFC3339Nano),
		},
	}
}

func isBetterChunkConflictCandidate(candidate chunkConflictCandidate, current chunkConflictCandidate) bool {
	if candidate.RelevanceScore != current.RelevanceScore {
		return candidate.RelevanceScore > current.RelevanceScore
	}

	if len(candidate.QueryMatchedTerms) != len(current.QueryMatchedTerms) {
		return len(candidate.QueryMatchedTerms) > len(current.QueryMatchedTerms)
	}

	if len(candidate.SharedTerms) != len(current.SharedTerms) {
		return len(candidate.SharedTerms) > len(current.SharedTerms)
	}

	candidateScore := combinedChunkScore(
		higherIsBetterScore(candidate.Left.Chunk),
		higherIsBetterScore(candidate.Right.Chunk),
	)
	currentScore := combinedChunkScore(
		higherIsBetterScore(current.Left.Chunk),
		higherIsBetterScore(current.Right.Chunk),
	)

	if candidateScore != currentScore {
		return candidateScore > currentScore
	}

	candidateRank := candidate.Left.ChunkRank + candidate.Right.ChunkRank
	currentRank := current.Left.ChunkRank + current.Right.ChunkRank

	return candidateRank < currentRank
}

func unionTerms(termLists ...[]string) []string {
	seen := map[string]bool{}
	result := make([]string, 0)

	for _, terms := range termLists {
		for _, term := range terms {
			if seen[term] {
				continue
			}

			seen[term] = true
			result = append(result, term)
		}
	}

	sort.Strings(result)

	return result
}

func combinedChunkScore(left *float64, right *float64) float64 {
	if left == nil && right == nil {
		return -1
	}

	leftValue := 0.0
	if left != nil {
		leftValue = *left
	}

	rightValue := 0.0
	if right != nil {
		rightValue = *right
	}

	return leftValue + rightValue
}

type numericExpression struct {
	Raw          string
	Value        string
	Unit         string
	Normalized   string
	Snippet      string
	ContextTerms []string
}

type numericMismatchCandidate struct {
	AnswerExpression numericExpression
	ChunkExpression  numericExpression
	Chunk            retrievedChunk
	ChunkRank        int
	SharedTerms      []string
}

var numericExpressionRegex = regexp.MustCompile(`(?i)\b(\d{1,4})(?:\s*(?:-\s*|to\s+)(\d{1,4}))?\s*(business\s+days?|days?|months?|years?|hours?|percent|%)\b`)

func (e *Engine) detectNumericMismatch(payload models.TracePayload) []models.Warning {
	answer, llmSpanID := extractFinalAnswer(payload)
	answer = strings.TrimSpace(answer)

	if answer == "" {
		return nil
	}

	if containsUncertaintyPhrase(answer) {
		return nil
	}

	answerExpressions := extractNumericExpressions(answer)
	if len(answerExpressions) == 0 {
		return nil
	}

	chunks := extractRetrievedChunks(payload.Spans)
	if len(chunks) == 0 {
		return nil
	}

	var best *numericMismatchCandidate

	for _, answerExpression := range answerExpressions {
		// Important false-positive guard:
		// A value like "20 days ago" is usually user elapsed time, not a policy value.
		// Example:
		//   "A purchase from 20 days ago is still within the 30-day return window."
		// The answer is comparing elapsed time to a policy limit, not claiming that
		// the policy window is 20 days.
		if isElapsedTimeAnswerExpression(answerExpression) {
			continue
		}

		// Important conflict/noise guard:
		// If the answer's numeric value is directly supported by at least one
		// retrieved chunk, do not flag that same answer value as a mismatch merely
		// because another retrieved chunk contains a conflicting legacy value.
		//
		// Example:
		//   answer: current policy says 30 days
		//   chunks: current policy says 30 days, legacy policy says 14 days
		//
		// That should be a conflicting_chunks warning, not numeric_mismatch.
		if answerExpressionSupportedByRetrievedChunk(answerExpression, chunks) {
			continue
		}

		for chunkIndex, chunk := range chunks {
			chunkText := strings.TrimSpace(chunk.Text)
			if chunkText == "" {
				continue
			}

			chunkExpressions := extractNumericExpressions(chunkText)
			for _, chunkExpression := range chunkExpressions {
				if answerExpression.Unit != chunkExpression.Unit {
					continue
				}

				if answerExpression.Value == chunkExpression.Value {
					continue
				}

				sharedTerms := sharedContextTerms(
					answerExpression.ContextTerms,
					chunkExpression.ContextTerms,
				)

				// Keep this deterministic rule conservative:
				// same unit + different value + at least one shared local context term.
				if len(sharedTerms) == 0 {
					continue
				}

				candidate := numericMismatchCandidate{
					AnswerExpression: answerExpression,
					ChunkExpression:  chunkExpression,
					Chunk:            chunk,
					ChunkRank:        chunkIndex + 1,
					SharedTerms:      sharedTerms,
				}

				if best == nil || isBetterNumericMismatchCandidate(candidate, *best) {
					best = &candidate
				}
			}
		}
	}

	if best == nil {
		return nil
	}

	answerValue := best.AnswerExpression.Normalized
	chunkValue := best.ChunkExpression.Normalized
	chunkSpanID := best.Chunk.SpanID
	chunkID := best.Chunk.ChunkID

	answerDiagnosticID := newDiagnosticObjectID()
	chunkDiagnosticID := newDiagnosticObjectID()

	evidence := []models.EvidenceItem{
		{
			EvidenceID: newEvidenceID(),
			Type:       "answer_snippet",
			Label:      "Answer numeric claim",
			SpanID:     llmSpanID,
			Snippet:    best.AnswerExpression.Snippet,
			Attributes: models.JSONMap{
				"value":            best.AnswerExpression.Value,
				"unit":             best.AnswerExpression.Unit,
				"normalized_value": best.AnswerExpression.Normalized,
			},
			DiagnosticObjectIDs: []string{answerDiagnosticID},
		},
		{
			EvidenceID: newEvidenceID(),
			Type:       "chunk_snippet",
			Label:      "Retrieved chunk numeric value",
			SpanID:     &chunkSpanID,
			ChunkID:    &chunkID,
			Source:     chunkSource(best.Chunk),
			Snippet:    best.ChunkExpression.Snippet,
			Attributes: models.JSONMap{
				"value":            best.ChunkExpression.Value,
				"unit":             best.ChunkExpression.Unit,
				"normalized_value": best.ChunkExpression.Normalized,
				"rank":             best.ChunkRank,
				"score":            nullableScore(best.Chunk.Score),
			},
			DiagnosticObjectIDs: []string{chunkDiagnosticID},
		},
		{
			EvidenceID: newEvidenceID(),
			Type:       "numeric_value",
			Label:      "Compared numeric values",
			Snippet: fmt.Sprintf(
				"Answer value %s differs from retrieved value %s.",
				answerValue,
				chunkValue,
			),
			Attributes: models.JSONMap{
				"answer_value":    answerValue,
				"retrieved_value": chunkValue,
				"shared_terms":    best.SharedTerms,
			},
		},
	}

	diagnostics := []models.DiagnosticObject{
		{
			DiagnosticObjectID: answerDiagnosticID,
			Type:               "numeric_claim",
			Label:              "Numeric value in final answer",
			SpanID:             llmSpanID,
			Text:               best.AnswerExpression.Snippet,
			Normalized: models.JSONMap{
				"value": best.AnswerExpression.Value,
				"unit":  best.AnswerExpression.Unit,
			},
			Attributes: models.JSONMap{
				"source": "answer",
			},
		},
		{
			DiagnosticObjectID: chunkDiagnosticID,
			Type:               "chunk_fact",
			Label:              "Numeric value in retrieved chunk",
			SpanID:             &chunkSpanID,
			Text:               best.ChunkExpression.Snippet,
			Normalized: models.JSONMap{
				"value":    best.ChunkExpression.Value,
				"unit":     best.ChunkExpression.Unit,
				"chunk_id": chunkID,
			},
			Attributes: models.JSONMap{
				"source": chunkSourceValue(best.Chunk),
				"rank":   best.ChunkRank,
				"score":  nullableScore(best.Chunk.Score),
			},
		},
	}

	signals := []models.DiagnosticSignal{
		{
			SignalID:   "same_unit_different_value",
			Label:      "Same unit but different numeric value",
			Observed:   answerValue,
			Expected:   chunkValue,
			Comparator: "not_equal",
			Strength:   "strong",
		},
		{
			SignalID:   "local_context_overlap",
			Label:      "Answer and chunk numeric values appear in similar local context",
			Observed:   strings.Join(best.SharedTerms, ", "),
			Expected:   "at least one shared context term",
			Comparator: "overlap_greater_than_zero",
			Strength:   "moderate",
			Attributes: models.JSONMap{
				"shared_terms": best.SharedTerms,
			},
		},
	}

	return []models.Warning{
		{
			WarningID:     newWarningID(),
			TraceID:       payload.Trace.TraceID,
			SpanID:        llmSpanID,
			Type:          TypeNumericMismatch,
			Severity:      "high",
			Message:       fmt.Sprintf("Answer says %s, but retrieved context says %s.", answerValue, chunkValue),
			SchemaVersion: stringPtr("2"),
			RuleID:        stringPtr(TypeNumericMismatch),
			RuleVersion:   stringPtr("2"),
			Title:         stringPtr("Answer numeric value conflicts with retrieved context"),
			Category:      stringPtr("grounding"),
			Confidence:    float64Ptr(0.9),
			Explanation: stringPtr(
				"SledTrace found a numeric value in the final answer that differs from a retrieved chunk with overlapping local context.",
			),
			Details: models.JSONMap{
				"rule":            TypeNumericMismatch,
				"answer_value":    answerValue,
				"retrieved_value": chunkValue,
				"shared_terms":    best.SharedTerms,
				"chunk_id":        chunkID,
				"chunk_rank":      best.ChunkRank,
				"reason":          "answer numeric value differs from retrieved numeric value in similar local context",
			},
			Evidence:          evidence,
			Diagnostics:       diagnostics,
			Signals:           signals,
			RecommendedAction: stringPtr("Inspect whether the answer copied an outdated value, ignored stronger retrieved evidence, or mixed conflicting policy chunks."),
			CreatedAt:         time.Now().UTC().Format(time.RFC3339Nano),
		},
	}
}

func isElapsedTimeAnswerExpression(expression numericExpression) bool {
	snippet := strings.ToLower(strings.TrimSpace(expression.Snippet))
	raw := strings.ToLower(strings.TrimSpace(expression.Raw))

	if snippet == "" || raw == "" {
		return false
	}

	quotedRaw := regexp.QuoteMeta(raw)

	patterns := []string{
		// "20 days ago"
		`\b` + quotedRaw + `\s+ago\b`,

		// "bought 20 days ago", "purchased 20 days ago", "ordered 20 days ago"
		`\b(bought|purchased|ordered)\b.{0,80}\b` + quotedRaw + `\s+ago\b`,

		// "purchase from 20 days ago", "order from 20 days ago"
		`\b(purchase|order|item|product)\b.{0,80}\b` + quotedRaw + `\s+ago\b`,
	}

	for _, pattern := range patterns {
		if regexp.MustCompile(pattern).MatchString(snippet) {
			return true
		}
	}

	return false
}

func answerExpressionSupportedByRetrievedChunk(
	answerExpression numericExpression,
	chunks []retrievedChunk,
) bool {
	for _, chunk := range chunks {
		chunkText := strings.TrimSpace(chunk.Text)
		if chunkText == "" {
			continue
		}

		chunkExpressions := extractNumericExpressions(chunkText)
		for _, chunkExpression := range chunkExpressions {
			if answerExpression.Unit != chunkExpression.Unit {
				continue
			}

			if answerExpression.Value != chunkExpression.Value {
				continue
			}

			sharedTerms := sharedContextTerms(
				answerExpression.ContextTerms,
				chunkExpression.ContextTerms,
			)

			if len(sharedTerms) > 0 {
				return true
			}
		}
	}

	return false
}

func isBetterNumericMismatchCandidate(candidate numericMismatchCandidate, current numericMismatchCandidate) bool {
	if len(candidate.SharedTerms) != len(current.SharedTerms) {
		return len(candidate.SharedTerms) > len(current.SharedTerms)
	}

	candidateScore := -1.0
	if score := higherIsBetterScore(candidate.Chunk); score != nil {
		candidateScore = *score
	}

	currentScore := -1.0
	if score := higherIsBetterScore(current.Chunk); score != nil {
		currentScore = *score
	}

	if candidateScore != currentScore {
		return candidateScore > currentScore
	}

	return candidate.ChunkRank < current.ChunkRank
}

func extractNumericExpressions(text string) []numericExpression {
	matches := numericExpressionRegex.FindAllStringSubmatch(text, -1)

	result := make([]numericExpression, 0, len(matches))
	seen := map[string]bool{}

	for _, match := range matches {
		if len(match) < 4 {
			continue
		}

		raw := strings.TrimSpace(match[0])
		if raw == "" {
			continue
		}

		value := strings.TrimSpace(match[1])
		if match[2] != "" {
			value = value + "-" + strings.TrimSpace(match[2])
		}

		unit := normalizeNumericUnit(match[3])
		if unit == "" {
			continue
		}

		normalized := value + " " + unit
		snippet := sentenceContaining(text, raw)
		key := normalized + "|" + snippet
		if seen[key] {
			continue
		}

		seen[key] = true

		result = append(result, numericExpression{
			Raw:          raw,
			Value:        value,
			Unit:         unit,
			Normalized:   normalized,
			Snippet:      snippet,
			ContextTerms: importantContextTerms(snippet),
		})
	}

	return result
}

func normalizeNumericUnit(raw string) string {
	unit := strings.ToLower(strings.TrimSpace(raw))
	unit = strings.Join(strings.Fields(unit), " ")

	switch unit {
	case "day", "days":
		return "days"
	case "business day", "business days":
		return "business days"
	case "month", "months":
		return "months"
	case "year", "years":
		return "years"
	case "hour", "hours":
		return "hours"
	case "percent", "%":
		return "percent"
	default:
		return ""
	}
}

func numericExpressionTopic(expression numericExpression) string {
	snippet := strings.ToLower(strings.TrimSpace(expression.Snippet))
	if snippet == "" {
		return ""
	}

	containsAny := func(keywords ...string) bool {
		for _, keyword := range keywords {
			if strings.Contains(snippet, keyword) {
				return true
			}
		}
		return false
	}

	// Order matters.
	// Damaged-item policy snippets often contain words such as "delivery" or
	// "shipping box", but their policy role is damaged-claim handling, not
	// shipping-delivery timing.
	if containsAny("damaged", "defective", "report", "photos", "photo", "packaging", "box", "shipping box") {
		return "damaged_report"
	}

	// Return/refund-window claims often contain the word "refund", so classify
	// purchase-window wording before refund-processing wording.
	withinDaysOfPurchase := regexp.MustCompile(`\bwithin\s+\d{1,4}(?:\s*(?:-|to)\s*\d{1,4})?\s+(?:business\s+)?days?\s+of\s+(?:the\s+)?purchase(?:\s+date)?\b`)
	if containsAny("return window", "refund window", "purchase date", "of purchase", "can still return", "still return") ||
		(containsAny("return", "returns", "returned", "request") && containsAny("purchase", "purchase date")) ||
		withinDaysOfPurchase.MatchString(snippet) {
		return "return_window"
	}

	// Refund processing is specifically about post-return processing/issuance
	// duration. Do not classify every "refund ... days" sentence as processing;
	// that would misclassify refund-window facts such as "request a refund within
	// 30 days of purchase".
	if containsAny(
		"processed",
		"processing",
		"issued",
		"issue the refund",
		"warehouse",
		"inspection",
		"refunds usually take",
		"refund usually take",
		"refunds take",
		"refund takes",
	) {
		return "refund_processing"
	}

	if containsAny("shipping", "shipment", "shipped", "package", "arrived", "delivery", "domestic", "international", "customs") {
		return "shipping_delivery"
	}

	if containsAny("warranty", "coverage", "manufacturing defects") {
		return "warranty_period"
	}

	if containsAny("subscription", "cancel", "access", "billing period") {
		return "subscription_access"
	}

	return ""
}

func mergeNumericExpressionTopics(left string, right string) string {
	if left != "" {
		return left
	}

	return right
}

func textIntentTopics(text string) []string {
	normalized := strings.ToLower(strings.TrimSpace(text))
	if normalized == "" {
		return nil
	}

	normalized = strings.Join(strings.Fields(normalized), " ")

	containsAny := func(keywords ...string) bool {
		for _, keyword := range keywords {
			if strings.Contains(normalized, keyword) {
				return true
			}
		}
		return false
	}

	topics := map[string]bool{}

	if containsAny("digital", "downloadable", "software", "license key", "license keys", "gift card", "gift cards", "non-refundable", "nonrefundable") {
		topics["digital_goods"] = true
	}

	if containsAny("damaged", "defective", "original box", "original packaging", "packaging", "photos", "photo", "repair", "replacement", "shipping box") {
		topics["damaged_report"] = true
	}

	if containsAny("warranty", "coverage", "manufacturing defect", "manufacturing defects") {
		topics["warranty_period"] = true
	}

	if containsAny("subscription", "cancel", "billing period", "access") {
		topics["subscription_access"] = true
	}

	if containsAny("shipping", "shipment", "shipped", "package arrived", "domestic package", "international", "customs", "delivery") &&
		!topics["damaged_report"] {
		topics["shipping_delivery"] = true
	}

	refundProcessingPhrase := containsAny(
		"refund processed",
		"refunds processed",
		"refund processing",
		"process refund",
		"process refunds",
		"refunds usually take",
		"refund usually take",
		"refunds take",
		"how long do refunds take",
		"how long does a refund take",
		"warehouse",
		"inspection",
	)

	refundProcessingQuestion := containsAny("refund", "refunds") &&
		containsAny("process", "processed", "processing", "take", "takes", "business days", "how long", "usually")

	if refundProcessingPhrase || refundProcessingQuestion {
		topics["refund_processing"] = true
	}

	returnWindowPhrase := containsAny("return window", "refund window", "purchase date", "can i still return", "still return")
	returnWindowQuestion := containsAny("return", "returns", "returned") &&
		containsAny("physical product", "physical products", "product", "purchase", "days", "how many", "how long", "window")

	if returnWindowPhrase || returnWindowQuestion {
		topics["return_window"] = true
	}

	result := make([]string, 0, len(topics))
	for topic := range topics {
		result = append(result, topic)
	}

	sort.Strings(result)
	return result
}

func topicMatchesAnyIntent(candidateTopic string, intentTopics []string) bool {
	if candidateTopic == "" || len(intentTopics) == 0 {
		return true
	}

	for _, intentTopic := range intentTopics {
		if candidateTopic == intentTopic {
			return true
		}
	}

	return false
}
func sentenceContaining(text string, needle string) string {
	text = strings.TrimSpace(text)
	if text == "" {
		return ""
	}

	needle = strings.TrimSpace(needle)
	if needle == "" {
		return text
	}

	index := strings.Index(strings.ToLower(text), strings.ToLower(needle))
	if index < 0 {
		return text
	}

	start := 0
	for i := index - 1; i >= 0; i-- {
		if text[i] == '.' || text[i] == '!' || text[i] == '?' || text[i] == '\n' {
			start = i + 1
			break
		}
	}

	end := len(text)
	for i := index + len(needle); i < len(text); i++ {
		if text[i] == '.' || text[i] == '!' || text[i] == '?' || text[i] == '\n' {
			end = i + 1
			break
		}
	}

	return strings.TrimSpace(text[start:end])
}

var nonWordRegex = regexp.MustCompile(`[^a-z0-9]+`)

func extractTraceQuery(payload models.TracePayload) (string, *string) {
	if payload.Trace.Input != nil {
		for _, key := range []string{"query", "question", "user_query", "input"} {
			if query := stringFromMap(payload.Trace.Input, key); query != "" {
				return query, nil
			}
		}
	}

	for _, span := range payload.Spans {
		if span.Type != "retrieval" {
			continue
		}

		spanID := span.SpanID

		if span.Input != nil {
			for _, key := range []string{"query", "question", "user_query", "input"} {
				if query := stringFromMap(span.Input, key); query != "" {
					return query, &spanID
				}
			}
		}

		if span.Metadata != nil {
			for _, key := range []string{"query", "question", "user_query"} {
				if query := stringFromMap(span.Metadata, key); query != "" {
					return query, &spanID
				}
			}
		}
	}

	return "", nil
}

func importantQueryTerms(query string) []string {
	return importantTermsWithStopwords(query, queryStopwords())
}

func importantContextTerms(text string) []string {
	return importantTermsWithStopwords(text, contextStopwords())
}

func importantTermsWithStopwords(text string, stopwords map[string]bool) []string {
	normalized := strings.ToLower(text)
	normalized = nonWordRegex.ReplaceAllString(normalized, " ")

	seen := map[string]bool{}
	result := make([]string, 0)

	for _, term := range strings.Fields(normalized) {
		if len(term) < 3 {
			continue
		}

		if stopwords[term] {
			continue
		}

		if _, err := fmt.Sscanf(term, "%d", new(int)); err == nil {
			continue
		}

		if seen[term] {
			continue
		}

		seen[term] = true
		result = append(result, term)
	}

	sort.Strings(result)

	return result
}

func queryStopwords() map[string]bool {
	stopwords := contextStopwords()
	for _, term := range []string{
		"what", "when", "where", "which", "who", "whom", "whose", "why", "how",
		"tell", "show", "give", "find", "need", "want", "know", "please",
		"does", "do", "did", "doing", "about",
	} {
		stopwords[term] = true
	}

	return stopwords
}

func contextStopwords() map[string]bool {
	return map[string]bool{
		"a": true, "an": true, "the": true, "and": true, "or": true, "but": true,
		"is": true, "are": true, "was": true, "were": true, "be": true, "been": true,
		"to": true, "of": true, "in": true, "on": true, "for": true, "with": true,
		"within": true, "from": true, "by": true, "at": true, "as": true,
		"can": true, "may": true, "must": true, "should": true, "will": true,
		"also": true, "this": true, "that": true, "these": true, "those": true,
		"customers": true, "customer": true, "users": true, "user": true,
		"days": true, "day": true, "business": true, "months": true, "month": true,
		"years": true, "year": true, "hours": true, "hour": true,
	}
}

func missingTerms(allTerms []string, matchedTerms []string) []string {
	matchedSet := map[string]bool{}
	for _, term := range matchedTerms {
		matchedSet[term] = true
	}

	result := make([]string, 0)
	for _, term := range allTerms {
		if matchedSet[term] {
			continue
		}

		result = append(result, term)
	}

	sort.Strings(result)

	return result
}

func sharedContextTerms(left []string, right []string) []string {
	rightSet := map[string]bool{}
	for _, term := range right {
		rightSet[term] = true
	}

	seen := map[string]bool{}
	result := make([]string, 0)

	for _, term := range left {
		if !rightSet[term] || seen[term] {
			continue
		}

		seen[term] = true
		result = append(result, term)
	}

	sort.Strings(result)

	return result
}

func chunkSource(chunk retrievedChunk) *string {
	value := chunkSourceValue(chunk)
	if value == "" {
		return nil
	}

	return &value
}

func chunkSourceValue(chunk retrievedChunk) string {
	keys := []string{
		"source",
		"file",
		"filename",
		"path",
		"document",
		"doc_id",
	}

	for _, key := range keys {
		raw, ok := chunk.Metadata[key]
		if !ok || raw == nil {
			continue
		}

		value, ok := raw.(string)
		if !ok {
			continue
		}

		value = strings.TrimSpace(value)
		if value != "" {
			return value
		}
	}

	return ""
}

func nullableScore(score *float64) any {
	if score == nil {
		return nil
	}

	return *score
}

type answerClaimSupportCandidate struct {
	Claim         string
	ClaimTerms    []string
	BestChunk     retrievedChunk
	BestChunkRank int
	MatchedTerms  []string
	MissingTerms  []string
	SupportRatio  float64
}

func (e *Engine) detectAnswerNotGrounded(payload models.TracePayload) []models.Warning {
	answer, llmSpanID := extractFinalAnswer(payload)
	answer = strings.TrimSpace(answer)

	if answer == "" {
		return nil
	}

	if containsUncertaintyPhrase(answer) {
		return nil
	}

	chunks := extractRetrievedChunks(payload.Spans)

	// Case 1:
	// The model gave a concrete answer even though retrieval returned no chunks.
	if len(chunks) == 0 {
		answerDiagnosticID := newDiagnosticObjectID()

		evidence := []models.EvidenceItem{
			{
				EvidenceID: newEvidenceID(),
				Type:       "answer_snippet",
				Label:      "Final answer without retrieved evidence",
				SpanID:     llmSpanID,
				Snippet:    answer,
				Attributes: models.JSONMap{
					"supporting_chunks": 0,
				},
				DiagnosticObjectIDs: []string{answerDiagnosticID},
			},
		}

		diagnostics := []models.DiagnosticObject{
			{
				DiagnosticObjectID: answerDiagnosticID,
				Type:               "answer_claim",
				Label:              "Final answer produced without retrieval support",
				SpanID:             llmSpanID,
				Text:               answer,
				Normalized: models.JSONMap{
					"supporting_chunks": 0,
				},
				Attributes: models.JSONMap{
					"source": "answer",
				},
			},
		}

		signals := []models.DiagnosticSignal{
			{
				SignalID:   "retrieved_chunk_count_zero_for_answer",
				Label:      "Final answer was produced with zero retrieved chunks",
				Observed:   0,
				Expected:   "> 0",
				Comparator: "equal",
				Strength:   "strong",
			},
		}

		return []models.Warning{
			{
				WarningID:     newWarningID(),
				TraceID:       payload.Trace.TraceID,
				SpanID:        llmSpanID,
				Type:          TypeAnswerNotGrounded,
				Severity:      SeverityWarning,
				Message:       "Answer may not be grounded because no retrieved chunks were available.",
				SchemaVersion: stringPtr("2"),
				RuleID:        stringPtr(TypeAnswerNotGrounded),
				RuleVersion:   stringPtr("2"),
				Title:         stringPtr("Answer produced without retrieved evidence"),
				Category:      stringPtr("grounding"),
				Confidence:    float64Ptr(0.85),
				Explanation: stringPtr(
					"SledTrace found a final answer even though no retrieved chunks were available to support it.",
				),
				Details: models.JSONMap{
					"rule":   TypeAnswerNotGrounded,
					"answer": answer,
					"reason": "final answer was produced without retrieved chunks",
				},
				Evidence:          evidence,
				Diagnostics:       diagnostics,
				Signals:           signals,
				RecommendedAction: stringPtr("Check why the answer generation step ran without retrieved context, or require the model to abstain when retrieval returns no evidence."),
				CreatedAt:         time.Now().UTC().Format(time.RFC3339Nano),
			},
		}
	}

	unsupported := findUnsupportedAnswerClaim(answer, chunks)
	if unsupported == nil {
		return nil
	}

	answerDiagnosticID := newDiagnosticObjectID()
	overlapDiagnosticID := newDiagnosticObjectID()

	chunkID := unsupported.BestChunk.ChunkID
	chunkSpanID := unsupported.BestChunk.SpanID

	evidence := []models.EvidenceItem{
		{
			EvidenceID: newEvidenceID(),
			Type:       "answer_snippet",
			Label:      "Unsupported answer claim",
			SpanID:     llmSpanID,
			Snippet:    unsupported.Claim,
			Attributes: models.JSONMap{
				"claim_terms":   unsupported.ClaimTerms,
				"missing_terms": unsupported.MissingTerms,
				"support_score": unsupported.SupportRatio,
			},
			DiagnosticObjectIDs: []string{answerDiagnosticID},
		},
		{
			EvidenceID: newEvidenceID(),
			Type:       "chunk_snippet",
			Label:      "Closest retrieved chunk",
			SpanID:     &chunkSpanID,
			ChunkID:    &chunkID,
			Source:     chunkSource(unsupported.BestChunk),
			Snippet:    unsupported.BestChunk.Text,
			Attributes: models.JSONMap{
				"rank":          unsupported.BestChunkRank,
				"score":         nullableScore(unsupported.BestChunk.Score),
				"matched_terms": unsupported.MatchedTerms,
				"missing_terms": unsupported.MissingTerms,
				"support_score": unsupported.SupportRatio,
			},
			DiagnosticObjectIDs: []string{overlapDiagnosticID},
		},
		{
			EvidenceID: newEvidenceID(),
			Type:       "overlap_measure",
			Label:      "Claim support measurement",
			Snippet: fmt.Sprintf(
				"Best support score %.0f%%; missing terms: %s.",
				unsupported.SupportRatio*100,
				strings.Join(unsupported.MissingTerms, ", "),
			),
			Attributes: models.JSONMap{
				"support_score": unsupported.SupportRatio,
				"claim_terms":   unsupported.ClaimTerms,
				"matched_terms": unsupported.MatchedTerms,
				"missing_terms": unsupported.MissingTerms,
				"threshold":     0.45,
			},
		},
	}

	diagnostics := []models.DiagnosticObject{
		{
			DiagnosticObjectID: answerDiagnosticID,
			Type:               "answer_claim",
			Label:              "Unsupported answer claim",
			SpanID:             llmSpanID,
			Text:               unsupported.Claim,
			Normalized: models.JSONMap{
				"terms": unsupported.ClaimTerms,
			},
			Attributes: models.JSONMap{
				"source":        "answer",
				"support_score": unsupported.SupportRatio,
			},
		},
		{
			DiagnosticObjectID: overlapDiagnosticID,
			Type:               "overlap_result",
			Label:              "Closest retrieved support for answer claim",
			SpanID:             &chunkSpanID,
			Text:               unsupported.BestChunk.Text,
			Normalized: models.JSONMap{
				"matched_terms": unsupported.MatchedTerms,
				"missing_terms": unsupported.MissingTerms,
				"support_score": unsupported.SupportRatio,
			},
			Attributes: models.JSONMap{
				"chunk_id": chunkID,
				"rank":     unsupported.BestChunkRank,
				"score":    nullableScore(unsupported.BestChunk.Score),
			},
		},
	}

	signals := []models.DiagnosticSignal{
		{
			SignalID:   "answer_claim_support_below_threshold",
			Label:      "Answer claim has weak support in retrieved chunks",
			Observed:   unsupported.SupportRatio,
			Expected:   ">= 0.45",
			Comparator: "less_than",
			Strength:   "moderate",
		},
		{
			SignalID:   "important_claim_terms_missing",
			Label:      "Important claim terms are missing from the closest retrieved chunk",
			Observed:   strings.Join(unsupported.MissingTerms, ", "),
			Expected:   "important claim terms present in retrieved evidence",
			Comparator: "missing_terms",
			Strength:   "moderate",
			Attributes: models.JSONMap{
				"missing_terms": unsupported.MissingTerms,
			},
		},
	}

	return []models.Warning{
		{
			WarningID:     newWarningID(),
			TraceID:       payload.Trace.TraceID,
			SpanID:        llmSpanID,
			Type:          TypeAnswerNotGrounded,
			Severity:      SeverityWarning,
			Message:       "Answer contains a claim that is weakly supported by retrieved chunks.",
			SchemaVersion: stringPtr("2"),
			RuleID:        stringPtr(TypeAnswerNotGrounded),
			RuleVersion:   stringPtr("2"),
			Title:         stringPtr("Answer contains an unsupported claim"),
			Category:      stringPtr("grounding"),
			Confidence:    float64Ptr(0.8),
			Explanation: stringPtr(
				"SledTrace found an answer sentence whose important terms are weakly supported by the retrieved chunks.",
			),
			Details: models.JSONMap{
				"rule":          TypeAnswerNotGrounded,
				"answer":        answer,
				"claim":         unsupported.Claim,
				"claim_terms":   unsupported.ClaimTerms,
				"matched_terms": unsupported.MatchedTerms,
				"missing_terms": unsupported.MissingTerms,
				"support_score": unsupported.SupportRatio,
				"chunk_id":      chunkID,
				"chunk_rank":    unsupported.BestChunkRank,
				"reason":        "answer claim has weak lexical support in retrieved chunks",
			},
			Evidence:          evidence,
			Diagnostics:       diagnostics,
			Signals:           signals,
			RecommendedAction: stringPtr("Compare the unsupported answer claim with the retrieved chunks and tighten the prompt to avoid adding facts that are not present in context."),
			CreatedAt:         time.Now().UTC().Format(time.RFC3339Nano),
		},
	}
}

func findUnsupportedAnswerClaim(answer string, chunks []retrievedChunk) *answerClaimSupportCandidate {
	claims := splitAnswerClaims(answer)

	var weakest *answerClaimSupportCandidate

	for _, claim := range claims {
		if isSkippableAnswerClaim(claim) {
			continue
		}

		claimTerms := importantContextTerms(claim)
		if len(claimTerms) < 2 {
			continue
		}

		candidate := bestClaimSupport(claim, claimTerms, chunks)
		if candidate == nil {
			continue
		}

		if candidate.SupportRatio >= 0.45 {
			continue
		}

		if weakest == nil || candidate.SupportRatio < weakest.SupportRatio {
			weakest = candidate
		}
	}

	return weakest
}

func splitAnswerClaims(answer string) []string {
	result := make([]string, 0)

	start := 0
	for index, char := range answer {
		if char != '.' && char != '!' && char != '?' && char != '\n' {
			continue
		}

		claim := strings.TrimSpace(answer[start : index+len(string(char))])
		if claim != "" {
			result = append(result, claim)
		}

		start = index + len(string(char))
	}

	if start < len(answer) {
		claim := strings.TrimSpace(answer[start:])
		if claim != "" {
			result = append(result, claim)
		}
	}

	return result
}

func isSkippableAnswerClaim(claim string) bool {
	claim = strings.TrimSpace(claim)
	if len(claim) < 24 {
		return true
	}

	if containsUncertaintyPhrase(claim) {
		return true
	}

	normalized := strings.ToLower(claim)
	skipPrefixes := []string{
		"according to the context",
		"based on the context",
		"based on the retrieved context",
		"the retrieved context says",
	}

	for _, prefix := range skipPrefixes {
		if strings.HasPrefix(normalized, prefix) {
			return true
		}
	}

	return false
}

func bestClaimSupport(claim string, claimTerms []string, chunks []retrievedChunk) *answerClaimSupportCandidate {
	var best *answerClaimSupportCandidate

	for index, chunk := range chunks {
		chunkTerms := importantContextTerms(chunk.Text)
		matchedTerms := sharedContextTerms(claimTerms, chunkTerms)
		missingTerms := missingTerms(claimTerms, matchedTerms)

		supportRatio := 0.0
		if len(claimTerms) > 0 {
			supportRatio = float64(len(matchedTerms)) / float64(len(claimTerms))
		}

		candidate := answerClaimSupportCandidate{
			Claim:         claim,
			ClaimTerms:    claimTerms,
			BestChunk:     chunk,
			BestChunkRank: index + 1,
			MatchedTerms:  matchedTerms,
			MissingTerms:  missingTerms,
			SupportRatio:  supportRatio,
		}

		if best == nil || isBetterClaimSupport(candidate, *best) {
			best = &candidate
		}
	}

	return best
}

func isBetterClaimSupport(candidate answerClaimSupportCandidate, current answerClaimSupportCandidate) bool {
	if candidate.SupportRatio != current.SupportRatio {
		return candidate.SupportRatio > current.SupportRatio
	}

	candidateScore := -1.0
	if score := higherIsBetterScore(candidate.BestChunk); score != nil {
		candidateScore = *score
	}

	currentScore := -1.0
	if score := higherIsBetterScore(current.BestChunk); score != nil {
		currentScore = *score
	}

	if candidateScore != currentScore {
		return candidateScore > currentScore
	}

	return candidate.BestChunkRank < current.BestChunkRank
}

type retrievedChunk struct {
	ChunkID        string         `json:"chunk_id"`
	ID             string         `json:"id"`
	Text           string         `json:"text"`
	Content        string         `json:"content"`
	Score          *float64       `json:"score"`
	ScoreType      string         `json:"score_type"`
	ScoreDirection string         `json:"score_direction"`
	Metadata       models.JSONMap `json:"metadata"`

	SpanID   string
	SpanName string
}

func higherIsBetterScore(chunk retrievedChunk) *float64 {
	if chunk.Score == nil {
		return nil
	}

	direction := strings.ToLower(strings.TrimSpace(chunk.ScoreDirection))
	scoreType := strings.ToLower(strings.TrimSpace(chunk.ScoreType))

	switch direction {
	case "higher_is_better":
		return chunk.Score
	case "lower_is_better", "unknown":
		return nil
	case "":
		// Preserve unannotated historical score payloads as higher-is-better.
		switch scoreType {
		case "", "score", "similarity", "relevance", "rerank":
			return chunk.Score
		case "distance", "unknown":
			return nil
		default:
			// A new metric without direction is not safe to compare.
			return nil
		}
	default:
		// Invalid direction annotations fail closed instead of guessing.
		return nil
	}
}

func extractRetrievedChunks(spans []models.Span) []retrievedChunk {
	result := make([]retrievedChunk, 0)

	for _, span := range spans {
		if span.Type != "retrieval" {
			continue
		}

		result = append(result, extractRetrievedChunksFromSpan(span)...)
	}

	return result
}

func extractRetrievedChunksFromSpan(span models.Span) []retrievedChunk {
	result := make([]retrievedChunk, 0)

	result = append(result, chunksFromMap(span.Output)...)
	result = append(result, chunksFromMap(span.Metadata)...)

	normalizeChunks(result)

	for i := range result {
		result[i].SpanID = span.SpanID
		result[i].SpanName = span.Name
	}

	return result
}

func chunksFromMap(value models.JSONMap) []retrievedChunk {
	if value == nil {
		return nil
	}

	keys := []string{
		"retrieved_chunks",
		"chunks",
		"documents",
		"contexts",
	}

	for _, key := range keys {
		raw, ok := value[key]
		if !ok {
			continue
		}

		chunks := parseChunks(raw)
		if len(chunks) > 0 {
			return chunks
		}
	}

	return nil
}

func parseChunks(raw any) []retrievedChunk {
	data, err := json.Marshal(raw)
	if err != nil {
		return nil
	}

	var chunks []retrievedChunk
	if err := json.Unmarshal(data, &chunks); err == nil {
		normalizeChunks(chunks)
		return chunks
	}

	// Fallback for simple []string contexts.
	var texts []string
	if err := json.Unmarshal(data, &texts); err == nil {
		result := make([]retrievedChunk, 0, len(texts))
		for i, text := range texts {
			result = append(result, retrievedChunk{
				ChunkID: fmt.Sprintf("chunk_%d", i+1),
				Text:    text,
			})
		}
		return result
	}

	return nil
}

func normalizeChunks(chunks []retrievedChunk) {
	for i := range chunks {
		if chunks[i].ChunkID == "" {
			chunks[i].ChunkID = chunks[i].ID
		}

		if chunks[i].ChunkID == "" {
			chunks[i].ChunkID = fmt.Sprintf("chunk_%d", i+1)
		}

		if chunks[i].Text == "" {
			chunks[i].Text = chunks[i].Content
		}
	}
}

func getLowScoreThreshold(span models.Span) float64 {
	if span.Metadata == nil {
		return DefaultLowScoreThreshold
	}

	raw, ok := span.Metadata["low_score_threshold"]
	if !ok {
		return DefaultLowScoreThreshold
	}

	switch value := raw.(type) {
	case float64:
		return value
	case float32:
		return float64(value)
	case int:
		return float64(value)
	default:
		return DefaultLowScoreThreshold
	}
}

func normalizeChunkText(text string) string {
	text = strings.ToLower(strings.TrimSpace(text))
	if text == "" {
		return ""
	}

	fields := strings.Fields(text)
	return strings.Join(fields, " ")
}

var refundWindowRegex = regexp.MustCompile(`(?i)\b(\d{1,3})\s*[- ]?\s*days?\b`)

func extractRefundWindowDays(text string) []string {
	matches := refundWindowRegex.FindAllStringSubmatch(text, -1)

	seen := map[string]bool{}
	result := make([]string, 0)

	for _, match := range matches {
		if len(match) < 2 {
			continue
		}

		value := match[1]
		if seen[value] {
			continue
		}

		seen[value] = true
		result = append(result, value)
	}

	sort.Strings(result)

	return result
}

func extractFinalAnswer(payload models.TracePayload) (string, *string) {
	if payload.Trace.Output != nil {
		if answer := stringFromMap(payload.Trace.Output, "answer"); answer != "" {
			return answer, nil
		}

		if response := stringFromMap(payload.Trace.Output, "response"); response != "" {
			return response, nil
		}
	}

	// Prefer the last LLM span output.
	for i := len(payload.Spans) - 1; i >= 0; i-- {
		span := payload.Spans[i]
		if span.Type != "llm" {
			continue
		}

		if span.Output == nil {
			continue
		}

		spanID := span.SpanID

		if answer := stringFromMap(span.Output, "answer"); answer != "" {
			return answer, &spanID
		}

		if response := stringFromMap(span.Output, "response"); response != "" {
			return response, &spanID
		}
	}

	return "", nil
}

func stringFromMap(value models.JSONMap, key string) string {
	if value == nil {
		return ""
	}

	raw, ok := value[key]
	if !ok {
		return ""
	}

	text, ok := raw.(string)
	if !ok {
		return ""
	}

	return text
}

func containsUncertaintyPhrase(answer string) bool {
	normalized := strings.ToLower(answer)

	phrases := []string{
		"i could not find",
		"not enough information",
		"insufficient information",
		"i don't know",
		"cannot determine",
		"unable to determine",
		"no information",
	}

	for _, phrase := range phrases {
		if strings.Contains(normalized, phrase) {
			return true
		}
	}

	return false
}

func newWarningID() string {
	return newPrefixedID("warning")
}

func newPrefixedID(prefix string) string {
	buffer := make([]byte, 8)

	if _, err := rand.Read(buffer); err != nil {
		return fmt.Sprintf("%s_%d", prefix, time.Now().UnixNano())
	}

	return prefix + "_" + hex.EncodeToString(buffer)
}
