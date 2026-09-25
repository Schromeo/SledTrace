"""One bounded, opt-in OpenAI answer over the public Federalist PDF index.

This is an integration exercise, not an agent or a quality evaluator. The
provider call is never made without --paid-call and --budget-usd.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from sledtrace import trace
from sledtrace.openai import record_response

from .external_federalist_rag import DEFAULT_QUERY, build_index, search


MODEL = "gpt-4o-mini"
MAX_OUTPUT_TOKENS = 256
INPUT_USD_PER_MILLION = 0.15  # Official Standard text rate checked 2026-09-25.
OUTPUT_USD_PER_MILLION = 0.60


def evidence_excerpt(text: str, *, max_chars: int = 1200) -> str:
    """Prefer the page's answer-bearing passage over its arbitrary prefix."""
    lower = text.lower()
    anchor = lower.find("latent causes of faction")
    if anchor < 0:
        anchor = lower.find("faction")
    start = max(0, anchor - 180) if anchor >= 0 else 0
    if start:
        next_space = text.find(" ", start, min(len(text), start + 40))
        if next_space >= 0:
            start = next_space + 1
    return text[start : start + max_chars]


def build_prompt(query: str, chunks: list[dict]) -> str:
    passages = "\n\n".join(
        f"[page {chunk['metadata']['page']}] {evidence_excerpt(chunk['text'])}"
        for chunk in chunks
    )
    return (
        "Answer only from the supplied Federalist Papers passages. "
        "State the direct answer briefly and cite the supporting page as "
        "[page N]. If the passages do not support an answer, say so.\n\n"
        f"Question: {query}\n\nPassages:\n{passages}"
    )


def conservative_cost_bound_usd(prompt: str) -> float:
    # UTF-8 byte length bounds the number of text tokens in this bounded
    # prompt conservatively; 256 extra input tokens cover request framing.
    input_tokens_bound = len(prompt.encode("utf-8")) + 256
    return (
        input_tokens_bound * INPUT_USD_PER_MILLION
        + MAX_OUTPUT_TOKENS * OUTPUT_USD_PER_MILLION
    ) / 1_000_000


def request_once(client: object, prompt: str) -> object:
    return client.responses.create(
        model=MODEL,
        input=prompt,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        store=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--collector-url", default="http://127.0.0.1:4319")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--paid-call", action="store_true", help="Opt in to exactly one provider request")
    parser.add_argument("--budget-usd", type=float, help="Maximum estimated USD for this request")
    args = parser.parse_args()

    if not args.pdf.is_file():
        parser.error(f"PDF not found: {args.pdf}")
    if args.rebuild or not args.db.is_file():
        build_index(args.pdf, args.db)
    chunks = search(args.db, DEFAULT_QUERY)
    if not chunks:
        parser.error("No source passages found; no provider request made")
    prompt = build_prompt(DEFAULT_QUERY, chunks)
    cost_bound = conservative_cost_bound_usd(prompt)
    pages = [chunk["metadata"]["page"] for chunk in chunks]
    print(f"Retrieved pages: {pages}; prompt bytes: {len(prompt.encode('utf-8'))}")
    print(f"Conservative text-token cost bound: ${cost_bound:.6f} USD (not an account spending cap)")

    if not args.paid_call:
        print("Dry run only; no provider request or trace was sent.")
        return 0
    if args.budget_usd is None or not 0 < args.budget_usd <= 0.10:
        parser.error("--paid-call requires --budget-usd > 0 and <= 0.10")
    if cost_bound > args.budget_usd:
        parser.error("Estimated upper bound exceeds the supplied budget; no provider request made")
    if not os.environ.get("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY is not set; no provider request made")
    try:
        from openai import OpenAI
    except ImportError:
        parser.error("Install the optional client first: python -m pip install openai")

    # Disable SDK retries: one CLI invocation can issue at most one request.
    client = OpenAI(max_retries=0, timeout=30.0)
    with trace(
        "federalist-openai-evidence",
        query=DEFAULT_QUERY,
        metadata={"corpus": "public-federalist-papers", "quality_review": "pending"},
        collector_url=args.collector_url,
    ) as current:
        current.retrieval(
            query=DEFAULT_QUERY,
            chunks=chunks,
            name="federalist_sqlite_fts5",
            top_k=3,
            metadata={"score_type": "bm25", "score_direction": "lower_is_better"},
        )
        try:
            with current.measure() as answer_timing:
                response = request_once(client, prompt)
        except Exception as exc:
            # Provider exceptions can contain request details. Keep only a
            # generic failure classification in the local trace and terminal.
            current.llm(
                model=MODEL, provider="openai", name="federalist_answer",
                status="error", error=f"Provider request failed ({type(exc).__name__})",
            )
            current.log_task_result("Provider request failed", accepted=False)
            answer = None
        else:
            record_response(current, response, name="federalist_answer", duration_ms=answer_timing.duration_ms)
            answer = response.output_text
            current.log_answer(answer)

    delivery = current.try_flush()
    print(f"Trace: {current.trace_id}; delivery: {'ok' if delivery.ok else 'failed'}")
    if answer is None:
        print("Provider request failed; actual provider usage, if any, is unknown.")
        return 1
    print(f"Model answer: {answer}")
    print("Manual quality check: does the answer identify human nature as the cause "
          "and cite the supporting retrieved page? This is not automatically graded.")
    return 0 if delivery.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
