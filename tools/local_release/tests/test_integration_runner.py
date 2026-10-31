from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json
from local_release.profiles.revelation import integration_files
from local_release.profiles.revelation import prepare_android_fixture


class IntegrationRunnerTest(unittest.TestCase):
    def test_binary_sqlite_fixtures_use_exec_in_instead_of_windows_text_shell(self):
        from local_release.core import digest, read_json
        from local_release.native_fixture import MODULES
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {"android_sdk": folder, "android_avd_name": "fixture-avd"}, host="windows")
            sources = {}
            for name in MODULES:
                source = ctx.workspace / "web/db" / name
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(b"SQLite format 3\x00\r\n\x1a\x00" + bytes(range(256)))
                sources[name] = source
            copied = []
            def command(argv, **kwargs):
                argv = [str(arg) for arg in argv]
                if "exec-in" in argv:
                    self.assertEqual(argv[3:8], ["exec-in", "run-as", "ai11.link.revelation", "sh", "-c"])
                    self.assertEqual(kwargs["stdin"].read(), sources[Path(argv[-1]).name].read_bytes())
                    copied.append(Path(argv[-1]).name)
                if argv[-1] == "name":
                    return "fixture-avd\nOK"
                if "sha256sum" in argv[-1]:
                    return digest(sources[Path(argv[-1]).name]) + "  fixture.sqlite"
                return ""
            with patch("local_release.profiles.android_release.dependencies"), patch.object(ctx, "command", side_effect=command):
                prepare_android_fixture(ctx, "emulator-5584")
            self.assertEqual(copied, list(MODULES))
            self.assertEqual(set(read_json(job / "results/android-fixtures.json")["module_sha256"]), set(MODULES))

    def test_every_file_including_smoke_runs_and_retry_preserves_passed_files(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {}, host="windows")
            for name in ("a_test.dart", "b_test.dart", "smoke/startup_test.dart"):
                test = ctx.workspace / "integration_test" / name
                test.parent.mkdir(parents=True, exist_ok=True)
                test.write_text("fixture")
            calls = []
            def first(test):
                calls.append(test.name)
                if test.name == "b_test.dart":
                    raise ReleaseError("device failed")
            with self.assertRaisesRegex(ReleaseError, "device failed"):
                integration_files(ctx, "windows", first)
            resumed = Context(job, {}, host="windows")
            records = integration_files(resumed, "windows", lambda test: calls.append(test.name))
            self.assertEqual(calls, ["a_test.dart", "b_test.dart", "b_test.dart", "startup_test.dart"])
            self.assertEqual(len(records), 3)
            self.assertTrue(any(path.startswith("integration_test/smoke/") for path in records))


if __name__ == "__main__":
    unittest.main()
