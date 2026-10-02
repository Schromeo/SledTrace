# AI Handoff — current implementation facts

Updated: 2026-09-29 (DOC1). This is a current snapshot, not an execution log.
[CURRENT_TASK](CURRENT_TASK.md) owns the selected slice and pending decisions;
[ROADMAP](ROADMAP.md) owns milestone state. Historical commands/snapshots are
in [DEVLOG](DEVLOG.md) and [frozen handoff history](AI_HANDOFF_HISTORY_2026_09_29.md).

## Released versus local

- Latest recorded release: v0.7.1, published 2026-09-25 through protected PyPI
  publishing, with external clean-wheel validation. This turn did not refresh
  remote release/PR state. See [release notes](../releases/V0_7_1.md).
- Python SDK: explicit retrieval/llm/caller-instrumented synchronous tool spans,
  measured/unknown timing and explicit task result. Preferred sledtrace import
  and SLEDTRACE_COLLECTOR_URL; preserve raglens and old env fallback.
- E3 explicitly accepts a non-streaming Responses object; it is not automatic
  provider capture. Usage and finite text-token pricing are not billing truth.
- Go Collector / SQLite / React Dashboard and deterministic RAG heuristics.
  No general Agent runtime, framework-wide adapter, cloud/auth or semantic judge.
- The wheel contains SDK/CLI, NOT Collector/Dashboard runtime. Outside a source
  checkout, serve still exits nonzero with documented guidance.
- Post-release reference commits and P3–P6B development are local/review work.
  This checkout HEAD is a97935d; accumulated prerequisite edits are uncommitted.
  No push, merge or publication in DOC1; verify remote topology before delivery.

## Locally implemented candidate and entry points

| Capability | Implementation entry | Evidence limit |
| --- | --- | --- |
| P3 atomic duplicate-safe MAMR import | collector/go/internal/storage/imports.go; internal/api/mamr.go; internal/mamr/ | Source fixtures; same payload no-op, changed same room conflicts; not a live-meeting verdict |
| Import/source readback | dashboard/web/src/components/MamrEvidence.tsx; utils/mamr.ts | Ordinary diagnostic-v1, bounded strict allowlist; no inferred model/body/causal link |
| P4/P6B failure explanation | dashboard/web/src/utils/mamrExplanation.ts; components/MamrExplanation.tsx | Exact unique attempt linkage; recorded reduction failure separate from call/provider/envelope; root cause unknown |
| P5B pair view | dashboard/web/src/pages/PairComparisonPage.tsx; utils/pairComparison.ts | Two existing records plus session-memory user declarations; not independently verified controls or quality |
| Slice validation | scripts/dev/slice.py; .agents/skills/ | Existing metadata/profile behavior retained; scope includes inherited dirty prerequisites |

Contracts and visible evidence: [MAMR import](../integrations/MAMR_DIAGNOSTIC_IMPORT.md),
[pair evidence](../integrations/PAIR_EVIDENCE.md). Actual UI acceptance used
sanitized offline fixtures. Earlier component passes are dated in DEVLOG;
documentation checks do not rerun or renew product test results.

## Current blockers and boundaries

- P6 / M3b lacks an observed reproducible application cause, controlled real pair
  and human keep/revert explanation. A passed gate, approved Memo or fewer tokens
  cannot establish task quality or improvement.
- Read-only P6C0 audit found existing reducer codes lost across source event/local
  transcript/export. Targeted-delta rejection shares an event but is a separate
  gate. The old real failure cannot be reconstructed from its exported boolean.
- Last read-only source observation: MAMR eabf737, clean; not refreshed in DOC1.
  Its source capture is ordinary runAgent/envelope only, not all Agent stages.
  MAMR is an observed testbed, not SledTrace's target runtime.
- [P6C proposal](../product/P6_REDUCTION_CAPTURE_PROPOSAL.md) remains unapproved.
  v2 capture/readback must not be treated as implemented, selected or permission
  to write another repository. No private body, new model run or historical
  trace rewrite occurred in this cleanup.
- Existing [MAMR case](../demo/MAMR_DIAGNOSTIC_CASE.md) is posthoc mapping; original
  input usage/timestamps are missing. Mapping duration is not execution duration,
  accepted=false is not a human quality rejection, and zero warnings is not health.
- Repo-independent runtime and independent first/repeat use remain unverified.
  Docker/WSL limitations are environment facts, not permission to modify Windows.

## Working environment and delivery caution

Windows/PowerShell: use npm.cmd. Verify service liveness, ports and dataset
identity before reuse; no historical preview URL is guaranteed live.
For this worktree, Git may need explicit GIT_DIR / GIT_WORK_TREE pointing to
the primary checkout's worktrees/agent-reference control directory and this tree.
Do not change global Git configuration, discard dirty work, or rerun release
builds after docs-only changes. Prior paid budgets are not standing authority.


