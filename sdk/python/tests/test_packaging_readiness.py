import os

import raglens
import sledtrace
from raglens import trace as legacy_trace
from raglens.trace import resolve_collector_url
from sledtrace import trace as new_trace


def test_sdk_version_exists() -> None:
    assert hasattr(sledtrace, "__version__")
    assert sledtrace.__version__ == "0.5.0"


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
    import sledtrace.cli

    assert callable(sledtrace.cli.main)
