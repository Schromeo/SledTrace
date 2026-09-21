#!/usr/bin/env python3
"""Validate the copied independent app against only the built SledTrace wheel."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
EXAMPLE = ROOT / "examples" / "independent_app.py"
EXPECTED_VERSION = "0.7.1"


def run(
    command: list[str], cwd: Path, env: Optional[dict[str, str]] = None
) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(command)}")
    result = subprocess.run(command, cwd=str(cwd), env=env, text=True, capture_output=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class CaptureHandler(BaseHTTPRequestHandler):
    payloads: list[dict] = []

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        if self.path != "/api/traces":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length))
        type(self).payloads.append(payload)
        body = json.dumps(
            {
                "trace_id": payload["trace"]["trace_id"],
                "status": "stored",
                "warnings_generated": 0,
            }
        ).encode("utf-8")
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def validate_payloads(payloads: list[dict]) -> None:
    require(len(payloads) == 2, f"expected 2 stored payloads, got {len(payloads)}")

    success, application_error = payloads
    success_trace = success["trace"]
    require(success_trace["name"] == "independent-app-success", "wrong success name")
    require(success_trace["status"] == "ok", "success trace was not ok")
    require(success_trace["ended_at"] is not None, "success trace did not finish")
    require(
        [span["type"] for span in success["spans"]] == ["retrieval", "llm"],
        "success trace did not contain retrieval then llm spans",
    )

    error_trace = application_error["trace"]
    require(
        error_trace["name"] == "independent-app-application-error",
        "wrong application-error name",
    )
    require(error_trace["status"] == "error", "application error was not recorded")
    require(
        error_trace["metadata"]["error"]["type"] == "ExampleBusinessError",
        "application error type was not preserved",
    )
    require(
        error_trace["metadata"]["error"]["message"]
        == "inventory service rejected the request",
        "application error message was not preserved",
    )
    require(
        [span["type"] for span in application_error["spans"]] == ["retrieval"],
        "error trace should contain work completed before the failure",
    )


def validate() -> int:
    wheels = sorted(DIST_DIR.glob(f"sledtrace-{EXPECTED_VERSION}-*.whl"))
    if not wheels:
        print(
            f"No SledTrace {EXPECTED_VERSION} wheel found in {DIST_DIR}. "
            "Run 'python -m build' first.",
            file=sys.stderr,
        )
        return 1

    wheel = wheels[-1].resolve()
    print(f"Using wheel: {wheel}")

    with tempfile.TemporaryDirectory(prefix="sledtrace-independent-app-") as temp_dir:
        temp_root = Path(temp_dir)
        external_wheel = temp_root / wheel.name
        shutil.copy2(wheel, external_wheel)
        venv_dir = temp_root / "venv"
        app_dir = temp_root / "external-app"
        app_dir.mkdir()
        copied_example = app_dir / "independent_app.py"
        shutil.copy2(EXAMPLE, copied_example)

        result = run([sys.executable, "-m", "venv", str(venv_dir)], cwd=temp_root)
        if result.returncode != 0:
            return 1

        if os.name == "nt":
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = venv_dir / "bin" / "python"

        result = run(
            [
                str(python_exe),
                "-m",
                "pip",
                "install",
                "--no-deps",
                str(external_wheel),
            ],
            cwd=app_dir,
        )
        if result.returncode != 0:
            return 1

        clean_env = os.environ.copy()
        clean_env.pop("PYTHONPATH", None)
        clean_env.pop("SLEDTRACE_COLLECTOR_URL", None)
        clean_env.pop("RAGLENS_COLLECTOR_URL", None)
        import_check = (
            "import pathlib, sledtrace; "
            f"assert sledtrace.__version__ == '{EXPECTED_VERSION}'; "
            f"assert pathlib.Path(sledtrace.__file__).resolve().is_relative_to(pathlib.Path({str(temp_root)!r}).resolve()); "
            "print(sledtrace.__version__, sledtrace.__file__)"
        )
        result = run([str(python_exe), "-c", import_check], cwd=app_dir, env=clean_env)
        if result.returncode != 0:
            return 1

        CaptureHandler.payloads = []
        server = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
        collector_url = f"http://127.0.0.1:{server.server_port}"
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        try:
            success = run(
                [
                    str(python_exe),
                    str(copied_example),
                    "success",
                    "--collector-url",
                    collector_url,
                ],
                cwd=app_dir,
                env=clean_env,
            )
            require(success.returncode == 0, "success case did not return 0")
            require("PASS: trace stored" in success.stdout, "success output was unclear")

            application_error = run(
                [
                    str(python_exe),
                    str(copied_example),
                    "application-error",
                    "--collector-url",
                    collector_url,
                ],
                cwd=app_dir,
                env=clean_env,
            )
            require(
                application_error.returncode == 2,
                "application-error case did not preserve its documented exit code",
            )
            require(
                "EXPECTED APPLICATION ERROR: ExampleBusinessError" in application_error.stdout,
                "application-error output did not preserve the business failure",
            )
            require(
                "SLEDTRACE DELIVERY: stored error trace" in application_error.stdout,
                "application-error trace was not observably delivered",
            )
            validate_payloads(CaptureHandler.payloads)
        finally:
            offline_port = server.server_port
            server.shutdown()
            server.server_close()
            server_thread.join(timeout=5)

        offline = run(
            [
                str(python_exe),
                str(copied_example),
                "collector-offline",
                "--collector-url",
                f"http://127.0.0.1:{offline_port}",
                "--timeout",
                "0.25",
            ],
            cwd=app_dir,
            env=clean_env,
        )
        require(offline.returncode == 1, "collector-offline case did not return 1")
        require("BUSINESS RESULT:" in offline.stdout, "offline case lost business output")
        require(
            "EXPECTED SLEDTRACE DELIVERY FAILURE: RuntimeError" in offline.stderr,
            "offline delivery failure was not observable",
        )

    print("PASS: copied independent app validated against the installed wheel.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(validate())
    except RuntimeError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
