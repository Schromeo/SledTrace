import importlib
import os
import unittest
from typing import Optional

from raglens import trace as legacy_trace
from raglens.trace import resolve_collector_url
from sledtrace import trace as new_trace


class RebrandCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_new = os.environ.get("SLEDTRACE_COLLECTOR_URL")
        self.previous_legacy = os.environ.get("RAGLENS_COLLECTOR_URL")
        os.environ.pop("SLEDTRACE_COLLECTOR_URL", None)
        os.environ.pop("RAGLENS_COLLECTOR_URL", None)

    def tearDown(self) -> None:
        self._restore("SLEDTRACE_COLLECTOR_URL", self.previous_new)
        self._restore("RAGLENS_COLLECTOR_URL", self.previous_legacy)

    def _restore(self, key: str, value: Optional[str]) -> None:
        if value is None:
            os.environ.pop(key, None)
            return
        os.environ[key] = value

    def test_default_collector_url(self) -> None:
        self.assertEqual(resolve_collector_url(None), "http://localhost:4319")

    def test_legacy_collector_url_fallback(self) -> None:
        os.environ["RAGLENS_COLLECTOR_URL"] = "http://legacy.example:4319"
        self.assertEqual(resolve_collector_url(None), "http://legacy.example:4319")

    def test_new_collector_url_preferred_over_legacy(self) -> None:
        os.environ["SLEDTRACE_COLLECTOR_URL"] = "http://new.example:4319"
        os.environ["RAGLENS_COLLECTOR_URL"] = "http://legacy.example:4319"
        self.assertEqual(resolve_collector_url(None), "http://new.example:4319")

    def test_explicit_collector_url_has_highest_priority(self) -> None:
        os.environ["SLEDTRACE_COLLECTOR_URL"] = "http://new.example:4319"
        self.assertEqual(
            resolve_collector_url("http://explicit.example:4319"),
            "http://explicit.example:4319",
        )

    def test_new_and_legacy_trace_imports_match(self) -> None:
        self.assertIs(new_trace, legacy_trace)

    def test_new_and_legacy_packages_load(self) -> None:
        self.assertIsNotNone(importlib.import_module("sledtrace"))
        self.assertIsNotNone(importlib.import_module("raglens"))


if __name__ == "__main__":
    unittest.main()
