# SledTrace Python SDK

SledTrace is a local-first observability and debugging SDK for RAG pipelines.

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

Do not rely on PyPI publishing for this release; this package is prepared for local distribution and installation from a built artifact.

## More docs

- `../../docs/product/USER_ONBOARDING.md`
- `../../docs/integrations/PYTHON_SDK_GUIDE.md`

Repository examples such as `examples.custom_pipeline_demo` are local developer examples and not a separate public SDK surface.


