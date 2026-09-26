from __future__ import annotations

import json
import os
import socket
from pathlib import Path

import pytest

from examples.pydantic_ai_bank_support import run


def test_invalid_case_is_rejected_before_optional_import(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="case must be"):
        run("unsupported", tmp_path)


def test_modified_upstream_source_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "pydantic_ai_examples" / "bank_support.py"
    source.parent.mkdir()
    source.write_text("# not the pinned source\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="differs from the pinned"):
        run("balance", tmp_path)


def test_live_mode_requires_explicit_cost_acknowledgement(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="paid-call acknowledgement"):
        run("balance", tmp_path, live_openai=True)
    with pytest.raises(ValueError, match="only the balance case"):
        run("missing-customer", tmp_path, live_openai=True, allow_paid_call=True)


def test_real_upstream_workflow_stays_offline_and_preserves_unknown_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    examples_path = os.environ.get("SLEDTRACE_A1_UPSTREAM_EXAMPLES")
    if not examples_path:
        pytest.skip("Set SLEDTRACE_A1_UPSTREAM_EXAMPLES for optional upstream check")
    pytest.importorskip("pydantic_ai")

    original_connect = socket.socket.connect

    def refuse_external_network(sock: socket.socket, address: object) -> None:
        # Windows asyncio creates a loopback socket pair to run coroutines.
        if (
            isinstance(address, tuple)
            and address[0] in {"127.0.0.1", "::1"}
            and address[1] != 9
        ):
            return original_connect(sock, address)
        raise AssertionError("A1 TestModel run attempted a provider connection")

    monkeypatch.setattr(socket.socket, "connect", refuse_external_network)
    monkeypatch.setenv("OPENAI_API_KEY", "a1-preexisting-key-must-not-be-used")
    upstream_examples = Path(examples_path)

    success = run("balance", upstream_examples)
    assert success["trace"]["status"] == "ok"
    assert "accepted" not in success["trace"]["output"]
    assert success["trace"]["metadata"]["structural_pass"] is True
    assert success["trace"]["metadata"]["quality_review"] == "not_assessed"
    assert [span["name"] for span in success["spans"]] == [
        "customer_name_lookup",
        "test_model_attempt",
        "customer_balance",
        "customer_name_lookup",
        "test_model_attempt",
    ]
    assert all("total_tokens" not in span["metadata"] for span in success["spans"])
    assert success["spans"][0]["metadata"]["execution_origin"] == "dynamic_instructions"
    assert success["spans"][2]["metadata"]["execution_origin"] == "agent_tool"
    assert "example_repeat_observation" not in success["spans"][0]["metadata"]
    repeat = success["spans"][3]["metadata"]["example_repeat_observation"]
    assert repeat == {
        "previous_span_id": success["spans"][0]["span_id"],
        "same_customer_id": True,
        "same_return_value": True,
        "fixture_state": "read_only_in_memory_sqlite",
        "repeat_context": "dynamic_instructions_reevaluated",
    }
    assert "John" not in json.dumps(repeat)
    assert "a1-preexisting-key-must-not-be-used" not in json.dumps(success)

    failure = run("missing-customer", upstream_examples)
    assert failure["trace"]["status"] == "error"
    assert failure["trace"]["output"]["accepted"] is False
    assert [span["status"] for span in failure["spans"]] == [
        "ok", "ok", "error"
    ]
    assert failure["spans"][-1]["error"] == {"message": "Customer not found"}
    assert failure["spans"][-1]["metadata"]["execution_origin"] == "agent_tool"
    assert "example_repeat_observation" not in failure["spans"][0]["metadata"]
    assert all("total_tokens" not in span["metadata"] for span in failure["spans"])


def test_live_mode_requires_key_before_client_creation(monkeypatch: pytest.MonkeyPatch) -> None:
    examples_path = os.environ.get("SLEDTRACE_A1_UPSTREAM_EXAMPLES")
    if not examples_path:
        pytest.skip("Set SLEDTRACE_A1_UPSTREAM_EXAMPLES for optional upstream check")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is absent"):
        run("balance", Path(examples_path), live_openai=True, allow_paid_call=True)


def test_live_wrapper_records_framework_usage_without_verified_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    examples_path = os.environ.get("SLEDTRACE_A1_UPSTREAM_EXAMPLES")
    if not examples_path:
        pytest.skip("Set SLEDTRACE_A1_UPSTREAM_EXAMPLES for optional upstream check")
    pytest.importorskip("pydantic_ai")
    from pydantic_ai.models.test import TestModel
    from pydantic_ai.models import openai as model_module
    from pydantic_ai.providers import openai as provider_module
    import openai as openai_module

    def refuse_external_network(_sock: socket.socket, _address: object) -> None:
        raise AssertionError("Stubbed live mode attempted a network connection")

    monkeypatch.setattr(socket.socket, "connect", refuse_external_network)
    monkeypatch.setenv("OPENAI_API_KEY", "unused-live-test-placeholder")
    monkeypatch.setattr(openai_module, "AsyncOpenAI", lambda **_kwargs: object())
    monkeypatch.setattr(provider_module, "OpenAIProvider", lambda **_kwargs: object())
    monkeypatch.setattr(
        model_module,
        "OpenAIResponsesModel",
        lambda *_args, **_kwargs: TestModel(
            custom_output_args={
                "support_advice": "Hello John, your balance is $123.45.",
                "block_card": False,
                "risk": 1,
            }
        ),
    )

    payload = run(
        "balance", Path(examples_path), live_openai=True, allow_paid_call=True
    )
    assert payload["trace"]["status"] == "ok"
    assert payload["trace"]["metadata"]["structural_pass"] is True
    assert "accepted" not in payload["trace"]["output"]
    assert [span["name"] for span in payload["spans"]] == [
        "customer_name_lookup", "agent_model_request", "customer_balance",
        "customer_name_lookup", "agent_model_request",
    ]
    attempts = [span for span in payload["spans"] if span["type"] == "llm"]
    assert [span["output"]["response"] for span in attempts] == [
        "customer_balance_tool_request", "structured_output",
    ]
    assert all(span["metadata"]["usage_capture"] == "pydantic_ai_model_response" for span in attempts)
    assert all("usage_source" not in span["metadata"] for span in attempts)
    assert "unused-live-test-placeholder" not in json.dumps(payload)


def test_live_mode_stops_repeated_tool_requests_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    examples_path = os.environ.get("SLEDTRACE_A1_UPSTREAM_EXAMPLES")
    if not examples_path:
        pytest.skip("Set SLEDTRACE_A1_UPSTREAM_EXAMPLES for optional upstream check")
    pytest.importorskip("pydantic_ai")
    from pydantic_ai.messages import ModelResponse, ToolCallPart
    from pydantic_ai.models.test import TestModel
    from pydantic_ai.models import openai as model_module
    from pydantic_ai.providers import openai as provider_module
    import openai as openai_module

    class RepeatingToolModel(TestModel):
        async def request(self, messages: object, model_settings: object, model_request_parameters: object) -> ModelResponse:
            return ModelResponse(parts=[ToolCallPart(tool_name="customer_balance", args={})])

    monkeypatch.setattr(
        socket.socket, "connect",
        lambda *_args: (_ for _ in ()).throw(AssertionError("Network attempted")),
    )
    monkeypatch.setenv("OPENAI_API_KEY", "unused-limit-test-placeholder")
    monkeypatch.setattr(openai_module, "AsyncOpenAI", lambda **_kwargs: object())
    monkeypatch.setattr(provider_module, "OpenAIProvider", lambda **_kwargs: object())
    monkeypatch.setattr(
        model_module, "OpenAIResponsesModel", lambda *_args, **_kwargs: RepeatingToolModel()
    )

    payload = run("balance", Path(examples_path), live_openai=True, allow_paid_call=True)
    assert payload["trace"]["status"] == "error"
    assert payload["trace"]["metadata"]["structural_pass"] is False
    assert sum(span["type"] == "llm" for span in payload["spans"]) <= 2
    assert "accepted" in payload["trace"]["output"]
    assert payload["trace"]["output"]["accepted"] is False
