"""Exercise real child exits and cancellation without a Snap/desktop dependency."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, read_json
from local_release.processes import JobStopped
from local_release.profiles import snap_acceptance as snap


class SnapSmokeTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / "releases/fixture/1.0.0+1" / ("a" * 40)
        atomic_json(self.directory / "job.json", {"schema": 1, "sha": "a" * 40,
            "run_id": "fixture-a", "project": "fixture", "version": "1.0.0", "build": 1})
        self.ctx = Context(self.directory, {}, host="linux")
        self.ctx.workspace.mkdir(parents=True)
        self.output = StringIO()
        self.processes = []
        self.addCleanup(self.cleanup_children)
        self.commands = []
        self.popen = subprocess.Popen
        for name, value in (("SMOKE_ALIVE_SECONDS", .6), ("SMOKE_TIMEOUT_SECONDS", 3)):
            mock = patch.object(snap, name, value)
            mock.start()
            self.addCleanup(mock.stop)

    def run_children(self, scripts):
        def launch(command, **kwargs):
            if command[0] != "snap":
                return self.popen(command, **kwargs)
            self.commands.append(command)
            child = self.popen([sys.executable, "-u", "-c", scripts[len(self.processes)]], **kwargs)
            self.processes.append(child)
            return child
        with patch.object(snap.subprocess, "Popen", side_effect=launch), redirect_stdout(self.output):
            return snap.smoke(self.ctx)

    def cleanup_children(self):
        for child in self.processes:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)
            if child.stdout and not child.stdout.closed:
                child.stdout.close()

    def report(self):
        return read_json(self.directory / "results/linux-snap-smoke.json")

    def assert_children_closed(self):
        self.assertTrue(self.processes)
        self.assertTrue(all(child.poll() is not None and child.stdout.closed for child in self.processes))

    def test_success_waits_then_closes_only_its_child_and_shows_instructions(self):
        proof = self.run_children(["import time; print('Started on TargetPlatform.linux'); time.sleep(20)"])
        self.assertEqual(proof["smoke_attempts"], 1)
        self.assertGreaterEqual(self.report()["attempts"][0]["elapsed_seconds"], .6)
        self.assertIsNone(self.report()["attempts"][0]["exit_code_before_cleanup"])
        self.assertIn("Не закрывайте окно", self.output.getvalue())
        self.assertIn("автоматического закрытия", self.output.getvalue())
        self.assertEqual(self.commands[0][:4], ["snap", "run", "--shell", snap.NAME])
        self.assert_children_closed()

    def test_manual_clean_close_retries_only_launch_and_keeps_the_full_gate(self):
        proof = self.run_children(["print('Started on TargetPlatform.linux')",
            "import time; print('Started on TargetPlatform.linux'); time.sleep(20)"])
        report = self.report()
        self.assertEqual([a["status"] for a in report["attempts"]], ["closed_early", "passed"])
        self.assertEqual(report["attempts"][0]["exit_code_before_cleanup"], 0)
        self.assertEqual(proof["smoke_attempts"], 2)
        self.assertGreaterEqual(report["attempts"][1]["elapsed_seconds"], .6)
        self.assertIn("Повторяю только запуск", self.output.getvalue())
        self.assert_children_closed()

    def test_repeated_early_close_stays_incomplete_with_clear_reason(self):
        with self.assertRaisesRegex(ReleaseError, "closed normally twice"):
            self.run_children(["print('Started on TargetPlatform.linux')"] * 2)
        self.assertEqual(self.report()["status"], "incomplete")
        self.assertEqual(len(self.processes), 2)
        self.assert_children_closed()

    def test_abnormal_exit_and_fatal_output_are_not_retried(self):
        for script, reason in [
            ("import sys; print('Started on TargetPlatform.linux'); sys.exit(3)", "exit=3"),
            ("print('Started on TargetPlatform.linux'); print('FATAL startup')", "fatal startup"),
            ("pass", "startup=False"),
        ]:
            with self.subTest(reason=reason):
                self.processes.clear()
                with self.assertRaisesRegex(ReleaseError, reason):
                    self.run_children([script])
                self.assertEqual(self.report()["status"], "failed")
                self.assertEqual(len(self.processes), 1)
                self.assert_children_closed()

    def test_stop_and_missing_startup_never_pass_or_retry(self):
        request = self.directory / "stop-request.json"
        request.write_text("{}", encoding="utf-8")
        with self.assertRaises(JobStopped):
            self.run_children(["import time; print('Started on TargetPlatform.linux'); time.sleep(20)"])
        self.assertEqual(self.report()["status"], "stopped")
        self.assert_children_closed()
        request.unlink()
        self.processes.clear()
        with patch.object(snap, "SMOKE_TIMEOUT_SECONDS", .4), self.assertRaisesRegex(ReleaseError, "did not report"):
            self.run_children(["import time; time.sleep(20)"])
        self.assertEqual(self.report()["status"], "failed")
        self.assert_children_closed()
