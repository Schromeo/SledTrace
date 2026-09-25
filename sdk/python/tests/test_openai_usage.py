"""Sanitized offline OpenAI Responses usage-shape tests."""

import json
from pathlib import Path
from types import SimpleNamespace

from sledtrace._openai_usage import extract_response_usage


FIXTURE = Path(__file__).parent / "fixtures" / "openai_response_usage.json"


def _object(value):
    if isinstance(value, dict):
        return SimpleNamespace(**{key: _object(item) for key, item in value.items()})
    return value


def test_sdk_attribute_shape_preserves_provider_totals_and_nested_counts():
    response = _object(json.loads(FIXTURE.read_text(encoding="utf-8")))
    usage = extract_response_usage(response)

    assert usage.input_tokens.value == 120
    assert usage.output_tokens.value == 80
    assert usage.total_tokens.value == 200
    assert usage.cached_input_tokens.value == 20
    assert usage.cache_write_tokens.value == 0
    assert usage.reasoning_output_tokens.value == 30
    assert usage.trustworthy_total == 200  # Not 250: nested counts are included.
    assert usage.issues == ()


def test_zero_is_known_not_missing_and_mapping_fixture_is_supported():
    usage = extract_response_usage(
        {
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 0},
            }
        }
    )
    assert usage.trustworthy_total == 0
    assert usage.cached_input_tokens.kind == "known"
    assert usage.cache_write_tokens.kind == "missing"
    assert usage.reasoning_output_tokens.kind == "known"


def test_missing_usage_never_becomes_zero():
    usage = extract_response_usage(SimpleNamespace(usage=None))
    assert usage.input_tokens.kind == "missing"
    assert usage.total_tokens.kind == "missing"
    assert usage.trustworthy_total is None


def test_malformed_counts_are_invalid_not_coerced():
    usage = extract_response_usage(
        {"usage": {"input_tokens": True, "output_tokens": -1, "total_tokens": "3"}}
    )
    assert usage.input_tokens.kind == "invalid"
    assert usage.output_tokens.kind == "invalid"
    assert usage.total_tokens.kind == "invalid"
    assert usage.trustworthy_total is None

    partial = extract_response_usage(
        {"usage": {"input_tokens": "bad", "output_tokens": 2, "total_tokens": 5}}
    )
    assert partial.total_tokens.value == 5
    assert partial.trustworthy_total is None


def test_conflicts_exclude_provider_total_instead_of_double_counting():
    usage = extract_response_usage(
        {
            "usage": {
                "input_tokens": 5,
                "output_tokens": 3,
                "total_tokens": 9,
                "input_tokens_details": {"cached_tokens": 6},
                "output_tokens_details": {"reasoning_tokens": 4},
            }
        }
    )
    assert usage.issues == (
        "total_mismatch",
        "cached_exceeds_input",
        "reasoning_exceeds_output",
    )
    assert usage.trustworthy_total is None


def test_invalid_usage_object_is_explicit():
    usage = extract_response_usage({"usage": "not an object"})
    assert usage.issues == ("invalid_usage_object",)
    assert usage.input_tokens.kind == "missing"
