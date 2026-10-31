from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, git, read_json
from local_release.profiles.revelation import integration_files
from local_release.profiles.revelation import prepare_android_fixture, wait_android_fixture
from local_release.profiles.revelation import integration
from local_release.profiles.revelation import web_integration_target


class IntegrationRunnerTest(unittest.TestCase):
    def test_historical_web_tools_assertions_are_platform_correct_and_audited(self):
        source = git(Path(__file__).resolve().parents[3], "show",
                     "abd9d33f77b837940f03eaaec430a9568adf3f6e:integration_test/smoke/about_download_navigation_smoke_test.dart") + "\n"
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {}, host="windows")
            test = ctx.workspace / "integration_test/smoke/about_download_navigation_smoke_test.dart"
            test.parent.mkdir(parents=True)
            test.write_text(source, encoding="utf-8")
            web_integration_target(ctx, test)
            evidence = read_json(job / "results/windows-web-driver-targets.json")[test.relative_to(ctx.workspace).as_posix()]
            copied = ctx.workspace / evidence["test_compatibility"]["target"]
            contents = copied.read_text()
            self.assertIn("kIsWeb ? findsNothing : findsOneWidget", contents)
            self.assertIn("expect(find.text(l10n.clear_cache), findsOneWidget)", contents)
            self.assertEqual(test.read_text(), source)
            test.write_text(source + "// changed scenario\n", encoding="utf-8")
            web_integration_target(ctx, test)
            changed = read_json(job / "results/windows-web-driver-targets.json")[test.relative_to(ctx.workspace).as_posix()]
            self.assertNotIn("test_compatibility", changed)

    def test_web_widget_targets_get_the_driver_bridge_without_editing_or_skipping_tests(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {}, host="windows")
            target = ctx.workspace / "integration_test/smoke/startup_test.dart"
            target.parent.mkdir(parents=True)
            original = "void main() { TestWidgetsFlutterBinding.ensureInitialized(); testWidgets('critical startup', check); }"
            target.write_text(original)
            wrapper = ctx.workspace / web_integration_target(ctx, target)
            contents = wrapper.read_text()
            self.assertLess(contents.index("IntegrationTestWidgetsFlutterBinding.ensureInitialized()"), contents.index("scenario.main()"))
            self.assertIn("../../integration_test/smoke/startup_test.dart", contents)
            self.assertIn("previousReporter(details, description)", contents)
            self.assertIn("Failure(description, '${details.exception}\\n${details.stack}')", contents)
            self.assertEqual(target.read_text(), original)
            target.write_text("void main() { IntegrationTestWidgetsFlutterBinding.ensureInitialized(); }")
            self.assertEqual(web_integration_target(ctx, target), "integration_test/smoke/startup_test.dart")

    def test_android_files_keep_seeded_data_between_flutter_processes(self):
        from contextlib import nullcontext
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {"integration_targets": ["android"], "android_device": "emulator-5584"}, host="windows")
            for name in ["first_test.dart", "second_test.dart"]:
                test = ctx.workspace / "integration_test" / name
                test.parent.mkdir(parents=True, exist_ok=True)
                test.write_text("fixture")
            with patch("local_release.prerequisites.android_device", return_value=nullcontext()), \
                    patch("local_release.profiles.revelation.prepare_android_fixture") as seed, patch.object(ctx, "command") as command:
                integration(ctx)
                seed.assert_called_once()
                self.assertEqual(command.call_count, 2)
                self.assertTrue(all("--no-uninstall" in call.args[0] for call in command.call_args_list))
            self.assertEqual(ctx.result["steps"]["integration-android"]["status"], "passed")

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
                if "wc -c" in argv[-1]:
                    return str(sources[Path(argv[-1]).name].stat().st_size) + " fixture.sqlite"
                return ""
            with patch("local_release.profiles.android_release.dependencies"), patch.object(ctx, "command", side_effect=command):
                prepare_android_fixture(ctx, "emulator-5584")
            self.assertEqual(copied, list(MODULES))
            self.assertEqual(set(read_json(job / "results/android-fixtures.json")["module_sha256"]), set(MODULES))

    def test_exec_in_return_does_not_hash_a_partially_written_database(self):
        from local_release.core import digest
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "fixture.sqlite"
            source.write_bytes(b"SQLite\x1a\x00data")
            ctx = unittest.mock.Mock()
            ctx.command.side_effect = ["4 remote.sqlite", str(source.stat().st_size) + " remote.sqlite", digest(source) + " remote.sqlite"]
            with patch("local_release.profiles.revelation.time.sleep"):
                self.assertEqual(wait_android_fixture(ctx, "adb", "emulator-5584", source, "remote.sqlite"), digest(source))
            self.assertNotIn("sha256sum", ctx.command.call_args_list[0].args[0][-1])
            self.assertIn("sha256sum", ctx.command.call_args_list[-1].args[0][-1])

    def test_complete_but_corrupt_database_never_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "fixture.sqlite"
            source.write_bytes(b"SQLite\x1a\x00data")
            ctx = unittest.mock.Mock()
            ctx.command.side_effect = [str(source.stat().st_size) + " remote.sqlite", "f" * 64 + " remote.sqlite"]
            with self.assertRaisesRegex(ReleaseError, "digest mismatch after complete"):
                wait_android_fixture(ctx, "adb", "emulator-5584", source, "remote.sqlite")

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
