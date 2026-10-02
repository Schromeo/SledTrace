# SledTrace

**A local debugger for RAG pipelines.** When your app gives a wrong answer,
SledTrace shows what the retriever returned, what the model was given, what it
said, and where those disagree. Everything runs on your machine: no account,
no API key, nothing uploaded.

![SledTrace dashboard](https://raw.githubusercontent.com/Schromeo/SledTrace/main/docs/assets/screenshots/dashboard-overview.png)

## Quickstart

```bash
pip install sledtrace
sledtrace serve        # opens the dashboard at http://127.0.0.1:4319
```

Then trace a request from your app:

```python
from sledtrace import trace

with trace(name="my-rag-request", query=question) as t:
    t.retrieval(query=question, chunks=[
        {"id": "c1", "text": "Customers can return items within 30 days.", "score": 0.82},
    ])
    t.llm(model="my-model", prompt=prompt, response=answer)

t.flush()   # after the `with` block; or t.try_flush() to never raise
```

The dashboard shows the trace with warnings such as conflicting retrieved
chunks, numbers in the answer that contradict the context, weak retrieval, and
claims that are not grounded. Each warning shows its evidence.

## What's included

- `trace`, retrieval, LLM and tool spans, task results and real span timing
- `normalize_chunk(s)` to keep distance/similarity score semantics intact
- `sledtrace.openai.record_response` to record OpenAI Responses token usage
- `sledtrace serve`: the local collector and dashboard. Platform wheels for
  Windows, macOS and Linux (x86-64 and ARM64) include everything; on other
  platforms run it [from source](https://github.com/Schromeo/SledTrace/blob/main/docs/DEVELOPMENT.md).
- Legacy `raglens` imports keep working.

Python 3.9+. No runtime dependencies.

## Documentation

- [5-minute quickstart](https://github.com/Schromeo/SledTrace/blob/main/docs/QUICKSTART.md)
- [Python SDK guide](https://github.com/Schromeo/SledTrace/blob/main/docs/integrations/PYTHON_SDK_GUIDE.md)
- [Warning rules](https://github.com/Schromeo/SledTrace/blob/main/docs/demo/WARNING_RULES.md)
- [Project on GitHub](https://github.com/Schromeo/SledTrace)
