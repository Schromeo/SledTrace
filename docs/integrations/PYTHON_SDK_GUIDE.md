# Python SDK Guide

This guide covers the current SledTrace Python SDK API.

It is intentionally API-focused. For a guided first integration, start with the
[quickstart](../QUICKSTART.md).

Covered here:

- `trace(...)` and span timing
- retrieval, LLM and tool spans, and the explicit task result
- chunk shape and retrieval score semantics
- flushing to the local collector
- recording OpenAI Responses usage

Not available: automatic LangChain / LlamaIndex / provider instrumentation,
memory or agent-loop spans, and cloud or hosted features.

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

Start the collector and dashboard with:

```bash
sledtrace serve
```

This serves both on `http://127.0.0.1:4319`. To run from a source checkout or
with Docker instead, see [development setup](../DEVELOPMENT.md).

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

## Validate an independent application

The source checkout contains a one-file application that imports only the
installed `sledtrace` package. It is intentionally separate from the built-in
RAG demo and can be copied into another directory after installing the wheel.
Repository examples track the SDK version declared in that checkout; if it is
newer than production PyPI, use the editable install or current built wheel.

With the Collector and Dashboard running, execute the success and business-error
paths from `sdk/python`:

```bash
python -m examples.independent_app success
python -m examples.independent_app application-error
```

The success path stores an `ok` trace containing one retrieval and one LLM span.
The second path deliberately raises an application-owned exception, records an
`error` trace containing the retrieval work completed before the failure, keeps
that original exception visible, and returns exit code 2.

To observe a telemetry failure without losing the completed application result,
point the third path at a known closed local port:

```bash
python -m examples.independent_app collector-offline --collector-url http://127.0.0.1:1
```

That path uses `try_flush()`, reports the delivery error, and returns exit code
1. It does not claim that a trace was stored. `scripts/validate-independent-app.py`
build validation goes further: it installs the current wheel in a clean temporary
environment, copies the example outside the repository, captures and checks the
two delivered payloads, then closes the test Collector and verifies the offline
outcome.

## API Summary

Current implemented API:

```python
trace(name, query=None, metadata=None, collector_url=None)
t.measure()
t.retrieval(query, chunks, name="retrieval", top_k=None, metadata=None, duration_ms=None, timing=None)
t.llm(model, prompt=None, response=None, messages=None, name="llm", provider=None, input_tokens=None, output_tokens=None, latency_ms=None, metadata=None, timing=None)
t.tool(name, input_summary=None, output_summary=None, *, status="ok", error=None, metadata=None, duration_ms=None, timing=None)
t.log_task_result(result, accepted)
t.flush(collector_url=None, timeout=5.0)
t.try_flush(collector_url=None, timeout=5.0)

normalize_chunk(chunk) / normalize_chunks(chunks)
sledtrace.openai.record_response(t, response, name="openai-response")
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
        with t.measure() as retrieval_timing:
            chunks = my_retriever(user_query)

        t.retrieval(
            query=user_query,
            chunks=chunks,
            name="primary_retrieval",
            top_k=len(chunks),
            metadata={
                "retriever": "my_retriever_v1",
            },
            timing=retrieval_timing,
        )

        with t.measure() as llm_timing:
            prompt, answer = my_answerer(user_query, chunks)

        t.llm(
            model="local-answerer-v1",
            prompt=prompt,
            response=answer,
            name="answer_generation",
            provider="local",
            timing=llm_timing,
        )

    t.flush()
    return answer
```

## Span Timing Contract

The recording calls run after your retriever or model has returned, so they cannot infer how long that earlier work took. Use `t.measure()` around the actual operation:

```python
with t.measure() as retrieval_timing:
    chunks = my_retriever(user_query)

t.retrieval(
    query=user_query,
    chunks=chunks,
    timing=retrieval_timing,
)
```

The timer uses a monotonic clock for elapsed time and UTC timestamps for the actual operation boundaries. Fractional milliseconds are truncated to the integer wire format; a measured sub-millisecond operation remains a real `0ms`.

For applications that already measure latency, pass an explicit non-negative integer instead:

```python
t.retrieval(query=user_query, chunks=chunks, duration_ms=retrieval_ms)
t.llm(model=model, response=answer, latency_ms=llm_ms)
```

Do not combine `timing` with `duration_ms` or `latency_ms` on the same span. Duration-only recording knows the elapsed time but not the original UTC boundaries, so `ended_at` remains `null`. A post-hoc call with neither form remains supported, but its `duration_ms` and `ended_at` are `null`; the Dashboard labels it **Not measured** instead of reconstructing timing from the later recording timestamps.

With the local Collector and Dashboard running, generate one measured and one deliberately unmeasured trace for visual verification:

```bash
cd sdk/python
python -m examples.timing_demo
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
- accepts a completed `timing` measurement or an explicit `duration_ms`

## Recommended Chunk Shape

The SDK accepts a list of chunk dictionaries.

Example:

```python
chunks = [
    {
        "id": "chunk_refund_current",
        "text": "Customers may request a refund within 30 days of purchase.",
        "score": 0.93,
        "score_type": "similarity",
        "score_direction": "higher_is_better",
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
- `score_type`
- `score_direction`
- `rank`
- `source`
- `document_id`
- `metadata`

Current SDK chunk behavior:

- retrieval chunks are shallow-copied before normalization
- if `rank` is missing, SDK auto-fills it using 1-based list position
- if `metadata` is missing or `None`, SDK auto-fills it as `{}`
- the SDK does not currently hard-validate fields like `text`, `score`, or `source`

Sparse chunks may still ingest, but diagnostics are better when `text`, `score`, `score_type`, `score_direction`, `source`, `document_id`, `rank`, and `metadata` are present.

### Retrieval score semantics

The legacy/canonical `score` field remains higher-is-better when no annotations
are present. For native retriever outputs, prefer `normalize_chunk(...)` or
`normalize_chunks(...)` so the metric meaning is retained:

- `score`, `similarity`, `similarity_score`, `relevance_score`, and
  `rerank_score` are higher-is-better
- `distance` is lower-is-better
- the second value in an unannotated `(document, value)` tuple is direction-unknown
- unscored chunks remain unscored

Distance and unknown values are preserved for display but do not participate in
the higher-is-better `low_retrieval_score` threshold or score-based diagnostic
ordering. SledTrace does not apply a universal `1 - distance` conversion because
distance scales and ranges vary by retriever.

For a custom metric, declare the mapping explicitly:

```python
chunk = normalize_chunk(
    raw_result,
    text="passage",
    score="metric_value",
    score_type="euclidean_distance",
    score_direction="lower_is_better",
)
```

Valid directions are `higher_is_better`, `lower_is_better`, and `unknown`.
Existing explicit `score=` mappings default to higher-is-better for compatibility.

## LLM Span Examples

Use `t.llm(...)` to record one LLM step.

Current behavior:

- records a span with type `llm`
- supports both `prompt` and `messages`
- if `response` is provided, it becomes the trace final answer
- `provider`, `input_tokens`, `output_tokens`, `total_tokens`, and `latency_ms` are stored in span metadata
- a completed `timing` measurement records the actual operation boundaries and duration

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

## Tool Spans and Task Results

A synchronous, caller-instrumented `tool` span and an explicit task result are
available since 0.7.1. From a source checkout, run the deterministic example
without a paid model:

```bash
cd sdk/python
python -m examples.agent_tool_demo success
python -m examples.agent_tool_demo business-failure
python -m examples.agent_tool_demo tool-recovery
```

Add `--flush` when a local Collector is running. The example uses one tool layer
and simulated LLM outputs solely to check integration; it is not proof of value
in a real external agent. For your own synchronous workflow, record safe input
and output summaries, and keep the final task result separate from intermediate
LLM responses:

```python
with trace("policy-review", metadata={
    "task_id": "case-1", "run_id": "run-1",
    "variant": "baseline", "app_version": "my-app-1",
}) as t:
    with t.measure() as timing:
        found = lookup_policy("refund")
    t.tool("policy_lookup", input_summary="refund key",
           output_summary="one match" if found else "no match", timing=timing)
    t.llm(model="my-model", response="draft", input_tokens=10)
    t.log_task_result("review accepted", accepted=True)
```

`t.tool(...)` records only what the application supplies and returns a span ID.
Use `status="error", error="safe summary"` for a failed tool or LLM attempt;
the error is per step and does not automatically fail a recovered task.
`log_task_result(result, accepted=...)` sets trace-level `task_result`,
`accepted`, and the compatibility `answer` field; `accepted=False` marks the
task trace as an error. No agent/LLM is run by the SDK, no provider usage is
captured automatically, and sensitive arguments or secrets should not be put
in summaries.

## OpenAI Responses Usage

Version 0.7.1 adds `sledtrace.openai.record_response` for one completed,
non-streaming OpenAI Python SDK Responses result. Your application makes the provider call;
the helper reads `response.model` and `response.usage` after the call and
records an LLM span without storing prompts, output text, IDs, or credentials:

```python
from sledtrace import trace
from sledtrace.openai import record_response

# response = your_openai_client.responses.create(...)
with trace("my-task") as t:
    record_response(t, response)
    # t.flush() when your local Collector is running
```

The OpenAI SDK is optional and not imported by SledTrace. Missing usage remains
unknown; cached input and reasoning output are included in their parent counts,
not added again. The Dashboard currently estimates Standard **text-token-only**
USD cost for `gpt-4.1-mini` and `gpt-4o-mini` (including their documented
snapshot IDs) using an official rate snapshot checked 2026-09-24. It leaves
other models, missing cache counts, nonzero cache writes, and conflicted usage
unpriced. This estimate is not a provider bill and excludes tools, alternate
tiers, regional uplifts and other charges. Later model/rate overrides can be
provided by a rate-card input in the Dashboard calculation; there is no user
settings UI yet.

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

`flush()` is intentionally strict. JSON serialization failures, timeouts, HTTP
errors, and connection failures raise. This preserves the historical contract
for tests and applications that require confirmed trace delivery.

For applications where observability must not replace business behavior, choose
`try_flush()` explicitly:

```python
delivery = t.try_flush()

if not delivery.ok:
    app_logger.warning("SledTrace delivery failed: %r", delivery.error)
```

It returns a `TraceFlushResult`:

- `ok=True`, `response=<collector response>`, `error=None` on success
- `ok=False`, `response=None`, `error=<original exception>` on an ordinary failure

The failure is not logged automatically; inspect or log `result.error` according
to your application's policy. A timeout means success was not confirmed—it does
not prove that the Collector failed to persist the request.

`try_flush()` makes one synchronous attempt. It adds no retry, queue, disk
buffer, background worker, or automatic flush. It deliberately does not catch
`KeyboardInterrupt`, `SystemExit`, or other `BaseException` subclasses.

Why this matters:

- `ended_at` and `duration_ms` are finalized when the trace context exits
- flushing inside the `with` block can send incomplete lifecycle fields
- `flush()` accepts optional `collector_url` and `timeout` arguments
- `try_flush()` accepts the same arguments and returns an observable result

## Error Trace Behavior

If an exception escapes the `with trace(...)` block:

- trace status becomes `error`
- error details are added under trace metadata
- the exception is not suppressed

That means the SDK records the failure state, but your application still receives the exception unless you catch it yourself.

If you also attempt trace delivery while an application exception is already
propagating, use `try_flush()` in `finally`; strict `flush()` can replace that
exception with a delivery error:

```python
delivery = None
t = trace(name="my-trace", query=query)
try:
    with t:
        answer = run_pipeline(query)
finally:
    delivery = t.try_flush()
```

The original application exception continues to propagate, and any delivery
failure remains available in `delivery.error`.

## Common Mistakes

### Collector not running

If the collector is not listening on `http://localhost:4319`, strict `flush()`
raises. `try_flush()` returns the same failure in `result.error`.

### Calling `flush()` inside the `with` block

This can send a trace before `ended_at` and `duration_ms` are finalized.

### Forgetting to convert retriever results into dict chunks

The SDK expects chunk dictionaries, not arbitrary retriever-native objects.

### Missing chunk `text`, score semantics, or `source`

The SDK may still ingest sparse chunks, but dashboard readability and warning quality will be worse.

### Using `local_rag_demo` as the integration point

Do not modify `local_rag_demo` for real usage. Instrument your own application code instead.

### Installing the SDK into the wrong virtualenv

If your app runs in one virtual environment and `SledTrace` was installed into another, imports will fail.

### `sledtrace serve` says the bundled collector is missing

Platform wheels (Windows, macOS, Linux on x86-64 and ARM64) include the
collector and dashboard. On other platforms pip installs the SDK-only wheel;
clone SledTrace and run `sledtrace serve` from inside that checkout, or use
Docker Compose.

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



