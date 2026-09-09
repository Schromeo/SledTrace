# AI Handoff

## Project Name

SledTrace

## One-liner

SledTrace is a local-first visual debugger for RAG pipelines.

## Current Released Version

v0.6.0 — Local CLI / Startup UX

Released on 2026-09-08:

- release commit: `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e`
- annotated tag: `v0.6.0`
- GitHub Release: https://github.com/Schromeo/SledTrace/releases/tag/v0.6.0

## Current Planned Milestone

v0.7.0 — External Developer Readiness

Status: implementation in progress; cross-stack CI and the published `0.7.0rc1` TestPyPI candidate validation are complete and green.

## Current Project Status

### v0.6.0 Status

**v0.6.0 implementation, validation, repository hygiene, tag publication, push, and GitHub Release are complete.**

Completed work includes:

- installable `sledtrace` console script via package metadata
- `sledtrace --help`, `sledtrace serve --help`, and `sledtrace version` working in editable and clean wheel installs
- package and Dashboard versions aligned to `0.6.0`
- source-checkout detection by walking upward from the current working directory
- `sledtrace serve` delegating to the repo-local startup script inside a valid checkout
- clear non-zero failure and actionable guidance when `serve` runs outside a checkout
- explicit v0.6 boundary: no standalone serving runtime is bundled in the wheel
- continued compatibility with the existing local collector + dashboard startup flow
- no contract changes to trace payloads, warnings, storage schema, or dashboard API
- release commit `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e`
- annotated `v0.6.0` tag and published GitHub Release
- tracked Python bytecode/cache artifacts removed from version control

Validation commands that passed:

```bash
cd sdk/python
python -m pip install -e .
sledtrace --help
sledtrace serve --help
sledtrace version
pytest -q
python -m build
python scripts/validate-wheel.py

cd ../../collector/go
go test ./... -count=1

cd ../../dashboard/web
npm.cmd run build
```

Observed results:

- editable install succeeded
- `sledtrace --help` and `sledtrace serve --help` displayed the documented CLI surface and source-checkout limitation
- `sledtrace version` printed `0.6.0`
- Python tests passed: 17 tests; warnings were the expected legacy-import deprecation warning and an environment-specific `.pytest_cache` permission warning
- `sledtrace-0.6.0` wheel and sdist builds succeeded
- clean wheel import and installed CLI validation succeeded
- wheel-installed `serve` outside a checkout returned the expected guidance and a non-zero exit
- repo-local detection and delegation tests passed without leaving child processes
- Go Collector tests passed
- Dashboard production build passed

Release outcome:

- `main` and `v0.6.0` were pushed to `origin`
- GitHub Release published: https://github.com/Schromeo/SledTrace/releases/tag/v0.6.0
- PyPI publication was not performed

### v0.7.0 Current Progress

**v0.7.0 is External Developer Readiness, not a claim of external adoption.**

Selected priorities:

- GitHub Actions CI for Python, package validation, Go, and Dashboard
- clean-clone first-run validation without author-only knowledge
- deterministic reference traces and explicit Dashboard success criteria
- user-visible browser/screenshots for dashboard-facing validation
- focused contributor entry points and a small real issue backlog
- at least two recorded external first-run attempts
- an explicit PyPI go/no-go and publication-workflow decision

Completed first slice:

- added `.github/workflows/ci.yml` for pushes to `main`, pull requests, and manual runs
- added independent Python 3.9, Python 3.13, Go Collector, and Dashboard jobs
- Python CI runs tests, wheel/sdist build, and clean-wheel validation
- added the CI status badge to the root README
- pushed commit `9d6435ce226e7701d24a133958fa1f32e8a58cac`
- verified GitHub Actions run https://github.com/Schromeo/SledTrace/actions/runs/34304017537 completed successfully in 41 seconds
- observed successful job durations: Dashboard 11s, Python 3.13 21s, Python 3.9 26s, Go Collector 37s

Known follow-up:

- `main` branch protection and required-check enforcement are not configured yet
- clean-clone and Docker/local first-run validation remain pending
- `npm audit` currently reports four transitive development-dependency advisories (one moderate and three high) through the Vite/Babel/PostCSS toolchain; they were recorded rather than mixed into the initial CI change
- local validation in the restricted Codex environment required elevated reruns for package isolation, wheel temp-environment access, the Go build cache, and the npm cache; the exact CI run on GitHub completed without those host-specific permission failures

Python publication readiness completed so far:

- PyPI and TestPyPI public APIs returned no project record for `sledtrace` before publication on 2026-09-08; the successful TestPyPI upload established the project there
- commit `4c6108c0c0ad35e060b2dca9a439bbb425d33717` added the trusted-publication preparation
- package metadata now exposes homepage, documentation, repository, and issue URLs
- the SDK distribution now includes the MIT license text
- normal CI runs `twine check` on both Python 3.9 and 3.13
- `.github/workflows/publish-python.yml` defaults to validation only and requires an explicit target for TestPyPI or PyPI
- actual publishing requires a `v`-prefixed tag matching the package version and grants `id-token: write` only to the selected upload job
- remote validate run https://github.com/Schromeo/SledTrace/actions/runs/34306741532 succeeded, retained one `python-package` artifact, and skipped both upload jobs
- v0.7.0 is the intended first production PyPI version; do not rebuild a different v0.6.0 artifact after its immutable release
- the pending Trusted Publisher for TestPyPI is registered for `Schromeo/SledTrace`, workflow `publish-python.yml`, environment `testpypi`
- local `0.7.0rc1` tests, isolated build, `twine check`, and clean-wheel import/CLI validation passed
- commit `01a443f2d94c4574948edfc8a495fb997aad3de9` and annotated tag `v0.7.0rc1` are pushed
- GitHub Actions run https://github.com/Schromeo/SledTrace/actions/runs/34309033246 published the candidate to TestPyPI; the production PyPI job was skipped
- a no-cache install from the TestPyPI public index passed outside the source repository, including imports, CLI version/help, and the expected non-zero `serve` boundary
- TestPyPI project: https://test.pypi.org/project/sledtrace/0.7.0rc1/
- the production PyPI pending Trusted Publisher is registered for `Schromeo/SledTrace`, workflow `publish-python.yml`, environment `pypi`
- GitHub environment `pypi` requires approval from `Schromeo`, allows self-review for the single-maintainer workflow, rejects branch deployments, and allows only tags matching `v*`

Important sequencing:

- do not pre-commit LangChain/LlamaIndex or eval work before external-use evidence
- do not claim `pip install sledtrace` until PyPI publication and clean-install validation succeed
- keep the root README as the visual showcase
- keep `sdk/python/README.md` suitable for package metadata without duplicating Dashboard screenshot assets

### v0.5.0 Status

**v0.5.0 packaging readiness is complete, validated, tagged, and published.**

Completed work includes:

- building the Python SDK as a wheel/sdist via `python -m build`
- verifying clean install from a built artifact in a fresh venv
- keeping the preferred import path `sledtrace` stable
- preserving temporary `raglens` compatibility during migration
- verifying `SLEDTRACE_COLLECTOR_URL` precedence over `RAGLENS_COLLECTOR_URL`
- keeping v0.5 limited to packaging and documentation, without touching the warning engine or collector contracts
- annotated tag `v0.5.0` targets `b3cad60a10636dbf7a5d371f51bac0c04a4af936`
- GitHub Release published: https://github.com/Schromeo/SledTrace/releases/tag/v0.5.0

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

Historical next-step outcome:

- v0.6 Local CLI / `sledtrace serve` was selected and is now complete
- PyPI publishing was not selected and remains out of scope

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
- source and local wheel installation are supported; `0.7.0rc1` is available on TestPyPI, while production PyPI publication is not
- the packaged CLI provides help and version behavior, while `serve` requires a source checkout
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

## Release State and Next Step

v0.6.0 is the current completed and published release. The Python package, installed CLI behavior, source-checkout delegation, Collector tests, Dashboard build, repository hygiene, tags, push, and GitHub Release have been validated or verified.

Published release history:

- v0.4.0 — Local Release
- v0.4.1 — SledTrace compatibility-preserving rebrand
- v0.5.0 — Python SDK Packaging Readiness
- v0.6.0 — Local CLI / Startup UX

Current next step:

- audit the remaining v0.7 acceptance items and decide which are required before the final `0.7.0` package/release
- prepare and validate the final `0.7.0` package only after that scope decision
- make the explicit production publication go/no-go decision
- keep user-visible Dashboard evidence alongside automated validation
- make the production PyPI go/no-go decision only after the TestPyPI result
- use external first-run evidence to select later framework, distribution, diagnostic, or eval work

Current publication boundary:

- v0.5.0 and v0.6.0 tags and GitHub Releases exist
- TestPyPI `0.7.0rc1` publication exists and is clean-install validated
- production PyPI publication does not exist
- do not rewrite or move published tags as part of post-release documentation work

## Important Guardrails

- Continue local-first and deterministic-first behavior.
- Preserve the current collector API, SQLite schema, dashboard data contract, and `retrieval`/`llm` span scope.
- Preserve temporary RAGLens compatibility.
- Do not add framework adapters, cloud/auth/hosted work, new warning rules, new span types, or LLM-as-judge as part of v0.6.0.
- Do not bundle the Collector, Dashboard, Docker images, or platform-specific runtime assets into the Python wheel.

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


