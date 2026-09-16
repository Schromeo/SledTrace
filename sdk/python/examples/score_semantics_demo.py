"""Generate deterministic traces for retrieval score semantics validation."""

from __future__ import annotations

from sledtrace import normalize_chunk, trace


QUERY = "What does the refund policy allow?"
TEXT = "The refund policy allows customers to return eligible products."
ANSWER = "The refund policy allows returns for eligible products."


def send_trace(name: str, raw_chunk: dict[str, object]) -> str:
    chunk = normalize_chunk(raw_chunk, rank=1)

    with trace(name, query=QUERY, metadata={"demo": "score-semantics"}) as current:
        current.retrieval(
            query=QUERY,
            chunks=[chunk],
            name="semantic_retrieval",
            top_k=1,
            duration_ms=5,
        )
        current.llm(
            model="deterministic-score-demo",
            prompt=f"Answer from this context: {TEXT}",
            response=ANSWER,
            name="grounded_answer",
            provider="local-demo",
            latency_ms=5,
        )
        current.log_answer(ANSWER)

    current.flush()
    return current.trace_id


def main() -> None:
    similarity_trace_id = send_trace(
        "score-semantics-similarity-low",
        {
            "id": "similarity-low",
            "text": TEXT,
            "source": "refund_policy.md",
            "similarity": 0.1,
        },
    )
    distance_trace_id = send_trace(
        "score-semantics-distance-near",
        {
            "id": "distance-near",
            "text": TEXT,
            "source": "refund_policy.md",
            "distance": 0.1,
        },
    )

    print(f"Sent similarity trace: {similarity_trace_id}")
    print(f"Sent distance trace: {distance_trace_id}")


if __name__ == "__main__":
    main()
