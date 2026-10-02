# SledTrace Release Checklist

Use this checklist for every project release. Tags and package-index versions are immutable: never move a published tag or rebuild an already published version with different contents.

## 1. Scope and state

- [ ] Confirm the milestone acceptance criteria and explicit non-goals.
- [ ] Confirm the working tree contains only intended changes.
- [ ] Confirm `sledtrace`, `SLEDTRACE_COLLECTOR_URL`, and temporary legacy compatibility remain accurate.
- [ ] Align Python package, CLI, example metadata, and Dashboard package versions.
- [ ] Prepare release notes and remove stale current-version claims.

## 2. Local validation

- [ ] `cd sdk/python && pytest -q`
- [ ] `cd sdk/python && python scripts/build_wheels.py --targets all`
- [ ] `cd sdk/python && python -m twine check dist/*`
- [ ] `cd sdk/python && python scripts/validate-wheel.py` (SDK-only wheel)
- [ ] `cd sdk/python && python scripts/validate-wheel.py --wheel dist/sledtrace-X.Y.Z-py3-none-<platform>.whl`
- [ ] `cd collector/go && go test ./... -count=1`
- [ ] `cd dashboard/web && npm ci && npm run build`
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

- [ ] Dispatch `publish-python.yml` with `target=testpypi` and `ref=vX.Y.Z`, then install from TestPyPI on a real machine and run `sledtrace serve`.
- [ ] Dispatch `publish-python.yml` from the release tag with `target=pypi` and `ref=vX.Y.Z`.
- [ ] Review and approve the protected `pypi` environment deployment.
- [ ] Confirm the workflow builds, validates, and uploads the sdist, the SDK-only wheel and all platform wheels.
- [ ] In a clean environment outside the source repository, run `python -m pip install --no-cache-dir sledtrace==X.Y.Z`.
- [ ] Verify preferred and legacy imports, CLI help/version, and that `sledtrace serve` opens the dashboard.

## 5. Release closure

- [ ] Publish the GitHub Release from the matching tag and release notes.
- [ ] Verify the PyPI long description and project links.
- [ ] Update README, `AGENTS.md`, and `docs/PLAN_V0_8.md` with actual—not intended—release state.
- [ ] Record validation evidence, workflow URLs, tag, commit, and known limitations in the release notes under `docs/releases/`.
- [ ] Confirm the final working tree is clean.
