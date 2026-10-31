from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.agent import cycle, remediation
from local_release.core import atomic_json, capture, git, install_local_excludes, read_json


class AgentTest(unittest.TestCase):
    def test_remediation_distinguishes_a_delivered_repair_from_a_retried_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            atomic_json(directory / "job.json", {"sha": "a" * 40, "preparation_revision": 14})
            result = {"status": "pending", "error": "unsquashfs probe exited 1", "runtime_revision": 14,
                      "attempt_runtime_revision": 13, "pending_runtime_revision": 14}
            atomic_json(directory / "results/linux.json", result)
            remediation(directory, {})
            self.assertTrue(read_json(directory / "results/linux-remediation.json")["runtime_update_ready"])
            result.update(status="failed", attempt_runtime_revision=14)
            result.pop("pending_runtime_revision")
            atomic_json(directory / "results/linux.json", result)
            remediation(directory, {})
            self.assertFalse(read_json(directory / "results/linux-remediation.json")["runtime_update_ready"])

    def test_dispatcher_continues_projects_in_order_and_selects_linux_profiles(self):
        with tempfile.TemporaryDirectory() as folder:
            registry = Path(folder) / "registry.json"
            projects = {name: {"hosts": hosts, "enabled": True, "cursor": "before"}
                        for name, hosts in (("second", ["linux"]), ("first", ["linux"]), ("windows-only", ["windows"]))}
            atomic_json(registry, {"schema": 1, "projects": projects})
            calls = []
            def runner(project, role):
                index = "first" if project is projects["first"] else "second"
                # Registry JSON objects are reloaded, so use stable ordering count.
                calls.append(role)
                if len(calls) == 1:
                    raise RuntimeError("first build failed")
                project["cursor"] = "after"
                return [{"status": "built"}]
            report = cycle(registry, "linux", runner=runner)
            self.assertEqual(calls, ["linux", "linux"])
            self.assertEqual(list(report["projects"]), ["first", "second"])
            self.assertEqual(report["status"], "finished_with_errors")
            self.assertEqual(read_json(registry)["projects"]["second"]["cursor"], "after")

    def test_generated_state_stays_ignored_on_a_branch_without_gitignore_rules(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            capture(["git", "init", repo])
            git(repo, "config", "user.name", "Fixture")
            git(repo, "config", "user.email", "fixture@example.invalid")
            (repo / "source").write_text("baseline")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "baseline")
            install_local_excludes(repo)
            for name in (".local-releases/private/job.json", "third_party/plugin/.gradle/8/cache.bin"):
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"generated")
            self.assertEqual(git(repo, "status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
