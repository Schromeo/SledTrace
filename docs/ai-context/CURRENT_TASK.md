---
slice_id: E1
slice_status: complete
components:
  - dashboard
  - documentation
validation_profile: dashboard
scope_base: HEAD
allowed_paths:
  - README.md
  - dashboard/web/src/pages/TraceDetailPage.tsx
  - dashboard/web/src/style.css
  - dashboard/web/src/utils/usage.ts
  - dashboard/web/tests/usage.test.mjs
  - docs/ai-context/AI_HANDOFF.md
  - docs/ai-context/CURRENT_TASK.md
  - docs/ai-context/DEVLOG.md
  - docs/ai-context/ROADMAP.md
  - docs/assets/screenshots/llm-usage-ledger.png
  - scripts/dev/test_slice.py
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

Updated: 2026-09-22. Status: **E1 is locally complete and review-ready — existing LLM usage is visible without changing collection contracts**.

## Baseline and authority

PR #3, PR #5 and PR #6 were squash-merged into `main` as `272bc56`,
`e8b034d` and `0a63e3d`. PR #4 remains closed as superseded and its branch is
retained for provenance. The latest confirmed publication remains v0.7.0; none
of these merges establishes a newer tag, package upload or release.

The user authorized continued bounded development after D0 merged. This activates
E1 only. It does not authorize E2, a public-contract change, a merge, versioning,
publication or release.

## E1 decision card

| Question | Answer |
| --- | --- |
| User value | Identify which recorded LLM call accounts for known tokens/time and see measurement gaps. |
| Confirmed blocker | LLM metadata stores input/output/total tokens, but the Dashboard has no per-call ledger or trustworthy known subtotal. |
| Existing capability | LLM span metadata, model/prompt/response fields, measured/unknown timing and existing span selection. |
| Smallest deliverable | Add a Dashboard-only usage normalizer plus compact known-subtotal/coverage and per-call rows; selecting a row reuses the current span detail. |
| Non-goals | No tool/agent spans, automatic provider capture, pricing service, A/B comparison, new backend contract, full graph, version or release. |
| Validation | Focused usage tests, Dashboard tests/build, diff check, and browser inspection of one multi-LLM trace plus one partial-data trace. |
| Visible evidence | Hand-checkable per-call values and known subtotal, explicit unknown/conflict states, and selected-call prompt/response. |
| Budget and stop | About 1–2 focused development days. Stop at a validated, documented, review-ready E1 branch; do not continue into E2. |

## Acceptance

1. Show input/output/total values per recorded LLM call, model and
   measured/unknown duration. Usage provenance absent from current records is
   labeled unknown rather than provider-verified.
2. Preserve zero versus missing/invalid values. Total-only records do not invent
   input/output splits; conflicting totals do not enter a confident aggregate.
3. Aggregate only one trustworthy total per observed call: use a valid supplied
   total when consistent, otherwise the valid input/output sum when both exist.
   Label the result a known subtotal with covered/observed call counts.
4. Old traces with no usage remain readable. Unknown data cannot look free or
   fast, and span durations are not summed as task wall time.
5. Selecting a call reveals its existing prompt/response or honest missing state.
6. Complete self-review, Dashboard tests/build, visible browser evidence and
   DEVLOG/CURRENT_TASK/ROADMAP closeout. Refresh the README screenshot because
   the trace-detail product surface materially changes.

## Guardrails

Only `retrieval` and `llm` spans exist. Do not add a new span family, change the
wire/schema, modify warning rules, infer hidden provider retries, or claim that
the known subtotal covers uninstrumented application calls.

Usage-source metadata is not part of the current public contract. E1 must show
that provenance as unknown rather than invent a provider-verified label. Pricing,
cost and automatic usage capture remain deferred.

## Closeout

- Added a Dashboard-only usage normalizer and a compact LLM call ledger. It
  preserves zero, missing, invalid and conflicting states and counts one
  trustworthy total per covered observed call.
- Added eight focused edge-case tests. The full Dashboard suite passes 24/24 and
  the production build completes with Vite 6.4.3.
- The repository slice scope accepts all eleven changed paths, and the final
  Dashboard validation profile passes tests, production build and diff check.
- Browser validation covered a three-call complete trace (known subtotal 220,
  coverage 3/3) and a partial/conflicting trace (known subtotal Unknown,
  coverage 0/3, one conflict excluded). Selecting a ledger row updated the
  existing prompt/response detail.
- Saved the real complete-trace view to
  `docs/assets/screenshots/llm-usage-ledger.png` and refreshed the README.
- No SDK, Collector, storage schema, public trace contract, warning rule,
  package version, tag or release changed. E1 is on Draft PR #7; it is not
  merged. The Slice Contract CI check initially exposed a D0-specific assertion
  in `test_slice.py`, now changed to validate the active contract generically.

## Next candidate — not active

E2 remains only a candidate: one deliberately bounded Python agent/tool path.
Before starting it, write a new decision card, examine warning applicability for
non-RAG runs, define failure/measurement semantics, and obtain any required
human-gate decision. Do not continue automatically from this completed slice.
