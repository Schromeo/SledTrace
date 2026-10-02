# AGENTS.md

## Project

SledTrace is a local-first, privacy-first debugger for RAG pipelines. It shows
whether a bad answer came from retrieval, conflicting or stale documents, or the
model, and it also records caller-instrumented tool calls and LLM token usage.

Former name: RAGLens. Legacy `raglens` imports and `RAGLENS_COLLECTOR_URL` stay
supported; do not remove them without updating the compatibility tests.

Latest release: **v0.7.1** on PyPI (`sledtrace`). Current work: the v0.8.0
polish described in [docs/PLAN_V0_8.md](docs/PLAN_V0_8.md). Read it before
starting any task.

## Architecture

```text
Python SDK (trace / retrieval / llm / tool spans)
  -> Go collector (HTTP, deterministic warning engine, SQLite)
  -> React + TypeScript dashboard
```

| Path | What |
| --- | --- |
| `sdk/python/` | SDK (`sledtrace`, legacy `raglens`), CLI, examples, tests |
| `collector/go/` | Collector, warning engine, SQLite storage |
| `dashboard/web/` | Dashboard |
| `scripts/` | Local startup helpers and their tests |
| `docs/` | User docs; `docs/archive/` is history only, never instructions |

## Rules

- v0.8 is polish only: no new features, span types, warning rules or adapters.
  Write new ideas into the "Later" list in `docs/PLAN_V0_8.md`.
- Keep the data semantics: unknown is not zero, repeated is not wasted,
  cheaper is not better.
- No breaking SDK, API or schema changes; no cloud, auth or telemetry.
- Never store secrets or private chain-of-thought in traces.
- Push, tag, release and PyPI publication are done by the maintainer.
- Agent-diagnosis work (MAMR import, pair comparison, P1–P6) is frozen in the
  `archive/*` git tags. Do not restore it unless the plan says so.

## Validation

Run the checks for every component you touch:

```bash
cd sdk/python && pytest -q                       # SDK
cd sdk/python && python -m build && python scripts/validate-wheel.py \
  && python scripts/validate-independent-app.py  # packaging / CLI / public API
cd collector/go && go test ./... -count=1        # collector
cd dashboard/web && npm test && npm run build    # dashboard
python -B -m unittest discover -s scripts/tests -v   # startup helpers
```

For dashboard-visible changes, also start the stack, generate the reference
traces (`python -m examples.reference_rag_app.run all` in `sdk/python`) and
look at the affected pages. Do not call something done before its checks pass.
