# Architecture Decisions

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
