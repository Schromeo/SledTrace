#!/usr/bin/env python3
"""Validate that a built SledTrace wheel installs cleanly and exposes the expected imports."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(command)}")
    return subprocess.run(command, cwd=str(cwd or ROOT), text=True, capture_output=True)


def build_if_needed() -> None:
    if not DIST_DIR.exists() or not any(DIST_DIR.glob("*.whl")):
        result = run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.stderr or result.stdout or "pip upgrade failed")

        result = run([sys.executable, "-m", "pip", "install", "build"], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.stderr or result.stdout or "build install failed")

        result = run([sys.executable, "-m", "build"], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.stderr or result.stdout or "python -m build failed")

    wheels = sorted(DIST_DIR.glob("*.whl"))
    if not wheels:
        raise SystemExit(f"No wheel artifacts found in {DIST_DIR}")

    print(f"Using wheel: {wheels[0]}")


def validate_wheel() -> int:
    build_if_needed()
    wheel = sorted((DIST_DIR).glob("*.whl"))[-1]

    with tempfile.TemporaryDirectory(prefix="sledtrace-wheel-validate-") as temp_dir:
        venv_dir = Path(temp_dir) / "venv"
        venv_result = run([sys.executable, "-m", "venv", str(venv_dir)], cwd=ROOT)
        if venv_result.returncode != 0:
            print(venv_result.stderr or venv_result.stdout)
            return 1

        if os.name == "nt":
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = venv_dir / "bin" / "python"

        install_result = run([str(python_exe), "-m", "pip", "install", str(wheel)], cwd=ROOT)
        if install_result.returncode != 0:
            print(install_result.stderr or install_result.stdout)
            return 1

        import_checks = [
            "import sledtrace; print(sledtrace.__version__)",
            "from sledtrace import trace; print(trace)",
            "import raglens; print('legacy raglens import ok')",
        ]

        for snippet in import_checks:
            result = run([str(python_exe), "-c", snippet], cwd=ROOT)
            if result.returncode != 0:
                print(result.stderr or result.stdout)
                return 1
            print(result.stdout.strip())

    print("PASS: wheel install and import validation succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate_wheel())
