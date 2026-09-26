"""Trace the pinned public PydanticAI bank-support example.

This optional integration exercise imports, rather than copies, the upstream
example. Run ``python -m examples.pydantic_ai_bank_support --help`` for setup.
The default TestModel run is offline and scripted. The explicit live mode can
make a paid OpenAI request using synthetic data; neither is bank advice.
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
LIVE_MODEL = "gpt-4o-mini-2024-07-18"
LIVE_PROMPT = "What is my balance? Use the customer_balance tool before answering."


def run(
    case: str,
    upstream_examples: Path,
    *,
    collector_url: str | None = None,
    flush: bool = False,
    live_openai: bool = False,
    allow_paid_call: bool = False,
) -> dict[str, Any]:
    """Run one synthetic-customer task and return its SledTrace payload."""
    if case not in {"balance", "missing-customer"}:
        raise ValueError("case must be balance or missing-customer")
    if live_openai and case != "balance":
        raise ValueError("live OpenAI mode supports only the balance case")
    if live_openai and not allow_paid_call:
        raise ValueError("live OpenAI mode requires explicit paid-call acknowledgement")
    example_file = upstream_examples / "pydantic_ai_examples" / "bank_support.py"
    if not example_file.is_file():
        raise FileNotFoundError(f"Upstream bank_support.py not found under {upstream_examples}")
    # Normalize Git's optional Windows CRLF checkout conversion.
    source_hash = hashlib.sha256(
        example_file.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()
    if source_hash != UPSTREAM_FILE_SHA256:
        raise RuntimeError("Upstream bank_support.py differs from the pinned source file")
    if live_openai and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is absent in this process")

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
    previous_name_lookup: tuple[int, str | None, str] | None = None
    task = trace(
        "pydantic-ai-bank-support-reference",
        query=LIVE_PROMPT if live_openai else "What is my balance?",
        metadata={
            "task_id": f"bank-support-{case}",
            "variant": "live-openai" if live_openai else "upstream-test-model",
            "sample_kind": (
                "external_synthetic_real_model"
                if live_openai else "external_synthetic_test_model"
            ),
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

    live_request_count = 0

    if live_openai:
        from openai import AsyncOpenAI
        from pydantic_ai import UsageLimits
        from pydantic_ai.models.openai import OpenAIResponsesModel
        from pydantic_ai.models.wrapper import WrapperModel
        from pydantic_ai.providers.openai import OpenAIProvider

        class TracedLiveModel(WrapperModel):
            async def request(
                self, messages: Any, model_settings: Any, model_request_parameters: Any
            ) -> Any:
                nonlocal live_request_count
                # The model is a small synthetic fixture. Abort unexpected
                # context growth before another provider request, not after.
                if live_request_count >= 2 or len(repr(messages)) > 20000:
                    raise RuntimeError("Live Agent probe request/context limit reached")
                live_request_count += 1
                try:
                    with task.measure() as timing:
                        response = await super().request(
                            messages, model_settings, model_request_parameters
                        )
                except Exception as exc:
                    task.llm(
                        model=LIVE_MODEL,
                        name="agent_model_request",
                        status="error",
                        error=type(exc).__name__,
                        metadata={"request_index": live_request_count},
                    )
                    raise
                tool_names = [
                    getattr(part, "tool_name", None)
                    for part in response.parts
                    if type(part).__name__ == "ToolCallPart"
                ]
                step_kind = (
                    "customer_balance_tool_request"
                    if "customer_balance" in tool_names
                    else "structured_output" if tool_names else "model_response"
                )
                usage = response.usage
                input_tokens = getattr(usage, "input_tokens", None)
                output_tokens = getattr(usage, "output_tokens", None)
                task.llm(
                    model=LIVE_MODEL,
                    name="agent_model_request",
                    response=step_kind,
                    input_tokens=(
                        input_tokens if type(input_tokens) is int and input_tokens >= 0 else None
                    ),
                    output_tokens=(
                        output_tokens if type(output_tokens) is int and output_tokens >= 0 else None
                    ),
                    timing=timing,
                    metadata={
                        "request_index": live_request_count,
                        # PydanticAI has parsed the provider response. This is
                        # not the direct Responses-object contract used by
                        # sledtrace.openai.record_response.
                        "usage_capture": "pydantic_ai_model_response",
                    },
                )
                return response

    class ObservedDatabase(upstream.DatabaseConn):
        async def customer_name(self, *, id: int) -> str | None:
            nonlocal previous_name_lookup
            with task.measure() as timing:
                name = await super().customer_name(id=id)
            observed["name"] = name
            metadata: dict[str, Any] = {"execution_origin": "dynamic_instructions"}
            if previous_name_lookup is not None:
                prior_id, prior_name, prior_span_id = previous_name_lookup
                same_argument = prior_id == id
                # Compare actual values only in process. The trace receives
                # booleans and a span reference, never the lookup values.
                metadata["example_repeat_observation"] = {
                    "previous_span_id": prior_span_id,
                    "same_customer_id": same_argument,
                    "same_return_value": prior_name == name if same_argument else None,
                    "fixture_state": "read_only_in_memory_sqlite",
                    "repeat_context": "dynamic_instructions_reevaluated",
                }
            span_id = task.tool(
                "customer_name_lookup",
                input_summary="synthetic customer ID lookup",
                output_summary="customer found" if name is not None else "customer missing",
                metadata=metadata,
                timing=timing,
            )
            previous_name_lookup = (id, name, span_id)
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
        if live_openai:
            # Ignore OPENAI_BASE_URL so an inherited setting cannot silently
            # redirect a paid call. The client reads the key from the process.
            client = AsyncOpenAI(
                base_url="https://api.openai.com/v1", max_retries=0, timeout=25.0
            )
            model = TracedLiveModel(
                OpenAIResponsesModel(LIVE_MODEL, provider=OpenAIProvider(openai_client=client))
            )
            run_options = {
                "model_settings": {"max_tokens": 300},
                "usage_limits": UsageLimits(request_limit=2),
                "retries": 0,
            }
        else:
            model = TracedTestModel(
                custom_output_args={
                    "support_advice": "Hello John, your balance is $123.45.",
                    "block_card": False,
                    "risk": 1,
                }
            )
            run_options = {}
        with task:
            with upstream.support_agent.override(model=model):
                try:
                    result = upstream.support_agent.run_sync(
                        LIVE_PROMPT if live_openai else "What is my balance?",
                        deps=deps,
                        **run_options,
                    )
                except Exception as exc:
                    if not live_openai and (
                        case != "missing-customer" or not isinstance(exc, ValueError)
                    ):
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
    parser.add_argument(
        "--live-openai", action="store_true",
        help="Use real OpenAI model; may incur API charges",
    )
    parser.add_argument(
        "--i-accept-api-costs", action="store_true", help="Required with --live-openai"
    )
    args = parser.parse_args()
    payload = run(
        args.case,
        args.upstream_examples,
        collector_url=args.collector_url,
        flush=args.flush,
        live_openai=args.live_openai,
        allow_paid_call=args.i_accept_api_costs,
    )
    print(json.dumps(payload, indent=2))
    if args.live_openai and payload["trace"]["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
