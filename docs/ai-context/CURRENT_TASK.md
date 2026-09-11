# Current Task

Updated: 2026-09-11. Status: **S1 implemented and locally validated; not committed, merged, versioned, or released**.

## Current focus and authority

The user asked the incoming assistant to continue development from the written handover. S1 was selected by that continuation request and completed on `codex/s1-trustworthy-span-timing` while preserving the previously uncommitted handover documents.

Do not redo S1 or reopen the v0.7 publication process. The next product slice has not been selected: review the result with the user, then choose whether to prepare this bounded change for review/commit or select another roadmap item under a new decision card.

v0.7.0 remains the released version. Candidate v0.7.1/v0.8 names and effort budgets in ROADMAP are proposals, not selected release scope, deadlines, or permission to publish.

## Sources of truth

- Released state, architecture, compatibility, and review findings: [AI_HANDOFF.md](AI_HANDOFF.md).
- Direct Chinese brief for the incoming assistant: [NEXT_AGENT_BRIEF.md](NEXT_AGENT_BRIEF.md).
- Candidate sequence and later work: [ROADMAP.md](ROADMAP.md#proposed-post-v07-sequence).
- Rationale and historical validation: [DECISIONS.md](DECISIONS.md), [DEVLOG.md](DEVLOG.md).

## S1 decision card

| Question | Current answer |
| --- | --- |
| User value | A developer can trust the displayed duration of retrieval and model calls. |
| Confirmed blocker | Recording methods start their clocks after the real calls; a 200ms sample trace recorded two 0ms spans. |
| Existing capability | Trace context manager timing, monotonic clock helper, nullable span duration, and explicit LLM `latency_ms` already exist. |
| Smallest deliverable | Define and implement honest measured versus unmeasured timing for the existing two span types, with matching display and an example. |
| Non-goals | Delivery retries, score semantics, new span types, standalone runtime packaging, framework adapters, warning-rule changes, and release automation. |
| Validation | Focused timing tests, required SDK/package checks, nullable-duration API/storage inspection, and affected Dashboard checks. |
| Visible evidence | The same local sample shows its actual measured timing or a clearly unmeasured state in both timeline and detail. |

## Implemented outcome

- Added one-shot `with t.measure() as timing:` measurement using UTC operation boundaries and monotonic elapsed time.
- Existing retrieval/LLM record calls remain valid. Without measurement, their span `duration_ms` and `ended_at` are `null` instead of logging-overhead `0ms`.
- Retrieval accepts explicit `duration_ms`; existing LLM `latency_ms` is retained. Both reject booleans, non-integers, negative values, and overlap with `timing`.
- Fractional measured milliseconds use integer truncation; a measured sub-millisecond call remains a real `0`.
- Preferred `sledtrace` and temporary `raglens` exports include the same `SpanTiming` class.
- Dashboard duration resolution is shared by timeline/detail. Canonical null renders `Not measured`; legacy aliases/metadata and timestamp-only objects without canonical duration remain readable.
- Trace duration remains authoritative and is never replaced by a partial/concurrent span sum.
- `examples.timing_demo` generates a measured 80ms/120ms trace and a deliberately unmeasured trace.

## Files to inspect before editing

1. `sdk/python/raglens/trace.py`: `retrieval`, `llm`, `__enter__`, `__exit__`.
2. `sdk/python/raglens/models.py`: `Span`, `now_ms`, `utc_now_iso`.
3. `sdk/python/sledtrace/__init__.py` and existing compatibility/packaging tests.
4. `collector/go/internal/models/models.go`, `internal/storage/sqlite.go`: current timestamp and nullable duration contract.
5. `dashboard/web/src/pages/TraceDetailPage.tsx`: duration parsing/fallback and trace aggregation.
6. `dashboard/web/src/components/SpanTimeline.tsx`, `TraceCard.tsx`, `src/types.ts`: presentation consistency.
7. The root README integration example and `docs/integrations/PYTHON_SDK_GUIDE.md`.

## Ordered implementation outline

1. Refresh `git status --short` and HEAD. Preserve these handover edits if they are still uncommitted. Use a focused development branch under the existing protected-main workflow.
2. Reproduce the logging-overhead problem without a real model/network dependency. Keep one human-visible sample; use a controlled monotonic clock for deterministic unit tests.
3. State the timing contract before editing. Post-hoc recording cannot automatically recover the duration or start time of an already completed call. Prefer an additive, explicit measurement interface compatible with existing calls; choose exact parameter/helper names after inspecting all callers.
4. Preserve `llm(latency_ms=...)` behavior and existing positional argument order. Define precedence if new inputs overlap. Treat valid measured zero separately from unknown, and define invalid/negative/non-finite input behavior.
5. Use monotonic elapsed time for measurements and UTC for recorded timestamps. Do not invent measured start/end instants merely to make durations agree. Distinguish recording timestamps from actual execution timestamps if needed within the existing contract.
6. Make the UI respect the distinction. **Changing only `duration_ms` to null is insufficient**: detail view currently computes a duration from start/end timestamps. Timeline and detail must agree. Inspect legacy metadata fallback and preserve readability of previously stored traces.
7. Check trace duration separately: the outer trace measurement remains authoritative. Do not equate summed span durations with wall-clock duration when calls overlap, or a partial sum with a fully measured trace.
8. Add focused regression tests and one small documented example covering an actually measured retrieval/LLM call and an unmeasured post-hoc record.
9. Run proportional validation, inspect the real Dashboard, report results, and update task status/evidence.
10. Finish S1 and reassess the next slice. Do not automatically start every roadmap item.

## Acceptance criteria

- [x] Existing `sledtrace` and temporary `raglens` imports/call patterns still work.
- [x] Existing explicit LLM latency is retained; new parameters do not reinterpret old positional arguments.
- [x] Controlled-clock tests verify the selected actual-operation measurement contract and integer conversion.
- [x] Unknown timing is not presented as measured 0ms or reconstructed from logging timestamps.
- [x] Real measured 0ms is not silently converted to unknown.
- [x] Unknown `null` and measured `0` remain distinct through SDK payload, POST ingestion, SQLite persistence, and GET retrieval.
- [x] Timestamp-only, duration-only, legacy, and malformed timing inputs have defined behavior.
- [x] The selected explicit timer does not create spans itself; application exceptions propagate unchanged and no success/duplicate span is emitted.
- [x] Timeline/detail agree; trace duration does not become a misleading partial or concurrent span sum.
- [x] A deterministic local request and an unmeasured request are visible in the Dashboard with evidence shown to the user.
- [x] Required SDK checks pass; affected Go/Dashboard contracts are checked.
- [x] No unrelated rule, score, delivery, runtime, or version changes entered the slice.

## Validation and exit

For SDK changes, run from `sdk/python`:

```text
pytest -q
python -m build
python scripts/validate-wheel.py
```

For any Go contract changes, run from `collector/go`: `go test ./... -count=1`.
For Dashboard changes, run from `dashboard/web`: `npm.cmd run build`, plus focused behavioral tests and real browser inspection.
Run `git diff --check` and inspect the final scope.

Report the command, exit result, and useful failure/output details. A successful build is not visual acceptance. Use the documented non-Docker path if Docker remains unavailable; do not repeat an already diagnosed WSL2 failure.

Do not rerun the full release pipeline or all stacks repeatedly without a new change or unresolved concern. S1 is done when the timing contract, regression coverage, and visible result agree. New release/version selection happens separately.

Completed evidence on 2026-09-11:

- `pytest -q`: 34 passed.
- `python -m build`: wheel and sdist built after rerunning outside the restricted dependency/bootstrap environment.
- `python scripts/validate-wheel.py`: clean wheel install, imports, new timing API, CLI, and out-of-checkout serving boundary passed.
- `go test ./... -count=1`: all Collector packages passed, including null/zero POST → SQLite → GET round trip.
- `npm.cmd test`: five timing behavior tests passed; `npm.cmd run build`: production build passed.
- `git diff --check`: passed with line-ending conversion warnings only.
- Real non-Docker browser check: `timing-validation-measured` displayed trace 200ms, retrieval 80ms, LLM 120ms; `timing-validation-unmeasured` displayed both spans as `Not measured`.

## After S1

Consult ROADMAP for score semantics (S2), delivery policy (S3), local defaults (S4), and evidence-driven onboarding/diagnostic work. These remain candidates. External first-run feedback can change their order; a confirmed active exposure or data-integrity issue can justify reprioritization. Do not start S2 automatically from this completed S1 turn.
