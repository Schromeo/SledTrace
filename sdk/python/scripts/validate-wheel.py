#!/usr/bin/env python3
"""Validate that a built SledTrace wheel installs cleanly and exposes the expected imports."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
EXPECTED_VERSION = "0.8.0"
EXPECTED_SERVE_ERROR = "does not include the bundled collector and dashboard"


def run(command: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(command)}")
    return subprocess.run(command, cwd=str(cwd or ROOT), text=True, capture_output=True)


def expected_wheels() -> list[Path]:
    return sorted(DIST_DIR.glob(f"sledtrace-{EXPECTED_VERSION}-py3-none-any.whl"))


def build_if_needed() -> Path:
    if not expected_wheels():
        result = run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.stderr or result.stdout or "pip upgrade failed")

        result = run([sys.executable, "-m", "pip", "install", "build"], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.stderr or result.stdout or "build install failed")

        result = run([sys.executable, "-m", "build"], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.stderr or result.stdout or "python -m build failed")

    wheels = expected_wheels()
    if not wheels:
        raise SystemExit(
            f"No SledTrace {EXPECTED_VERSION} wheel artifact found in {DIST_DIR}"
        )

    wheel = wheels[-1]
    print(f"Using wheel: {wheel}")
    return wheel


def wheel_has_bundle(wheel: Path) -> bool:
    with zipfile.ZipFile(wheel) as archive:
        return any(name.startswith("sledtrace/_bundle/") for name in archive.namelist())


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def http_get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def stop_serve(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        # Reaches both `sledtrace serve` and the collector in its process group.
        process.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def check_bundled_serve(sledtrace_exe: Path, python_exe: Path, temp_dir: Path) -> int:
    """`pip install` + `sledtrace serve` must run the dashboard and accept traces."""
    port = free_port()
    url = f"http://127.0.0.1:{port}"
    command = [
        str(sledtrace_exe), "serve", "--no-browser",
        "--port", str(port), "--db", str(temp_dir / "serve" / "traces.db"),
    ]
    print(f"$ {' '.join(command)}")
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    process = subprocess.Popen(
        command, cwd=str(temp_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, creationflags=creationflags,
    )

    try:
        deadline = time.monotonic() + 30
        while True:
            try:
                if json.loads(http_get(f"{url}/health")).get("service") == "sledtrace-collector":
                    break
            except OSError:
                pass
            if process.poll() is not None or time.monotonic() > deadline:
                print("Bundled 'sledtrace serve' did not become ready.")
                return 1
            time.sleep(0.3)

        page = http_get(f"{url}/")
        if "<title>SledTrace</title>" not in page:
            print(f"Expected the Dashboard at {url}/, got:\n{page[:300]}")
            return 1

        snippet = (
            "from sledtrace import trace; "
            "t=trace('wheel-serve-check', query='refund window?'); "
            "t.retrieval('refund window', chunks=[{'text':'30 days','score':0.9}]); "
            "t.llm('fixture', prompt='p', response='30 days'); "
            f"print(t.flush(collector_url='{url}')['status'])"
        )
        result = run([str(python_exe), "-c", snippet], cwd=temp_dir)
        if result.returncode != 0 or "stored" not in result.stdout:
            print(result.stderr or result.stdout)
            return 1

        if "wheel-serve-check" not in http_get(f"{url}/api/traces"):
            print("Trace sent to the bundled collector was not listed by the API.")
            return 1

        print(f"bundled serve ok: dashboard and API on {url}")
    finally:
        stop_serve(process)
        output = process.stdout.read() if process.stdout else ""
        print(output.strip())

    if "SledTrace is running at" not in output:
        print("'sledtrace serve' did not print its startup banner.")
        return 1

    return 0


def validate_wheel(wheel: Optional[Path] = None) -> int:
    wheel = wheel or build_if_needed()
    bundled = wheel_has_bundle(wheel)
    print(f"Validating {wheel.name} ({'with' if bundled else 'without'} bundled collector)")

    with tempfile.TemporaryDirectory(prefix="sledtrace-wheel-validate-") as temp_dir:
        venv_dir = Path(temp_dir) / "venv"
        venv_result = run([sys.executable, "-m", "venv", str(venv_dir)], cwd=ROOT)
        if venv_result.returncode != 0:
            print(venv_result.stderr or venv_result.stdout)
            return 1

        if os.name == "nt":
            python_exe = venv_dir / "Scripts" / "python.exe"
            sledtrace_exe = venv_dir / "Scripts" / "sledtrace.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
            sledtrace_exe = venv_dir / "bin" / "sledtrace"

        install_result = run([str(python_exe), "-m", "pip", "install", str(wheel)], cwd=ROOT)
        if install_result.returncode != 0:
            print(install_result.stderr or install_result.stdout)
            return 1

        import_checks = [
            f"import sledtrace; assert sledtrace.__version__ == '{EXPECTED_VERSION}'; print(sledtrace.__version__)",
            "from sledtrace import SpanTiming, trace; assert isinstance(trace('timing').measure(), SpanTiming); print(trace)",
            (
                "from sledtrace import TraceFlushResult, trace; "
                "result=trace('delivery').try_flush(collector_url='not-a-url'); "
                "assert isinstance(result, TraceFlushResult); "
                "assert not result.ok and result.error is not None; "
                "print('delivery policy ok')"
            ),
            (
                "from sledtrace import normalize_chunk; "
                "similarity=normalize_chunk({'text':'x','similarity':0.1}); "
                "distance=normalize_chunk({'text':'x','distance':0.1}); "
                "assert similarity['score_direction']=='higher_is_better'; "
                "assert distance['score_type']=='distance'; "
                "assert distance['score_direction']=='lower_is_better'; "
                "print('score semantics ok')"
            ),
            (
                "from sledtrace import trace; "
                "t=trace('wheel-tool'); "
                "span_id=t.tool('lookup', input_summary='key', output_summary='one match'); "
                "t.llm('fixture', response='draft', status='error', error='invalid', input_tokens=2); "
                "t.log_task_result('final', accepted=True); "
                "p=t.to_dict(); "
                "assert p['spans'][0]['span_id']==span_id and p['spans'][0]['type']=='tool'; "
                "assert p['spans'][1]['status']=='error' and p['spans'][1]['metadata']['input_tokens']==2; "
                "assert p['trace']['output']['answer']=='final'; "
                "print('agent tool contract ok')"
            ),
            "import raglens; print('legacy raglens import ok')",
        ]

        for snippet in import_checks:
            result = run([str(python_exe), "-c", snippet], cwd=ROOT)
            if result.returncode != 0:
                print(result.stderr or result.stdout)
                return 1
            print(result.stdout.strip())

        cli_checks = [
            ([str(sledtrace_exe), "--help"], "serve"),
            ([str(sledtrace_exe), "serve", "--help"], "source checkout"),
            ([str(sledtrace_exe), "version"], EXPECTED_VERSION),
        ]

        for command, expected_output in cli_checks:
            result = run(command, cwd=Path(temp_dir))
            if result.returncode != 0:
                print(result.stderr or result.stdout)
                return 1

            combined_output = f"{result.stdout}\n{result.stderr}"
            if expected_output not in combined_output:
                print(
                    f"Expected {expected_output!r} in CLI output, got:\n{combined_output}"
                )
                return 1

            print(result.stdout.strip())

        if bundled:
            if check_bundled_serve(sledtrace_exe, python_exe, Path(temp_dir)) != 0:
                return 1
        else:
            serve_result = run([str(sledtrace_exe), "serve"], cwd=Path(temp_dir))
            if serve_result.returncode == 0:
                print("Expected 'sledtrace serve' without a bundle or checkout to fail.")
                return 1

            if EXPECTED_SERVE_ERROR not in serve_result.stderr:
                print(
                    "Wheel-installed 'sledtrace serve' did not provide the expected guidance:\n"
                    f"stdout:\n{serve_result.stdout}\nstderr:\n{serve_result.stderr}"
                )
                return 1

            print(serve_result.stderr.strip())

    print("PASS: wheel install, import, and CLI validation succeeded.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, help="wheel to validate (default: build or reuse dist/)")
    options = parser.parse_args()
    raise SystemExit(validate_wheel(options.wheel.resolve() if options.wheel else None))
