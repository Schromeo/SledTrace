"""Generate measured and unmeasured traces for Dashboard timing validation."""

from __future__ import annotations

import time

from sledtrace import trace


QUERY = "How long is the refund window?"
CHUNKS = [
    {
        "id": "timing-refund-policy",
        "text": "Customers may request a refund within 30 days of purchase.",
        "score": 0.93,
        "rank": 1,
        "source": "refund_policy.md",
        "metadata": {"demo": "timing"},
    }
]
ANSWER = "The refund window is 30 days from purchase."


def send_measured_trace() -> None:
    with trace("timing-validation-measured", query=QUERY) as current_trace:
        with current_trace.measure() as retrieval_timing:
            time.sleep(0.08)
            chunks = list(CHUNKS)

        current_trace.retrieval(
            query=QUERY,
            chunks=chunks,
            name="measured_retrieval",
            timing=retrieval_timing,
        )

        with current_trace.measure() as llm_timing:
            time.sleep(0.12)
            answer = ANSWER

        current_trace.llm(
            model="deterministic-timing-demo",
            prompt=f"Answer from this context: {chunks[0]['text']}",
            response=answer,
            name="measured_llm",
            provider="local-demo",
            timing=llm_timing,
        )

    current_trace.flush()


def send_unmeasured_trace() -> None:
    with trace("timing-validation-unmeasured", query=QUERY) as current_trace:
        current_trace.retrieval(
            query=QUERY,
            chunks=list(CHUNKS),
            name="post_hoc_retrieval",
        )
        current_trace.llm(
            model="deterministic-timing-demo",
            prompt=f"Answer from this context: {CHUNKS[0]['text']}",
            response=ANSWER,
            name="post_hoc_llm",
            provider="local-demo",
        )

    current_trace.flush()


def main() -> None:
    send_measured_trace()
    send_unmeasured_trace()
    print("Sent timing-validation-measured and timing-validation-unmeasured.")


if __name__ == "__main__":
    main()
