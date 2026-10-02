from __future__ import annotations

import http.server
import json
import os
import socket
import sys
import textwrap
import threading
from pathlib import Path

import pytest

import sledtrace.cli as cli


def make_bundle(root: Path, collector_source: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    name = "sledtrace-collector.exe" if os.name == "nt" else "sledtrace-collector"
    binary = root / name
    binary.write_text(f"#!{sys.executable}\n{collector_source}", encoding="utf-8")
    binary.chmod(0o644)  # serve must make it executable itself
    (root / "dashboard").mkdir()
    (root / "dashboard" / "index.html").write_text("<title>SledTrace</title>", encoding="utf-8")
    return binary


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


FAKE_COLLECTOR = textwrap.dedent(
    """
    import http.server, json, os, threading, time
    host, port = os.environ["SLEDTRACE_COLLECTOR_ADDR"].rsplit(":", 1)
    with open(os.environ["FAKE_ENV_OUT"], "w") as handle:
        json.dump({k: os.environ[k] for k in os.environ if k.startswith("SLEDTRACE_")}, handle)

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = json.dumps({"status": "ok", "service": "sledtrace-collector"}).encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args):
            pass

    server = http.server.HTTPServer((host, int(port)), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(1.5)
    """
)


def test_find_bundle_requires_binary_and_dashboard(tmp_path: Path) -> None:
    assert cli.find_bundle(tmp_path) is None

    binary = make_bundle(tmp_path / "bundle", "")
    assert cli.find_bundle(tmp_path / "bundle") == (binary, tmp_path / "bundle" / "dashboard")

    (tmp_path / "bundle" / "dashboard" / "index.html").unlink()
    assert cli.find_bundle(tmp_path / "bundle") is None


def test_serve_prefers_bundle_unless_source_requested(tmp_path: Path, monkeypatch) -> None:
    bundle = (tmp_path / "collector", tmp_path / "dashboard")
    calls: list[str] = []
    monkeypatch.setattr(cli, "find_bundle", lambda: bundle)
    monkeypatch.setattr(cli, "serve_bundled", lambda *args, **kwargs: calls.append("bundled") or 0)
    monkeypatch.setattr(cli, "find_repo_root", lambda: tmp_path)
    monkeypatch.setattr(cli, "serve_from_checkout", lambda root: calls.append("source") or 0)

    assert cli.serve() == 0
    assert cli.serve(source=True) == 0
    assert calls == ["bundled", "source"]


def test_default_db_path_honours_environment(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SLEDTRACE_DB_PATH", str(tmp_path / "custom.db"))
    assert cli.default_db_path() == tmp_path / "custom.db"

    monkeypatch.delenv("SLEDTRACE_DB_PATH")
    assert cli.default_db_path() == Path.home() / ".sledtrace" / "sledtrace.db"


@pytest.mark.skipif(os.name == "nt", reason="fake collector relies on a shebang")
def test_serve_bundled_runs_collector_with_dashboard_and_db(tmp_path: Path, monkeypatch, capsys) -> None:
    env_out = tmp_path / "env.json"
    monkeypatch.setenv("FAKE_ENV_OUT", str(env_out))
    binary = make_bundle(tmp_path / "bundle", FAKE_COLLECTOR)
    port = free_port()
    db = tmp_path / "data" / "traces.db"

    code = cli.serve_bundled(binary, tmp_path / "bundle" / "dashboard", port=port, db_path=db, open_browser=False)

    assert code == 0
    assert db.parent.is_dir()
    seen = json.loads(env_out.read_text())
    assert seen["SLEDTRACE_COLLECTOR_ADDR"] == f"127.0.0.1:{port}"
    assert seen["SLEDTRACE_DB_PATH"] == str(db)
    assert seen["SLEDTRACE_DASHBOARD_DIR"] == str(tmp_path / "bundle" / "dashboard")
    out = capsys.readouterr().out
    assert f"SledTrace is running at http://127.0.0.1:{port}" in out
    assert "SLEDTRACE_COLLECTOR_URL" in out  # non-default port needs a hint


@pytest.mark.skipif(os.name == "nt", reason="fake collector relies on a shebang")
def test_serve_bundled_reports_early_collector_exit(tmp_path: Path, capsys) -> None:
    binary = make_bundle(tmp_path / "bundle", "import sys\nsys.exit(3)\n")

    code = cli.serve_bundled(
        binary, tmp_path / "bundle" / "dashboard", port=free_port(), db_path=tmp_path / "t.db", open_browser=False
    )

    assert code == 3
    assert "exited with code 3" in capsys.readouterr().err


class _HealthHandler(http.server.BaseHTTPRequestHandler):
    service = "sledtrace-collector"

    def do_GET(self):  # noqa: N802
        body = json.dumps({"status": "ok", "service": self.service}).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def _start_server(handler) -> http.server.HTTPServer:
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def test_serve_bundled_reuses_running_sledtrace(tmp_path: Path, capsys) -> None:
    server = _start_server(_HealthHandler)
    try:
        port = server.server_address[1]
        code = cli.serve_bundled(
            tmp_path / "missing-binary", tmp_path, port=port, db_path=tmp_path / "t.db", open_browser=False
        )
    finally:
        server.shutdown()

    assert code == 0
    assert "already running" in capsys.readouterr().out


def test_serve_bundled_refuses_port_used_by_another_program(tmp_path: Path, capsys) -> None:
    class Other(_HealthHandler):
        service = "something-else"

    server = _start_server(Other)
    try:
        port = server.server_address[1]
        code = cli.serve_bundled(
            tmp_path / "missing-binary", tmp_path, port=port, db_path=tmp_path / "t.db", open_browser=False
        )
    finally:
        server.shutdown()

    assert code == 1
    assert "already in use" in capsys.readouterr().err
