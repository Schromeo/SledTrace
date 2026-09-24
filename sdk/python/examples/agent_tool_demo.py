"""Deterministic one-tool Python workflow for the bounded E2 contract.

No model or paid API is called. This is integration evidence, not an external
developer trial or proof that the diagnostics improve a real agent.

From sdk/python: python -m examples.agent_tool_demo success --flush
"""

from __future__ import annotations

import argparse
from typing import Optional

from sledtrace import trace


DOCUMENTS = {
    "refund": "Refund requests are reviewed within five business days.",
}


def run(case: str, collector_url: Optional[str] = None, flush: bool = False) -> dict:
    task = trace(
        "policy-review-agent",
        metadata={
            "task_id": f"policy-{case}",
            "run_id": f"e2-{case}-001",
            "variant": "baseline",
            "app_version": "e2-fixture-1",
            "sample_kind": "internal_deterministic",
        },
        collector_url=collector_url,
    )
    with task:
        task.llm(
            model="deterministic-fixture",
            prompt="Choose one policy to inspect.",
            response="Inspect refund policy.",
            input_tokens=6,
            output_tokens=4,
        )

        if case == "business-failure":
            key = "missing-policy"
        else:
            key = "refund"

        if case == "tool-recovery":
            task.tool(
                "policy_lookup",
                input_summary="policy key: refund",
                status="error",
                error="temporary document index unavailable",
                duration_ms=0,
            )

        with task.measure() as timing:
            document = DOCUMENTS.get(key)
        task.tool(
            "policy_lookup",
            input_summary=f"policy key: {key}",
            output_summary="one policy found" if document else "no policy found",
            timing=timing,
        )

        if document is None:
            task.llm(
                model="deterministic-fixture",
                prompt="Summarize the missing policy.",
                response="Cannot substantiate a policy summary.",
                input_tokens=7,
                output_tokens=5,
                status="error",
                error="required document not found",
            )
            task.log_task_result("Policy review failed: document missing", accepted=False)
        else:
            task.llm(
                model="deterministic-fixture",
                prompt="Summarize the retrieved policy.",
                response="Draft: five business days.",
                input_tokens=8,
                output_tokens=6,
            )
            task.log_task_result("Refund review: five business days", accepted=True)

    if flush:
        task.flush()
    return task.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=["success", "business-failure", "tool-recovery"])
    parser.add_argument("--collector-url")
    parser.add_argument("--flush", action="store_true")
    args = parser.parse_args()
    import json

    print(json.dumps(run(args.case, args.collector_url, args.flush), indent=2))


if __name__ == "__main__":
    main()
