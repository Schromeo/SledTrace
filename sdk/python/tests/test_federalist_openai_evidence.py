"""Offline guardrails for the opt-in public-corpus provider exercise."""

import sqlite3
import sys
from types import SimpleNamespace

import pytest

from examples import federalist_openai_evidence as example
from raglens.trace import RAGLensTrace, TraceFlushResult


def test_prompt_uses_answer_bearing_excerpt_and_bounded_cost():
    text = "preface " * 300 + "The latent causes of faction are sown in the nature of man."
    chunks = [{"text": text, "metadata": {"page": 28}}]
    prompt = example.build_prompt(example.DEFAULT_QUERY, chunks)
    assert "nature of man" in prompt
    assert "[page 28]" in prompt
    assert len(prompt) < 1600
    assert 0 < example.conservative_cost_bound_usd(prompt) < 0.01


def test_request_once_has_no_tools_storage_or_hidden_retry():
    calls = []
    client = SimpleNamespace(responses=SimpleNamespace(create=lambda **kw: calls.append(kw) or object()))
    example.request_once(client, "bounded prompt")
    assert calls == [{
        "model": "gpt-4o-mini",
        "input": "bounded prompt",
        "max_output_tokens": 256,
        "store": False,
    }]


def test_dry_run_needs_no_key_and_paid_preflight_stops_without_budget(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "public.pdf"
    pdf.write_bytes(b"test placeholder; an existing index skips PDF parsing")
    db_path = tmp_path / "federalist.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE VIRTUAL TABLE passages USING fts5(source, page UNINDEXED, text)")
        db.execute(
            "INSERT INTO passages(source, page, text) VALUES (?, ?, ?)",
            ("public.pdf", 28, "The latent causes of faction are sown in the nature of man."),
        )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    argv = ["example", "--pdf", str(pdf), "--db", str(db_path)]
    monkeypatch.setattr(sys, "argv", argv)
    assert example.main() == 0
    assert "Dry run only" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", argv + ["--paid-call"])
    with pytest.raises(SystemExit, match="2"):
        example.main()
    assert "requires --budget-usd" in capsys.readouterr().err


def test_paid_preflight_stops_without_key(tmp_path, monkeypatch):
    pdf = tmp_path / "public.pdf"
    pdf.write_bytes(b"test")
    db_path = tmp_path / "federalist.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE VIRTUAL TABLE passages USING fts5(source, page UNINDEXED, text)")
        db.execute(
            "INSERT INTO passages(source, page, text) VALUES (?, ?, ?)",
            ("public.pdf", 28, "The latent causes of faction are sown in the nature of man."),
        )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(sys, "argv", [
        "example", "--pdf", str(pdf), "--db", str(db_path),
        "--paid-call", "--budget-usd", "0.10",
    ])
    with pytest.raises(SystemExit, match="2"):
        example.main()


def test_paid_path_records_one_fake_response_without_raw_provider_object(tmp_path, monkeypatch):
    pdf = tmp_path / "public.pdf"
    pdf.write_bytes(b"test")
    db_path = tmp_path / "federalist.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE VIRTUAL TABLE passages USING fts5(source, page UNINDEXED, text)")
        db.execute(
            "INSERT INTO passages(source, page, text) VALUES (?, ?, ?)",
            ("public.pdf", 28, "The latent causes of faction are sown in the nature of man."),
        )
    calls = []
    traces = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                model="gpt-4o-mini", output_text="Human nature. [page 28]",
                usage={"input_tokens": 30, "output_tokens": 10, "total_tokens": 40},
                secret_marker="never-persist-provider-object",
            )

    class FakeOpenAI:
        def __init__(self, **kwargs):
            assert kwargs == {"max_retries": 0, "timeout": 30.0}
            self.responses = FakeResponses()

    def fake_flush(run):
        traces.append(run.to_dict())
        return TraceFlushResult(ok=True, response={"status": "ok"})

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    monkeypatch.setattr(RAGLensTrace, "try_flush", fake_flush)
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-value")
    monkeypatch.setattr(sys, "argv", [
        "example", "--pdf", str(pdf), "--db", str(db_path),
        "--paid-call", "--budget-usd", "0.10",
    ])
    assert example.main() == 0
    assert len(calls) == 1
    assert calls[0]["store"] is False
    assert len(traces) == 1
    spans = traces[0]["spans"]
    assert [span["type"] for span in spans] == ["retrieval", "llm"]
    assert spans[1]["metadata"]["total_tokens"] == 40
    assert "never-persist-provider-object" not in str(traces[0])
    assert "test-only-value" not in str(traces[0])
