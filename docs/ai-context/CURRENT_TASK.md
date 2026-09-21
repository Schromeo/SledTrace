---
slice_id: D0
slice_status: complete
components:
  - repository_workflow
  - documentation
validation_profile: agent-harness
scope_base: HEAD
allowed_paths:
  - .agents/skills/sledtrace-review/SKILL.md
  - .agents/skills/sledtrace-slice/SKILL.md
  - .github/copilot-instructions.md
  - .github/workflows/ci.yml
  - AGENTS.md
  - docs/ai-context/AI_HANDOFF.md
  - docs/ai-context/CURRENT_TASK.md
  - docs/ai-context/DECISIONS.md
  - docs/ai-context/DEVLOG.md
  - docs/ai-context/ROADMAP.md
  - docs/development/AGENT_WORKFLOW.md
  - scripts/dev/slice.py
  - scripts/dev/test_slice.py
  - scripts/dev/validation_profiles.json
human_gates:
  - public_api_change
  - persisted_schema_or_data_contract_change
  - new_span_family
  - version_tag_release_or_publication
  - paid_external_api_or_model_call
  - cloud_auth_or_security_boundary_expansion
  - external_user_outreach
auto_continue: false
---

# Current Task

Updated: 2026-09-20. Status: **D0 is complete and review-ready in PR #6; E1 is the next candidate and has not started**.

## D0 outcome and review boundary

D0 adds repository-native delivery mechanics without starting E1. Its completed
scope is the machine-readable task contract, shared implementation/review skills,
deterministic `status`/`scope`/`check` commands, declarative validation profiles,
a lightweight CI contract job, Copilot instructions, and their documentation.

PR #3 and PR #5 were squash-merged into `main` as `272bc56` and `e8b034d`.
PR #6 is normalized directly onto that current `main` and contains only D0.
Cumulative PR #4 remains closed as superseded and its branch is retained for
provenance. PR #6 is not merged or released.
Automatic Copilot review still requires the maintainer's one-time GitHub setting
described in `docs/development/AGENT_WORKFLOW.md`.

## Baseline and authority

The delivery branch for PR #6 is `codex/d0-agent-development-harness-clean`.
Current `main` includes the v0.7.1 reliability and B1/B2/H0 integration commits,
but no newer tag or PyPI publication is established: the latest confirmed release
remains v0.7.0. D0 is review-ready repository infrastructure, not product or
release functionality.

The user adopted incremental development under ROAD_TO_V1_0 and explicitly
requires self-review, DEVLOG, CURRENT_TASK and ROADMAP closeout after each slice.
This authorizes bounded implementation, not every future feature or release.

## D0 acceptance and stop point

1. PR #6 compares directly with current `main` and contains only the 14 declared
   workflow/documentation paths.
2. `status`, committed-range `scope`, the `agent-harness` validation profile and
   the additive Slice Contract CI job pass without weakening the D0 boundary.
3. Existing Python, Collector and Dashboard CI jobs remain present and unchanged
   in purpose; no runtime product behavior, public API, schema or version changes.
4. Documentation distinguishes merged, review-ready, released and future states.
5. Stop after a review-ready PR and remote CI. Do not merge PR #6, begin E1, tag,
   publish or release without the corresponding human decision.

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

## Next candidate after D0 merge decision: E1 — existing LLM usage visibility

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
