# Current Task

Updated: 2026-09-11. Status: **S3 trace delivery policy implemented, validated, and locally committed; not pushed, merged, versioned, or released**.

## Current focus and authority

The user continued the bounded post-v0.7 reliability sequence. S1 timing is in
local commit `5b5d254`; S2 score semantics is in local commit `ee0a812`; S3 is
implemented, validated, and locally committed on
`codex/s3-trace-delivery-policy`.

Do not redo S1-S3 or publish a release. First inspect the S3 evidence below. The
next bounded action requires a fresh decision between integration/release
grouping and another roadmap slice. v0.7.0 remains the released version.

## S3 decision card

| Question | Current answer |
| --- | --- |
| User value | An application can explicitly keep telemetry delivery failure from replacing successful business work or an existing application exception, while retaining the delivery error for inspection. |
| Confirmed blocker | Only strict `flush()` existed. Offline, timeout, and serialization failures raised; a strict flush in `finally` could replace the original application exception. |
| Existing capability | Explicit synchronous `flush()`, dependency-free SDK, public compatibility exports, and dataclass-based models already existed. |
| Smallest deliverable | Keep strict `flush()` unchanged; add public `TraceFlushResult` and explicit one-attempt `try_flush()` returning success/response or the original ordinary exception. |
| Non-goals | No default change, auto-flush, retry, queue, disk buffer, background thread, logging policy, Collector/API/storage/UI change, version bump, or release. |
| Validation | Success, HTTP/offline, timeout, serialization, strict compatibility, `BaseException`, original application exception, preferred/legacy imports, build, and clean wheel. |
| Visible evidence | A deterministic console run contrasts strict raise with observable best-effort failure and proves the original `LookupError` still propagates. |

## Implemented contract

- `flush(collector_url=None, timeout=5.0)` remains the historical strict path.
  Serialization, request, timeout, HTTP, connection, and response-decoding
  failures still raise.
- `try_flush(collector_url=None, timeout=5.0)` performs one synchronous call to
  `flush()` and returns a `TraceFlushResult`.
- Success: `ok=True`, Collector response in `response`, `error=None`.
- Ordinary failure: `ok=False`, `response=None`, and the exact exception raised
  by `flush()` in `error`.
- `Exception` is caught deliberately; `KeyboardInterrupt`, `SystemExit`, and
  other `BaseException` subclasses continue to propagate.
- The method does not retry, persist, queue, log, or run automatically.
- A timeout means delivery was not confirmed; it does not prove the Collector
  failed to persist the request.
- `TraceFlushResult` is exported identically from preferred `sledtrace` and
  temporary compatibility `raglens` imports.

## Acceptance criteria

- [x] Existing strict `flush()` calls and return type remain unchanged.
- [x] Successful best-effort delivery returns the Collector response.
- [x] Offline/HTTP, timeout, serialization, and request failures remain observable.
- [x] Strict offline, timeout, and serialization behavior still raises.
- [x] `try_flush()` does not catch `BaseException`.
- [x] A delivery failure in `finally` does not replace an original application exception.
- [x] No silent logging policy, retry, queue, or automatic delivery was introduced.
- [x] Preferred and legacy public imports expose the same result class.
- [x] The built wheel contains and exercises the new public API outside the source tree.
- [x] No Collector, storage, API, Dashboard, warning, span, or score behavior changed.

## Validation evidence

Completed on 2026-09-11:

- `cd sdk/python && pytest -q`: 62 passed.
- `cd sdk/python && python -m build`: passed; wheel and sdist produced.
- `cd sdk/python && python scripts/validate-wheel.py`: passed, including
  `TraceFlushResult`, `try_flush()`, score semantics, timing API, imports, and CLI.
- `git diff --check`: passed with line-ending conversion warnings only.
- Deterministic failure demo:
  - strict path raised the expected `RuntimeError` for an offline Collector;
  - `try_flush()` returned `ok=False` with the same observable `RuntimeError`;
  - the application still raised its original `LookupError("business failure")`;
  - the delivery failure remained available separately in the result.

No Go or Dashboard check was repeated because S3 changed only the Python SDK,
package validator, and documentation. S1/S2 cross-stack checks remain tied to
their respective commits.

## Exit boundary

S3 is complete and committed only on the local branch. No push, PR, merge,
version bump, tag, package upload, or release exists yet. The running Dashboard
still demonstrates S2; S3 has no Dashboard-facing behavior.
