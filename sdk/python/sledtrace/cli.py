from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional

from . import __version__


REPO_MARKERS = (
    Path("AGENTS.md"),
    Path("docker-compose.yml"),
    Path("scripts") / "start-sledtrace.py",
)

SERVE_CHECKOUT_ERROR = (
    "sledtrace serve currently requires a SledTrace source checkout. "
    "Run it from the repository, or use Docker Compose from the repository root. "
    "Standalone wheel-installed serving is not supported in v0.6.0."
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


def serve() -> int:
    repo_root = find_repo_root()
    if repo_root is None:
        print(SERVE_CHECKOUT_ERROR, file=sys.stderr)
        return 1

    startup_script = repo_root / "scripts" / "start-sledtrace.py"

    print("Starting SledTrace local stack...")
    return subprocess.call([sys.executable, str(startup_script)])


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
        help="Start the collector and dashboard from a SledTrace source checkout",
        description=(
            "Start the local collector and dashboard. This command must be run "
            "from inside a SledTrace source checkout; standalone wheel-installed "
            "serving is not supported in v0.6.0."
        ),
    )
    serve_parser.set_defaults(func=lambda _args: serve())

    version_parser = subparsers.add_parser(
        "version",
        help="Print the installed SledTrace package version",
        description="Print the installed SledTrace package version.",
    )
    version_parser.set_defaults(func=lambda _args: show_version())

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
