# Roadmap

This roadmap is ordered by delivery sequence.

Each version includes clear scope boundaries so SledTrace stays local-first, lightweight, and useful as a developer tool.

## Current Snapshot

**Current released version:** v0.7.0 - External Developer Readiness

**Release status:** Complete, validated, tagged, published to production PyPI, and published as a GitHub Release on 2026-09-09

**Next product milestone:** v0.7.1 — Trustworthy Local Tracing is selected as the release candidate grouping for S1-S4. Local validation, clean-clone startup, release-facing metadata, screenshots, and all four required checks pass in PR #3. It is not merged, tagged, published, or released.

Release references:

* v0.5.0 tag targets `b3cad60a10636dbf7a5d371f51bac0c04a4af936`
* v0.5.0 release: https://github.com/Schromeo/SledTrace/releases/tag/v0.5.0
* v0.6.0 tag targets `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e`
* v0.6.0 release: https://github.com/Schromeo/SledTrace/releases/tag/v0.6.0
* v0.7.0 tag targets `58887907973aff3948d2cf3667681832f4305ec6`
* v0.7.0 release: https://github.com/Schromeo/SledTrace/releases/tag/v0.7.0
* production package: https://pypi.org/project/sledtrace/0.7.0/
* production publication workflow: https://github.com/Schromeo/SledTrace/actions/runs/34410674101

## Proposed post-v0.7 sequence

Status: **S1-S4 are in the open v0.7.1 candidate PR; B1 startup reliability and B2 independent-app integration are locally validated on subsequent separate branches**. Exact active-slice results belong in [CURRENT_TASK.md](CURRENT_TASK.md), and reviewed code evidence belongs in [AI_HANDOFF.md](AI_HANDOFF.md).

The proposed product outcome is: a Python RAG developer can find verifiable evidence for a bad answer and confirm the effect of a subsequent change. Shipping milestones measures readiness; external use, confirmed diagnoses, and repeat usage measure product value.

### A — Reliability candidates before broader onboarding (possible v0.7.1)

Planning budget: 3-5 focused development days, not a deadline. Release grouping/version is selected after the fixes and compatibility impact are understood.

| Order | Bounded slice | Acceptance outcome |
| --- | --- | --- |
| S1 — locally complete | Trustworthy span timing | Actual operation measurements and unmeasured records are represented honestly; existing call forms work; timeline and detail agree. See CURRENT_TASK for validation. |
| S2 — locally complete | Retrieval score semantics | Score type/direction is preserved; distance and unknown scores do not enter higher-is-better thresholds or ordering. Similarity, distance, unscored, tuple, and explicit mappings are covered without assuming `1 - distance`. See CURRENT_TASK for validation. |
| S3 — locally complete | Trace delivery policy | Strict `flush()` is preserved; explicit `try_flush()` returns an observable result without replacing business behavior. Offline/timeout/serialization and original exceptions are covered without adding retry or queue behavior. See CURRENT_TASK. |
| S4 — locally complete | Local network defaults | Host listener and Docker published ports default to loopback; allowed origins are explicit; normal SDK/UI flows pass. Container-internal listening remains compatible with Docker networking; intentional remote use has documented configuration. See CURRENT_TASK. |

Take one slice per focused PR where practical. A confirmed active exposure or data-loss issue can change the order. Do not wait indefinitely for external testers before fixing reproducible defects.

### B — Reliable First Integration (candidate v0.8)

Planning budget: 1-2 development weeks, adjusted from evidence. The milestone name and final scope are still proposals.

2026-09-14 phase decision: retain the integration outcome. B1 source startup
reliability and B2 independent-app integration are locally complete. B2 proves a
copied file against the built wheel for success, application error, and Collector
offline outcomes, and repairs installation-aware empty-state guidance. Next
prioritize trustworthy diagnostic presentation, then a fully automated
SDK-to-browser acceptance flow. Keep v0.7.1 publication separate from these
development branches.

- [x] One internally validated path starts in an independent application environment with the built SDK wheel.
- [x] A minimal integration example covers success, application failure, and Collector unavailability with explicit behavior.
- [x] Startup checks explain dependencies, occupied ports, health failures, and the actual Dashboard address.
- [x] Empty-state instructions work for the selected installation method; wheel users are not sent to unavailable example modules without checkout guidance.
- [ ] One automated end-to-end check sends a deterministic trace, opens its detail, and inspects evidence. B2 automates installed-wheel payload checks and adds manual real-browser proof, but does not mislabel that pair as browser automation.
- [ ] Record at least two independent external first-run attempts, including dependency setup time, time to first application trace, help requests, and blockers. A proposed goal is at most 10 minutes from satisfied prerequisites to the first application trace; report total setup time separately.

Two people are an initial usability sample, not proof of adoption. If they cannot be recruited promptly, internal independent-app checks can improve the product but must not be relabeled external validation.

### Optional bounded investigation — installed local runtime

The user values installing the Python package and directly seeing the product. Allow a 1-2 day feasibility budget when this is the next selected slice. Prefer investigating the existing Go Collector with embedded built Dashboard assets and a prebuilt runtime launched by the CLI; a Python backend rewrite is not assumed.

Before selecting delivery, compare platform support, artifact version/checksum verification, installation size, offline startup after installation, runtime cleanup/upgrade behavior, and maintenance cost. The exact distribution channel and CLI interface are not chosen. Changing the source-checkout-only boundary requires an explicit architecture decision and aligned package/docs/tests.

If runtime distribution exceeds the budget or obscures the first-integration goal, report the prototype/tradeoffs and split it from v0.8. Do not silently download executables or promise universal platform support through the existing pure-Python wheel.

### C — Diagnostic quality evidence

Planning budget: about one development week; data collection may overlap onboarding.

- Begin with roughly 20-30 positive/negative cross-domain cases to expose boundaries, including unsupported-language behavior. Expand toward 60-100 cases based on findings; the initial sample is not a general accuracy claim.
- Reserve evaluation cases before tuning; report per-rule false positives, false negatives, and unassessed cases with sample counts.
- Preserve deterministic execution. Current rules are not a semantic factuality evaluator, and fixed confidence values are not calibrated probabilities.
- Move honest diagnostic presentation before broader external validation: do not present uncalibrated constants as accuracy percentages. Display rule evidence and applicability clearly; an unassessed case must not imply a correct answer.
- Treat external confirmation that a warning helped fix an actual problem as stronger product evidence than more curated demo warnings.

### D — Confirming an improvement (later candidate, no version selected)

Prioritize evidence-to-chunk/span navigation, comparison of two runs for the same question, and search/pagination if users need them. Display source/answer changes alongside warnings; fewer warnings alone is not proof of a better answer. Retention/export and a full evaluation system require their own scope.

### Separate maintenance backlog

- Review and remeasure the four Dashboard dependency advisories recorded during v0.7; do not blindly run an automatic audit fix.
- Rerun Docker smoke on a virtualization-capable host; review the existing fixed amd64 build and Node-version difference before claiming broader support.
- Investigate atomic trace/span/warning persistence and duplicate submission semantics before adding delivery retries.
- Keep secrets out of shared trace evidence; any redaction/export capability needs explicit behavior and tests.

### Decision and stopping rules

After each slice, record the observed user benefit, validation, known limits, and whether the next priority changed. Do not broaden testing after required checks pass without a new change or unresolved concern. Budgets are estimates, not automatic permission to execute every slice.

Before selecting later adapters, cloud/auth, new spans, or LLM-as-judge, require a concrete user case and compare it with improving current diagnosis/installation. No v0.9 or v1.0 date is committed. A future v1.0 should be defined by reliable repeated real use and a stable supported contract, not feature count.

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



