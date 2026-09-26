from __future__ import annotations

import json

import pytest

from examples.agent_repeat_evidence import CASES, run


@pytest.mark.parametrize("case", CASES)
def test_e4_evidence_cases_preserve_observation_and_label_boundaries(case: str) -> None:
    payload = run(case)
    fixture = CASES[case]
    trace_record = payload["trace"]
    assert trace_record["metadata"]["sample_kind"] == "internal_scripted_e4_evidence"
    assert trace_record["metadata"]["quality_review"] == "not_assessed"
    assert trace_record["metadata"]["fixture_label"] == fixture["label"]
    assert trace_record["metadata"]["fixture_outcome"] == (
        "completed" if fixture["completed"] else "failed"
    )
    assert trace_record["output"].get("accepted") is (
        None if fixture["completed"] else False
    )
    assert trace_record["status"] == ("ok" if fixture["completed"] else "error")
    assert [span["type"] for span in payload["spans"]] == ["llm", "tool", "tool"]
    assert all(span["type"] != "retrieval" for span in payload["spans"])
    assert all("total_tokens" not in span["metadata"] for span in payload["spans"])
    for span, attempt in zip(payload["spans"][1:], fixture["attempts"]):
        assert span["name"] == attempt[0]
        assert span["status"] == attempt[3]
        assert span["metadata"]["fixture_comparison"] == {
            "argument_key": attempt[5],
            "result_key": attempt[6],
            "state_version": attempt[7],
        }


def test_same_result_is_not_enough_without_state_evidence() -> None:
    repeated = run("same_result_stable")["spans"][1:]
    unknown = run("confirmation_unknown_state")["spans"][1:]
    assert repeated[0]["metadata"]["fixture_comparison"] == repeated[1]["metadata"]["fixture_comparison"]
    assert unknown[0]["metadata"]["fixture_comparison"] == unknown[1]["metadata"]["fixture_comparison"]
    assert unknown[0]["metadata"]["fixture_comparison"]["state_version"] is None
    assert CASES["confirmation_unknown_state"]["label"] == "indeterminate"


def test_scripted_evidence_contains_no_provider_claim_or_private_fixture() -> None:
    encoded = json.dumps([run(case) for case in CASES])
    assert "openai_responses" not in encoded
    assert "provider_verified" not in encoded
    assert "OPENAI_API_KEY" not in encoded


def test_unknown_case_fails_before_recording() -> None:
    with pytest.raises(ValueError, match="Unknown evidence case"):
        run("not-a-case")
