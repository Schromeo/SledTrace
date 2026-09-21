# Current Task

Updated: 2026-09-15. Status: **H0 locally implemented and validated; E1 is next**.

## Baseline and authority

HEAD remains 1e77338 on codex/b2-independent-app-integration.
The worktree contains the previous roadmap documentation and this H0 slice;
neither was committed or published in this turn. Latest confirmed release is
v0.7.0; remote PR/publication state was not refreshed.

The user adopted incremental development under ROAD_TO_V1_0 and explicitly
requires self-review, DEVLOG, CURRENT_TASK and ROADMAP closeout after each slice.
This authorizes bounded implementation, not every future feature or release.

## H0 outcome and self-check

- Replaced confidence percentages with heuristic labeling and language/domain
  applicability guidance. Zero warnings explicitly does not confirm correctness.
- Preserved raw API confidence, legacy enhanced-layout selection, evidence,
  severity, numeric comparisons and recommended actions.
- Added six focused warning normalization/compatibility/guidance tests.
  Dashboard now passes 16 tests; production build passed after a sandbox-only
  esbuild directory denial was resolved by a normal-permission rerun.
- Real Collector/SDK/browser checks covered confidence 0.88, null confidence,
  evidence/actions, and a genuine zero-warning fixture. No percentage badges
  appeared. Malformed/legacy payload behavior is covered by unit tests, not
  claimed as a separate full browser automation suite.
- Refreshed the README conflict screenshot and explicitly labeled the retained
  older grounding screenshot. Exact commands/evidence are in DEVLOG.
- No SDK, Go, schema, warning-rule, dependency or version changes.
  No blocker remains for H0; do not reopen it for cosmetic work.

Preview was left at http://127.0.0.1:5174/ with Collector 4320, using a temporary
database. Verify it is still running before reuse; the original database was
not touched.

## Next implementation slice: E1 — existing LLM usage visibility

| Decision-card question | Answer |
| --- | --- |
| User value | Identify which recorded LLM call accounts for known tokens/time and see measurement gaps. |
| Confirmed blocker | Current llm metadata stores input/output/total tokens, but the Dashboard has no per-call ledger or known subtotal. |
| Existing capability | LLM span metadata, prompt/response viewer, measured/unknown timing and trace detail API. |
| Smallest deliverable | Add a compact per-call usage view and known subtotal/coverage in the existing detail page; navigate to the selected call using existing span selection. |
| Non-goals | No tool/agent spans, automatic provider capture, pricing service, A/B comparison, new runtime, full graph, version or release. |
| Validation | Focused usage aggregation/presentation tests; Dashboard tests/build; one real multi-LLM trace and one partial-data trace in the browser; diff and documentation checks. |
| Visible evidence | Hand-checkable per-call counts/subtotal, unknown data shown explicitly, selected call prompt/response visible. |
| Budget and stopping | About 1–2 focused development days. Stop when the existing-data ledger is useful and verified; defer additional charts and provider integrations. |

Acceptance:

1. Show input/output/total values per recorded LLM call, model and measured/unknown
   duration. If usage provenance is absent, label it unknown instead of claiming
   provider-verified counts.
2. Preserve zero versus missing/invalid values. Total-only records do not invent
   input/output splits; conflicting totals must not silently create a confident
   aggregate.
3. Label aggregates as known subtotals with coverage for observed calls, not all
   calls the uninstrumented application may have made. Do not double-count a
   supplied total and its components.
4. Old traces with no usage remain readable. Unknown data cannot look like a
   free/fast operation, and span durations are not summed as task wall time.
5. Selecting a call reveals its existing prompt/response or honest missing state.
6. Complete self-review, relevant tests, visible evidence and DEVLOG/CURRENT_TASK/
   ROADMAP updates before handing off. No automatic continuation into E2.

## Deferred findings and guardrails

Only retrieval/llm spans exist. Parent storage fields are already present, but
Python writes None; automatic usage capture and pricing are future work.

During H0, a no-retrieval fixture triggered the current no_retrieved_chunks rule.
E2 must review RAG-rule applicability before claiming general agent support.
Do not change warning rules as an incidental E1 fix.

Full plan and later gates: [ROAD_TO_V1_0](../product/ROAD_TO_V1_0.md).
