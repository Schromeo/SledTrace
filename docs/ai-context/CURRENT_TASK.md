# Current Task

# Current Task

## Current Focus

SledTrace v0.6.0 is the current milestone: Local CLI / Startup UX.

This release makes local developer startup easier by exposing a real package-installed CLI entry point, while keeping the existing collector/dashboard startup flow and compatibility guarantees intact.

## Current Goal

Deliver and validate the v0.6 local CLI path.

Completed focus areas:

- add an installable `sledtrace` console script
- keep the current repo-local startup flow as the production backend for `serve`
- keep the package install path and compatibility shim working
- validate CLI help/version behavior and wheel install readiness
- leave warning engine, collector protocol, storage schema, and trace contracts unchanged

## Current System Status

Completed so far:

- Product direction remains SledTrace-first
- v0.5 packaging readiness is complete and validated
- Python SDK tracing foundation remains intact
- Local collector + SQLite + dashboard lifecycle remains unchanged
- Current trace API still uses `trace()`, `retrieval()`, `llm()`, and `flush()`
- Legacy `raglens` compatibility remains temporarily supported
- `SLEDTRACE_COLLECTOR_URL` precedence remains implemented and validated
- `sledtrace` CLI entry point is installed and verified in editable mode

## Current Milestone

v0.6.0 Local CLI / Startup UX.

Status: initial CLI implementation is complete and verified.

## Acceptance Criteria

- [x] `python -m pip install -e .` succeeds
- [x] `sledtrace --help` shows the CLI surface
- [x] `sledtrace version` prints the installed version
- [x] `sledtrace serve` delegates to the repo-local startup script
- [x] `pytest -q` passes in `sdk/python`
- [x] `python -m build` succeeds
- [x] `python scripts/validate-wheel.py` passes

## Guardrails

- no warning engine changes
- no new span types
- no adapters
- no PyPI upload
- no collector API changes
- no storage schema changes
- no dashboard data contract changes
- keep packaging boring and local-first

## Current Validation Commands

```bash
cd sdk/python
python -m pip install --upgrade pip
python -m pip install build
python -m build

python -m venv .venv-package-test
source .venv-package-test/bin/activate
pip install dist/*.whl
python -c "import sledtrace; print(sledtrace.__version__)"
python -c "from sledtrace import trace; print(trace)"
python -c "import raglens; print('legacy raglens import ok')"
deactivate

pytest

cd collector/go
go test ./... -count=1

cd dashboard/web
npm run build
```

## Observed Validation Results

- `python -m build` succeeded and produced wheel + sdist
- clean venv install from the built wheel succeeded
- `import sledtrace` succeeded in a fresh environment
- `from sledtrace import trace` succeeded
- legacy `raglens` import succeeded
- `pytest` passed: 11 tests
- Go backend tests passed
- dashboard build passed

## Current Implementation Limits

Current implemented span types:

- `retrieval`
- `llm`

Current warning rules:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- `weak_query_chunk_overlap`
- `numeric_mismatch`
- `conflicting_chunks`
- `answer_not_grounded`

## Files Recently Updated

- `sdk/python/pyproject.toml` - SledTrace v0.5.0 metadata and packaging config
- `sdk/python/sledtrace/__init__.py` - version export and public import surface
- `sdk/python/raglens/__init__.py` - temporary compatibility shim and deprecation warning
- `sdk/python/tests/test_packaging_readiness.py` - v0.5 packaging/compatibility tests
- `sdk/python/README.md` - distributed-package instructions and usage
- `README.md` - v0.5 SDK packaging notes
- `docs/ai-context/ROADMAP.md` - v0.5 milestone status
- `docs/ai-context/DEVLOG.md` - v0.5 validation log
- `docs/releases/V0_5_0.md` - release notes
- `sdk/python/scripts/validate-wheel.py` - wheel validation script

## Current Status Summary

The packaging work is scoped to the Python SDK and stays within the guardrails for this milestone. No warning engine, collector, storage, or dashboard contracts were changed.

## Next Recommended Milestone

v0.6 Local CLI / `sledtrace serve` planning is the most likely next milestone, unless the project explicitly decides to pursue a PyPI publishing follow-up.



