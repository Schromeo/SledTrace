# Current Task

Updated: 2026-09-11. Status: **v0.7.1 release candidate prepared and locally validated; clean-clone and protected PR checks remain**.

## Current focus and authority

The user selected **v0.7.1 — Trustworthy Local Tracing** as the patch release
candidate for the four completed post-v0.7 reliability slices:

- S1 timing: local commit `5b5d254`
- S2 score semantics: local commit `ee0a812`
- S3 trace delivery policy: local commit `6562dc3`
- S4 local network defaults: local commit `fc85bda`

The active branch is `codex/v0.7.1-reliability`. The user authorized preparing,
pushing, and opening the candidate pull request. This does not authorize merging,
tagging, PyPI publication, a GitHub Release, or v0.8 implementation. v0.7.0
remains the latest published release until the complete protected release path is
proven.

## Candidate decision card

| Question | Current answer |
| --- | --- |
| User value | Deliver four evidence/reliability fixes to existing users as one reviewable patch without mixing in speculative product expansion. |
| Confirmed blocker | S1-S4 existed only as local commits with 0.7.0 metadata and no combined artifact, release notes, clean-clone result, or remote CI evidence. |
| Existing capability | Protected main, cross-stack CI, tag-gated Trusted Publishing, clean-wheel validation, reference traces, and a repeatable release checklist already exist. |
| Smallest deliverable | Align source metadata to 0.7.1, add release notes, refresh materially changed screenshots, complete local/clean-clone validation, then push and open one PR. |
| Non-goals | No merge, tag, package upload, GitHub Release, v0.8 feature, auth/cloud, new span, adapter, retry queue, or unrelated dependency fix. |
| Validation | Python tests/build/Twine/clean wheel; all Go tests; npm clean install/tests/build; Compose expansion; clean-clone source startup; live browser inspection; required PR checks. |
| Visible evidence | Nine deterministic 0.7.1 traces and refreshed real Dashboard images show `Not measured` and explicit score direction. |

## Prepared candidate

- Python package, preferred and legacy import versions, CLI, payload metadata,
  User-Agent, examples, test expectations, and wheel validator use `0.7.1`.
- Dashboard `package.json` and lockfile use `0.7.1`.
- Root README distinguishes the v0.7.1 source candidate from latest published
  v0.7.0. Package README contains intended 0.7.1 artifact content.
- `docs/releases/V0_7_1.md` records the four changes, compatibility constraints,
  remote-network upgrade note, validation, and explicit non-goals.
- All three README screenshots were recaptured from a clean temporary database
  populated with nine deterministic reference traces from current source.

## Local validation completed

- [x] `cd sdk/python && pytest -q`: 62 passed.
- [x] `cd sdk/python && python -m build`: 0.7.1 wheel/sdist built.
- [x] `cd sdk/python && python -m twine check dist/*`: 0.7.1 artifacts passed.
- [x] `cd sdk/python && python scripts/validate-wheel.py`: passed in a clean
  temporary venv, including imports, version, CLI, timing, scores, delivery, and
  out-of-checkout `serve` behavior.
- [x] `cd collector/go && go test ./... -count=1`: all packages passed.
- [x] `cd dashboard/web && npm.cmd ci`: passed.
- [x] `cd dashboard/web && npm.cmd test`: 10 passed.
- [x] `cd dashboard/web && npm.cmd run build`: passed; 38 modules transformed.
- [x] Default and explicit-remote `docker compose config` expansion passed.
- [x] Live non-Docker loopback stack stored and displayed nine reference traces.
- [x] Three 1440x950 Dashboard screenshots refreshed and visually inspected.
- [x] `git diff --check`: passed with Windows line-ending warnings only.

Environment notes:

- The restricted build initially could not bootstrap its isolated environment;
  the same build passed with normal temporary-directory/package-index access.
- Host Python lacked Twine, so Twine 7.0.0 was installed only into a system
  temporary directory for validation.
- `npm ci` re-reported four known development-dependency advisories: one
  moderate and three high. No automatic audit fix entered this candidate.
- Docker runtime remains untested on this WSL2-disabled host. Static Compose
  expansion is not being represented as a container startup smoke.

## Remaining gates

1. Commit the release-facing metadata, docs, and screenshots.
2. Create a clean clone of that commit and run the documented non-Docker startup
   path, health check, reference trace, and Dashboard API smoke.
3. Record the clean-clone evidence without changing product behavior.
4. Push `codex/v0.7.1-reliability`, open a pull request to `main`, and wait for
   all required checks on the exact remote commit.
5. Stop. Merge, tag, package publication, production-index validation, and
   GitHub Release require a separate release-stage decision.
