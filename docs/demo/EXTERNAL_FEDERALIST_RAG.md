# External Federalist Papers RAG exercise

This exercise uses the [Harvard HBS RAG example](https://github.com/harvard-hbs/rag-example)
at commit `e47fab50cfaf64ced94dac23ba68ed9c797ee667`. Its included
`source_documents/5008_Federalist Papers.pdf` is the source corpus. The upstream
application uses LangChain, Chroma, and a configurable LLM. This exercise adapts
that corpus to SQLite FTS5 and uses a labeled extractive simulation for the
answer. It does **not** run Harvard's Chroma index or a real LLM.

## Run locally

Clone the upstream project alongside the SledTrace checkout and install the PDF
reader:

```powershell
cd C:\path\to\SledTrace-parent
git clone https://github.com/harvard-hbs/rag-example.git external\harvard-rag-example
python -m pip install pymupdf
```

Start SledTrace Collector in another terminal. For an isolated exercise:

```powershell
cd SledTrace\collector\go
$env:SLEDTRACE_COLLECTOR_ADDR='127.0.0.1:4322'
$env:SLEDTRACE_DB_PATH='C:\path\to\SledTrace-parent\external\federalist_trace.db'
go run ./cmd/sledtrace-collector
```

Run from `SledTrace/sdk/python`:

```powershell
python -m examples.external_federalist_rag `
  --pdf '..\..\..\external\harvard-rag-example\source_documents\5008_Federalist Papers.pdf' `
  --db '..\..\..\external\federalist_fts.db' `
  --collector-url http://127.0.0.1:4322 --rebuild
```

`--rebuild` creates a real on-disk SQLite FTS5 database from the PDF. Use it
again if the source PDF changes. The script prints the trace ID, matched pages,
simulated answer, and Collector response. Open the trace in the SledTrace
Dashboard or GET `/api/traces/{trace_id}` from the Collector. A second query
with `--query xylophonically` exercises the empty retrieval path.

## Observed local run, 2026-09-24

- The source PDF had 297 pages; the FTS5 table held 297 page records.
- Default query: `What are the latent causes of faction?` Retrieved pages 28,
  29, and 85. The first page contains Madison's statement that the latent
  causes of faction lie in human nature.
- Collector readback for trace `trace_862f8fa097de4835af50dc8e0e53a992`
  contained a retrieval span and a `simulated_answer` span. BM25 values were
  marked `lower_is_better`. Warnings: 0.
- The out-of-corpus query returned no pages. Trace
  `trace_4e5cf4d414284adabe096ee0bbe5c900` yielded
  `no_retrieved_chunks` and `answer_not_grounded`.

The answer is an extracted source sentence, not model generation or proof of
answer quality. SledTrace's warnings are English-domain heuristics. No warning
on the first query means only that no rule fired for that trace. The two SQLite
databases are local exercise artifacts, outside the SledTrace Git repository.
