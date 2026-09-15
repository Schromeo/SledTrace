# Current Task

Updated: 2026-09-14. Status: **B2 independent-app integration implemented and locally validated**.

## Current focus

Branch: `codex/b2-independent-app-integration`, based on B1 commit `b6848c1`
and ultimately on candidate commit `1ab83ef`. This slice proves an application
can use the built wheel outside the repository; it remains separate from the
existing v0.7.1 candidate PR #3. Version metadata is unchanged. Latest confirmed
published version remains v0.7.0.

## Decision card

| Question | Answer |
| --- | --- |
| User value | Copy one Python file into an application environment and observe normal work, an application exception, and Collector unavailability without repository-only imports. |
| Confirmed blocker | Existing examples and Dashboard empty-state guidance assumed a source checkout and did not prove use of the built wheel from another directory. |
| Existing capability | The dependency-free wheel exposes tracing, measured retrieval/LLM spans, strict `flush()`, and observable `try_flush()`. |
| Smallest deliverable | One copyable example, clean-wheel/out-of-checkout validation for three explicit outcomes, and installation-aware empty-state/docs guidance. |
| Non-goals | No framework adapter, bundled runtime, new span type, diagnostic rule/UI redesign, version bump, publication, or claimed external tester. |
| Validation | SDK/build/wheel, copied-app payload assertions, startup/Collector/Dashboard regressions, real wheel-installed local ingestion, API readback, and browser inspection. |
| Visible evidence | Dashboard traces `independent-app-success` and `independent-app-application-error`; the latter is open with `ERROR` status and its completed retrieval span. |

## Completed behavior

- Added `examples/independent_app.py`, a single standard-library-only application
  with deterministic `success`, `application-error`, and `collector-offline`
  cases. It imports only the installed public `sledtrace` API.
- Normal success uses strict `flush()` and records measured retrieval/LLM spans.
  The application-error case preserves the original exception, stores an error
  trace with completed work, and returns 2. The offline case preserves the
  business result, exposes `try_flush()` failure, and returns 1.
- Added `scripts/validate-independent-app.py`: copy the wheel and example into a
  system temporary directory, install into a fresh venv, capture/assert two
  payloads, close the test Collector, and assert the offline outcome.
- Added that validator to both Python CI matrix jobs after the ordinary clean-wheel
  check. The example remains source-only rather than silently expanding the wheel.
- Replaced the Dashboard empty-state command with installed-SDK guidance plus an
  explicit source-checkout example command. Updated root/package/integration docs.

## Validation

- `cd sdk/python && pytest -q`: 62 passed; expected legacy warning plus the
  host's known pytest-cache permission warning.
- `cd sdk/python && python -m build`: built wheel and sdist after normal network
  access supplied isolated setuptools/wheel dependencies.
- A temporary Twine 7.0 environment reported both current artifacts `PASSED`;
  it was removed afterward because Twine is not installed in the host Python.
- `python scripts/validate-wheel.py`: existing 0.7.1 clean-wheel/API/CLI checks passed.
- `python scripts/validate-independent-app.py`: clean venv, installed wheel,
  external copied file, ok/error payload assertions, and offline behavior passed.
- `python -m unittest discover -s ../../scripts/tests -v`: 18 passed with normal
  process-tree permissions. The restricted first run was cleaned by exact PID.
- `cd collector/go && go test ./... -count=1`: all packages passed.
- `cd dashboard/web && npm.cmd test`: 10 passed; `npm.cmd run build`: passed,
  38 modules transformed. Restricted esbuild access failed before compilation;
  normal-permission rerun passed.
- A second fresh temp venv installed the current wheel, then a copied external
  app stored `trace_c1608d93e05d4fedad57b4c58d54ebb0` (ok, retrieval + llm) and
  `trace_d10a66eb1dd743fbbdda98a3ea5b790b` (error, retrieval, original error).
  API readback and the actual Dashboard confirmed both; the temp app was removed.
- Remote CI for B1/B2 has not run. This is internal independent-environment
  evidence, not either of the still-missing external first-run attempts.

## Next slice and remaining release work

B1 and B2 are locally complete on separate commits/branches. The next recommended
slice is honest diagnostic presentation: stop rendering fixed rule constants as
calibrated probability percentages, preserve evidence and applicability, and add
focused UI tests plus visible browser proof. After that, build a small reserved
cross-domain diagnostic baseline before tuning rules. A fully automated
SDK-to-browser acceptance flow and two genuine external first-run attempts remain
open B-milestone evidence; internal clean environments must not be relabeled as
external validation.

The v0.7.1 PR remains a separate release decision. Its completed candidate
validation is in DEVLOG (2026-09-11) and V0_7_1.md; do not repeat it because B1
started or describe the unpublished candidate as released.
