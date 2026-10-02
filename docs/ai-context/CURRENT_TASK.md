---
slice_id: DOC1
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
  - docs/ai-context/CURRENT_TASK_HISTORY_2026_09_29.md
  - docs/ai-context/AI_HANDOFF_HISTORY_2026_09_29.md
  - docs/ai-context/ROADMAP_HISTORY_2026_09_29.md
  - docs/product/ROAD_TO_V1_0_HISTORY_2026_09_29.md
human_gates:
  - public_api_or_persisted_data_contract_change
  - cross_repository_implementation
  - version_tag_release_or_publication
  - paid_external_api_or_model_call
  - cloud_auth_or_security_boundary_expansion
  - external_user_outreach
auto_continue: false
---

# Current Task — DOC1: bounded AI-context cleanup

Updated: 2026-09-29. User approved this documentation-only cleanup after a
read-only drift review. No product, harness, package, source-testbed, API or
persisted-data change; no automatic P6C, paid call, commit/push/merge/release.

## Decision card

- Outcome: a new assistant can identify the current goal, evidence gap and
  authority without interpreting a historical task as the next instruction.
- Blocker: active task/handoff/roadmap accumulated history and repeated status;
  smaller slice completion was obscuring the unchanged P6 product gate.
- Reuse: existing file names, metadata, slice tooling, DEVLOG and detailed plan.
- Patch: freeze old documents; keep active ownership short; distinguish milestone
  exit, cumulative effort, engineering evidence and real product decisions.
- Non-goals: new AI management system, harness changes, new roadmap/milestones,
  product builds, private-data inspection or implementation of capture v2.
- Acceptance: snapshots preserve original content; local links resolve; current
  documents agree on facts/authority; incremental changes are documentation only.
- Budget/stop: one bounded documentation turn. No second cleanup pass after
  acceptance; retain unresolved product questions instead of polishing forever.

## Scope interpretation

The metadata retains the existing dirty stack against scope_base for the
unchanged scope checker. Those inherited product paths are preservation context,
NOT permission to edit product code in DOC1. This turn's permitted writes are
AGENTS, CURRENT_TASK, AI_HANDOFF, ROADMAP, NEXT_AGENT_BRIEF, DECISIONS, DEVLOG,
ROAD_TO_V1_0 and four dated snapshots.
Verify incremental file hashes separately; scope alone cannot isolate this turn.
Do not shrink inherited scope by discarding, committing or resetting user work.

## Fixed parent goal — P6 / M3b

- Exit stays: one real problem informs an application change, with retained
  baseline/candidate evidence and fixed criteria explaining keep or revert.
  A useful regression finding qualifies; a synthetic UI pass does not.
- Original estimate: 1–2 effective days, excluding paid-call/authorization waits.
  Count P6A/P6B/P6C0 and any later necessary capture/readback against this parent;
  splitting/renaming slices does not reset its budget.
- Prior effective effort: UNKNOWN (no trustworthy cumulative time record).
  Completed prerequisites: P6A preflight, P6B display correction, P6C0 proposal.
  DOC1 is workflow maintenance, not progress toward the real repair gate.
- Future selected work records this-turn effort and cumulative known effort;
  retain the unknown historical portion. Reassess near twice the original
  estimate; never fabricate elapsed totals or quietly reset the estimate.
- State: real cause, controlled pair and keep/revert evidence remain absent.
  P6 / M3b is OPEN.

## Next decision — not an implementation authorization

First compare the smallest permitted evidence route: one locally supplied,
sanitized existing error plus a bounded reproduction, versus new source capture.
Do not assert that private historical details are available or inspect them
without appropriate authority. If old evidence is irrecoverable, record the
gap and defer that case, rather than waiting for a random failure.

[P6C capture proposal](../product/P6_REDUCTION_CAPTURE_PROPOSAL.md) is preserved,
NOT approved/implemented/automatically selected. If capture is necessary,
justify its minimum scope against the fixed P6 outcome before requesting the
cross-repository and new contract approval. A cause code is source attribution,
not a causal explanation. App correction needs an observed reproducible cause;
a new real experiment needs fixed task/controls/criteria and fresh cost authority.
Prefer one change and one controlled pair first; the existing maximum of two
repair rounds requires new evidence. Keep/revert/inconclusive are honest results;
inconclusive does not mark M3b complete. No third framework or new warning family
to postpone the decision.

## Closeout

DOC1 completed locally. Preservation, incremental docs-only hashes, local links,
metadata/scope/docs validation and diff hygiene passed; exact results and limits
are recorded once in [DEVLOG](DEVLOG.md). No product tests rerun or delivery made.
Stop reached. Next product evidence choice remains a decision, not an authorized
implementation. Do not begin another documentation polish or automatic P6C.

Previous tasks and their then-current next actions:
[frozen task history](CURRENT_TASK_HISTORY_2026_09_29.md).
