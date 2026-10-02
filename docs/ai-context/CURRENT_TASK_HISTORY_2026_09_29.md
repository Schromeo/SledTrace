# Frozen history — before DOC1 (2026-09-29)

This is a preserved pre-cleanup snapshot, not an active task, authorization,
current implementation claim or selected next action. Historical failures,
validation results and then-current plans remain unchanged. Read the live
[CURRENT_TASK](CURRENT_TASK.md), [AI_HANDOFF](AI_HANDOFF.md) and [ROADMAP](ROADMAP.md) instead.

---

---
slice_id: P6C0
slice_status: complete
components:
  - documentation
validation_profile: docs
scope_base: a97935dd148b7223068bd2da4ec02188203fb58b
allowed_paths:
  - AGENTS.md
  - README.md
  - CONTRIBUTING.md
  - docs/ai-context/CURRENT_TASK.md
  - docs/ai-context/AI_HANDOFF.md
  - docs/ai-context/NEXT_AGENT_BRIEF.md
  - docs/ai-context/ROADMAP.md
  - docs/ai-context/DECISIONS.md
  - docs/ai-context/DEVLOG.md
  - docs/product/ROAD_TO_V1_0.md
  - docs/product/PAIR_COMPARISON_PREFLIGHT.md
  - docs/product/P6_EXPERIMENT_PREFLIGHT.md
  - docs/product/P6_REDUCTION_CAPTURE_PROPOSAL.md
  - docs/product/AGENT_DIRECTION_PREP.md
  - docs/product/PRODUCT_SPEC.md
  - docs/product/USER_ONBOARDING.md
  - docs/architecture/SYSTEM_ARCHITECTURE.md
  - docs/architecture/TRACE_DATA_MODEL.md
  - docs/demo/AGENT_REPEAT_EVIDENCE.md
  - docs/demo/PYDANTIC_AI_BANK_SUPPORT.md
  - docs/demo/WARNING_RULES.md
  - docs/demo/MAMR_DIAGNOSTIC_CASE.md
  - docs/development/AGENT_WORKFLOW.md
  - docs/development/AGENT_ROADMAP_DOC_AUDIT.md
  - docs/integrations/PYTHON_SDK_GUIDE.md
  - docs/releases/RELEASE_CHECKLIST.md
  - collector/go/internal/storage/sqlite.go
  - collector/go/internal/storage/imports.go
  - collector/go/internal/storage/imports_test.go
  - collector/go/internal/mamr/*
  - collector/go/internal/mamr/testdata/*
  - collector/go/internal/api/handlers.go
  - collector/go/internal/api/mamr.go
  - collector/go/internal/api/mamr_test.go
  - dashboard/web/src/api/client.ts
  - dashboard/web/src/pages/TraceListPage.tsx
  - dashboard/web/src/pages/TraceDetailPage.tsx
  - dashboard/web/src/components/MamrEvidence.tsx
  - dashboard/web/src/utils/mamr.ts
  - dashboard/web/src/utils/usage.ts
  - dashboard/web/src/style.css
  - dashboard/web/tests/mamr.test.mjs
  - docs/integrations/MAMR_DIAGNOSTIC_IMPORT.md
  - docs/assets/screenshots/mamr-import-source.jpg
  - docs/assets/screenshots/mamr-import-receipt.jpg
  - dashboard/web/src/components/MamrExplanation.tsx
  - dashboard/web/src/utils/mamrExplanation.ts
  - dashboard/web/tests/mamrExplanation.test.mjs
  - docs/assets/screenshots/mamr-failure-explanation.jpg
  - docs/assets/screenshots/mamr-completed-explanation.jpg
  - dashboard/web/src/App.tsx
  - dashboard/web/src/pages/PairComparisonPage.tsx
  - dashboard/web/src/utils/pairComparison.ts
  - dashboard/web/tests/pairComparison.test.mjs
  - docs/integrations/PAIR_EVIDENCE.md
  - docs/assets/screenshots/pair-comparison.jpg
  - docs/assets/screenshots/pair-comparison-gap.jpg
  - docs/assets/screenshots/mamr-reduction-explanation.jpg
human_gates:
  - public_api_or_persisted_data_contract_change
  - cross_repository_implementation
  - version_tag_release_or_publication
  - paid_external_api_or_model_call
  - cloud_auth_or_security_boundary_expansion
  - external_user_outreach
auto_continue: false
---

# Current Task — P6C0: precise reduction evidence proposal (approval gate)

User continuation selects a bounded read-only cause audit and capture proposal,
not cross-repository implementation or a new persisted/import contract.
Preserve the entire local prerequisite stack. Documentation-only validation.

## P6C0 outcome and next decision card

- Verified the source reducer already emits four typed reason codes; the server
  reduction-error event discards code, and transcript persistence keeps only the
  message. The current export retains only a boolean. A separate targeted-delta
  precheck also uses that event; do not label every such failure Canonical reducer.
- Current MAMR HEAD eabf737a2197366c283a6c5e99c755264f023c5a is unchanged/clean.
  Existing archived evaluation explicitly lacks rejected raw JSON/reducer detail.
  Historical cause remains unknown; no new meeting or private artifact copied.
- [Proposed exact capture/version/privacy plan](../product/P6_REDUCTION_CAPTURE_PROPOSAL.md):
  preserve one fixed gate/code diagnostic through event→local record→explicit v2
  allowlisted export→strict import/readback. No rejected Claim/text, arbitrary
  error, prompt, response, secret or inferred cause. Keep v1 and old records.
- Next **P6C1**, pending explicit approval: MAMR-only source event/local record/
  v2 export implementation and offline validation, following its own instructions
  and bilingual closeout; zero paid calls. Stop after source slice.
- Then separately selected **P6C2**: SledTrace strict v2 import and explanation,
  preserving v1/immutable same-room conflict/atomicity/RAG; no SDK or DB migration.
  New gate/code is source attribution, not verified fix, quality or causal chain.
- Required human decision now: approve cross-repo implementation and the exact
  new local event/persisted/export/import contract in that proposal. Generic
  continuation does not cross these gates. No source patch, paid replay, commit/
  push/merge/release until its specific authority exists. Do not repeat this audit
  or search for another random failure while awaiting the decision.
- Actual application correction stays conditional on an observed code and a
  reproducible single cause; P6C0 is not an Agent fix, real pair or M3b closure.

## Historical Task — P6B: explain recorded application reduction failure (local closeout)

User continuation selects P6A's SledTrace-only Dashboard correction. Reuse
existing uniquely matched diagnostic-v1 turn flags and receipt navigation.
No MAMR/source/API/DB/SDK contract change, new warning or paid call.

- Value/blocker: a completed provider and passed envelope can still fail later
  reduction; P4 currently omits that existing source signal.
- Smallest patch: read-only explanation of recorded reduction/format flags,
  preserving preceding gate facts, separate workflow/quality and unknown cause.
  Ambiguous identities or conflicting/missing evidence do not invent attribution.
- Acceptance: reduction rejection after passed envelope, later recovery and
  approved Memo; format/call/provider/started-only preservation; duplicate/missing/
  mismatched turn/receipt; actual source navigation and RAG/P5 readback.
- Validation: targeted explanation tests, canonical Dashboard tests/build,
  scope/diff, actual isolated local Collector→Dashboard synthetic fixture and
  screenshot. No private content copied or real-provider repair claim.
- Stop: one locally validated/documented slice. Conditional P6C source fix,
  new capture, paid replay, commit/push/release remain separate decisions.

## P6B outcome and next decision card

- Explanation now includes uniquely matched source turn status, format and
  reduction failure, while preserving original receipt facts. Reduction after
  passed envelope has its own failure layer; combined flags do not create extra
  calls or replace the original failure. Missing/malformed flags, missing terminal
  and ambiguous turn/attempt identities stay gaps, not inferred success/cause.
- Targeted explanation 15/15; canonical frontend 67/67 + production build/diff
  pass under normal authorized Windows execution. Actual isolated Collector/UI
  synthetic reduction+recovery record shows the failure alongside complete/
  approved/not_evaluated. Keyboard receipt selection focuses the exact failed
  attempt. Existing RAG conflict and P5 manual regression comparison still read.
- Screenshot and guide/README updated; no private source input/Memo copied,
  paid call, API/DB/SDK/MAMR contract or stored warning changed. Prerequisite
  stack remains uncommitted/unpushed; published baseline remains v0.7.1.
- Next **P6C cause gate**: existing allowlisted export lacks reducer reason and
  failed raw structure. Do not rerun the room or guess unknown_reference. Obtain
  one locally sanitized existing reducer error/allowed structural evidence, or
  propose a narrowly scoped metadata-only reason capture with version/privacy
  plan. New cross-repo/capture implementation requires explicit authorization.
- A verified single cause must precede an app patch; offline branch reproduction
  precedes a separately budgeted replay. The public task/manual rubric stays in
  [P6 card](../product/P6_EXPERIMENT_PREFLIGHT.md); controls are not frozen yet.
  If no new evidence is available, defer the app repair with the exact gap, not
  another random failure search. UI correction is not controlled runs or M3b.
- Stop here; no automatic P6C, commit/push, merge, paid call or publication.

## Historical Task — P6A: evidence-backed experiment preflight (local closeout)

User continuation selects P6A's bounded source/evidence audit and documentation.
No product code, MeetingRoom edits, capture contract, paid call or publication.
Preserve the entire dirty prerequisite stack. Documentation-only validation;
old P5B tests are historical, not rerun results for this slice.

## P6A outcome and next decision card

- Read current ordinary MAMR export, parser, reducer and call lifecycle plus
  SledTrace import/explanation. A newer real ordinary-room record contains a
  JSON rejection and a separate reduction failure after passed Turn Envelope
  validation. Full private creative content is not copied/reused. Read-only
  source identity: MAMR eabf737a2197366c283a6c5e99c755264f023c5a, clean.
- Existing v1 turns already preserve reductionFailureObserved. P4's explanation
  checks only call/provider/envelope facts, not that downstream source signal.
  This establishes a SledTrace explanation gap, NOT the underlying reducer cause.
  Neither failed raw JSON nor reducer detail is available in this export.
- Fixed public ordinary task, quality rubric, control/version references, one
  intervention and bounded keep/revert rules are in the
  [P6 experiment card](../product/P6_EXPERIMENT_PREFLIGHT.md).
  No real controlled pair or M3b result yet; do not manufacture one from this run.
- Next **P6B**: repair the SledTrace read-only explanation for a uniquely matched
  turn's recorded reduction failure, retaining call/provider/envelope success,
  unknown cause, all attempts and exact receipt navigation. No new file/source/
  API/DB contract or warning. Deliver one neutral sanitized offline regression,
  tests/build and actual UI evidence; preserve RAG/legacy/P5 comparison behavior.
- Acceptance: passed envelope + reduction failure is not presented as an
  unqualified successful application attempt; later recovery/approved Memo does
  not hide it. Conflicting/ambiguous source identities do not invent a match;
  format failure is not silently relabelled; no error cause or extra cost inferred.
- Stop after that one local Dashboard slice. It needs no MeetingRoom edit or
  paid call; ordinary continuation can select it. P6C application repair remains
  conditional on cause evidence and specific cross-repo authorization. New
  capture/persisted contracts or paid replay need their own decision/budget.
  No automatic commit/push/merge/release. P6A is a preflight, not completed P6.

## Historical Task — P5B: read-only paired comparison (local closeout)

User explicitly approved the P5A proposal and bounded pair-file contract.
One Dashboard view reads two existing records and user-declared context in page
memory only; no SDK/Collector/DB/MAMR change. Reuse ledger, pricing, timing and P4.
Keep the entire earlier dirty stack. No paid calls, cross-repo writes or release.

- Value/blocker: inspect version differences without pretending missing controls
  or quality are known; source traces alone do not prove controlled comparison.
- Deliverable: exact 16 KiB v1 declaration parser, bounded references, pure
  comparison logic, two-run UI and original-record navigation. Manual evaluation
  remains separate from source task/workflow outcomes. No percentages/judge.
- Acceptance: match/mismatch/null/same version/self-pair; quality regression
  despite lower usage; partial/conflicting/mixed usage, zero/unknown time/cost;
  missing/offline/malformed records; actual UI/keyboard/source/RAG readback.
  Dashboard tests/build, scope/check/diff, deterministic screenshots.
- Stop: locally validated/documented candidate. No automatic P6, commit/push/
  merge/publication. P6 real source fix/assessment/budget needs its own decision.

## P5B outcome and next decision card

- Exact bounded v1 declaration parser, pure measurements/comparison and paired
  Dashboard are locally implemented. Duplicate/escaped keys, bad shape/version,
  unsupported references and self-pairs reject with non-echoing errors. File is
  page memory only; source facts/manual evaluation remain separate. No API/DB/
  SDK/MAMR source schema change. [Contract and UI evidence](../integrations/PAIR_EVIDENCE.md).
- Dashboard 61/61 tests, TypeScript/Vite build and diff pass. Actual UI covers
  synthetic quality regression despite lower recorded usage, MAMR missing
  conditions, different-case mismatch, missing-record/wrong-format/offline errors,
  keyboard disclosure/original-trace navigation and page-exit discard. Original
  RAG 30/14-day warning still reads. Two actual default-viewport screenshots saved.
- Evidence is synthetic/offline; source quality stays not_evaluated and manual
  refs are not independently verified. No controlled real pair or real fix was
  established. Existing preview retained; temporary offline test server stopped.
  Earlier dirty work remains uncommitted/unpushed; published v0.7.1 unchanged.
- Next candidate **P6A preflight**: choose one finite ordinary MAMR task, fixed
  sanitized input/control references and versioned quality criterion; inspect
  existing source gate/schema evidence to identify one defensible code change.
  Current exports omit actual invalid value/expected type; do not decide to relax
  validation or add retries based on invalid_type alone.
- Smallest next deliverable is a reproducible experiment card and proposed
  keep/revert standard, not a new warning/framework or another fixture sweep.
  Existing data first; stop if no new evidence, do not endlessly reproduce random
  failure. Before source implementation/new capture contracts or paid runs,
  obtain their specific authorizations and a fresh budget. P5B approval covers
  neither cross-repo changes nor paid calls. No automatic commit/push/release.

## Historical Task — P5A: paired-comparison evidence preflight (local closeout)

User continuation selected P5 preflight, not a new source/public contract.
Value: define what a two-run view can honestly compare. Existing ledgers and P4
explanation are reusable; MAMR lacks input/config/model/quality criteria, and
Python task_id/variant/accepted alone do not establish controlled comparison.
Read-only audit and documentation only; preserve all earlier dirty work.

## P5A outcome and next decision card

- Audited current MAMR exporter, SDK examples/result semantics and Dashboard
  usage/pricing/timing. Read four records in the existing isolated fixture DB;
  these are not all user traces or fresh real meetings. No suitable controlled
  before/after pair was established. See [preflight](../product/PAIR_COMPARISON_PREFLIGHT.md).
- Recommended **P5B, pending approval**: read two existing traces and a bounded
  versioned user-declared pair-evidence file, browser-session memory only.
  No new SDK/Collector/DB/MAMR fields. Keep captured facts and manual quality
  declarations separate; matched labels are not independently verified controls.
- Smallest visible outcome: one paired view with comparability/gaps, outcomes,
  failure layer and compatible observed metrics; no fake full-run savings,
  percentages, semantic judge, scheduler, new testbed or paid calls.
- Proposed JSON contract, null/mismatch/quality/metric rules, acceptance matrix
  and 1–2-day budget are in the preflight. This document is not an implemented
  format. Public/file-contract approval is the next human gate; stop here.
- Documentation-only slice; canonical docs scope/check validation is recorded
  in DEVLOG. No fresh code test/build or remote CI claim. All prior prerequisites
  remain uncommitted/unpushed; release remains v0.7.1.
- Next only after approval: implement P5B, run dashboard tests/build and actual
  paired UI/RAG acceptance, record screenshots, close out. No automatic P6,
  cross-repo source fix, commit/push/merge or publication.

## Historical Task — P4: source-backed failure explanation (local closeout)

User continuation selects the bounded P4 card after P3B. No public/persisted
contract, API, SDK or MeetingRoom change. Preserve the earlier uncommitted stack.

- Value: explain the known failed gate and next check without requiring users
  to decode receipt JSON; navigate to the matching source attempt.
- Blocker: P3B shows source fields but no concise failure-layer explanation.
- Reuse: imported source bundle/receipts, existing span detail and three fixtures.
- Deliverable: frontend-derived D1 overview; one card per source attempt, with
  call/provider/contract facts, next check and receipt navigation. Workflow/task
  context is grouped separately, not labelled a causal downstream chain.
- Non-goals: automatic repair, semantic judge, root-cause scores, new warnings,
  D2/D3, comparisons, new schema/adapter, source edits or paid calls.
- Acceptance: rejected/completed/started-only; call failure/provider incomplete;
  mixed attempts, duplicate/missing/malformed evidence and legacy fallback;
  no inferred correctness, billing, cause or expected field type. Native keyboard
  navigation to the exact source receipt. Dashboard tests/build, scope/diff,
  actual failure/success UI screenshots and an old RAG readback regression.
- Stop: local validated explanation and documentation closeout; next P5 card,
  no automatic comparison implementation, commit/push/merge or release.

## P4 outcome and next decision card

- Frontend-derived D1 overview is implemented for ordinary MAMR diagnostic-v1.
  One attempt/card, precise source validator/path and separate call/provider
  facts. Receipt navigation requires an exact unambiguous matching source span;
  native keyboard activation moves focus to that receipt. No stored warning,
  public API/schema change, source edit, paid call or general Agent diagnosis.
- Final `python scripts/dev/slice.py check` exit 0: dashboard 47/47 tests,
  TypeScript/Vite production build and diff check pass. Initial npm sandbox
  launch denial and two ES2020/module build errors were resolved without
  loosening tsconfig or bypassing tests. P4 modifies no Collector/SDK code;
  P3B's earlier cross-stack results are not reported as fresh P4 tests.
- Actual existing fixture records in the isolated Dashboard: rejection locates
  invalid_type/card.stance with returned/completed; completed still says quality
  not evaluated; started-only says failure layer unknown. Keyboard receipt and
  context disclosure work. Original RAG conflict remains visible with no MAMR
  explanation. Two screenshots are saved; no new provider meeting or real fix.
- Limits: no exported causal/blocking links, private output or expected type;
  workflow/memo context is not a proven impact chain. Legacy/posthoc records
  have no source-backed card. Real D1 usefulness and M3 product gates remain open.
  All earlier dirty work is preserved, uncommitted/unpushed; release unchanged.
- Next candidate **P5 preflight**: define the smallest defensible paired-run
  comparison from existing traces. The MAMR projection omits task/input/config/
  model and evaluated quality; different room IDs alone cannot prove comparable
  runs or an improvement. Reuse ledger, explicit task results and source facts.
- First inspect available case/input/config/acceptance-version evidence, define
  comparable/non-comparable and null/zero/failure rules, then propose one minimal
  view/contract. Stop for approval before adding any public/persisted source
  metadata contract; do not silently infer identity from similar names or memo
  presence. No testbed expansion, comparison scheduler, paid call or real source
  fix is automatically authorized by P4 closeout.

## Historical Task — P3B: strict MAMR import and Dashboard readback (local closeout)

Updated: 2026-09-29. User continuation authorizes this next bounded development
slice. Reviewable contract: POST /api/imports/mamr accepts only one ordinary
meeting diagnostic-v1 JSON (1 MiB, 1024 receipts, 1024 turns). Exact fields,
types, enums, relationships and derived outcome signals are validated before
P3A atomic persistence. Same room/content is a no-op; changed same room conflicts.
No existing API behavior, span family or MeetingRoom source code changes.

- Value: import a saved sanitized meeting and faithfully inspect its source
  attempts, call/validation/workflow states, timestamps and usage in Dashboard.
- Blocker: no strict JSON parser, local import action or source-specific readback.
- Reuse: MAMR export/three offline fixtures, P3A transaction, existing trace UI.
- Deliverable: one dedicated import route and file action; one span per attempt
  (merge start/terminal, do not double count); bounded source-evidence display.
  Export omits model/text: model stays unknown, quality stays not evaluated.
- Acceptance: three fixtures; null/zero and provenance; duplicate/conflict;
  malformed/unknown fields, oversized/version and contradictory evidence;
  no echoed arbitrary input or partial record; old RAG tests; actual browser
  import/readback screenshots. cross-stack profile, scope and diff checks.
- Stop: validated local code and DEVLOG/CURRENT_TASK/ROADMAP closeout. D1 impact
  diagnosis/comparison, paid calls, merges and release remain separate slices.

## P3B result and next decision card

- Dedicated bounded import, atomic save, retry/conflict handling and source UI
  are locally implemented. Source start/terminal receipts remain inspectable;
  one attempt contributes one span. Missing model/text/usage/quality are not
  invented. No model call or MeetingRoom implementation change in this slice.
- Final `python scripts/dev/slice.py check` exits 0: Python 89 passed / 4 skipped,
  all Go packages pass, frontend 38/38 tests and production build pass, and
  `git diff --check` passes. Workspace-local cache/temp directories and explicit
  Git worktree variables resolve Windows validation access failures; no check
  or acceptance test was removed. Scope includes the preserved earlier stack.
- Actual browser acceptance covers rejected/completed/started-only synthetic
  exports, exact re-import, changed-content conflict, separate status dimensions,
  known zero, unknown usage and no inferred model/price/duration. Original source
  fixtures share a room ID; separate-case browser copies change only synthetic
  room IDs. Old deterministic RAG ingestion/readback still shows its chunk
  conflict warning. See the import guide and two actual screenshots.
- P3's local offline path is connected, not a real meeting/product-value verdict.
  Live source-export UI handoff, real provider evidence and end-user acceptance
  are still open. Current changes and earlier P3A/docs are uncommitted; published
  v0.7.1 and its package remain unchanged.
- Next candidate **P4**: explain the known contract-rejection case from linked
  source receipts. Value: locate the observed failed gate, separate it from
  provider completion and workflow interruption, show evidence and the smallest
  actionable next check. Reuse this importer/UI; do not introduce generic Agent
  runtime, semantic judge, automatic repair or a new source adapter.
- Before P4 implementation, agree one case/card with observed facts, suspected
  impact and explicit unknowns. Acceptance: rejected/completed/unresolved cases
  cannot be conflated; no unsupported root-cause or quality claim; regression
  tests and one visible explanation. Stop after that bounded card. Do not start
  P4, paid calls, commit/push/merge or release automatically after this closeout.

## Historical Task — P3A: atomic, repeatable MAMR import storage (local closeout)

Updated: 2026-09-28. The user asked to continue Agent development after we
identified the MeetingRoom diagnostic export as the next source artifact.
MeetingRoom now has a one-room, allowlisted diagnostic-v1 export and three
synthetic examples. This slice prepares SledTrace storage for its import; it
does not yet claim the JSON parser, dashboard readback or full P3 completion.

## Result and next decision card

- Added an internal `SaveMAMRImport` transaction and a small `mamr_imports`
  receipt table. The content hash covers the mapped source trace/spans;
  generated warning IDs/timestamps are deliberately outside its identity.
  Identical content is a no-op, changed same ID and pre-existing generic traces
  conflict; spans, warnings and manifest commit or roll back together.
- Targeted and full Collector tests pass with a workspace-local Go build cache.
  Tests cover null versus reported zero, one warning/span round-trip, duplicate,
  conflict, bad span, duplicate span, wrong/orphan warning and old storage paths.
  No source bundle was parsed, posted or displayed by SledTrace in this slice.
- Next candidate P3B: strict, bounded parser for MAMR diagnostic-v1 JSON,
  source-provenance-preserving mapping, one local import action, and actual
  Dashboard readback of completed/rejected/started-only synthetic examples.
  Unknown stays unknown; content not present in the allowlist is rejected.
  The existing RAG POST behavior and P3A transaction are the starting point.
- Before P3B changes the external import/API contract, review its exact field
  map and failure behavior. Stop after P3A; do not infer that full P3 or M2.5
  has passed. No paid call, PR merge, version, tag or release in this slice.

- User value: retrying a local import must preserve a single trustworthy trace,
  its spans and warnings, with no partial record on failure.
- Blocker: generic POST currently saves trace/spans and generated warnings in
  separate transactions; duplicate trace IDs fail without a same/different
  classification. Reusing it directly would make P3 unreliable.
- Reuse: current SQLite trace/span/warning schema and readback. Add only a
  MAMR-specific import manifest and an internal atomic save method; leave the
  existing POST contract and old records unchanged.
- Scope: one trace payload plus its warnings in one transaction. Stable content
  fingerprint detects identical re-import; same trace ID with different data,
  or a pre-existing non-import trace, is a conflict. No overwrite or new ID.
- Acceptance: imported trace/span/warning round-trip; exact duplicate no new
  rows; changed same ID conflict; invalid span/warning or other mid-transaction
  failure leaves no trace, span, warning or import manifest; old RAG storage
  tests pass. Run collector test profile and diff/scope checks.
- Visible outcome: deterministic test results and import status; the Dashboard
  gets its real UI/readback gate in P3B after strict bundle parsing.
- Stop: close P3A with DEVLOG/ROADMAP and next P3B card. No new endpoint, paid
  call, historical trace migration, version/tag/release or automatic P3B work.

## Historical Task — P2: local source-attempt capture complete

Updated: 2026-09-27. User explicitly approved the additive event/local record
contract below. P2 is locally implemented and validated in MAMR; prior AR1/P1/P1B
changes remain uncommitted and preserved. Paid calls/import/release not authorized.

## Outcome and next decision card

- MAMR final `pnpm.cmd check` exit 0: 71/71 tests, build/lint/types. Browser IndexedDB
  round-trip/dedup/conflict rollback/delete passed with the real receipt component
  and synthetic data. No real model call, full live-meeting acceptance or remote CI.
- P2 covers ordinary runAgent calls and Turn Envelope validation only. Plan,
  Observer, Solo, Review work and later task/reducer validation are outside scope.
  Configured model is not verified served model; missing evidence stays unknown.
- Detailed contract, gate dimensions and reproduction: MAMR
  `docs/correction-briefs/2026-09-27-p2-source-attempts.md` (English/Chinese).
- Next candidate: **P3 preflight**, inspect SledTrace atomic save/idempotency and
  privacy boundaries before agreeing a minimum MAMR JSON export/import contract.
  Value: read the captured failure faithfully in SledTrace. Reuse existing stores
  and source IDs; do not add a second adapter, live streaming or generic JS SDK.
- Start with a read-only storage audit and bounded decision card. If necessary,
  split P3a transactional persistence from P3b import. New external/persisted
  contract still requires approval; P2 approval does not authorize it.
- Prospective acceptance: same bundle twice = no double count; changed same ID =
  conflict; partial failure = no orphan data; unknown/time/provenance preserved;
  unsafe/oversized/version-mismatched inputs rejected; old RAG reads preserved.
- Stop after P2. No P3 code, commit/push, merge, release or paid call in this turn.
  M2.5 remains incomplete until its P3 gate; roadmap order is unchanged.

## Decision card (implemented)

- Value: distinguish a reported provider termination from application validation
  rejection, while retaining actual timing and known usage on unsuccessful calls.
- Evidence: runAgent emits ordinary start/error/format events, but agent.error
  has no usage; adapters can receive usage then throw away the result on incomplete
  responses. Legacy UsageSummary uses numeric defaults. RoomStore skips streaming
  transcript items and stamps terminal events with record.updatedAt. These fields
  cannot prove attempt start time or preserve a started-but-unresolved call.
- Reuse: existing request/turn IDs, provider diagnostic extraction and Plan's
  started/terminal lifecycle pattern. Do not reuse Plan-specific acceptedDays/
  rejections or assume Plan receipts already cover ordinary meeting turns.
- Smallest proposed boundary: ordinary runAgent-backed meeting calls only,
  with source evidence transported and saved in MAMR's existing local storage.
  Plan artifact work, Observer, Solo and Review Editor/Verifier coverage remain
  explicitly outside this first slice; no generic all-call claim.

## Approved contract — locally validated scope

1. Versioned source-attempt metadata: request/turn/seat IDs, phase/round, configured
   provider/model identity (not a verified served model), a fixed app-owned capture/
   validator version and selected output cap. Room identity is attached locally,
   not invented from or conflated with a phase request ID.
2. Separate started and terminal receipts: source wall timestamps and monotonic
   elapsed time; provider finish/category, application validation stage/result,
   input/output/reasoning tokens as nullable counts with reported/unknown provenance.
   Do not infer quality acceptance, retries, recovery or causal links.
3. Add an optional versioned attempt collection to saved meeting records and a
   bounded lifecycle event to the transport/existing local event store. Preserve
   old records, do not migrate historical traces or bump a database store merely
   for additive payload fields. Started/terminal event identities must not collide
   with append-only transcript IDs; restoration must never repeat a provider call.
4. Strict fixed-field validation and bounded collection sizes; no prompts, raw
   responses, arbitrary exception strings, private reasoning, Connection labels,
   keys or headers. Evidence is local and deleted with its room. P3 owns export.
5. Missing terminal receipt stays unresolved, never zero-cost or confirmed
   cancellation. Browser disconnect may prevent receipt persistence; no durable
   server audit log or provider-side exactly-once billing claim.

Completed acceptance: offline success, contract rejection, provider
incomplete/error, abort/missing-terminal, partial/zero/unknown usage and fake-secret
fixtures; lifecycle ordering/dedup/room restoration; a minimal inspectable receipt;
old-record compatibility plus pnpm.cmd check. Do not change prompts, model choice,
budgets, existing validator decisions or legacy usage totals to implement capture.
If richer evidence requires broader behavior change, stop for that decision.

User approval received; this bounded contract is validated/documented and stopped.
No paid call, new warning, generic SDK, SledTrace import or P3 implementation.
MAMR bilingual brief: docs/correction-briefs/2026-09-27-p2-source-attempts.md.

## Historical Task — P1B: restore MAMR's validation baseline

Updated: 2026-09-27. **Locally validated, not committed/pushed.** Prior AR1/P1
work is preserved. Code is in sibling MAMR; this checkout's docs profile is not
its product gate.

- Value: make the selected source testbed's engineering gate trustworthy before P2.
- Cause: stale Solo mock cap assertion; incomplete phase-return type; two ignored
  Review helper arguments. Existing runtime budgets/validation remain unchanged.
- Patch: correct types and unused arguments; cover current Solo caps with mock
  assertions outside provider execution. No prompt/model/schema changes or calls.
- Result: typecheck exit 0; targeted Solo/P1 5/5; canonical pnpm.cmd check exit 0,
  including build, 68/68 tests, lint and types. Four Solo cap cases covered.
- Self-review: no introduced blocker; no compiler suppression, skipped test or
  changed runtime budget. No live call, browser acceptance, remote CI or release.
- Stop reached: local engineering baseline green; no automatic P2.
- MAMR evidence: docs/correction-briefs/2026-09-27-p1b-validation-baseline.md
  and its Chinese mirror. Previous failed P1 evidence remains historical.

## Next candidate — P2 source-attempt evidence

Value: retain what actually happened at the call/validation boundary, rather
than reconstructing a failed meeting from UI text. Inspect existing MAMR Plan
receipts before choosing the minimum reusable capture boundary; do not assume
they cover ordinary meeting turns. Record run/attempt, phase, provider/model,
usage provenance, termination and timing, with missing distinct from zero.
First agree any new public/persisted contract at the human gate.

Acceptance: offline success/failure fixtures, known failed-call usage retained,
ordering/provenance/secret-exclusion checks and the canonical MAMR check.
No generic JS SDK, raw-response archive, new paid calls, bundle import or new
warning rules. Stop at trustworthy source evidence; P3 is separate.
Product roadmap unchanged: P1 → P2 → P3 → P4/P5 → P6. M2.5 remains incomplete.

## Historical Task — P1: precise MAMR validation diagnostics

Updated: 2026-09-27. **Local diagnostic implementation delivered; MAMR's full check
still fails on baseline issues. Not committed/pushed.** Prior AR1 edits preserved.
This checkout changes docs only; P1 code/tests are in sibling Multi-AI-MeetingRoom.
Its own AGENTS and Correction Brief govern; this docs profile is not a code gate.

## Decision card and outcome

- Value: identify the invalid statement/card/other contract field without leaking
  rejected content. Historical invalid output is unavailable; no invented cause.
- Scope: user continuation of adopted P1. MAMR started clean at
  a0cae68688cb6963ca7ce3fb1a08cbe7c16676b1; no concurrent changes overwritten.
- Patch: existing error string retains old prefix plus versioned reason, fixed
  path and structural facts; existing format-error/history fields carry it.
  No public event/storage schema change, prompt/model change, relaxation or retry.
- Evidence: three new offline tests pass, including 29 diagnostic/privacy fixtures,
  boundary normalization, mocked-route usage/no-retry and saved-record round-trip.
  1,107 HEAD comparisons preserve acceptance/normalization. Build/lint pass.
- Full-check limit: pnpm.cmd check exits 1, 67/68 tests (existing Solo 502 vs 200).
  Typecheck exits 2, 41 errors in untouched route/page; compiler-host substitution
  of HEAD parser source yields exactly the same 41 errors.
- Review limits: nested collection errors stop at item index. Display wiring is
  source-tested; no fresh browser/IndexedDB acceptance. No native capture/import.
- Evidence owner: MAMR docs/evaluations/2026-09-27-p1-turn-validation-diagnostics.md
  and Chinese mirror. No paid call, old-trace rewrite, commit/push or release.
- Stop: P1 local diagnostic boundary delivered, NOT a full-green integration gate.

## Next decision — bounded baseline correction, then P2

Before a green MAMR integration claim, isolate and fix the existing Solo test and
route/page type errors in a bounded correction. Preserve prompt/model/validation
behavior; validate targeted regressions and pnpm.cmd check. Stop at green gate or
a separate product decision. This correction was not started during P1.

P2 remains the next product slice: actual run/attempt, phase, provider/model,
usage provenance, termination, timing and safe config version at source.
Read MAMR instructions first; use offline success/failure/missing/privacy fixtures.
Any public/persisted schema change requires its human gate. No generic JS SDK,
raw-content archive, paid call or importer. P3 is separate; no auto-continue.

Plan: [Road to v1.0](../product/ROAD_TO_V1_0.md).
Case: [MAMR evidence](../demo/MAMR_DIAGNOSTIC_CASE.md).

## Historical Task — AR1: Agent roadmap documentation alignment

Updated: 2026-09-26. **Locally validated documentation-only slice; not committed**.
The revised direction is adopted; P1–P7 implementation is not part of this turn.

## Decision card and acceptance

- Value: all active instructions agree on failure localization → comparison →
  one real improvement decision, without leaving old rule-count gates active.
- Blocker: the detailed roadmap predates released E1/E2/E3; several guides still
  deny tool support, and old next-step text would restart evidence hunting.
- Reuse: released Python/Go/SQLite/React, preserved Agent-reference candidates,
  existing RAG regressions and the real MAMR posthoc case.
- Patch: planning/hand-off/product/architecture/user/contributor/validation docs,
  a bounded case record and a complete documentation impact audit.
- Non-goals: no functional code, schema, version, database rewrite, MAMR edits,
  new paid calls, commit/push/merge/tag/release or screenshot fabrication.
- Validation: documentation link/claim/scope review, slice status/scope/docs
  check, git diff --check. No unchanged product build; package README unchanged.
- Visible result: detailed P1–P7 plan with milestone exits, evidence types,
  privacy/storage prerequisites and stopping rules; no new capability claim.
- Stop: deliver the documentation review result, leaving P1 as next candidate.

## Closeout

All 23 affected documentation paths are aligned, including an audit explaining
which historical/package/fixture documents remain unchanged. Local link checking
found 64 valid targets and no broken links; no fragment links required anchor
validation. Slice status/scope/docs check and diff hygiene passed. Self-review
found no remaining blocker in the changed documentation; no product tests or
remote CI were rerun, because product/package code and metadata did not change.
P1 remains unimplemented. DEVLOG records commands, results and limits.

## Historical AR1 next candidate — P1 (now locally delivered above)

User value: identify the exact contract-validation field instead of the combined
“statement or card invalid” message in MAMR. The current source has distinct
JSON/top-level gates followed by one combined statement/card gate; original
invalid output from the historical run is unavailable.

Smallest change: in MAMR's own repository, add safe reason codes, field paths and
structural summaries at its validator/failure-event boundary while preserving
all existing accept/reject behavior. Read its own AGENTS/current task and check
concurrent work before selecting scope; agree any changed public/event contract
before implementation. SledTrace planning does not override that repository.

Acceptance: offline missing/type/empty/length/nested-field branches and valid
old objects; fake secrets absent from diagnostics/logs; a visible, retained
field-specific error; no prompt/model changes, loosened validation, retry or
paid call. Budget 0.5–1.5 effective days. Stop once this diagnostic boundary is
visible and tested. P2/P3/native import and subsequent fixes are separate slices.

Detailed plan: [Road to v1.0](../product/ROAD_TO_V1_0.md).
Evidence: [MAMR case](../demo/MAMR_DIAGNOSTIC_CASE.md).
Audit: [documentation coverage](../development/AGENT_ROADMAP_DOC_AUDIT.md).

## Historical task records — not current instructions

The following outcomes, commands and then-current next decisions are retained
for provenance. Their scope/authorization and old E4 prerequisites do not
override the active P1 closeout or adopted roadmap. DEVLOG owns the execution record.

## Historical Task — E4R: executed normal-repeat counterexample

Updated: 2026-09-26. Status: **locally validated; stacked review candidate**.

Decision card: E4P's hand-authored comparison keys do not show whether an
executed Agent workflow can provide safe, relevant comparison evidence. Reuse
the pinned A1/A2 bank-support reference and its actual database reads. Within
that optional example only, compare the second dynamic-instruction name lookup
to the first in memory and record booleans plus the prior span ID, without
persisting raw arguments/results or introducing a public fingerprint schema.
This tests a normal-repeat counterexample, not a suspected-waste trigger.

Acceptance: the default offline balance run records two actually executed name
lookups; the second references the first and reports same argument/result in
the unchanged synthetic SQLite fixture, while identifying upstream dynamic
instruction re-evaluation as the reason repetition may be necessary. The
missing-customer path has no fabricated pair. Optional pinned-upstream tests
block external connections and assert no raw lookup data or secret leaks in
the new metadata. Inspect Collector readback and the real Dashboard; run SDK
scope/check. Stop after one counterexample. No warning rule, public data
contract, new span, paid call, merge or release.

Outcome: the pinned upstream `balance` run produced two actual name lookups;
the second references the first and records same ID/result in this read-only
synthetic fixture while disclosing dynamic-instruction re-evaluation. The
`missing-customer` run did not invent a pair. Optional no-network tests passed
7/7; the default SDK profile passed 89 with four optional skips. Collector
readback and local Dashboard showed the new evidence, Unknown model usage and
no Agent warning. The new metadata contains no raw lookup values or hash.
This establishes one normal-repeat counterexample only; details are in DEVLOG
and the E4 evidence runbook.

Next decision gate: this single public reference counterexample cannot prove
an Agent repeat warning useful. Compare the observed fields with E4P's
suspected cases and identify remaining genuine-workflow evidence or holdout
gaps. Do not turn the booleans into a generic duplicate verdict.

## Previous task — E4C: honest warning coverage for tool traces

Updated: 2026-09-26. Status: **locally validated; stacked review candidate**.

Decision card: the user's recent question and E4P browser review exposed a
specific UI gap: a tool-only trace shows `0 warnings` and generic RAG warning
copy without saying no Agent repeat/efficiency rule ran. Reuse the existing
span types and warning list; make the zero count visually neutral and show
coverage guidance based on whether `tool` and `retrieval` spans are present.
This small honesty follow-up does not advance E4 diagnostic eligibility or
change the roadmap sequence.

Acceptance: tool-only traces clearly state that RAG retrieval checks are
inapplicable and Agent repeat/efficiency checks are not implemented; mixed
tool+retrieval traces state that any RAG findings do not cover Agent behavior;
retrieval-only traces retain their existing guidance. Zero warnings is never
styled as a health verdict. Test old/missing span lists and both applicable
cases; run Dashboard tests/build/scope and inspect the affected local page.
No warning rule, Collector/SDK/API/schema change, paid call, merge or release.

Outcome: tool-only traces now disclose that retrieval-grounding checks do not
apply without a retrieval span and that Agent repeat/efficiency checks have not
been implemented. Mixed tool+retrieval traces limit retrieval findings to
their actual coverage; retrieval-only and old empty-span guidance is
unchanged. The zero-warning count is visually neutral. Dashboard tests and
build passed locally. In the local browser, tool-only, mixed and retrieval-only
traces displayed the intended copy; the existing numeric-mismatch RAG warning
remained visible. This changes presentation only, not warning production or
diagnostic eligibility. See DEVLOG for commands and environment caveats.

Next decision card: review the E4P evidence and one genuinely bounded workflow
for safe comparable fields, state-change evidence and normal-repeat
counterexamples. Only consider a first conservative E4 signal if that evidence
can be held out and a useful low-false-positive finding is demonstrated.
Otherwise retain observed steps/usage with no Agent warning. Do not infer a
rule, public metadata schema, paid call, merge or release from E4C.

## Previous task — E4P: labeled Agent-repeat evidence baseline

Updated: 2026-09-26. Status: **locally validated; review candidate**.

Decision card: the user-visible result is a small set of repeat-behavior traces
with explicit suspected/normal/indeterminate labels that can be inspected in
the existing Dashboard. The current blocker is missing safe comparable fields
and normal-repeat counterexamples, not a missing warning count. Reuse the E2
`llm`/`tool` contract and A1's naturally repeated dynamic-instruction lookup.
Add only an offline, scripted sample matrix and tests; no SDK/Collector/UI
contract change. The synthetic comparison keys are fixture-only, not hashes
of private arguments or a proposed public metadata schema.

Acceptance: a fixed matrix shows two suspected cases, normal polling, a
recovered retry, a corrected parameter and an unknown-state confirmation.
Trace status, task outcome and unknown token usage stay distinct. The
Collector and Dashboard show the ordered attempts and at least one positive,
one normal and one indeterminate case; no RAG warning is fabricated for
tool-only traces. The runbook distinguishes fixture labels from shipped
diagnosis and records the natural A1 repeat as a counterexample. Run SDK
profile, scope/check, and inspect the actual page. Stop after review-ready
evidence; no E4 rule, paid call, schema/API change, merge or release.

Outcome: six hand-labeled, fully offline cases now generate ordered scripted
LLM/tool traces. Nine targeted tests passed; the SDK profile, scope and diff
checks are recorded in DEVLOG. Collector API readback of the corrected six
records showed three spans and zero current RAG warnings each, with five `ok`
and one `error` task. The existing Dashboard showed the duplicate-result,
polling, unknown-state and repeated-error cases; usage stayed Unknown. UI
review caught that `accepted=true` on a scripted success misleadingly showed
“Acceptance: passed”; it was removed before final validation. Initial local
records remain as superseded trial data, identified in the runbook. This is
fixture coverage, not proof that an Agent warning is useful or accurate.

Next decision card: assess whether one genuine bounded workflow can supply
safe argument/result comparison keys and state-change evidence, including
normal-repeat counterexamples. Reuse the A1 reference's naturally repeated
dynamic-instruction lookup and this labeled baseline. A first conservative
E4 signal is conditional on expanding/holding out the evidence set and
demonstrating a useful, low-false-positive finding; absent that evidence,
keep warnings off and narrow the product to observed execution/usage. No
automatic move to rule implementation, new public metadata contract, another
paid call, merge or release. Stop after this review-ready E4P slice.

## Previous task — A2: reproducible opt-in real-model Agent probe

Updated: 2026-09-26. Status: **locally validated; stacked review candidate**.

Decision card: the user-visible value is a repeatable real-model Agent trace,
not a one-off script outside Git. The blocker found in the L2 run is that the
temporary probe is not reproducible from the repository and its generic
`usage_source=provider` is intentionally not recognized as a verified OpenAI
Responses record. Reuse A1's pinned public source, synthetic SQLite customer,
existing `llm`/`tool` SDK calls, and the prior live trace. Add an explicitly
opt-in, bounded OpenAI Responses model mode to the optional example, with no
core dependency or contract change. Keep framework-reported usage provenance
honest; do not label it as direct `sledtrace.openai.record_response` evidence.

Acceptance: default A1 runs remain offline with unknown tokens; a keyless live
attempt fails before a request; local tests exercise the live wrapper with a
stub model, request ceiling and structural tool path without network. The
CLI/runbook explain that the request/output guard is not an account spending
cap. Record prior authorized live trace `trace_8630bf7c3b5444a6b673af2655ff621f`
as historical L2 evidence, not as a fresh run of the new code. Run SDK profile,
slice scope/check, diff hygiene, and inspect a fresh offline trace in the
Collector/Dashboard. No paid rerun, E4 rules, schema/API, merge or release.

Outcome: the same optional example now supports an explicitly acknowledged
OpenAI mode with synthetic data and bounded requests, while default runs stay
offline. Seven pinned-upstream tests passed with external network blocked;
the default SDK profile passed 80 tests with four optional checks skipped. A
fresh default trace `trace_53efb0fcf50c4f75bc634c1a17d094da` was read from
an isolated Collector and inspected in a prebuilt Dashboard, with five spans,
unknown provider usage and no quality-acceptance claim. The new live mode was
tested with a stub, **not** a new paid successful call. An accidental live
guard-check encountered a process key and attempted one request before
`ModelAPIError`; no usage was captured, no trace was flushed, and billing is
unknown. See DEVLOG and the runbook. No core contract or E4 rule changed.

Next decision card: user value is a useful suspected-waste finding on a real
task, not more instrumented examples. The blocker is missing stable safe
parameter/result fingerprints, normal-repeat counterexamples and a user-owned
workflow. Reuse existing steps and task results; first review A2's stacked PR
and establish a small labeled E4 evidence set, or narrow the product to the
execution ledger if no actionable case emerges. Non-goals remain new Agent
runtime/span families, broad heuristics, another paid call, merge or release.
Validation for that later decision must distinguish fixture precision from
real-user value and show accepted/failed outcomes in the Dashboard. Stop here
after A2 is review-ready; do not begin E4 automatically.

## Previous task — A1: one public Agent reference workflow

Updated: 2026-09-25. Status: **locally validated; stacked review candidate**.

Decision card: a genuine user-owned Agent workflow is unavailable. The
published E2 contract already records explicit LLM/tool attempts and task
results; the blocker is independent, faithful execution evidence. Use the
MIT-licensed PydanticAI `bank_support.py` example at pinned upstream commit
`92e0b457bd1628d17e959f9b12d74568946a2709` with its synthetic in-memory
SQLite data and local `TestModel`. Add one optional example adapter that
records actual tool execution and ordered model responses through existing
SledTrace APIs, plus no-network tests and a reproducible runbook. Do not add
SDK/Collector schema or public API, a framework-wide adapter, E4 warnings,
private bank data, paid calls, merge or release.

Acceptance: one complete no-cost task and a naturally failing task are
observed in SDK payload, Collector API and Dashboard. Show actual tool
execution, final outcome and **unknown** provider tokens (never fabricated
zeros). Pin source/dependency versions, source license, case IDs, and a
structural pass/fail criterion before running. The `TestModel` cannot prove
answer quality or user value. Run targeted tests, SDK profile, scope and diff
checks; stop after review-ready A1 evidence, before E4.

Outcome: the pinned upstream file ran in a separate checkout under
`pydantic-ai-slim[openai]==2.50.0` and an explicit `TestModel` override. The
adapter records actual SQLite lookups, two scripted model responses on the
success case and a natural missing-customer tool failure. Local Collector API
and Dashboard readback agree on five successful-path and three failure-path
spans, with unknown tokens. The final success trace does **not** mark the
scripted answer accepted; it records only `structural_pass=true` and
`quality_review=not_assessed`. Exact trace IDs, source hash, validation and
limits are in [the A1 runbook](../demo/PYDANTIC_AI_BANK_SUPPORT.md).

Next decision: the public sample is L1 integration evidence, not a user-owned
workflow. Before E4, require stable, safe comparison fields and normal
counterexamples for the two proposed rules; otherwise continue toward a
real user task or narrow SledTrace to execution analysis. No E4 rule, merge,
paid call or release is authorized by A1.

## Previous task — AG0: Agent direction preparation

Updated: 2026-09-25. Status: **planning complete; review candidate**.

The user wants to prepare the Agent direction but has no Agent workflow of
their own. Existing E2 `agent_tool_demo.py` already validates the flat
LLM/tool/result contract; rebuilding an Agent runtime or adding E4 rules now
would not provide a genuine value test. This documentation-only slice defines
the [A1 reference-workflow selection and E4 evidence gates](../product/AGENT_DIRECTION_PREP.md).

Acceptance: distinguish a technical reference from genuine user use; require
a real executed tool, observable task outcome, normal counterexamples, and a
bounded candidate search. Keep paid calls, new API/schema/span contracts,
Agent runtime, E4 rules, merge and release out of scope. Validate document
links, factual consistency, slice scope and diff hygiene. No product build is
needed because this slice changes no product code.

Next decision: select and inspect at most two public Python workflow candidates
under the A1 screen, then run only the first fit with no-cost local inputs.
If none fits, report why and pause E4. PR #16 is a separate, unmerged E3
evidence candidate; AG0 does not depend on its code or turn its RAG call into
Agent evidence.

## Previous task — Post v0.7.1 publication documentation closeout

Updated: 2026-09-25. Status: **complete**.

The user chose to include E3 from PRs #12–#13 in v0.7.1. Release PR #14
merged to `main` as `33d2335`; annotated tag `v0.7.1` points to that commit.
The protected PyPI workflow succeeded on 2026-09-25 and published wheel plus
sdist. A fresh virtual environment outside the repository installed the wheel,
verified `sledtrace`/`raglens`/`sledtrace.openai` imports, CLI version/help and
the documented out-of-checkout serving guidance. GitHub Release:
https://github.com/Schromeo/SledTrace/releases/tag/v0.7.1 .

Closeout result: PR #14's five required CI checks and clean-clone release
profile passed; the final tag workflow built and checked both distributions,
then published them through protected PyPI Trusted Publishing. The real
PyPI wheel was installed and its expected CLI/import boundaries were verified.
The GitHub Release was published against the same immutable tag. E3 remains
limited to explicit caller-supplied non-streaming Responses usage, offline
fixtures and indicative cost; no paid provider call or bill reconciliation was
performed.

Known packaging note: PyPI's 0.7.1 long description is embedded in the
immutable published artifact and still contains pre-publication wording
("when available"). The repository SDK README now reflects publication; do
not rebuild/re-upload 0.7.1. Carry the corrected description into a later
version if PyPI does not provide a supported project-description edit.

Next decision: before E4, choose one genuine bounded workflow and decide what
quality outcome can be observed alongside usage/tool traces. Use an existing
user-owned run or a no-cost local fixture first; do not claim provider billing
or diagnostic effectiveness without corresponding evidence. The detailed
ROADMAP and ROAD_TO_V1_0 remain candidate sequencing, not blanket authorization.
The pre-existing untracked `docs/demo/comprehensive_trace_example.json` remains
untouched and outside this documentation closeout.

## Previous task — E3R usage-state review fix

Updated: 2026-09-25. Status: **locally complete, PR #13 update pending**.

Last review reproduced two Dashboard mislabels: an invalid Responses usage
object was shown as `Conflict` instead of `Unknown`, and an explicit invalid
cached-token state was shown as `Unknown` instead of `Invalid`. The SDK already
persists `usage_issues` and `*_state` markers. Fix only the Dashboard reader;
keep known totals, real arithmetic/subfield conflicts, zero, and old records
unchanged. Add regression tests for both reported cases plus no-cost behavior.

Acceptance: targeted and dashboard-profile validation pass; browser-visible
state is truthful; update PR #13 with a focused commit and await CI. Do not
merge the stack, publish, call a paid provider, or start E4 in this slice.

Closeout: provider `*_state=invalid` now drives the corresponding Dashboard
field to `Invalid`; an invalid/malformed usage object is `Unknown`, while
arithmetic and subset contradictions remain `Conflict`. Unknown/invalid calls
remain outside known subtotal and price. Existing legacy caller-supplied usage
and known-zero behavior are unchanged. Regression tests cover the two reported
cases. PR #13 remains stacked on #12 and #11; review their latest checks before
any merge. Real provider/billing evidence is still a later human-gated decision.
The Dashboard profile passed with 33 tests, production build and diff check.
An isolated local Collector and live Dashboard on 4327/5178 displayed a
malformed usage total as `Unknown`, an invalid cached field as `Invalid`,
coverage `0/2`, and no price estimate for either attempt.

## Historical Task — E3 OpenAI Responses usage ledger and indicative cost

Updated: 2026-09-25. Status: **locally complete; review delivery pending**.

The user approved a narrow persisted usage/UI contract and model-based cost
estimate. Record a non-streaming OpenAI Responses result at an explicit Python
call boundary, preserving provider model, token totals, cache/reasoning
subfields, source and conflict state in existing LLM span metadata. No new
Collector schema or route. Show those fields in the existing ledger and estimate
text-token USD cost only for a small versioned official Standard-rate snapshot
with unambiguous model, counts and cache treatment. Unknown/special conditions
remain unknown, never zero or billed-fact claims. Keep price-rate injection
possible in code; no settings UI yet.

Acceptance: SDK offline fixture -> trace serialization -> Collector readback ->
Dashboard ledger agrees field-for-field and avoids double counting. Test zero,
missing, invalid/conflict, unknown model, cache and failed attempt. Run SDK,
Go, Dashboard tests/build, package validators for the new public helper, and
real local UI inspection. No network provider call, paid usage, merge, version,
tag or publication. Branch is stacked on draft PR #12 and #11.

Closeout: the new optional `sledtrace.openai.record_response` helper records
only model and provider usage, never raw prompt/output content. Existing span
metadata carries source and cache/reasoning details; the Collector schema and
routes are unchanged. Dashboard shows per-call source and a dated Standard
text-token-only estimate for exact `gpt-4.1-mini`/`gpt-4o-mini` IDs; other
models and ambiguous usage show unknown. A rate-card argument leaves a future
user-specified-model/rate path without adding a settings UI now.

Evidence: SDK 77 tests, Go all packages, Dashboard 31 tests and build passed in
the cross-stack profile using isolated pytest temp storage; wheel/sdist build,
wheel validator and independent-app validator passed. A sanitized fixture was
ingested into an isolated local Collector on 4327, read back with exact fields,
and inspected in the real Dashboard on 5178. The visible card showed
120 input / 80 output / 200 total, 20 cached input / 0 cache write /
0 reasoning output, and `$0.000170 USD` indicative text-token cost. The first
demo used an unrealistic nonzero reasoning subfield for this model; a corrected
second trace is the visible acceptance record. Neither made a provider call.
The pre-existing unrelated untracked demo JSON remains untouched and is the
sole local slice-scope violation.
The final rebuilt wheel also installed and exercised the new helper in a
separate temporary venv outside the source tree.

Next bounded decision: review this stacked diff and its CI before merge. Then
choose whether an actual user-owned OpenAI workflow can validate one real
response within an explicit paid-call budget, or proceed to a separate E4
candidate while keeping E3's real-provider evidence gate open. Do not infer
provider-wide capture or final billing accuracy from offline fixtures.

Updated: 2026-09-24. Status: **offline parser locally complete; review pending**.

The user selected the official OpenAI Python SDK as E3's first source and
sanitized offline fixtures rather than paid calls. PR #11 (RC071) is validated
but unmerged; this branch is stacked on its latest commit `7fbdc0b` and must
remain a separate review diff. The E3 metadata/UI contract decision is pending.

Deliver the smallest independently useful foundation: parse one non-streaming
Responses SDK object's usage into validated input, output, total, cached input,
and reasoning output fields. Preserve zero versus missing/invalid and detect
inconsistent totals/subfield bounds without double-counting. Do not persist a
new metadata convention, change the public SDK API, add price estimates or UI,
or call the provider until the human gate is resolved. Use a sanitized fixture
and test the pure parser offline; core SDK dependencies remain empty.

Acceptance: parser tests cover normal, zero, missing, malformed and conflicting
usage, and the SDK profile passes. Record exactly what remains for the full E3
source-to-Collector-to-UI/price path. This is not E3 milestone completion.

Closeout: the internal, dependency-free parser and sanitized OpenAI Responses
fixture cover those cases. Six focused tests and the full SDK profile (74 tests)
passed; the fixture also validated against the installed OpenAI Python SDK
3.19.2 response-usage type without a network call. The pre-existing untracked
`docs/demo/comprehensive_trace_example.json` remains untouched and is the sole
local scope-check violation. No public SDK API, persisted metadata, Collector,
Dashboard, or pricing behavior changed. Next, obtain the explicit metadata/UI
data-contract decision, then implement and verify the source-to-Collector-to-UI
path as a separate bounded slice. Do not present this parser as E3 completion.

## Previous task — RC071 exact-main release candidate closure

Updated: 2026-09-24. Status: **locally complete, PR #11 draft/review-ready;
candidate-only authorization**.

X1 and X2 have merged into `main` through PRs #10 and #9. The source tree is
already versioned 0.7.1, but release notes and READMEs still describe an
earlier reliability-only tree and call E2 unmerged or absent. Prepare a truthful
0.7.1 candidate from exact post-X2 `main`: align current/released claims,
document the observed usage ledger, one synchronous tool path, and legacy
warning read fix, then validate the distribution and affected real UI flow.

Acceptance: full release validation profile, package metadata check,
clean-wheel/independent-app boundary, exact-candidate local Collector/UI
inspection, release-quality screenshot check, and a reviewable candidate PR.
No tag, GitHub Release, TestPyPI/PyPI upload, paid model call, or E3 change.
The user explicitly reserved final publication approval for a later turn.

Local validation: the complete nine-step release profile passed (SDK 68,
startup 18, Go all packages, Dashboard 27 plus build, package build/wheel and
independent-app, diff check). Twine accepted wheel and sdist. The aggregate
runner's initial attempts were interrupted after Windows sandbox/temp-path
problems; the final run passed with an isolated forward-slash temporary path.
An isolated Collector/SQLite/Dashboard fixture was
checked in the browser. The unrelated untracked
`docs/demo/comprehensive_trace_example.json` predates this slice and remains
untouched; it causes the scope checker to flag one out-of-scope path.

Candidate PR #11 is open with five required CI checks passing. A clean clone
of `cb0dfd0` passed locked `npm ci`, real startup/ingestion/CORS/shutdown smoke,
and clean Git status. `npm audit` found four fixable transitive Dashboard
toolchain advisories (one moderate, three high); review before publication.
No merge or release is authorized by this local/CI evidence alone.

Review follow-up: the handoff entry now distinguishes published v0.7.0's
`retrieval`/`llm` from the source-only E2 `tool` path. Three real-browser
candidate screenshots checked the trace header, usage/steps, and selected tool
error detail using the sanitized offline fixture; text was legible, no secrets
or private user data appeared, and the unknown provenance and no-warning caveat
remained visible. The in-app browser is narrow, so these are conversation
evidence rather than a new full-width README asset. The README's older
full-width usage screenshot is explicitly labeled as earlier candidate; refresh
full-width release imagery before publication.

Next bounded decision — E3: after PR #11 review/merge decision, select one
OpenAI Python SDK Responses non-streaming call boundary and an offline sanitized
fixture. Preserve the provider's input/output totals and cached/reasoning
subfields without double-counting. Keep OpenAI as an optional integration, not a
core SDK dependency. Do not call a paid API, add broad adapters or stream
ingestion, or claim provider-verified coverage beyond this explicit boundary.
Any persisted wire-contract change requires the recorded human gate.

## Previous task — X2 legacy warning read compatibility

Updated: 2026-09-24. Status: **locally complete; main-targeting review candidate**.

The two post-X1 RAG suites found historical SQLite warnings with text
`confidence="heuristic"`. The detail reader expects a float, so those traces
return HTTP 500. Preserve the existing numeric-or-unknown API contract: treat
text-typed stored confidence as unknown on read, without rewriting database
rows or changing the schema. Add a persisted-database regression through the
Collector API; verify ordinary numeric confidence still reads correctly.

Acceptance: the old trace detail returns HTTP 200 with its other warning
evidence intact; numeric confidence remains numeric; Go tests and slice scope
checks pass. Do not retune RAG rules, migrate user data, run load tests, or
start E3. X1 merged through PR #10 as `755c19c`; X2 keeps its original
commits and merges that mainline tree before PR #9 retargets to `main`.
Release, publication, and paid provider calls remain separate decisions.

Closeout: `getWarnings` now returns SQL `NULL` for text-typed historical
confidence, preserving numeric values and other warning fields. A regression
test writes `heuristic` into a persisted SQLite file, reopens the Collector
store, and checks HTTP 200 plus readable warnings. The existing numeric API
and storage round-trip tests remain green. Go full-suite and `git diff --check`
passed with a temporary Go build cache after the default Windows cache
returned access denied. No user database was changed; no scale claim follows.

Next decision: E3 remains the planned next product slice, but needs one actual
provider/client and an explicit call-cost budget before paid validation. A
small labeled diagnostic-quality baseline belongs before E4 rule expansion;
the recent two suites alone do not justify threshold changes. Review and land
X2 only after its retargeted CI passes.

## Previous task — X1 external RAG corpus exercise

Updated: 2026-09-24. Status: **locally complete, review ready**.

The user's 2026-09-24 request selected a bounded external RAG exercise. Harvard
HBS's public RAG example supplies an authentic Federalist Papers PDF. The
adapter builds a local SQLite FTS5 database, records real retrieval results
through the existing SDK, and marks answer extraction as a simulation. It
does not change the SledTrace SDK/API/schema, run Harvard's original Chroma
stack, call a paid model, or start E3.

Acceptance: a reproducible local index and query, Collector readback of
retrieval and simulated-answer spans, one empty-result diagnostic case, and an
explicit runbook. Local evidence and limits are in
`docs/demo/EXTERNAL_FEDERALIST_RAG.md` and DEVLOG. Next decision remains whether
to pursue E3 with a real provider usage source and an agreed call budget.

## Post-closeout diagnostic regression evidence

After X1, two additional local suites exercised the existing diagnostic path.
`reference_rag_app all` completed nine realistic mixed-shape retrieval cases;
`local_rag_demo trace-all` completed five deterministic warning cases. Together
they produced all seven warning types through real Collector/API flow, and the
fresh traces were visible in the Dashboard. This strengthens integration
confidence but is not scale evidence and did not use a real provider call.

The follow-up exposed one material reliability blocker for repeated or larger
runs: some historical warning rows store `confidence` as the string
`heuristic`, while current detail reads scan it as numeric and return HTTP 500.
The next bounded decision should choose whether to prioritize compatibility
read/migration and isolated validation databases before E3. Warning thresholds
and lexical precision also need a small labeled cross-domain evaluation; no
threshold retuning is authorized by this evidence alone.

---

## Previous task — E2 Python tool path

Updated: 2026-09-24. Status: **E2 locally complete, PR #8 merge candidate**.

## Authority and topology

The user explicitly approved E2's minimal `tool` span and public SDK contract
on 2026-09-24, then authorized review and merge of the current PRs. E1 PR #7
was squash-merged into `main` as `622ff69`. E2 PR #8 was restacked onto that
commit with the same file tree and retargeted from E1 to `main`. Version, tag,
publication, paid model call and external trial remain separate human gates.
Existing Collector span storage is generic; do not introduce a persisted
schema migration under this approval.

## Decision card

| Question | E2 answer |
| --- | --- |
| User value | Inspect a bounded Python task's LLM attempts, tool results, and explicit final outcome together. |
| Blocker | SDK has no tool span; failed LLM attempts are labeled `ok`; the last LLM response becomes the trace answer even when it is not the task result. |
| Reuse | Existing span wire/storage, timing, supplied usage, trace metadata, and Dashboard step/detail views. |
| Smallest change | Add one synchronous `tool` record method, explicit LLM failure and task-result methods, one runnable one-tool example, and only the Collector/UI adjustments needed for honest interpretation. |
| Non-goals | No agent/memory/retry span family, framework adapter, automatic provider usage/pricing, async/thread guarantee, DAG, optimizer, release or external validation. |
| Validation | Cross-stack profile, SDK build and installed-wheel checks for the public API, focused scenario tests, API readback, and real Dashboard inspection. |
| Visible evidence | Success, business failure, and tool-failure-then-recovery traces show ordered steps, step status, timing/usage gaps, and final outcome. |
| Stop | Review and merge PR #8 after fresh CI; E3 does not start automatically. |

## Acceptance

1. One standard-library, single-process Python sample records multiple LLM
   attempts and one tool layer. Tool records have name, summary-only input and
   output, status/error, span ID, and measured or explicitly unknown duration.
2. A failed LLM attempt is `error` while retaining any supplied usage. A later
   successful task can still have `ok` trace status. Existing positional RAG
   calls and default last-response behavior remain compatible.
3. An explicit task result owns the final result for E2 traces. Task/case ID,
   run ID, variant, app version and acceptance result use documented trace
   metadata/output, without an experiment database.
4. Non-RAG tool traces do not receive retrieval-grounding warnings solely for
   lacking retrieval. Existing RAG warning fixtures remain valid.
5. Success, business failure, and tool-failure-recovery examples survive
   Collector API readback and remain legible in the Dashboard. Unknown span
   fallback and old trace display remain intact.
6. Record exact local/remote evidence, update DEVLOG/ROADMAP/AI_HANDOFF and
   DECISIONS where needed, and stop before any merge or E3 work.

## Closeout

- SDK now records caller-supplied `tool` summaries with status/error/timing and
  span ID. Failed LLM attempts retain supplied usage; `log_task_result()`
  explicitly owns the final result and acceptance state. Existing RAG calls
  keep their default behavior and positional signature.
- Collector grounding checks require an actual retrieval span; an explicitly
  empty RAG retrieval still produces its existing warning. No persistence
  schema or API endpoint changed.
- The Dashboard shows task linkage, explicit result/acceptance, ordered steps,
  tool summaries, and step errors. Unknown span fallback remains generic JSON.
- Cross-stack profile passed: Python 68 tests, all Go packages, Dashboard 27
  tests, production build, and diff check. Wheel/sdist build, clean-wheel and
  copied independent-app validators passed. Seven slice-contract tests passed.
- Three deterministic sample traces were sent to an isolated local Collector
  on 4321 with a temporary SQLite database and read back through the API:
  success `ok`, business failure `error`, and tool failure then recovery `ok`.
  All had zero RAG warnings. Real Dashboard inspection on 5176 showed step
  errors and final acceptance. The sample uses no paid model or external app;
  the real-user value gate remains open.
- PR #8 now targets `main` after a tree-equivalent restack. Check its merge and
  CI status live. E2 is not versioned, tagged or published.

## Next candidate — not active

E3 should validate one actual provider/client usage source and a provenance-
aware price basis for the selected workflow. Before activation, choose a real
application/client, establish quality/usage evidence and any paid-call budget,
and write a new decision card. Do not generalize E2's deterministic fixture
into a production agent or automatically start E3.
