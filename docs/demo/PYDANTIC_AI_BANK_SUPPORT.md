# A1: one public Agent reference workflow (offline)

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
import-time OpenAI class, but every task runs under PydanticAI `TestModel`.
The adapter temporarily replaces any existing key with a dummy one and points
the provider's fallback endpoint at loopback during import. The offline test
rejects non-loopback connections. **No provider request or bill is made.**
`TestModel` produces scripted output, so its token fields remain **Unknown**;
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

Next gate: this independent public example establishes basic integration
only. It does not show that an actual developer found useful waste, nor give
the stable parameter/result fingerprints and changing-state evidence E4 needs.
Do not implement E4 rules or claim v0.8 readiness from this run alone.
