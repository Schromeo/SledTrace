from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def serve() -> int:
    repo_root = _repo_root()
    startup_script = repo_root / "scripts" / "start-sledtrace.py"

    if not startup_script.exists():
        print(f"Startup script not found: {startup_script}", file=sys.stderr)
        return 1

    print("Starting SledTrace local stack...")
    return subprocess.call([sys.executable, str(startup_script)])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sledtrace", description="SledTrace local developer CLI")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Start the local SledTrace collector and dashboard")
    serve_parser.set_defaults(func=lambda _args: serve())

    version_parser = subparsers.add_parser("version", help="Print the installed SledTrace version")
    version_parser.set_defaults(func=lambda _args: print(__version__))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
