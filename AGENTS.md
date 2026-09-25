
# AGENTS.md

## Project

SledTrace is an open-source, local-first observability and debugging tool for RAG pipelines.

Former project name: RAGLens.

Current stable project direction is SledTrace-first. Legacy RAGLens compatibility may remain temporarily where explicitly documented.

Current released version: **v0.7.1 — Trustworthy Local Tracing**, published from immutable tag `v0.7.1` on 2026-09-25. The protected PyPI workflow succeeded, and the wheel was installed from production PyPI in a clean virtual environment outside the repository.

Current development focus: **a bounded execution-efficiency path to v1.0**, adopted for incremental development by the user on 2026-09-15. v0.7.1 includes the reliability work, B1/B2/H0 integration, D0 harness, E1 usage visibility, E2's single Python tool path, X1 external-corpus exercise, X2 legacy-warning read fix, and E3's explicit offline-validated OpenAI Responses usage helper with indicative pricing. The published v0.7.1 release used offline E3 fixtures; a later draft PR #16 public-corpus example completed one paid Responses call with local Collector and Dashboard readback. The user accepted that one answer, not a general agent diagnostic; billing remains unreconciled. Later comparison/runtime capabilities remain candidates, not blanket authorization.

The Python package is published on production PyPI as `sledtrace==0.7.1`; its wheel and sdist are available. A clean external virtual environment installed the wheel, imported `sledtrace`, `raglens`, and `sledtrace.openai`, and verified CLI version/help plus the documented nonzero out-of-checkout `serve` guidance. `0.7.0rc1` remains on TestPyPI as historical candidate provenance.

## Before Doing Meaningful Work

Always read these files first:

1. `docs/ai-context/NEXT_AGENT_BRIEF.md` when taking over this work
2. `docs/ai-context/AI_HANDOFF.md`
3. `docs/ai-context/CURRENT_TASK.md`
4. `docs/ai-context/ROADMAP.md` current snapshot and proposed sequence

Read `docs/ai-context/DECISIONS.md` before making architecture decisions.

For roadmap selection, read the overview and relevant slice of
`docs/product/ROAD_TO_V1_0.md`. Its detailed future plan does not override the
current implementation facts or authorize the entire plan. Do not reread all
historical milestones before every small change.

Use the repository and these documents as the source of truth.
Do not assume old milestone information from this file overrides the current AI context documents.

For implementation, use `.agents/skills/sledtrace-slice/SKILL.md` and the active
CURRENT_TASK metadata. Use `python scripts/dev/slice.py status`, `scope`, and
`check` instead of rediscovering validation commands. For review, use
`.agents/skills/sledtrace-review/SKILL.md`. The skills contain workflow detail;
keep this standing file concise.

CURRENT_TASK owns the next slice and its acceptance criteria. AI_HANDOFF owns the current snapshot and known findings. ROADMAP owns candidate sequencing; DECISIONS owns rationale; DEVLOG owns historical execution evidence. Avoid duplicating long release histories across active documents or rereading historical sections for every small change.

## Pre-Implementation Decision Gate

Before each implementation slice, state a compact decision card covering:

1. user value
2. the actual current blocker
3. capabilities already present in the repository
4. the smallest deliverable change
5. explicit non-goals for the slice
6. proportional validation
7. user-visible evidence

Do not start implementation until these points form a coherent shortest path to the requested outcome.

Only one CURRENT_TASK slice may be active. Implementation agents stop at a
validated, documented, review-ready state; they never automatically start the
next slice. Public API/schema/span-family changes and external/release/security
actions remain subject to CURRENT_TASK's human gates.

Keep one primary outcome per slice. Record newly discovered non-blocking work instead of following it immediately. After validation and documentation, stop and reassess the next slice rather than continuing through an old plan by inertia.

Use one active slice, normally 0.5–3 focused development days. If work approaches
twice its initial budget, or two slices produce no visible user outcome, stop
expanding scope and reassess. Two unsuccessful investigations without new evidence
require a bounded findings report, not another speculative rewrite. These limits
do not excuse skipping necessary safety checks or claiming unfinished work passed.

## Current Architecture

```text
Python SDK
  -> trace()
  -> retrieval + llm + caller-instrumented tool spans (released)
  -> flush()
  -> Go collector
  -> deterministic Warning Engine
  -> SQLite
  -> React/TypeScript dashboard
```

Current implemented span types:

- retrieval
- llm
- tool — caller-instrumented synchronous span, published in v0.7.1; this does not execute an agent

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

Use proportional validation. During development, run targeted tests; at slice
completion, run the affected component's required checks below and inspect the
real affected flow. At integration/release, validate the exact candidate across
components and distribution boundaries. Do not repeat unchanged full release
checks after a planning-only edit or call old results a fresh pass.

For documentation-only changes, check links, factual/authorization consistency,
file scope, and `git diff --check`; no product build is needed. Package README or
metadata changes that affect distributions require their package checks.

For source startup helper changes, run `python -B -m unittest discover -s scripts/tests -v`.
When Go, Node.js and Dashboard dependencies are available, also run the opt-in
`python -B scripts/tests/smoke_startup.py` to check real startup, ingestion and cleanup.

For Python SDK behavior changes, run the SDK test suite. Also run build and both
installed-package validators below when public API, packaging, imports, CLI,
serialization/integration contracts, or dependency boundaries change; they all
remain mandatory at Python release-candidate validation:

```
cd sdk/python
pytest -q
python -m build
python scripts/validate-wheel.py
python scripts/validate-independent-app.py
```

For collector changes:

```
cd collector/go
go test ./... -count=1
```

For dashboard changes:

```
cd dashboard/web
npm test
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

After a meaningful completed slice, record execution evidence once. Document
ownership determines which files need updating; do not copy the same test log
into every context file:

User-required closeout workflow (2026-09-15): every development slice ends with
code-diff self-review, proportional tests, visible evidence when applicable,
a DEVLOG entry, CURRENT_TASK updated with outcome and the next bounded decision
card, and ROADMAP progress checked/updated (including a no-sequence-change note
when appropriate). Incomplete or failed validation must be recorded as such;
never advance a milestone just to complete the checklist. Do not hand off a
completed slice without these records. Commits and publication are separate.

- update `docs/ai-context/DEVLOG.md`
- update `docs/ai-context/AI_HANDOFF.md` when the current snapshot, contracts, or known risks change
- update `docs/ai-context/CURRENT_TASK.md` at every development-slice closeout
- update `docs/ai-context/ROADMAP.md` progress at every development-slice closeout; change sequencing only when evidence warrants it
- update `docs/ai-context/DECISIONS.md` when making a meaningful architecture decision
- update `docs/product/ROAD_TO_V1_0.md` only when product assumptions, gates, or detailed sequencing change
- keep `docs/ai-context/NEXT_AGENT_BRIEF.md` a stable navigation/working-agreement entry, not a second execution log
- update release notes, root README status, and package README status when publication state changes

Keep documentation aligned with actual tested repository behavior.

## Working Style

- Respond in Chinese unless the user explicitly requests English.
- Inherit the user's already authorized scope across model changes; do not ask them to repeat context or reconfirm routine implementation choices.
- Keep review findings, proposed milestones, authorized work, and completed/validated work distinct. The 2026-09-14 continuation authorizes the selected development slice; it is not a blanket instruction to execute every roadmap item or publish a version.
- When the user continues development, use CURRENT_TASK as the default first slice and complete its decision card before editing.
- Show real product/test evidence at relevant checkpoints. Known Docker/WSL environment failure is not a reason to block unrelated SDK work.
- Use bounded investigations. Once the required checks and acceptance criteria pass, hand off the result and reassess the next slice instead of extending the scope.

Before coding:

1. complete the pre-implementation decision gate
2. inspect the relevant implementation
3. understand the current contract
4. identify the smallest safe change
5. state important assumptions

After coding:

1. run relevant tests
2. inspect failures rather than bypassing them
3. summarize files changed
4. report exact validation results
5. call out remaining limitations honestly

Do not mark work complete merely because code was written.


