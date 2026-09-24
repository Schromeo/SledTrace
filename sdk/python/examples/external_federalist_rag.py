"""Trace a local SQLite search over Harvard HBS's Federalist Papers RAG corpus.

This is a small adaptation for an offline SledTrace exercise. The upstream
example uses Chroma and an optional hosted LLM; this script uses SQLite FTS5
and an explicitly simulated extractive answer.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from pathlib import Path

from sledtrace import trace


DEFAULT_QUERY = "What are the latent causes of faction?"


def build_index(pdf_path: Path, db_path: Path) -> int:
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit("Install PyMuPDF first: python -m pip install pymupdf") from exc

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db, fitz.open(pdf_path) as pdf:
        db.execute("DROP TABLE IF EXISTS passages")
        db.execute("CREATE VIRTUAL TABLE passages USING fts5(source, page UNINDEXED, text)")
        rows = []
        for page_number, page in enumerate(pdf, start=1):
            text = " ".join(page.get_text().split())
            # Page-based chunks follow the source document's natural boundary.
            if text:
                rows.append((pdf_path.name, page_number, text))
        db.executemany("INSERT INTO passages(source, page, text) VALUES (?, ?, ?)", rows)
        db.commit()
    return len(rows)


def search(db_path: Path, query: str, limit: int = 3) -> list[dict]:
    terms = [term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 3]
    if not terms:
        raise ValueError("Query needs at least one word longer than three characters")
    match = " OR ".join(f'"{term}"' for term in dict.fromkeys(terms))
    with sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True) as db:
        rows = db.execute(
            "SELECT rowid, source, page, text, bm25(passages) AS distance "
            "FROM passages WHERE passages MATCH ? ORDER BY distance LIMIT ?",
            (match, limit),
        ).fetchall()
    return [
        {
            "id": f"page-{page}-{rowid}",
            "source": f"{source}#page={page}",
            "text": text,
            "score": distance,
            "score_type": "bm25",
            "score_direction": "lower_is_better",
            "rank": rank,
            "metadata": {"page": page, "source_document": source},
        }
        for rank, (rowid, source, page, text, distance) in enumerate(rows, start=1)
    ]


def simulated_answer(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return "No matching source passage was found."
    terms = set(re.findall(r"[a-z0-9]+", query.lower())) - {
        "what", "are", "the", "of", "how", "why", "according", "to",
    }
    candidates = [
        (sentence.strip(), chunk["source"])
        for chunk in chunks
        for sentence in re.split(r"(?<=[.!?])\s+", chunk["text"])
        if 40 <= len(sentence.strip()) <= 500
    ]
    if not candidates:
        return "No complete source sentence was found."
    sentence, source = max(
        candidates,
        key=lambda item: sum(term in item[0].lower().split() for term in terms),
    )
    return f"{sentence} [{source}]"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True, help="Upstream Federalist Papers PDF")
    parser.add_argument("--db", type=Path, default=Path("federalist_fts.db"))
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--collector-url", default="http://127.0.0.1:4319")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    if not args.pdf.is_file():
        parser.error(f"PDF not found: {args.pdf}")
    if args.rebuild or not args.db.is_file():
        count = build_index(args.pdf, args.db)
        print(f"Indexed {count} PDF pages in {args.db}")

    pdf_sha256 = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
    with trace(
        "external-federalist-rag",
        query=args.query,
        metadata={
            "source_project": "harvard-hbs/rag-example",
            "source_pdf_sha256": pdf_sha256,
            "retriever": "sqlite-fts5-bm25",
            "answer_mode": "extractive-simulation",
        },
        collector_url=args.collector_url,
    ) as current:
        with current.measure() as retrieval_timing:
            chunks = search(args.db, args.query)
        current.retrieval(
            query=args.query,
            chunks=chunks,
            name="federalist_sqlite_fts5",
            top_k=3,
            metadata={"score_type": "bm25", "score_direction": "lower_is_better"},
            timing=retrieval_timing,
        )
        with current.measure() as answer_timing:
            answer = simulated_answer(args.query, chunks)
        current.llm(
            model="extractive-simulator",
            provider="local-simulation",
            prompt=args.query,
            response=answer,
            name="simulated_answer",
            metadata={"simulated": True},
            timing=answer_timing,
        )

    response = current.flush()
    print(f"Trace: {current.trace_id}; retrieved pages: {[c['metadata']['page'] for c in chunks]}")
    print(f"Simulated answer: {answer[:240]}")
    print(f"Collector response: {response}")


if __name__ == "__main__":
    main()
