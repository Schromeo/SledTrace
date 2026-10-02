#!/usr/bin/env python3
"""Build SledTrace distributions, including platform wheels that bundle the
collector binary and the built dashboard so `sledtrace serve` works after a
plain `pip install sledtrace`.

Outputs (in sdk/python/dist by default):
  - sledtrace-<v>.tar.gz and sledtrace-<v>-py3-none-any.whl  (SDK only)
  - sledtrace-<v>-py3-none-<platform>.whl                    (SDK + collector + dashboard)

Requirements: Go, Node.js/npm with dashboard dependencies installed
(`npm ci` in dashboard/web), and the `build` Python package.
Build on Linux or macOS so the collector keeps its executable bit.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SDK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SDK_DIR.parents[1]
COLLECTOR_DIR = REPO_ROOT / "collector" / "go"
DASHBOARD_DIR = REPO_ROOT / "dashboard" / "web"
BUNDLE_DIR = SDK_DIR / "sledtrace" / "_bundle"

# target name -> (GOOS, GOARCH, wheel platform tag)
TARGETS = {
    "linux-amd64": ("linux", "amd64", "manylinux2014_x86_64"),
    "linux-arm64": ("linux", "arm64", "manylinux2014_aarch64"),
    "macos-amd64": ("darwin", "amd64", "macosx_10_15_x86_64"),
    "macos-arm64": ("darwin", "arm64", "macosx_11_0_arm64"),
    "windows-amd64": ("windows", "amd64", "win_amd64"),
    "windows-arm64": ("windows", "arm64", "win_arm64"),
}


def current_target() -> str:
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "amd64"
    system = {"darwin": "macos", "win32": "windows"}.get(sys.platform, "linux")
    return f"{system}-{arch}"


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    print(f"$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=str(cwd), env=env, check=True)


def build_dashboard(out_dir: Path) -> None:
    npm = shutil.which("npm")
    if npm is None:
        raise SystemExit("npm is required to build the dashboard")

    env = dict(os.environ)
    # Empty means "same origin": the collector serves this build itself.
    env["VITE_SLEDTRACE_API_URL"] = ""
    run([npm, "run", "build", "--", "--outDir", str(out_dir), "--emptyOutDir"], DASHBOARD_DIR, env)

    if not (out_dir / "index.html").is_file():
        raise SystemExit(f"dashboard build did not produce {out_dir / 'index.html'}")


def build_collector(goos: str, goarch: str, output: Path) -> None:
    go = shutil.which("go")
    if go is None:
        raise SystemExit("Go is required to build the collector")

    env = dict(os.environ, CGO_ENABLED="0", GOOS=goos, GOARCH=goarch)
    run(
        [go, "build", "-trimpath", "-ldflags=-s -w", "-o", str(output), "./cmd/sledtrace-collector"],
        COLLECTOR_DIR,
        env,
    )
    output.chmod(0o755)


def clean_build_state() -> None:
    shutil.rmtree(SDK_DIR / "build", ignore_errors=True)
    for egg_info in SDK_DIR.glob("*.egg-info"):
        shutil.rmtree(egg_info, ignore_errors=True)


def build_python(out_dir: Path, args: list[str]) -> None:
    clean_build_state()
    run([sys.executable, "-m", "build", "--outdir", str(out_dir), *args], SDK_DIR)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--targets",
        default="all",
        help=f"comma-separated targets, 'current', or 'all' (default). Known: {', '.join(TARGETS)}",
    )
    parser.add_argument("--outdir", type=Path, default=SDK_DIR / "dist")
    parser.add_argument("--no-sdk-only", action="store_true", help="skip the sdist and the SDK-only any wheel")
    options = parser.parse_args()

    if options.targets == "all":
        targets = list(TARGETS)
    else:
        targets = [
            current_target() if name.strip() == "current" else name.strip()
            for name in options.targets.split(",")
            if name.strip()
        ]
    unknown = [name for name in targets if name not in TARGETS]
    if unknown:
        raise SystemExit(f"unknown targets: {', '.join(unknown)}")

    out_dir = options.outdir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(BUNDLE_DIR, ignore_errors=True)

    try:
        if not options.no_sdk_only:
            build_python(out_dir, ["--sdist", "--wheel"])

        if targets:
            with tempfile.TemporaryDirectory(prefix="sledtrace-dashboard-") as dashboard_tmp:
                dashboard_build = Path(dashboard_tmp) / "dist"
                build_dashboard(dashboard_build)

                for name in targets:
                    goos, goarch, plat = TARGETS[name]
                    shutil.rmtree(BUNDLE_DIR, ignore_errors=True)
                    BUNDLE_DIR.mkdir(parents=True)
                    binary = "sledtrace-collector.exe" if goos == "windows" else "sledtrace-collector"
                    build_collector(goos, goarch, BUNDLE_DIR / binary)
                    shutil.copytree(dashboard_build, BUNDLE_DIR / "dashboard")
                    build_python(out_dir, ["--wheel", f"-C--build-option=--plat-name={plat}"])
    finally:
        shutil.rmtree(BUNDLE_DIR, ignore_errors=True)
        clean_build_state()

    print("\nBuilt:")
    for artifact in sorted(out_dir.iterdir()):
        print(f"  {artifact.name}  ({artifact.stat().st_size / 1_000_000:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
