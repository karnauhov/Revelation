from copy import deepcopy
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, digest, read_json
from local_release.processes import JobStopped
from local_release.profiles import snap_acceptance as snap


class SnapAcceptanceTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.job = Path(temporary.name) / "releases/fixture/1.0.0+1" / ("a" * 40)
        atomic_json(self.job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture",
            "version": "1.0.0", "build": 1, "artifacts": ["fixture.snap"]})
        self.ctx = Context(self.job, {}, host="linux")
        self.home = Path(temporary.name) / "home"
        home = patch.object(Path, "home", return_value=self.home)
        home.start()
        self.addCleanup(home.stop)
        self.ctx.env["DISPLAY"] = ":fixture"
        package = self.ctx.output / "fixture.snap"
        package.write_bytes(b"exact inspected package")
        self.expected = digest(package)
        atomic_json(self.job / "results/linux-snap-package.json", {"sha256": self.expected})
        self.before = {"version": "0.9.0", "revision": "42", "tracking": "latest/stable", "sha256": "old-package"}
        self.current = deepcopy(self.before)
        self.calls = []
        self.real_authorize = snap.authorize
        self.real_installed = snap.installed
        for target, kwargs in (("local_release.native_fixture.application_running", {"return_value": False}),
                               (snap.__name__ + ".authorize", {}),
                               (snap.__name__ + ".installed", {"side_effect": lambda ctx: deepcopy(self.current)}),
                               (snap.__name__ + ".privileged", {"side_effect": self.command})):
            mock = patch(target, **kwargs)
            mock.start()
            self.addCleanup(mock.stop)

    def command(self, ctx, *args):
        self.calls.append(args)
        if args[0] == "save":
            return "Set Snap Age Version Rev Size Notes\n7 revelation-x 0s 0.9.0 42 10kB -\n"
        if args[0] == "install":
            self.current = {"version": "1.0.0.1", "revision": "x1", "tracking": "latest/stable", "sha256": self.expected}
        elif args[0] == "revert":
            self.current = deepcopy(self.before)
        elif args[:2] == ("remove", "--purge"):
            self.current = None
        return "ok"

    def test_exact_package_is_smoked_and_original_revision_data_are_restored(self):
        with patch.object(snap, "smoke", return_value={"startup_marker": True, "alive_seconds_after_startup": 10}):
            self.ctx.stage("verify-linux", lambda: snap.acceptance(self.ctx), ["results/linux-packages.json"])
        self.assertEqual(self.current, self.before)
        self.assertIn(("revert", "revelation-x", "--revision=42"), self.calls)
        self.assertIn(("restore", "7", "revelation-x"), self.calls)
        self.assertEqual(self.calls[-1], ("forget", "7"))
        self.assertNotIn(("remove", "--purge", "revelation-x"), self.calls)
        proof = read_json(self.job / "results/linux-packages.json")
        self.assertEqual(proof["package_sha256"], self.expected)
        self.assertTrue(proof["restored"])
        self.assertNotIn("snapshot", proof)
        self.assertFalse(list(self.ctx.root.rglob("restore.json")))

    def test_failed_or_cancelled_smoke_restores_original_and_never_passes_gate(self):
        for error in (ReleaseError("startup failed"), JobStopped("cancelled")):
            with self.subTest(error=type(error).__name__), patch.object(snap, "smoke", side_effect=error):
                with self.assertRaises(type(error)):
                    self.ctx.stage("verify-linux", lambda: snap.acceptance(self.ctx))
            self.assertEqual(self.current, self.before)
            self.assertNotEqual(self.ctx.result["steps"]["verify-linux"]["status"], "passed")
            self.assertFalse((self.job / "results/linux-packages.json").exists())

    def test_clean_early_close_relaunches_without_reinstall_or_rebuild(self):
        with patch.object(snap, "smoke_once", side_effect=[snap.EarlySnapClose("closed early"),
                {"startup_marker": True, "alive_seconds_after_startup": 10}]):
            snap.verify(self.ctx)
        self.assertEqual(sum(args[0] == "install" for args in self.calls), 1)
        self.assertEqual(sum(args[0] == "save" for args in self.calls), 1)
        self.assertEqual(sum(args[0] == "revert" for args in self.calls), 1)
        self.assertEqual(self.current, self.before)
        self.assertEqual(read_json(self.job / "results/linux-packages.json")["smoke_attempts"], 2)

    def test_new_install_is_removed_but_unrelated_install_is_preserved(self):
        self.current = None
        with patch.object(snap, "smoke", return_value={"startup_marker": True}):
            snap.verify(self.ctx)
        self.assertIsNone(self.current)
        self.assertIn(("remove", "--purge", "revelation-x"), self.calls)
        self.calls.clear()
        journal = self.ctx.root / "restore.json"
        atomic_json(journal, {"name": snap.NAME, "sha": self.ctx.job["sha"], "before": None,
            "package_sha256": self.expected, "snapshot": None})
        self.current = self.before
        with self.assertRaisesRegex(ReleaseError, "unrelated"):
            snap.restore(self.ctx, journal)
        self.assertEqual(self.calls, [])
        self.assertTrue(journal.exists())

    def test_changed_package_is_rejected_before_installation(self):
        (self.ctx.output / "fixture.snap").write_bytes(b"changed after inspection")
        with self.assertRaisesRegex(ReleaseError, "bytes changed"):
            snap.acceptance(self.ctx)
        self.assertEqual(self.calls, [])

    def test_all_owner_files_including_snapshot_excluded_cache_are_restored_after_failure(self):
        root, backup = snap.data_paths(self.ctx)
        original = root / "common/.cache/owner-data.bin"
        original.parent.mkdir(parents=True)
        original.write_bytes(b"original owner bytes")
        os.utime(original, ns=(1700000000000000000, 1700000000000000000))
        original_mtime = original.stat().st_mtime_ns
        def fail(ctx):
            self.assertTrue(backup.is_dir())
            original.parent.mkdir(parents=True)
            original.write_bytes(b"temporary test data")
            raise ReleaseError("smoke failed")
        with patch.object(snap, "smoke", side_effect=fail):
            with self.assertRaisesRegex(ReleaseError, "smoke failed"):
                snap.verify(self.ctx)
        self.assertEqual(original.read_bytes(), b"original owner bytes")
        self.assertEqual(original.stat().st_mtime_ns, original_mtime)
        self.assertFalse(backup.exists())

    def test_recovery_rejects_option_injection_without_running_privileged_commands(self):
        journal = self.ctx.root / "restore.json"
        atomic_json(journal, {"name": snap.NAME, "sha": self.ctx.job["sha"], "before": self.before,
            "package_sha256": self.expected, "snapshot": "--all"})
        with self.assertRaisesRegex(ReleaseError, "invalid package/snapshot"):
            snap.restore(self.ctx, journal)
        self.assertEqual(self.calls, [])

    def test_interactive_sudo_keeps_the_desktop_terminal_and_never_pipes_password(self):
        with patch.object(os, "geteuid", return_value=1000, create=True), \
                patch.object(sys.stdin, "isatty", return_value=True), \
                patch.object(self.ctx, "command", side_effect=[ReleaseError("authentication required"), ""]) as command, \
                patch.object(subprocess, "run", return_value=subprocess.CompletedProcess(["sudo", "-v"], 0)) as authenticate:
            self.real_authorize(self.ctx)
        self.assertFalse(command.call_args.kwargs["new_session"])
        self.assertFalse(command.call_args.kwargs["cancellable"])
        self.assertEqual(authenticate.call_args.args[0], ["sudo", "-v"])
        for name in ("stdin", "stdout", "stderr", "start_new_session"):
            self.assertNotIn(name, authenticate.call_args.kwargs)

    def test_root_readable_installed_package_is_hashed_with_authenticated_sudo(self):
        expected = "a" * 64
        commands = []
        def invoke(argv, **kwargs):
            commands.append((argv, kwargs))
            if argv == ["snap", "list", "revelation-x"]:
                return "Название Версия Ревизия Канал Издатель Примечания\nrevelation-x 1.0.7.172 6 latest/stable owner -\n"
            self.assertEqual(argv, ["sudo", "-n", "sha256sum", "--", "/var/lib/snapd/snaps/revelation-x_6.snap"])
            return expected + "  /var/lib/snapd/snaps/revelation-x_6.snap\n"
        with patch.object(self.ctx, "command", side_effect=invoke), \
                patch.object(snap, "digest", side_effect=PermissionError("ordinary user cannot read installed Snap")):
            value = self.real_installed(self.ctx)
        self.assertEqual(value["sha256"], expected)
        self.assertEqual(value["revision"], "6")
        self.assertFalse(commands[-1][1]["new_session"])
        self.assertFalse(commands[-1][1]["cancellable"])

    def test_protected_checksum_rejects_invalid_revision_and_wrong_file(self):
        with patch.object(self.ctx, "command") as command:
            with self.assertRaisesRegex(ReleaseError, "invalid installed Snap revision"):
                snap.installed_revision_digest(self.ctx, "../../foreign")
            command.assert_not_called()
        with patch.object(self.ctx, "command", return_value="a" * 64 + "  /wrong/package.snap\n"):
            with self.assertRaisesRegex(ReleaseError, "checksum output is invalid"):
                snap.installed_revision_digest(self.ctx, "6")

    def test_recovery_after_interruption_precedes_another_install(self):
        folder = self.ctx.root / "w" / self.ctx.job["sha"][:12] / "snap-acceptance"
        journal = folder / "restore.json"
        atomic_json(journal, {"schema": 1, "name": snap.NAME, "sha": self.ctx.job["sha"], "before": self.before,
            "package_sha256": self.expected, "snapshot": 6, "test_revision": "x1"})
        self.current = {**self.before, "revision": "x1", "sha256": self.expected}
        with patch.object(snap, "smoke", return_value={"startup_marker": True}):
            snap.verify(self.ctx)
        self.assertEqual(self.calls[0], ("revert", "revelation-x", "--revision=42"))
        self.assertLess(self.calls.index(("restore", "6", "revelation-x")), self.calls.index(("save", "revelation-x")))
        self.assertEqual(self.current, self.before)
