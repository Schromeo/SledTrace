"""Offline Responses-to-span contract tests; no OpenAI dependency or call."""

import json
from pathlib import Path

import pytest

from sledtrace import trace
from sledtrace.openai import record_response


FIXTURE = Path(__file__).parent / "fixtures" / "openai_response_usage.json"


def test_response_usage_is_recorded_once_without_raw_content():
    response = json.loads(FIXTURE.read_text(encoding="utf-8"))
    response["model"] = "gpt-4.1-mini"
    response["usage"]["output_tokens_details"]["reasoning_tokens"] = 0
    response["output"] = [{"private": "never retain"}]
    with trace("offline-openai") as run:
        record_response(run, response, duration_ms=0)

    span = run.to_dict()["spans"][0]
    assert span["input"] == {"model": "gpt-4.1-mini"}
    assert span["output"] == {}
    assert span["metadata"] == {
        "provider": "openai",
        "usage_source": "openai_responses",
        "input_tokens": 120,
        "output_tokens": 80,
        "total_tokens": 200,
        "cached_input_tokens": 20,
        "cache_write_tokens": 0,
        "reasoning_output_tokens": 0,
        "latency_ms": 0,
    }
    assert "private" not in json.dumps(run.to_dict())


def test_missing_and_conflicting_usage_is_not_fabricated():
    with trace("missing") as run:
        record_response(run, {"model": "gpt-4.1-mini", "usage": None})
        record_response(run, {"model": "gpt-4.1-mini", "usage": {
            "input_tokens": 5, "output_tokens": 3, "total_tokens": 9,
        }}, status="error", error="rejected output")

    missing, conflicting = run.to_dict()["spans"]
    assert "total_tokens" not in missing["metadata"]
    assert conflicting["metadata"]["total_tokens"] == 9
    assert conflicting["metadata"]["usage_issues"] == ["total_mismatch"]
    assert conflicting["status"] == "error"


def test_zero_and_unknown_model_validation():
    with trace("zero") as run:
        record_response(run, {"model": "other-model", "usage": {
            "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
            "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0},
        }})
        with pytest.raises(ValueError, match="model"):
            record_response(run, {"usage": None})
    assert run.to_dict()["spans"][0]["metadata"]["total_tokens"] == 0
    assert len(run.to_dict()["spans"]) == 1
