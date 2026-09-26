"""Offline, labeled tool-repeat traces for E4 rule design.

These are scripted counterexamples, not a real Agent or waste verdict. From
sdk/python: python -m examples.agent_repeat_evidence all --flush
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from sledtrace import trace


# Keys below are hand-authored for synthetic data only. They are not hashes of
# private tool arguments, nor a proposed public metadata contract.
CASES: dict[str, dict[str, Any]] = {
    "same_result_stable": {
        "label": "suspected_duplicate_result",
        "completed": True,
        "result": "A policy answer was produced; repeat necessity is unassessed.",
        "attempts": [
            ("policy_lookup", "refund", "five days", "ok", None, "refund", "five-days", "s1"),
            ("policy_lookup", "refund", "five days", "ok", None, "refund", "five-days", "s1"),
        ],
    },
    "polling_changed_state": {
        "label": "normal_polling",
        "completed": True,
        "result": "The job completed after a pending response.",
        "attempts": [
            ("job_status", "job A", "pending", "ok", None, "job-a", "pending", "s1"),
            ("job_status", "job A", "complete", "ok", None, "job-a", "complete", "s2"),
        ],
    },
    "confirmation_unknown_state": {
        "label": "indeterminate",
        "completed": True,
        "result": "A second confirmation was requested; external state is unknown.",
        "attempts": [
            ("approval_status", "request A", "approved", "ok", None, "request-a", "approved", None),
            ("approval_status", "request A", "approved", "ok", None, "request-a", "approved", None),
        ],
    },
    "repeat_error_stable": {
        "label": "suspected_repeated_failure",
        "completed": False,
        "result": "The policy lookup failed twice without a known change.",
        "attempts": [
            ("policy_lookup", "missing", None, "error", "NotFound", "missing", None, "s1"),
            ("policy_lookup", "missing", None, "error", "NotFound", "missing", None, "s1"),
        ],
    },
    "retry_recovered": {
        "label": "normal_retry_recovery",
        "completed": True,
        "result": "The lookup succeeded after a transient timeout.",
        "attempts": [
            ("policy_lookup", "refund", None, "error", "Timeout", "refund", None, "s1"),
            ("policy_lookup", "refund", "five days", "ok", None, "refund", "five-days", "s1"),
        ],
    },
    "corrected_parameter": {
        "label": "normal_parameter_fix",
        "completed": True,
        "result": "The corrected account reference resolved the task.",
        "attempts": [
            ("account_lookup", "invalid ref", None, "error", "InvalidReference", "invalid", None, "s1"),
            ("account_lookup", "corrected ref", "account found", "ok", None, "corrected", "found", "s1"),
        ],
    },
}


def run(case: str, *, collector_url: str | None = None, flush: bool = False) -> dict[str, Any]:
    """Record one synthetic sequence without executing tools or calling a model."""
    if case not in CASES:
        raise ValueError(f"Unknown evidence case: {case}")
    fixture = CASES[case]
    task = trace(
        f"e4-repeat-evidence-{case}",
        metadata={
            "task_id": f"e4-{case}",
            "sample_kind": "internal_scripted_e4_evidence",
            "quality_review": "not_assessed",
            "fixture_label": fixture["label"],
            "fixture_outcome": "completed" if fixture["completed"] else "failed",
        },
        collector_url=collector_url,
    )
    with task:
        task.llm(
            model="scripted-fixture-no-provider",
            name="scripted_tool_choice",
            response="Inspect the synthetic tool result.",
            metadata={"source": "scripted_fixture", "usage_status": "unknown"},
        )
        for name, argument, result, status, error, argument_key, result_key, state in fixture["attempts"]:
            task.tool(
                name,
                input_summary=f"synthetic reference: {argument}",
                output_summary=f"synthetic result: {result}" if result is not None else None,
                status=status,
                error=error,
                metadata={
                    "fixture_comparison": {
                        "argument_key": argument_key,
                        "result_key": result_key,
                        "state_version": state,
                    }
                },
            )
        if fixture["completed"]:
            # A scripted completion is not an answer-quality acceptance.
            task.log_answer(fixture["result"])
        else:
            task.log_task_result(fixture["result"], accepted=False)
    if flush:
        task.flush()
    return task.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=[*CASES, "all"])
    parser.add_argument("--collector-url")
    parser.add_argument("--flush", action="store_true")
    args = parser.parse_args()
    cases = CASES if args.case == "all" else (args.case,)
    print(json.dumps([run(case, collector_url=args.collector_url, flush=args.flush) for case in cases], indent=2))


if __name__ == "__main__":
    main()
