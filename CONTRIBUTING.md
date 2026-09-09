# Contributing to SledTrace

SledTrace is a local-first debugger for RAG pipelines. Contributions should preserve the current `retrieval` and `llm` span contracts, deterministic diagnostics, and the temporary `raglens` compatibility layer unless a separately documented change explicitly replaces them.

## Before opening an issue

- Search existing issues first.
- Use the bug template for reproducible failures and the feature template for scoped proposals.
- Do not describe planned capabilities as implemented. Agent/tool/memory spans, framework adapters, cloud hosting, authentication, and LLM-as-judge are not part of the current product.

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
