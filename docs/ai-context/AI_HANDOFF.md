# AI Handoff

## Project Name

SledTrace

## One-liner

SledTrace is a local-first visual debugger for RAG pipelines.

## Current Release Target

v0.5.0 — Python SDK Distribution / Packaging Readiness

## Current Project Status

### v0.5.0 Status

**v0.5.0 packaging readiness is complete and validated.**

Completed work includes:

- building the Python SDK as a wheel/sdist via `python -m build`
- verifying clean install from a built artifact in a fresh venv
- keeping the preferred import path `sledtrace` stable
- preserving temporary `raglens` compatibility during migration
- verifying `SLEDTRACE_COLLECTOR_URL` precedence over `RAGLENS_COLLECTOR_URL`
- keeping v0.5 limited to packaging and documentation, without touching the warning engine or collector contracts

Validation commands that passed:

```bash
cd sdk/python
python -m pip install --upgrade pip
python -m pip install build
python -m build

python -m venv .venv-package-test
source .venv-package-test/bin/activate
pip install dist/*.whl
python -c "import sledtrace; print(sledtrace.__version__)"
python -c "from sledtrace import trace; print(trace)"
python -c "import raglens; print('legacy raglens import ok')"
deactivate

pytest

cd collector/go
go test ./... -count=1

cd dashboard/web
npm run build
```

Observed results:

- wheel + sdist produced successfully
- wheel install succeeded in clean venv
- `sledtrace.__version__` prints `0.5.0`
- `from sledtrace import trace` works
- legacy `raglens` compatibility import works
- `pytest` passed with 11 tests
- Go backend tests passed
- dashboard build passed

Next recommended milestone:

- v0.6 Local CLI / `sledtrace serve` planning, or
- v0.5.1 PyPI publishing follow-up if the team chooses to publish later

### v0.4.1 Status

**v0.4.1 Rebrand is complete and compatibility-preserving.**

v0.4.1 implementation focus:

- Rename active branding from RAGLens to SledTrace
- Preserve compatibility for legacy startup and collector environment variables
- Keep APIs, warning logic, and SQLite schema unchanged
- Add migration and release documentation for the rebrand

Historical context:

- v0.4.0 was originally released under the RAGLens name

### v0.4.0 Status

**v0.4.0 Local Release / Install & First-Run Experience is complete and smoke-tested.**

v0.4.0 implementation focus:

- Docker Compose stack for collector + dashboard
- first-run quickstart consolidation
- health and reset guidance
- release-note and smoke-doc alignment

Validation state:

- implementation completed
- required validation commands passed on 2026-07-15

### v0.1 Status

**v0.1 Local RAG Debugger MVP is complete and smoke-tested.**

Completed v0.1 foundation:

- Python SDK tracing foundation
- Go collector ingestion APIs
- SQLite trace/span/warning persistence
- React dashboard MVP
- Warning Engine / Diagnosis Layer MVP
- Real Local RAG Demo
- Demo packaging / developer experience

### v0.2 Status

**v0.2 Developer Integration / Local SDK Onboarding is complete and smoke-tested.**

Completed v0.2 work:

- `docs/product/USER_ONBOARDING.md`
- `docs/integrations/PYTHON_SDK_GUIDE.md`
- `sdk/python/examples/custom_pipeline_demo.py`
- `scripts/start-sledtrace.py`
- `README.md` two-path quickstart
- root README documentation map
- SDK packaging hygiene:
  - `sdk/python` version `0.2.0`
  - local SDK README
  - local editable install path

### v0.3 Status

**v0.3 RAG Quality Analysis / Diagnostic Intelligence core is complete and smoke-tested.**

v0.3 upgraded SledTrace from simple warning flags into evidence-backed diagnostic insights.

Completed v0.3 core work:

- Warning Schema v2 infrastructure
- evidence-backed warning payloads
- deterministic diagnostic signals
- diagnostic objects
- evidence items
- dashboard warning detail rendering
- numeric value diff block
- recommended action label
- responsive warning detail layout polish
- deterministic diagnostic demo cases

Implemented or upgraded v0.3 warning rules:

- `weak_query_chunk_overlap`
- `numeric_mismatch`
- `answer_not_grounded` with evidence-backed v2 details
- `conflicting_chunks` with evidence-backed v2 details

Existing warning rules retained:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`

### v0.3 Hardening Status

**v0.3.5 diagnostic-quality hardening is complete and smoke-tested.**

Added backend tests and hardening coverage for:

- warning engine unit tests
- SQLite Warning Schema v2 round-trip persistence
- legacy warning table migration for v2 columns
- API handler coverage for v0.3 warning generation
- API trace detail response coverage for v2 warning fields
- numeric range extraction behavior (`5-10` and `5 to 10` forms)
- relevance-aware conflicting chunk selection and query gating
- deterministic numeric-expression topic gating for conflicts

Added reference integration validation assets:

- `sdk/python/examples/reference_rag_app/run.py`
- `sdk/python/examples/reference_rag_app/docs/*.md`
- mixed retrieval raw-shape normalization flow through `normalize_chunks()`

Current backend test coverage verifies:

- v0.3 diagnostic rules generate expected warning types
- v2 warning fields persist through SQLite
- legacy warning tables can be migrated with v2 columns
- `POST /api/traces` generates v0.3 warnings
- `GET /api/traces/{trace_id}` returns dashboard-consumable v2 warning fields
- wrong policy-window mismatch still fires (`45 days` vs retrieved `30 days`)
- processing-range mismatch still fires (`2 business days` vs retrieved `5-10 business days`)
- elapsed-time answer phrasing remains protected from false-positive numeric mismatch

## Current Implemented Flow

```text
Python SDK
  ->
trace()
  ->
retrieval span + LLM span
  ->
t.flush()
  ->
POST /api/traces
  ->
Go Collector (:4319)
  ->
Warning Engine
  ->
SQLite
  ->
GET /api/traces/{trace_id}
  ->
React Dashboard
```

## Exact Commands That Passed

v0.4.0 validation commands that passed:

```bash
cd collector/go
go test ./... -count=1

cd dashboard/web
npm run build

cd ..\..
docker compose up --build
curl http://localhost:4319/health

cd sdk/python
pip install -e .
python -m examples.reference_rag_app.run all
```

Additional v0.4 runtime checks that passed:

```bash
curl http://localhost:5173
docker compose down
docker compose down -v
```

Legacy validated v0.2 / v0.3 / v0.3.5 runtime commands:

```bash
python scripts/start-sledtrace.py

cd sdk/python
python -m examples.custom_pipeline_demo
python -m examples.local_rag_demo.run_demo trace-all
python -m examples.diagnostic_quality_demo all
python -m examples.real_llm_rag_demo all
python -m examples.reference_rag_app.run all
python -m examples.reference_rag_app.run processing-range
python -m examples.reference_rag_app.run wrong-processing-range
```

Validated backend tests:

```bash
cd collector/go
go test ./... -count=1
```

Validated dashboard build:

```bash
cd dashboard/web
npm run build
```

## Verified Dashboard Results

- dashboard showed custom-rag-pipeline
- dashboard showed built-in local RAG demo traces
- dashboard showed warning-focused diagnostic demo traces
- warning detail cards showed evidence-backed sections
- numeric mismatch showed compared value diff block
- recommended action label appeared in warning cards
- reference integration traces were visible and inspectable (`reference-rag-app-*`)

## Current Implemented Span Types

Only these span types are implemented today:

- retrieval
- llm

Do not claim these as implemented yet:

- tool spans
- memory spans
- verification spans
- human feedback spans
- agent spans
- retry spans
- running traces
- partial span ingestion

## Current Warning Rules

Implemented warning rules:

- no_retrieved_chunks
- low_retrieval_score
- duplicate_chunks
- weak_query_chunk_overlap
- numeric_mismatch
- conflicting_chunks
- answer_not_grounded

Important current state:

- answer_not_grounded is now evidence-backed v2, but still deterministic and heuristic-based.
- conflicting_chunks is now evidence-backed v2 for numeric conflicts in similar local context.
- numeric_mismatch detects answer numeric values that conflict with retrieved chunk values.
- weak_query_chunk_overlap detects low lexical overlap between the query and top retrieved chunks.
- SledTrace still does not use LLM-as-judge by default.
- conflicting chunk selection is relevance-aware and topic-gated in v0.3.5.
- numeric extraction supports natural-language ranges (for example `5 to 10 business days`).

## Current v0.3 Diagnostic Demo Cases

Current demo file:

- sdk/python/examples/diagnostic_quality_demo.py

Current cases:

- numeric-mismatch
- weak-overlap
- unsupported-claim
- conflicting-chunks
- all

Expected run command:

```bash
cd sdk/python
python -m examples.diagnostic_quality_demo all
```

## Files Added or Updated Recently

Core v0.3 implementation files:

- collector/go/internal/warnings/engine.go
- collector/go/internal/warnings/engine_test.go
- collector/go/internal/storage/sqlite.go
- collector/go/internal/models/models.go
- dashboard/web/src/pages/TraceDetailPage.tsx
- dashboard/web/src/style.css
- sdk/python/examples/diagnostic_quality_demo.py
- sdk/python/examples/real_llm_rag_demo.py
- sdk/python/examples/reference_rag_app/__init__.py
- sdk/python/examples/reference_rag_app/run.py
- sdk/python/examples/reference_rag_app/docs/refund_policy_current.md
- sdk/python/examples/reference_rag_app/docs/refund_policy_legacy.md
- sdk/python/examples/reference_rag_app/docs/returns_process.md
- sdk/python/examples/reference_rag_app/docs/shipping_policy.md
- sdk/python/examples/reference_rag_app/docs/warranty_policy.md
- sdk/python/examples/reference_rag_app/docs/subscription_policy.md
- sdk/python/examples/reference_rag_app/docs/damaged_items_policy.md
- sdk/python/examples/reference_rag_app/docs/digital_goods_policy.md

Backend test files added:

- collector/go/internal/warnings/engine_test.go
- collector/go/internal/storage/sqlite_test.go
- collector/go/internal/api/server_test.go

v0.3 documentation files:

- docs/product/V0_3_DIAGNOSTIC_INTELLIGENCE.md
- docs/ai-context/ROADMAP.md
- docs/ai-context/CURRENT_TASK.md
- docs/ai-context/DEVLOG.md
- docs/ai-context/AI_HANDOFF.md

v0.2 onboarding artifacts still relevant:

- docs/product/USER_ONBOARDING.md
- docs/integrations/PYTHON_SDK_GUIDE.md
- sdk/python/examples/custom_pipeline_demo.py
- scripts/start-sledtrace.py
- README.md
- sdk/python/pyproject.toml
- sdk/python/README.md

## Current Limitations

Current scope limits:

- only retrieval and llm spans are implemented
- onboarding path is local-first and repo-based
- editable install from local checkout is the supported SDK path today
- no packaged CLI yet
- no PyPI publishing yet
- no LangChain adapter yet
- no LlamaIndex adapter yet
- no cloud sync, auth, hosted collector, or hosted features
- no full LLM-as-judge grounding evaluator
- no running-trace lifecycle handling for multi-step agent harnesses
- no partial span ingestion
- no retry spans
- no diagnostics for agent loops, oscillation, retry storms, or no-progress execution

## Current Positioning

SledTrace is:

- a local-first visual debugger for RAG pipelines
- a local trace and debugging layer for existing RAG apps
- useful both with the built-in demo and with user-owned Python RAG pipelines instrumented through the SDK
- currently strongest at explaining RAG failures through deterministic evidence-backed diagnostics

SledTrace is not:

- a chatbot framework
- a vector database
- a training framework
- a hosted AI platform
- a replacement for the user's RAG app
- a general-purpose eval platform
- a LangChain/LlamaIndex integration layer yet
- an AgentOps platform yet

## Recommended Next Milestone

Recommended next step: v0.4 -Packaging and External Developer Experience

The v0.3.5 hardening scope is complete.

Recommended version naming:

- v0.3: Diagnostic Intelligence core
- v0.3.5: deterministic warning-quality hardening + reference integration validation
- v0.4: packaging / distribution / external developer experience

Recommended v0.4 goal:

Make local-first SledTrace easier to adopt outside this repository while preserving deterministic diagnostics and current trace contracts.

Real LLM demo status:

- `sdk/python/examples/real_llm_rag_demo.py` already exists and has been smoke-tested.
- It should remain a validation asset, not a next-milestone deliverable.

Why this is next:

- v0.3.5 delivered deterministic warning-quality hardening and realistic integration validation.
- the next priority is reducing first-run friction for external developers.
- packaging and startup ergonomics now provide higher leverage than adding another demo.

## Suggested v0.4 Scope

In scope:

- Docker Compose local stack for collector + dashboard
- `.env.example` for local configuration defaults
- startup health checks and clearer startup failure guidance
- clean local database reset/sample-data guidance
- README quickstart consolidation and first-run clarity
- release-clean docs pass for external developer onboarding
- optional local CLI wrapper investigation (without forcing packaging decisions)

Existing validation assets:

- `sdk/python/examples/real_llm_rag_demo.py`
- `sdk/python/examples/reference_rag_app/run.py`
- `sdk/python/examples/diagnostic_quality_demo.py`

Out of scope for v0.4:

- LangChain adapter
- LlamaIndex adapter
- PyPI
- hosted collector
- auth
- cloud sync
- paid SaaS features
- agent spans
- tool spans
- memory spans
- LLM-as-judge default evaluator

Unless explicitly selected:

- framework adapters (LangChain/LlamaIndex)
- PyPI publishing

## Important Guardrails

- Continue local-first.
- Continue deterministic-first for rule logic.
- Do not add framework adapters yet.
- Do not start Docker, CLI, or PyPI until a later packaging milestone.
- Do not add agent/tool/memory spans in the current milestone.
- Do not make LLM-as-judge the default diagnostic path.
- The real LLM demo should test SledTrace as an observer of a realistic RAG flow, not turn SledTrace into a RAG framework.

## Future Agent Harness Observability Direction

Future possible TraceForge direction, not implemented in current SledTrace:

- running traces for multi-step agent/harness executions
- partial span ingestion for long-running or interrupted runs
- additional span types such as agent, tool, and retry
- diagnostics for agent loops
- diagnostics for oscillation between states/actions
- diagnostics for retry storms
- diagnostics for no-progress execution

Important scope note:

- none of the above is implemented in current SledTrace
- this direction is future-only and should not be claimed as current capability


