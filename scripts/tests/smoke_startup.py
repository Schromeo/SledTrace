"""Opt-in real source-stack startup/ingestion/shutdown smoke (requires Go/Node/npm)."""
from __future__ import annotations

import importlib.util
import json
import os
import signal
import socket
import sys
import tempfile
import urllib.request
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("sledtrace_startup_smoke", ROOT / "scripts/start-sledtrace.py")
startup = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = startup
spec.loader.exec_module(startup)
sys.path.insert(0, str(ROOT / "sdk/python"))
from sledtrace import trace


def main() -> None:
    # Hold two ephemeral reservations until immediately before starting. The helper
    # still preflights them and fails rather than taking over an occupied port.
    with socket.socket() as collector, socket.socket() as dashboard:
        collector.bind(("127.0.0.1", 0))
        dashboard.bind(("127.0.0.1", 0))
        collector_port = collector.getsockname()[1]
        dashboard_port = dashboard.getsockname()[1]
    collector_url = f"http://127.0.0.1:{collector_port}"
    dashboard_url = f"http://127.0.0.1:{dashboard_port}"

    def inspect_then_interrupt(processes):
        with trace("startup-reliability-smoke", query="What is the return window?", collector_url=collector_url) as current:
            with current.measure() as timing:
                chunks = [{"chunk_id": "policy", "text": "Returns are accepted within 30 days of purchase.", "score": 0.9}]
            current.retrieval(query="What is the return window?", chunks=chunks, timing=timing)
            current.llm(model="deterministic-smoke", response="Returns are accepted within 45 days of purchase.")
        result = current.flush()
        assert result["status"] == "stored", result
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        request = urllib.request.Request(f"{collector_url}/api/traces/{current.trace_id}", headers={"Origin": dashboard_url})
        with opener.open(request, timeout=3) as response:
            assert response.headers["Access-Control-Allow-Origin"] == dashboard_url
            detail = json.load(response)
        assert len(detail["spans"]) == 2, detail
        assert detail["warnings"], detail
        print(f"Trace round trip passed: {current.trace_id}; 2 spans; {len(detail['warnings'])} warning(s).", flush=True)
        signal.raise_signal(signal.SIGINT)

    with tempfile.TemporaryDirectory(prefix="sledtrace-startup-smoke-") as directory:
        env = {"SLEDTRACE_COLLECTOR_ADDR": f"127.0.0.1:{collector_port}",
               "SLEDTRACE_DB_PATH": str(Path(directory) / "smoke.db"),
               "SLEDTRACE_ALLOWED_ORIGINS": "", "VITE_SLEDTRACE_API_URL": "",
               "VITE_RAGLENS_API_URL": ""}
        with patch.dict(os.environ, env), patch.object(startup, "supervise", inspect_then_interrupt):
            code = startup.main(["--dashboard-port", str(dashboard_port), "--startup-timeout", "90"])
        assert code == 130, f"expected interrupt exit 130, got {code}"
        for port in (collector_port, dashboard_port):
            try:
                connection = socket.create_connection(("127.0.0.1", port), timeout=0.3)
            except OSError:
                continue
            connection.close()
            raise AssertionError(f"Service still listens on port {port} after shutdown")
        print("PASS: real startup, health, Dashboard HTTP, SDK ingestion, CORS, SIGINT and both ports released.")


if __name__ == "__main__":
    main()
