---
slice_id: E2
slice_status: complete
components:
  - sdk
  - collector
  - dashboard
  - documentation
validation_profile: cross-stack
scope_base: origin/codex/e1-existing-usage-visibility
allowed_paths:
  - AGENTS.md
  - sdk/python/raglens/trace.py
  - sdk/python/tests/test_agent_tool_path.py
  - sdk/python/examples/agent_tool_demo.py
  - sdk/python/README.md
  - sdk/python/scripts/validate-wheel.py
  - sdk/python/scripts/validate-independent-app.py
  - collector/go/internal/warnings/engine.go
  - collector/go/internal/warnings/engine_test.go
  - dashboard/web/src/pages/TraceDetailPage.tsx
  - dashboard/web/src/App.tsx
  - dashboard/web/src/components/SpanTimeline.tsx
  - dashboard/web/src/utils/taskDisplay.ts
  - dashboard/web/src/style.css
  - dashboard/web/tests/agent_trace.test.mjs
  - docs/ai-context/AI_HANDOFF.md
  - docs/ai-context/CURRENT_TASK.md
  - docs/ai-context/DEVLOG.md
  - docs/ai-context/ROADMAP.md
  - docs/ai-context/DECISIONS.md
  - docs/assets/screenshots/agent-tool-path.png
human_gates:
  - persisted_schema_or_data_contract_change
  - version_tag_release_or_publication
  - paid_external_api_or_model_call
  - cloud_auth_or_security_boundary_expansion
  - external_user_outreach
auto_continue: false
---

# Current Task — E2 Python tool path

Updated: 2026-09-24. Status: **E2 locally complete, stacked review candidate**.

## Authority and topology

The user explicitly approved E2's minimal `tool` span and public SDK contract
on 2026-09-24. E1 is on unmerged Draft PR #7. This E2 branch starts at E1's
`941fd06`; its eventual PR must target the E1 branch and disclose that stack.
No merge, version, tag, publication, paid model call or external trial is
authorized. Existing Collector span storage is generic; do not introduce a
persisted schema migration under this approval.

## Decision card

| Question | E2 answer |
| --- | --- |
| User value | Inspect a bounded Python task's LLM attempts, tool results, and explicit final outcome together. |
| Blocker | SDK has no tool span; failed LLM attempts are labeled `ok`; the last LLM response becomes the trace answer even when it is not the task result. |
| Reuse | Existing span wire/storage, timing, supplied usage, trace metadata, and Dashboard step/detail views. |
| Smallest change | Add one synchronous `tool` record method, explicit LLM failure and task-result methods, one runnable one-tool example, and only the Collector/UI adjustments needed for honest interpretation. |
| Non-goals | No agent/memory/retry span family, framework adapter, automatic provider usage/pricing, async/thread guarantee, DAG, optimizer, release or external validation. |
| Validation | Cross-stack profile, SDK build and installed-wheel checks for the public API, focused scenario tests, API readback, and real Dashboard inspection. |
| Visible evidence | Success, business failure, and tool-failure-then-recovery traces show ordered steps, step status, timing/usage gaps, and final outcome. |
| Stop | Review-ready stacked Draft PR after self-review and closeout; E3 does not start automatically. |

## Acceptance

1. One standard-library, single-process Python sample records multiple LLM
   attempts and one tool layer. Tool records have name, summary-only input and
   output, status/error, span ID, and measured or explicitly unknown duration.
2. A failed LLM attempt is `error` while retaining any supplied usage. A later
   successful task can still have `ok` trace status. Existing positional RAG
   calls and default last-response behavior remain compatible.
3. An explicit task result owns the final result for E2 traces. Task/case ID,
   run ID, variant, app version and acceptance result use documented trace
   metadata/output, without an experiment database.
4. Non-RAG tool traces do not receive retrieval-grounding warnings solely for
   lacking retrieval. Existing RAG warning fixtures remain valid.
5. Success, business failure, and tool-failure-recovery examples survive
   Collector API readback and remain legible in the Dashboard. Unknown span
   fallback and old trace display remain intact.
6. Record exact local/remote evidence, update DEVLOG/ROADMAP/AI_HANDOFF and
   DECISIONS where needed, and stop before any merge or E3 work.

## Closeout

- SDK now records caller-supplied `tool` summaries with status/error/timing and
  span ID. Failed LLM attempts retain supplied usage; `log_task_result()`
  explicitly owns the final result and acceptance state. Existing RAG calls
  keep their default behavior and positional signature.
- Collector grounding checks require an actual retrieval span; an explicitly
  empty RAG retrieval still produces its existing warning. No persistence
  schema or API endpoint changed.
- The Dashboard shows task linkage, explicit result/acceptance, ordered steps,
  tool summaries, and step errors. Unknown span fallback remains generic JSON.
- Cross-stack profile passed: Python 68 tests, all Go packages, Dashboard 27
  tests, production build, and diff check. Wheel/sdist build, clean-wheel and
  copied independent-app validators passed. Seven slice-contract tests passed.
- Three deterministic sample traces were sent to an isolated local Collector
  on 4321 with a temporary SQLite database and read back through the API:
  success `ok`, business failure `error`, and tool failure then recovery `ok`.
  All had zero RAG warnings. Real Dashboard inspection on 5176 showed step
  errors and final acceptance. The sample uses no paid model or external app;
  the real-user value gate remains open.
- This branch is stacked on unmerged E1 Draft PR #7. It is not merged,
  versioned, tagged or published. Delivery/remote CI status is in DEVLOG.

## Next candidate — not active

E3 should validate one actual provider/client usage source and a provenance-
aware price basis for the selected workflow. Before activation, choose a real
application/client, establish quality/usage evidence and any paid-call budget,
and write a new decision card. Do not generalize E2's deterministic fixture
into a production agent or automatically start E3.
