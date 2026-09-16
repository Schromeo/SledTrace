from __future__ import annotations

import importlib
import io
import json
import urllib.error

import pytest

from sledtrace import TraceFlushResult, trace


trace_module = importlib.import_module("raglens.trace")


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        return False

    def read(self) -> bytes:
        return self.body


def test_try_flush_returns_success_response(monkeypatch) -> None:
    monkeypatch.setattr(
        trace_module.urllib.request,
        "urlopen",
        lambda request, timeout: FakeResponse({"status": "stored"}),
    )

    result = trace("success").try_flush(timeout=0.25)

    assert result == TraceFlushResult(ok=True, response={"status": "stored"})
    assert result.error is None


def test_try_flush_keeps_offline_failure_observable(monkeypatch) -> None:
    def offline(request, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(trace_module.urllib.request, "urlopen", offline)

    result = trace("offline").try_flush()

    assert result.ok is False
    assert result.response is None
    assert isinstance(result.error, RuntimeError)
    assert "connection refused" in str(result.error)


def test_try_flush_keeps_http_failure_observable(monkeypatch) -> None:
    def unavailable(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url,
            503,
            "service unavailable",
            hdrs=None,
            fp=io.BytesIO(b"collector unavailable"),
        )

    monkeypatch.setattr(trace_module.urllib.request, "urlopen", unavailable)

    result = trace("http-error").try_flush()

    assert result.ok is False
    assert result.response is None
    assert isinstance(result.error, RuntimeError)
    assert "HTTP 503: collector unavailable" in str(result.error)


def test_try_flush_keeps_timeout_observable(monkeypatch) -> None:
    def timeout(request, timeout):
        raise TimeoutError("timed out")

    monkeypatch.setattr(trace_module.urllib.request, "urlopen", timeout)

    result = trace("timeout").try_flush(timeout=0.01)

    assert result.ok is False
    assert result.response is None
    assert isinstance(result.error, TimeoutError)
    assert str(result.error) == "timed out"


def test_try_flush_reports_serialization_failure_without_network(monkeypatch) -> None:
    def unexpected_request(request, timeout):
        raise AssertionError("network should not be called")

    monkeypatch.setattr(trace_module.urllib.request, "urlopen", unexpected_request)
    current = trace("serialization", metadata={"bad": object()})

    result = current.try_flush()

    assert result.ok is False
    assert result.response is None
    assert isinstance(result.error, TypeError)
    assert "not JSON serializable" in str(result.error)


def test_strict_flush_behavior_is_unchanged(monkeypatch) -> None:
    def offline(request, timeout):
        raise urllib.error.URLError("strict failure")

    monkeypatch.setattr(trace_module.urllib.request, "urlopen", offline)

    with pytest.raises(RuntimeError, match="strict failure"):
        trace("strict").flush()


def test_strict_flush_still_raises_timeout(monkeypatch) -> None:
    def timeout(request, timeout):
        raise TimeoutError("strict timeout")

    monkeypatch.setattr(trace_module.urllib.request, "urlopen", timeout)

    with pytest.raises(TimeoutError, match="strict timeout"):
        trace("strict-timeout").flush()


def test_strict_flush_still_raises_serialization_error() -> None:
    current = trace("strict-serialization", metadata={"bad": object()})

    with pytest.raises(TypeError, match="not JSON serializable"):
        current.flush()


def test_try_flush_does_not_replace_original_application_exception(
    monkeypatch,
) -> None:
    def offline(request, timeout):
        raise urllib.error.URLError("collector offline")

    monkeypatch.setattr(trace_module.urllib.request, "urlopen", offline)
    current = trace("business-exception")
    delivery_result = None

    with pytest.raises(LookupError, match="business failure"):
        try:
            with current:
                raise LookupError("business failure")
        finally:
            delivery_result = current.try_flush()

    assert delivery_result is not None
    assert delivery_result.ok is False
    assert isinstance(delivery_result.error, RuntimeError)


def test_try_flush_does_not_catch_base_exception(monkeypatch) -> None:
    current = trace("interrupt")

    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt("stop")

    monkeypatch.setattr(current, "flush", interrupt)

    with pytest.raises(KeyboardInterrupt, match="stop"):
        current.try_flush()
