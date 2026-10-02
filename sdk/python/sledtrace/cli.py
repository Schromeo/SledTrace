from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import Iterable, Optional, Sequence

from . import __version__


REPO_MARKERS = (
    Path("AGENTS.md"),
    Path("docker-compose.yml"),
    Path("scripts") / "start-sledtrace.py",
)

BUNDLE_DIR = Path(__file__).resolve().parent / "_bundle"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4319
HEALTH_TIMEOUT_SECONDS = 15.0

SERVE_CHECKOUT_ERROR = (
    "This sledtrace installation does not include the bundled collector and "
    "dashboard (no prebuilt wheel exists for this platform). Run 'sledtrace serve' "
    "from a SledTrace source checkout, or use Docker Compose from the repository root."
)


def _candidate_directories(start: Path) -> Iterable[Path]:
    current = start.resolve()
    if current.is_file():
        current = current.parent

    yield current
    yield from current.parents


def find_repo_root(start: Optional[Path] = None) -> Optional[Path]:
    """Find a SledTrace source checkout at or above the starting directory."""
    for candidate in _candidate_directories(start or Path.cwd()):
        if all((candidate / marker).exists() for marker in REPO_MARKERS):
            return candidate

    return None


def find_bundle(bundle_dir: Optional[Path] = None) -> Optional[tuple[Path, Path]]:
    """Return (collector binary, dashboard directory) when this install ships them."""
    root = bundle_dir or BUNDLE_DIR
    binary_name = "sledtrace-collector.exe" if os.name == "nt" else "sledtrace-collector"
    binary = root / binary_name
    dashboard = root / "dashboard"

    if binary.is_file() and (dashboard / "index.html").is_file():
        return binary, dashboard

    return None


def default_db_path() -> Path:
    configured = os.environ.get("SLEDTRACE_DB_PATH")
    if configured:
        return Path(configured)

    return Path.home() / ".sledtrace" / "sledtrace.db"


def _display_host(host: str) -> str:
    return "127.0.0.1" if host in ("", "0.0.0.0", "::") else host


def _url(host: str, port: int) -> str:
    display = _display_host(host)
    if ":" in display:
        display = f"[{display}]"
    return f"http://{display}:{port}"


def _collector_health(url: str, timeout: float = 1.0) -> Optional[dict]:
    try:
        with urllib.request.urlopen(f"{url}/health", timeout=timeout) as response:
            if response.status != 200:
                return None
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _is_sledtrace(health: Optional[dict]) -> bool:
    return bool(health) and health.get("service") == "sledtrace-collector"


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET6 if ":" in host else socket.AF_INET) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((_display_host(host), port)) == 0


def _ensure_executable(binary: Path) -> None:
    if os.name == "nt":
        return

    mode = binary.stat().st_mode
    if not mode & stat.S_IXUSR:
        try:
            binary.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            pass


def _open_browser(url: str, enabled: bool) -> None:
    if not enabled:
        return

    try:
        webbrowser.open(url)
    except Exception:  # pragma: no cover - depends on the local desktop
        pass


def serve_bundled(
    binary: Path,
    dashboard: Path,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    db_path: Optional[Path] = None,
    open_browser: bool = True,
) -> int:
    url = _url(host, port)

    if _is_sledtrace(_collector_health(url)):
        print(f"SledTrace is already running at {url}")
        _open_browser(url, open_browser)
        return 0

    if _port_in_use(host, port):
        print(
            f"Port {port} on {_display_host(host)} is already in use by another program. "
            "Stop it or choose another port with --port.",
            file=sys.stderr,
        )
        return 1

    db = db_path or default_db_path()
    db.parent.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["SLEDTRACE_COLLECTOR_ADDR"] = f"{host}:{port}"
    env["SLEDTRACE_DB_PATH"] = str(db)
    env["SLEDTRACE_DASHBOARD_DIR"] = str(dashboard)

    _ensure_executable(binary)
    process = subprocess.Popen([str(binary)], env=env)

    deadline = time.monotonic() + HEALTH_TIMEOUT_SECONDS
    while not _is_sledtrace(_collector_health(url)):
        if process.poll() is not None:
            print(
                f"The SledTrace collector exited with code {process.returncode} "
                "before it became ready. See the log above.",
                file=sys.stderr,
            )
            return process.returncode or 1
        if time.monotonic() > deadline:
            print(f"The SledTrace collector did not become ready at {url}.", file=sys.stderr)
            _stop(process)
            return 1
        time.sleep(0.2)

    print("")
    print(f"SledTrace is running at {url}")
    print(f"  Traces are stored in {db}")
    if port != DEFAULT_PORT or _display_host(host) != DEFAULT_HOST:
        print(f"  Point your app at it with SLEDTRACE_COLLECTOR_URL={url}")
    print("  Press Ctrl+C to stop.")
    print("", flush=True)

    _open_browser(url, open_browser)

    previous_handlers = _interrupt_on_termination()
    try:
        return process.wait()
    except KeyboardInterrupt:
        print("\nStopping SledTrace...", flush=True)
        _stop(process)
        return 0
    finally:
        _restore_handlers(previous_handlers)


def _raise_keyboard_interrupt(signum, frame):  # noqa: ARG001
    raise KeyboardInterrupt


def _interrupt_on_termination() -> dict:
    """Treat SIGTERM (and SIGBREAK on Windows) like Ctrl+C so the collector stops too."""
    previous = {}
    for name in ("SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is None:
            continue
        try:
            previous[signum] = signal.signal(signum, _raise_keyboard_interrupt)
        except (ValueError, OSError):  # not the main thread, or unsupported
            pass
    return previous


def _restore_handlers(previous: dict) -> None:
    for signum, handler in previous.items():
        try:
            signal.signal(signum, handler)
        except (ValueError, OSError):
            pass


def _stop(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def serve_from_checkout(repo_root: Path) -> int:
    startup_script = repo_root / "scripts" / "start-sledtrace.py"

    print("Starting SledTrace local stack from the source checkout...")
    return subprocess.call([sys.executable, str(startup_script)])


def serve(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    db_path: Optional[Path] = None,
    open_browser: bool = True,
    source: bool = False,
) -> int:
    bundle = None if source else find_bundle()
    if bundle is not None:
        binary, dashboard = bundle
        return serve_bundled(binary, dashboard, host, port, db_path, open_browser)

    repo_root = find_repo_root()
    if repo_root is None:
        print(SERVE_CHECKOUT_ERROR, file=sys.stderr)
        return 1

    return serve_from_checkout(repo_root)


def show_version() -> int:
    print(__version__)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sledtrace",
        description="Inspect and run SledTrace local developer tooling.",
    )
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the local collector and open the dashboard",
        description=(
            "Start the local SledTrace collector and dashboard on one address "
            f"(default {_url(DEFAULT_HOST, DEFAULT_PORT)}) and open it in your browser. "
            "Installs from a platform wheel include everything needed. Without the "
            "bundled collector, run this from a SledTrace source checkout instead."
        ),
    )
    serve_parser.add_argument("--host", default=DEFAULT_HOST, help="address to bind (default: %(default)s)")
    serve_parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="port to listen on (default: %(default)s)")
    serve_parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="SQLite file for traces (default: $SLEDTRACE_DB_PATH or ~/.sledtrace/sledtrace.db)",
    )
    serve_parser.add_argument("--no-browser", action="store_true", help="do not open the dashboard in a browser")
    serve_parser.add_argument(
        "--source",
        action="store_true",
        help="ignore the bundled collector and run the source checkout's development stack",
    )
    serve_parser.set_defaults(
        func=lambda args: serve(
            host=args.host,
            port=args.port,
            db_path=args.db,
            open_browser=not args.no_browser,
            source=args.source,
        )
    )

    version_parser = subparsers.add_parser(
        "version",
        help="Print the installed SledTrace package version",
        description="Print the installed SledTrace package version.",
    )
    version_parser.set_defaults(func=lambda _args: show_version())

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
