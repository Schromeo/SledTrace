# SledTrace Python SDK

SledTrace is a local-first observability and debugging SDK for RAG pipelines.

Current release candidate: **0.7.0rc1 — TestPyPI validation**

Project and visual overview: [github.com/Schromeo/SledTrace](https://github.com/Schromeo/SledTrace)

## Distribution status

This is a prerelease candidate intended for TestPyPI validation. It is not a production PyPI release, so ordinary `pip install sledtrace` is not currently a supported installation path.

`0.7.0rc1` is published on [TestPyPI](https://test.pypi.org/project/sledtrace/0.7.0rc1/). Install that exact candidate in a clean environment with:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ sledtrace==0.7.0rc1
```

For local development before or outside that validation, use one of the source or built-artifact paths below.

## Install from source for development

```bash
cd sdk/python
pip install -e .
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
pip install dist/*.whl
```

## CLI

Editable and wheel installations provide:

```bash
sledtrace --help
sledtrace serve --help
sledtrace version
```

`sledtrace version` reports `0.7.0rc1` for this candidate.

`sledtrace serve` must be run from inside a SledTrace source checkout. It locates the repository from the current working directory and delegates to `scripts/start-sledtrace.py`. The wheel does not bundle the Collector, Dashboard, Docker assets, or a standalone serving runtime; outside a checkout, `serve` exits with actionable guidance.

## Basic usage

```python
from sledtrace import trace

with trace("example") as t:
    t.retrieval(
        query="What is the refund policy?",
        chunks=[
            {
                "id": "chunk-1",
                "text": "Refunds are accepted within 30 days with proof of purchase.",
                "score": 0.92,
                "metadata": {"source": "refund_policy.md"},
            }
        ],
        top_k=1,
    )

    t.llm(
        model="demo-model",
        prompt="Question: What is the refund policy?",
        response="Refunds are accepted within 30 days with proof of purchase.",
        provider="local-demo",
    )

t.flush()
```

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

This candidate is for TestPyPI validation only. Production PyPI publication remains a separate release decision.

## More docs

- [Full project README and screenshots](https://github.com/Schromeo/SledTrace#readme)
- [User onboarding guide](https://github.com/Schromeo/SledTrace/blob/main/docs/product/USER_ONBOARDING.md)
- [Python SDK integration guide](https://github.com/Schromeo/SledTrace/blob/main/docs/integrations/PYTHON_SDK_GUIDE.md)
- [v0.6.0 release](https://github.com/Schromeo/SledTrace/releases/tag/v0.6.0)

Repository examples such as `examples.custom_pipeline_demo` are local developer examples and not a separate public SDK surface.


