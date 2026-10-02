# SledTrace Release Checklist

Use this checklist for every project release. Tags and package-index versions are immutable: never move a published tag or rebuild an already published version with different contents.

## 1. Scope and state

- [ ] Confirm the milestone acceptance criteria and explicit non-goals.
- [ ] Confirm the working tree contains only intended changes.
- [ ] Confirm `sledtrace`, `SLEDTRACE_COLLECTOR_URL`, and temporary legacy compatibility remain accurate.
- [ ] Align Python package, CLI, example metadata, and Dashboard package versions.
- [ ] Prepare release notes and remove stale current-version claims.

## Agent milestone evidence (when included)

- [ ] Check the selected [milestone exit gate](../product/ROAD_TO_V1_0.md), not a quota of warning rules.
- [ ] D1 evidence, actual repair/regression decision and comparison limits match the release claim; optional D2/D3 include counterexamples and abstention.
- [ ] Distinguish fixture, live provider, posthoc mapping, internal dogfooding and independent user evidence.
- [ ] Verify source provenance, unknown usage, interrupted vs rejected quality, and original vs import timestamps.
- [ ] Any included import has tested privacy, atomic save, duplicate/conflict and old-data behavior.
- [ ] Include all failed/extra attempts in comparison; no invented savings or invoice accuracy.
- [ ] Preserve prior release notes/tags/artifacts; new planning does not retroactively add capabilities.

## 2. Local validation

- [ ] `cd sdk/python && pytest -q`
- [ ] `cd sdk/python && python -m build`
- [ ] `cd sdk/python && python -m twine check dist/*`
- [ ] `cd sdk/python && python scripts/validate-wheel.py`
- [ ] `cd sdk/python && python scripts/validate-independent-app.py`
- [ ] `cd collector/go && go test ./... -count=1`
- [ ] `cd dashboard/web && npm ci && npm test && npm run build` (use npm.cmd on Windows)
- [ ] `git diff --check`
- [ ] Clean-clone smoke test completed for the documented startup path.
- [ ] Dashboard traces and expected warnings inspected in a browser.

## 3. Review and tag

- [ ] Push a release branch and open a pull request.
- [ ] Required CI checks pass on the exact release commit.
- [ ] Merge without bypassing `main` protection.
- [ ] Confirm `main` is clean and synchronized with `origin/main`.
- [ ] Create an annotated `vX.Y.Z` tag at the validated commit.
- [ ] Push the immutable tag.

## 4. Python publication

- [ ] Dispatch `publish-python.yml` from the release tag with `target=pypi` and `ref=vX.Y.Z`.
- [ ] Review and approve the protected `pypi` environment deployment.
- [ ] Confirm the workflow builds, validates, and uploads both wheel and sdist.
- [ ] In a clean environment outside the source repository, run `python -m pip install --no-cache-dir sledtrace==X.Y.Z`.
- [ ] Verify preferred and legacy imports, CLI help/version, and the documented non-zero `sledtrace serve` boundary outside a checkout.

## 5. Release closure

- [ ] Publish the GitHub Release from the matching tag and release notes.
- [ ] Verify the PyPI long description and project links.
- [ ] Update README, `AGENTS.md`, and AI-context documents with actual—not intended—release state.
- [ ] Record validation evidence, workflow URLs, tag, commit, and known limitations in `DEVLOG.md`.
- [ ] Confirm the final working tree is clean.
