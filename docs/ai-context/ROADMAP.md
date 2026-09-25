# Roadmap

## Active planning baseline — 2026-09-15

The detailed, reviewable plan is [Road to v1.0](../product/ROAD_TO_V1_0.md).
It defines target users, defensible product hypotheses, per-slice acceptance,
non-goals, evidence gates, budgets, and stopping rules. Read its overview and the
selected slice, not every historical milestone before each change.

Recommended direction: a local Python execution-efficiency debugger for bounded
AI workflows. Preserve RAG evidence; add trustworthy usage attribution, one agent
integration, conservative waste signals, and outcome-aware before/after comparison.
The user adopted this direction for incremental development on 2026-09-15.
Future scope is not implemented capability or blanket authorization.

### Current facts

- AG0 is a documentation-only Agent-direction preparation candidate. The user
  has no current Agent workflow; [the A1 screen](../product/AGENT_DIRECTION_PREP.md)
  separates a public reference workflow from real adoption. E4 rule work
  waits for observable steps, task outcome and counterexamples; this does not
  change the M3 product-value gate or claim Agent support beyond E2.
- A1 locally ran the pinned public PydanticAI bank-support sample with its
  synthetic in-memory SQLite data and no-cost TestModel. Its real tool calls
  and scripted model attempts appeared in Collector/Dashboard with missing
  token usage shown as unknown; a missing customer produced a visible tool
  and task failure. This is L1 integration evidence, not provider execution,
  user value, or E4 duplicate-rule validation. See the A1 runbook and
  CURRENT_TASK; AG0/A1 are not a released milestone.
- Latest release: v0.7.1 — Trustworthy Local Tracing, published 2026-09-25
  from immutable annotated tag `v0.7.1` at `33d2335`. Protected PyPI upload,
  clean install outside the repository, and GitHub Release all succeeded.
- S1–S4 reliability work and B1/B2/H0 integration were included in the
  protected v0.7.1 mainline and release.
- D0 workflow harness was squash-merged through PR #6 as `0a63e3d`; cumulative
  PR #4 remains closed as superseded. PR #3 and PR #5 are merged.
- E1 usage visibility was squash-merged via PR #7 as `622ff69` and is in
  v0.7.1: per-call recorded tokens, trustworthy subtotal/coverage,
  measured/unknown timing, and explicit conflict/provenance states.
- E2's single Python tool path merged via PR #8 as `0734e20`. Deterministic
  success, business failure and recovery paths passed local API/UI checks.
  It is one caller-instrumented synchronous tool span, not an agent runtime.
- X1 merged via PR #10 as `755c19c`: a Harvard Federalist Papers PDF was
  indexed into SQLite FTS5 and queried through a traced adapter. This exercises
  existing retrieval diagnostics; it does not add a product capability.
- X2 merged via PR #9 as `92b27b9`; historical text `confidence="heuristic"`
  now reads as unknown without rewriting SQLite rows.
- E3 is an optional explicit mapping for caller-supplied completed,
  non-streaming OpenAI Responses results, with an indicative estimate for two
  supported models. Evidence is sanitized offline fixture and local UI
  readback, not a paid provider call, complete capture or billing comparison.
- No independent external first-run or repeat-use evidence is recorded.
- PRs #11–#13 and release-closure PR #14 merged in order. All v0.7.1 release
  gates are complete; see CURRENT_TASK and DEVLOG for evidence.
- E3R corrects two Dashboard state labels found in PR #13 review: invalid
  provider usage is unknown, while true count contradictions remain conflicts;
  explicit invalid token fields remain invalid. This is a reliability follow-up
  within E3, not a roadmap sequence change or real-provider validation.
- The release gate is closed. Product sequence remains unchanged; A1's public
  reference run is complete locally, but no user-owned Agent run is available.
  Its technical result cannot close E4/E5 product-value gates.

### Proposed post-v0.7 sequence

This sequence supersedes the 2026-09-10/14 active A–D ordering, not its completed
work or historical evidence. Keep H0 honest diagnostic presentation first, but
defer broad RAG-rule expansion and bring the efficiency/comparison loop forward.

| Stage | Bounded deliverables | Exit gate | Suggested release grouping |
| --- | --- | --- | --- |
| M0 — complete and released | Honest warning presentation and release cleanup | UI, compatibility tests, build, real-browser checks, protected publication and clean install passed | Included in v0.7.1 |
| M1 — complete and released | E1: existing LLM usage and measured/unknown timing, per call and known subtotal | A user can identify where observed tokens/time went | Included in v0.7.1 |
| M2 — implementation released, external value unverified | E2: one Python tool path; E3: explicit OpenAI Responses usage and bounded indicative pricing | Validate a genuine workflow and determine whether the captured evidence changes a decision | v0.7.1 shipped; v0.8 scope remains open |
| M3 | E4: two conservative waste signals; E5: outcome-aware A/B comparison | One real, reviewable improvement or useful regression finding; no fabricated savings | v0.8 candidate, subject to product gate |
| M4 | U1: checkout-free runtime; U2: find/detail/compare; U3: content/data controls; U4: external onboarding | Supported install path and two genuine first uses | v0.9 candidate |
| M5 | R1: storage/delivery contract; R2: compatibility; R3: supported-platform verification | Frozen, reliable supported scope | v1.0.0rc candidate |
| G1 | Quality-preserving efficiency evidence, repeat use, RC observation, authorized publication | All checklist evidence in the detailed plan | v1.0.0 |

Atomic persistence must precede retries/repeated-import semantics; sensitive-data
controls must precede relevant external trials. These dependencies may advance a
bounded slice, not authorize parallel feature expansion.

### Next action and scope

[CURRENT_TASK](CURRENT_TASK.md) records A1's bounded integration result and
the remaining E4 evidence gate. PRs #11–#14 are merged; E3's offline validation
and the separate draft PR #16 public-corpus probe are not Agent evidence.
H0 has been handed off; do not reopen it for cosmetic optimization. No automatic
optimizer, cloud/auth, broad adapter catalog, or live partial-trace system is part
of the proposed 1.0.

Work-in-progress limit: one slice, generally 0.5–3 focused development days.
Demonstrate the affected real flow early. Run proportional checks; full candidate
validation remains a release gate, not a ritual for every documentation change.
After two slices without a visible user outcome, reassess before adding features.

The full plan guides incremental development, not automatic execution. Do not bump versions,
merge, tag, publish, contact external users, or incur model costs based on this
document alone. Keep candidate, locally validated, and released states distinct.

## Historical milestone record

The sections below retain historical goals, release evidence, and then-open work.
Their old “next” statements do not override the active sequence above.

## v0.7.0 - External Developer Readiness

**Status:** Complete and released on 2026-09-09

### Goal

Make SledTrace trustworthy and understandable for an external developer who did not participate in its development.

This milestone creates the conditions for adoption. It does not claim adoption merely because community files or screenshots exist.

### Priority Scope

#### P0 - Continuous validation

* [x] GitHub Actions for Python SDK tests on Python 3.9 and 3.13
* [x] wheel/package validation in CI
* [x] Go Collector tests
* [x] Dashboard production build
* [x] visible checks on pull requests and pushes
* [x] protect `main` with the agreed required CI checks

#### P1 - External first-run evidence

* [x] clean-clone non-Docker first-run path with no undocumented steps
* [x] deterministic reference trace generation
* [x] explicit Dashboard success criteria
* [x] actionable troubleshooting guidance, including Docker virtualization prerequisites
* [ ] at least two external first-run attempts recorded

#### P2 - Contributor readiness

* [x] focused `CONTRIBUTING.md`
* [x] bug report and feature request templates
* [x] pull-request template
* [ ] small, real, near-term public issue backlog
* [x] repeatable release checklist

#### P3 - Visible validation and project presentation

* [x] live browser/Dashboard evidence for the v0.7 clean-clone validation
* [x] deterministic screenshots refreshed to remove stale RAGLens branding and paths
* [x] README screenshots refreshed because public product presentation was stale
* [x] release-quality visual pass completed without changing Dashboard behavior

### PyPI Decision Gate

Ordinary `python -m pip install sledtrace==0.7.0` from production PyPI is supported for the Python SDK and installed CLI. The explicit `0.7.0rc1` prerelease remains available from TestPyPI as candidate history.

The v0.7 release decision covered package ownership, secure publication, TestPyPI/PyPI sequencing, long-description rendering, clean-install validation, and the relationship between the installable SDK/CLI and the source-checkout runtime.

Do not claim PyPI availability until publication and validation have succeeded.

Current progress:

* [x] confirm no public `sledtrace` project existed on PyPI or TestPyPI during the pre-publication check on 2026-09-08
* [x] add PyPI project URLs and include the MIT license in wheel/sdist artifacts
* [x] validate package metadata and long-description rendering with `twine check`
* [x] add an OIDC Trusted Publishing workflow with separate validate, TestPyPI, and PyPI paths
* [x] complete a remote validate-only run with a retained distribution artifact and no package-index upload
* [x] select v0.7.0, rather than retroactively rebuilding v0.6.0, as the intended first production PyPI release
* [x] register the pending TestPyPI Trusted Publisher
* [x] publish and clean-install tagged `v0.7.0rc1` from TestPyPI
* [x] configure production PyPI Trusted Publishing with required approval and a `v*` tag-only deployment policy
* [x] make the final production PyPI go/no-go decision
* [x] publish and clean-install `sledtrace` from production PyPI

### Scope Boundary

Do not add LangChain/LlamaIndex adapters, cloud/auth/hosted functionality, new span types, LLM-as-judge, or unrelated warning features as incidental v0.7 work. Select later product work from external-use evidence rather than pre-committing v0.8 scope.

---

### v0.6.0 Goal

Make local startup and validation easier for developers by exposing a real installable CLI entry point:

* `sledtrace serve` starts the local collector and dashboard from inside a source checkout
* `sledtrace version` prints the installed SDK version
* wheel-installed CLI help and version behavior work without bundling runtime assets
* wheel-installed `serve` outside a checkout fails with actionable guidance
* repo-local startup flows remain compatible with existing scripts
* local install and wheel validation remain green
* packaging compatibility remains preserved

### v0.6.0 Scope

* [x] `sledtrace` console script is installed via the Python package
* [x] `sledtrace --help` shows the CLI surface
* [x] `sledtrace version` prints the installed package version
* [x] `sledtrace serve` detects a source checkout and delegates to the existing repo-local startup script
* [x] wheel build/install smoke checks remain passing
* [x] wheel-installed `serve` fails gracefully outside a checkout
* [x] local startup UX and help text explain the v0.6 source-checkout boundary

### v0.6.0 Status Notes

This milestone is intentionally small and scoped to developer ergonomics. It does not change the collector protocol, warning engine behavior, or span schema.

Validated results:

* `python -m pip install -e .` succeeded
* `sledtrace --help` displayed the CLI usage
* `sledtrace version` printed `0.6.0`
* `pytest -q` passed with 17 tests in `sdk/python`; output included the expected legacy-import deprecation warning and an environment-specific `.pytest_cache` permission warning
* `python -m build` succeeded
* `python scripts/validate-wheel.py` passed all import and installed-CLI checks
* `go test ./... -count=1` passed in `collector/go`
* `npm.cmd run build` passed in `dashboard/web`

The Python wheel intentionally does not bundle the Go collector, dashboard, Docker images, or platform-specific runtime assets. Standalone wheel-installed serving is outside v0.6.0 scope.

Release outcome:

* release commit `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e`
* annotated tag `v0.6.0`
* GitHub Release published on 2026-09-08
* release hygiene removed tracked Python bytecode/cache artifacts
* no PyPI publication

---

### v0.5.0 Goal

Prepare the Python SDK for clean local distribution as an installable package:

* package metadata aligned to SledTrace-first naming
* wheel and sdist build validation from `sdk/python`
* public import path `sledtrace` remains clean and importable
* temporary legacy `raglens` compatibility preserved for migration
* `SLEDTRACE_COLLECTOR_URL` precedence validated with legacy fallback
* local wheel validation script and compatibility tests added

### v0.5.0 Scope

* [x] package metadata ready for wheel/sdist build
* [x] `python -m build` succeeds from `sdk/python`
* [x] local wheel install succeeds in clean venv
* [x] `import sledtrace` works
* [x] `from sledtrace import trace` works
* [x] `import raglens` compatibility remains available during migration
* [x] `SLEDTRACE_COLLECTOR_URL` precedence works
* [x] README and release docs updated for packaging

### v0.5.0 Status Notes

This milestone is intentionally limited to packaging and compatibility readiness. It does not change the warning engine, collector API, storage schema, dashboard data contract, or span type set.

Validated results:

* `python -m build` succeeded and produced wheel + sdist artifacts
* clean venv install from the built wheel succeeded
* `sledtrace.__version__` is available
* `from sledtrace import trace` works
* legacy `raglens` import still works as a temporary compatibility shim
* `pytest` passed in `sdk/python`
* collector Go tests passed
* dashboard build passed

v0.5.0 is complete and remains the current packaging baseline.

---

### v0.4.1 status

**Historical release:** v0.4.1 - Rebrand
**Status:** Completed and smoke-tested

SledTrace has completed the local inspection loop for both the built-in demo and user-owned Python RAG pipelines, and is now upgrading the warning layer into evidence-backed diagnostics:

```text
Python SDK
  ->
Go Collector
  ->
SQLite
  ->
React Dashboard
```

Current implemented span types:

* `retrieval`
* `llm`

Current warning rules:

* `no_retrieved_chunks`
* `low_retrieval_score`
* `duplicate_chunks`
* `weak_query_chunk_overlap`
* `conflicting_chunks`
* `answer_not_grounded`
* `numeric_mismatch`

Current v0.3.5 hardening highlights:

* numeric expression range handling supports both hyphen and natural-language ranges
* conflicting chunk selection is query/answer relevance-aware and deterministic
* conflicting chunk topic gating reduces cross-topic numeric noise
* thin reference integration app validates mixed raw retrieval output normalization
* deterministic-first behavior retained, with optional real LLM validation path

Completed foundation highlights:

* `docs/product/USER_ONBOARDING.md`
* `docs/integrations/PYTHON_SDK_GUIDE.md`
* `sdk/python/examples/custom_pipeline_demo.py`
* `scripts/start-sledtrace.py`
* README two-path quickstart for demo usage and real integration
* README documentation map for users and maintainers
* SDK packaging hygiene (`sdk/python` version `0.2.0`, local SDK README, local editable install path)
* integration smoke test validation through the dashboard
* v0.3 diagnostic intelligence design spec in `docs/product/V0_3_DIAGNOSTIC_INTELLIGENCE.md`
* v0.3 diagnostic quality demo cases for numeric mismatch, weak overlap, unsupported claim, and conflicting chunks
* evidence-backed warning detail UI with compared-value and recommended-action blocks
* v0.3.5 reference integration app and policy corpus under `sdk/python/examples/reference_rag_app/`

Current v0.4.1 rebrand highlights:

* active project branding renamed to SledTrace
* compatibility wrapper retained at `scripts/start-raglens.py`
* new preferred collector env var `SLEDTRACE_COLLECTOR_URL` with legacy fallback
* migration guide at `docs/REBRANDING.md`
* release notes at `docs/releases/V0_4_1.md`

Current v0.4.0 release-readiness highlights:

* Docker Compose local stack for collector + dashboard
* collector and dashboard Dockerfiles
* root `.env.example`
* first-run smoke-test and reset guidance
* release notes and README quickstart consolidation

---

## v0.1 -Local RAG Debugger MVP

**Status:** Done

### Goal

Let a developer trace a RAG pipeline, store traces locally, and inspect the pipeline in a browser UI.

### Scope

#### Core tracing and ingestion

* [x] Python SDK
* [x] Trace context manager
* [x] Retrieval span logging
* [x] LLM call span logging
* [x] Trace payload generation
* [x] SDK `flush()` to local collector
* [x] Refund policy demo
* [x] Real local RAG demo using local documents, deterministic chunking, and TF-IDF retrieval

#### Collector and local storage

* [x] Go collector
* [x] `GET /health`
* [x] `POST /api/traces`
* [x] `GET /api/traces`
* [x] `GET /api/traces/{trace_id}`
* [x] SQLite storage
* [x] Trace persistence
* [x] Span persistence
* [x] Warning persistence

#### Dashboard

* [x] Trace list page
* [x] Trace detail page
* [x] Retrieved chunks viewer
* [x] LLM prompt / response viewer
* [x] Warning cards in trace detail
* [x] Demo-friendly trace list labels
* [x] Improved warning card readability
* [x] Responsive trace detail layout polish

#### Warning engine

* [x] `no_retrieved_chunks`
* [x] `low_retrieval_score`
* [x] `duplicate_chunks`
* [x] `conflicting_chunks`
* [x] simplified `answer_not_grounded`

### Validation

v0.1 smoke test passed.

Verified:

* collector starts successfully
* dashboard starts successfully
* local RAG `trace-all` runs successfully
* demo traces appear in dashboard
* warning cards render in trace detail
* retrieved chunks, scores, prompt, response, and warnings are inspectable
* expected warning-focused demo cases generate warnings

---

## v0.2 -Developer Integration / Local SDK Onboarding

**Status:** Done

### Goal

Make it clear how a developer can use SledTrace with their own RAG pipeline instead of modifying the built-in local demo.

The built-in `local_rag_demo` is a deterministic proof demo and smoke-test fixture. Real users should instrument their own retrieval and LLM calls with the SledTrace Python SDK.

### Completed Core Scope

#### User onboarding docs

* [x] `docs/product/USER_ONBOARDING.md`
* [x] Explain SledTrace as a local-first debugging/observability layer for RAG pipelines
* [x] Explain that real users do not modify the built-in demo for production usage
* [x] Explain how users instrument their own RAG pipeline
* [x] Explain what data SledTrace expects today

#### Python SDK integration guide

* [x] `docs/integrations/PYTHON_SDK_GUIDE.md`
* [x] local editable install instructions
* [x] `SLEDTRACE_COLLECTOR_URL` configuration
* [x] `trace()` basics
* [x] Retrieval span example
* [x] LLM span examples
* [x] `flush()` behavior
* [x] Common mistakes and troubleshooting

#### Custom pipeline example

* [x] `sdk/python/examples/custom_pipeline_demo.py`
* [x] Show how to instrument a user-owned retrieval pipeline
* [x] Keep the example local and deterministic
* [x] Avoid LangChain, LlamaIndex, OpenAI, Anthropic, and other external APIs

#### Unified local startup path

* [x] `scripts/start-sledtrace.py`
* [x] Cross-platform repo-local startup helper
* [x] Recommended local startup flow documented in README and SDK guide
* [x] Existing PowerShell and macOS script paths preserved as shortcuts/fallbacks

#### README integration path

* [x] Two-path quickstart in `README.md`
* [x] Path A: built-in demo validation flow
* [x] Path B: integrate the SDK into your own Python RAG app

### Smoke-Tested Validation

The following commands passed during v0.2 integration validation:

```bash
python scripts/start-sledtrace.py
cd sdk/python
python -m examples.custom_pipeline_demo
python -m examples.local_rag_demo.run_demo trace-all
```

Validated results:

* dashboard confirmed `custom-rag-pipeline`
* dashboard confirmed built-in local RAG demo traces
* dashboard confirmed warning-focused demo cases
* custom pipeline demo flushed successfully through the local collector

### Explicitly Not Completed in v0.2

Future work, not current v0.2 completion:

* Docker Compose local setup
* packaged CLI
* PyPI publishing
* raw LLM provider examples
* LangChain adapter
* LlamaIndex adapter
* LLM-assisted diagnostics

### Out of Scope

Not part of current v0.2 implementation:

* tool spans
* memory spans
* verification spans
* human feedback spans
* agent tracing
* cloud sync
* auth
* hosted collector
* full LLM-as-judge grounding evaluator

---

## v0.3 -RAG Quality Analysis / Diagnostic Intelligence

**Status:** Core implemented and smoke-tested

### Goal

Upgrade warnings from simple flags into evidence-backed diagnostics.

### Scope

* [x] warning schema v2
* [x] evidence-backed warning details
* [x] diagnostic object design
* [x] improved `answer_not_grounded` heuristics
* [x] weak query/chunk overlap diagnostics
* [x] numeric mismatch diagnostics
* [x] conflict detection v2
* [x] dashboard warning detail improvements
* [x] diagnostic quality demo cases

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

### Out of Scope

Not part of this milestone:

* LangChain / LlamaIndex
* PyPI / Docker / CLI
* agent/tool/memory spans
* LLM-as-judge default path
* cloud sync
* auth
* hosted collector

These remain intentionally outside the v0.3 local-first deterministic-first path.

---

## v0.3.5 -Diagnostic Quality Hardening

**Status:** Done

### Goal

Harden deterministic warning quality on realistic integration traces without introducing LLM-as-judge or changing core trace/storage contracts.

### Scope

* [x] natural-language numeric range extraction in warning engine
* [x] conservative numeric mismatch behavior preserved for elapsed-time and directly-supported values
* [x] relevance-aware conflicting chunk candidate selection
* [x] deterministic topic classifier for numeric conflict candidate gating
* [x] expanded warning-engine tests for range and relevance behavior
* [x] thin reference RAG integration app with mixed raw retrieval output normalization
* [x] deterministic answer cleanup for lower avoidable grounding-noise in demo traces

### Validation

```bash
cd collector/go
go test ./... -count=1

cd sdk/python
python -m examples.reference_rag_app.run all
python -m examples.reference_rag_app.run processing-range
python -m examples.reference_rag_app.run wrong-processing-range
python -m examples.real_llm_rag_demo all
```

### Out of Scope

* storage schema changes
* dashboard UI/schema changes
* SDK trace API changes
* LLM-as-judge or non-deterministic warning evaluation

---

## v0.4 -Packaging and External Developer Experience

**Status:** Done

### Goal

Make SledTrace easier for an external developer to run locally from a fresh checkout.

### Scope

* [x] Docker Compose for collector + dashboard
* [x] `.env.example`
* [x] startup health checks and guidance
* [x] local database reset guidance (Docker and non-Docker)
* [x] clearer first-run setup
* [x] README quickstart polish
* [x] release notes and docs pass
* [x] optional local `scripts/check-raglens.py` health script

### Validation Gate

Required before marking complete:

* `cd collector/go && go test ./... -count=1`
* `cd dashboard/web && npm run build`
* `docker compose up --build`
* `curl http://localhost:4319/health`
* `cd sdk/python && pip install -e . && python -m examples.reference_rag_app.run all`

Validated on 2026-07-15:

* all commands above passed
* `GET /api/traces` contained all expected `reference-rag-app-*` trace names
* Docker cleanup commands passed:
  * `docker compose down`
  * `docker compose down -v`

### Out of Scope

* hosted collector
* auth
* cloud sync
* paid SaaS features
* LLM-as-judge default evaluator
* agent/tool/memory spans
* LangChain/LlamaIndex adapters unless explicitly selected
* PyPI publishing unless explicitly selected

---

## Future -Agent Harness Observability (TraceForge Direction)

**Status:** Future

Potential future direction after current milestones:

* running traces for multi-step agent/harness executions
* partial span ingestion for long-running or interrupted runs
* future span types such as `agent`, `tool`, and `retry`
* diagnostics for agent loops
* diagnostics for oscillation between states/actions
* diagnostics for retry storms
* diagnostics for no-progress execution

Important scope note:

* none of the above is implemented in current SledTrace
* this direction is not part of v0.6.0 or any completed milestone



