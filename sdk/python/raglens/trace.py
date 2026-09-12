from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import os
import sys
import traceback
import urllib.request
import urllib.error

from .models import (
    JsonDict,
    Span,
    TraceRecord,
    TracePayload,
    new_id,
    now_ms,
    utc_now_iso,
)


@dataclass(frozen=True)
class TraceFlushResult:
    """Observable result from the explicit best-effort ``try_flush`` path."""

    ok: bool
    response: Optional[JsonDict] = None
    error: Optional[Exception] = None


class SpanTiming:
    """Measure an operation before recording its span."""

    def __init__(self) -> None:
        self.started_at: Optional[str] = None
        self.ended_at: Optional[str] = None
        self.duration_ms: Optional[int] = None
        self._start_ms: Optional[float] = None

    def __enter__(self) -> "SpanTiming":
        if self._start_ms is not None or self.duration_ms is not None:
            raise RuntimeError("A SledTrace timing measurement cannot be reused.")

        self.started_at = utc_now_iso()
        self._start_ms = now_ms()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        if self._start_ms is None:
            raise RuntimeError("SledTrace timing measurement was not started.")

        self.ended_at = utc_now_iso()
        elapsed_ms = now_ms() - self._start_ms
        if elapsed_ms < 0:
            raise RuntimeError("SledTrace monotonic clock moved backwards.")

        # The wire format stores integer milliseconds. Preserve measured zero
        # rather than treating a sub-millisecond operation as unknown.
        self.duration_ms = int(elapsed_ms)
        return False

    def span_fields(self) -> tuple[str, str, int]:
        if (
            self.started_at is None
            or self.ended_at is None
            or self.duration_ms is None
        ):
            raise RuntimeError(
                "SledTrace timing measurement must finish before recording a span."
            )

        return self.started_at, self.ended_at, _validate_duration_ms(
            self.duration_ms,
            "timing.duration_ms",
        )


class RAGLensTrace:
    """
    A lightweight trace context manager for recording one RAG request.

    Public API example:

        from sledtrace import trace

        with trace("refund-policy-qa") as t:
            t.retrieval(query="...", chunks=[...])
            t.llm(model="...", prompt="...", response="...")
    """

    def __init__(
        self,
        name: str,
        query: Optional[str] = None,
        metadata: Optional[JsonDict] = None,
        collector_url: Optional[str] = None,
    ) -> None:
        self.trace_id = new_id("trace")
        self.name = name
        self.query = query
        self.metadata = metadata or {}
        self.collector_url = resolve_collector_url(collector_url)

        self._started_at: Optional[str] = None
        self._ended_at: Optional[str] = None
        self._start_ms: Optional[float] = None
        self._duration_ms: Optional[int] = None

        self._status = "ok"
        self._output: JsonDict = {}
        self._spans: List[Span] = []
        self._error: Optional[JsonDict] = None

    def __enter__(self) -> "RAGLensTrace":
        self._started_at = utc_now_iso()
        self._start_ms = now_ms()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        self._ended_at = utc_now_iso()

        if self._start_ms is not None:
            self._duration_ms = int(now_ms() - self._start_ms)

        if exc is not None:
            self._status = "error"
            self._error = {
                "type": exc_type.__name__ if exc_type else "Error",
                "message": str(exc),
                "stack": "".join(traceback.format_exception(exc_type, exc, tb)),
            }

        # Do not suppress exceptions.
        return False

    def measure(self) -> SpanTiming:
        """Return a one-shot context manager for measuring an actual operation."""
        return SpanTiming()

    def retrieval(
        self,
        query: str,
        chunks: List[JsonDict],
        name: str = "retrieval",
        top_k: Optional[int] = None,
        metadata: Optional[JsonDict] = None,
        duration_ms: Optional[int] = None,
        timing: Optional[SpanTiming] = None,
    ) -> None:
        """
        Record a retrieval span.

        Args:
            query: Query sent to retriever.
            chunks: Retrieved chunks.
            name: Human-readable span name.
            top_k: Number of requested chunks.
            metadata: Retriever metadata.
            duration_ms: Explicit retriever latency in integer milliseconds.
            timing: Completed measurement returned by ``t.measure()``.
        """
        started_at, ended_at, resolved_duration_ms = _resolve_span_timing(
            timing=timing,
            explicit_duration_ms=duration_ms,
            explicit_name="duration_ms",
        )

        normalized_chunks = self._normalize_chunks(chunks)

        span_input: JsonDict = {
            "query": query,
        }

        if top_k is not None:
            span_input["top_k"] = top_k

        span = Span(
            span_id=new_id("span"),
            trace_id=self.trace_id,
            parent_span_id=None,
            type="retrieval",
            name=name,
            status="ok",
            input=span_input,
            output={
                "chunks": normalized_chunks,
            },
            metadata=metadata or {},
            started_at=started_at,
            ended_at=ended_at,
            duration_ms=resolved_duration_ms,
            error=None,
        )

        self._spans.append(span)

        if self.query is None:
            self.query = query

    def llm(
        self,
        model: str,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        messages: Optional[List[JsonDict]] = None,
        name: str = "llm",
        provider: Optional[str] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[JsonDict] = None,
        timing: Optional[SpanTiming] = None,
    ) -> None:
        """
        Record an LLM span.

        Args:
            model: Model name.
            prompt: Prompt text.
            response: Model response text.
            messages: Optional chat messages.
            name: Human-readable span name.
            provider: LLM provider.
            input_tokens: Input token count.
            output_tokens: Output token count.
            latency_ms: LLM call latency.
            metadata: Additional metadata.
            timing: Completed measurement returned by ``t.measure()``.
        """
        started_at, ended_at, resolved_duration_ms = _resolve_span_timing(
            timing=timing,
            explicit_duration_ms=latency_ms,
            explicit_name="latency_ms",
        )

        span_input: JsonDict = {
            "model": model,
        }

        if prompt is not None:
            span_input["prompt"] = prompt

        if messages is not None:
            span_input["messages"] = messages

        span_output: JsonDict = {}

        if response is not None:
            span_output["response"] = response
            self._output["answer"] = response

        span_metadata: JsonDict = metadata.copy() if metadata else {}

        if provider is not None:
            span_metadata["provider"] = provider

        if input_tokens is not None:
            span_metadata["input_tokens"] = input_tokens

        if output_tokens is not None:
            span_metadata["output_tokens"] = output_tokens

        if input_tokens is not None and output_tokens is not None:
            span_metadata["total_tokens"] = input_tokens + output_tokens

        if latency_ms is not None:
            span_metadata["latency_ms"] = resolved_duration_ms

        span = Span(
            span_id=new_id("span"),
            trace_id=self.trace_id,
            parent_span_id=None,
            type="llm",
            name=name,
            status="ok",
            input=span_input,
            output=span_output,
            metadata=span_metadata,
            started_at=started_at,
            ended_at=ended_at,
            duration_ms=resolved_duration_ms,
            error=None,
        )

        self._spans.append(span)

    def log_answer(self, answer: str) -> None:
        """Record the final answer at trace level."""
        self._output["answer"] = answer

    def to_payload(self) -> TracePayload:
        trace_input: JsonDict = {}

        if self.query is not None:
            trace_input["query"] = self.query

        trace_metadata = {
            "sdk_language": "python",
            "sdk_version": "0.7.0",
            **self.metadata,
        }

        if self._error is not None:
            trace_metadata["error"] = self._error

        record = TraceRecord(
            trace_id=self.trace_id,
            name=self.name,
            status=self._status,
            input=trace_input,
            output=self._output,
            metadata=trace_metadata,
            started_at=self._started_at or utc_now_iso(),
            ended_at=self._ended_at,
            duration_ms=self._duration_ms,
        )

        return TracePayload(trace=record, spans=self._spans)

    def to_dict(self) -> JsonDict:
        return self.to_payload().to_dict()

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def print_json(self) -> None:
        print(self.to_json())

    def flush(self, collector_url: Optional[str] = None, timeout: float = 5.0) -> JsonDict:
        """
        Send the trace payload to the local SledTrace collector.

        Args:
            collector_url: Optional collector base URL. Defaults to self.collector_url.
            timeout: HTTP timeout in seconds.

        Returns:
            Collector JSON response.

        Raises:
            Exception: Preserves the historical strict behavior. Serialization,
                request construction, timeout, HTTP, connection, or response
                decoding failures are raised to the caller.
        """
        base_url = (collector_url or self.collector_url).rstrip("/")
        url = f"{base_url}/api/traces"

        data = json.dumps(self.to_dict()).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "sledtrace-python-sdk/0.7.0",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
                if not response_body:
                    return {}

                return json.loads(response_body)

        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"SledTrace collector returned HTTP {exc.code}: {body}"
            ) from exc

        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Failed to connect to SledTrace collector at {url}: {exc.reason}"
            ) from exc

    def try_flush(
        self,
        collector_url: Optional[str] = None,
        timeout: float = 5.0,
    ) -> TraceFlushResult:
        """
        Attempt to send the trace without raising ordinary delivery errors.

        This is an explicit business-safe alternative to strict ``flush()``.
        Failures remain observable through ``result.error``. No retry, queue,
        background delivery, or automatic logging is performed.

        ``BaseException`` subclasses such as KeyboardInterrupt and SystemExit
        are deliberately not caught.
        """
        try:
            response = self.flush(collector_url=collector_url, timeout=timeout)
        except Exception as exc:
            return TraceFlushResult(ok=False, error=exc)

        return TraceFlushResult(ok=True, response=response)

    def _normalize_chunks(self, chunks: List[JsonDict]) -> List[JsonDict]:
        normalized: List[JsonDict] = []

        for index, chunk in enumerate(chunks):
            normalized_chunk = dict(chunk)

            if "rank" not in normalized_chunk:
                normalized_chunk["rank"] = index + 1

            if "metadata" not in normalized_chunk or normalized_chunk["metadata"] is None:
                normalized_chunk["metadata"] = {}

            normalized.append(normalized_chunk)

        return normalized


def _resolve_span_timing(
    timing: Optional[SpanTiming],
    explicit_duration_ms: Optional[int],
    explicit_name: str,
) -> tuple[str, Optional[str], Optional[int]]:
    if timing is not None:
        if not isinstance(timing, SpanTiming):
            raise TypeError("timing must be a completed value returned by t.measure().")
        if explicit_duration_ms is not None:
            raise ValueError(
                f"Pass either timing or {explicit_name}, not both."
            )

        started_at, ended_at, duration_ms = timing.span_fields()
        return started_at, ended_at, duration_ms

    recorded_at = utc_now_iso()
    if explicit_duration_ms is None:
        return recorded_at, None, None

    return (
        recorded_at,
        None,
        _validate_duration_ms(explicit_duration_ms, explicit_name),
    )


def _validate_duration_ms(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer number of milliseconds.")
    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to zero.")
    return value


def trace(
    name: str,
    query: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    collector_url: Optional[str] = None,
) -> RAGLensTrace:
    """
    Create a SledTrace trace context manager.
    """
    return RAGLensTrace(name=name, query=query, metadata=metadata, collector_url=collector_url,)


SledTraceTrace = RAGLensTrace

_DEFAULT_COLLECTOR_URL = "http://localhost:4319"
_LEGACY_COLLECTOR_ENV = "RAGLENS_COLLECTOR_URL"
_NEW_COLLECTOR_ENV = "SLEDTRACE_COLLECTOR_URL"
_legacy_env_notice_emitted = False


def resolve_collector_url(explicit_url: Optional[str]) -> str:
    if explicit_url:
        return explicit_url

    new_value = os.getenv(_NEW_COLLECTOR_ENV)
    if new_value:
        return new_value

    legacy_value = os.getenv(_LEGACY_COLLECTOR_ENV)
    if legacy_value:
        emit_legacy_env_warning_once()
        return legacy_value

    return _DEFAULT_COLLECTOR_URL


def emit_legacy_env_warning_once() -> None:
    global _legacy_env_notice_emitted
    if _legacy_env_notice_emitted:
        return

    _legacy_env_notice_emitted = True
    print(
        "DEPRECATED: RAGLENS_COLLECTOR_URL is deprecated; use SLEDTRACE_COLLECTOR_URL instead.",
        file=sys.stderr,
    )
