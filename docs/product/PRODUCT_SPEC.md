# SledTrace Product Spec

Historical v0.1 product specification and implementation snapshot. Its old
next-step recommendations are not the active roadmap. See
[Road to v1.0](ROAD_TO_V1_0.md) for the 2026-09-15 proposed direction and
[AI_HANDOFF](../ai-context/AI_HANDOFF.md) for currently implemented behavior.

## Product Name

SledTrace

## Tagline

Local-first visual debugger for RAG pipelines.

## Problem

RAG systems are hard to debug.

When a RAG application gives an incorrect answer, developers often cannot easily tell whether the failure came from retrieval, chunking, stale context, conflicting documents, or the LLM generation step.

Most developers debug RAG pipelines with print statements.

SledTrace aims to make the pipeline visible.

## Target Users

### Primary Users

- Developers building RAG applications
- Indie hackers building AI tools
- Backend engineers adding LLM/RAG features
- AI engineers debugging retrieval pipelines

### Secondary Users

- Teams evaluating prompt and retrieval changes
- Developers building local-first AI apps
- Open-source contributors working on LLM tooling

## Core Use Case

A developer has a RAG pipeline:

1. User asks a question
2. App retrieves top-k chunks
3. App sends chunks to an LLM
4. LLM returns an answer

The answer is wrong.

The developer wants to inspect:

- What query was used
- Which chunks were retrieved
- What scores they had
- Where they came from
- What prompt was sent
- What answer was returned
- Whether the answer seems grounded in the retrieved chunks
- Whether chunks conflict with each other

## MVP User Story

As a developer, I want to add a few lines of Python to my RAG app so that I can inspect the retrieval and LLM generation process in a local UI.

## MVP API Example

```python
from sledtrace import trace

with trace("refund-policy-qa") as t:
    t.retrieval(
        query="What is the refund window?",
        chunks=[
            {
                "id": "chunk_1",
                "text": "Customers may request a refund within 30 days.",
                "score": 0.91,
                "source": "refund_policy_new.md",
                "metadata": {"version": "2026"}
            },
            {
                "id": "chunk_2",
                "text": "Customers may request a refund within 14 days.",
                "score": 0.84,
                "source": "refund_policy_old.md",
                "metadata": {"version": "2024"}
            }
        ]
    )

    t.llm(
        model="gpt-4o-mini",
        prompt="Answer the user question using the retrieved context.",
        response="Customers may request a refund within 14 days.",
        input_tokens=320,
        output_tokens=80,
        latency_ms=900
    )
```

## MVP Features

### 1. Python SDK

The SDK should allow developers to create a trace and record RAG events.

Required methods:

- `trace(name)`
- `t.retrieval(query, chunks)`
- `t.llm(model, prompt, response, input_tokens=None, output_tokens=None, latency_ms=None)`

### 2. Local Collector

Receives trace events from the SDK.

Initial endpoints:

- `POST /api/traces`
- `GET /api/traces`
- `GET /api/traces/{trace_id}`

### 3. Local Storage

Stores traces, spans, chunks, and LLM calls.

SQLite is preferred for local-first MVP.

### 4. Dashboard

The dashboard should have:

- Trace list page
- Trace detail page
- Query section
- Retrieval section
- Chunk cards
- LLM call section
- Final answer section
- Warning section

### 5. Basic Warning Rules

Initial warning rules:

- No retrieved chunks
- Top retrieval score is low
- Retrieved chunks appear to conflict
- Answer may not be grounded in top chunks
- Duplicate or near-duplicate chunks

These can start as simple heuristic rules.

### 6. Demo

Create a refund policy demo with old and new policy documents.

The demo should show a case where:

- One chunk says refund window is 30 days
- Another chunk says refund window is 14 days
- The LLM answer uses the outdated 14-day policy
- SledTrace surfaces a warning

## Non-goals for v0.1

SledTrace v0.1 will not include:

- User authentication
- Team workspace
- Cloud hosting
- Billing
- Multi-tenancy
- Kafka
- Kubernetes
- ClickHouse
- Full prompt management
- Full eval framework
- AI gateway
- Semantic cache
- Multi-agent PR reviewer

## Success Criteria for v0.1

v0.1 is successful if:

- A developer can install and run SledTrace locally.
- A developer can instrument a simple RAG pipeline with a few lines of Python.
- A developer can open the UI and inspect retrieved chunks and LLM output.
- The demo clearly shows how SledTrace helps debug a wrong RAG answer.
- The README makes the project understandable within 60 seconds.

## Implementation Snapshot (2026-06-15)

Current milestone status:

- Warning Engine / Diagnosis Layer MVP is complete.
- The dashboard warning section now renders real persisted warnings (not placeholder-only UI).

Validated local flow:

```text
Python SDK
    -> t.flush()
    -> POST /api/traces
    -> Go Collector (:4319)
    -> SQLite persistence
    -> warning generation + persistence
    -> GET /api/traces/{trace_id}
    -> React dashboard warning cards
```

Implemented warning rules:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- `conflicting_chunks`
- simplified `answer_not_grounded`

Primary warning smoke test:

- `sdk/python/examples/warning_rules_demo.py`
- supports all-rules and single-rule runs
- expected result per case: `warnings_generated: 1`

Next recommended milestone:

- Real Local RAG Demo
- keep schema stable, replace mock chunks with real retrieval output
- do this before LangChain/LlamaIndex adapter work

## Long-term Vision

SledTrace begins as a local-first debugger for RAG pipelines. This keeps the MVP focused and useful.

The broader product direction is local-first observability for AI application harnesses. In this framing, a RAG pipeline is one type of AI harness: it selects context, calls a model, and produces an answer. Future AI harnesses may also include tools, memory, planners, verification steps, permissions, human feedback, and multi-step agent workflows.

SledTrace should preserve a general trace/span foundation so future versions can support additional span types beyond retrieval and LLM calls.

Future harness-observability expansion can include running traces, partial span ingestion, and span types such as agent, tool, and retry, with diagnostics for agent loops, oscillation, retry storms, and no-progress execution. This is future direction only and is not implemented in current SledTrace.

## Product Principle

SledTrace should feel like a developer tool, not an enterprise observability platform.

The v0.1 experience should be:

- Local-first
- Easy to install
- Easy to instrument
- Visual and inspectable
- Useful within the first demo run

The project should avoid premature infrastructure complexity.


