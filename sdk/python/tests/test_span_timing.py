from __future__ import annotations

import importlib

import pytest


trace_module = importlib.import_module("raglens.trace")


def test_measure_records_actual_timestamps_and_monotonic_duration(monkeypatch) -> None:
    timestamps = iter(
        ["2026-09-11T10:00:00.000Z", "2026-09-11T10:00:00.013Z"]
    )
    monotonic_values = iter([1_000.0, 1_012.9])
    monkeypatch.setattr(trace_module, "utc_now_iso", lambda: next(timestamps))
    monkeypatch.setattr(trace_module, "now_ms", lambda: next(monotonic_values))

    tr = trace_module.RAGLensTrace("measured")
    with tr.measure() as timing:
        pass

    tr.retrieval(query="q", chunks=[], timing=timing)
    span = tr._spans[0].to_dict()

    assert span["started_at"] == "2026-09-11T10:00:00.000Z"
    assert span["ended_at"] == "2026-09-11T10:00:00.013Z"
    assert span["duration_ms"] == 12


def test_unmeasured_post_hoc_records_are_not_reported_as_zero() -> None:
    tr = trace_module.RAGLensTrace("unmeasured")
    tr.retrieval(query="q", chunks=[])
    tr.llm(model="model", response="answer")

    for span in tr.to_dict()["spans"]:
        assert span["started_at"]
        assert span["ended_at"] is None
        assert span["duration_ms"] is None


def test_explicit_zero_is_preserved_for_both_span_types() -> None:
    tr = trace_module.RAGLensTrace("zero")
    tr.retrieval(query="q", chunks=[], duration_ms=0)
    tr.llm(model="model", response="answer", latency_ms=0)

    retrieval, llm = tr.to_dict()["spans"]
    assert retrieval["duration_ms"] == 0
    assert llm["duration_ms"] == 0
    assert llm["metadata"]["latency_ms"] == 0


def test_existing_positional_arguments_keep_their_meaning() -> None:
    tr = trace_module.RAGLensTrace("positional")
    tr.retrieval("q", [], "search", 2, {"retriever": "legacy"})
    tr.llm("model", "prompt", "answer", None, "generate", "local", 2, 3, 7, {"mode": "legacy"})

    retrieval, llm = tr.to_dict()["spans"]
    assert retrieval["name"] == "search"
    assert retrieval["metadata"]["retriever"] == "legacy"
    assert retrieval["duration_ms"] is None
    assert llm["name"] == "generate"
    assert llm["metadata"]["provider"] == "local"
    assert llm["metadata"]["total_tokens"] == 5
    assert llm["duration_ms"] == 7


@pytest.mark.parametrize("invalid", [-1, 1.5, float("inf"), True, "12"])
def test_retrieval_rejects_invalid_explicit_duration(invalid) -> None:
    tr = trace_module.RAGLensTrace("invalid")
    with pytest.raises((TypeError, ValueError)):
        tr.retrieval(query="q", chunks=[], duration_ms=invalid)


@pytest.mark.parametrize("invalid", [-1, 1.5, float("nan"), False, "12"])
def test_llm_rejects_invalid_explicit_latency(invalid) -> None:
    tr = trace_module.RAGLensTrace("invalid")
    with pytest.raises((TypeError, ValueError)):
        tr.llm(model="model", latency_ms=invalid)


def test_measurement_must_finish_and_cannot_conflict_with_explicit_latency() -> None:
    tr = trace_module.RAGLensTrace("unfinished")
    unfinished = tr.measure()

    with pytest.raises(RuntimeError, match="must finish"):
        tr.retrieval(query="q", chunks=[], timing=unfinished)

    with tr.measure() as timing:
        pass

    with pytest.raises(ValueError, match="either timing or latency_ms"):
        tr.llm(model="model", latency_ms=1, timing=timing)


def test_measurement_preserves_the_original_application_exception() -> None:
    tr = trace_module.RAGLensTrace("failure")

    with pytest.raises(LookupError, match="business failure"):
        with tr.measure():
            raise LookupError("business failure")

    assert tr.to_dict()["spans"] == []


def test_measurement_is_one_shot() -> None:
    tr = trace_module.RAGLensTrace("one-shot")
    timing = tr.measure()

    with timing:
        pass

    with pytest.raises(RuntimeError, match="cannot be reused"):
        with timing:
            pass
