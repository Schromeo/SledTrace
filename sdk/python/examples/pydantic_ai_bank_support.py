"""Trace the upstream PydanticAI bank-support sample with a no-cost TestModel.

This optional integration exercise imports, rather than copies, the upstream
example. Run ``python -m examples.pydantic_ai_bank_support --help`` for setup.
No provider request is made; TestModel output is scripted, not bank advice.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

from sledtrace import trace


UPSTREAM_COMMIT = "92e0b457bd1628d17e959f9b12d74568946a2709"
UPSTREAM_FILE_SHA256 = "9fe72475bd293d83f1e534dbf04f865d7f0f531f15ce87de9e03fbbe2ca3505c"


def run(
    case: str,
    upstream_examples: Path,
    *,
    collector_url: str | None = None,
    flush: bool = False,
) -> dict[str, Any]:
    """Run one synthetic-customer task and return its SledTrace payload."""
    if case not in {"balance", "missing-customer"}:
        raise ValueError("case must be balance or missing-customer")
    example_file = upstream_examples / "pydantic_ai_examples" / "bank_support.py"
    if not example_file.is_file():
        raise FileNotFoundError(f"Upstream bank_support.py not found under {upstream_examples}")
    # Normalize Git's optional Windows CRLF checkout conversion.
    source_hash = hashlib.sha256(
        example_file.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    if source_hash != UPSTREAM_FILE_SHA256:
        raise RuntimeError("Upstream bank_support.py differs from the pinned source file")

    try:
        from pydantic_ai.models.test import TestModel
    except ImportError as exc:
        raise RuntimeError("Install optional pydantic-ai-slim==2.50.0 first") from exc

    sys.path.insert(0, str(upstream_examples))
    try:
        # Upstream constructs an OpenAI Agent at import time, before we can
        # override it. Force a dummy key and loopback-only endpoint so neither
        # a real user key nor the public API can be used, even on a mistake.
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "sk-a1-offline-placeholder",
                "OPENAI_BASE_URL": "http://127.0.0.1:9",
            },
        ):
            upstream = importlib.import_module("pydantic_ai_examples.bank_support")
    finally:
        sys.path.remove(str(upstream_examples))

    customer_id = 123 if case == "balance" else 999
    observed: dict[str, Any] = {"name": None, "balance": None}
    task = trace(
        "pydantic-ai-bank-support-reference",
        query="What is my balance?",
        metadata={
            "task_id": f"bank-support-{case}",
            "variant": "upstream-test-model",
            "sample_kind": "external_synthetic_test_model",
            "quality_review": "not_assessed",
            "upstream_commit": UPSTREAM_COMMIT,
        },
        collector_url=collector_url,
    )
    task.metadata["run_id"] = task.trace_id

    class TracedTestModel(TestModel):
        async def request(self, messages: Any, model_settings: Any, model_request_parameters: Any) -> Any:
            with task.measure() as timing:
                response = await super().request(messages, model_settings, model_request_parameters)
            step_kind = (
                "tool_request"
                if any(type(part).__name__ == "ToolCallPart" for part in response.parts)
                else "final_output"
            )
            task.llm(
                model="pydantic-test-model",
                name="test_model_attempt",
                response=step_kind,
                timing=timing,
                metadata={"source": "scripted_test_model", "usage_status": "unknown"},
            )
            return response

    class ObservedDatabase(upstream.DatabaseConn):
        async def customer_name(self, *, id: int) -> str | None:
            with task.measure() as timing:
                name = await super().customer_name(id=id)
            observed["name"] = name
            task.tool(
                "customer_name_lookup",
                input_summary="synthetic customer ID lookup",
                output_summary="customer found" if name is not None else "customer missing",
                metadata={"execution_origin": "dynamic_instructions"},
                timing=timing,
            )
            return name

        async def customer_balance(self, *, id: int) -> float:
            try:
                with task.measure() as timing:
                    balance = await super().customer_balance(id=id)
            except ValueError as exc:
                task.tool(
                    "customer_balance",
                    input_summary="synthetic customer ID lookup",
                    status="error",
                    error=str(exc),
                    metadata={"execution_origin": "agent_tool"},
                    timing=timing,
                )
                raise
            observed["balance"] = balance
            task.tool(
                "customer_balance",
                input_summary="synthetic customer ID lookup",
                output_summary="balance found",
                metadata={"execution_origin": "agent_tool"},
                timing=timing,
            )
            return balance

    with sqlite3.connect(":memory:") as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE customers(id INTEGER, name TEXT, balance REAL)")
        cursor.execute("INSERT INTO customers VALUES (123, 'John', 123.45)")
        connection.commit()
        # The pinned upstream sample reads a module-level ``cur`` created by
        # its __main__ block, rather than DatabaseConn.sqlite_conn.
        upstream.cur = cursor
        deps = upstream.SupportDependencies(
            customer_id=customer_id,
            db=ObservedDatabase(sqlite_conn=connection),
        )
        model = TracedTestModel(
            custom_output_args={
                "support_advice": "Hello John, your balance is $123.45.",
                "block_card": False,
                "risk": 1,
            }
        )
        with task:
            with upstream.support_agent.override(model=model):
                try:
                    result = upstream.support_agent.run_sync(
                        "What is my balance?", deps=deps
                    )
                except ValueError as exc:
                    if case != "missing-customer":
                        raise
                    task.metadata["structural_pass"] = False
                    task.log_task_result(
                        f"Bank support task failed: {type(exc).__name__}",
                        accepted=False,
                    )
                else:
                    if case == "missing-customer":
                        raise AssertionError("Missing customer unexpectedly succeeded")
                    structural_pass = (
                        isinstance(result.output, upstream.SupportOutput)
                        and result.output.block_card is False
                        and observed == {"name": "John", "balance": 123.45}
                    )
                    task.metadata["structural_pass"] = structural_pass
                    if structural_pass:
                        # The TestModel's scripted answer is not a human
                        # quality judgment. Do not show "Acceptance: passed".
                        task.log_answer(str(result.output))
                    else:
                        task.log_task_result("Structural fixture check failed", accepted=False)

    if flush:
        task.flush()
    return task.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=["balance", "missing-customer"])
    parser.add_argument(
        "--upstream-examples",
        type=Path,
        required=True,
        help="Path to the pinned PydanticAI repository's examples directory",
    )
    parser.add_argument("--collector-url")
    parser.add_argument("--flush", action="store_true")
    args = parser.parse_args()
    payload = run(
        args.case,
        args.upstream_examples,
        collector_url=args.collector_url,
        flush=args.flush,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
