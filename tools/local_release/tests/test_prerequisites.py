from contextlib import contextmanager
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, digest
from local_release import prerequisites as prerequisites


class PrerequisitesTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        job = Path(temporary.name) / "releases/fixture/1+1" / ("a" * 40)
        atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
        self.ctx = Context(job, {"android_sdk": temporary.name, "android_device": "emulator-5584",
            "android_avd_name": "fixture-owned", "adb_server_port": 5041}, host="windows")

    def test_phone_global_adb_and_occupied_emulator_are_never_touched(self):
        for field, value in [("android_device", "owner-phone"), ("adb_server_port", 5037)]:
            config = self.ctx.config.copy()
            with self.subTest(field=field), patch.object(self.ctx, "command") as command:
                self.ctx.config[field] = value
                with self.assertRaisesRegex(ReleaseError, "isolated AVD"):
                    with prerequisites.android_device(self.ctx):
                        self.fail("unsafe fixture accepted")
                command.assert_not_called()
            self.ctx.config = config
        with patch.object(self.ctx, "command", return_value="List of devices attached"), \
                patch.object(prerequisites, "port_free", return_value=False):
            with self.assertRaisesRegex(ReleaseError, "ports are occupied"):
                with prerequisites.android_device(self.ctx):
                    self.fail("occupied port accepted")

    def test_borrowed_matching_avd_is_never_stopped_and_other_avd_is_refused(self):
        for name in ["fixture-owned", "someone-else"]:
            commands = []
            def invoke(argv, **kwargs):
                commands.append(argv)
                return "emulator-5584 device" if argv[-1] == "devices" else name + "\nOK"
            with self.subTest(name=name), patch.object(self.ctx, "command", side_effect=invoke), \
                    patch.object(prerequisites, "child") as child:
                if name == "fixture-owned":
                    with prerequisites.android_device(self.ctx):
                        pass
                else:
                    with self.assertRaisesRegex(ReleaseError, "another AVD"):
                        with prerequisites.android_device(self.ctx):
                            self.fail("foreign AVD accepted")
                child.assert_not_called()
            self.assertFalse(any("kill" in command for command in commands))

    def test_owned_avd_closes_after_test_failure_and_restores_environment(self):
        environment = self.ctx.env.copy()
        commands = []
        def invoke(argv, **kwargs):
            commands.append(argv)
            return "fixture-owned\nOK" if argv[-1] == "name" else ""
        process = Mock()
        @contextmanager
        def launch(ctx, argv, label):
            self.assertIn("-no-window", argv)
            self.assertIn("-read-only", argv)
            yield process
        with patch.object(self.ctx, "command", side_effect=invoke), \
                patch.object(prerequisites, "port_free", return_value=True), \
                patch.object(prerequisites, "child", side_effect=launch), \
                patch.object(prerequisites, "wait_ready"):
            with self.assertRaisesRegex(RuntimeError, "fixture failure"):
                with prerequisites.android_device(self.ctx):
                    self.assertEqual(self.ctx.env["ADB_SERVER_SOCKET"], "tcp:127.0.0.1:5041")
                    raise RuntimeError("fixture failure")
        self.assertEqual(commands[-1][-2:], ["emu", "kill"])
        self.assertEqual(self.ctx.env, environment)

    def test_driver_checksum_and_occupied_port_preserve_other_browser_sessions(self):
        driver = self.ctx.directory / "driver.exe"
        driver.write_bytes(b"approved driver")
        self.ctx.config.update(chromedriver_path=str(driver), chromedriver_port=9517, chromedriver_sha256=digest(driver))
        with patch.object(prerequisites, "port_free", return_value=False), patch.object(prerequisites, "child") as child:
            with self.assertRaisesRegex(ReleaseError, "dedicated port"):
                with prerequisites.chrome_driver(self.ctx):
                    self.fail("occupied port accepted")
            child.assert_not_called()
        driver.write_bytes(b"changed binary")
        with self.assertRaisesRegex(ReleaseError, "digest differs"):
            with prerequisites.chrome_driver(self.ctx):
                self.fail("changed binary accepted")

    def test_hidden_owned_child_is_closed_after_failure(self):
        child = None
        with self.assertRaisesRegex(RuntimeError, "fixture failure"):
            with prerequisites.child(self.ctx, [sys.executable, "-c", "import time; time.sleep(30)"], "fixture") as child:
                raise RuntimeError("fixture failure")
        self.assertIsNotNone(child.poll())
