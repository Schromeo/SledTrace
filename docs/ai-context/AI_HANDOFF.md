# AI Handoff

## 2026-09-25 post-release E3 probe candidate

Branch `codex/e3-real-workflow-evidence` adds a separate, opt-in example using
the authentic public Federalist PDF and local FTS5 index to prepare one
`gpt-4o-mini` Responses request. Its default path is a no-network dry run;
offline fake-client tests verify one request shape, recorded usage, no raw
provider object/credential persistence, and missing-key/budget stops. The
actual provider request remains **unrun**: `OPENAI_API_KEY` and the optional
`openai` client are absent in this execution environment. The user authorized
at most one request with a $0.10 ceiling, not repeated calls or an open-ended
bill. Do not claim real provider or billing validation before a successful
authorized run and local Collector readback. The original simulated example
remains unchanged. See CURRENT_TASK/DEVLOG for scope and exact validation.


## 2026-09-25 published v0.7.1 snapshot

The latest release is **v0.7.1 — Trustworthy Local Tracing**. PRs #11–#13
landed the reliability, E2 tool path and E3 usage work; release-closure PR #14
merged as `33d2335`. Immutable annotated tag `v0.7.1` points to that commit.
The protected PyPI workflow succeeded, publishing wheel and sdist; GitHub
Release is available at
https://github.com/Schromeo/SledTrace/releases/tag/v0.7.1 . A clean virtual
environment outside the source repository installed `sledtrace==0.7.1`,
verified `sledtrace`, `raglens`, and `sledtrace.openai` imports, CLI version
`0.7.1`, help, and the documented source-checkout serving boundary.

E3 records a caller-supplied completed non-streaming OpenAI Responses result
through the existing SDK/Collector/SQLite/Dashboard path. Its dated two-model
Standard text-token estimate is indicative. The release used sanitized offline
fixtures and a real local Dashboard readback; no paid provider call or bill
reconciliation was performed. Tool tracing is caller-instrumented and does not
execute an agent. The wheel remains SDK/CLI only; `sledtrace serve` requires a
source checkout. See CURRENT_TASK and DEVLOG for exact evidence and the next
workflow decision.

Last repository-history refresh: 2026-09-25. PRs
[#3](https://github.com/Schromeo/SledTrace/pull/3),
[#5](https://github.com/Schromeo/SledTrace/pull/5), and
[#6](https://github.com/Schromeo/SledTrace/pull/6) were squash-merged into
`main` as `272bc56`, `e8b034d`, and `0a63e3d`. E1 PR
[#7](https://github.com/Schromeo/SledTrace/pull/7) was squash-merged as
`622ff69`. Cumulative PR
[#4](https://github.com/Schromeo/SledTrace/pull/4) remains closed as superseded,
and its branch is retained for provenance. E1 existing-usage visibility is
included in the published v0.7.1 package.

E2's synchronous one-tool Python path was merged through PR #8 as `0734e20`
and is included in v0.7.1. It is a tracing contract, not a general agent
runtime.

## Read this first

- [NEXT_AGENT_BRIEF.md](NEXT_AGENT_BRIEF.md): concise Chinese entry for any incoming assistant.
- [CURRENT_TASK.md](CURRENT_TASK.md): the recommended first implementation slice, acceptance criteria, and stopping point.
- [ROADMAP.md](ROADMAP.md): candidate sequence and milestone-selection gates.
- [ROAD_TO_V1_0.md](../product/ROAD_TO_V1_0.md): detailed product hypotheses, slices, acceptance gates, and stopping rules; a proposed plan, not implemented scope.
- [DECISIONS.md](DECISIONS.md): rationale and historical decisions.
- [DEVLOG.md](DEVLOG.md): chronological work and validation evidence.
- [AGENT_WORKFLOW.md](../development/AGENT_WORKFLOW.md): repository-native slice commands, skills and one-time Copilot setting.

Do not repeat the release setup, handover audit, or S1 implementation just because the model changes. Refresh Git state and the files relevant to the next selected slice. Read historical sections only when needed.

## Released baseline

SledTrace is a local-first visual debugger for RAG pipelines, formerly RAGLens.

- current release: **v0.7.1 — Trustworthy Local Tracing**, published 2026-09-25
- immutable annotated release tag target: `33d2335b1f908588e46a1a003c574786735355ef`
- [production PyPI](https://pypi.org/project/sledtrace/0.7.1/)
- [GitHub Release](https://github.com/Schromeo/SledTrace/releases/tag/v0.7.1)
- [successful protected publication workflow](https://github.com/Schromeo/SledTrace/actions/runs/36132895644)
- release-closure PR [#14](https://github.com/Schromeo/SledTrace/pull/14)
- immutable annotated release tag target: `58887907973aff3948d2cf3667681832f4305ec6`
- subsequent documentation-closure commit: `906fd2999a86fac5abb538cb83ee16b79ce4cda8`
- [production PyPI](https://pypi.org/project/sledtrace/0.7.0/)
- [GitHub Release](https://github.com/Schromeo/SledTrace/releases/tag/v0.7.0)
- [successful protected publication workflow](https://github.com/Schromeo/SledTrace/actions/runs/34410674101)
- [release PR #1](https://github.com/Schromeo/SledTrace/pull/1) and [documentation PR #2](https://github.com/Schromeo/SledTrace/pull/2) are merged

Do not move published tags or upload rebuilt artifacts under an existing version. Local commits and documentation text are not evidence of a merge or publication.

Historical releases: v0.4.0 local/Docker release; v0.4.1 compatibility-preserving rebrand; v0.5.0 wheel/sdist readiness; v0.6.0 CLI/startup UX; v0.7.0 external-developer readiness; v0.7.1 trustworthy local tracing and explicit usage estimate. Detailed evidence remains in DEVLOG and versioned release notes.

## Implemented architecture and boundaries

```text
Python trace() -> retrieval / llm / tool records -> explicit flush()
  -> POST /api/traces -> Go Collector -> deterministic warnings
  -> SQLite -> React/TypeScript Dashboard
```

- The SDK has no runtime dependencies; public imports use `sledtrace`.
- Most SDK implementation still lives in `sdk/python/raglens/`; `sledtrace/__init__.py` re-exports it. This is intentional compatibility, not a second implementation to rewrite.
- Preferred configuration is `SLEDTRACE_COLLECTOR_URL`, with temporary `RAGLENS_COLLECTOR_URL` fallback.
- The wheel contains SDK/CLI only. `sledtrace serve` requires a source checkout; it does not install or bundle Collector/Dashboard runtime assets.
- API routes: `GET /health`, `POST /api/traces`, `GET /api/traces`, `GET /api/traces/{trace_id}`.
- Published v0.7.1 has `retrieval`, `llm`, and one caller-instrumented
  synchronous `tool` span. This is not agent/memory/retry, streaming or partial
  ingestion. E2 merged through PR #8.
- `llm()` stores supplied input/output/total token metadata. E2 adds an
  explicit failed-attempt status/error while retaining supplied usage; only
  successful responses update the legacy trace answer until the application
  sets an explicit task result. E3's optional `sledtrace.openai.record_response`
  explicitly reads usage from a caller-supplied non-streaming Responses result;
  it does not automatically capture calls or calculate a complete provider bill.
- The Dashboard normalizes recorded token fields into a
  per-call ledger with a known subtotal and coverage. It distinguishes zero,
  missing, invalid, and conflicting values; usage provenance remains explicitly
  unknown. E3 marks its explicit Responses source and estimates text-token cost
  for two supported models; its estimate is not billing truth.
- The wire/Go/SQLite model already has `parent_span_id`; current Python retrieval/LLM methods set it to None. Extend deliberately if a selected workflow needs nesting; do not invent a missing-storage-field migration.
- E2's `tool()` returns its span ID and records only caller-provided summaries,
  status/error and measured/unknown timing. `log_task_result(result, accepted)`
  records final output and acceptance separately from attempts; an uncaught
  application exception still marks the trace as error. Task/run/variant/app
  version are optional caller-supplied metadata, not an experiment system.
- E2's Collector grounding rule requires a retrieval span. Tool-only runs no
  longer get a RAG grounding warning; an empty retrieval span still can.
- Seven warning rules exist: no retrieved chunks, low retrieval score, duplicates, weak query/chunk overlap, conflicting chunks, numeric mismatch, and answer not grounded.
- Grounding/conflict diagnostics are deterministic heuristics, not semantic factuality evaluation. No framework adapters, cloud/auth service, or LLM-as-judge are implemented.

## Evidence from the 2026-09-10 read-only review

All findings below were unfixed at the released baseline. Timing, score semantics, trace delivery policy, and local network defaults are resolved in local S1-S4 commits; misleading confidence presentation is resolved in local H0 work. The other findings remain open. Code locations are relative to the repository; use symbols because line numbers will change.

| Finding | Evidence and qualification | Code entry point |
| --- | --- | --- |
| Span duration measured logging overhead by default — **resolved locally in S1** | `t.measure()` captures actual UTC boundaries and monotonic duration; explicit retrieval duration and existing LLM latency remain supported. Unmeasured post-hoc records carry null duration/end rather than a false 0ms. | `sdk/python/raglens/trace.py`: `SpanTiming`, `retrieval`, `llm` |
| UI reconstructed misleading duration — **resolved locally in S1** | Shared timing resolution treats canonical null as `Not measured`, preserves real zero and legacy fallbacks, and never substitutes a span-duration sum for trace duration. | `dashboard/web/src/utils/timing.ts`, `SpanTimeline.tsx`, `TraceDetailPage.tsx` |
| Distance was treated as relevance score — **resolved locally in S2** | Normalization now preserves metric type/direction. Named distance is lower-is-better, ambiguous tuples are unknown, explicit mappings can declare semantics, and only higher-is-better/legacy scores enter the threshold and score ordering. Dashboard labels the distinction. | `sdk/python/raglens/chunks.py`; `engine.go`: `higherIsBetterScore`; `scoreSemantics.ts` |
| Trace delivery could replace successful work or an application exception — **resolved locally in S3** | Strict `flush()` remains unchanged. Explicit `try_flush()` performs one synchronous attempt and returns `TraceFlushResult(ok, response, error)` for ordinary failures, without retry/queue/logging. `BaseException` still propagates. | `sdk/python/raglens/trace.py`: `TraceFlushResult`, `flush`, `try_flush` |
| Rule generality is unproven | Tokenization uses `[^a-z0-9]+`, topics focus on English store policies, and numeric extraction handles limited integer/range/unit forms. The 13 warning tests reviewed focus on that domain; no measured multilingual or cross-domain accuracy is established. | `engine.go`: `nonWordRegex`, numeric/topic helpers; `engine_test.go` |
| Percentage confidence is not calibrated — **presentation resolved locally in H0** | The raw constants remain in the API for compatibility; UI now uses heuristic guidance and applicability limits without a percentage. Evidence/severity/actions remain. No calibration or general accuracy claim was added. | `engine.go`: warning construction; `TraceDetailPage.tsx`; `utils/warnings.ts` |
| Local defaults expose more than loopback — **resolved locally in S4** | Native Collector and Vite defaults bind loopback; Compose publishes host ports on loopback while retaining container-internal listeners; CORS allows exact configured origins. Explicit address, host, origin, and client URL settings preserve intentional remote use. | `cmd/sledtrace-collector/main.go`, `internal/api/handlers.go`, `dashboard/web/package.json`, `docker-compose.yml` |
| Persistence/retry boundary needs a separate reliability slice | Trace/spans commit before warnings in another transaction. A later write failure can leave partial state; resending hits existing primary keys. This follows from code; no fault-injection test ran in the review. | `handlers.go`: `handlePostTrace`; `sqlite.go`: `SaveTracePayload`, `SaveWarnings` |
| Repeated debugging is limited | List is capped at latest 100 without pagination; no baseline comparison or trace deep link; evidence preview shows only two items without chunk navigation. | `sqlite.go`: `ListTraces`; `dashboard/web/src/App.tsx`, page components |

S1-S4 candidate validation is recorded in DEVLOG (2026-09-11). B1 closes the reproduced partial-startup cleanup gap and adds dependency/port/readiness checks. B2 adds a copied external application check for success, business exception, and Collector-offline behavior from the built wheel, plus installation-aware empty-state guidance. DEVLOG records the completed tests. The remaining findings are a prioritized candidate backlog, not instructions to fix everything in one pass.

## Validation already completed versus still needed

Historical v0.7 release validation on 2026-09-09:

- 17 Python tests, wheel/sdist build, twine check, clean-wheel imports and CLI passed.
- Production-index clean install of `sledtrace==0.7.0` outside the source checkout passed.
- Preferred and legacy imports reported 0.7.0; legacy import emitted its expected deprecation warning.
- CLI help/version passed; out-of-checkout `serve` returned expected exit code 1 and guidance.
- Go tests and Dashboard build passed; required PR and post-merge checks passed.
- Clean-clone non-Docker services, health, nine reference traces, conflict/weak cases, and browser-visible screenshots passed.

These release tests establish the tested packaging/runtime contracts, not general diagnostic accuracy. The 2026-09-10 review used code inspection and small in-memory reproductions; it did not rerun the full release suite or change product code.

2026-09-24 diagnostic regression evidence: `reference_rag_app all` completed
nine local realistic-shape cases, and `local_rag_demo trace-all` completed five
deterministic cases. Together they exercised all seven warning types through
Collector/API readback; fresh traces and warning counts were visible in the
Dashboard. This is small-scale integration evidence only. It did not use a real
provider or paid call, and it measured no concurrency or throughput.

The run also exposed a compatibility risk in the repo-local development DB:
some legacy warning rows contain string `confidence="heuristic"`, while current
detail reads expect a numeric value and can return HTTP 500. Treat compatibility
read/migration and isolated validation databases as candidates before any larger
repeated-run or scale test. The suites also suggest that generic score
thresholds and lexical rules need labeled cross-domain precision evidence before
threshold retuning; do not interpret warning counts as accuracy.

S1 local validation on 2026-09-11: 34 Python tests, wheel/sdist build, clean-wheel validation including `SpanTiming`, all Go tests, five Dashboard timing tests, Dashboard production build, and `git diff --check` passed. A live non-Docker run persisted and displayed a measured 200ms trace with 80ms retrieval/120ms LLM spans plus an unmeasured trace whose two spans read `Not measured`.

S2 local validation on 2026-09-11: 52 Python tests, wheel/sdist build, clean-wheel validation including score semantics, all Go tests, ten Dashboard tests, Dashboard production build, and `git diff --check` passed. A live isolated run showed similarity 0.10 with one low-score warning and `Similarity 0.10 ↑`, while distance 0.10 showed zero warnings and `Distance 0.10 ↓`.

S3 local validation on 2026-09-11: 62 Python tests, wheel/sdist build, clean-wheel validation of `TraceFlushResult`/`try_flush()` and existing package contracts, plus `git diff --check` passed. Deterministic failure injection covered success, HTTP/offline, timeout, serialization, strict compatibility, `BaseException`, and preservation of the original application exception. No Go/Dashboard validation was repeated because those components did not change.

S4 local validation on 2026-09-11: all Go tests, ten Dashboard tests, Dashboard production build, default and explicit-remote Compose configuration expansion, live loopback listeners, SDK ingestion, CORS allow/deny checks, and browser-visible trace detail passed. Docker runtime was not started because this host's WSL2 backend is unavailable; Compose structure was validated without the daemon.

v0.7.1 candidate validation on 2026-09-11: 62 Python tests, wheel/sdist build, Twine metadata check, clean-wheel install/API/CLI validation at version 0.7.1, all Go tests, ten Dashboard tests, Dashboard 0.7.1 production build, Compose default/remote expansion, nine live reference traces, and three refreshed 1440x950 Dashboard screenshots passed. A clean clone of `25521d4` also passed npm install, editable SDK install, installed CLI version/startup, loopback listeners, health/Dashboard HTTP, reference trace round trip, and clean Git status. PR #3 passed Python 3.9, Python 3.13, Go Collector, and Dashboard checks.

B1/B2 local validation on 2026-09-14: 18 startup tests, 62 SDK tests,
wheel/sdist build, existing clean-wheel validation, copied independent-app
validation, all Go packages, ten Dashboard tests, and Dashboard production build
passed. A separate temporary venv installed the wheel and sent real ok/error
traces from a copied file; API readback and the actual Dashboard confirmed them.
No B1/B2 remote CI has run, and this internal evidence is not an external tester.

E1 local validation on 2026-09-22: eight focused usage tests and the full 24-test
Dashboard suite passed; the Vite 6.4.3 production build passed. A real source
stack showed a complete three-call trace with known subtotal 220 and coverage
3/3, plus a partial/conflicting trace with Unknown subtotal, coverage 0/3, and
one excluded conflict. Selecting calls reused the existing span detail. The
fixtures are deterministic and used no paid model calls. They were written to
the repo-local ignored `raglens.db`, so those two development traces remain in
the local data unless the maintainer chooses to remove them.

Environment facts last observed:

- Local host is Windows/PowerShell. Use `npm.cmd` where needed.
- Docker Desktop failed because WSL2 virtualization was disabled. Do not loop on Docker startup or change BIOS/system settings to complete unrelated SDK work.
- Non-Docker path uses Python, Go, Node/npm; install locked Dashboard dependencies with `npm.cmd ci` before starting the source helper.
- Four dependency advisories (one moderate, three high) were recorded during v0.7 validation; audit them again in a dedicated slice before calling this a current count.
- No two independent external first-run attempts are recorded. Recruitment must not block already evidenced fixes; contact people only with user authorization.

## Working agreement

Reply in Chinese unless the user asks for English. Start each implementation slice with the compact decision card in AGENTS. Complete the authorized slice through proportional tests and visible evidence; avoid repeated direction questions after an ordinary continuation request.

Show actual Dashboard behavior for timing/UI work, not only a diff or build log. Use deterministic screenshots without secrets or personal paths. Update README screenshots when their content materially changes.

The user adopted incremental development under the roadmap on 2026-09-15 and
requires self-review, DEVLOG, CURRENT_TASK and ROADMAP closeout each slice. H0
and D0 are merged. E1 usage visibility was merged via PR #7. E2's single tool path
is locally complete in PR #8, targeting `main`; check its merge status live. E3 usage provenance
is the next candidate, not active. Conservative signals and outcome-aware comparison
remain later gates. Broad RAG tuning stays behind that value experiment. Later
runtime, privacy/data controls and release reliability remain gated. Publication
is separate; keep v0.7.0 as the latest confirmed release until newer publication
is proven.

D0 makes that workflow executable without changing product behavior:
CURRENT_TASK has simple YAML metadata; `.agents/skills` contains implementation
and review workflows; `scripts/dev/slice.py` owns status, scope and validation
profiles; CI has an additive Slice Contract job; Copilot instructions point to
the same review policy. Use `python scripts/dev/slice.py status`, then the active
skill. `scope` defaults to HEAD and therefore must run before commit.

Automatic Copilot review was not configured remotely: GitHub CLI authentication
for `Schromeo` was invalid during D0. Do not retry repeatedly. The maintainer's
one-time Settings path is documented in AGENT_WORKFLOW. PR #3, PR #5 and the
D0-only PR #6 are now merged; do not reconstruct their former stack.

H0 browser evidence used an isolated loopback Collector 4320/Dashboard 5174 and
temporary database, not the user's existing data. The preview was left available
for inspection; verify liveness before reusing it. A no-retrieval fixture generated
the existing no_retrieved_chunks warning even without a retrieval span. Before E2
claims non-RAG agent support, review rule applicability; this is not a new H0 fix.

E1 browser evidence uses the source stack on Collector 4319/Dashboard 5175. The
preview was left available for user inspection at closeout; verify liveness
before reusing it. Unlike H0, the startup helper used the repo-local ignored
`raglens.db`; trace IDs `trace-e1-complete-20260922` and
`trace-e1-partial-20260922` are deliberate local test records, not product data.

For scope that changes architecture or publication, inspect DECISIONS and the current user instruction. Preserve prior authorization where it actually applies, and never bypass protected branch or deployment rules.

Historical context and old exact command transcripts live in [DEVLOG.md](DEVLOG.md) and [release notes](../releases/). They need not be reread on every slice.


