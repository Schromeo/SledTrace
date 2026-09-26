# A1/A2: one public Agent reference workflow

This is a **technical integration exercise**, not a genuine user deployment or
an answer-quality/efficiency result. It instruments PydanticAI's official
[`bank_support.py`](https://github.com/pydantic/pydantic-ai/blob/92e0b457bd1628d17e959f9b12d74568946a2709/examples/pydantic_ai_examples/bank_support.py)
at commit `92e0b457bd1628d17e959f9b12d74568946a2709`. The upstream project
is [MIT licensed](https://github.com/pydantic/pydantic-ai/blob/92e0b457bd1628d17e959f9b12d74568946a2709/LICENSE).
SledTrace imports that file from a separate checkout; it does not vendor it or
add PydanticAI to the core SDK dependencies. The adapter verifies the source
file SHA-256 before import (CRLF checkout line endings are normalized to LF):
`9fe72475bd293d83f1e534dbf04f865d7f0f531f15ce87de9e03fbbe2ca3505c`.

## Task and predeclared checks

The sample's in-memory SQLite table contains **synthetic** customer 123,
`John`, with balance `$123.45`; no real bank records are used. Case `balance`
asks `What is my balance?`. Structural pass requires the upstream agent to
return its `SupportOutput` type and the real SQLite lookups to return `John`
and `123.45`. Case `missing-customer` uses ID 999; its balance lookup must
fail and the task must end in error. These are technical checks, not a human
judgment that scripted customer advice is correct.

The locally installed `pydantic-ai-slim[openai]==2.50.0` supplies upstream's
import-time OpenAI class. By default every task runs under PydanticAI `TestModel`.
The adapter temporarily replaces any existing key with a dummy one and points
the provider's fallback endpoint at loopback during import. The offline test
rejects non-loopback connections. In default mode, **no provider request or
bill is made**. `TestModel` produces scripted output, so its token fields remain
**Unknown**;
measured sub-millisecond step durations may round to `0ms` and are not real
model latency. The success trace has `quality_review=not_assessed` and
`structural_pass=true` metadata, but no `accepted=true` task-quality claim.

The pinned upstream sample uses a module-global `cur` in its database methods
even though it carries a SQLite connection in `DatabaseConn`. The adapter
initializes that cursor exactly as the sample's `__main__` block does and
records this as integration friction, not as a SledTrace SDK requirement.

## Reproduce locally

Keep the upstream checkout and optional virtual environment **outside** the
SledTrace Git repository. Check out the exact commit above and make its
`examples/pydantic_ai_examples/bank_support.py` available. In an isolated
Python 3.10+ environment install `pydantic-ai-slim[openai]==2.50.0`; no
PydanticAI dependency is installed by `pip install sledtrace`.

From `sdk/python`, using that environment's Python:

```powershell
python -m examples.pydantic_ai_bank_support balance `
  --upstream-examples 'C:\path\to\pydantic-ai\examples' `
  --collector-url http://127.0.0.1:4319 --flush
python -m examples.pydantic_ai_bank_support missing-customer `
  --upstream-examples 'C:\path\to\pydantic-ai\examples' `
  --collector-url http://127.0.0.1:4319 --flush
```

Omit `--flush` for a no-Collector payload inspection. The optional integration
test runs only when `SLEDTRACE_A1_UPSTREAM_EXAMPLES` points at that pinned
`examples` directory; without it the normal SDK suite runs the source/argument
guards and skips the external integration check.

### Explicit live-model mode (optional; may incur charges)

Only the synthetic `balance` case is allowed. Set `OPENAI_API_KEY` in the
**same process environment** as the command; never paste it into a trace,
argument or Git file. The command requires both switches:

```powershell
python -m examples.pydantic_ai_bank_support balance `
  --upstream-examples 'C:\path\to\pydantic-ai\examples' `
  --live-openai --i-accept-api-costs `
  --collector-url http://127.0.0.1:4319 --flush
```

The example pins `gpt-4o-mini-2024-07-18`, disables SDK retries, sets a
25-second request timeout, permits at most two model requests, limits each
response to 300 output tokens, and rejects unexpectedly large message context.
The model endpoint is fixed to OpenAI's official API rather than an inherited
`OPENAI_BASE_URL`. These are **local request guards, not a hard account spending
cap**; check the current [official model price](https://developers.openai.com/api/docs/models/gpt-4o-mini)
and your API account limits before opting in. No live call is run by tests.

The live wrapper records token counts from PydanticAI's parsed `ModelResponse`
and labels the capture path `pydantic_ai_model_response`. This is not a raw
Responses object passed to `sledtrace.openai.record_response`; Dashboard
therefore shows known totals but **Unknown / not provider-verified** source and
does not treat them as the E3 direct-Responses pricing contract. The final
answer remains `quality_review=not_assessed`; a matching synthetic balance is
a structural check, not a customer-advice quality verdict.

## Observed local result, 2026-09-25

- `balance` trace `trace_e886bef4c629428284c44cd8e1731ad0`: status `ok`;
  five ordered spans: name lookup, TestModel response, balance lookup, name
  lookup, TestModel response. The repeat name lookup comes from upstream's
  dynamic instructions on the second model step; it is **not** labeled waste.
  Its `execution_origin=dynamic_instructions` metadata distinguishes it from
  the registered `customer_balance` Agent tool.
  The final scripted output and unique run ID are visible in Dashboard.
- `missing-customer` trace `trace_d571f67e64834f04b7a5943f2ec50d07`:
  status `error`; name lookup, TestModel response, balance tool error
  `Customer not found`. Dashboard shows the failed task and selected tool
  error. No token total was recorded for either trace; the UI shows coverage
  `0/2` and `0/1`, not zero-token cost.
- Both traces were delivered to the isolated loopback Collector on port 4319,
  read back through `GET /api/traces/{id}`, and inspected in the real local
  Dashboard on port 5173. Both had 0 RAG heuristic warnings, which says
  nothing about Agent efficiency or answer quality.
- The optional pinned-upstream test passed 3/3 with external network blocked.
  The original first balance trace used `accepted=true` for a structural
  check; after browser review, the adapter was corrected and the trace above
  is the final success record. Historical local traces were not rewritten.

E4R later added example-only in-process comparison of the naturally repeated
name lookup: the second call records booleans for matching synthetic customer
ID and returned value, a reference to the first span, and the dynamic-
instruction context. No raw ID/name or derived hash is added to that metadata.
The separate [E4 evidence runbook](AGENT_REPEAT_EVIDENCE.md) records the new
offline trace and its limits. This is one normal-repeat counterexample, not a
public fingerprint contract or a useful-waste finding.

Next gate: this independent public example establishes basic integration
only. It does not show that an actual developer found useful waste, nor give
general safe comparison/state evidence across workflows or a held-out E4
evaluation set. Do not implement E4 rules or claim v0.8 readiness from this
run alone.

## Historical real-model evidence and A2 boundary

On 2026-09-25 the user separately authorized one real-model probe with a
$0.10 maximum budget. The **temporary external probe**, before A2's in-repo
mode existed, produced trace `trace_8630bf7c3b5444a6b673af2655ff621f`:
two `gpt-4o-mini-2024-07-18` requests (254 input, 60 output tokens), one
actual `customer_balance` Agent-tool lookup, five ordered spans, and a
structurally correct `$123.45` answer. The Collector and Dashboard read it
back. The temporary probe used unrecognized `usage_source=provider`, so the UI
showed the counts but classified their provenance as Unknown. It also labeled
both `ToolCallPart`s as tool requests, although the second is the structured
final output. The new optional example corrects that step label and does not
claim direct-Responses provenance, but **has not itself had a paid live run**.

On 2026-09-26 a CLI guard-check was mistakenly run while a key was present in
the process. One request was attempted and exited with `ModelAPIError`; no
provider token usage was captured or trace flushed. Whether that failed
attempt incurred any account charge is unknown. It was not retried, and no
successful live-model claim follows from it. A2 validation uses only offline
stubs and the earlier external-probe trace as historical evidence.
