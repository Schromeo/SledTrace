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

The Python SDK instruments a RAG pipeline.

It records:

- trace metadata
- retrieval spans
- retrieved chunks
- LLM calls
- final answer

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
  - simplified `answer_not_grounded`

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
- warning cards

## Current Data Flow

1. Developer runs a RAG app instrumented with the Python SDK.
2. SDK records retrieval and LLM spans.
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


