from __future__ import annotations

import pytest

from sledtrace import trace


def test_recovered_tool_failure_keeps_step_error_and_task_success() -> None:
    with trace(
        "document-check",
        metadata={
            "task_id": "case-1",
            "run_id": "run-a",
            "variant": "baseline",
            "app_version": "demo-1",
        },
    ) as task:
        task.llm(model="fixture", response="Need source", input_tokens=3, output_tokens=2)
        failed_id = task.tool(
            "lookup",
            input_summary="document key",
            status="error",
            error="source temporarily unavailable",
            duration_ms=0,
        )
        task.tool("lookup", input_summary="document key", output_summary="one match")
        task.llm(model="fixture", response="Draft based on match", input_tokens=4)
        task.log_task_result("Accepted summary", accepted=True)

    payload = task.to_dict()
    assert payload["trace"]["status"] == "ok"
    assert payload["trace"]["output"] == {
        "answer": "Accepted summary",
        "task_result": "Accepted summary",
        "accepted": True,
    }
    assert [span["type"] for span in payload["spans"]] == [
        "llm", "tool", "tool", "llm"
    ]
    failed = payload["spans"][1]
    assert failed["span_id"] == failed_id
    assert failed["status"] == "error"
    assert failed["error"] == {"message": "source temporarily unavailable"}
    assert failed["duration_ms"] == 0
    assert payload["spans"][2]["duration_ms"] is None
    assert payload["spans"][0]["metadata"]["total_tokens"] == 5
    assert payload["spans"][3]["metadata"]["input_tokens"] == 4
    assert "total_tokens" not in payload["spans"][3]["metadata"]


def test_failed_llm_attempt_retains_usage_but_not_final_answer() -> None:
    with trace("business-failure") as task:
        task.llm(
            model="fixture",
            response="Unusable draft",
            input_tokens=7,
            output_tokens=3,
            status="error",
            error="invalid structured output",
        )
        task.log_task_result("Could not verify the document", accepted=False)

    payload = task.to_dict()
    assert payload["trace"]["status"] == "error"
    assert payload["trace"]["output"]["answer"] == "Could not verify the document"
    assert payload["trace"]["output"]["accepted"] is False
    assert payload["spans"][0]["status"] == "error"
    assert payload["spans"][0]["metadata"]["total_tokens"] == 10


def test_old_rag_calls_and_separate_traces_remain_compatible() -> None:
    with trace("old-rag", query="q") as old:
        old.retrieval("q", [{"text": "context"}])
        old.llm("fixture", "prompt", "legacy answer")

    with trace("new-task") as new:
        new.tool("lookup", output_summary="one match")
        new.log_task_result("done", accepted=True)

    assert old.to_dict()["trace"]["output"] == {"answer": "legacy answer"}
    assert old.to_dict()["trace"]["status"] == "ok"
    assert len(old.to_dict()["spans"]) == 2
    assert len(new.to_dict()["spans"]) == 1
    assert old.trace_id != new.trace_id
    assert new.to_dict()["spans"][0]["trace_id"] == new.trace_id


def test_invalid_step_and_result_contracts_fail_without_appending() -> None:
    with trace("validation") as task:
        with pytest.raises(ValueError, match="error step"):
            task.tool("lookup", status="error")
        with pytest.raises(ValueError, match="cannot have"):
            task.llm("fixture", status="ok", error="not valid")
        with pytest.raises(ValueError, match="non-empty string"):
            task.tool("")
        with pytest.raises(TypeError, match="string summary"):
            task.tool("lookup", input_summary={"raw": "private"})
        with pytest.raises(TypeError, match="boolean"):
            task.log_task_result("done", accepted="yes")
    assert task.to_dict()["spans"] == []


def test_tool_timing_uses_completed_measurement() -> None:
    with trace("timed-tool") as task:
        with task.measure() as timing:
            output = "one match"
        task.tool("lookup", output_summary=output, timing=timing)
    span = task.to_dict()["spans"][0]
    assert span["started_at"] and span["ended_at"]
    assert isinstance(span["duration_ms"], int)


def test_explicit_result_is_not_replaced_by_later_llm_attempt() -> None:
    with trace("result-precedence") as task:
        task.log_task_result("accepted", accepted=True)
        task.llm("fixture", response="late intermediate response")
    assert task.to_dict()["trace"]["output"]["answer"] == "accepted"
