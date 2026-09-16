"""
SledTrace Thin Reference RAG App

This example is intentionally a thin RAG app, not a full RAG framework.

It demonstrates a realistic integration flow:

  local docs
    -> simple chunking
    -> local lexical retrieval
    -> mixed raw retrieval result shapes
    -> normalize_chunks()
    -> SledTrace retrieval span
    -> deterministic or real LLM answer
    -> SledTrace llm span
    -> flush to collector

Run from sdk/python:

  python -m examples.reference_rag_app.run refund
  python -m examples.reference_rag_app.run conflict
    python -m examples.reference_rag_app.run wrong-window
    python -m examples.reference_rag_app.run processing-range
    python -m examples.reference_rag_app.run wrong-processing-range
  python -m examples.reference_rag_app.run damaged
  python -m examples.reference_rag_app.run digital
  python -m examples.reference_rag_app.run subscription
  python -m examples.reference_rag_app.run weak
  python -m examples.reference_rag_app.run all

Optional real LLM mode:

  export OPENAI_API_KEY="your_key"
  export OPENAI_MODEL="gpt-4o-mini"
  export OPENAI_BASE_URL="https://api.openai.com/v1"

  python -m examples.reference_rag_app.run conflict --llm

Ollama-compatible local mode:

  export OPENAI_API_KEY="ollama"
  export OPENAI_BASE_URL="http://localhost:11434/v1"
  export OPENAI_MODEL="llama3.1:8b"

  python -m examples.reference_rag_app.run refund --llm
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sledtrace import normalize_chunks, trace

DOCS_DIR = Path(__file__).parent / "docs"

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_BASE_URL = "https://api.openai.com/v1"

CASE_QUERIES = {
    "refund": "I bought a physical product 20 days ago. Can I still return it?",
    "conflict": "How many days do customers have to return a physical product?",
    "wrong-window": "How long do customers have to return most physical products under the current refund policy?",
    "processing-range": "How long do refunds usually take to process?",
    "wrong-processing-range": "How long do refunds usually take to process?",
    "damaged": "My item arrived damaged but I threw away the original box. What should I do?",
    "digital": "Can I get a refund for downloadable software if I never opened it?",
    "subscription": "If I cancel my subscription today, do I lose access immediately?",
    "weak": "Can support fix my birthday coupon issue?",
}


@dataclass
class LocalDocument:
    source: str
    text: str
    metadata: Dict[str, Any]


@dataclass
class RawChunk:
    chunk_id: str
    text: str
    source: str
    score: float
    rank: int
    metadata: Dict[str, Any]


@dataclass
class LangChainLikeDocument:
    page_content: str
    metadata: Dict[str, Any]


@dataclass
class HaystackLikeDocument:
    content: str
    meta: Dict[str, Any]
    score: float
    id: str


@dataclass
class LlamaIndexLikeNode:
    text: str
    metadata: Dict[str, Any]
    node_id: str


@dataclass
class LlamaIndexLikeNodeWithScore:
    node: LlamaIndexLikeNode
    score: float


def now_ms() -> int:
    return int(time.perf_counter() * 1000)


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def load_documents() -> List[LocalDocument]:
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Missing docs directory: {DOCS_DIR}")

    documents: List[LocalDocument] = []

    for path in sorted(DOCS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        metadata = infer_document_metadata(path.name, text)

        documents.append(
            LocalDocument(
                source=path.name,
                text=text,
                metadata=metadata,
            )
        )

    if not documents:
        raise RuntimeError(f"No markdown documents found in {DOCS_DIR}")

    return documents


def infer_document_metadata(filename: str, text: str) -> Dict[str, Any]:
    lowered = filename.lower()

    version = "current"
    if "legacy" in lowered or "2021" in lowered:
        version = "legacy"
    elif "draft" in lowered:
        version = "draft"

    if "refund" in lowered or "return" in lowered:
        doc_type = "refund_policy"
        owner = "support"
    elif "shipping" in lowered:
        doc_type = "shipping_policy"
        owner = "operations"
    elif "warranty" in lowered:
        doc_type = "warranty_policy"
        owner = "legal"
    elif "subscription" in lowered:
        doc_type = "subscription_policy"
        owner = "billing"
    elif "damaged" in lowered:
        doc_type = "damaged_items_policy"
        owner = "support"
    elif "digital" in lowered:
        doc_type = "digital_goods_policy"
        owner = "commerce"
    else:
        doc_type = "knowledge_base_doc"
        owner = "unknown"

    updated_at = "2026-06-01"
    if version == "legacy":
        updated_at = "2021-04-15"

    return {
        "doc_type": doc_type,
        "version": version,
        "owner": owner,
        "updated_at": updated_at,
        "format": "markdown",
        "char_count": len(text),
    }


def chunk_document(
    doc: LocalDocument,
    max_chars: int = 520,
    overlap_chars: int = 80,
) -> List[RawChunk]:
    text = doc.text.strip()
    chunks: List[RawChunk] = []

    if len(text) <= max_chars:
        chunks.append(
            RawChunk(
                chunk_id=f"{doc.source}::chunk_0",
                text=text,
                source=doc.source,
                score=0.0,
                rank=0,
                metadata={
                    **doc.metadata,
                    "chunk_index": 0,
                    "source": doc.source,
                },
            )
        )
        return chunks

    start = 0
    index = 0

    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                RawChunk(
                    chunk_id=f"{doc.source}::chunk_{index}",
                    text=chunk_text,
                    source=doc.source,
                    score=0.0,
                    rank=0,
                    metadata={
                        **doc.metadata,
                        "chunk_index": index,
                        "source": doc.source,
                    },
                )
            )

        if end >= len(text):
            break

        start = max(0, end - overlap_chars)
        index += 1

    return chunks


def build_chunks(documents: Sequence[LocalDocument]) -> List[RawChunk]:
    chunks: List[RawChunk] = []

    for doc in documents:
        chunks.extend(chunk_document(doc))

    return chunks


def compute_idf(chunks: Sequence[RawChunk]) -> Dict[str, float]:
    doc_count = len(chunks)
    df: Dict[str, int] = {}

    for chunk in chunks:
        terms = set(tokenize(chunk.text))
        for term in terms:
            df[term] = df.get(term, 0) + 1

    return {
        term: math.log((doc_count + 1) / (count + 1)) + 1.0
        for term, count in df.items()
    }


def retrieve(query: str, chunks: Sequence[RawChunk], top_k: int = 6) -> List[RawChunk]:
    """
    Simple deterministic lexical retriever.

    This is intentionally not a production retriever. It exists so SledTrace can
    observe a realistic-ish RAG flow without turning SledTrace into a RAG framework.
    """
    idf = compute_idf(chunks)
    query_terms = set(tokenize(query))
    scored: List[RawChunk] = []

    for chunk in chunks:
        chunk_terms = set(tokenize(chunk.text))
        overlap = query_terms.intersection(chunk_terms)

        if not overlap:
            score = 0.0
        else:
            weighted_overlap = sum(idf.get(term, 1.0) for term in overlap)
            query_weight = sum(idf.get(term, 1.0) for term in query_terms) or 1.0
            score = weighted_overlap / query_weight

        scored.append(
            RawChunk(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                source=chunk.source,
                score=round(score, 4),
                rank=0,
                metadata=dict(chunk.metadata),
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)

    top = scored[:top_k]
    for index, chunk in enumerate(top, start=1):
        chunk.rank = index

    return top


def to_mixed_raw_retrieval_results(chunks: Sequence[RawChunk]) -> List[Any]:
    """
    Convert internal RawChunk objects into deliberately mixed retrieval result
    shapes that resemble real-world RAG framework outputs.

    This is where the reference app proves why normalize_chunks() matters:
    a real RAG app might return LangChain-like Documents, Haystack-like
    Documents, LlamaIndex-like Nodes, dicts, tuples, or custom enterprise shapes.
    """
    mixed: List[Any] = []

    for index, chunk in enumerate(chunks):
        shape = index % 6

        if shape == 0:
            # Standard dict shape.
            mixed.append(
                {
                    "id": chunk.chunk_id,
                    "text": chunk.text,
                    "source": chunk.source,
                    "score": chunk.score,
                    "metadata": {
                        **chunk.metadata,
                        "raw_shape": "standard_dict",
                    },
                }
            )

        elif shape == 1:
            # LangChain-like dict shape.
            mixed.append(
                {
                    "page_content": chunk.text,
                    "metadata": {
                        **chunk.metadata,
                        "source": chunk.source,
                        "raw_shape": "langchain_like_dict",
                    },
                    "similarity": chunk.score,
                }
            )

        elif shape == 2:
            # LangChain vector store common shape: (Document, score).
            mixed.append(
                (
                    LangChainLikeDocument(
                        page_content=chunk.text,
                        metadata={
                            **chunk.metadata,
                            "source": chunk.source,
                            "raw_shape": "langchain_tuple_document_score",
                        },
                    ),
                    chunk.score,
                )
            )

        elif shape == 3:
            # Haystack-like object shape.
            mixed.append(
                HaystackLikeDocument(
                    content=chunk.text,
                    meta={
                        **chunk.metadata,
                        "source": chunk.source,
                        "raw_shape": "haystack_like_object",
                    },
                    score=chunk.score,
                    id=chunk.chunk_id,
                )
            )

        elif shape == 4:
            # LlamaIndex-like NodeWithScore shape.
            mixed.append(
                LlamaIndexLikeNodeWithScore(
                    node=LlamaIndexLikeNode(
                        text=chunk.text,
                        metadata={
                            **chunk.metadata,
                            "file_name": chunk.source,
                            "raw_shape": "llamaindex_like_node_with_score",
                        },
                        node_id=chunk.chunk_id,
                    ),
                    score=chunk.score,
                )
            )

        else:
            # Custom enterprise dict shape with unusual names.
            mixed.append(
                {
                    "passage": chunk.text,
                    "document": {
                        "path": f"s3://company-kb/policies/{chunk.source}",
                        "title": chunk.source,
                    },
                    "rank_score": str(chunk.score),
                    "extra": {
                        **chunk.metadata,
                        "raw_shape": "custom_enterprise_dict",
                    },
                }
            )

    return mixed


def normalize_reference_results(raw_results: Sequence[Any]) -> List[Dict[str, Any]]:
    """
    Normalize mixed retrieval result shapes into SledTrace chunks.

    Most shapes are auto-detected by normalize_chunks(). The custom enterprise
    dict shape needs explicit mapping because it uses unusual field names:
      passage
      document.path
      rank_score
      extra
    """
    normalized: List[Dict[str, Any]] = []

    for index, raw in enumerate(raw_results, start=1):
        if isinstance(raw, dict) and "passage" in raw and "document" in raw:
            normalized.extend(
                normalize_chunks(
                    [raw],
                    text="passage",
                    source="document.path",
                    score="rank_score",
                    metadata=lambda item: {
                        **item.get("extra", {}),
                        "document_title": item.get("document", {}).get("title"),
                    },
                    start_rank=index,
                )
            )
        else:
            normalized.extend(
                normalize_chunks(
                    [raw],
                    start_rank=index,
                )
            )

    return normalized


def build_prompt(query: str, chunks: Sequence[Dict[str, Any]]) -> str:
    context_blocks = []

    for chunk in chunks:
        context_blocks.append(
            f"[Rank {chunk.get('rank')}; Source: {chunk.get('source')}; "
            f"Score: {chunk.get('score')}]\n{chunk.get('text')}"
        )

    context = "\n\n---\n\n".join(context_blocks)

    return f"""
You are answering a user question using only the retrieved context.

Rules:
- Prefer current policy documents over legacy documents.
- If retrieved chunks conflict, say the context contains conflicting information.
- Do not invent policy values.
- Include numeric values only if they appear in the retrieved context.
- Be concise.

Retrieved context:

{context}

User question:

{query}

Answer:
""".strip()


def deterministic_answer(case_name: str) -> str:
    """
    Deterministic fallback answer used when --llm is not enabled.

    Some answers intentionally contain realistic RAG failure modes so SledTrace can
    show diagnostics without requiring an API key.
    """
    if case_name == "refund":
        return (
            "Yes. The current refund policy says customers may return most physical "
            "products within 30 days of purchase, so a purchase from 20 days ago is "
            "still within the return window."
        )

    if case_name == "conflict":
        return (
            "One retrieved refund policy says customers may return most physical products "
            "within 30 days. Another archived legacy refund policy says physical products "
            "can only be returned within 14 days."
        )

    if case_name == "wrong-window":
        return (
            "Customers have 45 days to return most physical products under the current "
            "refund policy."
        )

    if case_name == "processing-range":
        return (
            "Refunds are usually processed within 5 to 10 business days after the returned "
            "item is received by the warehouse."
        )

    if case_name == "wrong-processing-range":
        return (
            "Refunds are usually processed within 2 business days after the returned item is "
            "received by the warehouse."
        )

    if case_name == "damaged":
        return (
            "Customers should report damaged or defective items within 7 days of delivery. "
            "A damaged item report should include the order number, a description of the "
            "issue, and clear photos of the damaged product and shipping box if available. "
            "Original packaging is recommended, but support may still review a claim if the "
            "packaging was discarded."
        )

    if case_name == "digital":
        return (
            "Downloadable software is generally non-refundable after purchase. A refund may "
            "be considered only when the digital item was not delivered, the license key was "
            "invalid, or a duplicate charge occurred."
        )

    if case_name == "subscription":
        return (
            "Cancellation takes effect at the end of the current billing cycle, so access "
            "usually continues until that cycle ends."
        )

    if case_name == "weak":
        return (
            "Support can fix birthday coupon issues by manually adding a $25 account credit."
        )

    return "The retrieved context is insufficient to answer confidently."


def call_openai_compatible_chat_completion(
    prompt: str,
    model: str,
    api_key: str,
    base_url: str,
    timeout_seconds: int = 60,
) -> str:
    normalized_base_url = base_url.rstrip("/")
    url = f"{normalized_base_url}/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a careful assistant inside a RAG debugging demo. "
                    "Answer only from the retrieved context."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
    }

    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"LLM request failed with HTTP {exc.code}.\n"
            f"Response body:\n{error_body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LLM request failed: {exc}") from exc

    data = json.loads(raw)

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Unexpected LLM response shape:\n{json.dumps(data, indent=2)}"
        ) from exc


def record_retrieval_span(
    t: Any,
    query: str,
    chunks: Sequence[Dict[str, Any]],
    elapsed_ms: int,
) -> None:
    payload = {
        "name": "reference_rag_local_retriever",
        "query": query,
        "chunks": list(chunks),
        "top_k": len(chunks),
        "duration_ms": elapsed_ms,
        "metadata": {
            "retriever": "reference_rag_lexical_retriever",
            "demo": "reference_rag_app",
            "demo_version": "v0.3.5",
            "duration_ms": elapsed_ms,
            "latency_ms": elapsed_ms,
        },
    }

    for method_name in (
        "retrieval",
        "retrieval_span",
        "log_retrieval",
        "add_retrieval_span",
    ):
        method = getattr(t, method_name, None)

        if callable(method):
            method(**payload)
            return

    raise AttributeError(
        "Could not find retrieval span method on SledTrace trace object."
    )


def record_llm_span(
    t: Any,
    model: str,
    prompt: str,
    response: str,
    elapsed_ms: int,
    provider: str,
) -> None:
    payload = {
        "name": "reference_rag_answer_generation",
        "model": model,
        "prompt": prompt,
        "response": response,
        "latency_ms": elapsed_ms,
        "metadata": {
            "provider": provider,
            "demo": "reference_rag_app",
            "demo_version": "v0.3.5",
            "duration_ms": elapsed_ms,
            "latency_ms": elapsed_ms,
        },
    }

    for method_name in (
        "llm",
        "llm_span",
        "log_llm",
        "add_llm_span",
    ):
        method = getattr(t, method_name, None)

        if callable(method):
            method(**payload)
            return

    raise AttributeError("Could not find LLM span method on SledTrace trace object.")


def flush_trace(t: Any) -> None:
    flush = getattr(t, "flush", None)

    if not callable(flush):
        raise AttributeError("Could not find flush() on SledTrace trace object.")

    flush()


def run_case(case_name: str, use_llm: bool = False) -> None:
    if case_name not in CASE_QUERIES:
        valid = ", ".join(sorted(CASE_QUERIES.keys())) + ", all"
        raise ValueError(f"Unknown case: {case_name}. Valid cases: {valid}")

    query = CASE_QUERIES[case_name]

    docs_started = now_ms()
    documents = load_documents()
    all_chunks = build_chunks(documents)
    docs_elapsed_ms = now_ms() - docs_started

    retrieval_started = now_ms()
    retrieved = retrieve(query, all_chunks, top_k=6)
    raw_results = to_mixed_raw_retrieval_results(retrieved)
    normalized_chunks = normalize_reference_results(raw_results)
    retrieval_elapsed_ms = now_ms() - retrieval_started

    prompt = build_prompt(query, normalized_chunks)

    print("=" * 80)
    print(f"SledTrace Reference RAG App case: {case_name}")
    print(f"Query: {query}")
    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(all_chunks)}")
    print(f"Retrieved top-k: {len(normalized_chunks)}")
    print(f"Docs/chunking latency: {docs_elapsed_ms}ms")
    print(f"Retrieval + normalization latency: {retrieval_elapsed_ms}ms")
    print(f"LLM mode: {'real OpenAI-compatible LLM' if use_llm else 'deterministic fallback'}")

    print("\nNormalized retrieved chunks:")
    for chunk in normalized_chunks:
        print(
            f"  rank={chunk.get('rank')} "
            f"score={chunk.get('score')} "
            f"source={chunk.get('source')} "
            f"shape={chunk.get('metadata', {}).get('raw_shape')}"
        )

    trace_name = f"reference-rag-app-{case_name}"

    with trace(
        trace_name,
        query=query,
        metadata={
            "demo": "reference_rag_app",
            "demo_version": "v0.3.5",
            "case": case_name,
            "docs_count": len(documents),
            "chunks_count": len(all_chunks),
            "retrieved_count": len(normalized_chunks),
            "docs_elapsed_ms": docs_elapsed_ms,
            "retrieval_elapsed_ms": retrieval_elapsed_ms,
            "answer_mode": "llm" if use_llm else "deterministic",
        },
    ) as t:
        record_retrieval_span(
            t=t,
            query=query,
            chunks=normalized_chunks,
            elapsed_ms=retrieval_elapsed_ms,
        )

        llm_started = now_ms()

        if use_llm:
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
            base_url = os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL)

            if not api_key:
                raise RuntimeError(
                    "Missing OPENAI_API_KEY. Either set it or run without --llm."
                )

            answer = call_openai_compatible_chat_completion(
                prompt=prompt,
                model=model,
                api_key=api_key,
                base_url=base_url,
            )
            provider = "openai_compatible"
        else:
            model = "deterministic_reference_answer"
            answer = deterministic_answer(case_name)
            provider = "deterministic"

        llm_elapsed_ms = now_ms() - llm_started

        record_llm_span(
            t=t,
            model=model,
            prompt=prompt,
            response=answer,
            elapsed_ms=llm_elapsed_ms,
            provider=provider,
        )

        flush_trace(t)

    print("\nAnswer:")
    print(answer)
    print(f"\nAnswer generation latency: {llm_elapsed_ms}ms")
    print(f"Trace flushed: {trace_name}")
    print("Open the SledTrace dashboard and inspect diagnostics.")
    print("=" * 80)


def parse_args(argv: Sequence[str]) -> tuple[str, bool]:
    args = list(argv)

    use_llm = False
    if "--llm" in args:
        use_llm = True
        args.remove("--llm")

    case_name = args[0] if args else "refund"
    return case_name, use_llm


def main(argv: Optional[Sequence[str]] = None) -> int:
    case_name, use_llm = parse_args(argv if argv is not None else sys.argv[1:])

    try:
        if case_name == "all":
            for name in CASE_QUERIES:
                run_case(name, use_llm=use_llm)
            return 0

        run_case(case_name, use_llm=use_llm)
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except Exception as exc:
        print(f"\nreference_rag_app failed: {exc}\n", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())



