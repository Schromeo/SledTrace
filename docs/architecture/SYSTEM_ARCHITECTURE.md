# System Architecture

## Current Architecture

SledTrace currently runs as local-first components:

```text
Python SDK
  -> Go Collector
  -> SQLite

React Dashboard
  <- Go Collector API
```

## Components

### Python SDK

The Python SDK explicitly instruments RAG or bounded AI application steps;
it does not execute models or tools.

It records:

- trace metadata
- retrieval spans
- retrieved chunks
- LLM calls
- caller-instrumented synchronous tool steps and failed LLM attempts
- final answer or explicit task result/acceptance
- supplied usage, or explicit completed Responses usage via the optional helper

It sends trace payloads to the collector using:

- `POST /api/traces`

### Go Collector

The collector is a local HTTP service, running by default at:

- `http://localhost:4319`

The native process listens on `127.0.0.1:4319` by default. Docker keeps the
container-internal listener on `:4319`, but publishes its host port on
`127.0.0.1` by default. Intentional remote use must set
`SLEDTRACE_COLLECTOR_ADDR` or the Compose `SLEDTRACE_BIND_HOST` explicitly.

Browser CORS access defaults to the exact local Dashboard origins
`http://localhost:5173` and `http://127.0.0.1:5173`. A comma-separated
`SLEDTRACE_ALLOWED_ORIGINS` value replaces that list. Requests from the SDK or
command-line tools without an `Origin` header are unaffected.

Implemented endpoints:

- `GET /health`
- `POST /api/traces`
- `GET /api/traces`
- `GET /api/traces/{trace_id}`

The collector validates incoming trace payloads and persists data to SQLite.

### SQLite

SQLite is the local storage backend.

Current tables:

- `traces`
- `spans`
- `warnings`

Note:

- Warning generation is implemented in the Go collector.
- Warning Engine / Diagnosis Layer MVP is complete with:
  - `no_retrieved_chunks`
  - `low_retrieval_score` (default threshold `0.5`, overridable via span metadata)
  - `duplicate_chunks`
  - `conflicting_chunks`
  - `weak_query_chunk_overlap`
  - `numeric_mismatch`
  - deterministic `answer_not_grounded` (requires retrieval evidence)

### React Dashboard

The dashboard runs locally with Vite, whose development and preview listeners
default to `127.0.0.1:5173`. Docker publishes the Nginx port to host loopback by
default while leaving container-internal listening unchanged.

It reads collector APIs and displays:

- trace list
- trace detail
- span timeline
- retrieval chunks
- LLM prompt and response
- metadata
- warning cards with evidence and heuristic limitations
- ordered tool/LLM attempts, explicit task result and usage subtotal/coverage

## Current Data Flow

1. Developer runs a RAG app instrumented with the Python SDK.
2. SDK records explicit retrieval, LLM and/or synchronous tool spans.
3. SDK calls `t.flush()`.
4. Collector receives the trace payload.
5. Collector stores trace and spans in SQLite.
6. Collector runs the warning engine.
7. Collector stores generated warnings in SQLite.
8. Dashboard fetches traces from the collector.
9. Developer inspects spans and warnings in the browser.

Primary smoke test path:

- `sdk/python/examples/warning_rules_demo.py`
- run all or single-rule demos
- expected per-case collector response: `warnings_generated: 1`

## Warning Engine Flow

The warning engine runs inside the Go collector after trace ingestion and before the response is returned from `POST /api/traces`.

Current flow:

```text
POST /api/traces
  -> save trace/spans
  -> run warning engine
  -> save warnings
  -> return stored response with warnings_generated
```

## Local candidate source evidence path — P3B

The [roadmap](../product/ROAD_TO_V1_0.md) selects a bounded MAMR
source-event → sanitized diagnostic bundle → importer → existing local stack
path, now locally connected with offline fixtures. Capture happens at the actual call/validator boundary; submission can
occur after completion/interruption. This is not a live Collector stream or
generic JavaScript SDK.

Call, contract-validation, workflow and task-quality states stay distinct.
Generic trace POST still stores trace/spans and warnings in separate transactions.
The dedicated MAMR route strictly validates the existing allowlisted source JSON
and uses P3A's single transaction for trace/spans/warnings/import manifest.
Exact re-import is a no-op; changed same-room content conflicts. Source evidence
and counted attempts are separate. [Contract](../integrations/MAMR_DIAGNOSTIC_IMPORT.md).
Secret/content controls apply before data leaves the application.
P4 locally derives a bounded D1 gate explanation at view time from accepted
source metadata. It adds no warning-engine/persistence contract. No explicit
causal links were exported, so workflow context is not an impact chain. P5B reads
two existing GET details with a user-declared pair file in page memory only;
no new route/table/source schema. [Contract](../integrations/PAIR_EVIDENCE.md).
D2/D3 remain unimplemented; no general Agent diagnosis or real fix is implied.


