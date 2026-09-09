# Smoke Test

This document defines the current local-first smoke test for first-run developer experience.

Goal:

```txt
Fresh clone
  -> start collector + dashboard
  -> run reference traces
  -> open dashboard
  -> inspect diagnostics
```

## Path A: Docker (recommended)

Prerequisites: Git, Python 3.9+, and a running Docker Engine with Docker Compose. On Windows, Docker Desktop requires its WSL2 or Hyper-V virtualization backend to be enabled.

From repository root:

```bash
docker compose up --build
```

In another terminal:

```bash
curl http://localhost:4319/health
```

Expected health response:

```json
{
  "service": "sledtrace-collector",
  "status": "ok"
}
```

Generate reference traces:

```bash
cd sdk/python
python -m pip install -e .
python -m examples.reference_rag_app.run all
```

Open dashboard:

```text
http://localhost:5173
```

## Path B: Non-Docker fallback

Prerequisites: Python 3.9+, Go, Node.js 22, and npm.

From repository root, install the locked Dashboard dependencies once:

```bash
cd dashboard/web
npm ci
cd ../..
```

Start the Collector and Dashboard:

```bash
python scripts/start-sledtrace.py
```

Then:

```bash
cd sdk/python
python -m pip install -e .
python -m examples.reference_rag_app.run all
```

## Expected reference traces

- `reference-rag-app-refund`
- `reference-rag-app-conflict`
- `reference-rag-app-wrong-window`
- `reference-rag-app-processing-range`
- `reference-rag-app-wrong-processing-range`
- `reference-rag-app-damaged`
- `reference-rag-app-digital`
- `reference-rag-app-subscription`
- `reference-rag-app-weak`

## Expected high-level behavior checks

- `damaged` does not produce unrelated refund-processing conflict
- `processing-range` still shows relevant refund-processing conflict
- `wrong-processing-range` still shows `numeric_mismatch`
- `wrong-window` still shows `numeric_mismatch`
- `weak` still shows `answer_not_grounded`
- `subscription` remains low-noise and typically warning-free

## Stop and reset

Stop Docker stack:

```bash
docker compose down
```

Reset Docker data volume:

```bash
docker compose down -v
```

Reset non-Docker SQLite data:

- Collector defaults to `raglens.db` and `scripts/start-sledtrace.py` runs collector from `collector/go`.
- So the default local DB path is `collector/go/raglens.db`.

Bash:

```bash
rm -f collector/go/raglens.db
```

PowerShell:

```powershell
Remove-Item .\collector\go\raglens.db -ErrorAction SilentlyContinue
```

## Validation checklist

```txt
docker compose up --build: pass / fail
collector /health: pass / fail
reference-rag-app run all: pass / fail
dashboard loads: pass / fail
reference traces visible: pass / fail
```

## v0.7 clean-clone record

On 2026-09-09, a new checkout of `main` completed the non-Docker path on Windows after the documented `npm ci` and editable SDK install:

- Collector `/health`: pass
- all nine deterministic reference traces: pass
- Dashboard load and current SledTrace branding: pass
- conflict evidence (30-day versus 14-day values): pass
- weak-retrieval and unsupported-claim evidence: pass

The same host could not execute the Docker path because Docker Desktop reported that WSL2 virtualization was disabled. This is an environment prerequisite failure, not a SledTrace container failure; Docker validation was not represented as passing in this v0.7 run.


