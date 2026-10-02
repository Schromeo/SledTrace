# Real Local RAG Demo Milestone

## Status
Completed

## Goal
Replace mock retrieval chunks with real local retrieval output while keeping the existing SledTrace trace schema and warning pipeline unchanged.

## Why This Milestone
The Warning Engine / Diagnosis Layer MVP is complete and validated end-to-end.

This milestone validates that warnings remain useful on real retrieval data, not only synthetic demo chunks.

## Current Baseline (Already Working)

```text
Python SDK
  -> t.flush()
  -> POST /api/traces
  -> Go Collector (:4319)
  -> SQLite (traces/spans/warnings)
  -> GET /api/traces/{trace_id}
  -> React Dashboard warning cards
```

Implemented warning rules:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- `conflicting_chunks`
- simplified `answer_not_grounded`

Primary smoke test:

- `python -m examples.warning_rules_demo all`
- Expected: each case returns `warnings_generated: 1`.

## Completed

- Added local markdown policy documents.
- Implemented local document loader.
- Implemented deterministic chunking.
- Implemented TF-IDF + cosine similarity retriever.
- Added simple local answerer.
- Added demo case matrix.
- Integrated real local retrieval output with existing Python SDK trace schema.
- Sent traces to Go Collector on port `4319`.
- Verified traces in Dashboard.
- Verified existing warning rules trigger on real retrieval output.

## Non-Goals

- Do not introduce LangChain adapters in this milestone.
- Do not introduce LlamaIndex adapters in this milestone.
- Do not change trace/warning schema unless a blocker appears.

## Demo Commands

## Runbook

```powershell
# terminal 1
cd collector/go
go run ./cmd/sledtrace-collector

# terminal 2
cd sdk/python
$env:SLEDTRACE_COLLECTOR_URL="http://localhost:4319"
python -m examples.local_rag_demo.run_demo inspect
python -m examples.local_rag_demo.run_demo retrieve "How can I reset my password?"
python -m examples.local_rag_demo.run_demo trace duplicate
python -m examples.local_rag_demo.run_demo trace-all
python -m examples.warning_rules_demo all
```

## Expected Warning-Target Cases

- `no_match` -> `no_retrieved_chunks`
- `low_score` -> `low_retrieval_score`
- `duplicate` -> `duplicate_chunks`
- `conflict` -> `conflicting_chunks`
- `hallucinated` -> `answer_not_grounded`

## Risks (Observed and Remaining)

- Keyword-based retrieval may miss semantically similar phrasing.
- Character chunking can split facts at boundaries.
- Low-score thresholds may need tuning for real corpora.

## Follow-up After Completion

- Improve warning explanation and details rendering.
- Add unit tests for warning rules.
- Evaluate semantic retrieval baseline (sentence-transformers + cosine).
- Consider framework adapters after schema and warning behavior remain stable.



