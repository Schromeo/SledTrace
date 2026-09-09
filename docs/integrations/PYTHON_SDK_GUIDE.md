# Python SDK Guide

This guide covers the current SledTrace Python SDK API.

It is intentionally API-focused. For broader product positioning and local-first onboarding flow, see `docs/product/USER_ONBOARDING.md`.

Current scope only:

- local-first tracing
- `trace(...)`
- retrieval spans
- LLM spans
- local collector flushes

Out of scope for this guide:

- LangChain integration
- LlamaIndex integration
- OpenAI or Anthropic integration guides
- agent, tool, or memory spans
- cloud sync, auth, or hosted features

## Installation

Install the released SDK from PyPI:

```bash
python -m pip install sledtrace
```

Use an editable install when developing SledTrace itself.

### Install while working inside the SledTrace repo

```bash
cd sdk/python
python -m pip install -e .
```

### Install into another local application

```bash
python -m pip install -e /path/to/sledtrace/sdk/python
```

## Collector URL

The default local collector URL is:

```txt
http://localhost:4319
```

Recommended local startup from the repo checkout:

From the SledTrace repo root:

```bash
python scripts/start-sledtrace.py
```

This repo-local helper starts the collector from `collector/go` and the dashboard from `dashboard/web`.

You can still start services manually if needed.

Collector:

```bash
cd collector/go
go run ./cmd/sledtrace-collector
```

Dashboard:

```bash
cd dashboard/web
npm ci
npm run dev
```

If this is your first non-Docker Dashboard startup, run `npm ci` before `npm run dev`.

You can configure the collector URL through an environment variable in your app process.

Bash / Mac / Linux:

```bash
export SLEDTRACE_COLLECTOR_URL=http://localhost:4319
```

Windows PowerShell:

```powershell
$env:SLEDTRACE_COLLECTOR_URL="http://localhost:4319"
```

The current SDK API also lets you pass an explicit collector URL through `trace(...)` or `flush(...)`.

## API Summary

Current implemented API:

```python
trace(name, query=None, metadata=None, collector_url=None)
t.retrieval(query, chunks, name="retrieval", top_k=None, metadata=None)
t.llm(model, prompt=None, response=None, messages=None, name="llm", provider=None, input_tokens=None, output_tokens=None, latency_ms=None, metadata=None)
t.flush(collector_url=None, timeout=5.0)
```

`trace(...)` returns a `SledTraceTrace` context manager.

In normal usage, one trace should represent one user request or one top-level RAG pipeline run.

## Basic Trace Example

```python
from sledtrace import trace


def answer_question(user_query: str) -> str:
    with trace(
        name="custom-rag-pipeline",
        query=user_query,
        metadata={
            "app": "my-rag-app",
            "environment": "local",
        },
    ) as t:
        chunks = my_retriever(user_query)

        t.retrieval(
            query=user_query,
            chunks=chunks,
            name="primary_retrieval",
            top_k=len(chunks),
            metadata={
                "retriever": "my_retriever_v1",
            },
        )

        prompt, answer = my_answerer(user_query, chunks)

        t.llm(
            model="local-answerer-v1",
            prompt=prompt,
            response=answer,
            name="answer_generation",
            provider="local",
        )

    t.flush()
    return answer
```

## Retrieval Span Example

Use `t.retrieval(...)` to record one retrieval step.

```python
t.retrieval(
    query=user_query,
    chunks=chunks,
    name="primary_retrieval",
    top_k=4,
    metadata={
        "retriever": "bm25-local",
        "low_score_threshold": 0.5,
    },
)
```

Behavior:

- records a span with type `retrieval`
- stores the retrieval query in span input
- stores retrieved chunks in span output
- if the trace-level query was not set, the retrieval query becomes the trace query

## Recommended Chunk Shape

The SDK accepts a list of chunk dictionaries.

Example:

```python
chunks = [
    {
        "id": "chunk_refund_current",
        "text": "Customers may request a refund within 30 days of purchase.",
        "score": 0.93,
        "rank": 1,
        "source": "refund_policy.md",
        "document_id": "refund_policy",
        "metadata": {
            "section": "refund_window",
            "policy_version": "current",
        },
    }
]
```

Recommended fields for better diagnostics:

- `id`
- `text`
- `score`
- `rank`
- `source`
- `document_id`
- `metadata`

Current SDK chunk behavior:

- retrieval chunks are shallow-copied before normalization
- if `rank` is missing, SDK auto-fills it using 1-based list position
- if `metadata` is missing or `None`, SDK auto-fills it as `{}`
- the SDK does not currently hard-validate fields like `text`, `score`, or `source`

Sparse chunks may still ingest, but diagnostics are better when `text`, `score`, `source`, `document_id`, `rank`, and `metadata` are present.

## LLM Span Examples

Use `t.llm(...)` to record one LLM step.

Current behavior:

- records a span with type `llm`
- supports both `prompt` and `messages`
- if `response` is provided, it becomes the trace final answer
- `provider`, `input_tokens`, `output_tokens`, `total_tokens`, and `latency_ms` are stored in span metadata

Usage note:

- use `prompt` for text-style model calls
- use `messages` for chat-style model calls
- at least one of `prompt` or `messages` should normally be provided for useful debugging

### Prompt-based example

```python
t.llm(
    model="local-answerer-v1",
    prompt=prompt,
    response=answer,
    name="answer_generation",
    provider="local",
    input_tokens=120,
    output_tokens=24,
    latency_ms=35,
)
```

### Messages-based example

```python
t.llm(
    model="local-chat-answerer-v1",
    messages=[
        {"role": "system", "content": "Answer using the retrieved context only."},
        {"role": "user", "content": "What is the refund window?"},
    ],
    response="The refund window is 30 days from purchase.",
    name="chat_answer_generation",
    provider="local",
)
```

## flush() Behavior

`flush()` sends the trace payload to the local collector by POSTing to:

```txt
POST http://localhost:4319/api/traces
```

More generally:

```txt
POST {collector_url}/api/traces
```

Recommended usage:

```python
with trace(name="my-trace", query=query) as t:
    ...

t.flush()
```

Why this matters:

- `ended_at` and `duration_ms` are finalized when the trace context exits
- flushing inside the `with` block can send incomplete lifecycle fields
- `flush()` accepts optional `collector_url` and `timeout` arguments

## Error Trace Behavior

If an exception escapes the `with trace(...)` block:

- trace status becomes `error`
- error details are added under trace metadata
- the exception is not suppressed

That means the SDK records the failure state, but your application still receives the exception unless you catch it yourself.

## Common Mistakes

### Collector not running

If the collector is not listening on `http://localhost:4319`, `flush()` will fail.

### Calling `flush()` inside the `with` block

This can send a trace before `ended_at` and `duration_ms` are finalized.

### Forgetting to convert retriever results into dict chunks

The SDK expects chunk dictionaries, not arbitrary retriever-native objects.

### Missing chunk `text`, `score`, or `source`

The SDK may still ingest sparse chunks, but dashboard readability and warning quality will be worse.

### Using `local_rag_demo` as the integration point

Do not modify `local_rag_demo` for real usage. Instrument your own application code instead.

### Installing the SDK into the wrong virtualenv

If your app runs in one virtual environment and `SledTrace` was installed into another, imports will fail.

### Expecting `sledtrace serve` to work outside a source checkout

The installed CLI provides help and version commands everywhere, but `sledtrace serve` needs the repository's Collector and Dashboard files. Clone SledTrace and run `serve` from inside that checkout.

## Troubleshooting

### Check collector health

```bash
curl http://localhost:4319/health
```

### Check `SLEDTRACE_COLLECTOR_URL`

Make sure your application process points at the collector you actually started.

### Run the local SDK example

Make sure the collector is already running before you execute the example.
Unless you explicitly overrode it, the collector URL should be `http://localhost:4319`.

From `sdk/python`:

```bash
python -m examples.custom_pipeline_demo
```

### Refresh the dashboard

If the trace was flushed successfully but is not visible yet, refresh the dashboard page.

### Check collector logs

If `flush()` fails or traces do not appear, inspect the collector terminal output first.



