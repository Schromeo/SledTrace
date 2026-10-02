# Development setup

Most users only need `pip install sledtrace` and `sledtrace serve`
(see the [quickstart](QUICKSTART.md)). This page is for running SledTrace from a
source checkout: to contribute, to use the bundled demos, or on a platform
without a prebuilt wheel.

```bash
git clone https://github.com/Schromeo/SledTrace.git
cd SledTrace
```

## Option A: Docker Compose

Prerequisites: Docker Desktop (or Docker Engine with Compose) and Python 3.9+.

```bash
docker compose up --build
```

The collector listens on `http://localhost:4319` and the dashboard on
`http://localhost:5173`.

## Option B: Startup helper (no Docker)

Prerequisites: Python 3.9+, Go, Node.js 22 and npm. Install the dashboard
dependencies once, then start both services:

```bash
cd dashboard/web && npm ci && cd ../..
python scripts/start-sledtrace.py
```

The helper checks Go, Node.js, npm, installed dependencies and free ports first,
reports **SledTrace ready** only after both services respond, and stops them on
Ctrl+C. Inside a checkout without a bundled collector, `sledtrace serve` runs
this same helper (`sledtrace serve --source` forces it).

Useful options:

```bash
python scripts/start-sledtrace.py --dashboard-port 5174 --startup-timeout 120
```

Manual start, one terminal each:

```bash
cd collector/go && go run ./cmd/sledtrace-collector
cd dashboard/web && npm run dev
```

Shortcut scripts for the same steps live in `scripts/windows/*.ps1` and
`scripts/mac/*.sh` (start collector, start dashboard, generate demo traces,
smoke test).

## Generate demo traces

With the services running, install the SDK from the checkout and run the
reference app (deterministic, no API key):

```bash
cd sdk/python
python -m pip install -e ".[dev]"
python -m examples.reference_rag_app.run all
```

It produces nine traces such as `reference-rag-app-conflict` and
`reference-rag-app-weak`. Other demos:

| Command (in `sdk/python`) | What it shows |
| --- | --- |
| `python -m examples.local_rag_demo.run_demo trace-all` | Real local RAG over markdown docs with TF-IDF retrieval ([guide](demo/LOCAL_RAG_DEMO.md)) |
| `python -m examples.independent_app success` | A standalone app that only depends on the installed package |
| `python -m examples.real_llm_rag_demo all` | Optional run against a real LLM (needs an API key) |
| `python -m examples.external_federalist_rag ...` | Tracing a public external corpus; needs a downloaded PDF ([guide](demo/EXTERNAL_FEDERALIST_RAG.md)) |

Expected results and reset steps: [smoke test](demo/SMOKE_TEST.md) and
[reference app runbook](demo/REFERENCE_RAG_APP.md).

## Configuration

| Variable | Used by | Default |
| --- | --- | --- |
| `SLEDTRACE_COLLECTOR_URL` | SDK: where traces are sent | `http://localhost:4319` |
| `SLEDTRACE_COLLECTOR_ADDR` | Collector: listen address | `127.0.0.1:4319` |
| `SLEDTRACE_DB_PATH` | Collector / `sledtrace serve`: SQLite file | `raglens.db` (source) / `~/.sledtrace/sledtrace.db` (`serve`) |
| `SLEDTRACE_DASHBOARD_DIR` | Collector: serve a built dashboard on the same port | unset |
| `SLEDTRACE_ALLOWED_ORIGINS` | Collector: browser origins allowed to call the API | `http://localhost:5173,http://127.0.0.1:5173` |
| `VITE_SLEDTRACE_API_URL` | Dashboard build: collector URL (empty = same origin) | `http://localhost:4319` |

Legacy `RAGLENS_*` names are still accepted.

### Exposing SledTrace to another machine

Everything binds to loopback by default. SledTrace has no authentication or
TLS, so only expose it on a network you trust and review your firewall first:

```bash
# Docker Compose (.env)
SLEDTRACE_BIND_HOST=0.0.0.0
SLEDTRACE_ALLOWED_ORIGINS=http://YOUR_HOST:5173
VITE_SLEDTRACE_API_URL=http://YOUR_HOST:4319

# Packaged install
sledtrace serve --host 0.0.0.0

# SDK on another machine
SLEDTRACE_COLLECTOR_URL=http://YOUR_HOST:4319
```

## Building the packages

`sdk/python/scripts/build_wheels.py` builds the sdist, the SDK-only wheel and
platform wheels that bundle the collector and dashboard (needs Go, Node.js and
`pip install build`):

```bash
cd sdk/python
python scripts/build_wheels.py --targets current     # or: all, linux-amd64,windows-amd64,...
python scripts/validate-wheel.py --wheel dist/sledtrace-*-<platform>.whl
```

## Tests

See [CONTRIBUTING](../CONTRIBUTING.md) for the checks each component needs
before a pull request.
