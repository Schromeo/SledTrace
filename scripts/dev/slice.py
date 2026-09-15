#!/usr/bin/env python3
"""Deterministic status, scope, and validation checks for one active slice."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Sequence


REQUIRED_KEYS = {
    "slice_id",
    "slice_status",
    "components",
    "validation_profile",
    "scope_base",
    "allowed_paths",
    "human_gates",
    "auto_continue",
}
LIST_KEYS = {"components", "allowed_paths", "human_gates"}


class SliceConfigError(ValueError):
    """CURRENT_TASK metadata is missing or invalid."""


def parse_frontmatter(text: str) -> dict[str, Any]:
    lines = text.replace("\r\n", "\n").splitlines()
    if not lines or lines[0] != "---":
        raise SliceConfigError("CURRENT_TASK must start with YAML frontmatter")

    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise SliceConfigError("CURRENT_TASK frontmatter is not closed") from exc

    metadata: dict[str, Any] = {}
    active_list: str | None = None
    for line_number, raw in enumerate(lines[1:closing], start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        if raw.startswith("  - "):
            if active_list is None:
                raise SliceConfigError(
                    f"unexpected list item on frontmatter line {line_number}"
                )
            metadata[active_list].append(_parse_scalar(raw[4:].strip()))
            continue

        if raw.startswith((" ", "\t")) or ":" not in raw:
            raise SliceConfigError(
                f"unsupported frontmatter syntax on line {line_number}"
            )

        key, raw_value = raw.split(":", 1)
        key = key.strip()
        if key in metadata:
            raise SliceConfigError(f"duplicate frontmatter key: {key}")

        raw_value = raw_value.strip()
        if raw_value:
            metadata[key] = _parse_scalar(raw_value)
            active_list = None
        else:
            metadata[key] = []
            active_list = key

    return metadata


def _parse_scalar(raw: str) -> str | bool:
    if raw == "true":
        return True
    if raw == "false":
        return False
    return raw


def _validate_metadata(metadata: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_KEYS - metadata.keys())
    if missing:
        raise SliceConfigError(f"missing frontmatter keys: {', '.join(missing)}")

    for key in LIST_KEYS:
        value = metadata[key]
        if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item for item in value
        ):
            raise SliceConfigError(f"{key} must be a non-empty string list")

    for key in REQUIRED_KEYS - LIST_KEYS - {"auto_continue"}:
        if not isinstance(metadata[key], str) or not metadata[key]:
            raise SliceConfigError(f"{key} must be a non-empty string")

    if metadata["slice_status"] not in {"active", "blocked", "complete"}:
        raise SliceConfigError("slice_status must be active, blocked, or complete")
    if metadata["auto_continue"] is not False:
        raise SliceConfigError("auto_continue must be false")


def load_metadata(task_path: Path) -> dict[str, Any]:
    metadata = parse_frontmatter(task_path.read_text(encoding="utf-8"))
    _validate_metadata(metadata)
    return metadata


def path_allowed(path: str, patterns: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return any(fnmatch.fnmatchcase(normalized, pattern) for pattern in patterns)


def _git(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_paths(repo_root: Path, base: str) -> list[str]:
    changed = _git(
        repo_root,
        "diff",
        "--name-only",
        "--diff-filter=ACMRDTUXB",
        base,
        "--",
    )
    untracked = _git(repo_root, "ls-files", "--others", "--exclude-standard")
    return sorted(set(changed + untracked))


def load_profiles(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("commands"), dict):
        raise SliceConfigError("validation profile file needs a commands object")
    if not isinstance(value.get("profiles"), dict):
        raise SliceConfigError("validation profile file needs a profiles object")
    return value


def profile_steps(profile_name: str, profiles: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        command_names = profiles["profiles"][profile_name]
    except KeyError as exc:
        raise SliceConfigError(f"unknown validation profile: {profile_name}") from exc
    if not isinstance(command_names, list) or not command_names:
        raise SliceConfigError(f"validation profile {profile_name} is empty")

    steps = []
    for command_name in command_names:
        try:
            step = profiles["commands"][command_name]
        except KeyError as exc:
            raise SliceConfigError(
                f"profile {profile_name} references unknown command {command_name}"
            ) from exc
        if not isinstance(step, dict) or not isinstance(step.get("argv"), list):
            raise SliceConfigError(f"command {command_name} has invalid argv")
        steps.append({"name": command_name, **step})
    return steps


def _display_status(metadata: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(metadata, indent=2, sort_keys=True))
        return
    print(f"Slice: {metadata['slice_id']} ({metadata['slice_status']})")
    print(f"Components: {', '.join(metadata['components'])}")
    print(f"Validation profile: {metadata['validation_profile']}")
    print(f"Scope base: {metadata['scope_base']}")
    print("Allowed paths:")
    for pattern in metadata["allowed_paths"]:
        print(f"  - {pattern}")
    print("Human gates:")
    for gate in metadata["human_gates"]:
        print(f"  - {gate}")
    print("Auto-continue: false")


def _check_scope(repo_root: Path, metadata: dict[str, Any], base: str) -> int:
    paths = changed_paths(repo_root, base)
    violations = [
        path for path in paths if not path_allowed(path, metadata["allowed_paths"])
    ]
    print(f"Slice {metadata['slice_id']} scope base: {base}")
    if paths:
        print("Changed paths:")
        for path in paths:
            marker = "OK" if path not in violations else "VIOLATION"
            print(f"  [{marker}] {path}")
    else:
        print("Changed paths: none")
    if violations:
        print(f"FAIL: {len(violations)} path(s) are outside the allowed slice scope")
        return 1
    print(f"PASS: {len(paths)} changed path(s) are within the allowed slice scope")
    return 0


def _run_profile(
    repo_root: Path,
    profile_name: str,
    profiles: dict[str, Any],
) -> int:
    steps = profile_steps(profile_name, profiles)
    print(f"Validation profile: {profile_name} ({len(steps)} steps)", flush=True)
    for index, step in enumerate(steps, start=1):
        argv = step.get("windows_argv") if os.name == "nt" else None
        argv = argv or step["argv"]
        argv = [sys.executable if item == "{python}" else item for item in argv]
        cwd = (repo_root / step["cwd"]).resolve()
        try:
            cwd.relative_to(repo_root.resolve())
        except ValueError:
            print(f"FAIL: command cwd escapes repository: {step['cwd']}")
            return 2
        print(
            f"[{index}/{len(steps)}] {step['name']}: "
            f"(cd {step['cwd']} && {' '.join(argv)})",
            flush=True,
        )
        result = subprocess.run(argv, cwd=cwd, check=False)
        if result.returncode != 0:
            print(f"FAIL: {step['name']} exited {result.returncode}")
            return result.returncode
        print(f"PASS: {step['name']}", flush=True)
    print(f"PASS: validation profile {profile_name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--task", type=Path)
    parser.add_argument("--profiles", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="show active slice metadata")
    status.add_argument("--json", action="store_true")
    scope = commands.add_parser("scope", help="check changed paths against scope")
    scope.add_argument("--base", help="override the metadata scope base")
    check = commands.add_parser("check", help="run a validation profile")
    check.add_argument("--profile", help="override the active validation profile")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    script_root = Path(__file__).resolve().parents[2]
    repo_root = (args.repo_root or script_root).resolve()
    task_path = args.task or repo_root / "docs/ai-context/CURRENT_TASK.md"
    profile_path = args.profiles or repo_root / "scripts/dev/validation_profiles.json"
    try:
        metadata = load_metadata(task_path)
        if args.command == "status":
            _display_status(metadata, args.json)
            return 0
        if args.command == "scope":
            return _check_scope(repo_root, metadata, args.base or metadata["scope_base"])
        profiles = load_profiles(profile_path)
        return _run_profile(
            repo_root,
            args.profile or metadata["validation_profile"],
            profiles,
        )
    except (OSError, RuntimeError, SliceConfigError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
