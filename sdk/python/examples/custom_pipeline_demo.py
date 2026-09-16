from sledtrace import trace


def my_retriever(query: str) -> list[dict]:
    """Stand-in for the user's existing retriever."""
    normalized_query = query.strip().lower()

    if "refund" in normalized_query:
        return [
            {
                "id": "chunk_refund_current",
                "text": "Customers may request a refund within 30 days of purchase.",
                "score": 0.93,
                "rank": 1,
                "source": "refund_policy.md",
                "document_id": "refund_policy",
                "metadata": {
                    "section": "refund_window",
                    "policy_version": "current",
                },
            },
            {
                "id": "chunk_returns_general",
                "text": "Refund requests must be submitted through the customer support portal.",
                "score": 0.78,
                "rank": 2,
                "source": "returns_process.md",
                "document_id": "returns_process",
                "metadata": {
                    "section": "submission_process",
                },
            },
        ]

    return [
        {
            "id": "chunk_default",
            "text": "No specific policy match was found in the local knowledge base.",
            "score": 0.22,
            "rank": 1,
            "source": "fallback_notes.md",
            "document_id": "fallback_notes",
            "metadata": {
                "section": "fallback",
            },
        }
    ]


def my_answerer(query: str, chunks: list[dict]) -> tuple[str, str]:
    """Stand-in for the user's existing prompt builder and answerer."""
    context_lines = []

    for chunk in chunks:
        context_lines.append(
            f"[{chunk['rank']}] {chunk['text']}"
        )

    prompt = (
        "Answer the user question using the retrieved context.\n\n"
        f"Question: {query}\n\n"
        "Retrieved context:\n"
        + "\n".join(context_lines)
    )

    if chunks and "refund within 30 days" in chunks[0]["text"].lower():
        answer = "The refund window is 30 days from purchase."
    else:
        answer = "I could not find enough information to answer that question."

    return prompt, answer


def answer_question(user_query: str) -> str:
    with trace(
        name="custom-rag-pipeline",
        query=user_query,
        metadata={
            "app": "custom-pipeline-demo",
            "environment": "local",
            "demo": "developer_integration",
        },
    ) as t:
        with t.measure() as retrieval_timing:
            chunks = my_retriever(user_query)

        t.retrieval(
            query=user_query,
            chunks=chunks,
            name="custom_retrieval",
            top_k=len(chunks),
            metadata={
                "retriever": "deterministic_local_retriever",
            },
            timing=retrieval_timing,
        )

        with t.measure() as llm_timing:
            prompt, answer = my_answerer(user_query, chunks)

        t.llm(
            model="local-template-answerer-v1",
            prompt=prompt,
            response=answer,
            name="custom_answer_generation",
            provider="local-demo",
            timing=llm_timing,
        )

    t.flush()
    return answer


def main() -> None:
    query = "What is the refund window?"
    answer = answer_question(query)

    print(f"Query: {query}")
    print(f"Answer: {answer}")
    print("Trace flushed to the local SledTrace collector.")


if __name__ == "__main__":
    main()


