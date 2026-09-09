# User Onboarding: Integrating SledTrace Into Your Existing RAG App

SledTrace is a local-first trace and debugging layer for RAG pipelines.

This guide explains how to instrument your own pipeline using the Python SDK.
Do not modify the built-in `local_rag_demo` for real usage. Use it only as a reference and smoke test.

## What SledTrace Is

SledTrace helps you debug why a RAG answer was good or bad by showing:

- retrieval spans and retrieved chunks
- LLM spans (prompt/response)
- warning signals generated from trace data

SledTrace is built for local development loops: run your app locally, send traces to the local collector, inspect them in the local dashboard.

## What SledTrace Is Not

SledTrace is not:

- a chatbot framework
- a vector database
- a model training framework
- a hosted AI platform
- a replacement for your RAG application

The current release also does not include:

- LangChain integration
- LlamaIndex integration
- real LLM provider integrations inside SledTrace itself
- agent/tool/memory span tracing
- cloud sync, auth, or hosted features

## Who This Is For

This guide is for developers who already have a RAG pipeline and want observability without rewriting their stack.

You should already have your own:

- document ingestion and indexing
- retrieval call(s)
- LLM call(s)
- answer assembly

## Two Ways to Use SledTrace

SledTrace has two practical local-first entry points.

### 1. Try the built-in demo

Use this path when you want to verify that SledTrace itself works on your machine.

1. Clone the SledTrace repo.
2. Start the Collector and Dashboard from that repo. Docker Compose is the recommended path:

```bash
docker compose up --build
```

For the non-Docker fallback, install Dashboard dependencies first:

```bash
cd dashboard/web
npm ci
cd ../..
```

```bash
python scripts/start-sledtrace.py
```

3. Run the built-in local demo or smoke test.
4. Open the local dashboard and inspect the generated traces.

Use this only to verify the SledTrace stack. Do not modify `local_rag_demo` for real usage.

### 2. Integrate SledTrace into your own RAG app

Use this path when you want to instrument an existing application.

1. Clone the SledTrace repo somewhere on your machine.
2. Start the collector and dashboard from that repo.

```bash
python scripts/start-sledtrace.py
```

3. In your own app's virtual environment, install the SDK from PyPI:

```bash
python -m pip install sledtrace
```

4. Import `trace` from `sledtrace`.
5. Wrap your own RAG request path.
6. Log retrieval and LLM spans.
7. Call `flush()` after the trace context exits.
8. Inspect traces in the local dashboard.

For development against local SDK changes, use `python -m pip install -e /path/to/sledtrace/sdk/python` instead.

## How SledTrace Fits Into an Existing RAG App

SledTrace wraps what you already do.

1. Start a trace at request entry.
2. Log retrieval output as a retrieval span.
3. Log your LLM call as an LLM span.
4. Exit the trace context.
5. Flush the trace to the local collector.

Your retrieval system, prompts, model client, and business logic remain in your app.

## Local Development Loop

Use this loop while iterating on quality:

1. Run collector + dashboard locally.
2. Run your app locally with SDK instrumentation enabled.
3. Trigger real user-like queries in your app.
4. Open dashboard traces and inspect chunks, prompts, responses, and warnings.
5. Adjust retriever/prompting logic and repeat.

## Start Local Services

Recommended startup from the repo root:

```bash
docker compose up --build
```

Non-Docker fallback prerequisites are Python 3.9+, Go, Node.js 22, and npm. Install Dashboard dependencies once before starting:

```bash
cd dashboard/web
npm ci
cd ../..
```

```bash
python scripts/start-sledtrace.py
```

This repo-local helper starts the collector from `collector/go` and the dashboard from `dashboard/web`.

If you need manual fallback steps, start the two local services separately:

### Collector

```bash
cd collector/go
go run ./cmd/sledtrace-collector
```

Health check:

```bash
curl http://localhost:4319/health
```

### Dashboard

```bash
cd dashboard/web
npm ci
npm run dev
```

Keep collector at `http://localhost:4319` for local SDK flushes.

## Use the Python SDK

Install the released SDK from PyPI:

```bash
python -m pip install sledtrace
```

Use an editable install when contributing inside a checkout.

If you are working inside the SledTrace repo:

```bash
cd sdk/python
python -m pip install -e .
```

If you are developing against a local SledTrace checkout from another project:

```bash
python -m pip install -e /path/to/sledtrace/sdk/python
```

Basic import:

```python
from sledtrace import trace
```

## Wrap Your Pipeline With `trace()`

Use one trace per user request (or per top-level pipeline call).

```python
from sledtrace import trace


def answer_question(user_query: str) -> str:
    with trace(
        name="my-rag-request",
        query=user_query,
        metadata={
            "app": "my-rag-app",
            "environment": "local",
            "retriever": "my_retriever_v2",
        },
    ) as t:
        retrieved = my_retriever.search(user_query, top_k=4)

        t.retrieval(
            name="primary_retrieval",
            query=user_query,
            chunks=to_SledTrace_chunks(retrieved),
            top_k=4,
            metadata={
                "retriever": "my_retriever_v2",
                "low_score_threshold": 0.5,
            },
        )

        prompt = build_prompt(user_query, retrieved)

        llm_result = my_llm.generate(prompt)

        t.llm(
            name="answer_generation",
            model="my-model-name",
            prompt=prompt,
            response=llm_result.text,
            provider="my-provider",
            input_tokens=llm_result.input_tokens,
            output_tokens=llm_result.output_tokens,
            latency_ms=llm_result.latency_ms,
        )

    # Flush after exiting the with-block.
    t.flush()

    return llm_result.text
```

## Log Retrieval Spans

Use `t.retrieval(...)` for your retrieval step:

- `query`: the retriever query text
- `chunks`: list of retrieved chunk objects
- `top_k`: optional retrieval request size
- `metadata`: optional retriever metadata

`chunks` should represent what your retriever actually returned, not transformed synthetic data.

In this example, `to_SledTrace_chunks(...)` is an application-owned adapter function, not necessarily an SDK helper. It converts your retriever-native result objects into SledTrace chunk dictionaries.

## Log LLM Spans

Use `t.llm(...)` for the generation step:

- `model`: model identifier
- `prompt`: text-style model input
- `messages`: chat-style model input
- `response`: model output text
- `provider`, `input_tokens`, `output_tokens`, `latency_ms`: optional top-level fields
- `metadata`: optional additional details

If your app has both prompt-style and chat-style representations, log the one that best matches your LLM call path.

Current implemented span types are:

- `retrieval`
- `llm`

## Why `flush()` Should Be Called After `with trace(...)`

Call `flush()` after the `with` block exits.

Reason:

- the trace context finalizes `ended_at` and `duration_ms` when exiting
- if an exception escapes the `with` block, trace status becomes `error` and error details are added under trace metadata
- flushing too early can send incomplete lifecycle fields

Recommended pattern:

```python
with trace(name="my-trace", query=query) as t:
    ...

t.flush()
```

## Retrieved Chunk Object Shape

Use JSON-like dict objects for each chunk.

Example:

```python
{
    "id": "chunk_42",
    "text": "Customers may request a refund within 30 days.",
    "score": 0.91,
    "rank": 1,
    "source": "refund_policy_new.md",
    "document_id": "refund_policy_new",
    "metadata": {
        "section": "refund_window",
        "retriever": "my_retriever_v2"
    }
}
```

### Minimum Useful vs Recommended Fields

Technically, chunks can be sparse, but useful analysis depends on fields:

- Minimum useful chunk:
    - `text`
- Recommended chunk:
    - `id`, `text`, `score`, `rank`, `source`, `document_id`, `metadata`

Notes:

- Retrieval chunks are shallow-copied before SDK normalization.
- If `rank` is missing, SDK auto-fills it using 1-based list position.
- If `metadata` is missing or `None`, SDK auto-fills it as `{}`.
- The SDK does not currently hard-validate fields like `text`, `score`, or `source`.
- Missing optional fields usually do not block ingestion, but they reduce dashboard clarity and warning quality.
- In particular, missing `score` weakens `low_retrieval_score` diagnostics.

## What SledTrace Analyzes Today

Current warning analysis includes:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- `conflicting_chunks`
- `answer_not_grounded` (current deterministic MVP behavior)

These rules are intentionally simple and local-first.

## What SledTrace Does Not Analyze Yet

SledTrace does not yet perform:

- semantic retrieval relevance evaluation
- claim extraction + entailment checking
- comprehensive factuality scoring
- generalized hallucination detection
- tool span or memory span diagnostics
- agent-level workflow tracing

## `local_rag_demo` vs Real User Integration

`local_rag_demo` is a built-in deterministic demo to validate the stack.

- Use it to verify local setup and see expected warning behavior.
- Do not modify it for production or real integration.

For real usage:

- instrument your own retriever and LLM calls with the SDK
- emit traces from your own app request path
- keep your existing architecture and business logic

## Practical Integration Checklist

1. Start local collector and dashboard.
2. Add `from sledtrace import trace` to your app.
3. Wrap one top-level request with `with trace(...) as t:`.
4. Log `t.retrieval(...)` with real retrieved chunks.
5. Log `t.llm(...)` with prompt/response and model details.
6. Call `t.flush()` after the `with` block.
7. Inspect traces in dashboard and iterate.



