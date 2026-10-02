# Contributing to SledTrace

SledTrace is a local-first debugger for RAG pipelines. Contributions should preserve the current `retrieval`, `llm`, and caller-instrumented synchronous `tool` span contracts, deterministic diagnostics, and the temporary `raglens` compatibility layer unless a separately documented change explicitly replaces them.

## Before opening an issue

- Search existing issues first.
- Use the bug template for reproducible failures and the feature template for scoped proposals.
- Do not describe planned capabilities as implemented. Generic Agent runtime, agent/memory/retry span families, framework-wide adapters, cloud hosting, authentication, and LLM-as-judge are not implemented. A caller-recorded `tool` span is already released.

## Scope and evidence

Use [CURRENT_TASK](docs/ai-context/CURRENT_TASK.md) for one active slice and
[Road to v1.0](docs/product/ROAD_TO_V1_0.md) for the adopted P1–P7 direction.
D1 failure localization precedes optional repeat/budget signals; two waste rules
are not a prerequisite for comparison. Fixture coverage, real-model execution,
internal dogfooding and independent user value are different evidence.

Documentation-only work checks links/claims/scope and diff hygiene; do not rerun
unchanged product builds. Historical release notes retain their original facts.
Cross-repository work must follow that repository's own task and instructions.

## Local setup

The recommended first run uses Docker Desktop with Docker Compose:

```bash
docker compose up --build
```

If Docker is unavailable, install Python 3.9+, Go, Node.js 22, and npm, then run:

```bash
cd dashboard/web
npm ci

cd ../..
python scripts/start-sledtrace.py
```

In another terminal, install the SDK and generate deterministic traces:

```bash
cd sdk/python
python -m pip install -e ".[dev]"
python -m examples.reference_rag_app.run all
```

Open `http://localhost:5173` and follow [the smoke-test guide](docs/demo/SMOKE_TEST.md) for expected results and reset instructions.

## Required validation

Run checks for every area you change. Before a release-oriented pull request, run the complete set:

```bash
cd sdk/python
pytest -q
python -m build
python scripts/validate-wheel.py

cd ../../collector/go
go test ./... -count=1

cd ../../dashboard/web
npm ci
npm run build

cd ../..
git diff --check
```

On Windows use `npm.cmd` if PowerShell does not resolve `npm` correctly.

## Pull requests

- Keep the change focused and explain the user-visible outcome.
- Include tests for behavior changes.
- Include browser evidence for Dashboard-facing changes.
- Update public and AI-context documentation when release state or supported behavior changes.
- Keep generated build artifacts and virtual environments out of Git.
- Wait for all required CI checks before merging.

Maintainers use [the release checklist](docs/releases/RELEASE_CHECKLIST.md) for package publication and project releases.
