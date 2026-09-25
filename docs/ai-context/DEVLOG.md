# Devlog

## 2026-09-25 — AG0 Agent-direction preparation

- The user confirmed they have no current Agent workflow, then asked to
  prepare that direction. Inspected the published E2 `llm`/`tool`/task-result
  contract, the deterministic one-tool example, E4/E5 roadmap gates and the
  separate unmerged E3 evidence candidate.
- Defined a one-workflow A1 screen, technical-versus-value evidence levels,
  E4 positive/counterexample requirements, and a stop rule in
  `docs/product/AGENT_DIRECTION_PREP.md`. No runtime, API, schema, span type,
  diagnostic rule, dependency or paid call was added. No public workflow has
  yet been selected or run; E4 and v0.8 remain unvalidated candidates.


## 2026-09-25 — v0.7.1 published and release closure verified

- Merged release-closure PR #14 as `33d2335b1f908588e46a1a003c574786735355ef`.
- Created and pushed immutable annotated tag `v0.7.1` at that exact commit.
- Protected publication workflow
  https://github.com/Schromeo/SledTrace/actions/runs/36132895644 succeeded:
  built wheel and sdist, passed Twine check, and uploaded both to production
  PyPI through the `pypi` environment. An initial run triggered from `main`
  was rejected by the environment branch rule before upload; the successful
  rerun used `v0.7.1` for both trigger and build refs.
- PyPI JSON lists `sledtrace-0.7.1-py3-none-any.whl` and
  `sledtrace-0.7.1.tar.gz`; `pip index versions sledtrace` reports 0.7.1 as
  latest.
- A new virtual environment under the system temp directory installed
  `sledtrace==0.7.1` from production PyPI. `sledtrace version` printed
  `0.7.1`; `--help`, `serve --help`, `sledtrace`, `raglens`, and
  `sledtrace.openai` checks passed. Running `serve` outside a source checkout
  exited 1 with the documented repository/Docker guidance.
- Published GitHub Release:
  https://github.com/Schromeo/SledTrace/releases/tag/v0.7.1 . The release
  checklist's package and release gates are complete.
- PyPI's 0.7.1 JSON long description is the README embedded before publication
  and still says "install from PyPI when available"; the published files are
  immutable, so the source SDK README was corrected for the next build. Do not
  rebuild or re-upload 0.7.1 to change display metadata.
- E3 evidence remains a sanitized offline Responses fixture and local UI
  readback. There was no paid provider request or invoice comparison.
- The pre-existing untracked `docs/demo/comprehensive_trace_example.json`
  remains untouched and excluded from the release.

Next decision: select one genuine bounded workflow and an observable quality
outcome before finalizing E4 scope. The v1.0 roadmap remains staged planning,
not a mandate to implement every proposed capability.

## 2026-09-25 — E3-inclusive v0.7.1 release acceptance in progress

The user chose PRs #11–#13 together for 0.7.1. PR #11 squash-merged as
`70e0342`, #12 as `36c00af`, and #13 as `7bcbeec` after each restacked
layer's five CI checks passed. Required linear history was preserved; merge
conflicts were resolved to trees identical to the already validated branch
trees. No tag or package publication has occurred at this point.

The combined `7bcbeec` tree passed the nine-step release profile: SDK 77,
startup 18, Go packages, Dashboard 33 and build, wheel/sdist build,
clean-wheel and copied independent-app validators, and diff check. An initial
attempt was stopped because pytest's temporary directory was mistakenly
inside the repository, causing the out-of-checkout CLI test to enter source
startup; the rerun used a fresh external temp path and passed. The host has no
Twine module; the PR Python CI runs `twine check` on both artifacts.

The previous lockfile audited at four fixable transitive advisories (one
moderate, three high). A lockfile-only update within existing ranges now
reports zero audit findings. `npm ci` in the live workspace could not unlink
the esbuild binary held by the running Dashboard preview; the final closure
tested a clean isolated checkout without stopping that preview. In that
checkout, `npm.cmd ci` installed 69 packages with zero audit findings; the
nine-step release profile passed again (SDK 77, startup 18, Go all packages,
Dashboard 33 and build, wheel/sdist, both installed-package validators and
diff check). Slice scope passed for all ten intended files and the clone's
Git status remained clean. The pre-existing untracked JSON stays only in the
primary workspace and was not included in this release branch.

An explicit, sanitized non-streaming Responses mapping was recorded through
the local Collector and shown in the real Dashboard: 120 input, 80 output,
200 total, 20 cached input, 1/1 coverage and `$0.000170 USD` indicative
Standard text-token cost. A 1440×950 screenshot was saved for the README. No
provider call, invoice comparison, secret, prompt or output content was used.
PR CI with Twine metadata check, protected publication and production-index
install remain pending; do not call this release complete yet.

---

## 2026-09-25 — E3R Dashboard usage-state review follow-up

Review of draft PR #13 found two reproducible mislabels. The Dashboard treated
`invalid_usage_object` as a token conflict even though no comparable counts
existed; it also discarded explicit `*_state=invalid` markers and displayed
those fields as missing. The reader now distinguishes invalid/malformed input
from arithmetic or subfield contradictions, without changing persisted data,
SDK capture, Collector or price rates. Unknown and invalid states remain out
of the known subtotal and cost estimate. Added focused regressions for both
cases; existing zero, legacy and true-conflict cases still pass.

Dashboard profile passed: 33 tests, production build and diff check. A fresh
temporary SQLite Collector on 4327 stored a sanitized two-attempt trace; the
real Dashboard on 5178 showed malformed usage `Total: Unknown`, explicit
invalid cache `Cached input: Invalid`, coverage `0/2`, and no cost estimate for
either. The unrelated pre-existing untracked demo JSON still causes the local
slice scope check's only violation and was excluded from the patch. Final PR
CI remains to be checked after push; no merge or release is implied.

## 2026-09-25 — E3 explicit Responses usage and indicative text-token cost

Built on the separate E3 parser PR branch, not on public `main`. A caller may
pass one completed non-streaming OpenAI Responses object to
`sledtrace.openai.record_response`; it stores only model and usage fields in an
LLM span. It does not import the OpenAI client, execute an API call, or persist
the prompt, generated content, response ID, or credentials. Existing Collector
generic metadata storage needs no schema or route change.

- The Dashboard ledger now distinguishes this explicitly recorded source from
  unknown provenance and shows cached input, cache write and reasoning output
  as subfields rather than additional totals. Inconsistent/malformed source
  usage cannot enter the known subtotal or a cost estimate.
- A dated 2026-09-24 official OpenAI Standard text-token rate snapshot covers
  only exact `gpt-4.1-mini` and `gpt-4o-mini` IDs and their documented snapshots.
  The estimate excludes tools, tiers, regional and other charges and is never
  represented as a bill. The calculator takes a rate-card argument for a later
  user-supplied-model/rate workflow; no settings UI was added.
- Cross-stack profile passed: Python 77, Go all packages, Dashboard 31, Vite
  production build and diff check. The first attempts hit Windows Go cache and
  shared pytest-temp access denials; an isolated pytest temp path with permitted
  execution passed. Python wheel/sdist build, wheel validator and independent-
  app validator passed.
- The final rebuilt wheel was installed in a separate clean temporary venv
  outside the SDK directory; `from sledtrace.openai import record_response`
  recorded and serialized expected usage without an OpenAI dependency.
- An isolated local Collector/SQLite on 4327 stored the sanitized fixture and
  returned exact source/count fields through GET. Real Dashboard on 5178 showed
  the corrected `gpt-4.1-mini` trace with 120/80/200 tokens, cached 20,
  cache-write 0, reasoning 0 and `$0.000170 USD` indicative cost. The initially
  displayed fixture had an unrealistic reasoning count for that model; it was
  superseded by a corrected second local trace. Neither made a provider call.
- Local slice scope was otherwise clean but flagged the pre-existing unrelated
  untracked `docs/demo/comprehensive_trace_example.json`; it was not staged.

Real provider/cost-bill verification and user price settings remain open gates.
This is development evidence, not publication or external-user validation.

## 2026-09-24 — E3 OpenAI Responses offline parser foundation

On a branch stacked on the unmerged v0.7.1 candidate, added an internal pure
parser for non-streaming OpenAI Responses usage. It distinguishes known zero
from missing or invalid counts, retains provider input/output/total and cached
input/reasoning output separately, and flags conflicting totals or subfield
bounds. It makes no API call, does not add a core dependency, and does not
write a persisted metadata convention or price estimate.

- Six focused tests passed with a sanitized, prompt-free fixture; full SDK
  profile passed with 74 tests and `git diff --check`.
- The fixture was also validated offline against the installed official OpenAI
  Python SDK 3.19.2 `ResponseUsage` type. No token or network use occurred.
- Local slice scope reported only the pre-existing unrelated untracked
  `docs/demo/comprehensive_trace_example.json`; it was preserved and excluded
  from this change.
- This is E3 groundwork, not the provider-to-Collector-to-Dashboard usage or
  pricing feature. Persisted metadata/UI semantics require the pending human
  contract decision; no release or merge is implied.

## 2026-09-24 — X2 legacy warning confidence read compatibility

The post-X1 RAG suites exposed persisted warning rows with text
`confidence="heuristic"` that made historical trace detail return HTTP 500.
X2 keeps the numeric-or-unknown API contract: the warning SELECT returns
`NULL` for text-typed confidence while leaving the stored row untouched.
Current numeric values and all other warning fields are read normally.

- Added a persisted-file API regression: POST a trace, set its saved warning
  confidence to the historical text value, reopen the store, then GET detail.
  The response is HTTP 200 and retains readable warnings with unknown
  confidence. Existing numeric API and storage round-trip tests still pass.
- `go test ./internal/api ./internal/storage -count=1` passed with a temporary
  Go build cache. Its first attempt did not run tests because the default
  Windows Go cache returned `Access is denied`.
- `python scripts/dev/slice.py status`, `scope`, and `check` passed on X2;
  `check` ran `go test ./... -count=1` and `git diff --check`, both passing.
- No schema, user database, diagnostic threshold, SDK, or Dashboard change;
  no scale or provider-usage validation claim.

X2 is stacked on X1 commit `3ecf21f`, which is not on `main`. Review/merge
dependency remains explicit. E3 selection and any paid call remain separate.

## 2026-09-24 — Two-suite RAG diagnostic regression validation

Ran two local end-to-end RAG suites against the source Collector on
`127.0.0.1:4319` and inspected the real Dashboard at `127.0.0.1:5173`.
Neither run called an external model or incurred a paid API call.

- `reference_rag_app all`: nine cases completed successfully through local
  document loading, lexical retrieval, mixed result-shape normalization, SDK
  tracing, Collector ingestion, SQLite persistence, and API readback. The
  observed warning coverage included `conflicting_chunks`,
  `low_retrieval_score`, `weak_query_chunk_overlap`, `numeric_mismatch`, and
  `answer_not_grounded`. The `damaged` and `subscription` cases returned zero
  warnings, providing two low-noise checks.
- `local_rag_demo trace-all`: five cases completed with Collector status
  `stored`. The cases exercised `no_retrieved_chunks`, `low_retrieval_score`,
  `duplicate_chunks`, `conflicting_chunks`, and `answer_not_grounded`. A fresh
  `no_match` readback returned one `no_retrieved_chunks` warning. A fresh
  duplicate case returned trace
  `trace_62ca9cf1916342f8b0c7acf160c3bee2` with
  `duplicate_chunks, answer_not_grounded`.
- Dashboard inspection showed the fresh traces in the list with warning counts;
  the duplicate trace detail was reachable and rendered its warning state.

This is realistic small-scale integration evidence, not a scale or performance
test. The corpus and request volume are small, execution is sequential, and no
throughput, concurrency, p95 latency, memory, SQLite contention, or large
Dashboard-list behavior was measured.

New findings and bounded follow-up candidates:

- The local development database contains legacy warnings whose `confidence`
  value is the string `heuristic`. Current detail reads expect a numeric value,
  so some historical trace detail requests return HTTP 500. A compatibility
  read/migration test should precede any larger repeated-run or scale exercise.
- Warning counts are not equivalent to warning precision. Correct or benign
  reference cases can still receive low-score or conflict warnings because the
  generic threshold and lexical heuristics are not calibrated to every
  retriever/corpus. Build a small cross-domain labeled corpus and measure false
  positives before changing thresholds or adding rules.
- The two suites should become separate validation layers: deterministic rule
  fixtures for exact coverage, and realistic external-corpus adapters for
  ingestion/normalization/readback. Each run should use an isolated database or
  a unique trace namespace so historical records cannot contaminate results.
- A later scale profile should vary corpus size, payload size, concurrent
  flushes, sustained duration, and Dashboard list volume, and should report
  throughput and p50/p95/p99 latency. This remains a candidate investigation,
  not an authorization to start E3 or add infrastructure.

No product code or schema was changed by this validation. The provider-usage
and price-provenance question remains the separately gated E3 decision.

Documentation closeout validation: `python scripts/dev/slice.py scope` and
`git diff --check` passed. Earlier reruns encountered Windows pytest temporary-
directory ACL errors and a Collector process left on port 4319 during browser
inspection. At delivery, a fresh `python scripts/dev/slice.py check` passed all
68 SDK tests and diff check; pytest only reported a cache-write warning. No
source regression is attributed to the documentation-only update.

## 2026-09-24 — X1 external Federalist Papers RAG exercise

- Selected [harvard-hbs/rag-example](https://github.com/harvard-hbs/rag-example)
  at `e47fab50cfaf64ced94dac23ba68ed9c797ee667` because its included
  Federalist Papers PDF is authentic source material. Rejected an otherwise
  convenient prebuilt movie SQLite database after checking its 90 invented plots.
- Adapted the PDF to a local 297-row SQLite FTS5 page index. The adapter records
  BM25 as lower-is-better retrieval data and labels its answer extraction as a
  simulation. No SDK/API/schema change, real LLM, paid call, or external trial.
- Default query matched pages 28/29/85; Collector stored trace
  `trace_862f8fa097de4835af50dc8e0e53a992` with retrieval and simulated
  answer spans, both visible on API readback, and zero warnings. Empty-result
  query stored `trace_4e5cf4d414284adabe096ee0bbe5c900` with
  `no_retrieved_chunks` and `answer_not_grounded`. The isolated Collector ran
  on 4322 with a separate database. See the runbook for commands and limits.
- This confirms local ingestion and rule behavior for two cases, not retrieval
  accuracy, answer quality, or upstream Chroma/LLM compatibility. E3 remains a
  separate decision.
- Validation: `python scripts/dev/slice.py scope` passed for five changed paths;
  the `sdk` profile passed 68 SDK tests and `git diff --check`. Python syntax
  compilation passed. Pytest reported a cache-write warning in this sandbox;
  tests themselves passed. No Collector or Dashboard source was changed.

---

## 2026-09-24 — E1 merge and E2 restack for review

- Reviewed E1 and E2 against the slice contract. No blocking code finding was
  identified; known limits remain caller-supplied usage and an internal-only
  E2 integration example.
- Squash-merged E1 PR #7 into `main` as `622ff69` after five green checks.
  The E1 branch and new `main` had identical file trees.
- Preserved the original E2 commit `468ee48` under local branch
  `archive/e2-pre-restack-20260924`; rebased its single change onto `622ff69`
  as `d4d8982`. The old and new E2 heads have identical file trees. PR #8 now
  targets `main` and shows the original E2-only 18-file diff.
- Local review validation: 68 Python tests, all Go packages, 27 Dashboard
  tests, production build, and diff check passed. The default Go cache and
  sandboxed Vite config read failed for environment reasons; a temporary Go
  cache and normal-permission build passed without code changes.
- E2 merge and fresh PR checks remain to be confirmed. No version, tag,
  publication, paid call, or E3 work occurred.

---

## 2026-09-24 — E2 single Python tool path (stacked on E1)

Outcome: locally implemented one synchronous Python tool path after the user
approved the public SDK method and `tool` span family. Work is on
`codex/e2-python-tool-path`, based on unmerged E1 commit `941fd06`. This is an
internal review candidate, not a release or a real external-agent validation.

- Added `t.tool(...)` with caller-supplied safe summaries, explicit status and
  error, optional measured/unknown timing, and returned span ID. Added failed
  LLM status/error without losing supplied usage, plus
  `t.log_task_result(result, accepted)` to separate attempts from final outcome.
  Old positional RAG calls and legacy import remain supported.
- Reused generic Collector span storage; no schema migration or endpoint change.
  Grounding now requires a retrieval span, while an explicit empty retrieval
  still warns. Dashboard shows task linkage, final acceptance, ordered tool/LLM
  steps and failed-step details. Unknown spans retain generic JSON fallback.
- Added standard-library deterministic success, business-failure and
  tool-recovery scenarios. No paid model, provider API, framework adapter or
  external tester was involved.

Validation:

- Targeted SDK E2 tests passed 5/5 initially; final full cross-stack profile
  passed 68 Python tests, all Go packages, 27 Dashboard tests, production build
  and `git diff --check`. Slice Contract tests passed 7/7 and E2 path scope
  passed. `python -m build` produced wheel/sdist; `validate-wheel.py` passed a
  clean-venv E2 API check and legacy import/CLI checks;
  `validate-independent-app.py` passed its copied-wheel legacy flow.
- A local isolated stack used Collector `127.0.0.1:4321`, Dashboard
  `127.0.0.1:5176`, and a temporary E2 SQLite DB. All three sample traces
  were POSTed and read back by ID. Returned task statuses were `ok`, `error`,
  `ok`; tool recovery had steps `llm ok → tool error → tool ok → llm ok`.
  Each produced zero RAG warnings. The actual Dashboard showed result,
  acceptance, ledger subtotal and step error. The recovery view remains open
  for user inspection during this turn.
- Environment incidents: isolated build and Vite/Go cache access needed normal
  permissions. The first full profile encountered a pre-existing pytest temp
  ACL denial. A Windows-backslash `PYTEST_ADDOPTS` attempt misparsed and created
  two test-only directories inside `sdk/python`; both exact paths were checked
  and removed. A forward-slash dedicated temp path let the full profile pass.

No merge, tag, version bump, PyPI upload or external trial occurred. Remote
push/PR/CI state is recorded separately after delivery. E3 did not start.

---

## 2026-09-24 — E1 Draft PR CI repair

- Pushed `codex/e1-existing-usage-visibility` and opened Draft PR #7. The
  Dashboard, Collector, Python 3.9 and Python 3.13 CI jobs passed on its first
  run. Slice Contract failed because `test_slice.py` asserted the historical
  `D0` ID and metadata while `CURRENT_TASK` had correctly advanced to E1.
- Updated the repository-contract test to validate the current metadata and
  compare the status CLI's JSON with that metadata, without hard-coding a
  particular slice. No product implementation, wire contract or schema changed.
- `python scripts/dev/test_slice.py -v` passed 7/7 locally after the repair.
  `python scripts/dev/slice.py scope --base origin/main` accepted all eleven
  changed paths. `python scripts/dev/slice.py check` passed all three steps
  under normal permissions: Dashboard 24/24 tests, production build and diff
  check. Its sandboxed build attempt hit the same Windows esbuild path-access
  denial recorded in the E1 development run; no code workaround was added.
- Remote CI is pending a new run after this repair is pushed.
- E2 has not started. No PR merge, version, tag or release was performed.

---

## 2026-09-22 — E1 Existing LLM Usage Visibility

Outcome: completed the bounded E1 Dashboard slice on
`codex/e1-existing-usage-visibility`. A user can now see where recorded LLM
tokens and call time went without changing SDK capture, the wire contract,
Collector storage, warning rules, or package version. E2 did not start.

Implementation:

- Added a pure Dashboard usage normalizer for observed `llm` spans. Token fields
  preserve known zero, missing and invalid states. A valid recorded total is
  counted once when consistent; otherwise two valid components can provide an
  input-plus-output total. Conflicting totals are explicit and excluded.
- Added a trace-detail ledger with per-call order/name/model, input/output/total,
  measured or unknown duration, and unknown/not-provider-verified provenance.
  The summary reports a known subtotal and covered/observed calls; zero covered
  calls renders `Unknown`, not a misleading free-use total.
- Kept interaction small: selecting a ledger row reuses the existing span detail
  for prompt, response and metadata. No new route, chart, pricing table, provider
  adapter, span family, or backend contract was added.
- Added eight focused tests for recorded/derived totals, total-only records,
  zero, conflicts, malformed/partial data, ordering/filtering and format states.
- Captured the actual complete-trace view as
  `docs/assets/screenshots/llm-usage-ledger.png` and refreshed README capability
  wording. The screenshot contains deterministic fixture content only.

Validation:

- `npm.cmd test` in `dashboard/web` — exit 0; 24/24 tests passed.
- `npm.cmd run build` in `dashboard/web` — exit 0 with normal permissions; Vite
  6.4.3 transformed 40 modules and produced the production bundle. The sandboxed
  attempt had failed at esbuild access after TypeScript checking, so no product
  workaround or dependency change was made.
- `python -B scripts/start-sledtrace.py --dashboard-port 5175
  --startup-timeout 60` — source Collector and Dashboard reached readiness at
  `127.0.0.1:4319` and `127.0.0.1:5175`. The sandboxed first attempt was cleaned
  up after Go-cache/esbuild access errors; the normal-permission run succeeded.
- Browser inspection verified a three-call complete trace: 132 recorded-total
  tokens at 80ms, 50 total-only tokens with unknown duration, and 38 derived
  tokens at 40ms. Summary: known subtotal 220, coverage 3/3. Selecting Call 2
  changed the existing detail panel to that call's model/prompt/response.
- A partial-data trace verified input-only usage, a conflicting 10 + 5 versus 99
  total, missing usage, and a real 0ms duration. Summary: known subtotal Unknown,
  coverage 0/3, one conflict excluded. Unknown, invalid, zero and conflict did
  not collapse into the same presentation.
- Final repository workflow checks: `python scripts/dev/slice.py scope` — exit 0,
  all ten changed paths accepted; `python scripts/dev/slice.py check` — exit 0,
  all three Dashboard-profile steps passed (24 tests, production build, and
  `git diff --check`). Node's existing experimental type-stripping warning and
  Windows line-ending notices were non-failing.

Data and delivery boundary:

- The startup helper used the repo-local ignored `raglens.db`; deterministic
  trace IDs `trace-e1-complete-20260922` and
  `trace-e1-partial-20260922` remain as local development records. No tracked
  source or schema was modified by those writes.
- E1 is locally implemented and browser-validated. At this record it has not
  been pushed, opened as a PR, merged, tagged, versioned, or published. The
  latest confirmed release remains v0.7.0.

---

## 2026-09-20 — Normalize D0 Candidate after PR #5 Merge

Outcome: rebuilt the PR #6 candidate directly on current `origin/main` after
PR #3 and PR #5 were squash-merged. The candidate retains the three validated
D0 commits and adds only the minimum contract/documentation correction required
for a truthful D0-only review. No product functionality, E1 work, release action
or `main` rewrite occurred.

Review findings and correction:

- PR #6 still targeted the now-diverged PR #5 branch, so GitHub displayed 14
  commits instead of the intended three D0 commits. A direct retarget would also
  have reverted current README statements introduced by the merged history.
- Replayed `459d762`, `b09803a` and `91610fe` without conflict onto `e8b034d`.
  The effective candidate is exactly the 14 D0 workflow/documentation paths;
  root and SDK README files are no longer part of the diff.
- The prior CURRENT_TASK declared E1 active while `auto_continue` was false. Its
  documented reviewer command, `slice.py scope --base origin/main`, therefore
  rejected ten files in D0 itself. CURRENT_TASK now records D0 complete and
  review-ready, E1 as the unstarted next candidate, and the exact D0 boundary.
- Added the `agent-harness` validation profile and aligned harness tests with the
  D0 contract. Historical validation entries below remain as point-in-time
  evidence rather than being rewritten.

Local validation on the normalized candidate:

- `python scripts/dev/slice.py status` — exit 0; D0 complete, repository workflow
  plus documentation, `agent-harness` profile, auto-continue false.
- `python scripts/dev/slice.py scope --base origin/main` — exit 0; all 14 changed
  paths accepted, zero violations.
- `python scripts/dev/slice.py check` — exit 0; seven harness tests passed and
  `git diff --check` passed. Windows printed line-ending conversion warnings only.

Delivery state at this record: local normalization branch prepared; remote PR #6
update and fresh CI are still required. PR #6 is not merged, and E1 remains
unstarted.

---

## 2026-09-15 — Normalize Stacked PR History

Outcome: replaced the cumulative D0 review surface with an explicit three-layer
stack without changing product functionality, starting E1, publishing, merging,
or rewriting public history.

Topology:

- Preserved PR [#3](https://github.com/Schromeo/SledTrace/pull/3) unchanged as
  the v0.7.1 reliability candidate: `main` <-
  `codex/v0.7.1-reliability` at `1ab83ef`.
- Created draft PR [#5](https://github.com/Schromeo/SledTrace/pull/5) for the
  reviewable B1+B2+H0 integration layer: base
  `codex/v0.7.1-reliability`, head `codex/b1-b2-h0-integration` at `0fc1e00`.
  Its diff contains exactly four existing commits: `b6848c1`, `00619cf`,
  `1e77338`, and `0fc1e00`.
- Created draft PR [#6](https://github.com/Schromeo/SledTrace/pull/6) for the
  D0-only layer: base `codex/b1-b2-h0-integration`, head
  `codex/d0-agent-development-harness-clean`. It preserves D0 implementation
  commit `459d762` and delivery record `b09803a`; this normalization record is a
  documentation-only follow-up on the same D0 review layer.
- Commented on cumulative PR [#4](https://github.com/Schromeo/SledTrace/pull/4)
  with both replacements and closed it as superseded. The original
  `codex/d0-agent-development-harness` branch remains available for provenance.
- No force-push, rebase, cherry-pick, commit replacement, branch deletion, main
  rewrite, merge, version/tag/release action, or E1 implementation occurred.

Validation:

- Refreshed remote refs and verified strict ancestry with `git merge-base
  --is-ancestor`: `origin/main` -> PR #3 -> `0fc1e00` -> `b09803a`; all three
  checks exited 0.
- PR #5 initial GitHub Actions run
  [35023978893](https://github.com/Schromeo/SledTrace/actions/runs/35023978893)
  succeeded in 45 seconds: Python 3.9, Python 3.13, Go Collector, and Dashboard.
- PR #6 initial GitHub Actions run
  [35024010553](https://github.com/Schromeo/SledTrace/actions/runs/35024010553)
  succeeded in 53 seconds: Slice Contract, Python 3.9, Python 3.13, Go Collector,
  and Dashboard.
- Documentation-only closeout before commit: `git diff --check` exited 0;
  `python scripts/dev/slice.py status` exited 0 without changing the active E1
  contract; `python scripts/dev/slice.py scope` exited 0 and accepted exactly
  the four ai-context documentation paths. The post-push #6 run is the final
  remote gate for this documentation follow-up.

---

## 2026-09-15 — D0 Repository-Native Agent Development Harness

Outcome: implemented a small workflow harness without starting E1 or changing
runtime product behavior. Created branch `codex/d0-agent-development-harness`.
Because the incoming worktree contained validated but uncommitted planning/H0
work, preserved it first as separate prerequisite commit `0fc1e00` rather than
mixing it into the D0 commit or discarding it. Relative to `main`, the resulting
draft PR is necessarily stacked on v0.7.1/B1/B2/H0 prerequisites.

Implementation:

- Added simple CURRENT_TASK frontmatter for active E1: component, validation
  profile, HEAD scope base, allowed code/doc paths, seven human gates and
  `auto_continue: false`. The existing E1 prose and acceptance remain intact.
- Added shared `.agents/skills/sledtrace-slice` and `sledtrace-review` workflows.
  The implementation skill ends after one review-ready slice; review prioritizes
  acceptance, data semantics, missing/unknown, compatibility, failure, privacy,
  claims and high-value tests rather than cosmetic requests.
- Added standard-library `scripts/dev/slice.py` with `status`, `scope` and
  `check`; named commands and docs/Dashboard/SDK/Collector/cross-stack/release
  profiles live once in `validation_profiles.json`.
- Added seven deterministic harness tests, including status JSON, E1 metadata,
  allowed scope, a deliberate scope violation, dot-prefixed paths, profile reuse,
  skill/Copilot structure, and preservation of all CI jobs.
- Added repository-wide Copilot instructions and one additive `Slice Contract`
  CI job. Existing Python, Go Collector and Dashboard jobs were not changed.
- Added `docs/development/AGENT_WORKFLOW.md` with local use and the maintainer's
  one-time automatic Copilot review setting. AGENTS now points to the shared
  skills/script without copying E1 details.

Validation:

- `python scripts/dev/slice.py status` — exit 0; reported E1 active, Dashboard
  profile, allowed paths, all human gates and auto-continue false.
- `python scripts/dev/test_slice.py -v` — exit 0; 7 tests passed. The deliberate
  temp-repository violation exited 1 and was asserted; an allowed Dashboard path
  exited 0 and was asserted.
- `python scripts/dev/slice.py check` — first exit 1 at dashboard-build because
  the Windows sandbox denied esbuild access above the workspace. It correctly
  stopped. The identical normal-permission command exited 0: 16 Dashboard tests,
  Vite 6.4.3 build with 39 modules, and diff check passed.
- PyYAML 6.0.2 `safe_load` parsed `.github/workflows/ci.yml`; assertions confirmed
  `slice-contract`, `python`, `collector`, and `dashboard` jobs. `actionlint` was
  unavailable. The new CI job provides the remote parser/execution check.
- `python scripts/dev/slice.py scope` against active E1 intentionally exited 1
  for nine D0 workflow paths and accepted CURRENT_TASK. D0 did not weaken E1's
  scope to make its own bootstrap pass; the unit tests prove both scope outcomes.
- One diff-versus-D0-acceptance self-review found and fixed dot-directory path
  normalization. Final `git diff --check` and local Markdown-link checks passed.

Boundaries and delivery state after the repository-only closeout:

- harness locally validated: yes
- D0 implementation committed: yes, `459d762`
- pushed: yes, `origin/codex/d0-agent-development-harness`
- draft PR opened: yes, [#4](https://github.com/Schromeo/SledTrace/pull/4)
- remote CI: five of five checks passed on 2026-09-15, including the new Slice
  Contract job plus Python 3.9/3.13, Go Collector and Dashboard
- merged: no; merging is explicitly out of scope
- E1 implementation/product schema/version/release: unchanged
- automatic Copilot review setting: not changed because local `gh` authentication
  is invalid; exact one-time maintainer action is documented

---

## 2026-09-15 — H0 Honest Diagnostic Presentation

The user authorized starting incremental development and required a repeatable
self-review/log/current-task/roadmap closeout workflow. H0 is locally complete
in the existing working tree; the preceding planning changes are preserved.

Implementation:

- Removed numerical confidence badges from TraceDetailPage. Display heuristic
  labeling and explicit English-pattern/domain applicability instead; zero
  warnings is not presented as a correctness verdict.
- Kept the API and raw confidence untouched, including legacy enhanced-layout
  selection. Extracted the existing warning normalization helpers into
  src/utils/warnings.ts and added six compatibility/guidance tests without a new
  dependency or testing framework. Evidence, severity, comparisons and actions
  remain unchanged.
- Saved a real warning/evidence screenshot as
  docs/assets/screenshots/heuristic-warning-detail.png and updated README's
  conflict image. The retained older grounding image is explicitly labeled as
  pre-H0, including its uncalibrated badge limitation.
- Made the user-required closeout workflow explicit in AGENTS; updated the
  current task, roadmap progress and handoff. E1 is next; no sequence expansion.

Validation (repository-relative working directories):

- dashboard/web: `npm.cmd test` — exit 0, 16 passed, including six new cases;
  Node emitted the existing experimental type-stripping warning.
- dashboard/web: `npm.cmd run build` — first exit 1 after TypeScript checking,
  because esbuild could not read a parent directory under sandbox restrictions.
  The identical command with normal permissions exited 0: Vite 6.4.3,
  39 modules transformed. No code workaround or dependency update was used.
- Root: `python -B scripts/start-sledtrace.py --dashboard-port 5174
  --startup-timeout 60` with SLEDTRACE_COLLECTOR_ADDR=127.0.0.1:4320 and a fresh
  SLEDTRACE_DB_PATH — both real services reached readiness. Persistent exec
  session 46901 was intentionally left running for user inspection, not reported
  as an exited command. No Docker/WSL changes.
- sdk/python, with SLEDTRACE_COLLECTOR_URL=http://127.0.0.1:4320:
  `python -B -m examples.reference_rag_app.run conflict`, `refund` and
  `wrong-window` — each exit 0, deterministic/no paid LLM calls.
- Readback showed conflict trace trace_84f843bba759461caf34e362a9d3a560 retained
  confidence 0.88 and three evidence items. Refund also exercised a null-confidence
  low-score warning. Actual browser inspection confirmed heuristic wording,
  evidence/action retention and zero percentage badges.
- An initial no-retrieval fixture generated the existing no_retrieved_chunks
  warning, so it was not treated as zero-warning evidence. A retrieved greeting
  fixture (trace_19c300e5785b40e68875172468adcb67) then returned zero warnings;
  its real page explicitly said this does not confirm answer correctness.
  Defer non-RAG rule applicability to E2; do not expand H0 to change the engine.
- Self-review: inspected the functional diff and new tests; only presentation
  and helper extraction changed. Malformed/legacy confidence is tested at the
  unit boundary; this is not a new automated SDK-to-browser CI suite.

Closeout: diff/whitespace and local-document-link checks passed. SDK/Go builds
and package release validation were not repeated because their implementations
did not change. Preview uses a temporary database, preserving existing user data.
No commit, push, merge, tag, version bump or publication was performed.

---

## 2026-09-15 — Draft a gated product roadmap through v1.0

- The user requested detailed product, competitive-positioning, usability and
  milestone planning to avoid overengineering. This turn changed documentation
  only, based on local HEAD `1e77338` and a clean initial worktree.
- Added `docs/product/ROAD_TO_V1_0.md`: current assets versus gaps, target users,
  defensible hypotheses, honest usage/cost/quality semantics, M0–M5 slices and a
  v1.0 go/no-go checklist. Competitive references were checked against official
  Langfuse documentation and the ClawTrace research abstract; product prospects
  remain hypotheses, not proven demand.
- Recommended preserving RAG evidence while testing a bounded Python execution
  efficiency loop: H0 honest wording, existing-token visibility, one agent/tool
  path, conservative signals, then outcome-aware comparison. Defer broad RAG-rule
  tuning and gate runtime/UX investment on real actionable value.
- Updated the active ROADMAP and CURRENT_TASK, aligned AGENTS/AI_HANDOFF, added
  the planning rationale to DECISIONS, and shortened NEXT_AGENT_BRIEF. Marked the
  original product/schema designs as historical instead of changing their old
  proposals into claims of current support.
- Added one-slice work limits, bounded investigations, visible acceptance,
  proportional test cadence, documentation ownership and explicit shrink/stop
  conditions. Checkout-free runtime, privacy, storage semantics, independent
  onboarding and repeat use remain later gates, not completed capabilities.

Validation: Markdown-only scope and local-link/whitespace checks passed;
`git diff --check` passed (Git reports expected LF-to-CRLF checkout warnings).
No SDK/Go/Dashboard tests, package builds, service startup, paid model calls or
remote publication checks were rerun for this documentation-only task.

Boundary: the plan is submitted for user review. No functional code, version,
commit, merge, tag, publication or external-user outreach was changed. H0 is the
next recommended slice when the user resumes implementation under this plan.

---

## 2026-09-14 — B2 Independent-App Integration

- Continued from B1 commit `b6848c1` on
  `codex/b2-independent-app-integration`, without changing the open v0.7.1 PR.
- Added a copyable pure-Python application covering successful delivery,
  application-owned exception propagation/error tracing, and observable
  Collector-offline behavior.
- Added a clean-wheel validator that copies the artifact and example outside the
  repository, installs into a fresh venv, asserts success/error payloads through
  a local capture server, then verifies offline behavior after shutdown. Added it
  to Python 3.9/3.13 CI after the existing clean-wheel validation.
- Replaced the Dashboard's checkout-ambiguous empty state with installed-SDK and
  explicitly repo-local commands. The header now displays the configured API
  base URL rather than a hard-coded default. Updated root, package, and
  integration docs.

Validation:

- `cd sdk/python && pytest -q`: 62 passed.
- `cd sdk/python && python -m build`: wheel and sdist passed after normal network
  access supplied the isolated build environment. The first restricted attempt
  exposed a Windows output-decoding issue; UTF-8 mode showed the actual denied
  PyPI connection before the permitted rerun succeeded.
- A one-use temporary Twine 7.0 environment reported both the wheel and sdist
  `PASSED` and was removed; the host Python remains unmodified.
- Existing `validate-wheel.py` passed. New `validate-independent-app.py` passed
  from an installed 0.7.1 wheel in a temporary external directory for exit codes
  0 (success), 2 (application error), and 1 (Collector offline).
- Startup regressions: 18 passed with normal process permissions. The restricted
  first run could not terminate its own wrapper/listener tree; exact test PIDs
  13148 and 10232 were terminated before the passing rerun.
- Collector: all Go packages passed. Dashboard: 10 tests and production build
  passed; the restricted esbuild attempt failed before compilation on directory
  access and the normal-permission rerun transformed 38 modules.
- A separate fresh venv installed the wheel from a system temporary directory.
  Its copied application stored `independent-app-success` (ok, retrieval + llm)
  and `independent-app-application-error` (error, retrieval) in the real local
  Collector. API readback preserved `ExampleBusinessError` and its message.
  The actual Dashboard displayed both traces and was left open on the error
  detail; the temporary app environment was removed.
- A second isolated preview with an empty database, Collector 4320, and Dashboard
  5174 visibly rendered zero traces and the new instructions. That check exposed
  and then verified removal of the old static `localhost:4319` header label; the
  page displayed its actual `http://127.0.0.1:4320` API endpoint.

Boundary: this is internal independent-environment evidence, not an external
first-run attempt. The example remains source-only; the wheel still does not
bundle Collector/Dashboard assets or standalone serving. No version, remote PR,
merge, tag, release, or publication action was performed.

Next: honest confidence presentation, then a reserved cross-domain diagnostic
baseline; retain automated browser acceptance and genuine external first runs as
explicit open evidence rather than silently declaring them complete.

---

## 2026-09-14 — B1 Source Startup Reliability

- Phase review confirmed S1-S4 against implementation and PR #3; production
  PyPI remained 0.7.0. Continued development on `codex/b1-startup-reliability`
  from `1ab83ef`, leaving the existing remote candidate unchanged.
- Added preflight checks for Go/Node 22+/npm, installed Vite, source directories
  and bind availability; missing dependencies now point to `npm ci`.
- Added strict-port Vite startup, configurable helper Dashboard port/startup
  timeout, configured Collector health URL, and consistent default API/CORS.
- Ready output waits for both services. Partial launches, health timeout,
  interruption and unexpected service exit all enter owned-process cleanup.
- Added 18 standard-library startup tests to Python CI and an opt-in real-stack
  smoke script. No SDK/package, Collector or Dashboard source changed.

Validation:

- `python -B -m unittest discover -s scripts/tests -v`: 18 passed on Windows,
  including a real wrapper/listening-child cleanup test. The first sandboxed
  run could not terminate its own test tree; a normal-permission rerun passed
  and the original test PIDs were verified and cleaned up.
- `cd sdk/python && python -B -m pytest -q -p no:cacheprovider`: 62 passed;
  expected legacy-import deprecation warning only.
- `python -B scripts/tests/smoke_startup.py`: real Go/Vite startup, health,
  Dashboard HTTP, SDK ingestion/readback (two spans, two warnings), custom-port
  CORS, SIGINT and both ports released passed. Temporary smoke DB was removed
  by the test after shutdown.
- A second helper invocation against occupied default ports exited 1 with
  guidance and did not disturb the existing preview.
- Browser inspection displayed `b1-startup-verified` with two spans and
  45-day answer versus 30-day retrieved evidence. Conversation screenshots
  captured the actual page; README showcase images were not changed because
  Dashboard presentation did not change.
- The weak-overlap warning on this short fixture remains diagnostic-quality
  backlog evidence, not a rule fix or accuracy claim in B1.
- No package/build repeat or Docker runtime attempt was needed. New-branch
  remote CI, including POSIX process-tree execution, has not run.

Next: review B1, then independent-app integration and installation-aware guidance.
The v0.7.1 merge/publication remains a separate release-stage action.

---

## 2026-09-11 (v0.7.1 Release Candidate Preparation)

### Completed

- Selected **v0.7.1 — Trustworthy Local Tracing** as the patch release grouping
  for S1 timing, S2 score semantics, S3 delivery policy, and S4 network defaults.
- Created `codex/v0.7.1-reliability` from S4 commit `fc85bda`.
- Aligned Python package/import/CLI/runtime/example validation and Dashboard
  package metadata to 0.7.1.
- Added `docs/releases/V0_7_1.md` and kept root release status explicit that
  v0.7.0 remains the latest published version.
- Generated nine deterministic reference traces from the 0.7.1 source and
  refreshed all three README screenshots from the real local Dashboard at
  1440x950. The images show honest unknown trace duration and score-direction
  labels rather than generated or mocked UI.

### Local validation

- `cd sdk/python && pytest -q`: 62 passed.
- `cd sdk/python && python -m build`: built
  `sledtrace-0.7.1-py3-none-any.whl` and `sledtrace-0.7.1.tar.gz`.
- `cd sdk/python && python -m twine check dist/*`: passed for the 0.7.1 artifacts
  and retained historical local artifacts. Twine was installed only in a system
  temporary directory because it was absent from the host Python environment.
- `cd sdk/python && python scripts/validate-wheel.py`: passed in a new temporary
  virtual environment, including version 0.7.1, preferred/legacy imports,
  timing, score semantics, delivery policy, CLI, and out-of-checkout `serve`.
- `cd collector/go && go test ./... -count=1`: all packages passed.
- `cd dashboard/web && npm.cmd ci`: passed; npm re-reported the known four
  development-dependency advisories (one moderate, three high).
- `cd dashboard/web && npm.cmd test`: 10 passed.
- `cd dashboard/web && npm.cmd run build`: passed; 38 modules transformed.
- Default and explicit-remote `docker compose config` expansion passed.
- Live Collector/Dashboard listeners were loopback-only and all nine reference
  traces rendered in the browser.

### Remaining candidate gates

- Do not merge, tag, publish to PyPI, or create a GitHub Release without a
  separate release-stage decision.

### Clean-clone validation

- Committed release preparation as `25521d4508a924a96132b72147f69171e7a3af37`.
- Cloned that exact branch commit to a new system temporary directory; initial
  and post-smoke `git status --short` were clean.
- `npm.cmd ci` installed the locked Dashboard dependencies in the clone.
- A new venv installed the clone's SDK; installed `sledtrace version` returned
  `0.7.1`.
- The installed `sledtrace serve` entry point found the checkout and started the
  current Collector/Dashboard on `127.0.0.1:4319` and `127.0.0.1:5173`.
- Collector health and Dashboard HTML returned 200.
- The clone's reference app stored a conflict trace; API readback returned two
  spans, one warning, null trace duration, and higher-is-better semantics for the
  first score. The same detail is open in the user's browser.

### Pull request validation

- Pushed `codex/v0.7.1-reliability` and opened protected pull request
  [#3](https://github.com/Schromeo/SledTrace/pull/3) to `main`.
- The PR head matches the locally prepared candidate history; `origin/main`
  remained the direct ancestor with no rebase or conflict required.
- Required checks passed: Python 3.9, Python 3.13, Go Collector, and Dashboard.
- The PR remains open. No merge, tag, PyPI upload, production-index claim, or
  GitHub Release was performed.

---

## 2026-09-11 (S4 Local Network Defaults)

### Completed

- Changed the native Collector fallback and Vite development/preview scripts to
  loopback while preserving explicit address/host overrides.
- Bound both Docker-published host ports to `SLEDTRACE_BIND_HOST`, defaulting to
  `127.0.0.1`, while keeping container-internal listeners unchanged.
- Replaced wildcard CORS with the two exact local Dashboard origins plus a
  comma-separated `SLEDTRACE_ALLOWED_ORIGINS` replacement list.
- Added address precedence and CORS allow/deny/preflight tests.
- Documented the full intentional-remote boundary, including binding, browser
  origin, Dashboard API URL, SDK URL, and the unauthenticated-service warning.
- Replaced the old S2 live services with the current S4 processes and left the
  validated Dashboard available at `http://127.0.0.1:5173`.

### Validation

- Focused Collector address/API tests: passed.
- `cd collector/go && go test ./... -count=1`: all packages passed.
- `cd dashboard/web && npm.cmd test`: 10 tests passed.
- `cd dashboard/web && npm.cmd run build`: passed; 38 modules transformed.
- Default `docker compose config`: both host ports expanded to `127.0.0.1`,
  Collector stayed on container `:4319`, and local origins were explicit.
- Explicit remote Compose expansion preserved `0.0.0.0`, the supplied origin,
  and the supplied Dashboard API URL.
- Live listeners were exactly `127.0.0.1:4319` and `127.0.0.1:5173`.
- Live HTTP checks covered no Origin, both allowed local origins, and a denied
  origin with `Vary: Origin`.
- Python SDK trace `trace_abc2dc4e6b494b6687a2472903863998` stored and rendered
  in the actual Dashboard with retrieval/LLM spans and a warning.
- Restricted Go/npm runs initially hit local cache/path access denials; the same
  tests passed with normal tool access. One assistant-written live probe used
  unsupported `trace(input=..., output=...)` arguments and failed before network
  I/O; it was corrected to the repository's real API and then passed.

### Boundary

- S4 is complete and committed only on the local branch; it is not pushed,
  merged, versioned, or released.
- Docker runtime was not retried because the known WSL2 host prerequisite is
  unavailable; Compose structure was validated without the daemon.
- No auth, TLS, firewall, proxy, API, storage, warning, span, SDK URL default,
  Dashboard visual, version, or publication change entered the slice.

---

## 2026-09-11 (S3 Trace Delivery Policy)

### Completed

- Reproduced strict delivery behavior for non-JSON metadata, offline Collector,
  timeout, and delivery attempted while an application exception propagated.
- Kept `flush()` strict and additive-only; added public frozen
  `TraceFlushResult` plus explicit `try_flush()` for a single observable
  best-effort attempt.
- Preserved exact ordinary exceptions in `result.error`, left
  `KeyboardInterrupt`/`SystemExit` behavior untouched, and verified that a
  delivery failure no longer replaces an original business exception when the
  caller chooses `try_flush()` in `finally`.
- Exported the same result class through preferred `sledtrace` and temporary
  `raglens` compatibility imports; extended clean-wheel validation.
- Updated root/package integration guidance and the active context documents.

### Validation

- Focused delivery/package tests: 21 passed after correcting the test module
  target; the first six failures occurred before product execution because the
  package-level `raglens.trace` function shadowed the module in a string mock path.
- `cd sdk/python && pytest -q`: 62 passed.
- `cd sdk/python && python -m build`: passed; wheel and sdist produced.
- `cd sdk/python && python scripts/validate-wheel.py`: passed, including the new
  delivery result, S1/S2 APIs, preferred/legacy imports, and CLI.
- `git diff --check`: passed with line-ending conversion warnings only.
- Deterministic demonstration: strict offline flush raised `RuntimeError`;
  `try_flush()` returned `ok=False` with that error; the application still
  propagated `LookupError("business failure")` while delivery failure remained
  separately inspectable.

### Boundary

- S3 is complete and committed only on the local branch; it is not pushed,
  merged, versioned, or released.
- No Collector, API, SQLite, Dashboard, warning, span, retry, queue, disk buffer,
  background worker, automatic logging, version, or publication change entered
  the slice.
- Go and Dashboard checks were not repeated because those components did not
  change. Their S2 validation remains attached to local commit `ee0a812`.

---

## 2026-09-11 (S2 Retrieval Score Semantics)

### Completed

- Closed S1 into local commit `5b5d254` and created
  `codex/s2-retrieval-score-semantics`; no push, PR, merge, version, tag, or
  release was created.
- Reproduced that similarity 0.10, distance 0.10, explicit score 0.10, and a
  tuple value 0.10 all collapsed into the same bare `score` contract.
- Added `score_type` and `score_direction` to normalized chunks, automatic known
  metric semantics, explicit custom overrides, unknown tuple semantics, and
  non-finite-value handling while preserving explicit/legacy score behavior.
- Gated the Collector's low-score threshold and score-based diagnostic ordering
  so lower/unknown/unannotated-custom/invalid directions cannot be silently
  interpreted as higher-is-better.
- Added Dashboard metric/direction labels and dependency-free behavior tests.
- Added `examples.score_semantics_demo` and aligned SDK, onboarding, architecture,
  active-context, and handoff documentation.

### Validation

- `cd sdk/python && pytest -q`: 52 passed.
- `cd sdk/python && python -m build`: passed.
- `cd sdk/python && python scripts/validate-wheel.py`: passed.
- Clean-wheel score-semantics probe outside the checkout: passed.
- `cd collector/go && go test ./... -count=1`: all packages passed.
- `cd dashboard/web && npm.cmd test`: ten tests passed.
- `cd dashboard/web && npm.cmd run build`: passed; 38 modules transformed.
- `git diff --check`: passed with line-ending conversion warnings only.
- Live trace/API/Dashboard evidence: similarity 0.10 produced
  `low_retrieval_score` and `Similarity 0.10 ↑`; distance 0.10 produced no
  warning and `Distance 0.10 ↓`.

### Boundary

- S2 is complete and committed only on the local branch; it is not pushed,
  merged, versioned, or released.
- No score conversion, retriever-specific adapter, threshold tuning, new span or
  warning, delivery behavior, runtime packaging, or publication work was added.
- README prose was updated for the contract, but showcase images were not
  replaced. The existing images remain accurate; live screenshots cover this
  localized checkpoint, with release-quality refresh deferred to a selected
  Dashboard-changing release.

---

## 2026-09-11 (S1 Trustworthy Span Timing)

### Completed

- Continued from the assistant handover on branch `codex/s1-trustworthy-span-timing`, preserving all uncommitted handover documentation.
- Added public `SpanTiming` and `t.measure()` for actual-operation UTC boundaries plus monotonic elapsed time.
- Changed unmeasured post-hoc retrieval/LLM records from logging-overhead duration to null; added retrieval `duration_ms`, retained LLM `latency_ms`, and preserved prior positional argument order and `sledtrace`/`raglens` compatibility.
- Added controlled-clock, invalid-input, real-zero, exception-propagation, compatibility, and payload tests.
- Added POST → SQLite → GET coverage proving null and zero remain distinct.
- Centralized Dashboard timing resolution, rendered canonical null as `Not measured`, preserved legacy data fallback, and removed misleading trace span-sum fallback.
- Added five dependency-free Node timing tests and wired them into Dashboard CI.
- Updated root/package SDK examples, the integration guide, custom/reference examples, and a deterministic `examples.timing_demo` visual fixture.

### Validation

- `cd sdk/python && pytest -q`: 34 passed.
- `cd sdk/python && python -m build`: passed; produced wheel and sdist. The first restricted run failed while bootstrapping isolated build dependencies and then hit local error-output encoding; rerunning with normal dependency/temp access passed before project build assertions were evaluated.
- `cd sdk/python && python scripts/validate-wheel.py`: passed, including clean install, preferred/legacy imports, new timing API, CLI, and documented out-of-checkout `serve` behavior.
- `cd collector/go && go test ./... -count=1`: passed. Initial restricted cache access failed before compilation; the normal-permission rerun passed.
- `cd dashboard/web && npm.cmd test`: five tests passed.
- `cd dashboard/web && npm.cmd run build`: passed. Initial sandbox path access failed before Vite loaded configuration; normal-permission reruns passed.
- `git diff --check`: passed with line-ending conversion warnings only.
- Live non-Docker Collector/Dashboard check used an isolated ignored database: measured trace displayed 200ms total, 80ms retrieval, and 120ms LLM; unmeasured trace displayed `Not measured` for both spans. The in-app browser was left open for the user.

### Boundary

- S1 is complete in the working tree only. No commit, push, PR, version bump, tag, or release was created.
- No score, delivery, network-default, warning-rule, new-span, or standalone-runtime work was included.
- Existing README showcase screenshots were not replaced: they still represent valid diagnostic views and do not demonstrate the new unknown-timing state. Conversation/browser evidence and `examples.timing_demo` cover this checkpoint; refresh release-quality screenshots if a selected release needs the state publicly showcased.

---

## 2026-09-10 (Strategy Review and Next-Assistant Handover)

### Work recorded

- Reviewed the released repository at `906fd2999a86fac5abb538cb83ee16b79ce4cda8` and compared the product direction with official competitor documentation.
- Recorded SDK timing, distance/score semantics, strict trace-delivery behavior, heuristic diagnostic limits, uncalibrated confidence display, local network defaults, and persistence/UI follow-up findings in AI_HANDOFF.
- During the preceding read-only review, an in-memory sample with about 80ms retrieval and 120ms LLM work produced about 200ms trace duration and two 0ms recorded spans; a no-network normalization sample mapped distance 0.1 to score 0.1. Mocked delivery/serialization failures were also reproduced. These were observations, not fixes.
- At the user's request, wrote NEXT_AGENT_BRIEF for the incoming assistant and made CURRENT_TASK a focused span-timing action/acceptance contract.
- Added explicitly proposed post-v0.7 sequencing to ROADMAP and documented its non-committed status in DECISIONS.
- Condensed AI_HANDOFF into current state and evidence, leaving detailed release history in existing DEVLOG/release notes. Removed the stale pending-PyPI statement and incorrect API test path from the active handoff.
- Updated AGENTS with Chinese-response preference, context ownership, visible-validation expectations, and bounded continuation guidance.

### Scope and validation boundary

- Documentation only; no SDK, Collector, Dashboard, dependency, version, or workflow changes.
- No new commit, push, PR, tag, or release is part of this handover turn.
- Documentation validation passed: `git diff --check` exited 0 (only existing LF/CRLF conversion warnings), all 17 internal file links across the seven changed documents resolved, and the proposed roadmap anchor was checked. Scope review confirmed only documentation changes; full product builds/tests were not rerun for this prose-only change.
- Independent read-only handover review found no release-state or authority contradiction. Added explicit null/zero storage-round-trip and conditional wrapper-exception acceptance criteria to S1.
- The v0.7 production installation, full suite results, and Docker/WSL limitation below remain dated historical evidence, not validations rerun on 2026-09-10.
- No proposed fix or future milestone is marked complete. When development resumes, start with S1 in CURRENT_TASK and reassess after its acceptance criteria pass.

---

## 2026-09-09 (v0.7.0 Published and Clean-Install Validated)

### Completed

- Merged protected pull request #1 after the required `Python 3.9`, `Python 3.13`, `Go Collector`, and `Dashboard` checks passed.
- Created and pushed immutable annotated tag `v0.7.0` at release commit `58887907973aff3948d2cf3667681832f4305ec6`.
- Dispatched production publishing from that exact tag and approved the protected `pypi` environment.
- Published `sledtrace==0.7.0` to production PyPI through OIDC Trusted Publishing.
- Created GitHub Release `SledTrace v0.7.0 — External Developer Readiness`.

### Production Validation

- workflow https://github.com/Schromeo/SledTrace/actions/runs/34410674101 completed successfully
- production project: https://pypi.org/project/sledtrace/0.7.0/
- a no-cache install downloaded `sledtrace-0.7.0-py3-none-any.whl` from the production index into a new virtual environment outside the repository
- preferred `sledtrace` import reported `0.7.0`
- temporary legacy `raglens` import reported `0.7.0` with the expected deprecation warning
- `sledtrace --help`, `sledtrace serve --help`, and `sledtrace version` passed
- `sledtrace serve` outside a checkout exited 1 with the documented source-checkout guidance

### Next Evidence

- collect two external first-run attempts before selecting a v0.8 product milestone
- rerun the Docker path on a host with working virtualization
- deliberately review the four recorded Dashboard development-dependency advisories

---

## 2026-09-09 (v0.7 Final Release Preparation and Clean-Clone Evidence)

### Completed

- Enabled `main` branch protection with strict required checks `Python 3.9`, `Python 3.13`, `Go Collector`, and `Dashboard`.
- Applied protection to administrators, required linear history and resolved conversations, and disabled force pushes and branch deletion.
- Created local release branch `release/v0.7.0` so the final work can return through a protected pull request.
- Cloned the public repository into a new temporary directory and exercised the documented startup path.
- Identified that the non-Docker fallback omitted the first-run `npm` dependency-install step; selected a documentation correction rather than adding automatic dependency installation to the startup script.
- Installed locked Dashboard dependencies with `npm ci`, installed the SDK into a new virtual environment, and started the Collector and Dashboard from the clean clone.
- Generated all nine deterministic reference traces and inspected the trace list, conflict case, and weak/unsupported-answer case in a live browser.
- Replaced README screenshots that contained stale RAGLens branding, old local paths, and old demo traces.
- Added focused contributor entry points, issue/PR templates, a repeatable release checklist, and v0.7 release notes.
- Prepared final `0.7.0` Python and Dashboard version metadata without changing trace contracts, API/storage behavior, or warning rules.

### Validation Evidence

- Collector `/health` returned `{"service":"sledtrace-collector","status":"ok"}`.
- `python -m examples.reference_rag_app.run all` flushed all nine expected traces.
- `reference-rag-app-conflict` displayed 30-day versus 14-day retrieved-chunk evidence.
- `reference-rag-app-weak` displayed low-score, weak-match, and unsupported-claim diagnostics.
- Docker Desktop could not start on the validation host because WSL2 virtualization was disabled; Docker was not represented as freshly validated.
- The non-Docker clean-clone fallback passed after the now-documented `npm ci` prerequisite.
- `npm ci` reported the known baseline of 4 dependency advisories (1 moderate, 3 high); no automatic audit fix was applied.

### Next Gate

- push `release/v0.7.0`, open a pull request, and require all four CI checks
- merge through protected `main`, tag `v0.7.0`, publish through the protected production environment, and clean-install from production PyPI

### Final Local Validation

- Python SDK: 17 tests passed
- `python -m build` produced `sledtrace-0.7.0-py3-none-any.whl` and `sledtrace-0.7.0.tar.gz`
- `twine check` passed for the final wheel and sdist after using an isolated environment with the required tool and workspace read permission
- clean-wheel imports, CLI help/version, and expected non-zero out-of-checkout `serve` behavior passed
- Go Collector tests passed
- Dashboard `npm ci` completed with the recorded advisory baseline and `npm.cmd run build` passed as `sledtrace-dashboard@0.7.0`
- `git diff --check` passed; line-ending notices are host configuration warnings rather than whitespace errors

---

## 2026-09-09 (Production PyPI Trusted Publishing Protected)

### Completed

- Registered the production PyPI pending Trusted Publisher for project `sledtrace`, owner `Schromeo`, repository `SledTrace`, workflow `publish-python.yml`, and environment `pypi`.
- Created the GitHub `pypi` deployment environment.
- Required approval from GitHub user `Schromeo` before production publication jobs can proceed.
- Allowed self-review because SledTrace currently has one maintainer; disabling self-review with no second reviewer would deadlock releases.
- Disabled branch deployments and added one custom deployment policy allowing only Git tags matching `v*`.

### Validation Status

- GitHub environment API returned the required-reviewer rule for `Schromeo` with `prevent_self_review: false`.
- GitHub environment API returned `protected_branches: false` and `custom_branch_policies: true`.
- deployment-policy API returned exactly one rule: name `v*`, type `tag`.
- no workflow was triggered and no package was uploaded to production PyPI.
- no repository functional files were changed.

### Next Gate

- audit the remaining v0.7 acceptance items before declaring the project-wide `v0.7.0` release ready
- after that decision, prepare the final package, validate it, create an immutable tag, approve the protected deployment, and verify ordinary production-index installation

---

## 2026-09-08 (v0.7.0rc1 TestPyPI Candidate Published and Validated)

### Completed

- Registered the pending TestPyPI Trusted Publisher for project `sledtrace`, owner `Schromeo`, repository `SledTrace`, workflow `publish-python.yml`, and environment `testpypi`.
- Prepared Python package version `0.7.0rc1` as a prerelease candidate; v0.6.0 remains the current stable SledTrace release.
- Updated package metadata, runtime SDK metadata, installed CLI version output, validation expectations, and package README consistently.
- Kept the temporary `raglens` compatibility import and version aligned with the preferred `sledtrace` package.
- Reworded the wheel-installed `serve` limitation so it remains accurate without embedding a stale release number.
- Pushed commit `01a443f2d94c4574948edfc8a495fb997aad3de9` and annotated tag `v0.7.0rc1`.
- Published `0.7.0rc1` to TestPyPI through OIDC Trusted Publishing: https://test.pypi.org/project/sledtrace/0.7.0rc1/

### Validation Status

- Python tests passed: 17 tests with the expected legacy-import warning.
- isolated wheel/sdist build succeeded and produced `sledtrace-0.7.0rc1-py3-none-any.whl` and `sledtrace-0.7.0rc1.tar.gz`
- `twine check` passed for both artifacts
- clean-wheel installation, `sledtrace` and legacy `raglens` imports, CLI help, `sledtrace version`, and the repository-outside `serve` failure path passed
- GitHub CI run https://github.com/Schromeo/SledTrace/actions/runs/34308937339 passed Go, Dashboard, Python 3.9, and Python 3.13 jobs
- publishing run https://github.com/Schromeo/SledTrace/actions/runs/34309033246 passed the build and TestPyPI jobs while skipping production PyPI
- a no-cache install from `https://test.pypi.org/simple/` succeeded outside the source repository and reported `0.7.0rc1`
- `git diff --check` passed

### Current Boundary

- TestPyPI publication and clean-index validation are complete
- no package has been uploaded to production PyPI yet
- the next external step is production Trusted Publisher registration followed by the final v0.7.0 go/no-go decision
- ordinary `pip install sledtrace` remains unsupported until production PyPI publication and clean-install validation succeed

---

## 2026-09-08 (v0.7 Python Trusted Publishing Preparation)

### Completed

- Confirmed the public PyPI and TestPyPI APIs had no `sledtrace` project record; the official PyPI project URL displayed a 404 page.
- Added project homepage, documentation, repository, and issue URLs to the Python package metadata.
- Added the MIT license inside the Python package build context and verified it appears in the wheel.
- Added `twine check` to both Python CI matrix jobs.
- Added `.github/workflows/publish-python.yml` with manual validate, TestPyPI, and PyPI targets.
- Restricted OIDC `id-token: write` permission to the selected package-index upload job.
- Added tag/package-version matching for real publication targets.
- Pinned release-workflow actions to the verified commits corresponding to checkout v7.0.1, setup-python v7.0.0, upload-artifact v7.0.1, download-artifact v8.0.1, and gh-action-pypi-publish v1.14.2.
- Created and pushed commit `4c6108c0c0ad35e060b2dca9a439bbb425d33717`.

### Validation Status

- local package build succeeded
- `twine check` passed for the wheel and source distribution
- clean-wheel imports and installed CLI validation passed
- isolated Pytest validation passed with 17 tests and the expected legacy-import warning
- GitHub CI run https://github.com/Schromeo/SledTrace/actions/runs/34306672732 passed all four jobs, including `twine check` on Python 3.9 and 3.13
- validate-only publishing run https://github.com/Schromeo/SledTrace/actions/runs/34306741532 succeeded in 25 seconds
- the publishing dry-run retained one `python-package` artifact; TestPyPI and PyPI jobs were both skipped

### Decision and Next Gate

- v0.7.0 is the intended first production PyPI release; do not rebuild or retroactively publish a different v0.6.0 artifact
- no package has been uploaded to TestPyPI or PyPI
- at that point, the next gate was owner-side pending Trusted Publisher registration on TestPyPI for `Schromeo/SledTrace`, workflow `publish-python.yml`, environment `testpypi`; it was completed later the same day

---

## 2026-09-08 (v0.7 Initial Cross-Stack CI Baseline)

### Completed

- Added `.github/workflows/ci.yml` for pushes to `main`, pull requests, and manual dispatch.
- Added Python 3.9 and 3.13 matrix jobs covering `pytest -q`, wheel/sdist build, and clean-wheel validation.
- Added independent Go Collector tests and Dashboard production-build jobs.
- Added a live CI badge to the root README.
- Created and pushed commit `9d6435ce226e7701d24a133958fa1f32e8a58cac` with message `ci: add cross-stack validation workflow`.
- Verified GitHub Actions run https://github.com/Schromeo/SledTrace/actions/runs/34304017537 completed successfully.
- Opened the successful run as visible browser evidence; no Dashboard screenshot was changed because this slice did not alter Dashboard UI behavior.

### Validation Status

- GitHub Actions total duration: 41 seconds.
- Python 3.9: passed in 26 seconds.
- Python 3.13: passed in 21 seconds.
- Go Collector: passed in 37 seconds.
- Dashboard: passed in 11 seconds.
- Local Python tests passed with 17 tests and the expected legacy-import warning.
- Local package build, clean-wheel validation, Go tests, and Dashboard build passed after rerunning outside host-specific sandbox/cache restrictions.

### Known Follow-up

- `main` branch protection and required-check enforcement are not configured yet.
- Clean-clone and Docker/local first-run validation remain pending.
- `npm audit` reports four transitive development-dependency advisories: one moderate and three high. They are reached through the current Vite/Babel/PostCSS build toolchain and should be handled in a focused dependency-update slice rather than silently ignored or mixed into the initial CI commit.

---

## 2026-09-08 (v0.6.0 Release Closure and v0.7 Direction Selected)

### Completed

- Created release commit `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e` with message `feat(cli): complete SledTrace v0.6.0 startup UX`.
- Included repository hygiene in the v0.6 commit by removing tracked Python bytecode/cache artifacts and expanding `.gitignore` coverage for package-test virtual environments.
- Created and pushed annotated tag `v0.5.0` at `b3cad60a10636dbf7a5d371f51bac0c04a4af936`.
- Created and pushed annotated tag `v0.6.0` at `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e`.
- Published the v0.5.0 GitHub Release:
  - https://github.com/Schromeo/SledTrace/releases/tag/v0.5.0
- Published the v0.6.0 GitHub Release:
  - https://github.com/Schromeo/SledTrace/releases/tag/v0.6.0
- Confirmed both releases are non-draft, non-prerelease releases.
- Selected **v0.7.0 — External Developer Readiness** as the next planned milestone.
- Established CI, clean-clone first-run evidence, contributor readiness, and user-visible Dashboard validation as the v0.7 priority order.
- Elevated PyPI publication to a v0.7 decision gate without claiming it is currently available.
- Established screenshot policy: conversation evidence for UI checkpoints, README updates only for material visible changes, and release-quality refreshes for releases that change the Dashboard.
- Reconciled root README, SDK package README, release notes, and AI-context documents with the actual published state.

### Validation Status

- v0.6 release validation remains the accepted 2026-09-07 validation record below.
- This post-release closure is documentation-only and does not change runtime behavior.
- No Dashboard screenshots were refreshed because v0.6 did not change Dashboard UI behavior.
- PyPI publication was not performed.

### Notes

- These post-release documentation updates occur after the immutable v0.6.0 tag and do not rewrite the released tag.
- GitHub Release bodies should remain synchronized with the corrected release-note files after this documentation update is reviewed and published.

---

## 2026-09-07 (v0.6.0 Local CLI / Startup UX Completed)

### Completed

- Added a package-installed `sledtrace` CLI entry point via `project.scripts` in the Python package.
- Added the first CLI module at `sdk/python/sledtrace/cli.py` with `serve` and `version` subcommands.
- Kept `sledtrace serve` minimal and compatibility-safe by delegating to the existing repo-local startup script.
- Added a regression test covering `sledtrace.cli` import and CLI presence.
- Replaced module-location-based repository inference with explicit upward discovery from the current working directory.
- Required `AGENTS.md`, `docker-compose.yml`, and `scripts/start-sledtrace.py` as checkout markers.
- Added clear non-zero guidance for `sledtrace serve` outside a source checkout.
- Expanded CLI help to document the source-checkout limitation.
- Aligned Python package, public CLI, SDK trace metadata, demo metadata, and Dashboard package versions to `0.6.0`.
- Expanded clean-wheel validation to execute installed CLI help, version, and expected `serve` failure behavior.
- Added unit coverage for repository discovery, outside-checkout guidance, and repo-local startup delegation without launching child services.
- Corrected the SDK README example so `flush()` runs after the trace context exits.
- Added `docs/releases/V0_6_0.md` and reconciled current-status documentation.

### Validation Status

Validated successfully:

- `python -m pip install -e .` succeeded
- `sledtrace --help` displayed the CLI commands
- `sledtrace serve --help` documented the source-checkout boundary
- `sledtrace version` printed `0.6.0`
- `pytest -q` passed with 17 tests; output included the expected legacy-import deprecation warning and an environment-specific `.pytest_cache` permission warning
- `python -m build` produced the `sledtrace-0.6.0` wheel and sdist
- `python scripts/validate-wheel.py` passed preferred/legacy imports and all installed CLI checks
- wheel-installed `sledtrace serve` outside a checkout returned the documented guidance and a non-zero exit
- `go test ./... -count=1` passed in `collector/go`
- `npm.cmd run build` passed in `dashboard/web`
- repo-local detection and delegation validation passed without leaving long-running processes

### Notes

- The CLI milestone is intentionally small and does not alter collector protocol, warning logic, or trace schema.
- The package-level compatibility and SledTrace-first import path remain in place.
- The wheel intentionally does not bundle Collector, Dashboard, Docker, or platform-specific runtime assets.
- At milestone-completion time, no Git tag, GitHub release, or PyPI publication had been created. The tag and GitHub Release were subsequently published on 2026-09-08; PyPI publication remains incomplete.

---

## 2026-09-07 (v0.5.0 Python SDK Distribution / Packaging Readiness)

### Completed

- Updated SDK package metadata to SledTrace-first naming and version `0.5.0`.
- Added public `__version__` export at the `sledtrace` package root.
- Preserved temporary `raglens` compatibility shim and deprecation warning for migration.
- Added packaging/compatibility coverage under `sdk/python/tests/`.
- Added local wheel validation script at `sdk/python/scripts/validate-wheel.py`.
- Updated SDK and root README docs for local wheel installation and SledTrace-first usage.
- Documented v0.5.0 milestone in the release notes at `docs/releases/V0_5_0.md`.

### Validation Status

Validated successfully with the required local package workflow:

- `python -m build` succeeded
- clean venv wheel install succeeded
- `import sledtrace` succeeded
- `from sledtrace import trace` succeeded
- legacy `raglens` import succeeded
- `pytest` passed in `sdk/python`
- `go test ./... -count=1` passed in `collector/go`
- `npm run build` passed in `dashboard/web`

### Notes

- No warning engine changes were made.
- No collector API contract changes were made.
- No storage schema changes were made.
- No dashboard data contract changes were made.
- No new span types were introduced.
- No PyPI upload step is part of this release.

---

## 2026-07-15 (v0.4.1 Rebrand)

### Completed

- Rebranded active project name from RAGLens to SledTrace across product docs and UI labels.
- Added rebrand migration guide:
  - `docs/REBRANDING.md`
- Added release notes:
  - `docs/releases/V0_4_1.md`
- Added new primary startup launcher:
  - `scripts/start-sledtrace.py`
- Kept legacy startup command via compatibility wrapper:
  - `scripts/start-raglens.py`
- Added preferred collector env var support in SDK and docs:
  - `SLEDTRACE_COLLECTOR_URL`
- Kept legacy collector env var support for this release:
  - `RAGLENS_COLLECTOR_URL` (deprecated)
- Updated dashboard and compose branding to SledTrace while keeping collector port `4319`.
- Kept SQLite table schema and contracts unchanged.

### Notes

- v0.4.1 is compatibility-preserving and does not change warning logic, API semantics, or storage schema.
- v0.4.0 remains historically accurate as a release originally published under the RAGLens name.

## 2026-07-14 (v0.4.0 Local Release / First-Run DX)

### Completed

- Added Docker local stack at repository root:
  - `docker-compose.yml`
  - collector service on `:4319`
  - dashboard service on `:5173`
  - persistent Docker volume `sledtrace_data` for SQLite storage
- Added collector container build:
  - `collector/go/Dockerfile`
- Added dashboard container build and static serving:
  - `dashboard/web/Dockerfile`
  - `dashboard/web/nginx.conf`
- Added release/install support files:
  - `.dockerignore`
  - `.env.example`
  - `LICENSE` (MIT)
- Added v0.4 docs:
  - `docs/releases/V0_4_0.md`
  - `docs/demo/REFERENCE_RAG_APP.md`
- Updated first-run guidance:
  - `README.md`
  - `docs/demo/SMOKE_TEST.md`
  - `docs/ai-context/ROADMAP.md`
  - `docs/ai-context/CURRENT_TASK.md`
  - `docs/ai-context/AI_HANDOFF.md`
- Added optional local health checker:
  - `scripts/check-raglens.py`

### Validation Commands

Planned v0.4 validation commands:

```bash
cd collector/go
go test ./... -count=1

cd dashboard/web
npm run build

cd ..\..
docker compose up --build
curl http://localhost:4319/health

cd sdk/python
pip install -e .
python -m examples.reference_rag_app.run all
```

### Observed Results

- `cd collector/go && go test ./... -count=1` passed.
- `cd dashboard/web && npm run build` passed.
- `docker compose up --build` built both collector and dashboard images and started containers successfully.
- `curl http://localhost:4319/health` returned HTTP 200 with JSON `{"service":"sledtrace-collector","status":"ok"}`.
- `curl http://localhost:5173` returned HTTP 200 HTML for dashboard app.
- `cd sdk/python && pip install -e .` passed in local `.venv`.
- `python -m examples.reference_rag_app.run all` completed and flushed all expected traces:
  - `reference-rag-app-refund`
  - `reference-rag-app-conflict`
  - `reference-rag-app-wrong-window`
  - `reference-rag-app-processing-range`
  - `reference-rag-app-wrong-processing-range`
  - `reference-rag-app-damaged`
  - `reference-rag-app-digital`
  - `reference-rag-app-subscription`
  - `reference-rag-app-weak`
- Collector list API verification confirmed all 9 expected reference trace names were present.
- Docker cleanup commands passed:
  - `docker compose down`
  - `docker compose down -v`

### Notes

- v0.4.0 keeps warning behavior deterministic-first.
- No SDK trace API changes were made.
- No collector API contract changes were made.
- No storage schema changes were made.
- No dashboard data contract changes were made.

## 2026-07-08 (v0.3.5 Diagnostic Quality Hardening Completed)

### Completed

- Added `sdk/python/examples/reference_rag_app/` as a thin deterministic-first reference integration app.
- Added local policy corpus for reference integration validation under `sdk/python/examples/reference_rag_app/docs/`.
- Completed mixed raw retrieval output normalization flow with `normalize_chunks()` in the reference app.
- Added optional real LLM validation path while keeping deterministic-first default behavior.
- Hardened warning engine numeric extraction to support natural-language ranges:
  - `5 to 10 business days`
  - `2 to 3 business days`
  - `10 to 20 business days`
  - `1 to 2 years`
  - `24 to 48 hours`
- Preserved prior deterministic numeric mismatch guardrails:
  - no false-positive numeric mismatch for elapsed-time phrasing like `20 days ago`
  - mismatch still fires for unsupported policy windows like `45 days` vs retrieved `30 days`
  - mismatch suppression remains when answer numeric value is directly supported by at least one retrieved chunk
- Hardened conflicting chunk candidate selection with deterministic relevance-aware ranking and query gating.
- Added deterministic topic classifier for numeric expressions and topic gating in conflicting chunk selection.
- Added query-intent compatibility for conflicting chunk diagnostics so damaged-item queries do not surface unrelated refund-processing conflicts.
- Added/updated warning tests for:
  - numeric range mismatch behavior
  - matching-range non-mismatch behavior
  - query-relevant conflicting chunk preference and noise suppression
- Cleaned deterministic demo answers for `conflict`, `digital`, and `damaged` to reduce avoidable grounding-noise.

### Validation

Validated with:

```bash
cd collector/go
go test ./... -count=1

cd sdk/python
python -m examples.reference_rag_app.run processing-range
python -m examples.reference_rag_app.run wrong-processing-range
python -m examples.reference_rag_app.run all

cd sdk/python
python -m examples.real_llm_rag_demo all
```

Observed results:

- collector warning-engine tests passed after numeric/range/conflict hardening updates
- reference integration traces were generated and persisted successfully
- wrong-window and wrong-processing-range still trigger `numeric_mismatch` as expected
- weak case continues to trigger retrieval + grounding diagnostics
- subscription case remains low-noise and typically warning-free

Observed final reference app behavior:

- `damaged` produces no warning after query-intent/topic compatibility gating
- `processing-range` still surfaces relevant refund-processing conflicts
- `wrong-processing-range` still surfaces `numeric_mismatch`
- `weak` still surfaces `answer_not_grounded`

### Notes

- v0.3.5 is complete as a deterministic warning-quality and integration-hardening slice.
- warning generation remains collector-side and deterministic-first.
- no storage schema, dashboard schema, or SDK trace API changes were required for this hardening pass.

## 2026-07-06 (v0.3 Backend Test Coverage Added)

### Completed

- Added focused Go unit tests for the v0.3 warning engine.
- Covered core diagnostic rules:
  - `numeric_mismatch`
  - `weak_query_chunk_overlap`
  - `answer_not_grounded`
  - `conflicting_chunks`
- Added SQLite storage round-trip tests for Warning Schema v2 payloads.
- Verified that v2 warning fields persist and load correctly:
  - `schema_version`
  - `rule_id`
  - `rule_version`
  - `category`
  - `confidence`
  - `explanation`
  - `evidence`
  - `diagnostics`
  - `signals`
  - `recommended_action`
- Added migration coverage for legacy `warnings` tables missing v2 columns.
- Added API handler tests to verify that:
  - `POST /api/traces` generates v0.3 warnings
  - `GET /api/traces/{trace_id}` returns v2 warning fields for dashboard consumption

### Validation

Validated with:

```bash
cd collector/go
go test ./... -count=1
```

Observed result:

- warning engine tests passed
- storage round-trip tests passed
- legacy warning table migration test passed
- API handler tests passed

### Notes

- v0.3 diagnostic intelligence is now covered at the rule, storage, and API layers.

## 2026-07-06 (v0.3 Diagnostic Intelligence Core Implemented and Smoke-Tested)

### Completed

- Implemented Warning Schema v2 defaults and evidence-backed warning enrichment in the collector.
- Implemented or upgraded the first v0.3 diagnostic rules:
  - `weak_query_chunk_overlap`
  - `numeric_mismatch`
  - `answer_not_grounded` with v2 evidence-backed payloads
  - `conflicting_chunks` with v2 evidence-backed payloads
- Added deterministic demo cases in `sdk/python/examples/diagnostic_quality_demo.py` for:
  - `numeric_mismatch`
  - `weak_query_chunk_overlap`
  - `answer_not_grounded`
  - `conflicting_chunks`
- Updated the dashboard warning detail UI to show:
  - evidence preview blocks
  - compared numeric values for `numeric_mismatch`
  - recommended action labeling
  - responsive warning detail polish

### Validation

Validated with:

```bash
cd collector/go
go test ./...

cd dashboard/web
npm run build

cd sdk/python
python -m examples.diagnostic_quality_demo all
```

Observed results:

- Go collector packages compiled successfully.
- Dashboard TypeScript and production build completed successfully.
- All four v0.3 diagnostic demo cases ran successfully and flushed traces:
  - `numeric_mismatch`
  - `weak_query_chunk_overlap`
  - `answer_not_grounded`
  - `conflicting_chunks`

### Notes

- v0.3 core diagnostic intelligence is now implemented and smoke-tested.
- The milestone remains local-first and deterministic-first.
- Current span coverage remains limited to `retrieval` and `llm` spans.

## 2026-07-06 (v0.3 Diagnostic Intelligence Spec Added)

### Completed

- Added `docs/product/V0_3_DIAGNOSTIC_INTELLIGENCE.md`.
- Defined v0.3 as the milestone that upgrades warning flags into evidence-backed diagnostic insights.
- Captured the first structured design for:
  - Warning Schema v2
  - EvidenceItem schema
  - DiagnosticObject schema
- Defined the first enhanced warning set:
  - `low_retrieval_score_v2`
  - `weak_query_chunk_overlap`
  - `answer_not_grounded_v2`
  - `numeric_mismatch`
  - `conflicting_chunks_v2`
- Locked scope boundaries so v0.3 remains local-first, deterministic-first, and limited to current `retrieval` and `llm` spans.

### Notes

- Explicitly out of scope: LangChain, LlamaIndex, PyPI, Docker, CLI, agent spans, tool spans, memory spans, cloud, auth, and LLM-as-judge.
- The document is a product and schema design spec only. No implementation work was started.

## 2026-07-03 (Future Agent Harness Observability Direction Documented)

### Completed

- Added documentation-only positioning updates for future agent harness observability.
- Clarified that future direction may include:
  - running traces for multi-step harness executions
  - partial span ingestion
  - future `agent` / `tool` / `retry` span types
  - diagnostics for agent loops, oscillation, retry storms, and no-progress execution
- Explicitly marked all of the above as not implemented in current SledTrace.

## 2026-07-02 (v0.2 Developer Integration / Local SDK Onboarding Completed)

### Completed

- Marked v0.2 Developer Integration / Local SDK Onboarding as completed.
- Finalized onboarding and integration documentation:
  - `docs/product/USER_ONBOARDING.md`
  - `docs/integrations/PYTHON_SDK_GUIDE.md`
- Added `sdk/python/examples/custom_pipeline_demo.py` and validated dashboard visibility for `custom-rag-pipeline`.
- Added and polished `scripts/start-sledtrace.py` as a cross-platform repo-local startup helper.
- Updated `README.md` with two quickstart paths:
  - Path A: built-in demo
  - Path B: own RAG app integration
- Added root README documentation map to separate user docs from maintainer docs.
- Completed SDK packaging hygiene:
  - `sdk/python` package version set to `0.2.0`
  - added `sdk/python/README.md`
  - `pyproject.toml` `readme` points to the local SDK README
  - editable install remains the supported v0.2 path

### Validation

Validated the v0.2 integration flow with:

```bash
python scripts/start-sledtrace.py
cd sdk/python
python -m examples.custom_pipeline_demo
python -m examples.local_rag_demo.run_demo trace-all
```

Observed results:

- Dashboard showed `custom-rag-pipeline`.
- Dashboard showed built-in local RAG demo traces and warning-focused cases.

### Notes

- Current implemented span types remain `retrieval` and `llm` only.
- Current warning rules remain:
  - `no_retrieved_chunks`
  - `low_retrieval_score`
  - `duplicate_chunks`
  - `conflicting_chunks`
  - simplified `answer_not_grounded`
- v0.3 recommended next focus is RAG Quality Analysis / Diagnostic Intelligence.

## 2026-07-02 (v0.2 Developer Integration / Local SDK Onboarding Core Complete)

### Completed

- Completed the core v0.2 Developer Integration / Local SDK Onboarding work.
- Added and refined user onboarding documentation:
  - `docs/product/USER_ONBOARDING.md`
  - `docs/integrations/PYTHON_SDK_GUIDE.md`
- Added `sdk/python/examples/custom_pipeline_demo.py` as a minimal deterministic integration example.
- Added and polished `scripts/start-sledtrace.py` as a cross-platform repo-local startup helper.
- Updated `README.md` to document two quickstart paths:
  - Path A: try SledTrace with the built-in demo
  - Path B: use SledTrace with your own RAG app

### Validation

Validated the v0.2 integration flow with the following commands:

```bash
python scripts/start-sledtrace.py
cd sdk/python
python -m examples.custom_pipeline_demo
python -m examples.local_rag_demo.run_demo trace-all
```

Observed result:

- `custom-rag-pipeline` was visible in the dashboard.
- Built-in local RAG demo traces were visible in the dashboard.
- Warning-focused demo traces and warning cards were visible in the dashboard.

### Notes

- Current implemented span types remain `retrieval` and `llm` only.
- Current warning rules remain:
  - `no_retrieved_chunks`
  - `low_retrieval_score`
  - `duplicate_chunks`
  - `conflicting_chunks`
  - simplified `answer_not_grounded`
- v0.2 is core complete and in final documentation polish.

## 2026-07-02 (Startup Guidance Sync)

### Completed

- Unified startup guidance across `README.md`, `docs/product/USER_ONBOARDING.md`, and `docs/integrations/PYTHON_SDK_GUIDE.md`.
- Standardized the recommended v0.2 local startup command to `python scripts/start-sledtrace.py`.
- Kept manual collector/dashboard startup steps as fallback paths where useful.

## 2026-07-02 (Repo-Local Startup Helper Polish)

### Completed

- Added `scripts/start-sledtrace.py` as the recommended repo-local v0.2 startup helper.
- Kept the helper dependency-free and cross-platform:
  - starts collector from `collector/go`
  - starts dashboard from `dashboard/web`
  - uses `npm.cmd` on Windows and `npm` on macOS/Linux
  - terminates the sibling process if either child exits first
  - handles Ctrl+C / SIGTERM with terminate-then-kill cleanup
- Updated `docs/integrations/PYTHON_SDK_GUIDE.md` to document:
  - the repo-local startup helper
  - Bash and PowerShell collector URL environment variable setup
  - explicit `POST {collector_url}/api/traces` flush target
  - collector-running prerequisite for the custom pipeline demo

## 2026-07-02 (Python SDK Guide)

### Completed

- Added `docs/integrations/PYTHON_SDK_GUIDE.md` as a practical API usage guide for the current Python SDK.
- Documented only the currently implemented v0.2 SDK surface:
  - `trace(...)`
  - `retrieval(...)`
  - `llm(...)`
  - `flush(...)`
- Captured current SDK behaviors and limitations:
  - prompt and messages support for LLM spans
  - retrieval chunk shallow-copy and defaulting behavior
  - flush timing requirements
  - trace error-state behavior when exceptions escape the context
  - local editable install as the current supported integration path

## 2026-07-02 (v0.2 User Onboarding Guide)

### Completed

- Added `docs/product/USER_ONBOARDING.md` for Developer Integration / User Onboarding.
- Documented practical integration for existing RAG pipelines using the Python SDK (without modifying `local_rag_demo`).
- Captured clear positioning boundaries:
  - SledTrace is a local-first tracing and debugging layer for RAG pipelines.
  - SledTrace is not a chatbot framework, vector DB, training framework, hosted platform, or app replacement.
- Included concrete guidance for:
  - local service startup (collector + dashboard)
  - wrapping request paths with `trace(...)`
  - logging `retrieval` and `llm` spans
  - calling `flush()` after exiting the trace context
  - chunk object field expectations (required vs recommended)
  - current warning analysis scope and current non-goals/limitations

## 2026-06-30 (Positioning Update: RAG Debugger -> TraceForge Direction)

### Completed

- Clarified long-term direction: SledTrace remains a local-first visual debugger for RAG pipelines in v0.1, while the tracing core is positioned to evolve toward TraceForge-style AI application harness observability.
- Documented RAG as the first vertical slice because retrieval quality, context quality, conflicting evidence, and grounding are common AI failure points.
- Updated docs to separate current implementation from future direction:
  - v0.1 remains completed
  - v0.2 remains Developer Integration / User Onboarding
  - harness-level spans (tool, memory, verification, human feedback) remain future possible directions

## 2026-06-30 (Platform-Specific Script Folders)

### Completed

- Split repository startup scripts into platform-specific folders:
  - `scripts/windows` for PowerShell entry points
  - `scripts/mac` for Bash entry points
- Added macOS shell wrappers for collector, dashboard, demo trace generation, and smoke testing.
- Added one-click `start-all` launchers for macOS and Windows to start collector and dashboard together.
- Replaced the split root launchers with a single cross-platform `scripts/start-all.py` entry point.
- Updated README quickstart and shortcut commands to point at the cross-platform one-click entry point.

### Notes

- macOS scripts are executable Bash entry points and can be run with `bash ./scripts/mac/...`.
- Windows scripts remain PowerShell-based and now live under `scripts/windows`.

## 2026-06-22 (Dashboard UI Polish + Final v0.1 Release Prep)

### Completed

- Dashboard sidebar trace list: added text truncation for query and answer fields
  - Query: max 2 lines, ellipsis overflow
  - Answer: max 3 lines, ellipsis overflow
  - Ensures uniform card heights regardless of content length
- Final answer card in trace detail:
  - Repositioned from floating window to grid layout with Query/Duration/Warnings
  - Added inline vertical resizing with `resize: vertical` CSS
  - Scrollable content area for long answers
  - Removed nested border structure (single outer card border)
  - Initial height: 92px min, 320px max, user-adjustable
- README aligned with current screenshots and feature set
- All dashboard, SDK, collector, and documentation paths verified and consistent

### Notes

- Sidebar truncation prevents layout explosion when some traces have very long final answers
- Final answer card resizing allows users to expand/collapse inline without moving page flow
- UI changes improve dashboard readability for both quick scanning (list view) and detailed inspection (detail view)

## 2026-06-22 (Demo Packaging Progress + Final Smoke Validation)

### Completed

- Ran startup and demo scripts from repository root:
  - `scripts/start-collector.ps1`
  - `scripts/start-dashboard.ps1`
  - `scripts/demo-trace-all.ps1`
  - `scripts/smoke.ps1`
- Verified `trace-all` completed with `Generated traces: 5` and `Failed traces: 0`.
- Verified expected warning mapping via collector API for generated trace IDs.
- Aligned README and demo docs command paths with actual directories:
  - collector path -> `collector/go`
  - dashboard path -> `dashboard/web`
- Added cross-links across demo docs:
  - `LOCAL_RAG_DEMO.md` <-> `WARNING_RULES.md` <-> `SMOKE_TEST.md`

### Acceptance Snapshot

- Collector health: pass
- Dashboard starts: pass
- trace-all runs: pass
- no_match warning: pass
- low_score warning: pass
- duplicate warning: pass
- conflict warning: pass
- hallucinated warning: pass
- Trace detail readable: pass
- README commands accurate: pass

### Notes

- Conflict trace can include an additional warning alongside `conflicting_chunks` in some runs.
- For acceptance, conflict case validation checks that `conflicting_chunks` is present.

## 2026-06-21 (Real Local RAG Demo Documentation and Milestone Closeout)

### Completed

- Finalized documentation for the Real Local RAG Demo milestone.
- Updated local demo runbook in `sdk/python/examples/local_rag_demo/README.md` for new developers.
- Synced milestone-complete status across AI handoff, roadmap, and current task docs.
- Documented verified command set and expected warning-target case mapping.

### What Was Built (Milestone Summary)

- local markdown policy corpus
- local loader
- deterministic chunker
- TF-IDF plus cosine retriever
- simple local answerer
- SDK trace integration to collector on `:4319`
- dashboard verification of real retrieval traces and warning cards

### Why TF-IDF Was Chosen

- Fully local-first and easy to run in v0.1.
- Transparent scoring behavior for debugging and explanation.
- Minimal dependency and infrastructure complexity.
- Good baseline before semantic retriever comparison.

### What Was Verified

- End-to-end flow from SDK flush to collector to SQLite to dashboard.
- Real retrieved chunks include ids, source, rank, text, and scores.
- Warning cards render from real retrieval output, not only synthetic fixtures.

### Warning Rules Triggered In Verified Cases

- `no_retrieved_chunks` via `no_match`
- `low_retrieval_score` via `low_score`
- `duplicate_chunks` via `duplicate`
- `conflicting_chunks` via `conflict`
- simplified `answer_not_grounded` via `hallucinated`

### Deferred By Design

- LangChain adapter integration
- LlamaIndex adapter integration
- Vector database integration
- External embedding providers

These remain intentionally deferred until DX hardening and test coverage improve.

## 2026-06-15 (Real Local RAG Milestone Completed)

### Completed

- Marked Real Local RAG Demo milestone as completed across milestone, roadmap, task, and handoff docs.
- Captured completed implementation scope:
  - local markdown policy documents
  - local document loader
  - deterministic chunking
  - TF-IDF + cosine retriever
  - simple local answerer
  - demo case matrix
  - traced integration through existing SDK schema
  - collector ingestion on `:4319`
  - dashboard verification
  - warning trigger verification on real retrieval output

### Notes

- Added explicit demo command runbook to the milestone and handoff docs.
- Shifted active focus to post-milestone hardening (warning explanations, tests, semantic retriever evaluation).

## 2026-06-15 (Real Local RAG Docs)

### Completed

- Added `docs/ai-context/REAL_LOCAL_RAG_MILESTONE.md` to define active milestone scope, exit criteria, runbook, and non-goals.
- Added `docs/architecture/LOCAL_RETRIEVAL_BASELINE.md` to document current local retrieval implementation (chunking + TF-IDF + cosine).

### Notes

- Current retriever baseline is intentionally lexical and transparent.
- Framework adapters remain deferred until Real Local RAG Demo is validated.

## 2026-06-15 (Docs Sync)

### Completed

- Updated core docs to reflect that Warning Engine / Diagnosis Layer MVP is complete.
- Synced status across README, roadmap, handoff, current task, architecture, and product docs.
- Marked Real Local RAG Demo as the next active milestone.

### Notes

- Warning rules now documented as implemented: `no_retrieved_chunks`, `low_retrieval_score`, `duplicate_chunks`, `conflicting_chunks`, simplified `answer_not_grounded`.
- `sdk/python/examples/warning_rules_demo.py` documented as primary warning smoke test.

## 2026-06-15

### Completed

- Updated `sdk/python/examples/warning_rules_demo.py` to call `print_and_flush(t)` after exiting each `with trace(...)` block.
- Ensured all five warning-rule smoke demos finalize trace lifecycle before serialization and POST.

### Validation

Ran all warning demos:

```bash
cd sdk/python
python -m examples.warning_rules_demo all
```

Observed result:

- All five demos still return `warnings_generated: 1`.
- `trace.ended_at` is now populated (no longer `null`) across all demo payloads.
- `trace.duration_ms` is now populated as `0` for this fast local smoke run (no longer `null`).

### Notes

This keeps demo payload timing fields compatible with timeline rendering and future latency-oriented warning logic.

## 2026-06-13

### Completed

- Added Warning Engine in the Go collector.
- Implemented the first diagnosis rule: `conflicting_chunks`.
- Collector now generates and persists warnings after storing trace payloads.
- Dashboard trace detail now renders real warning cards.
- Refund policy demo now reliably triggers one warning for conflicting `30 days` vs `14 days` refund-policy chunks.

### Validation

Collector health check:

```powershell
Invoke-RestMethod http://localhost:4319/health
```

Demo execution:

```bash
cd sdk/python
python -m examples.refund_policy_demo
```

Observed result:

- Trace is ingested and persisted.
- `conflicting_chunks` warning is generated and stored.
- Warning appears on dashboard trace detail.

### Notes

SledTrace now has an end-to-end diagnosis path from ingestion to UI rendering.

The warning engine is intentionally incremental in v0.1: start with one high-signal rule, validate the full loop, then add additional rules.

### Next Step

Expand warning coverage with the next rules:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- simplified `answer_not_grounded`

## 2026-05-15

### Completed

- Defined the v0.1 product direction for SledTrace.
- Confirmed that SledTrace starts as a local-first visual debugger for RAG pipelines.
- Established the long-term architecture direction: start with RAG debugging, while keeping the internal model compatible with future AgentOps/TraceForge-style tracing.
- Created the initial product specification in `docs/product/PRODUCT_SPEC.md`.
- Defined the initial trace/span data model in `docs/architecture/TRACE_DATA_MODEL.md`.
- Decided that the developer-facing Python API should stay simple, while the internal representation uses traces and spans.
- Defined the core v0.1 entities:
  - Trace
  - Span
  - Retrieval chunk
  - LLM span
  - Warning
- Defined the initial SQLite schema for:
  - `traces`
  - `spans`
  - `warnings`
- Implemented the first minimal Python SDK.
- Added a `trace()` context manager.
- Added support for recording retrieval spans.
- Added support for recording LLM spans.
- Created the refund policy demo.
- Verified that the SDK can generate a complete trace payload locally.
- Pushed the initial documentation and SDK code to GitHub.

### Key Decisions

- SledTrace v0.1 will use a local-first architecture.
- SQLite will be the default local storage backend.
- The Python SDK will expose a simple API:
  - `trace(name)`
  - `t.retrieval(...)`
  - `t.llm(...)`
- Internally, SledTrace will represent RAG pipeline activity using a trace/span model.
- A trace represents one complete RAG request.
- A span represents one step inside the pipeline, such as retrieval or LLM generation.
- The initial span types are:
  - `retrieval`
  - `prompt`
  - `llm`
  - `custom`
- Warning rules will start as lightweight heuristics, not ML-based evaluation.

## 2026-05-14

### Completed

- Chose SledTrace as the first product cut.
- Defined the long-term path: SledTrace -> AgentOps Lite -> TraceForge.
- Decided to start with a local-first visual debugger for RAG pipelines.
- Created the initial repository documentation plan.

### Key Decisions

- Start narrow with RAG debugging instead of building a full LLMOps platform.
- Keep v0.1 local-first.
- Prioritize usability, visual clarity, and easy setup.
- Use project docs as long-term memory for AI collaboration.

### Next

- Create the initial repo structure.
- Write PRODUCT_SPEC.md.
- Design the trace/span data model.
- Decide the first implementation order.

Ran the refund policy demo locally:

```bash
cd sdk/python
python -m examples.refund_policy_demo
```

The SDK successfully generated a trace payload containing:

- One trace named refund-policy-qa
- One retrieval span named search_refund_docs
- Two retrieved chunks:
  - refund_policy_new.md, version 2026, refund window 30 days
  - refund_policy_old.md, version 2024, refund window 14 days
- One LLM span named generate_answer
- A final answer using the outdated 14 days refund window

### Notes

This is the first runnable milestone for SledTrace.

The project now has both:

- A documented product and architecture direction
- A working Python SDK prototype that can generate structured trace payloads

The current SDK only prints trace JSON locally.

The next step is to build the Go collector so the SDK can send traces to a local HTTP endpoint and persist them in SQLite.

### Next Step

Build the local Go collector.

Initial collector scope:

- GET /health
- POST /api/traces
- SQLite persistence
- GET /api/traces
- GET /api/traces/{trace_id}

## 2026-05-15

### Completed

- Implemented the initial Go collector.
- Added `GET /health`.
- Added `POST /api/traces`.
- Added SQLite-backed local persistence.
- Added storage for traces and spans.
- Verified that the collector can receive a Python SDK-generated trace payload.
- Verified that the collector stores trace data in local SQLite.

### Validation

Started the collector locally:

```bash
cd collector/go
go run ./cmd/sledtrace-collector
```

Checked collector health:

```powershell
Invoke-RestMethod http://localhost:4319/health
```

Posted a sample trace payload:

```powershell
Invoke-RestMethod `
  -Uri http://localhost:4319/api/traces `
  -Method POST `
  -ContentType "application/json" `
  -InFile sample_trace.json
```

The collector returned:

```json
{
  "status": "stored",
  "warnings_generated": 0
}
```

### Notes

The local collector can now receive and persist trace payloads.

The next step is to add a flush() method to the Python SDK so demo traces can be sent directly to the collector without manually copying JSON into a file.

### Commit

```bash
git add .
git commit -m "feat(collector): add Go collector with SQLite persistence"
git push
```

## 2026-05-18

### Completed

- Added `flush()` support to the Python SDK.
- Added `collector_url` support to the trace context manager.
- Updated the refund policy demo to send traces directly to the local collector.
- Verified that the Python SDK can POST trace payloads to `POST /api/traces`.
- Verified that the Go collector returns a successful stored response.

### Validation

Started the collector:

```bash
cd collector/go
go run ./cmd/sledtrace-collector
```

Ran the Python demo:

```bash
cd sdk/python
python -m examples.refund_policy_demo
```

The SDK generated a trace payload and sent it to the collector.

Collector response:

```json
{
  "trace_id": "trace_af404e92216b4f7f97fb415208dc5992",
  "status": "stored",
  "warnings_generated": 0
}
```

### Notes

SledTrace now has a working local trace ingestion path from Python SDK to Go collector to SQLite.

The next step is to build the initial React Dashboard so traces can be inspected visually instead of through raw JSON.

## 2026-05-19

### Completed

- Audited task documentation against implemented code and roadmap.
- Reconciled `CURRENT_TASK.md` to remove stale/duplicated initialization-phase content.
- Confirmed current milestone as dashboard implementation on top of the verified local ingestion path.

### Validation

- Verified collector endpoints remain aligned with docs:
  - `GET /health`
  - `POST /api/traces`
  - `GET /api/traces`
  - `GET /api/traces/{trace_id}`
- Verified SDK still supports posting traces through `flush()`.
- Verified dashboard source files exist but are not implemented yet (placeholders/whitespace).

### Notes

Documentation now matches actual project state:

- Infrastructure path is working end-to-end locally.
- Current data values in the demo are mock/sample values.
- The immediate workstream is building the first usable dashboard views.

### Documentation Sync

- Updated `docs/ai-context/ROADMAP.md` to include explicit phase status.
- Marked v0.1 as in progress, with SDK/collector/storage path done and dashboard work next.
- Left v0.2, v0.3, and v0.4 as not started.

## 2026-06-13

### Completed

- Reformatted `docs/ai-context/AI_HANDOFF.md` for readability and consistency.
- Normalized heading hierarchy and section spacing.
- Converted free-form completion/status blocks into structured bullet lists.
- Added clear subsection boundaries for implementation status, known issues, and next step.

### Notes

- This change is documentation-only and does not affect runtime behavior.

## 2026-06-13

### Completed

- Reformatted `docs/ai-context/CURRENT_TASK.md` for consistent Markdown structure.
- Fixed broken section boundaries and unclosed code block in the working path section.
- Standardized file lists and warning rules into clear bullet formatting.
- Converted final validation flow to a numbered checklist.

### Notes

- This change is documentation-only and does not affect runtime behavior.

## 2026-05-19

### Completed

- Added the initial React Dashboard MVP.
- Added trace list UI.
- Added trace detail UI.
- Added span timeline UI.
- Added retrieved chunk cards.
- Added LLM prompt and response viewer.
- Added JSON metadata viewer.
- Added warning placeholder UI.
- Connected the dashboard to the Go collector APIs:
  - `GET /api/traces`
  - `GET /api/traces/{trace_id}`
- Verified that traces generated by the Python SDK can be inspected in the browser.
- Fixed a dashboard blank-screen issue caused by `warnings` being returned as `null`.
- Updated backend/ frontend handling so empty warnings and spans are treated as empty arrays.
- Updated `.gitignore` to exclude local artifacts such as `node_modules`, SQLite databases, Python caches, and sample trace files.

### Validation

Started the collector:

```bash
cd collector/go
go run ./cmd/sledtrace-collector
```

Generated and flushed a demo trace:

```bash
cd sdk/python
python -m examples.refund_policy_demo
```

Started the dashboard:

```bash
cd dashboard/web
npm install
npm run dev
```

Opened:

- http://localhost:5173

Verified that the dashboard can display:

- local trace list
- selected trace detail
- retrieval span
- retrieved chunks
- LLM prompt
- LLM response
- metadata JSON

### Notes

SledTrace now has a complete local inspection loop:

- Python SDK -> Go Collector -> SQLite -> React Dashboard

The project is ready for the first diagnosis layer.

### Next Step

Implement the warning engine.

The first target warning is conflicting_chunks for the refund policy demo.

## 2026-06-13

### Completed

- Reformatted `docs/ai-context/ROADMAP.md` and removed duplicated v0.1 sections.
- Reorganized roadmap into a single logical sequence: current snapshot -> v0.1 -> v0.2 -> v0.3 -> v0.4 -> future direction.
- Added explicit v0.1 exit criteria to make completion conditions measurable.
- Aligned warning-engine scope language with `CURRENT_TASK.md` and `AI_HANDOFF.md`.

### Notes

- This update is documentation-only and does not change runtime behavior.

## 2026-06-13

### Completed

- Updated `docs/ai-context/ROADMAP.md` to keep a dedicated "Latest Progress (v0.1 Execution Status)" section at the end.
- Preserved roadmap phase order while making newest implementation status easy to find in the final section.

### Notes

- This is a documentation structure decision to separate long-horizon plan from rolling execution status.

## 2026-06-13

### Completed

- Reformatted `docs/architecture/SYSTEM_ARCHITECTURE.md` for consistent heading hierarchy and readable section flow.
- Fixed malformed Markdown structure, including unclosed code block and collapsed plain-text lists.
- Reorganized architecture description into clear sections: components, data flow, and next architecture addition.

### Notes

- This is a documentation-only change and does not affect runtime behavior.


# 2026-09-24 — RC071 exact-main release-candidate validation

X1 PR #10 and X2 PR #9 passed required CI and merged into `main` as `755c19c`
and `92b27b9`. The user authorized a v0.7.1 release candidate only; tagging,
GitHub Release, PyPI upload, paid calls, and E3 are separate gates. Candidate
documentation now includes E1 observed usage, E2 one synchronous tool path,
X1 source-only exercise, and X2 legacy warning read compatibility.

Local validation from post-X2 main: SDK pytest 68 passed; startup unittest 18
passed; `python -m build` produced 0.7.1 wheel/sdist; clean-wheel and
independent-app scripts passed; Twine 7.0.0 checked both 0.7.1 artifacts;
Go `go test ./... -count=1` passed; Dashboard `npm.cmd test` passed 27 tests and
`npm.cmd run build` passed. `git diff --check` passed. Initial aggregate
attempts were interrupted: default sandbox blocked Windows child-process
cleanup, pytest default temp ACL, and Vite config traversal. A final complete
`python scripts/dev/slice.py check` passed all nine release-profile steps with
normal process permissions and an isolated forward-slash pytest temporary path.
Do not infer remote CI from these local results.

An isolated local stack used Collector 127.0.0.1:4327, Dashboard 5177, and a
temporary SQLite file. The offline deterministic `tool-recovery` fixture stored
trace `trace_9c99eb895dbf4f51b6ad621516800bf9`. In the real browser, its
detail showed two observed LLM calls, 24 known tokens, unknown/unverified usage
source, a tool error followed by a successful attempt, and the retained step
error. No paid/provider call occurred. The preexisting untracked
`docs/demo/comprehensive_trace_example.json` was not changed or staged; it
causes the slice scope checker to report an out-of-scope path.

PR #11 was opened from candidate commit `cb0dfd0`; its Dashboard, Go,
Python 3.9, Python 3.13, and Slice Contract checks passed. A clean temporary
clone of that commit ran locked `npm ci` and `scripts/tests/smoke_startup.py`:
real health/HTTP, SDK ingestion, CORS readback with two warnings, SIGINT
cleanup, both ports released, and clean Git status. `npm audit` reported four
fixable transitive toolchain advisories: baseline-browser-mapping (moderate),
browserslist, nanoid, and postcss (high). These were not changed here; review
the lockfile and exposure before any publication decision.

RC071 review closeout: corrected `NEXT_AGENT_BRIEF.md`'s stale span inventory.
Captured three real-browser conversation screenshots of the sanitized
tool-recovery fixture at the trace header, usage/steps, and selected failed
tool detail. Checked legibility, error/provenance/no-warning wording, and
absence of secrets/private user data. These are narrow-view candidate evidence,
not a new full-width README screenshot. PR #11 remains a draft; no merge, tag,
PyPI upload, or GitHub Release occurred. E3 remains the next separate slice.
The RC071 `release` validation profile was rerun after these documentation
changes and passed all nine steps (SDK 68, startup 18, Go suite, Dashboard 27,
build/wheel/independent-app, and diff check). Local `scope` still reports only
the preexisting untracked `docs/demo/comprehensive_trace_example.json`; it is
not included in the PR. Confirm the clean PR scope through Slice Contract CI.
