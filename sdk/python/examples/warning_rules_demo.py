import argparse
import json
from typing import Callable

from sledtrace import trace


def print_and_flush(t):
    print(t.to_json())

    response = t.flush()
    print("\nSent trace to SledTrace collector:")
    print(response)
    print("-" * 80)


def run_conflicting_chunks_demo():
    query = "What is the refund window?"

    with trace(
        name="warning-conflicting-chunks-demo",
        query=query,
        metadata={
            "sdk_language": "python",
            "sdk_version": "0.6.0",
            "app": "warning-rules-demo",
            "case": "conflicting_chunks",
            "environment": "local",
        },
    ) as t:
        chunks = [
            {
                "id": "chunk_1",
                "text": "Customers may request a refund within 30 days.",
                "score": 0.91,
                "source": "refund_policy_new.md",
                "document_id": "refund_policy_new",
                "metadata": {
                    "version": "2026",
                    "policy_type": "refund",
                },
                "rank": 1,
            },
            {
                "id": "chunk_2",
                "text": "Customers may request a refund within 14 days.",
                "score": 0.84,
                "source": "refund_policy_old.md",
                "document_id": "refund_policy_old",
                "metadata": {
                    "version": "2024",
                    "policy_type": "refund",
                },
                "rank": 2,
            },
        ]

        t.retrieval(
            name="search_refund_docs",
            query=query,
            chunks=chunks,
            top_k=2,
            metadata={
                "retriever": "mock_vector_store",
                "embedding_model": "mock-embedding-model",
            },
        )

        answer = "Customers may request a refund within 14 days."

        t.llm(
            name="generate_answer",
            model="gpt-4o-mini",
            prompt=(
                "Answer the user question using the retrieved context.\n\n"
                f"Question: {query}\n\n"
                "Context:\n"
                "1. Customers may request a refund within 30 days.\n"
                "2. Customers may request a refund within 14 days."
            ),
            response=answer,
            metadata={
                "temperature": 0.2,
                "provider": "openai",
                "input_tokens": 320,
                "output_tokens": 80,
                "total_tokens": 400,
                "latency_ms": 900,
            },
        )

    print_and_flush(t)


def run_no_chunks_demo():
    query = "What is the warranty policy?"

    with trace(
        name="warning-no-retrieved-chunks-demo",
        query=query,
        metadata={
            "sdk_language": "python",
            "sdk_version": "0.6.0",
            "app": "warning-rules-demo",
            "case": "no_retrieved_chunks",
            "environment": "local",
        },
    ) as t:
        t.retrieval(
            name="search_empty_docs",
            query=query,
            chunks=[],
            top_k=3,
            metadata={
                "retriever": "mock_vector_store",
                "embedding_model": "mock-embedding-model",
            },
        )

        answer = "I could not find enough information to answer this question."

        t.llm(
            name="generate_answer",
            model="gpt-4o-mini",
            prompt=(
                "Answer the user question using the retrieved context.\n\n"
                f"Question: {query}\n\n"
                "Context:\n"
            ),
            response=answer,
            metadata={
                "temperature": 0.2,
                "provider": "openai",
                "input_tokens": 120,
                "output_tokens": 20,
                "total_tokens": 140,
                "latency_ms": 500,
            },
        )

    print_and_flush(t)


def run_low_score_demo():
    query = "How do customers reset their account password?"

    with trace(
        name="warning-low-retrieval-score-demo",
        query=query,
        metadata={
            "sdk_language": "python",
            "sdk_version": "0.6.0",
            "app": "warning-rules-demo",
            "case": "low_retrieval_score",
            "environment": "local",
        },
    ) as t:
        chunks = [
            {
                "id": "chunk_1",
                "text": "The company cafeteria is open from 9 AM to 5 PM.",
                "score": 0.31,
                "source": "office_policy.md",
                "document_id": "office_policy",
                "metadata": {
                    "policy_type": "office",
                },
                "rank": 1,
            },
            {
                "id": "chunk_2",
                "text": "Employees can reserve conference rooms through the workplace portal.",
                "score": 0.27,
                "source": "workplace_policy.md",
                "document_id": "workplace_policy",
                "metadata": {
                    "policy_type": "workplace",
                },
                "rank": 2,
            },
        ]

        t.retrieval(
            name="search_password_docs",
            query=query,
            chunks=chunks,
            top_k=2,
            metadata={
                "retriever": "mock_vector_store",
                "embedding_model": "mock-embedding-model",
                "low_score_threshold": 0.5,
            },
        )

        answer = "Customers can reset their password from the account settings page."

        t.llm(
            name="generate_answer",
            model="gpt-4o-mini",
            prompt=(
                "Answer the user question using the retrieved context.\n\n"
                f"Question: {query}\n\n"
                "Context:\n"
                "1. The company cafeteria is open from 9 AM to 5 PM.\n"
                "2. Employees can reserve conference rooms through the workplace portal."
            ),
            response=answer,
            metadata={
                "temperature": 0.2,
                "provider": "openai",
                "input_tokens": 260,
                "output_tokens": 50,
                "total_tokens": 310,
                "latency_ms": 700,
            },
        )

    print_and_flush(t)


def run_duplicate_chunks_demo():
    query = "What is the shipping policy?"

    with trace(
        name="warning-duplicate-chunks-demo",
        query=query,
        metadata={
            "sdk_language": "python",
            "sdk_version": "0.6.0",
            "app": "warning-rules-demo",
            "case": "duplicate_chunks",
            "environment": "local",
        },
    ) as t:
        chunks = [
            {
                "id": "chunk_1",
                "text": "Standard shipping is available for domestic orders.",
                "score": 0.88,
                "source": "shipping_policy.md",
                "document_id": "shipping_policy",
                "metadata": {
                    "section": "standard_shipping",
                },
                "rank": 1,
            },
            {
                "id": "chunk_2",
                "text": " standard   shipping is available for domestic orders. ",
                "score": 0.86,
                "source": "shipping_policy_copy.md",
                "document_id": "shipping_policy_copy",
                "metadata": {
                    "section": "standard_shipping_duplicate",
                },
                "rank": 2,
            },
        ]

        t.retrieval(
            name="search_shipping_docs",
            query=query,
            chunks=chunks,
            top_k=2,
            metadata={
                "retriever": "mock_vector_store",
                "embedding_model": "mock-embedding-model",
            },
        )

        answer = "Standard shipping is available for domestic orders."

        t.llm(
            name="generate_answer",
            model="gpt-4o-mini",
            prompt=(
                "Answer the user question using the retrieved context.\n\n"
                f"Question: {query}\n\n"
                "Context:\n"
                "1. Standard shipping is available for domestic orders.\n"
                "2. standard shipping is available for domestic orders."
            ),
            response=answer,
            metadata={
                "temperature": 0.2,
                "provider": "openai",
                "input_tokens": 210,
                "output_tokens": 30,
                "total_tokens": 240,
                "latency_ms": 600,
            },
        )

    print_and_flush(t)


def run_ungrounded_answer_demo():
    query = "What is the refund window?"

    with trace(
        name="warning-answer-not-grounded-demo",
        query=query,
        metadata={
            "sdk_language": "python",
            "sdk_version": "0.6.0",
            "app": "warning-rules-demo",
            "case": "answer_not_grounded",
            "environment": "local",
        },
    ) as t:
        chunks = [
            {
                "id": "chunk_1",
                "text": "Customers may request a refund within 30 days.",
                "score": 0.93,
                "source": "refund_policy.md",
                "document_id": "refund_policy",
                "metadata": {
                    "version": "2026",
                    "policy_type": "refund",
                },
                "rank": 1,
            }
        ]

        t.retrieval(
            name="search_refund_docs",
            query=query,
            chunks=chunks,
            top_k=1,
            metadata={
                "retriever": "mock_vector_store",
                "embedding_model": "mock-embedding-model",
            },
        )

        answer = "Customers may request a refund within 14 days."

        t.llm(
            name="generate_answer",
            model="gpt-4o-mini",
            prompt=(
                "Answer the user question using the retrieved context.\n\n"
                f"Question: {query}\n\n"
                "Context:\n"
                "1. Customers may request a refund within 30 days."
            ),
            response=answer,
            metadata={
                "temperature": 0.2,
                "provider": "openai",
                "input_tokens": 220,
                "output_tokens": 40,
                "total_tokens": 260,
                "latency_ms": 800,
            },
        )

    print_and_flush(t)


DEMOS: dict[str, Callable[[], None]] = {
    "conflicting": run_conflicting_chunks_demo,
    "no_chunks": run_no_chunks_demo,
    "low_score": run_low_score_demo,
    "duplicate": run_duplicate_chunks_demo,
    "ungrounded": run_ungrounded_answer_demo,
}


def main():
    parser = argparse.ArgumentParser(
        description="Run SledTrace warning rule demos."
    )
    parser.add_argument(
        "demo",
        nargs="?",
        default="all",
        choices=["all", *DEMOS.keys()],
        help="Which warning rule demo to run.",
    )

    args = parser.parse_args()

    if args.demo == "all":
        for name, demo_func in DEMOS.items():
            print(f"\nRunning demo: {name}")
            print("=" * 80)
            demo_func()
        return

    print(f"\nRunning demo: {args.demo}")
    print("=" * 80)
    DEMOS[args.demo]()


if __name__ == "__main__":
    main()


