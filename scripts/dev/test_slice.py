from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SLICE_PATH = Path(__file__).with_name("slice.py")
SPEC = importlib.util.spec_from_file_location("sledtrace_slice", SLICE_PATH)
assert SPEC and SPEC.loader
slice_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(slice_module)


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def task_text(allowed_paths: list[str]) -> str:
    paths = "\n".join(f"  - {path}" for path in allowed_paths)
    return f"""---
slice_id: TEST
slice_status: active
components:
  - dashboard
validation_profile: dashboard
scope_base: HEAD
allowed_paths:
{paths}
human_gates:
  - public_api_change
auto_continue: false
---

# Test task
"""


class MetadataTests(unittest.TestCase):
    def test_current_task_metadata_and_status(self) -> None:
        metadata = slice_module.load_metadata(
            REPO_ROOT / "docs/ai-context/CURRENT_TASK.md"
        )
        self.assertEqual(metadata["slice_id"], "D0")
        self.assertEqual(metadata["slice_status"], "complete")
        self.assertEqual(
            metadata["components"], ["repository_workflow", "documentation"]
        )
        self.assertEqual(metadata["validation_profile"], "agent-harness")
        self.assertFalse(metadata["auto_continue"])

        result = subprocess.run(
            [sys.executable, str(SLICE_PATH), "status", "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["slice_id"], "D0")

    def test_active_profile_resolves_without_duplicated_commands(self) -> None:
        profiles = slice_module.load_profiles(
            REPO_ROOT / "scripts/dev/validation_profiles.json"
        )
        steps = slice_module.profile_steps("agent-harness", profiles)
        self.assertEqual(
            [step["name"] for step in steps],
            ["agent-harness-test", "diff-check"],
        )
        self.assertIn("dashboard", profiles["profiles"])
        self.assertIn("cross-stack", profiles["profiles"])
        self.assertIn("release", profiles["profiles"])


class ScopeTests(unittest.TestCase):
    def test_dot_prefixed_repository_paths_are_not_rewritten(self) -> None:
        self.assertTrue(
            slice_module.path_allowed(
                ".github/workflows/ci.yml", [".github/workflows/**"]
            )
        )
        self.assertFalse(
            slice_module.path_allowed(
                ".github/workflows/ci.yml", ["github/workflows/**"]
            )
        )

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="sledtrace-slice-test-")
        self.repo = Path(self.temp_dir.name)
        run_git(self.repo, "init", "-q")
        run_git(self.repo, "config", "user.email", "test@sledtrace.local")
        run_git(self.repo, "config", "user.name", "SledTrace Test")
        (self.repo / "dashboard/web/src").mkdir(parents=True)
        (self.repo / "docs/ai-context").mkdir(parents=True)
        (self.repo / "dashboard/web/src/app.ts").write_text(
            "export {};\n", encoding="utf-8"
        )
        (self.repo / "docs/ai-context/CURRENT_TASK.md").write_text(
            task_text(["dashboard/web/src/**", "docs/ai-context/CURRENT_TASK.md"]),
            encoding="utf-8",
        )
        run_git(self.repo, "add", ".")
        run_git(self.repo, "commit", "-qm", "fixture")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_scope(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SLICE_PATH),
                "--repo-root",
                str(self.repo),
                "scope",
            ],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_allowed_scope_passes(self) -> None:
        (self.repo / "dashboard/web/src/app.ts").write_text(
            "export const value = 1;\n", encoding="utf-8"
        )
        result = self.run_scope()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[OK] dashboard/web/src/app.ts", result.stdout)

    def test_deliberate_scope_violation_fails(self) -> None:
        (self.repo / "collector").mkdir()
        (self.repo / "collector/outside.go").write_text(
            "package collector\n", encoding="utf-8"
        )
        result = self.run_scope()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[VIOLATION] collector/outside.go", result.stdout)
        self.assertIn("FAIL: 1 path(s)", result.stdout)


class RepositoryInstructionTests(unittest.TestCase):
    def test_skill_structure_and_copilot_pointer(self) -> None:
        expected = {
            "sledtrace-slice": "sledtrace-slice",
            "sledtrace-review": "sledtrace-review",
        }
        for folder, expected_name in expected.items():
            skill = REPO_ROOT / ".agents/skills" / folder / "SKILL.md"
            metadata = slice_module.parse_frontmatter(skill.read_text(encoding="utf-8"))
            self.assertEqual(metadata["name"], expected_name)
            self.assertTrue(metadata["description"])

        copilot = (REPO_ROOT / ".github/copilot-instructions.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(".agents/skills/sledtrace-review/SKILL.md", copilot)

    def test_existing_ci_jobs_and_slice_contract_job_remain_present(self) -> None:
        workflow = (REPO_ROOT / ".github/workflows/ci.yml").read_text(
            encoding="utf-8"
        )
        for job in ("python:", "collector:", "dashboard:", "slice-contract:"):
            self.assertIn(job, workflow)
        self.assertIn("python scripts/dev/slice.py status", workflow)
        self.assertIn("python scripts/dev/test_slice.py -v", workflow)


if __name__ == "__main__":
    unittest.main()
