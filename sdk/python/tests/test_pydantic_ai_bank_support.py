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
    assert "a1-preexisting-key-must-not-be-used" not in json.dumps(success)

    failure = run("missing-customer", upstream_examples)
    assert failure["trace"]["status"] == "error"
    assert failure["trace"]["output"]["accepted"] is False
    assert [span["status"] for span in failure["spans"]] == [
        "ok", "ok", "error"
    ]
    assert failure["spans"][-1]["error"] == {"message": "Customer not found"}
    assert failure["spans"][-1]["metadata"]["execution_origin"] == "agent_tool"
    assert all("total_tokens" not in span["metadata"] for span in failure["spans"])
