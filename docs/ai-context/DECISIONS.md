# Architecture Decisions

## 2026-09-09 — Close v0.7.0 only after protected publication and clean-index validation

### Decision

Declare v0.7.0 External Developer Readiness complete after the protected pull request and required checks pass, the immutable `v0.7.0` tag publishes through the approval-gated `pypi` environment, a no-cache install from production PyPI succeeds outside the repository, and the GitHub Release is published.

Keep the release tag fixed at `58887907973aff3948d2cf3667681832f4305ec6`. Record later documentation closure in a separate protected pull request rather than moving or rebuilding the released artifact.

### Reason

- package upload success alone does not prove that ordinary users can install the published artifact
- keeping the tag immutable preserves release provenance
- separating post-release documentation from the release artifact avoids silently changing published package contents

### Outcome

- pull request #1 merged after `Python 3.9`, `Python 3.13`, `Go Collector`, and `Dashboard` passed
- production publishing workflow https://github.com/Schromeo/SledTrace/actions/runs/34410674101 completed successfully
- `sledtrace==0.7.0` installed from production PyPI in a clean environment outside the source repository
- preferred and legacy imports, CLI help/version, and the expected out-of-checkout `serve` failure path passed
- GitHub Release https://github.com/Schromeo/SledTrace/releases/tag/v0.7.0 was published
- external first-run evidence, Docker validation on a suitable host, and dependency-advisory review remain post-release inputs to the next milestone

---

## 2026-09-09 — Separate project-release blockers from post-release adoption evidence

### Decision

Before declaring the project-wide v0.7.0 External Developer Readiness milestone complete, require protected `main` checks, one current clean-clone first run, browser-visible deterministic diagnostics, accurate public screenshots, contributor entry points, a release checklist, and production PyPI clean-install validation.

Treat two independent external first-run attempts and a small public issue backlog as post-release evidence rather than blockers for the first production package. Do not create synthetic issues to make the repository appear active.

Accept the non-Docker clean-clone path as the v0.7 runtime evidence on the current Windows host because Docker Desktop reported that WSL2 virtualization was disabled. Document that prerequisite honestly; do not represent the Docker path as freshly validated.

### Reason

- the v0.7 name promises an author-independent, trustworthy path, so repository protection, complete instructions, and visible runtime evidence are part of the project release—not cosmetic follow-up
- production PyPI availability is needed before most external developers can try the canonical installation path
- external participation cannot be manufactured or guaranteed before release
- the current README screenshots contained old RAGLens branding and paths, so refreshing them corrects public product evidence without changing Dashboard behavior

### Outcome

- `main` requires `Python 3.9`, `Python 3.13`, `Go Collector`, and `Dashboard` checks, applies to administrators, requires linear history and resolved conversations, and disallows force pushes and deletion
- final v0.7 work proceeds through `release/v0.7.0` and a protected pull request
- the clean-clone non-Docker path explicitly includes `npm ci` and an SDK install before startup and trace generation
- external first-run attempts, Docker smoke automation, dependency-advisory work, and a real evidence-backed issue backlog remain visible post-release work

## 2026-09-08 — Use v0.7.0 and OIDC Trusted Publishing for the first PyPI release

### Decision

Target v0.7.0 as SledTrace's first production PyPI release. Do not retroactively upload or rebuild v0.6.0: the immutable v0.6.0 package README correctly records that PyPI publication had not occurred, and rebuilding that version with different publication metadata would weaken release provenance.

Publish through a manually dispatched GitHub Actions workflow using PyPI Trusted Publishing and short-lived OIDC credentials. Default the workflow to validation only, require an explicit TestPyPI or PyPI target, and require the selected `v`-prefixed tag to match the package version. Validate through TestPyPI before the production PyPI decision.

### Reason

- package index publication is the shortest path to the user-visible `pip install sledtrace` outcome
- v0.6.0 is already an immutable GitHub release with historically accurate non-PyPI documentation
- OIDC avoids storing a long-lived PyPI API token in GitHub secrets
- manual target selection and version/tag matching reduce accidental or mismatched publication risk
- a validate-only path proves artifact construction without requiring package-index credentials

### Outcome

- `publish-python.yml` has separate validate, TestPyPI, and PyPI paths
- publishing actions are pinned to verified commits and only selected upload jobs receive `id-token: write`
- package metadata, README rendering, project URLs, and included license text are validated
- the first remote validate-only run passed and did not upload a package
- the TestPyPI pending Trusted Publisher is registered for `Schromeo/SledTrace`, workflow `publish-python.yml`, environment `testpypi`
- tagged candidate `v0.7.0rc1` was published through Trusted Publishing and clean-installed from the public TestPyPI index outside the source repository
- the production PyPI pending Trusted Publisher is registered against GitHub environment `pypi`
- the `pypi` environment requires approval from `Schromeo`, allows self-review for the single-maintainer workflow, blocks branch deployments, and allows only tags matching `v*`
- the final `0.7.0` scope and production publication remain explicit go/no-go decisions

---

## 2026-09-08 — Establish independent cross-stack CI as the v0.7 baseline

### Decision

Run the Python SDK/package, Go Collector, and Dashboard validations as independent GitHub Actions jobs on pushes to `main` and on pull requests.

Test the Python package on both the declared minimum Python version, 3.9, and the current development version, 3.13. Run package build and clean-wheel CLI validation in both matrix jobs so the supported import, compatibility, and startup-boundary contracts are exercised from built artifacts.

Keep Docker first-run smoke validation and branch-protection enforcement as explicit follow-up work instead of representing them as part of the initial CI baseline. Do not make `npm audit` a failing CI gate until the current transitive development-dependency baseline is deliberately updated and validated.

### Reason

- independent jobs make failures visible by stack and allow them to run concurrently
- testing the minimum and current Python versions catches both compatibility drift and local-development regressions
- built-wheel validation protects the distribution surface that editable-install tests alone do not cover
- Docker smoke and required-check enforcement have different operational risks and deserve their own validation steps
- introducing a failing security gate before resolving the known baseline would make CI permanently red without improving safety

### Outcome

- `.github/workflows/ci.yml` is the repository CI entry point
- the first remote run passed Python 3.9, Python 3.13, Go Collector, and Dashboard validation
- the root README exposes the live CI status
- dependency advisories, Docker smoke validation, and branch protection remain visible v0.7 work rather than hidden or overstated completion

---

## 2026-09-08 — Select v0.7 External Developer Readiness after releasing v0.6

### Decision

Treat v0.6.0 as fully released and make **v0.7.0 — External Developer Readiness** the next planned milestone.

Define v0.7 around trustworthy repository automation, verifiable clean-clone first run, contributor entry points, and user-visible validation evidence. Do not treat repository cosmetics or a large synthetic issue backlog as proof of adoption.

Make PyPI publication an explicit high-priority decision gate for v0.7 without claiming that `pip install sledtrace` works before publication and clean-install validation succeed.

For dashboard-facing work, automated tests and production builds remain required, but completion also requires practical visual evidence when the environment supports it. Conversation screenshots should be produced at UI checkpoints; README screenshots should change only when the visible product or onboarding flow materially changes.

### Reason

- v0.6 completed the local CLI and startup UX boundary and was published successfully.
- SledTrace has a coherent local RAG debugging loop, but external developers still lack CI signals and a proven author-independent first-run path.
- Adoption is an observed outcome, while readiness can be implemented and measured.
- PyPI distribution may remove more onboarding friction than premature framework adapters, but publication requires an explicit security, ownership, and support decision.
- Dashboard build success does not prove that the real product state is readable or usable.

### Outcome

- v0.6.0 remains the current released version.
- v0.7 begins with CI and clean-clone validation rather than new product surface.
- external first-run evidence will inform later framework, distribution, diagnostic, or eval work.
- LangChain/LlamaIndex adapters, new spans, cloud/auth, and LLM-as-judge remain unselected future work.
- the root README remains the visual showcase; the SDK README is kept package-metadata friendly without duplicating Dashboard screenshot assets.

---

## 2026-09-07 — v0.6 CLI remains source-checkout based for serving

### Decision

Ship the `sledtrace` console entry point in the Python package, while keeping `sledtrace serve` explicitly tied to a SledTrace source checkout for v0.6.0.

The CLI locates a checkout by walking upward from the current working directory and requiring these markers:

- `AGENTS.md`
- `docker-compose.yml`
- `scripts/start-sledtrace.py`

Inside a checkout, `serve` delegates to the existing startup script. Outside a checkout, it exits non-zero with actionable guidance.

### Reason

- The existing startup script already owns the local Collector and Dashboard lifecycle.
- Bundling Go, Node, Docker, or platform-specific runtime assets into the Python wheel would materially expand packaging complexity.
- Wheel users still benefit from a valid CLI entry point, help, version reporting, and an explicit support boundary.

### Outcome

- Python package and CLI version are `0.6.0`.
- `sledtrace --help`, `sledtrace serve --help`, and `sledtrace version` work after wheel installation.
- Standalone wheel-installed serving is not supported in v0.6.0.
- No collector protocol, storage schema, dashboard data contract, warning rule, or span-type changes were introduced.

---

## 2026-07-06 - v0.3 diagnostic intelligence remains local-first and deterministic-first

### Decision

Define v0.3 diagnostic intelligence around structured warning evidence and deterministic heuristics over the existing `retrieval` and `llm` spans.

### Reason

- The next product step should make warnings explainable before adding more infrastructure or integrations.
- Deterministic local diagnostics are inspectable in the dashboard and easier to trust during debugging.
- The current trace model is sufficient for a first evidence-backed warning system without adding agent, tool, or memory span families.

### Outcome

- v0.3 scope centers on Warning Schema v2, EvidenceItem, DiagnosticObject, and five first enhanced warning rules.
- v0.3 explicitly excludes cloud, auth, LangChain, LlamaIndex, Docker, CLI, PyPI, and LLM-as-judge work.
- Current implemented span types remain `retrieval` and `llm` only for this milestone.

---

## 2026-05-14 — Start with RAGLens instead of full TraceForge

### Decision

Start with RAGLens, a local-first visual debugger for RAG pipelines.

### Reason

A full AI observability platform is too broad for the first version. A focused RAG debugging tool has a clearer user pain point and a better chance of being useful to developers.

### Alternatives Considered

- Full AgentOps platform
- AI Gateway with semantic cache
- Multi-agent PR reviewer
- Generic LLM evaluation framework

### Outcome

RAGLens will be the first product cut.

The long-term platform vision remains TraceForge.

---

## 2026-05-14 — Use local-first development as the MVP principle

### Decision

RAGLens v0.1 should run locally with minimal setup.

### Reason

Community adoption is more likely if users can try the tool quickly without signing up for a cloud service or deploying complex infrastructure.

### Outcome

The MVP should prioritize:

- Simple install
- Local collector
- Local storage
- Local dashboard
- Example app

# Decisions

## 2026-05-14

### RAGLens starts as a local-first RAG debugger

RAGLens v0.1 will focus on helping developers understand why a RAG pipeline produced a bad answer.

It will not start as a full LLM observability platform.

### Trace/span model will be designed with future AgentOps support

The initial data model will use traces and spans.

A trace represents one complete RAG request.

A span represents one step inside the pipeline, such as retrieval, prompt construction, or LLM generation.

This keeps v0.1 narrow while preserving a path toward broader agent tracing later.

### Local storage will use SQLite

RAGLens v0.1 will use SQLite for local-first storage.

This keeps setup simple and avoids requiring developers to run external infrastructure.

### v0.1 span types

> Superseded historical proposal: although the initial design listed `prompt` and `custom`, the implemented and currently supported span types were narrowed to `retrieval` and `llm`. See the 2026-07-06 decision above and current repository contracts.

The initial supported span types are:

- retrieval
- prompt
- llm
- custom

Additional span types such as tool_call, agent_step, memory_read, rerank, and eval may be added later.

## Warning engine will live in the Go collector for v0.1

The v0.1 warning engine will run inside the Go collector.

Reason:

- The collector receives the full trace payload.
- The collector owns SQLite persistence.
- Warnings should be generated consistently regardless of which SDK sends traces.
- The Python SDK should stay lightweight and focus on instrumentation.
- The React Dashboard should only display warnings, not generate them.

The initial warning engine will use simple heuristic rules.

The first target warning is `conflicting_chunks`, demonstrated by the refund policy demo where retrieved chunks contain both `30 days` and `14 days` refund windows.

## Dashboard before warning engine

RAGLens built the dashboard before the warning engine.

Reason:

The SDK → Collector → SQLite path was already working, and a visual inspection UI makes the product easier to validate.

Having the dashboard first also gives warning rules a visible place to appear once implemented.

## 2026-06-13 — Warning rules ship incrementally in v0.1

The warning engine is now active in the Go collector and runs after trace persistence.

For v0.1, warning rules should be shipped incrementally instead of waiting for a full rule set.

Reason:

- It validates the full diagnosis loop early: ingestion -> warning generation -> SQLite -> API -> dashboard card rendering.
- It reduces delivery risk by keeping each rule small and testable.
- It keeps the product local-first and simple while still delivering visible debugging value.

Current baseline:

- First live rule: `conflicting_chunks`
- Demo validation: refund policy chunks with conflicting `30 days` and `14 days` windows generate one warning end-to-end.

---

## 2026-06-15 — Diagnosis Layer MVP marked complete

### Decision

Mark the Warning Engine / Diagnosis Layer MVP as complete for v0.1.

### Reason

The local end-to-end loop is validated:

- Python SDK `trace()` instrumentation and `flush()`
- `POST /api/traces` ingestion on collector `:4319`
- SQLite persistence for traces, spans, and warnings
- warning generation in collector
- `GET /api/traces/{trace_id}` returns warning records
- React dashboard renders real warning cards

Implemented warning rules in MVP:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- `conflicting_chunks`
- simplified `answer_not_grounded`

### Outcome

Shift active focus from warning rule expansion to Real Local RAG Demo.

---

## 2026-06-15 — Sequence real retrieval before framework adapters

### Decision

Do Real Local RAG Demo before adding LangChain/LlamaIndex adapters.

### Reason

- Need to validate schema and warning quality on real retrieval outputs first.
- Keep MVP local-first and transparent.
- Avoid adding adapter complexity before core behavior is proven.

### Outcome

Next milestone scope:

- local docs
- simple chunking
- transparent local retrieval (TF-IDF + cosine, or sentence-transformers + cosine)
- SDK instrumentation and warning validation on real retrieval traces

---

## 2026-06-22 — Dashboard UI: Inline Final answer with text truncation

### Decision

Move Final answer from floating fixed-position window to grid layout alongside Query/Duration/Warnings.
Add text truncation in sidebar to keep trace card heights uniform.
Use CSS `resize: vertical` for inline answer card expansion/collapse.

### Reason

- Fixed floating window disrupted page layout flow and was not discoverable in all viewport sizes.
- Long answer text in sidebar trace cards caused cards to grow unpredictably, breaking visual consistency.
- Users expect grid layout consistency across summary cards (all at same height unless explicitly resized).
- Inline resizing is more intuitive than separate modal or floating window.

### Outcome

**Trace list (sidebar):**
- Query field: max 2 lines, ellipsis overflow
- Answer field: max 3 lines, ellipsis overflow
- Result: uniform card heights regardless of content length

**Trace detail (main):**
- Final answer: inline scrollable card in 4-column grid
- Default height: min 92px, max 320px
- User can drag bottom edge to resize vertically
- Content area scrolls independently

Effect:
- Sidebar is predictable and scannable
- Detail view grid remains balanced (Query / Answer / Duration / Warnings all in one row)
- No out-of-page floating elements
- Responsive to different answer lengths
