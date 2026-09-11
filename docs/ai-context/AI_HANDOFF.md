# AI Handoff

Last reviewed: 2026-09-11 on branch `codex/s1-trustworthy-span-timing`, based on `main` commit `906fd2999a86fac5abb538cb83ee16b79ce4cda8`.
This snapshot distinguishes released behavior from the locally implemented and validated S1 timing change. S1 is not yet committed, merged, versioned, or released.

## Read this first

- [NEXT_AGENT_BRIEF.md](NEXT_AGENT_BRIEF.md): Chinese handover addressed to the next assistant, expected to be GPT-5.6.
- [CURRENT_TASK.md](CURRENT_TASK.md): the recommended first implementation slice, acceptance criteria, and stopping point.
- [ROADMAP.md](ROADMAP.md): candidate sequence and milestone-selection gates.
- [DECISIONS.md](DECISIONS.md): rationale and historical decisions.
- [DEVLOG.md](DEVLOG.md): chronological work and validation evidence.

Do not repeat the release setup, handover audit, or S1 implementation just because the model changes. Refresh Git state and the files relevant to the next selected slice. Read historical sections only when needed.

## Released baseline

SledTrace is a local-first visual debugger for RAG pipelines, formerly RAGLens.

- current release: **v0.7.0 — External Developer Readiness**, published 2026-09-09
- immutable annotated release tag target: `58887907973aff3948d2cf3667681832f4305ec6`
- subsequent documentation-closure commit: `906fd2999a86fac5abb538cb83ee16b79ce4cda8`
- [production PyPI](https://pypi.org/project/sledtrace/0.7.0/)
- [GitHub Release](https://github.com/Schromeo/SledTrace/releases/tag/v0.7.0)
- [successful protected publication workflow](https://github.com/Schromeo/SledTrace/actions/runs/34410674101)
- [release PR #1](https://github.com/Schromeo/SledTrace/pull/1) and [documentation PR #2](https://github.com/Schromeo/SledTrace/pull/2) are merged

Do not move published tags or upload rebuilt artifacts under an existing version. The new handover documents are local edits until their Git status proves otherwise; documentation text is not evidence of a new commit or publication.

Historical releases: v0.4.0 local/Docker release; v0.4.1 compatibility-preserving rebrand; v0.5.0 wheel/sdist readiness; v0.6.0 CLI/startup UX; v0.7.0 external-developer readiness and first production PyPI publication. Detailed evidence remains in DEVLOG and versioned release notes.

## Implemented architecture and boundaries

```text
Python trace() -> retrieval / llm records -> explicit flush()
  -> POST /api/traces -> Go Collector -> deterministic warnings
  -> SQLite -> React/TypeScript Dashboard
```

- The SDK has no runtime dependencies; public imports use `sledtrace`.
- Most SDK implementation still lives in `sdk/python/raglens/`; `sledtrace/__init__.py` re-exports it. This is intentional compatibility, not a second implementation to rewrite.
- Preferred configuration is `SLEDTRACE_COLLECTOR_URL`, with temporary `RAGLENS_COLLECTOR_URL` fallback.
- The wheel contains SDK/CLI only. `sledtrace serve` requires a source checkout; it does not install or bundle Collector/Dashboard runtime assets.
- API routes: `GET /health`, `POST /api/traces`, `GET /api/traces`, `GET /api/traces/{trace_id}`.
- Implemented spans are only `retrieval` and `llm`. No agent/tool/memory/retry spans, streaming lifecycle, or partial ingestion.
- Seven warning rules exist: no retrieved chunks, low retrieval score, duplicates, weak query/chunk overlap, conflicting chunks, numeric mismatch, and answer not grounded.
- Grounding/conflict diagnostics are deterministic heuristics, not semantic factuality evaluation. No framework adapters, cloud/auth service, or LLM-as-judge are implemented.

## Evidence from the 2026-09-10 read-only review

All findings below were unfixed at the released baseline. The first two are resolved in the current S1 working tree and validated locally; the others remain unfixed. Code locations are relative to the repository; use symbols because line numbers will change.

| Finding | Evidence and qualification | Code entry point |
| --- | --- | --- |
| Span duration measured logging overhead by default — **resolved locally in S1** | `t.measure()` now captures actual UTC boundaries and monotonic duration; explicit retrieval duration and existing LLM latency remain supported. Unmeasured post-hoc records carry null duration/end rather than a false 0ms. | `sdk/python/raglens/trace.py`: `SpanTiming`, `retrieval`, `llm` |
| UI reconstructed misleading duration — **resolved locally in S1** | Shared timing resolution treats canonical null as `Not measured`, preserves real zero and legacy fallbacks, and never substitutes a span-duration sum for trace duration. | `dashboard/web/src/utils/timing.ts`, `SpanTimeline.tsx`, `TraceDetailPage.tsx` |
| Distance is treated as relevance score | `normalize_chunks([{'text': 'Nearest matching document', 'distance': 0.1}])` produced `score: 0.1`. Collector assumes higher is better and defaults to threshold 0.5; per-span threshold overrides do not fix score direction. | `sdk/python/raglens/chunks.py`: `_extract_score`; `engine.go`: `detectLowRetrievalScore` |
| Trace delivery can fail an otherwise successful business call | `flush` is synchronous, defaults to a 5s timeout, and raises on network failure; non-JSON metadata fails serialization before the request. Mocked failures were reproduced. This is currently documented strict behavior; changing the default requires a compatibility decision. | `sdk/python/raglens/trace.py`: `flush`; root README integration example |
| Rule generality is unproven | Tokenization uses `[^a-z0-9]+`, topics focus on English store policies, and numeric extraction handles limited integer/range/unit forms. The 13 warning tests reviewed focus on that domain; no measured multilingual or cross-domain accuracy is established. | `engine.go`: `nonWordRegex`, numeric/topic helpers; `engine_test.go` |
| Percentage confidence is not calibrated | Some confidence values are constants such as 0.75, 0.88, and 0.9, rendered as percentage confidence. No calibration dataset was found. | `engine.go`: warning construction; `TraceDetailPage.tsx`: `formatConfidence` |
| Local defaults expose more than loopback | Collector binds `:4319`; Compose host publishing is not loopback-specific; CORS allows all origins. Actual reachability depends on firewall/network/browser policy; no leak was demonstrated. | `cmd/sledtrace-collector/main.go`, `internal/api/handlers.go`, `docker-compose.yml` |
| Persistence/retry boundary needs a separate reliability slice | Trace/spans commit before warnings in another transaction. A later write failure can leave partial state; resending hits existing primary keys. This follows from code; no fault-injection test ran in the review. | `handlers.go`: `handlePostTrace`; `sqlite.go`: `SaveTracePayload`, `SaveWarnings` |
| Repeated debugging is limited | List is capped at latest 100 without pagination; no baseline comparison or trace deep link; evidence preview shows only two items without chunk navigation. | `sqlite.go`: `ListTraces`; `dashboard/web/src/App.tsx`, page components |

S1 span timing correctness is complete in the current working tree, with results in CURRENT_TASK. The remaining findings are a prioritized candidate backlog, not instructions to start S2 or fix everything in one pass.

## Validation already completed versus still needed

Historical v0.7 release validation on 2026-09-09:

- 17 Python tests, wheel/sdist build, twine check, clean-wheel imports and CLI passed.
- Production-index clean install of `sledtrace==0.7.0` outside the source checkout passed.
- Preferred and legacy imports reported 0.7.0; legacy import emitted its expected deprecation warning.
- CLI help/version passed; out-of-checkout `serve` returned expected exit code 1 and guidance.
- Go tests and Dashboard build passed; required PR and post-merge checks passed.
- Clean-clone non-Docker services, health, nine reference traces, conflict/weak cases, and browser-visible screenshots passed.

These release tests establish the tested packaging/runtime contracts, not general diagnostic accuracy. The 2026-09-10 review used code inspection and small in-memory reproductions; it did not rerun the full release suite or change product code.

S1 local validation on 2026-09-11: 34 Python tests, wheel/sdist build, clean-wheel validation including `SpanTiming`, all Go tests, five Dashboard timing tests, Dashboard production build, and `git diff --check` passed. A live non-Docker run persisted and displayed a measured 200ms trace with 80ms retrieval/120ms LLM spans plus an unmeasured trace whose two spans read `Not measured`.

Environment facts last observed:

- Local host is Windows/PowerShell. Use `npm.cmd` where needed.
- Docker Desktop failed because WSL2 virtualization was disabled. Do not loop on Docker startup or change BIOS/system settings to complete unrelated SDK work.
- Non-Docker path uses Python, Go, Node/npm; install locked Dashboard dependencies with `npm.cmd ci` before starting the source helper.
- Four dependency advisories (one moderate, three high) were recorded during v0.7 validation; audit them again in a dedicated slice before calling this a current count.
- No two independent external first-run attempts are recorded. Recruitment must not block already evidenced fixes; contact people only with user authorization.

## Working agreement

Reply in Chinese unless the user asks for English. Start each implementation slice with the compact decision card in AGENTS. Complete the authorized slice through proportional tests and visible evidence; avoid repeated direction questions after an ordinary continuation request.

Show actual Dashboard behavior for timing/UI work, not only a diff or build log. Use deterministic screenshots without secrets or personal paths. Update README screenshots when their content materially changes.

The user authorized and completed S1 development on 2026-09-11. That does not authorize a new release or every later roadmap item. Use CURRENT_TASK for the completed evidence, then make a fresh bounded decision before preparing a commit/review or selecting another slice. Candidate v0.7.1/v0.8 labels are not selected release commitments.

For scope that changes architecture or publication, inspect DECISIONS and the current user instruction. Preserve prior authorization where it actually applies, and never bypass protected branch or deployment rules.

Historical context and old exact command transcripts live in [DEVLOG.md](DEVLOG.md) and [release notes](../releases/). They need not be reread on every slice.


