# Devlog

## 2026-09-08 (v0.7.0rc1 TestPyPI Candidate Published and Validated)

### Completed

- Registered the pending TestPyPI Trusted Publisher for project `sledtrace`, owner `Schromeo`, repository `SledTrace`, workflow `publish-python.yml`, and environment `testpypi`.
- Prepared Python package version `0.7.0rc1` as a prerelease candidate; v0.6.0 remains the current stable SledTrace release.
- Updated package metadata, runtime SDK metadata, installed CLI version output, validation expectations, and package README consistently.
- Kept the temporary `raglens` compatibility import and version aligned with the preferred `sledtrace` package.
- Reworded the wheel-installed `serve` limitation so it remains accurate without embedding a stale release number.
- Pushed commit `01a443f2d94c4574948edfc8a495fb997aad3de9` and annotated tag `v0.7.0rc1`.
- Published `0.7.0rc1` to TestPyPI through OIDC Trusted Publishing: https://test.pypi.org/project/sledtrace/0.7.0rc1/

### Validation Status

- Python tests passed: 17 tests with the expected legacy-import warning.
- isolated wheel/sdist build succeeded and produced `sledtrace-0.7.0rc1-py3-none-any.whl` and `sledtrace-0.7.0rc1.tar.gz`
- `twine check` passed for both artifacts
- clean-wheel installation, `sledtrace` and legacy `raglens` imports, CLI help, `sledtrace version`, and the repository-outside `serve` failure path passed
- GitHub CI run https://github.com/Schromeo/SledTrace/actions/runs/34308937339 passed Go, Dashboard, Python 3.9, and Python 3.13 jobs
- publishing run https://github.com/Schromeo/SledTrace/actions/runs/34309033246 passed the build and TestPyPI jobs while skipping production PyPI
- a no-cache install from `https://test.pypi.org/simple/` succeeded outside the source repository and reported `0.7.0rc1`
- `git diff --check` passed

### Current Boundary

- TestPyPI publication and clean-index validation are complete
- no package has been uploaded to production PyPI yet
- the next external step is production Trusted Publisher registration followed by the final v0.7.0 go/no-go decision
- ordinary `pip install sledtrace` remains unsupported until production PyPI publication and clean-install validation succeed

---

## 2026-09-08 (v0.7 Python Trusted Publishing Preparation)

### Completed

- Confirmed the public PyPI and TestPyPI APIs had no `sledtrace` project record; the official PyPI project URL displayed a 404 page.
- Added project homepage, documentation, repository, and issue URLs to the Python package metadata.
- Added the MIT license inside the Python package build context and verified it appears in the wheel.
- Added `twine check` to both Python CI matrix jobs.
- Added `.github/workflows/publish-python.yml` with manual validate, TestPyPI, and PyPI targets.
- Restricted OIDC `id-token: write` permission to the selected package-index upload job.
- Added tag/package-version matching for real publication targets.
- Pinned release-workflow actions to the verified commits corresponding to checkout v7.0.1, setup-python v7.0.0, upload-artifact v7.0.1, download-artifact v8.0.1, and gh-action-pypi-publish v1.14.2.
- Created and pushed commit `4c6108c0c0ad35e060b2dca9a439bbb425d33717`.

### Validation Status

- local package build succeeded
- `twine check` passed for the wheel and source distribution
- clean-wheel imports and installed CLI validation passed
- isolated Pytest validation passed with 17 tests and the expected legacy-import warning
- GitHub CI run https://github.com/Schromeo/SledTrace/actions/runs/34306672732 passed all four jobs, including `twine check` on Python 3.9 and 3.13
- validate-only publishing run https://github.com/Schromeo/SledTrace/actions/runs/34306741532 succeeded in 25 seconds
- the publishing dry-run retained one `python-package` artifact; TestPyPI and PyPI jobs were both skipped

### Decision and Next Gate

- v0.7.0 is the intended first production PyPI release; do not rebuild or retroactively publish a different v0.6.0 artifact
- no package has been uploaded to TestPyPI or PyPI
- at that point, the next gate was owner-side pending Trusted Publisher registration on TestPyPI for `Schromeo/SledTrace`, workflow `publish-python.yml`, environment `testpypi`; it was completed later the same day

---

## 2026-09-08 (v0.7 Initial Cross-Stack CI Baseline)

### Completed

- Added `.github/workflows/ci.yml` for pushes to `main`, pull requests, and manual dispatch.
- Added Python 3.9 and 3.13 matrix jobs covering `pytest -q`, wheel/sdist build, and clean-wheel validation.
- Added independent Go Collector tests and Dashboard production-build jobs.
- Added a live CI badge to the root README.
- Created and pushed commit `9d6435ce226e7701d24a133958fa1f32e8a58cac` with message `ci: add cross-stack validation workflow`.
- Verified GitHub Actions run https://github.com/Schromeo/SledTrace/actions/runs/34304017537 completed successfully.
- Opened the successful run as visible browser evidence; no Dashboard screenshot was changed because this slice did not alter Dashboard UI behavior.

### Validation Status

- GitHub Actions total duration: 41 seconds.
- Python 3.9: passed in 26 seconds.
- Python 3.13: passed in 21 seconds.
- Go Collector: passed in 37 seconds.
- Dashboard: passed in 11 seconds.
- Local Python tests passed with 17 tests and the expected legacy-import warning.
- Local package build, clean-wheel validation, Go tests, and Dashboard build passed after rerunning outside host-specific sandbox/cache restrictions.

### Known Follow-up

- `main` branch protection and required-check enforcement are not configured yet.
- Clean-clone and Docker/local first-run validation remain pending.
- `npm audit` reports four transitive development-dependency advisories: one moderate and three high. They are reached through the current Vite/Babel/PostCSS build toolchain and should be handled in a focused dependency-update slice rather than silently ignored or mixed into the initial CI commit.

---

## 2026-09-08 (v0.6.0 Release Closure and v0.7 Direction Selected)

### Completed

- Created release commit `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e` with message `feat(cli): complete SledTrace v0.6.0 startup UX`.
- Included repository hygiene in the v0.6 commit by removing tracked Python bytecode/cache artifacts and expanding `.gitignore` coverage for package-test virtual environments.
- Created and pushed annotated tag `v0.5.0` at `b3cad60a10636dbf7a5d371f51bac0c04a4af936`.
- Created and pushed annotated tag `v0.6.0` at `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e`.
- Published the v0.5.0 GitHub Release:
  - https://github.com/Schromeo/SledTrace/releases/tag/v0.5.0
- Published the v0.6.0 GitHub Release:
  - https://github.com/Schromeo/SledTrace/releases/tag/v0.6.0
- Confirmed both releases are non-draft, non-prerelease releases.
- Selected **v0.7.0 — External Developer Readiness** as the next planned milestone.
- Established CI, clean-clone first-run evidence, contributor readiness, and user-visible Dashboard validation as the v0.7 priority order.
- Elevated PyPI publication to a v0.7 decision gate without claiming it is currently available.
- Established screenshot policy: conversation evidence for UI checkpoints, README updates only for material visible changes, and release-quality refreshes for releases that change the Dashboard.
- Reconciled root README, SDK package README, release notes, and AI-context documents with the actual published state.

### Validation Status

- v0.6 release validation remains the accepted 2026-09-07 validation record below.
- This post-release closure is documentation-only and does not change runtime behavior.
- No Dashboard screenshots were refreshed because v0.6 did not change Dashboard UI behavior.
- PyPI publication was not performed.

### Notes

- These post-release documentation updates occur after the immutable v0.6.0 tag and do not rewrite the released tag.
- GitHub Release bodies should remain synchronized with the corrected release-note files after this documentation update is reviewed and published.

---

## 2026-09-07 (v0.6.0 Local CLI / Startup UX Completed)

### Completed

- Added a package-installed `sledtrace` CLI entry point via `project.scripts` in the Python package.
- Added the first CLI module at `sdk/python/sledtrace/cli.py` with `serve` and `version` subcommands.
- Kept `sledtrace serve` minimal and compatibility-safe by delegating to the existing repo-local startup script.
- Added a regression test covering `sledtrace.cli` import and CLI presence.
- Replaced module-location-based repository inference with explicit upward discovery from the current working directory.
- Required `AGENTS.md`, `docker-compose.yml`, and `scripts/start-sledtrace.py` as checkout markers.
- Added clear non-zero guidance for `sledtrace serve` outside a source checkout.
- Expanded CLI help to document the source-checkout limitation.
- Aligned Python package, public CLI, SDK trace metadata, demo metadata, and Dashboard package versions to `0.6.0`.
- Expanded clean-wheel validation to execute installed CLI help, version, and expected `serve` failure behavior.
- Added unit coverage for repository discovery, outside-checkout guidance, and repo-local startup delegation without launching child services.
- Corrected the SDK README example so `flush()` runs after the trace context exits.
- Added `docs/releases/V0_6_0.md` and reconciled current-status documentation.

### Validation Status

Validated successfully:

- `python -m pip install -e .` succeeded
- `sledtrace --help` displayed the CLI commands
- `sledtrace serve --help` documented the source-checkout boundary
- `sledtrace version` printed `0.6.0`
- `pytest -q` passed with 17 tests; output included the expected legacy-import deprecation warning and an environment-specific `.pytest_cache` permission warning
- `python -m build` produced the `sledtrace-0.6.0` wheel and sdist
- `python scripts/validate-wheel.py` passed preferred/legacy imports and all installed CLI checks
- wheel-installed `sledtrace serve` outside a checkout returned the documented guidance and a non-zero exit
- `go test ./... -count=1` passed in `collector/go`
- `npm.cmd run build` passed in `dashboard/web`
- repo-local detection and delegation validation passed without leaving long-running processes

### Notes

- The CLI milestone is intentionally small and does not alter collector protocol, warning logic, or trace schema.
- The package-level compatibility and SledTrace-first import path remain in place.
- The wheel intentionally does not bundle Collector, Dashboard, Docker, or platform-specific runtime assets.
- At milestone-completion time, no Git tag, GitHub release, or PyPI publication had been created. The tag and GitHub Release were subsequently published on 2026-09-08; PyPI publication remains incomplete.

---

## 2026-09-07 (v0.5.0 Python SDK Distribution / Packaging Readiness)

### Completed

- Updated SDK package metadata to SledTrace-first naming and version `0.5.0`.
- Added public `__version__` export at the `sledtrace` package root.
- Preserved temporary `raglens` compatibility shim and deprecation warning for migration.
- Added packaging/compatibility coverage under `sdk/python/tests/`.
- Added local wheel validation script at `sdk/python/scripts/validate-wheel.py`.
- Updated SDK and root README docs for local wheel installation and SledTrace-first usage.
- Documented v0.5.0 milestone in the release notes at `docs/releases/V0_5_0.md`.

### Validation Status

Validated successfully with the required local package workflow:

- `python -m build` succeeded
- clean venv wheel install succeeded
- `import sledtrace` succeeded
- `from sledtrace import trace` succeeded
- legacy `raglens` import succeeded
- `pytest` passed in `sdk/python`
- `go test ./... -count=1` passed in `collector/go`
- `npm run build` passed in `dashboard/web`

### Notes

- No warning engine changes were made.
- No collector API contract changes were made.
- No storage schema changes were made.
- No dashboard data contract changes were made.
- No new span types were introduced.
- No PyPI upload step is part of this release.

---

## 2026-07-15 (v0.4.1 Rebrand)

### Completed

- Rebranded active project name from RAGLens to SledTrace across product docs and UI labels.
- Added rebrand migration guide:
  - `docs/REBRANDING.md`
- Added release notes:
  - `docs/releases/V0_4_1.md`
- Added new primary startup launcher:
  - `scripts/start-sledtrace.py`
- Kept legacy startup command via compatibility wrapper:
  - `scripts/start-raglens.py`
- Added preferred collector env var support in SDK and docs:
  - `SLEDTRACE_COLLECTOR_URL`
- Kept legacy collector env var support for this release:
  - `RAGLENS_COLLECTOR_URL` (deprecated)
- Updated dashboard and compose branding to SledTrace while keeping collector port `4319`.
- Kept SQLite table schema and contracts unchanged.

### Notes

- v0.4.1 is compatibility-preserving and does not change warning logic, API semantics, or storage schema.
- v0.4.0 remains historically accurate as a release originally published under the RAGLens name.

## 2026-07-14 (v0.4.0 Local Release / First-Run DX)

### Completed

- Added Docker local stack at repository root:
  - `docker-compose.yml`
  - collector service on `:4319`
  - dashboard service on `:5173`
  - persistent Docker volume `sledtrace_data` for SQLite storage
- Added collector container build:
  - `collector/go/Dockerfile`
- Added dashboard container build and static serving:
  - `dashboard/web/Dockerfile`
  - `dashboard/web/nginx.conf`
- Added release/install support files:
  - `.dockerignore`
  - `.env.example`
  - `LICENSE` (MIT)
- Added v0.4 docs:
  - `docs/releases/V0_4_0.md`
  - `docs/demo/REFERENCE_RAG_APP.md`
- Updated first-run guidance:
  - `README.md`
  - `docs/demo/SMOKE_TEST.md`
  - `docs/ai-context/ROADMAP.md`
  - `docs/ai-context/CURRENT_TASK.md`
  - `docs/ai-context/AI_HANDOFF.md`
- Added optional local health checker:
  - `scripts/check-raglens.py`

### Validation Commands

Planned v0.4 validation commands:

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

### Observed Results

- `cd collector/go && go test ./... -count=1` passed.
- `cd dashboard/web && npm run build` passed.
- `docker compose up --build` built both collector and dashboard images and started containers successfully.
- `curl http://localhost:4319/health` returned HTTP 200 with JSON `{"service":"sledtrace-collector","status":"ok"}`.
- `curl http://localhost:5173` returned HTTP 200 HTML for dashboard app.
- `cd sdk/python && pip install -e .` passed in local `.venv`.
- `python -m examples.reference_rag_app.run all` completed and flushed all expected traces:
  - `reference-rag-app-refund`
  - `reference-rag-app-conflict`
  - `reference-rag-app-wrong-window`
  - `reference-rag-app-processing-range`
  - `reference-rag-app-wrong-processing-range`
  - `reference-rag-app-damaged`
  - `reference-rag-app-digital`
  - `reference-rag-app-subscription`
  - `reference-rag-app-weak`
- Collector list API verification confirmed all 9 expected reference trace names were present.
- Docker cleanup commands passed:
  - `docker compose down`
  - `docker compose down -v`

### Notes

- v0.4.0 keeps warning behavior deterministic-first.
- No SDK trace API changes were made.
- No collector API contract changes were made.
- No storage schema changes were made.
- No dashboard data contract changes were made.

## 2026-07-08 (v0.3.5 Diagnostic Quality Hardening Completed)

### Completed

- Added `sdk/python/examples/reference_rag_app/` as a thin deterministic-first reference integration app.
- Added local policy corpus for reference integration validation under `sdk/python/examples/reference_rag_app/docs/`.
- Completed mixed raw retrieval output normalization flow with `normalize_chunks()` in the reference app.
- Added optional real LLM validation path while keeping deterministic-first default behavior.
- Hardened warning engine numeric extraction to support natural-language ranges:
  - `5 to 10 business days`
  - `2 to 3 business days`
  - `10 to 20 business days`
  - `1 to 2 years`
  - `24 to 48 hours`
- Preserved prior deterministic numeric mismatch guardrails:
  - no false-positive numeric mismatch for elapsed-time phrasing like `20 days ago`
  - mismatch still fires for unsupported policy windows like `45 days` vs retrieved `30 days`
  - mismatch suppression remains when answer numeric value is directly supported by at least one retrieved chunk
- Hardened conflicting chunk candidate selection with deterministic relevance-aware ranking and query gating.
- Added deterministic topic classifier for numeric expressions and topic gating in conflicting chunk selection.
- Added query-intent compatibility for conflicting chunk diagnostics so damaged-item queries do not surface unrelated refund-processing conflicts.
- Added/updated warning tests for:
  - numeric range mismatch behavior
  - matching-range non-mismatch behavior
  - query-relevant conflicting chunk preference and noise suppression
- Cleaned deterministic demo answers for `conflict`, `digital`, and `damaged` to reduce avoidable grounding-noise.

### Validation

Validated with:

```bash
cd collector/go
go test ./... -count=1

cd sdk/python
python -m examples.reference_rag_app.run processing-range
python -m examples.reference_rag_app.run wrong-processing-range
python -m examples.reference_rag_app.run all

cd sdk/python
python -m examples.real_llm_rag_demo all
```

Observed results:

- collector warning-engine tests passed after numeric/range/conflict hardening updates
- reference integration traces were generated and persisted successfully
- wrong-window and wrong-processing-range still trigger `numeric_mismatch` as expected
- weak case continues to trigger retrieval + grounding diagnostics
- subscription case remains low-noise and typically warning-free

Observed final reference app behavior:

- `damaged` produces no warning after query-intent/topic compatibility gating
- `processing-range` still surfaces relevant refund-processing conflicts
- `wrong-processing-range` still surfaces `numeric_mismatch`
- `weak` still surfaces `answer_not_grounded`

### Notes

- v0.3.5 is complete as a deterministic warning-quality and integration-hardening slice.
- warning generation remains collector-side and deterministic-first.
- no storage schema, dashboard schema, or SDK trace API changes were required for this hardening pass.

## 2026-07-06 (v0.3 Backend Test Coverage Added)

### Completed

- Added focused Go unit tests for the v0.3 warning engine.
- Covered core diagnostic rules:
  - `numeric_mismatch`
  - `weak_query_chunk_overlap`
  - `answer_not_grounded`
  - `conflicting_chunks`
- Added SQLite storage round-trip tests for Warning Schema v2 payloads.
- Verified that v2 warning fields persist and load correctly:
  - `schema_version`
  - `rule_id`
  - `rule_version`
  - `category`
  - `confidence`
  - `explanation`
  - `evidence`
  - `diagnostics`
  - `signals`
  - `recommended_action`
- Added migration coverage for legacy `warnings` tables missing v2 columns.
- Added API handler tests to verify that:
  - `POST /api/traces` generates v0.3 warnings
  - `GET /api/traces/{trace_id}` returns v2 warning fields for dashboard consumption

### Validation

Validated with:

```bash
cd collector/go
go test ./... -count=1
```

Observed result:

- warning engine tests passed
- storage round-trip tests passed
- legacy warning table migration test passed
- API handler tests passed

### Notes

- v0.3 diagnostic intelligence is now covered at the rule, storage, and API layers.

## 2026-07-06 (v0.3 Diagnostic Intelligence Core Implemented and Smoke-Tested)

### Completed

- Implemented Warning Schema v2 defaults and evidence-backed warning enrichment in the collector.
- Implemented or upgraded the first v0.3 diagnostic rules:
  - `weak_query_chunk_overlap`
  - `numeric_mismatch`
  - `answer_not_grounded` with v2 evidence-backed payloads
  - `conflicting_chunks` with v2 evidence-backed payloads
- Added deterministic demo cases in `sdk/python/examples/diagnostic_quality_demo.py` for:
  - `numeric_mismatch`
  - `weak_query_chunk_overlap`
  - `answer_not_grounded`
  - `conflicting_chunks`
- Updated the dashboard warning detail UI to show:
  - evidence preview blocks
  - compared numeric values for `numeric_mismatch`
  - recommended action labeling
  - responsive warning detail polish

### Validation

Validated with:

```bash
cd collector/go
go test ./...

cd dashboard/web
npm run build

cd sdk/python
python -m examples.diagnostic_quality_demo all
```

Observed results:

- Go collector packages compiled successfully.
- Dashboard TypeScript and production build completed successfully.
- All four v0.3 diagnostic demo cases ran successfully and flushed traces:
  - `numeric_mismatch`
  - `weak_query_chunk_overlap`
  - `answer_not_grounded`
  - `conflicting_chunks`

### Notes

- v0.3 core diagnostic intelligence is now implemented and smoke-tested.
- The milestone remains local-first and deterministic-first.
- Current span coverage remains limited to `retrieval` and `llm` spans.

## 2026-07-06 (v0.3 Diagnostic Intelligence Spec Added)

### Completed

- Added `docs/product/V0_3_DIAGNOSTIC_INTELLIGENCE.md`.
- Defined v0.3 as the milestone that upgrades warning flags into evidence-backed diagnostic insights.
- Captured the first structured design for:
  - Warning Schema v2
  - EvidenceItem schema
  - DiagnosticObject schema
- Defined the first enhanced warning set:
  - `low_retrieval_score_v2`
  - `weak_query_chunk_overlap`
  - `answer_not_grounded_v2`
  - `numeric_mismatch`
  - `conflicting_chunks_v2`
- Locked scope boundaries so v0.3 remains local-first, deterministic-first, and limited to current `retrieval` and `llm` spans.

### Notes

- Explicitly out of scope: LangChain, LlamaIndex, PyPI, Docker, CLI, agent spans, tool spans, memory spans, cloud, auth, and LLM-as-judge.
- The document is a product and schema design spec only. No implementation work was started.

## 2026-07-03 (Future Agent Harness Observability Direction Documented)

### Completed

- Added documentation-only positioning updates for future agent harness observability.
- Clarified that future direction may include:
  - running traces for multi-step harness executions
  - partial span ingestion
  - future `agent` / `tool` / `retry` span types
  - diagnostics for agent loops, oscillation, retry storms, and no-progress execution
- Explicitly marked all of the above as not implemented in current SledTrace.

## 2026-07-02 (v0.2 Developer Integration / Local SDK Onboarding Completed)

### Completed

- Marked v0.2 Developer Integration / Local SDK Onboarding as completed.
- Finalized onboarding and integration documentation:
  - `docs/product/USER_ONBOARDING.md`
  - `docs/integrations/PYTHON_SDK_GUIDE.md`
- Added `sdk/python/examples/custom_pipeline_demo.py` and validated dashboard visibility for `custom-rag-pipeline`.
- Added and polished `scripts/start-sledtrace.py` as a cross-platform repo-local startup helper.
- Updated `README.md` with two quickstart paths:
  - Path A: built-in demo
  - Path B: own RAG app integration
- Added root README documentation map to separate user docs from maintainer docs.
- Completed SDK packaging hygiene:
  - `sdk/python` package version set to `0.2.0`
  - added `sdk/python/README.md`
  - `pyproject.toml` `readme` points to the local SDK README
  - editable install remains the supported v0.2 path

### Validation

Validated the v0.2 integration flow with:

```bash
python scripts/start-sledtrace.py
cd sdk/python
python -m examples.custom_pipeline_demo
python -m examples.local_rag_demo.run_demo trace-all
```

Observed results:

- Dashboard showed `custom-rag-pipeline`.
- Dashboard showed built-in local RAG demo traces and warning-focused cases.

### Notes

- Current implemented span types remain `retrieval` and `llm` only.
- Current warning rules remain:
  - `no_retrieved_chunks`
  - `low_retrieval_score`
  - `duplicate_chunks`
  - `conflicting_chunks`
  - simplified `answer_not_grounded`
- v0.3 recommended next focus is RAG Quality Analysis / Diagnostic Intelligence.

## 2026-07-02 (v0.2 Developer Integration / Local SDK Onboarding Core Complete)

### Completed

- Completed the core v0.2 Developer Integration / Local SDK Onboarding work.
- Added and refined user onboarding documentation:
  - `docs/product/USER_ONBOARDING.md`
  - `docs/integrations/PYTHON_SDK_GUIDE.md`
- Added `sdk/python/examples/custom_pipeline_demo.py` as a minimal deterministic integration example.
- Added and polished `scripts/start-sledtrace.py` as a cross-platform repo-local startup helper.
- Updated `README.md` to document two quickstart paths:
  - Path A: try SledTrace with the built-in demo
  - Path B: use SledTrace with your own RAG app

### Validation

Validated the v0.2 integration flow with the following commands:

```bash
python scripts/start-sledtrace.py
cd sdk/python
python -m examples.custom_pipeline_demo
python -m examples.local_rag_demo.run_demo trace-all
```

Observed result:

- `custom-rag-pipeline` was visible in the dashboard.
- Built-in local RAG demo traces were visible in the dashboard.
- Warning-focused demo traces and warning cards were visible in the dashboard.

### Notes

- Current implemented span types remain `retrieval` and `llm` only.
- Current warning rules remain:
  - `no_retrieved_chunks`
  - `low_retrieval_score`
  - `duplicate_chunks`
  - `conflicting_chunks`
  - simplified `answer_not_grounded`
- v0.2 is core complete and in final documentation polish.

## 2026-07-02 (Startup Guidance Sync)

### Completed

- Unified startup guidance across `README.md`, `docs/product/USER_ONBOARDING.md`, and `docs/integrations/PYTHON_SDK_GUIDE.md`.
- Standardized the recommended v0.2 local startup command to `python scripts/start-sledtrace.py`.
- Kept manual collector/dashboard startup steps as fallback paths where useful.

## 2026-07-02 (Repo-Local Startup Helper Polish)

### Completed

- Added `scripts/start-sledtrace.py` as the recommended repo-local v0.2 startup helper.
- Kept the helper dependency-free and cross-platform:
  - starts collector from `collector/go`
  - starts dashboard from `dashboard/web`
  - uses `npm.cmd` on Windows and `npm` on macOS/Linux
  - terminates the sibling process if either child exits first
  - handles Ctrl+C / SIGTERM with terminate-then-kill cleanup
- Updated `docs/integrations/PYTHON_SDK_GUIDE.md` to document:
  - the repo-local startup helper
  - Bash and PowerShell collector URL environment variable setup
  - explicit `POST {collector_url}/api/traces` flush target
  - collector-running prerequisite for the custom pipeline demo

## 2026-07-02 (Python SDK Guide)

### Completed

- Added `docs/integrations/PYTHON_SDK_GUIDE.md` as a practical API usage guide for the current Python SDK.
- Documented only the currently implemented v0.2 SDK surface:
  - `trace(...)`
  - `retrieval(...)`
  - `llm(...)`
  - `flush(...)`
- Captured current SDK behaviors and limitations:
  - prompt and messages support for LLM spans
  - retrieval chunk shallow-copy and defaulting behavior
  - flush timing requirements
  - trace error-state behavior when exceptions escape the context
  - local editable install as the current supported integration path

## 2026-07-02 (v0.2 User Onboarding Guide)

### Completed

- Added `docs/product/USER_ONBOARDING.md` for Developer Integration / User Onboarding.
- Documented practical integration for existing RAG pipelines using the Python SDK (without modifying `local_rag_demo`).
- Captured clear positioning boundaries:
  - SledTrace is a local-first tracing and debugging layer for RAG pipelines.
  - SledTrace is not a chatbot framework, vector DB, training framework, hosted platform, or app replacement.
- Included concrete guidance for:
  - local service startup (collector + dashboard)
  - wrapping request paths with `trace(...)`
  - logging `retrieval` and `llm` spans
  - calling `flush()` after exiting the trace context
  - chunk object field expectations (required vs recommended)
  - current warning analysis scope and current non-goals/limitations

## 2026-06-30 (Positioning Update: RAG Debugger -> TraceForge Direction)

### Completed

- Clarified long-term direction: SledTrace remains a local-first visual debugger for RAG pipelines in v0.1, while the tracing core is positioned to evolve toward TraceForge-style AI application harness observability.
- Documented RAG as the first vertical slice because retrieval quality, context quality, conflicting evidence, and grounding are common AI failure points.
- Updated docs to separate current implementation from future direction:
  - v0.1 remains completed
  - v0.2 remains Developer Integration / User Onboarding
  - harness-level spans (tool, memory, verification, human feedback) remain future possible directions

## 2026-06-30 (Platform-Specific Script Folders)

### Completed

- Split repository startup scripts into platform-specific folders:
  - `scripts/windows` for PowerShell entry points
  - `scripts/mac` for Bash entry points
- Added macOS shell wrappers for collector, dashboard, demo trace generation, and smoke testing.
- Added one-click `start-all` launchers for macOS and Windows to start collector and dashboard together.
- Replaced the split root launchers with a single cross-platform `scripts/start-all.py` entry point.
- Updated README quickstart and shortcut commands to point at the cross-platform one-click entry point.

### Notes

- macOS scripts are executable Bash entry points and can be run with `bash ./scripts/mac/...`.
- Windows scripts remain PowerShell-based and now live under `scripts/windows`.

## 2026-06-22 (Dashboard UI Polish + Final v0.1 Release Prep)

### Completed

- Dashboard sidebar trace list: added text truncation for query and answer fields
  - Query: max 2 lines, ellipsis overflow
  - Answer: max 3 lines, ellipsis overflow
  - Ensures uniform card heights regardless of content length
- Final answer card in trace detail:
  - Repositioned from floating window to grid layout with Query/Duration/Warnings
  - Added inline vertical resizing with `resize: vertical` CSS
  - Scrollable content area for long answers
  - Removed nested border structure (single outer card border)
  - Initial height: 92px min, 320px max, user-adjustable
- README aligned with current screenshots and feature set
- All dashboard, SDK, collector, and documentation paths verified and consistent

### Notes

- Sidebar truncation prevents layout explosion when some traces have very long final answers
- Final answer card resizing allows users to expand/collapse inline without moving page flow
- UI changes improve dashboard readability for both quick scanning (list view) and detailed inspection (detail view)

## 2026-06-22 (Demo Packaging Progress + Final Smoke Validation)

### Completed

- Ran startup and demo scripts from repository root:
  - `scripts/start-collector.ps1`
  - `scripts/start-dashboard.ps1`
  - `scripts/demo-trace-all.ps1`
  - `scripts/smoke.ps1`
- Verified `trace-all` completed with `Generated traces: 5` and `Failed traces: 0`.
- Verified expected warning mapping via collector API for generated trace IDs.
- Aligned README and demo docs command paths with actual directories:
  - collector path -> `collector/go`
  - dashboard path -> `dashboard/web`
- Added cross-links across demo docs:
  - `LOCAL_RAG_DEMO.md` <-> `WARNING_RULES.md` <-> `SMOKE_TEST.md`

### Acceptance Snapshot

- Collector health: pass
- Dashboard starts: pass
- trace-all runs: pass
- no_match warning: pass
- low_score warning: pass
- duplicate warning: pass
- conflict warning: pass
- hallucinated warning: pass
- Trace detail readable: pass
- README commands accurate: pass

### Notes

- Conflict trace can include an additional warning alongside `conflicting_chunks` in some runs.
- For acceptance, conflict case validation checks that `conflicting_chunks` is present.

## 2026-06-21 (Real Local RAG Demo Documentation and Milestone Closeout)

### Completed

- Finalized documentation for the Real Local RAG Demo milestone.
- Updated local demo runbook in `sdk/python/examples/local_rag_demo/README.md` for new developers.
- Synced milestone-complete status across AI handoff, roadmap, and current task docs.
- Documented verified command set and expected warning-target case mapping.

### What Was Built (Milestone Summary)

- local markdown policy corpus
- local loader
- deterministic chunker
- TF-IDF plus cosine retriever
- simple local answerer
- SDK trace integration to collector on `:4319`
- dashboard verification of real retrieval traces and warning cards

### Why TF-IDF Was Chosen

- Fully local-first and easy to run in v0.1.
- Transparent scoring behavior for debugging and explanation.
- Minimal dependency and infrastructure complexity.
- Good baseline before semantic retriever comparison.

### What Was Verified

- End-to-end flow from SDK flush to collector to SQLite to dashboard.
- Real retrieved chunks include ids, source, rank, text, and scores.
- Warning cards render from real retrieval output, not only synthetic fixtures.

### Warning Rules Triggered In Verified Cases

- `no_retrieved_chunks` via `no_match`
- `low_retrieval_score` via `low_score`
- `duplicate_chunks` via `duplicate`
- `conflicting_chunks` via `conflict`
- simplified `answer_not_grounded` via `hallucinated`

### Deferred By Design

- LangChain adapter integration
- LlamaIndex adapter integration
- Vector database integration
- External embedding providers

These remain intentionally deferred until DX hardening and test coverage improve.

## 2026-06-15 (Real Local RAG Milestone Completed)

### Completed

- Marked Real Local RAG Demo milestone as completed across milestone, roadmap, task, and handoff docs.
- Captured completed implementation scope:
  - local markdown policy documents
  - local document loader
  - deterministic chunking
  - TF-IDF + cosine retriever
  - simple local answerer
  - demo case matrix
  - traced integration through existing SDK schema
  - collector ingestion on `:4319`
  - dashboard verification
  - warning trigger verification on real retrieval output

### Notes

- Added explicit demo command runbook to the milestone and handoff docs.
- Shifted active focus to post-milestone hardening (warning explanations, tests, semantic retriever evaluation).

## 2026-06-15 (Real Local RAG Docs)

### Completed

- Added `docs/ai-context/REAL_LOCAL_RAG_MILESTONE.md` to define active milestone scope, exit criteria, runbook, and non-goals.
- Added `docs/architecture/LOCAL_RETRIEVAL_BASELINE.md` to document current local retrieval implementation (chunking + TF-IDF + cosine).

### Notes

- Current retriever baseline is intentionally lexical and transparent.
- Framework adapters remain deferred until Real Local RAG Demo is validated.

## 2026-06-15 (Docs Sync)

### Completed

- Updated core docs to reflect that Warning Engine / Diagnosis Layer MVP is complete.
- Synced status across README, roadmap, handoff, current task, architecture, and product docs.
- Marked Real Local RAG Demo as the next active milestone.

### Notes

- Warning rules now documented as implemented: `no_retrieved_chunks`, `low_retrieval_score`, `duplicate_chunks`, `conflicting_chunks`, simplified `answer_not_grounded`.
- `sdk/python/examples/warning_rules_demo.py` documented as primary warning smoke test.

## 2026-06-15

### Completed

- Updated `sdk/python/examples/warning_rules_demo.py` to call `print_and_flush(t)` after exiting each `with trace(...)` block.
- Ensured all five warning-rule smoke demos finalize trace lifecycle before serialization and POST.

### Validation

Ran all warning demos:

```bash
cd sdk/python
python -m examples.warning_rules_demo all
```

Observed result:

- All five demos still return `warnings_generated: 1`.
- `trace.ended_at` is now populated (no longer `null`) across all demo payloads.
- `trace.duration_ms` is now populated as `0` for this fast local smoke run (no longer `null`).

### Notes

This keeps demo payload timing fields compatible with timeline rendering and future latency-oriented warning logic.

## 2026-06-13

### Completed

- Added Warning Engine in the Go collector.
- Implemented the first diagnosis rule: `conflicting_chunks`.
- Collector now generates and persists warnings after storing trace payloads.
- Dashboard trace detail now renders real warning cards.
- Refund policy demo now reliably triggers one warning for conflicting `30 days` vs `14 days` refund-policy chunks.

### Validation

Collector health check:

```powershell
Invoke-RestMethod http://localhost:4319/health
```

Demo execution:

```bash
cd sdk/python
python -m examples.refund_policy_demo
```

Observed result:

- Trace is ingested and persisted.
- `conflicting_chunks` warning is generated and stored.
- Warning appears on dashboard trace detail.

### Notes

SledTrace now has an end-to-end diagnosis path from ingestion to UI rendering.

The warning engine is intentionally incremental in v0.1: start with one high-signal rule, validate the full loop, then add additional rules.

### Next Step

Expand warning coverage with the next rules:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- simplified `answer_not_grounded`

## 2026-05-15

### Completed

- Defined the v0.1 product direction for SledTrace.
- Confirmed that SledTrace starts as a local-first visual debugger for RAG pipelines.
- Established the long-term architecture direction: start with RAG debugging, while keeping the internal model compatible with future AgentOps/TraceForge-style tracing.
- Created the initial product specification in `docs/product/PRODUCT_SPEC.md`.
- Defined the initial trace/span data model in `docs/architecture/TRACE_DATA_MODEL.md`.
- Decided that the developer-facing Python API should stay simple, while the internal representation uses traces and spans.
- Defined the core v0.1 entities:
  - Trace
  - Span
  - Retrieval chunk
  - LLM span
  - Warning
- Defined the initial SQLite schema for:
  - `traces`
  - `spans`
  - `warnings`
- Implemented the first minimal Python SDK.
- Added a `trace()` context manager.
- Added support for recording retrieval spans.
- Added support for recording LLM spans.
- Created the refund policy demo.
- Verified that the SDK can generate a complete trace payload locally.
- Pushed the initial documentation and SDK code to GitHub.

### Key Decisions

- SledTrace v0.1 will use a local-first architecture.
- SQLite will be the default local storage backend.
- The Python SDK will expose a simple API:
  - `trace(name)`
  - `t.retrieval(...)`
  - `t.llm(...)`
- Internally, SledTrace will represent RAG pipeline activity using a trace/span model.
- A trace represents one complete RAG request.
- A span represents one step inside the pipeline, such as retrieval or LLM generation.
- The initial span types are:
  - `retrieval`
  - `prompt`
  - `llm`
  - `custom`
- Warning rules will start as lightweight heuristics, not ML-based evaluation.

## 2026-05-14

### Completed

- Chose SledTrace as the first product cut.
- Defined the long-term path: SledTrace -> AgentOps Lite -> TraceForge.
- Decided to start with a local-first visual debugger for RAG pipelines.
- Created the initial repository documentation plan.

### Key Decisions

- Start narrow with RAG debugging instead of building a full LLMOps platform.
- Keep v0.1 local-first.
- Prioritize usability, visual clarity, and easy setup.
- Use project docs as long-term memory for AI collaboration.

### Next

- Create the initial repo structure.
- Write PRODUCT_SPEC.md.
- Design the trace/span data model.
- Decide the first implementation order.

Ran the refund policy demo locally:

```bash
cd sdk/python
python -m examples.refund_policy_demo
```

The SDK successfully generated a trace payload containing:

- One trace named refund-policy-qa
- One retrieval span named search_refund_docs
- Two retrieved chunks:
  - refund_policy_new.md, version 2026, refund window 30 days
  - refund_policy_old.md, version 2024, refund window 14 days
- One LLM span named generate_answer
- A final answer using the outdated 14 days refund window

### Notes

This is the first runnable milestone for SledTrace.

The project now has both:

- A documented product and architecture direction
- A working Python SDK prototype that can generate structured trace payloads

The current SDK only prints trace JSON locally.

The next step is to build the Go collector so the SDK can send traces to a local HTTP endpoint and persist them in SQLite.

### Next Step

Build the local Go collector.

Initial collector scope:

- GET /health
- POST /api/traces
- SQLite persistence
- GET /api/traces
- GET /api/traces/{trace_id}

## 2026-05-15

### Completed

- Implemented the initial Go collector.
- Added `GET /health`.
- Added `POST /api/traces`.
- Added SQLite-backed local persistence.
- Added storage for traces and spans.
- Verified that the collector can receive a Python SDK-generated trace payload.
- Verified that the collector stores trace data in local SQLite.

### Validation

Started the collector locally:

```bash
cd collector/go
go run ./cmd/sledtrace-collector
```

Checked collector health:

```powershell
Invoke-RestMethod http://localhost:4319/health
```

Posted a sample trace payload:

```powershell
Invoke-RestMethod `
  -Uri http://localhost:4319/api/traces `
  -Method POST `
  -ContentType "application/json" `
  -InFile sample_trace.json
```

The collector returned:

```json
{
  "status": "stored",
  "warnings_generated": 0
}
```

### Notes

The local collector can now receive and persist trace payloads.

The next step is to add a flush() method to the Python SDK so demo traces can be sent directly to the collector without manually copying JSON into a file.

### Commit

```bash
git add .
git commit -m "feat(collector): add Go collector with SQLite persistence"
git push
```

## 2026-05-18

### Completed

- Added `flush()` support to the Python SDK.
- Added `collector_url` support to the trace context manager.
- Updated the refund policy demo to send traces directly to the local collector.
- Verified that the Python SDK can POST trace payloads to `POST /api/traces`.
- Verified that the Go collector returns a successful stored response.

### Validation

Started the collector:

```bash
cd collector/go
go run ./cmd/sledtrace-collector
```

Ran the Python demo:

```bash
cd sdk/python
python -m examples.refund_policy_demo
```

The SDK generated a trace payload and sent it to the collector.

Collector response:

```json
{
  "trace_id": "trace_af404e92216b4f7f97fb415208dc5992",
  "status": "stored",
  "warnings_generated": 0
}
```

### Notes

SledTrace now has a working local trace ingestion path from Python SDK to Go collector to SQLite.

The next step is to build the initial React Dashboard so traces can be inspected visually instead of through raw JSON.

## 2026-05-19

### Completed

- Audited task documentation against implemented code and roadmap.
- Reconciled `CURRENT_TASK.md` to remove stale/duplicated initialization-phase content.
- Confirmed current milestone as dashboard implementation on top of the verified local ingestion path.

### Validation

- Verified collector endpoints remain aligned with docs:
  - `GET /health`
  - `POST /api/traces`
  - `GET /api/traces`
  - `GET /api/traces/{trace_id}`
- Verified SDK still supports posting traces through `flush()`.
- Verified dashboard source files exist but are not implemented yet (placeholders/whitespace).

### Notes

Documentation now matches actual project state:

- Infrastructure path is working end-to-end locally.
- Current data values in the demo are mock/sample values.
- The immediate workstream is building the first usable dashboard views.

### Documentation Sync

- Updated `docs/ai-context/ROADMAP.md` to include explicit phase status.
- Marked v0.1 as in progress, with SDK/collector/storage path done and dashboard work next.
- Left v0.2, v0.3, and v0.4 as not started.

## 2026-06-13

### Completed

- Reformatted `docs/ai-context/AI_HANDOFF.md` for readability and consistency.
- Normalized heading hierarchy and section spacing.
- Converted free-form completion/status blocks into structured bullet lists.
- Added clear subsection boundaries for implementation status, known issues, and next step.

### Notes

- This change is documentation-only and does not affect runtime behavior.

## 2026-06-13

### Completed

- Reformatted `docs/ai-context/CURRENT_TASK.md` for consistent Markdown structure.
- Fixed broken section boundaries and unclosed code block in the working path section.
- Standardized file lists and warning rules into clear bullet formatting.
- Converted final validation flow to a numbered checklist.

### Notes

- This change is documentation-only and does not affect runtime behavior.

## 2026-05-19

### Completed

- Added the initial React Dashboard MVP.
- Added trace list UI.
- Added trace detail UI.
- Added span timeline UI.
- Added retrieved chunk cards.
- Added LLM prompt and response viewer.
- Added JSON metadata viewer.
- Added warning placeholder UI.
- Connected the dashboard to the Go collector APIs:
  - `GET /api/traces`
  - `GET /api/traces/{trace_id}`
- Verified that traces generated by the Python SDK can be inspected in the browser.
- Fixed a dashboard blank-screen issue caused by `warnings` being returned as `null`.
- Updated backend/ frontend handling so empty warnings and spans are treated as empty arrays.
- Updated `.gitignore` to exclude local artifacts such as `node_modules`, SQLite databases, Python caches, and sample trace files.

### Validation

Started the collector:

```bash
cd collector/go
go run ./cmd/sledtrace-collector
```

Generated and flushed a demo trace:

```bash
cd sdk/python
python -m examples.refund_policy_demo
```

Started the dashboard:

```bash
cd dashboard/web
npm install
npm run dev
```

Opened:

- http://localhost:5173

Verified that the dashboard can display:

- local trace list
- selected trace detail
- retrieval span
- retrieved chunks
- LLM prompt
- LLM response
- metadata JSON

### Notes

SledTrace now has a complete local inspection loop:

- Python SDK -> Go Collector -> SQLite -> React Dashboard

The project is ready for the first diagnosis layer.

### Next Step

Implement the warning engine.

The first target warning is conflicting_chunks for the refund policy demo.

## 2026-06-13

### Completed

- Reformatted `docs/ai-context/ROADMAP.md` and removed duplicated v0.1 sections.
- Reorganized roadmap into a single logical sequence: current snapshot -> v0.1 -> v0.2 -> v0.3 -> v0.4 -> future direction.
- Added explicit v0.1 exit criteria to make completion conditions measurable.
- Aligned warning-engine scope language with `CURRENT_TASK.md` and `AI_HANDOFF.md`.

### Notes

- This update is documentation-only and does not change runtime behavior.

## 2026-06-13

### Completed

- Updated `docs/ai-context/ROADMAP.md` to keep a dedicated "Latest Progress (v0.1 Execution Status)" section at the end.
- Preserved roadmap phase order while making newest implementation status easy to find in the final section.

### Notes

- This is a documentation structure decision to separate long-horizon plan from rolling execution status.

## 2026-06-13

### Completed

- Reformatted `docs/architecture/SYSTEM_ARCHITECTURE.md` for consistent heading hierarchy and readable section flow.
- Fixed malformed Markdown structure, including unclosed code block and collapsed plain-text lists.
- Reorganized architecture description into clear sections: components, data flow, and next architecture addition.

### Notes

- This is a documentation-only change and does not affect runtime behavior.


