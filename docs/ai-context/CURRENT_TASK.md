# Current Task

Updated: 2026-09-14. Status: **B1 source startup reliability implemented and locally validated**.

## Current focus

Branch: `codex/b1-startup-reliability`, based on candidate commit `1ab83ef`.
The user resumed development after the phase review. This slice improves source
startup; it is separate from the existing v0.7.1 candidate PR #3. Version metadata
is unchanged. Latest confirmed published version remains v0.7.0.

## Decision card

| Question | Answer |
| --- | --- |
| User value | Reach a working local Dashboard or receive an actionable failure without leaving services from a partial startup. |
| Confirmed blocker | Dashboard launch could fail after Collector launch but before cleanup was registered; no health gate or complete dependency/port checks existed. |
| Existing capability | Source-installed CLI delegates to the helper; Go health endpoint, Vite, SDK and local process tools already exist. |
| Smallest deliverable | Preflight tools/dependencies/listeners, strict Dashboard port, real readiness probes, and owned-process cleanup across startup/exit paths. |
| Non-goals | No package/runtime redistribution, version bump, diagnostic/UI redesign, automatic dependency installation, or publication action. |
| Validation | Standard-library startup regressions, SDK regressions, real startup/trace/CORS/interrupt/port-release smoke, existing-browser inspection. |
| Visible evidence | Actual startup output plus Dashboard trace `b1-startup-verified`, with two spans and numeric evidence. |

## Completed behavior

- Check Go, Node.js 22+, npm, installed Vite, source directories and both bind
  addresses before launching services. Never terminate an existing port owner.
- Keep Collector address precedence, including legacy fallback; derive health
  and default Dashboard API URLs from the selected address.
- Keep explicit browser API/origin settings; otherwise align origins with the
  chosen local Dashboard port.
- Support helper options `--dashboard-port` and `--startup-timeout`; use
  Vite strict-port mode. Installed `sledtrace serve` still uses helper defaults.
- Print ready only after Collector identity/health and Dashboard HTTP checks.
- Register interruption handling before launches and clean up after partial
  startup, timeout, interrupt, or a service exit (including unexpected exit 0).
- Test Windows child-tree cleanup with a real wrapper/listening child; POSIX
  process-group cleanup is wired into the existing Linux Python CI jobs.

## Validation

- `python -B -m unittest discover -s scripts/tests -v`: 18 passed on Windows.
- `cd sdk/python && python -B -m pytest -q -p no:cacheprovider`: 62 passed.
- `python -B scripts/tests/smoke_startup.py`: passed real Go/Vite startup,
  SDK POST/detail GET, custom-port CORS, SIGINT handling and both ports released.
- Second real startup while default ports were occupied: expected exit 1;
  the original services remained available.
- Browser displayed the newly ingested `b1-startup-verified` trace and evidence.
- SDK/package, Collector and Dashboard source did not change; their builds were
  not repeated. Remote CI for this new branch has not run.

## Next slice and remaining release work

B1 is ready for review. The next proposed implementation slice is independent-app
integration: use the SDK outside the repository, document success/business-error/
Collector-offline paths, and repair installation-aware empty-state guidance.
Move uncalibrated confidence presentation ahead of broader external validation;
start diagnostic evaluation with a small cross-domain baseline before tuning.

The v0.7.1 PR remains a separate release decision. Its completed candidate
validation is in DEVLOG (2026-09-11) and V0_7_1.md; do not repeat it because B1
started or describe the unpublished candidate as released.
