# SledTrace Python SDK

SledTrace is a local-first observability and debugging SDK for RAG pipelines.

Current release: **0.7.0 — External Developer Readiness**

Project and visual overview: [github.com/Schromeo/SledTrace](https://github.com/Schromeo/SledTrace)

## Distribution status

Install the released SDK and CLI from production PyPI:

```bash
python -m pip install sledtrace==0.7.0
```

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

`sledtrace version` reports `0.7.0` for this release.

`sledtrace serve` must be run from inside a SledTrace source checkout. It locates the repository from the current working directory and delegates to `scripts/start-sledtrace.py`. The wheel does not bundle the Collector, Dashboard, Docker assets, or a standalone serving runtime; outside a checkout, `serve` exits with actionable guidance.

## Basic usage

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
- [v0.7.0 release](https://github.com/Schromeo/SledTrace/releases/tag/v0.7.0)

Repository examples such as `examples.custom_pipeline_demo` are local developer examples and not a separate public SDK surface.


