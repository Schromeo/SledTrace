# Roadmap — current milestone index

Updated: 2026-09-29 (DOC1). This page is state and sequencing, not a test log.
Detailed goals and gates: [ROAD_TO_V1_0](../product/ROAD_TO_V1_0.md).
Execution contract: [CURRENT_TASK](CURRENT_TASK.md). Facts/entry points:
[AI_HANDOFF](AI_HANDOFF.md). Evidence: [DEVLOG](DEVLOG.md).
Historical plans: [frozen roadmap](ROADMAP_HISTORY_2026_09_29.md); their old
next actions are NOT current instructions.

## Direction and status

Local-first, Python-first AI workflow failure localization and evidence-backed
improvement verification, preserving RAG. Not a generic Agent platform.
Latest recorded release remains v0.7.1; no DOC1 publication or remote refresh.
The old requirement to implement two E4 warnings before comparison is superseded.

| Stage | Current evidence | Remaining exit gate |
| --- | --- | --- |
| M0–M2 | Reliability/integration/harness, E1/E2/E3 released in v0.7.1 | Broader Agent value not implied by released technical paths |
| M2.5 / P1–P3 | Source-side P1/P1B/P2 and local SledTrace strict import/readback accepted with fixtures | Actual live source-export handoff remains separate evidence |
| M3a / P4–P5 | Bounded D1 explanation, P6B reduction visibility and manual-context paired view locally implemented | Useful real diagnosis and controlled outcome evidence remain unproven |
| M3b / P6 | Preflight/display correction/capture proposal completed as prerequisites | OPEN: one real change plus defensible keep/revert explanation |
| M4 / U1–U4 | Planned | Checkout-free supported runtime, minimal UX/privacy and two independent first uses |
| M5 / R1–R3 | Necessary import atomicity implemented early; remaining work planned | Scope/compatibility/support validation on exact release candidate |
| G1 | Planned | Independent repeated use, stability and authorized 1.0 release |

Local slice completion does not advance a milestone whose exit gate is unmet.
Keep local implementation, validation, commit/push, merge, release and real value
as distinct states. No percentage-complete claim can replace these gates.

## Current decision and default sequence

DOC1 maintenance is locally complete and stopped at documentation acceptance.
Next product decision: minimum actionable evidence for P6.
Existing P6C1/P6C2 proposals remain available but NOT automatically selected or
approved. Compare a permitted sanitized existing error/reproduction first;
new capture needs a demonstrated blocker and its explicit authority.
Do not repeat audits or random failure searches without new evidence.

P1/P2 → P3 (necessary storage/privacy) → P4/P5 → P6 real keep/revert decision
→ product-value review → U1/U2/U3/U4 → remaining R1/R2/R3 → G1.
P7/D2 or D3 is optional, not a warning quota or a prerequisite for productization.
U1's bounded feasibility investigation may be brought forward only by an
explicit decision, not used to silently mark M3b done.

## Progress and budget discipline

- P6 exit and original 1–2-effective-day estimate stay fixed across subordinate
  preflight/capture/readback slices. Historical effort is unknown; no fake total.
  See CURRENT_TASK for the current parent ledger and detailed plan for stop rules.
- Fixed testbeds: MAMR, pinned PydanticAI and existing RAG. No third framework
  to delay the product decision. Source code/gate attribution is not root-cause proof.
- One selected slice at a time. Near twice the original budget, or two slices
  without a visible user result, reassess rather than adding another prerequisite.
- Check progress here at closeout; update changed status only. Detailed commands,
  screenshots and failures belong in DEVLOG/owned evidence, not every entry file.



