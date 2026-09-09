
# AGENTS.md

## Project

SledTrace is an open-source, local-first observability and debugging tool for RAG pipelines.

Former project name: RAGLens.

Current stable project direction is SledTrace-first. Legacy RAGLens compatibility may remain temporarily where explicitly documented.

Current released version: **v0.6.0 — Local CLI / Startup UX**.

Current planned milestone: **v0.7.0 — External Developer Readiness**.

The Python package is buildable as a wheel/sdist but is not published to PyPI yet. Do not document `pip install sledtrace` as an available installation path until publication has actually been completed and verified.

## Before Doing Meaningful Work

Always read these files first:

1. `docs/ai-context/AI_HANDOFF.md`
2. `docs/ai-context/CURRENT_TASK.md`
3. `docs/ai-context/ROADMAP.md`

Read `docs/ai-context/DECISIONS.md` before making architecture decisions.

Use the repository and these documents as the source of truth.
Do not assume old milestone information from this file overrides the current AI context documents.

## Current Architecture

```text
Python SDK
  -> trace()
  -> retrieval + llm spans
  -> flush()
  -> Go collector
  -> deterministic Warning Engine
  -> SQLite
  -> React/TypeScript dashboard
```

Current implemented span types:

- retrieval
- llm

Current major components:

- Python SDK
- Go collector
- SQLite local persistence
- deterministic diagnostic engine
- React + TypeScript dashboard
- Docker Compose local stack
- reference RAG application
- buildable Python wheel/sdist
- package-installed `sledtrace` CLI with source-checkout-based `serve`

## Engineering Philosophy

SledTrace is local-first developer infrastructure.

Prefer:

- simple implementations
- explicit behavior
- deterministic diagnostics where practical
- small focused changes
- compatibility with existing RAG applications
- reproducible tests
- easy local installation
- clear developer UX

Avoid speculative abstractions.

Do not turn SledTrace into a generic chatbot.

Do not turn SledTrace into a large hosted LLMOps platform unless the roadmap explicitly changes.

## Scope Guardrails

Do not add any of the following unless the current milestone explicitly requires it:

- hosted cloud infrastructure
- authentication or billing
- multi-tenancy
- Kafka
- Kubernetes
- ClickHouse
- new span types
- LangChain/LlamaIndex adapters
- LLM-as-judge
- unrelated warning rules
- breaking SDK/API/schema changes

Do not log or attempt to collect private chain-of-thought.

Do not store secrets in traces.

## Compatibility

Preferred public project/package naming:

- SledTrace
- `sledtrace`
- `SLEDTRACE_COLLECTOR_URL`

Legacy RAGLens compatibility may exist temporarily:

- `raglens`
- `RAGLENS_COLLECTOR_URL`

Do not remove legacy compatibility without checking the current milestone and compatibility tests.

## Validation

For Python SDK changes:

```
cd sdk/python
pytest -q
python -m build
python scripts/validate-wheel.py
```

For collector changes:

```
cd collector/go
go test ./... -count=1
```

For dashboard changes:

```
cd dashboard/web
npm run build
```

For dashboard-visible changes, a successful build is necessary but not sufficient. When practical:

1. start the real local Collector and Dashboard
2. generate deterministic reference traces
3. open the Dashboard and inspect the affected flows
4. provide user-visible screenshots or an interactive browser view
5. distinguish automated-test evidence from visual acceptance evidence

Screenshot policy:

- provide conversation screenshots for dashboard-facing validation checkpoints
- update README screenshots only when the visible product or onboarding flow materially changes
- refresh release-quality screenshots before a release that changes the Dashboard
- keep screenshots deterministic and free of secrets, private paths, or personal data

For full local smoke validation when relevant:

```
docker compose up --build
curl http://localhost:4319/health

cd sdk/python
python -m examples.reference_rag_app.run all
```

Do not claim a milestone is complete unless its required validation has actually passed.

## Documentation Discipline

After meaningful completed work:

- update `docs/ai-context/DEVLOG.md`
- update `docs/ai-context/AI_HANDOFF.md`
- update `docs/ai-context/CURRENT_TASK.md` when milestone state changes
- update `docs/ai-context/ROADMAP.md` when roadmap state changes
- update `docs/ai-context/DECISIONS.md` when making a meaningful architecture decision
- update release notes, root README status, and package README status when publication state changes

Keep documentation aligned with actual tested repository behavior.

## Working Style

Before coding:

1. inspect the relevant implementation
2. understand the current contract
3. identify the smallest safe change
4. state important assumptions

After coding:

1. run relevant tests
2. inspect failures rather than bypassing them
3. summarize files changed
4. report exact validation results
5. call out remaining limitations honestly

Do not mark work complete merely because code was written.


