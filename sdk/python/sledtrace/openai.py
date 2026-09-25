"""Explicit, offline-friendly recording of one OpenAI Responses result.

The caller executes the provider request. This helper reads only model and usage;
it never persists the response body, prompt, response ID, or credentials.
"""

from typing import Any, Optional

from ._openai_usage import TokenField, extract_response_usage


def _known(field: TokenField) -> Optional[int]:
    return field.value if field.kind == "known" else None


def record_response(
    trace: Any,
    response: Any,
    *,
    name: str = "openai-response",
    status: str = "ok",
    error: Optional[str] = None,
    duration_ms: Optional[int] = None,
) -> None:
    """Record provider-reported usage from one non-streaming Responses object.

    A completed provider call may be recorded with ``status='error'`` when a
    later application step rejects it. Missing/malformed usage remains unknown.
    The response's model name is used as-is; no model is guessed from prompts.
    """
    model = response.get("model") if isinstance(response, dict) else getattr(response, "model", None)
    if not isinstance(model, str) or not model.strip():
        raise ValueError("OpenAI response.model must be a non-empty string")

    usage = extract_response_usage(response)
    metadata = {"usage_source": "openai_responses"}
    for key, field in (
        ("cached_input_tokens", usage.cached_input_tokens),
        ("cache_write_tokens", usage.cache_write_tokens),
        ("reasoning_output_tokens", usage.reasoning_output_tokens),
    ):
        if field.kind == "known":
            metadata[key] = field.value
        elif field.kind == "invalid":
            metadata[key + "_state"] = "invalid"
    if usage.issues:
        metadata["usage_issues"] = list(usage.issues)
    for key, field in (
        ("input_tokens", usage.input_tokens),
        ("output_tokens", usage.output_tokens),
        ("total_tokens", usage.total_tokens),
    ):
        if field.kind == "invalid":
            metadata[key + "_state"] = "invalid"

    trace.llm(
        model=model,
        name=name,
        provider="openai",
        input_tokens=_known(usage.input_tokens),
        output_tokens=_known(usage.output_tokens),
        total_tokens=_known(usage.total_tokens),
        latency_ms=duration_ms,
        metadata=metadata,
        status=status,
        error=error,
    )
