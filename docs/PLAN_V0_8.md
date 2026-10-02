# Plan: v0.8.0 — a RAG debugger others can use

Adopted 2026-10-01. This file replaces the earlier roadmap documents (now in
`docs/archive/`).

## Goal

Turn the released v0.7.1 into something a developer can install and use on
their own, and release it as **v0.8.0**. Polish only, no new features.

**Positioning:** SledTrace is a local, privacy-first RAG debugger. It shows
whether an answer went wrong because of retrieval, conflicting documents or the
model, and it also records tool calls and token usage.

## Kept vs frozen

| Kept (on `main`, v0.7.1) | Frozen (in `archive/*` tags) |
| --- | --- |
| Python SDK: retrieval / llm / tool spans, task outcome | MAMR import, P1–P6 diagnosis chain |
| Go collector + SQLite, React dashboard | Pair comparison page, Agent repeat evidence (E4) |
| RAG warnings, usage ledger, OpenAI Responses usage | PydanticAI reference agent, live probes |
| Local RAG demo, reference RAG app, Federalist example | v1.0 milestone plan (M2.5–G1) |

Frozen work restarts only when a real user asks for it.

## Stages

Each stage runs on its own branch and stops for the maintainer's review.

1. **Cleanup** — archive branches as tags, remove stale worktrees, archive process
   docs, shorten AGENTS.md, drop the slice harness. *Done when:* `main` plus one
   working branch, clean `git status`, all tests pass.
2. **One-command start** — `pip install sledtrace` then `sledtrace serve` opens the
   dashboard without a source checkout, Go or Node. The collector serves the
   built dashboard from `SLEDTRACE_DASHBOARD_DIR` on its own port;
   `sdk/python/scripts/build_wheels.py` cross-compiles the pure-Go collector and
   packs it with the dashboard into platform wheels. Docker and source
   development stay as they are.
   *Done when:* a clean environment runs the demo trace using only pip.
3. **Front page** — README fits on one screen (problem → 3-minute start →
   screenshots → links); a 5-minute "trace your own RAG app" guide using
   `docs/demo/comprehensive_trace_example.json`; fresh screenshots.
   *Done when:* someone new can start from the README alone.
4. **Release prep** — version 0.8.0, changelog, full clean-install check.
   The maintainer pushes, tags and publishes.

## Later (not in this plan)

- LangChain / LlamaIndex auto-instrumentation
- Docker image on GHCR
- Agent diagnosis (frozen)
- Find 2–3 RAG developers to try v0.8.0 and record where they get stuck
