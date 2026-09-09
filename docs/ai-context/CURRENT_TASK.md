# Current Task

## Current Focus

SledTrace v0.6.0 — Local CLI / Startup UX Completion and Release Alignment.

Status: implementation and required local validation are complete. No tag or GitHub release has been created.

## Goal

Finish the package-installed CLI without turning the Python wheel into a standalone SledTrace runtime.

The supported v0.6 behavior is:

- `sledtrace --help` works after editable or wheel installation
- `sledtrace serve --help` explains the source-checkout requirement
- `sledtrace version` reports `0.6.0`
- `sledtrace serve` walks upward from the current working directory to find a SledTrace checkout
- repo-local `serve` delegates to `scripts/start-sledtrace.py`
- outside a checkout, `serve` exits non-zero with actionable guidance

The wheel does not bundle the Go collector, dashboard build, Docker images, or other platform-specific runtime assets.

## Acceptance Criteria

- [x] package version and public CLI version are `0.6.0`
- [x] Dashboard package version is aligned to `0.6.0`
- [x] `sledtrace --help` works in editable and wheel installs
- [x] `sledtrace serve --help` documents the source-checkout limitation
- [x] `sledtrace version` prints `0.6.0`
- [x] repo detection walks upward using `AGENTS.md`, `docker-compose.yml`, and `scripts/start-sledtrace.py`
- [x] repo-local `serve` delegates to the existing startup script
- [x] wheel-installed `serve` outside a checkout fails gracefully
- [x] legacy `raglens` import compatibility remains available
- [x] required Python, Collector, and Dashboard validation passes
- [x] release and AI-context documentation is reconciled

## Validation Results

Validated on 2026-09-07:

```bash
cd sdk/python
pytest -q
python -m build
python scripts/validate-wheel.py

cd collector/go
go test ./... -count=1

cd dashboard/web
npm.cmd run build
```

Observed results:

- Python SDK tests: 17 passed; warnings were the expected legacy-import deprecation warning and an environment-specific `.pytest_cache` permission warning
- wheel and sdist build: passed; produced `sledtrace-0.6.0`
- clean wheel environment: preferred and legacy imports passed
- clean wheel CLI: root help, `serve --help`, and version checks passed
- wheel-installed `serve` outside a checkout: expected non-zero exit with the documented guidance
- Collector packages and tests: passed
- Dashboard TypeScript/Vite production build: passed
- editable install: passed
- repo detection from a nested checkout directory: passed
- repo-local delegation test: passed without starting long-running child processes

## Current Implementation Limits

- supported span types remain `retrieval` and `llm`
- warning behavior remains deterministic and unchanged in v0.6.0
- no PyPI publication
- no standalone wheel-installed serving
- no framework adapters, cloud hosting, authentication, or hosted features
- no agent, tool, memory, verification, human-feedback, or retry spans
- no running-trace lifecycle or partial span ingestion

## Compatibility Guardrails

- prefer `sledtrace` and `SLEDTRACE_COLLECTOR_URL`
- preserve temporary `raglens` and `RAGLENS_COLLECTOR_URL` compatibility
- preserve collector API, SQLite schema, dashboard data contract, and current span contracts
- do not remove legacy database/startup compatibility without a separate migration decision

## Release State and Next Step

v0.6.0 meets its implementation and validation criteria and is ready to be marked complete in the repository.

Release publication remains a separate user-approved action:

- do not create or push `v0.5.0` or `v0.6.0` tags yet
- do not create GitHub releases yet
- do not publish to PyPI

Historical tag recommendation: `b3cad60a10636dbf7a5d371f51bac0c04a4af936` cleanly represents completed v0.5.0 packaging readiness and is the recommended target for a future annotated `v0.5.0` tag.
