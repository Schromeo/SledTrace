#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.client
import json
import math
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


class StartupError(RuntimeError):
    """An actionable local startup failure."""


@dataclass
class Settings:
    repo_root: Path
    collector_host: str
    collector_port: int
    dashboard_port: int
    timeout: float
    env: dict[str, str]

    @property
    def collector_url(self) -> str:
        host = self.collector_host
        if host in ("", "0.0.0.0"):
            host = "127.0.0.1"
        elif host == "::":
            host = "::1"
        if ":" in host:
            host = f"[{host}]"
        return f"http://{host}:{self.collector_port}"

    @property
    def dashboard_url(self) -> str:
        return f"http://127.0.0.1:{self.dashboard_port}"


def configure(repo_root: Path, argv: list[str] | None = None) -> Settings:
    parser = argparse.ArgumentParser(description="Start and check the local SledTrace source stack.")
    parser.add_argument("--dashboard-port", type=int, default=5173)
    parser.add_argument("--startup-timeout", type=float, default=60,
                        help="Seconds to wait for both services (default: 60)")
    args = parser.parse_args(argv)
    if not 1 <= args.dashboard_port <= 65535:
        raise StartupError("Dashboard port must be between 1 and 65535.")
    if not math.isfinite(args.startup_timeout) or args.startup_timeout <= 0:
        raise StartupError("Startup timeout must be a finite positive number.")

    env = os.environ.copy()
    address = (env.get("SLEDTRACE_COLLECTOR_ADDR")
               or env.get("RAGLENS_COLLECTOR_ADDR") or "127.0.0.1:4319")
    try:
        parsed = urlsplit("http://" + address)
        port = parsed.port
        host = parsed.hostname or ""
        if (not port or parsed.path or parsed.query or parsed.fragment
                or parsed.username is not None or parsed.password is not None):
            raise ValueError("expected host:port")
    except ValueError as exc:
        raise StartupError(
            "Invalid Collector address. Set SLEDTRACE_COLLECTOR_ADDR to host:port "
            "(for example 127.0.0.1:4319 or [::1]:4319)."
        ) from exc

    settings = Settings(repo_root, host, port, args.dashboard_port, args.startup_timeout, env)
    # Keep services consistent without overriding explicit client/origin settings.
    env["SLEDTRACE_COLLECTOR_ADDR"] = address
    env["VITE_SLEDTRACE_API_URL"] = (env.get("VITE_SLEDTRACE_API_URL")
                                     or env.get("VITE_RAGLENS_API_URL")
                                     or settings.collector_url)
    if not env.get("SLEDTRACE_ALLOWED_ORIGINS"):
        env["SLEDTRACE_ALLOWED_ORIGINS"] = (
            f"http://localhost:{settings.dashboard_port},{settings.dashboard_url}"
        )
    return settings


def npm_command() -> str:
    return "npm.cmd" if sys.platform == "win32" else "npm"


def format_socket_error(exc: OSError) -> str:
    code = getattr(exc, "winerror", None) or exc.errno
    return f"socket error {code}" if code is not None else "socket error"


def check_port(host: str, port: int, label: str) -> None:
    try:
        addresses = socket.getaddrinfo(host or "0.0.0.0", port, type=socket.SOCK_STREAM)
        for family, socktype, protocol, _, address in addresses:
            with socket.socket(family, socktype, protocol) as probe:
                if sys.platform == "win32":
                    probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
                else:
                    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                probe.bind(address)
    except OSError as exc:
        option = "SLEDTRACE_COLLECTOR_ADDR" if label == "Collector" else "--dashboard-port"
        raise StartupError(
            f"{label} cannot bind {host or '0.0.0.0'}:{port} ({format_socket_error(exc)}). "
            f"Stop the existing service yourself or choose another address/port with {option}."
        ) from exc


def preflight(settings: Settings) -> dict[str, str]:
    for relative in ("collector/go", "dashboard/web"):
        if not (settings.repo_root / relative).is_dir():
            raise StartupError(f"Missing {relative}. Run this helper from a complete source checkout.")
    commands = {}
    for name in ("go", "node", npm_command()):
        executable = shutil.which(name)
        if not executable:
            raise StartupError(f"Missing executable: {name}. Install Go and Node.js 22+ (with npm), then reopen your terminal.")
        commands[name] = executable
    try:
        version = subprocess.run([commands["node"], "--version"], capture_output=True,
                                 text=True, check=True, timeout=5).stdout.strip()
        if int(version.lstrip("v").split(".")[0]) < 22:
            raise StartupError(f"Node.js 22+ is required; found {version}.")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise StartupError("Could not check Node.js. Confirm node --version works and reports 22+.") from exc
    if not (settings.repo_root / "dashboard/web/node_modules/vite/bin/vite.js").is_file():
        raise StartupError("Dashboard dependencies are missing. From the checkout run: cd dashboard/web && npm ci")
    check_port(settings.collector_host, settings.collector_port, "Collector")
    check_port("127.0.0.1", settings.dashboard_port, "Dashboard")
    return commands


def start_process(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.Popen:
    # go run and npm spawn children; give each service an owned process tree.
    options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
               if sys.platform == "win32" else {"start_new_session": True})
    try:
        return subprocess.Popen(command, cwd=str(cwd), env=env, **options)
    except OSError as exc:
        raise StartupError(f"Failed to start {command[0]}: {exc}") from exc


def stop_processes(processes: list[tuple[str, subprocess.Popen]]) -> None:
    for name, proc in reversed(processes):
        try:
            if sys.platform == "win32":
                if proc.poll() is None:
                    # Target only the PID created by this helper and its descendants.
                    result = subprocess.run(
                        ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                        capture_output=True, timeout=10,
                    )
                    if result.returncode and proc.poll() is None:
                        detail = (result.stderr or result.stdout).decode(errors="replace").strip()
                        raise StartupError(f"Could not stop {name} process tree (PID {proc.pid}): {detail}")
            else:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
            if sys.platform != "win32":
                # A wrapper can exit before a child; clean up its remaining group.
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        except (OSError, StartupError, subprocess.SubprocessError) as exc:
            print(f"Cleanup failed for {name} (PID {proc.pid}): {exc}", file=sys.stderr)


def ensure_running(processes: list[tuple[str, subprocess.Popen]]) -> None:
    for name, proc in processes:
        code = proc.poll()
        if code is not None:
            raise StartupError(f"{name} exited with code {code}. See its output above.")


def probe_service(url: str, collector: bool) -> tuple[bool, str]:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url, timeout=0.5) as response:
            body = response.read(8192)
            if response.status != 200:
                return False, f"HTTP {response.status}"
        if collector:
            payload = json.loads(body)
            if not isinstance(payload, dict) or payload.get("status") != "ok" or payload.get("service") != "sledtrace-collector":
                return False, "response is not a healthy SledTrace Collector"
        elif b"<title>SledTrace</title>" not in body:
            return False, "response is not the SledTrace Dashboard"
        return True, "ready"
    except (OSError, ValueError, http.client.HTTPException) as exc:
        return False, str(exc)


def wait_until_ready(settings: Settings, processes: list[tuple[str, subprocess.Popen]]) -> None:
    deadline = time.monotonic() + settings.timeout
    targets = [("Collector", settings.collector_url + "/health", True),
               ("Dashboard", settings.dashboard_url, False)]
    pending = targets.copy()
    failures = {}
    while pending:
        ensure_running(processes)
        for target in pending.copy():
            name, url, collector = target
            ready, detail = probe_service(url, collector)
            if ready:
                print(f"{name} ready: {url}", flush=True)
                pending.remove(target)
            else:
                failures[name] = f"{url}: {detail}"
        if pending and time.monotonic() >= deadline:
            detail = "; ".join(f"{name} at {failures[name]}" for name, _, _ in pending)
            raise StartupError(f"Startup timed out after {settings.timeout:g}s. {detail}. Check service output or increase --startup-timeout for the first Go build.")
        if pending:
            time.sleep(0.2)
    ensure_running(processes)


def supervise(processes: list[tuple[str, subprocess.Popen]]) -> None:
    while True:
        ensure_running(processes)
        time.sleep(0.2)


def main(argv: list[str] | None = None) -> int:
    processes = []
    previous_handlers = {}

    def interrupt(_signal, _frame):
        raise KeyboardInterrupt

    try:
        settings = configure(Path(__file__).resolve().parent.parent, argv)
        commands = preflight(settings)
        for sig in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[sig] = signal.signal(sig, interrupt)
        print("Preflight passed. Starting local services...", flush=True)
        processes.append(("Collector", start_process(
            [commands["go"], "run", "./cmd/sledtrace-collector"],
            settings.repo_root / "collector/go", settings.env)))
        processes.append(("Dashboard", start_process(
            [commands[npm_command()], "run", "dev", "--", "--strictPort", "--host", "127.0.0.1",
             "--port", str(settings.dashboard_port)],
            settings.repo_root / "dashboard/web", settings.env)))
        wait_until_ready(settings, processes)
        print(f"SledTrace ready. Open {settings.dashboard_url}", flush=True)
        print(f"SDK Collector URL: {settings.collector_url}", flush=True)
        if settings.env["VITE_SLEDTRACE_API_URL"] != settings.collector_url:
            print(f"Dashboard API override: {settings.env['VITE_SLEDTRACE_API_URL']}", flush=True)
        print("Press Ctrl+C to stop both services.", flush=True)
        supervise(processes)
        return 0
    except KeyboardInterrupt:
        print("Stopping SledTrace services...", flush=True)
        return 130
    except StartupError as exc:
        print(f"SledTrace startup failed: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        for sig in previous_handlers:
            signal.signal(sig, signal.SIG_IGN)
        try:
            stop_processes(processes)
        finally:
            for sig, previous in previous_handlers.items():
                signal.signal(sig, previous)


if __name__ == "__main__":
    raise SystemExit(main())
