#!/usr/bin/env python3
"""Validate that a built SledTrace wheel installs cleanly and exposes the expected imports."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
EXPECTED_VERSION = "0.7.0"
EXPECTED_SERVE_ERROR = (
    "sledtrace serve currently requires a SledTrace source checkout. "
    "Run it from the repository, or use Docker Compose from the repository root. "
    "Standalone wheel-installed serving is not supported by this package."
)


def run(command: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(command)}")
    return subprocess.run(command, cwd=str(cwd or ROOT), text=True, capture_output=True)


def expected_wheels() -> list[Path]:
    return sorted(DIST_DIR.glob(f"sledtrace-{EXPECTED_VERSION}-*.whl"))


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


def validate_wheel() -> int:
    wheel = build_if_needed()

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
            "from sledtrace import trace; print(trace)",
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

        serve_result = run([str(sledtrace_exe), "serve"], cwd=Path(temp_dir))
        if serve_result.returncode == 0:
            print("Expected wheel-installed 'sledtrace serve' outside a checkout to fail.")
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
    raise SystemExit(validate_wheel())
