"""Offline extraction of one OpenAI Responses usage object.

This module does not call OpenAI or change SledTrace's persisted span contract.
The official Python SDK exposes usage fields as attributes; mappings are also
accepted so sanitized JSON fixtures can exercise the same field names.
"""

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Optional, Tuple


_MISSING = object()


@dataclass(frozen=True)
class TokenField:
    kind: Literal["known", "missing", "invalid"]
    value: Optional[int] = None


@dataclass(frozen=True)
class OpenAIResponseUsage:
    input_tokens: TokenField
    output_tokens: TokenField
    total_tokens: TokenField
    cached_input_tokens: TokenField
    cache_write_tokens: TokenField
    reasoning_output_tokens: TokenField
    issues: Tuple[str, ...]

    @property
    def trustworthy_total(self) -> Optional[int]:
        """Return a provider total only when all available fields agree."""
        if self.issues or self.total_tokens.kind != "known":
            return None
        if any(
            field.kind == "invalid"
            for field in (
                self.input_tokens,
                self.output_tokens,
                self.cached_input_tokens,
                self.cache_write_tokens,
                self.reasoning_output_tokens,
            )
        ):
            return None
        return self.total_tokens.value


def extract_response_usage(response: Any) -> OpenAIResponseUsage:
    """Read non-streaming ``Response.usage`` without deriving missing counts.

    Cached tokens are part of input tokens, and reasoning tokens are part of
    output tokens. Neither subfield is added to the parent count.
    """
    usage = _get(response, "usage")
    input_tokens = _token(usage, "input_tokens")
    output_tokens = _token(usage, "output_tokens")
    total_tokens = _token(usage, "total_tokens")
    input_details = _get(usage, "input_tokens_details")
    cached_input_tokens = _token(input_details, "cached_tokens")
    cache_write_tokens = _token(input_details, "cache_write_tokens")
    reasoning_output_tokens = _token(
        _get(usage, "output_tokens_details"), "reasoning_tokens"
    )

    issues = []
    if usage is not _MISSING and usage is not None and not _is_record(usage):
        issues.append("invalid_usage_object")
    if (
        input_tokens.kind == "known"
        and output_tokens.kind == "known"
        and total_tokens.kind == "known"
        and total_tokens.value != input_tokens.value + output_tokens.value
    ):
        issues.append("total_mismatch")
    if (
        input_tokens.kind == "known"
        and cached_input_tokens.kind == "known"
        and cached_input_tokens.value > input_tokens.value
    ):
        issues.append("cached_exceeds_input")
    if (
        output_tokens.kind == "known"
        and reasoning_output_tokens.kind == "known"
        and reasoning_output_tokens.value > output_tokens.value
    ):
        issues.append("reasoning_exceeds_output")

    return OpenAIResponseUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cached_input_tokens=cached_input_tokens,
        cache_write_tokens=cache_write_tokens,
        reasoning_output_tokens=reasoning_output_tokens,
        issues=tuple(issues),
    )


def _get(record: Any, field: str) -> Any:
    if isinstance(record, Mapping):
        return record.get(field, _MISSING)
    if record is _MISSING or record is None:
        return _MISSING
    return getattr(record, field, _MISSING)


def _is_record(value: Any) -> bool:
    return isinstance(value, Mapping) or hasattr(value, "input_tokens")


def _token(record: Any, field: str) -> TokenField:
    value = _get(record, field)
    if value is _MISSING or value is None:
        return TokenField("missing")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return TokenField("invalid")
    return TokenField("known", value)
