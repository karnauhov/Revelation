from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.agent import cycle, remediation, project_cycle
from local_release.core import atomic_json, capture, git, install_local_excludes, read_json


class AgentTest(unittest.TestCase):
    def test_linux_skips_a_release_completed_elsewhere_after_exchange_files_are_gone(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            profile, config = root / "profile.json", root / "config.json"
            atomic_json(profile, {"project": "fixture"})
            atomic_json(config, {})
            directory = root / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(directory / "job.json", {"schema": 1, "sha": "a" * 40, "project": "fixture",
                "run_id": "fixture-a", "version": "1.0.0", "build": 1})
            atomic_json(directory / "publication.json", {"published": False, "release_id": 1})
            project = {"project": "fixture", "profile": str(profile), "config": str(config), "catalogue": str(root), "repo": str(root)}
            with patch("local_release.agent.update_main"), patch("local_release.agent.discover_jobs", return_value="a" * 40), \
                    patch("local_release.retention.synchronize"), \
                    patch("local_release.transport.receive_jobs", return_value=[]), \
                    patch("local_release.github.reconcile_published", return_value=True), \
                    patch("local_release.agent.execute_prepared") as run:
                records = project_cycle(project, "linux")
                run.assert_not_called()
            self.assertEqual(records, [{"run_id": "fixture-a", "status": "published"}])

    def test_linux_applies_tombstones_before_receiving_or_starting_builds(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            profile, config = root / 'profile.json', root / 'config.json'
            atomic_json(profile, {'project': 'fixture'})
            atomic_json(config, {})
            directory = root / 'releases/fixture/1.0.0+1' / ('a' * 40)
            atomic_json(directory / 'job.json', {'schema': 1, 'sha': 'a' * 40})
            project = {'project': 'fixture', 'profile': str(profile), 'config': str(config), 'catalogue': str(root), 'repo': str(root)}
            order = []
            def cleanup(*args):
                order.append('delete')
                atomic_json(root / 'deletions/fixture' / ('a' * 40 + '.json'), {'confirmed': True})
            def receive(*args):
                order.append('receive')
                return [directory]
            with patch('local_release.agent.update_main'), patch('local_release.retention.synchronize', side_effect=cleanup), \
                    patch('local_release.transport.receive_jobs', side_effect=receive), \
                    patch('local_release.agent.discover_jobs', return_value='a' * 40), \
                    patch('local_release.agent.execute_prepared') as run:
                self.assertEqual(project_cycle(project, 'linux'), [])
                run.assert_not_called()
            self.assertEqual(order, ['delete', 'receive'])

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
