# SledTrace v0.3 - Diagnostic Intelligence

## Purpose

Define the scope and design for SledTrace v0.3 - RAG Quality Analysis / Diagnostic Intelligence.

v0.3 upgrades SledTrace from simple warning flags into evidence-backed diagnostic insights.

Warnings should explain why they were raised, which chunks, claims, and values were involved, and which deterministic signals triggered the diagnosis.

The design remains local-first and deterministic-first.

## Status Update

As of 2026-07-06, the v0.3 diagnostic intelligence core is implemented and smoke-tested.

As of 2026-07-08, v0.3.5 diagnostic-quality hardening is also implemented and smoke-tested.

Completed in v0.3.5:

- warning-engine numeric range extraction supports both hyphen and natural-language range forms
- conflicting chunk selection is relevance-aware and query-gated
- deterministic numeric-expression topic classifier reduces cross-topic conflict noise
- warning-engine regression coverage expanded for range and relevance behavior
- thin reference integration app (`sdk/python/examples/reference_rag_app/`) validates mixed raw retrieval-shape normalization
- deterministic demo-answer cleanup reduces avoidable grounding-noise while preserving weak-case true positives

Validated with:

```bash
cd collector/go
go test ./... -count=1

cd sdk/python
python -m examples.reference_rag_app.run all
python -m examples.reference_rag_app.run processing-range
python -m examples.reference_rag_app.run wrong-processing-range
python -m examples.real_llm_rag_demo all
```

Completed in code:

- Warning Schema v2 default enrichment in the collector
- evidence-backed warning payloads with signals and diagnostics
- `weak_query_chunk_overlap`
- `numeric_mismatch`
- evidence-backed `answer_not_grounded`
- evidence-backed `conflicting_chunks`
- diagnostic quality demo cases
- dashboard warning detail UI for evidence, numeric diffs, and recommended actions

Validated with:

```bash
cd collector/go
go test ./...

cd dashboard/web
npm run build

cd sdk/python
python -m examples.diagnostic_quality_demo all
```

Current implemented span types are still only:

- `retrieval`
- `llm`

Current shipped warning rules are now:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- `weak_query_chunk_overlap`
- `conflicting_chunks`
- `answer_not_grounded`
- `numeric_mismatch`

v0.3 establishes the first implemented evidence-backed diagnostic layer without introducing cloud dependencies, framework adapters, or non-deterministic judge systems.

---

## 1. v0.3 Goal

The goal of v0.3 is to help a developer answer three questions for a bad RAG response:

1. Why did SledTrace raise this warning?
2. What exact evidence inside the trace triggered it?
3. Which part of the failure came from retrieval quality versus answer grounding?

In practical terms, v0.3 should turn each warning from a short label into a structured diagnostic result with:

- deterministic signals
- linked evidence
- extracted claims or values when useful
- a short explanation suitable for the dashboard
- a stable machine-readable schema for future rule expansion

---

## 2. Explicit In-Scope Items

v0.3 is in scope for the following work:

- warning schema v2 with richer evidence and signal fields
- evidence item schema that can point to chunks, answer snippets, and span fields
- diagnostic object schema for structured extracted facts used by rules
- enhanced deterministic warning rules for retrieval quality and answer grounding
- dashboard UX that shows why a warning fired instead of only showing its title
- demo traces that clearly exercise each new warning rule
- rule logic built only from local deterministic heuristics over trace data already captured by SledTrace

Additional scope clarifications:

- use only current `retrieval` and `llm` spans
- use only local trace data already stored or naturally derivable from those spans
- support multiple evidence items per warning
- allow warnings to carry both a human-readable explanation and structured machine-readable details
- prefer simple, inspectable heuristics over opaque scoring systems

---

## 3. Explicit Out-of-Scope Items

The following are explicitly out of scope for v0.3:

- LangChain integration
- LlamaIndex integration
- PyPI publishing work
- Docker or Docker Compose work
- CLI packaging
- agent spans
- tool spans
- memory spans
- cloud sync or hosted collector features
- auth or multi-user features
- LLM-as-judge or any model-based evaluator
- hidden semantic scoring systems that cannot be explained from trace evidence
- generalized eval platform work beyond warning diagnostics for RAG traces
- non-deterministic rewrite or remediation agents

Also out of scope for v0.3:

- adding new primary span types beyond `retrieval` and `llm`
- introducing embeddings-only or vector-store-specific diagnostics that require vendor-specific adapters
- attempting to solve every hallucination pattern; the milestone should focus on a small, explainable first set of rules

---

## 4. Warning Schema v2 Design

## Design intent

Warning Schema v2 should preserve the simple top-level warning concept while making each warning inspectable and evidence-backed.

Each warning should contain:

- identity
- severity
- short summary
- detailed explanation
- deterministic triggering signals
- linked evidence items
- linked diagnostic objects
- optional thresholds or comparison values used by the rule

## Proposed logical shape

```json
{
  "warning_id": "warn_01",
  "trace_id": "trace_01",
  "rule_id": "answer_not_grounded_v2",
  "schema_version": "2",
  "status": "active",
  "severity": "high",
  "title": "Answer claim is weakly grounded in retrieved evidence",
  "summary": "The answer contains a concrete claim that is not well supported by the retrieved chunks.",
  "explanation": "The answer states '14 days', but the strongest retrieved support points to '30 days' and overlap with the cited answer claim is weak.",
  "category": "grounding",
  "span_ids": ["span_retrieval_1", "span_llm_1"],
  "signals": [
    {
      "signal_id": "answer_numeric_value_mismatch",
      "label": "Answer numeric value differs from strongest retrieved value",
      "observed": "14",
      "expected": "30",
      "comparator": "not_equal",
      "strength": "strong"
    }
  ],
  "thresholds": {
    "min_overlap_ratio": 0.2,
    "min_supporting_chunks": 1
  },
  "evidence_items": ["evidence_01", "evidence_02", "evidence_03"],
  "diagnostic_object_ids": ["diag_answer_claim_01", "diag_chunk_fact_02"],
  "recommended_action": "Inspect retrieval ranking and verify whether the answer copied an outdated value.",
  "created_at": "2026-07-06T00:00:00Z"
}
```

## Required Warning Schema v2 fields

| Field | Purpose |
| --- | --- |
| `warning_id` | Stable warning record identifier |
| `trace_id` | Parent trace |
| `rule_id` | Warning rule name such as `numeric_mismatch` |
| `schema_version` | Distinguishes v2 warnings from current simpler warnings |
| `severity` | UI sorting and emphasis |
| `title` | Short card title |
| `summary` | One-sentence explanation |
| `explanation` | More specific rule result text |
| `category` | Example: `retrieval`, `grounding`, `conflict`, `coverage` |
| `span_ids` | Relevant `retrieval` and or `llm` spans |
| `signals` | Deterministic trigger facts the rule observed |
| `evidence_items` | IDs of linked evidence objects |
| `diagnostic_object_ids` | IDs of reusable extracted structures |

## Notes

- `rule_id` should stay stable even if explanation text changes.
- `signals` are not free-form chain-of-thought. They are compact observed facts.
- `thresholds` should be included only when useful for debugging a heuristic threshold.
- The schema should work whether a warning has one evidence item or many.

---

## 5. EvidenceItem Schema Design

## Design intent

An evidence item is the atomic UI-ready proof object behind a warning.

It should answer: what exact text, chunk, answer fragment, or span field contributed to this diagnosis?

Evidence items should be small, direct, and linkable.

## Proposed logical shape

```json
{
  "evidence_id": "evidence_01",
  "type": "chunk_snippet",
  "label": "Retrieved chunk with strongest conflicting refund window",
  "span_id": "span_retrieval_1",
  "chunk_id": "chunk_2",
  "source": "refund_policy_old.md",
  "locator": {
    "field": "text",
    "start_char": 0,
    "end_char": 46
  },
  "snippet": "Customers may request a refund within 14 days.",
  "attributes": {
    "rank": 2,
    "score": 0.84,
    "normalized_value": "14 days"
  },
  "diagnostic_object_ids": ["diag_chunk_fact_02"]
}
```

## Evidence item types

Initial v0.3 evidence item types should include:

- `query_text`
- `answer_snippet`
- `chunk_snippet`
- `chunk_score`
- `numeric_value`
- `overlap_measure`
- `conflict_pair`
- `retrieval_stat`

## Required EvidenceItem fields

| Field | Purpose |
| --- | --- |
| `evidence_id` | Stable identifier within the warning payload |
| `type` | What kind of proof object this is |
| `label` | Human-readable description for UI |
| `span_id` | Related span |
| `chunk_id` | Optional chunk linkage for retrieval evidence |
| `snippet` | Exact text or value shown in the UI |
| `attributes` | Structured values such as score, rank, overlap ratio, numeric value |

## Notes

- Evidence items should prefer exact snippets over vague summaries.
- A single warning may include evidence from both `retrieval` and `llm` spans.
- Evidence items should remain deterministic artifacts and must not include hidden model reasoning.

---

## 6. DiagnosticObject Schema Design

## Design intent

Diagnostic objects are structured intermediate artifacts extracted by deterministic analysis.

They are more reusable than evidence items.

Example: a warning may refer to the same answer claim, numeric value, or chunk fact from multiple evidence items. That shared structure should live as a diagnostic object.

## Proposed logical shape

```json
{
  "diagnostic_object_id": "diag_answer_claim_01",
  "type": "answer_claim",
  "label": "Refund window claim in final answer",
  "span_id": "span_llm_1",
  "text": "Customers may request a refund within 14 days.",
  "normalized": {
    "entity": "refund_window",
    "numeric_value": 14,
    "unit": "days"
  },
  "attributes": {
    "claim_kind": "numeric_policy_fact",
    "confidence": "deterministic_extracted"
  }
}
```

## Initial DiagnosticObject types

- `answer_claim`
- `chunk_fact`
- `numeric_claim`
- `query_term_set`
- `overlap_result`
- `conflict_group`
- `retrieval_summary`

## Required DiagnosticObject fields

| Field | Purpose |
| --- | --- |
| `diagnostic_object_id` | Stable identifier referenced by warnings and evidence items |
| `type` | Type of extracted structured artifact |
| `label` | Human-readable descriptor |
| `span_id` | Source span |
| `text` | Raw text the object was derived from when relevant |
| `normalized` | Structured normalized values used by rules |
| `attributes` | Additional deterministic metadata |

## Notes

- Diagnostic objects should stay lightweight and rule-driven.
- The system should not attempt open-ended knowledge extraction in v0.3.
- A rule can emit warning evidence directly, but reusable extracted facts should be promoted into diagnostic objects.

---

## 7. First Enhanced Warning Rules

The first v0.3 rules should stay intentionally narrow, deterministic, and explainable.

## `low_retrieval_score_v2`

### Intent

Upgrade the existing low score warning so it explains not just that the top score is low, but how low it was and how the overall retrieval distribution looked.

### Trigger idea

Raise when the top retrieval score is below a configured threshold, with optional contextual signals such as narrow separation between top results or weak score spread.

### Deterministic signals

- top chunk score
- average top-k score
- gap between rank 1 and rank 2
- retrieved chunk count

### Evidence examples

- top chunk score value
- score list for top-k chunks
- query text

### Why it matters

This helps the user distinguish poor retrieval confidence from later answer-generation issues.

## `weak_query_chunk_overlap`

### Intent

Detect cases where retrieved chunks have weak lexical overlap with the user query, even if scores are present.

### Trigger idea

Raise when normalized query terms have low overlap with the top retrieved chunks.

### Deterministic signals

- query token set
- per-chunk overlap ratio
- missing key query terms
- top-k average overlap ratio

### Evidence examples

- query terms not found in any top chunk
- chunk snippets with low supporting term overlap
- overlap measurements per chunk

### Why it matters

This surfaces retrieval mismatch that raw score thresholds may miss.

## `answer_not_grounded_v2`

### Intent

Upgrade the simplified grounding warning into an evidence-backed diagnostic that points to unsupported answer claims.

### Trigger idea

Raise when a concrete answer claim has weak support across retrieved chunks based on lexical overlap, missing key terms, or contradiction with stronger chunk facts.

### Deterministic signals

- extracted answer claim text
- supporting chunk count
- overlap ratio between answer claim and best matching chunks
- presence or absence of key claim terms in retrieved text
- whether a stronger conflicting chunk fact exists

### Evidence examples

- answer snippet containing the unsupported claim
- retrieved chunk snippets with strongest candidate support
- query text when the answer diverges from the request intent

### Why it matters

This is the core diagnostic for "the model answered something the retrieval context does not actually support."

## `numeric_mismatch`

### Intent

Detect cases where the answer states a numeric value that differs from numeric values found in retrieved chunks.

### Trigger idea

Raise when the answer contains an extracted numeric claim and the strongest retrieved evidence contains a conflicting numeric value for the same local concept.

### Deterministic signals

- answer numeric value
- one or more retrieved numeric values
- local phrase match around the value, such as `refund`, `days`, `window`
- best-supported retrieved value and its score/rank

### Evidence examples

- answer snippet: `14 days`
- chunk snippet: `30 days`
- conflicting chunk snippet: `14 days` from old source when relevant

### Why it matters

This gives a more concrete and actionable version of answer grounding failure for common policy and pricing cases.

## `conflicting_chunks_v2`

### Intent

Upgrade the current conflict warning so it explains which chunks conflict, around which normalized fact, and which values differ.

### Trigger idea

Raise when multiple retrieved chunks appear to express incompatible values for the same local concept.

### Deterministic signals

- same local entity or phrase context
- differing normalized values
- source/version metadata when available
- ranks and scores of conflicting chunks

### Evidence examples

- chunk pair with highlighted conflicting snippets
- extracted normalized values such as `14 days` vs `30 days`
- source labels showing old versus new policy documents when present

### Why it matters

This helps the user see that the retrieval set itself is internally inconsistent before blaming the answer model alone.

## Rule interaction guidance

- Multiple warnings may fire on one trace.
- `conflicting_chunks_v2` and `numeric_mismatch` should often co-occur in the refund-policy scenario.
- `answer_not_grounded_v2` should remain a broader rule, while `numeric_mismatch` is a specialized sub-case with stronger evidence.
- Rules should be designed to reuse shared diagnostic objects where possible.

---

## 8. Dashboard Evidence-Backed Warning UX

The dashboard should evolve from basic warning cards into expandable evidence views.

## UX goals

- let a user understand a warning without reading raw JSON first
- show the evidence that triggered the warning
- make it obvious whether the issue is retrieval quality, internal chunk conflict, or answer grounding
- keep the UI inspectable and deterministic rather than "AI said so"

## Proposed warning card structure

Each warning card should display:

- warning title
- severity badge
- one-sentence summary
- expandable explanation section
- "why this fired" signal list
- linked evidence list
- optional compared values block for numeric or conflict rules

## Evidence panel behavior

When expanded, a warning should show:

- exact answer snippet when the warning references an answer claim
- exact chunk snippets with source, rank, and score
- extracted compared values where applicable
- short deterministic signal labels such as `top_score_below_threshold` or `missing_query_terms`

## UX principles

- default to compact summary, expand for proof
- keep evidence items visually tied to their chunk source and span type
- distinguish observed values from expected or stronger-support values
- avoid implying certainty beyond the heuristic strength of the rule

## Non-goals for UX in v0.3

- no free-form AI-generated explanation text
- no chat assistant inside the warning panel
- no complex graph exploration beyond current trace detail scope

---

## 9. Demo Cases Needed for v0.3

v0.3 needs explicit demo traces that prove the diagnostic layer is understandable, not just technically present.

## Required demo cases

### 1. Low-score retrieval case

Goal: trigger `low_retrieval_score_v2` with clearly weak top result scores.

Expected evidence:

- top score below threshold
- weak score distribution in top-k

### 2. Weak overlap retrieval case

Goal: trigger `weak_query_chunk_overlap` where the retrieved chunks do not meaningfully match key query terms.

Expected evidence:

- missing important query terms
- low per-chunk overlap ratios

### 3. Unsupported answer claim case

Goal: trigger `answer_not_grounded_v2` with an answer claim that cannot be supported by retrieved text.

Expected evidence:

- answer snippet
- low support count
- strongest candidate chunk still shows weak grounding

### 4. Numeric mismatch case

Goal: trigger `numeric_mismatch` where the answer states the wrong numeric value.

Expected evidence:

- answer value
- strongest retrieved value
- local phrase context tying both to the same concept

### 5. Conflicting chunk case

Goal: trigger `conflicting_chunks_v2` with top chunks that disagree on the same policy fact.

Expected evidence:

- chunk pair or group
- conflicting normalized values
- source labels and scores

### 6. Combined failure case

Goal: show a realistic trace where multiple warnings co-occur.

Suggested scenario:

- retrieval returns conflicting policy chunks
- top score is not especially strong
- final answer copies the outdated numeric value

Expected warnings:

- `conflicting_chunks_v2`
- `numeric_mismatch`
- `answer_not_grounded_v2`

---

## 10. Success Criteria

v0.3 is successful if the following are true:

- a developer can inspect a warning and see exactly what evidence triggered it
- warning records are structured enough for both dashboard rendering and future API consumers
- at least the first five enhanced warning rules are defined with deterministic inputs and outputs
- the diagnostic layer works only from local trace data and deterministic heuristics
- the dashboard can distinguish retrieval issues from grounding issues in a visible way
- the demo set makes each warning understandable within a few seconds of inspection
- the milestone does not introduce cloud features, auth, new span families, or LLM-as-judge dependencies

## Practical acceptance standard

For each v0.3 demo trace, a developer should be able to answer all of the following from the dashboard:

1. Which rule fired?
2. What exact text or values triggered it?
3. Which chunks or answer claims were involved?
4. Is the problem mainly retrieval quality, chunk conflict, or answer grounding?

If those answers are visible without reading collector code, v0.3 has met its product goal.


