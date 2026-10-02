# AGENTS.md

## Working principle

每次只完成当前任务；按变更范围验证；结果有证据；发现范围外问题则报告，不自动扩展；满足验收条件后停止。

## Product and boundaries

SledTrace is a local-first debugger for RAG and explicitly instrumented AI
workflows. Agent direction: failure localization and outcome-aware improvement
verification, NOT an Agent runtime or hosted LLMOps platform. Python remains the
main SDK; a selected cross-language testbed does not imply generic JS support.
Current implementation/release facts belong in AI_HANDOFF, not this standing file.

Architecture: Python explicit trace/flush → Go Collector → deterministic
diagnostics → SQLite → React/TypeScript Dashboard.
Preserve retrieval/llm/caller-instrumented synchronous tool spans, existing RAG
behavior, sledtrace/SLEDTRACE_COLLECTOR_URL preferences and documented
raglens/RAGLENS_COLLECTOR_URL compatibility. No compatibility removal by cleanup.

## Read and authority

For a small, explicitly described task, read this file and the files you will
change; read CURRENT_TASK only when the task is the active slice. When taking over
a stage or choosing what to do next, read NEXT_AGENT_BRIEF, then CURRENT_TASK,
AI_HANDOFF and ROADMAP. Read DECISIONS or ROAD_TO_V1_0 sections only for the
architecture or stage choice at hand. DEVLOG and *_HISTORY_* files are lookup
material, not default reading.
Latest human instructions govern; archived next actions and plan text are not
authorization. Standing rules do not override newer verified implementation facts.

CURRENT_TASK owns one selected slice and its acceptance. AI_HANDOFF owns current
facts/risks/entry points. ROADMAP owns milestone status and candidate sequence.
ROAD_TO_V1_0 owns product goals/gates. DECISIONS owns durable rationale;
DEVLOG owns execution history. NEXT_AGENT_BRIEF is stable navigation.
Keep active documents short; archive history with working links and evidence.

Implementation uses .agents/skills/sledtrace-slice/SKILL.md; review uses
.agents/skills/sledtrace-review/SKILL.md. Use existing scripts/dev/slice.py
status/scope/check and authoritative profiles, not a new workflow framework.
Preserve dirty/unmerged prerequisites; scope permission does not authorize
changing every inherited path. `slice.py scope` reports everything changed since
scope_base, including uncommitted earlier slices; do not build extra hash
inventories or custom scanners to prove the increment. If uncommitted slices are
piling up, tell the user and suggest a commit point instead.

## Before selecting an implementation

State a compact card: user result, confirmed blocker, reusable capability,
smallest patch, non-goals, proportional validation, visible evidence and stop.
Compare a smaller evidence/reproduction route before new capture or infrastructure.
Do not implement until it is a coherent shortest path to the requested result.

WIP=1; normally 0.5–3 effective days. Completion stops at validated documented
review-readiness, not automatic next-slice implementation. Public API/schema/
span-family, cross-repo, release/security actions and paid calls require the
corresponding human decision; ordinary authorized details do not need reapproval.
Never infer authorization to commit/push/merge/publish from docs cleanup.

## Parent milestone and anti-loop rules

Keep the parent milestone exit and initial budget fixed while splitting work.
Preflight, capture and readback count toward that goal; new slice IDs do not reset
the budget. Record actual effort/known cumulative effort with an explicit unknown
historical portion. Never invent time or declare a milestone done from slice count.

Near twice the initial budget, or two slices without visible user outcome,
stop scope growth and reassess. A failing check gets at most one targeted fix
and one rerun. The same failure without new evidence ends the attempt: report it as introduced here, confirmed
pre-existing, environment limit or unknown (do not guess pre-existing), and mark
the task incomplete if it affects correctness.
Two real scenarios without actionable value require narrowing, not more adapters.
Safety and necessary verification are not optional under these stop rules.

At acceptance, stop. Record non-blocking discoveries instead of following them.
Keep/revert/inconclusive are valid experiment findings; inconclusive leaves the
product gate open. Do not manufacture success through repeated tests or screenshots.

## Diagnostic and scope guardrails

Unknown is not zero; equal tool output is not proven waste; cheaper is not better;
estimated USD is not provider billing. Separate call/provider, application
contract, workflow, manual assessment and unevaluated quality. Parent nesting,
time order and a source error code do not establish causal root cause.
No private chain-of-thought, secrets or unapproved private artifacts in traces.

D1 is required by the detailed plan; D2/D3 conditional, with no warning quota.
Existing RAG rules keep retrieval applicability. Use offline branches for
validators, counterexamples/holdouts for heuristics, actual comparisons for
outcome claims. Fixed testbeds are MAMR, pinned PydanticAI and existing RAG;
do not seek a third framework to postpone a value decision.
MAMR is the observed workflow; read its own instructions before authorized edits.
Capture at source is not live Collector streaming. Historical budgets are not
standing API authority.

No cloud/auth/billing/multi-tenancy, Kafka/Kubernetes/ClickHouse, new span families,
broad framework adapters, LLM-as-judge, unrelated rules or breaking SDK/data
contracts unless the selected milestone and human authority require them.
Prefer existing components, explicit behavior and bounded changes over abstractions.

## Validation

Daily development and release acceptance are separate. Daily: run targeted
tests while working, then the changed component's checks below once at the end
(`slice.py check` with the slice's profile). Release: the `release` profile and
RELEASE_CHECKLIST, only when the user asks to prepare a release. Do not rerun
unchanged components, repeat a passing check, or call old results a fresh pass.

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

For Dashboard changes whose acceptance depends on what the user sees, also do a visual check when practical:

1. start the real local Collector and Dashboard
2. generate deterministic reference traces
3. open the Dashboard and inspect the affected flows
4. provide user-visible screenshots or an interactive browser view
5. distinguish automated-test evidence from visual acceptance evidence

Screenshot policy:

- one screenshot of the changed view is enough; skip it when no visible behavior changed
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

## Closeout and document ownership

Closing a slice: review the diff once against the acceptance criteria, run its
validation, add one short DEVLOG entry (commands, results, limits) and set
CURRENT_TASK status/outcome. Do not draft the next slice or decision card unless
the user asks; listing open issues is enough. ROADMAP changes only when a
milestone status changes. Record failures and limits; do not advance product
gates to finish a checklist.
Update AI_HANDOFF only when facts/risks/contracts change; DECISIONS only for a
durable choice; detailed plan only for product/stage decisions. README/releases
change when usable behavior/publication changes, not to advertise proposals.
Archive replaced active history instead of appending it into CURRENT_TASK.
Keep local validation, committed, pushed, merged, released and real-user value
distinct. Commits/publication remain separately authorized.

Reply in Chinese unless asked for English. Explain assumptions and evidence;
do not ask the user to repeat already authorized routine details.
Use bounded relevant checks. Known Docker/WSL limitations do not justify
repeated startup retries or changes to the user's system for unrelated work.


