# SledTrace Python SDK

SledTrace is a local-first observability and debugging SDK for RAG pipelines.

This checkout's source and package metadata are the **0.7.1 — Trustworthy Local
Tracing** release candidate, which is not yet merged, tagged, or published.

Project and visual overview: [github.com/Schromeo/SledTrace](https://github.com/Schromeo/SledTrace)

## Distribution status

Production PyPI currently publishes **sledtrace 0.7.0**:

```bash
python -m pip install sledtrace==0.7.0
```

After the 0.7.1 candidate described in this README is published, install it with:

```bash
python -m pip install sledtrace==0.7.1
```

Until then, use "Install from source for development" below to run the 0.7.1
candidate APIs (such as `t.measure()` and `try_flush()`) documented further down
in this README.

The immutable `0.7.0rc1` publication candidate remains available on [TestPyPI](https://test.pypi.org/project/sledtrace/0.7.0rc1/) for release-history purposes.

## Install from source for development

```bash
cd sdk/python
python -m pip install -e .
```

## Build a local wheel or sdist

```bash
cd sdk/python
python -m pip install --upgrade pip
python -m pip install build
python -m build
```

This produces wheel and source-distribution artifacts in `dist/`.

## Install the built wheel

```bash
python -m pip install dist/*.whl
```

## CLI

Editable and wheel installations provide:

```bash
sledtrace --help
sledtrace serve --help
sledtrace version
```

`sledtrace version` reports `0.7.1` when installed from this source checkout's candidate; production PyPI currently reports `0.7.0`.

`sledtrace serve` must be run from inside a SledTrace source checkout. It locates the repository from the current working directory and delegates to `scripts/start-sledtrace.py`. The wheel does not bundle the Collector, Dashboard, Docker assets, or a standalone serving runtime; outside a checkout, `serve` exits with actionable guidance.

## Copyable independent-app example

The source repository includes a single-file example that depends only on the
installed `sledtrace` package and Python's standard library:

```bash
cd sdk/python
python -m examples.independent_app success
python -m examples.independent_app application-error
python -m examples.independent_app collector-offline --collector-url http://127.0.0.1:1
```

`application-error` intentionally returns 2 after the error trace is delivered.
`collector-offline` intentionally returns 1 and prints both the completed
business result and the observable SledTrace delivery failure. Copy
`examples/independent_app.py` into another project or temporary directory to
verify that it runs against an installed wheel without relying on the SledTrace
checkout. When the checkout version is newer than production PyPI, install this
checkout's editable package or built wheel before running its examples.

## Basic usage

### E2 development candidate: one Python tool path

The unmerged E2 branch adds a synchronous, caller-instrumented `tool` span and
explicit task result. These APIs are **not in production PyPI 0.7.0**. From this
checkout, run the standard-library, deterministic example without a paid model:

```bash
cd sdk/python
python -m examples.agent_tool_demo success
python -m examples.agent_tool_demo business-failure
python -m examples.agent_tool_demo tool-recovery
```

Add `--flush` when a local Collector is running. The example uses one tool layer
and simulated LLM outputs solely to check integration; it is not proof of value
in a real external agent. For your own synchronous workflow, record safe input
and output summaries, and keep the final task result separate from intermediate
LLM responses:

```python
with trace("policy-review", metadata={
    "task_id": "case-1", "run_id": "run-1",
    "variant": "baseline", "app_version": "my-app-1",
}) as t:
    with t.measure() as timing:
        found = lookup_policy("refund")
    t.tool("policy_lookup", input_summary="refund key",
           output_summary="one match" if found else "no match", timing=timing)
    t.llm(model="my-model", response="draft", input_tokens=10)
    t.log_task_result("review accepted", accepted=True)
```

`t.tool(...)` records only what the application supplies and returns a span ID.
Use `status="error", error="safe summary"` for a failed tool or LLM attempt;
the error is per step and does not automatically fail a recovered task.
`log_task_result(result, accepted=...)` sets trace-level `task_result`,
`accepted`, and the compatibility `answer` field; `accepted=False` marks the
task trace as an error. No agent/LLM is run by the SDK, no provider usage is
captured automatically, and sensitive arguments or secrets should not be put
in summaries.

## Existing RAG usage

This example uses the 0.7.1 candidate's `t.measure()` and `t.try_flush()`,
available from source or after 0.7.1 publication (see "Distribution status"
above). Against the published `sledtrace==0.7.0` package, omit `t.measure()`
and pass explicit `duration_ms`/`latency_ms` (or leave timing unset).

```python
from sledtrace import trace

with trace("example") as t:
    with t.measure() as retrieval_timing:
        chunks = [
            {
                "id": "chunk-1",
                "text": "Refunds are accepted within 30 days with proof of purchase.",
                "score": 0.92,
                "score_type": "similarity",
                "score_direction": "higher_is_better",
                "metadata": {"source": "refund_policy.md"},
            }
        ]

    t.retrieval(
        query="What is the refund policy?",
        chunks=chunks,
        top_k=1,
        timing=retrieval_timing,
    )

    with t.measure() as llm_timing:
        answer = "Refunds are accepted within 30 days with proof of purchase."

    t.llm(
        model="demo-model",
        prompt="Question: What is the refund policy?",
        response=answer,
        provider="local-demo",
        timing=llm_timing,
    )

t.flush()
```

`t.flush()` is the existing strict delivery path and still raises on
serialization, timeout, HTTP, or connection failures. Applications that must
keep telemetry failure separate from business behavior can opt into the
observable best-effort path:

```python
delivery = t.try_flush()
if not delivery.ok:
    print(f"SledTrace delivery failed: {delivery.error!r}")
```

`try_flush()` returns `TraceFlushResult(ok, response, error)`. It performs one
synchronous attempt with the same URL/timeout options as `flush()`; it does not
retry, queue, log automatically, or catch `KeyboardInterrupt`/`SystemExit`.

`t.measure()` captures actual operation timing. Calls recorded only after the work, without `timing`, `duration_ms` for retrieval, or `latency_ms` for LLM, remain compatible and are shown as not measured.

For retriever-native results, use `normalize_chunk(...)` or `normalize_chunks(...)`.
The normalizer preserves `score_type` and `score_direction`: named distances are
lower-is-better, named similarity/relevance scores are higher-is-better, and
ambiguous tuple scores are unknown. SledTrace never assumes a universal
`1 - distance` conversion. Explicit custom mappings can set `score_type` and
`score_direction`; existing explicit `score=` mappings remain higher-is-better by
default for compatibility.

## Collector URL configuration

The default collector URL is `http://localhost:4319`.

Use the SledTrace environment variable:

```bash
export SLEDTRACE_COLLECTOR_URL=http://localhost:4319
```

PowerShell:

```powershell
$env:SLEDTRACE_COLLECTOR_URL="http://localhost:4319"
```

Legacy compatibility remains temporarily supported for migration:

```bash
export RAGLENS_COLLECTOR_URL=http://localhost:4319
```

The precedence is:

1. `SLEDTRACE_COLLECTOR_URL`
2. `RAGLENS_COLLECTOR_URL`
3. `http://localhost:4319`

## Legacy compatibility note

Legacy `raglens` imports remain temporarily supported during migration, but new code should use the SledTrace package path:

```python
from sledtrace import trace
```

## More docs

- [Full project README and screenshots](https://github.com/Schromeo/SledTrace#readme)
- [User onboarding guide](https://github.com/Schromeo/SledTrace/blob/main/docs/product/USER_ONBOARDING.md)
- [Python SDK integration guide](https://github.com/Schromeo/SledTrace/blob/main/docs/integrations/PYTHON_SDK_GUIDE.md)
- [v0.7.1 release notes](https://github.com/Schromeo/SledTrace/blob/main/docs/releases/V0_7_1.md)
- [v0.7.0 release](https://github.com/Schromeo/SledTrace/releases/tag/v0.7.0)

Repository examples are source-only aids and are not bundled as a separate
public SDK surface. `examples.independent_app` is deliberately copyable and uses
only the installed public API; the other examples remain local developer demos.


