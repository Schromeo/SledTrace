import os
import subprocess
import sys
from pathlib import Path

import raglens
import sledtrace
import sledtrace.cli
from raglens import trace as legacy_trace
from raglens.trace import resolve_collector_url
from sledtrace import trace as new_trace


def test_sdk_version_exists() -> None:
    assert hasattr(sledtrace, "__version__")
    assert sledtrace.__version__ == "0.7.0rc1"


def test_public_trace_imports() -> None:
    assert new_trace is not None
    assert legacy_trace is not None
    assert new_trace is legacy_trace


def test_default_collector_url() -> None:
    previous_new = os.environ.get("SLEDTRACE_COLLECTOR_URL")
    previous_legacy = os.environ.get("RAGLENS_COLLECTOR_URL")
    os.environ.pop("SLEDTRACE_COLLECTOR_URL", None)
    os.environ.pop("RAGLENS_COLLECTOR_URL", None)
    try:
        assert resolve_collector_url(None) == "http://localhost:4319"
    finally:
        if previous_new is not None:
            os.environ["SLEDTRACE_COLLECTOR_URL"] = previous_new
        else:
            os.environ.pop("SLEDTRACE_COLLECTOR_URL", None)
        if previous_legacy is not None:
            os.environ["RAGLENS_COLLECTOR_URL"] = previous_legacy
        else:
            os.environ.pop("RAGLENS_COLLECTOR_URL", None)


def test_collector_url_env_precedence() -> None:
    previous_new = os.environ.get("SLEDTRACE_COLLECTOR_URL")
    previous_legacy = os.environ.get("RAGLENS_COLLECTOR_URL")
    os.environ["SLEDTRACE_COLLECTOR_URL"] = "http://new.example:4319"
    os.environ["RAGLENS_COLLECTOR_URL"] = "http://legacy.example:4319"
    try:
        assert resolve_collector_url(None) == "http://new.example:4319"
    finally:
        if previous_new is not None:
            os.environ["SLEDTRACE_COLLECTOR_URL"] = previous_new
        else:
            os.environ.pop("SLEDTRACE_COLLECTOR_URL", None)
        if previous_legacy is not None:
            os.environ["RAGLENS_COLLECTOR_URL"] = previous_legacy
        else:
            os.environ.pop("RAGLENS_COLLECTOR_URL", None)


def test_trace_object_can_be_created_without_collector() -> None:
    tr = new_trace("demo")
    assert tr.name == "demo"
    assert tr.collector_url == "http://localhost:4319"


def test_cli_module_and_entry_point_exist() -> None:
    assert callable(sledtrace.cli.main)


def test_cli_help_describes_source_checkout_limit(capsys) -> None:
    try:
        sledtrace.cli.main(["serve", "--help"])
    except SystemExit as exc:
        assert exc.code == 0

    output = " ".join(capsys.readouterr().out.split())
    assert "source checkout" in output
    assert "standalone wheel-installed serving is not supported" in output


def test_cli_version_reports_package_version(capsys) -> None:
    assert sledtrace.cli.main(["version"]) == 0
    assert capsys.readouterr().out.strip() == "0.7.0rc1"


def test_find_repo_root_walks_up_from_nested_directory(tmp_path: Path) -> None:
    repo_root = make_checkout(tmp_path)
    nested = repo_root / "sdk" / "python"
    nested.mkdir(parents=True)

    assert sledtrace.cli.find_repo_root(nested) == repo_root


def test_serve_outside_checkout_fails_with_guidance(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)

    assert sledtrace.cli.serve() == 1
    assert capsys.readouterr().err.strip() == sledtrace.cli.SERVE_CHECKOUT_ERROR


def test_serve_delegates_to_repo_startup_script(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = make_checkout(tmp_path)
    nested = repo_root / "sdk" / "python"
    nested.mkdir(parents=True)
    calls: list[list[str]] = []

    monkeypatch.chdir(nested)
    monkeypatch.setattr(
        subprocess,
        "call",
        lambda command: calls.append(command) or 0,
    )

    assert sledtrace.cli.serve() == 0
    assert calls == [
        [sys.executable, str(repo_root / "scripts" / "start-sledtrace.py")]
    ]


def make_checkout(parent: Path) -> Path:
    repo_root = parent / "SledTrace"
    (repo_root / "scripts").mkdir(parents=True)
    (repo_root / "AGENTS.md").touch()
    (repo_root / "docker-compose.yml").touch()
    (repo_root / "scripts" / "start-sledtrace.py").touch()
    return repo_root
