"""A copyable, dependency-free SledTrace integration example.

Install ``sledtrace`` into any Python environment, copy this file outside the
SledTrace repository, and run one of the three cases documented by ``--help``.
The retriever and answerer are deterministic stand-ins for application-owned
code; only the tracing calls are SledTrace-specific.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from sledtrace import SledTraceTrace, trace


QUERY = "What is the refund window?"
DASHBOARD_URL = "http://127.0.0.1:5173"


class ExampleBusinessError(RuntimeError):
    """Intentional application error used to demonstrate trace semantics."""


def retrieve_documents(query: str) -> list[dict]:
    """Stand-in for an application-owned retriever."""
    return [
        {
            "id": "refund-policy-current",
            "text": "Refund requests are accepted within 30 days of purchase.",
            "score": 0.94,
            "score_type": "similarity",
            "score_direction": "higher_is_better",
            "source": "refund_policy.md",
            "document_id": "refund-policy",
            "metadata": {"query": query, "policy_version": "current"},
        }
    ]


def generate_answer(query: str, chunks: list[dict]) -> tuple[str, str]:
    """Stand-in for an application-owned prompt builder and model call."""
    context = chunks[0]["text"]
    prompt = f"Answer from the provided context.\nQuestion: {query}\nContext: {context}"
    return prompt, "The refund window is 30 days from purchase."


def new_trace(name: str, collector_url: Optional[str]) -> SledTraceTrace:
    return trace(
        name=name,
        query=QUERY,
        collector_url=collector_url,
        metadata={"app": "independent-python-example", "example_case": name},
    )


def record_retrieval(current_trace: SledTraceTrace) -> list[dict]:
    with current_trace.measure() as retrieval_timing:
        chunks = retrieve_documents(QUERY)

    current_trace.retrieval(
        query=QUERY,
        chunks=chunks,
        name="policy_retrieval",
        top_k=len(chunks),
        timing=retrieval_timing,
        metadata={"retriever": "application-owned-demo"},
    )
    return chunks


def record_answer(current_trace: SledTraceTrace, chunks: list[dict]) -> str:
    with current_trace.measure() as llm_timing:
        prompt, answer = generate_answer(QUERY, chunks)

    current_trace.llm(
        model="application-owned-demo-model",
        prompt=prompt,
        response=answer,
        name="answer_generation",
        provider="local-demo",
        timing=llm_timing,
    )
    return answer


def run_success(collector_url: Optional[str], timeout: float, dashboard_url: str) -> int:
    current_trace = new_trace("independent-app-success", collector_url)
    with current_trace:
        chunks = record_retrieval(current_trace)
        answer = record_answer(current_trace, chunks)

    response = current_trace.flush(timeout=timeout)
    print(f"BUSINESS RESULT: {answer}")
    print(
        "PASS: trace stored "
        f"(trace_id={current_trace.trace_id}, status={response.get('status', 'unknown')})."
    )
    print(f"Open {dashboard_url} and refresh Traces.")
    return 0


def run_application_error(
    collector_url: Optional[str], timeout: float, dashboard_url: str
) -> int:
    current_trace = new_trace("independent-app-application-error", collector_url)
    delivery = None

    try:
        try:
            with current_trace:
                record_retrieval(current_trace)
                raise ExampleBusinessError("inventory service rejected the request")
        finally:
            delivery = current_trace.try_flush(timeout=timeout)
    except ExampleBusinessError as error:
        print(f"EXPECTED APPLICATION ERROR: {type(error).__name__}: {error}")
        if delivery is not None and delivery.ok:
            print(f"SLEDTRACE DELIVERY: stored error trace {current_trace.trace_id}.")
            print(f"Open {dashboard_url} and refresh Traces.")
        else:
            delivery_error = delivery.error if delivery is not None else "not attempted"
            print(f"SLEDTRACE DELIVERY FAILED: {delivery_error}", file=sys.stderr)
        return 2

    raise AssertionError("The intentional application error did not propagate.")


def run_collector_offline(collector_url: Optional[str], timeout: float) -> int:
    current_trace = new_trace("independent-app-collector-offline", collector_url)
    with current_trace:
        chunks = record_retrieval(current_trace)
        answer = record_answer(current_trace, chunks)

    print(f"BUSINESS RESULT: {answer}")
    delivery = current_trace.try_flush(timeout=timeout)
    if delivery.ok:
        print(
            "UNEXPECTED: trace delivery succeeded. Use --collector-url with a closed "
            "local port to exercise the offline case.",
            file=sys.stderr,
        )
        return 3

    print(
        f"EXPECTED SLEDTRACE DELIVERY FAILURE: {type(delivery.error).__name__}: "
        f"{delivery.error}",
        file=sys.stderr,
    )
    print("The application result remains available because try_flush() was explicit.")
    return 1


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a standalone SledTrace integration outcome."
    )
    parser.add_argument(
        "case",
        choices=("success", "application-error", "collector-offline"),
        help=(
            "success stores an ok trace; application-error stores an error trace and "
            "returns 2; collector-offline preserves the business result and returns 1"
        ),
    )
    parser.add_argument(
        "--collector-url",
        help="Collector base URL; otherwise the SDK environment/default is used.",
    )
    parser.add_argument(
        "--dashboard-url",
        default=DASHBOARD_URL,
        help=f"Dashboard URL printed after stored traces (default: {DASHBOARD_URL}).",
    )
    parser.add_argument(
        "--timeout",
        default=2.0,
        type=float,
        help="Trace delivery timeout in seconds (default: 2.0).",
    )
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    return args


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    if args.case == "success":
        return run_success(args.collector_url, args.timeout, args.dashboard_url)
    if args.case == "application-error":
        return run_application_error(
            args.collector_url, args.timeout, args.dashboard_url
        )
    return run_collector_offline(args.collector_url, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
