# Current Task

# Current Task

## Current Focus

SledTrace v0.5.0 is the current milestone: Python SDK Distribution / Packaging Readiness.

This release makes the Python SDK buildable as a local wheel/sdist, installable in a clean virtual environment, and usable through the preferred `sledtrace` import path while keeping temporary `raglens` compatibility for migration.

## Current Goal

Deliver and validate SledTrace v0.5.0.

Completed focus areas:

- package the SDK as a clean local installable artifact
- keep package name, version, and README aligned to SledTrace
- preserve temporary compatibility for legacy `raglens` imports and env vars
- validate build/install/import behavior in a fresh venv
- keep warning engine, collector API, storage schema, dashboard contract, and span types unchanged

## Current System Status

Completed so far:

- Product direction defined and active project name is SledTrace
- Python SDK tracing foundation remains intact
- Local collector + SQLite + dashboard lifecycle remains unchanged
- Current trace API still uses `trace()`, `retrieval()`, `llm()`, and `flush()`
- Legacy `raglens` compatibility remains temporarily supported
- `SLEDTRACE_COLLECTOR_URL` precedence is implemented and validated
- v0.5 packaging readiness is complete and validated from `sdk/python`

## Current Milestone

v0.5.0 Python SDK Distribution / Packaging Readiness.

Status: completed and validated.

## Acceptance Criteria

- [x] `python -m build` succeeds from `sdk/python`
- [x] wheel install succeeds in a clean virtual environment
- [x] `import sledtrace` works
- [x] `from sledtrace import trace` works
- [x] legacy `raglens` import works for compatibility during migration
- [x] `SLEDTRACE_COLLECTOR_URL` precedence works
- [x] tests pass

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



