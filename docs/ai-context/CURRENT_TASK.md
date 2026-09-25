---
slice_id: E3
slice_status: complete
components:
  - sdk
  - documentation
validation_profile: sdk
scope_base: 7fbdc0b
allowed_paths:
  - sdk/python/sledtrace/_openai_usage.py
  - sdk/python/tests/test_openai_usage.py
  - sdk/python/tests/fixtures/openai_response_usage.json
  - docs/ai-context/AI_HANDOFF.md
  - docs/ai-context/CURRENT_TASK.md
  - docs/ai-context/DEVLOG.md
  - docs/ai-context/ROADMAP.md
human_gates:
  - persisted_schema_or_data_contract_change
  - version_tag_release_or_publication
  - paid_external_api_or_model_call
  - cloud_auth_or_security_boundary_expansion
  - external_user_outreach
auto_continue: false
---

# Current Task — E3 OpenAI Responses offline usage extraction

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
