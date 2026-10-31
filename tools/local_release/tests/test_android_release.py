from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, read_json
from local_release.profiles.android_release import dependencies, recover_cache


class AndroidPathsTest(unittest.TestCase):
    def test_detached_alias_is_repaired_before_gradle_without_deleting_packages(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {}, host="windows")
            plugin = ctx.workspace / "third_party/fixture_plugin"
            plugin.mkdir(parents=True)
            package = ctx.output / "already-signed.apk"
            package.write_bytes(b"preserve these signed bytes")
            index = ctx.workspace / ".flutter-plugins-dependencies"
            atomic_json(index, {"plugins": {"android": [{"name": "fixture_plugin", "path": str(ctx.root / "detached/plugin")}]}})
            ctx.result["steps"]["android-cache-recovery"] = {"status": "failed", "started": 1, "finished": 2}
            calls = []
            def command(argv, **kwargs):
                calls.append((argv, kwargs["cwd"]))
                if argv == ["flutter", "pub", "get"]:
                    atomic_json(index, {"plugins": {"android": [{"name": "fixture_plugin", "path": str(plugin)}]}})
            with patch.object(ctx, "command", side_effect=command):
                recover_cache(ctx)
                dependencies(ctx)
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][1], ctx.workspace)
            self.assertEqual(calls[1], ([ctx.workspace / "android/gradlew.bat", "help", "--offline"], ctx.workspace / "android"))
            self.assertEqual(package.read_bytes(), b"preserve these signed bytes")
            proof = read_json(job / "results/windows-android-cache-recovery.json")
            self.assertEqual(proof["previous_attempt"]["status"], "failed")
            self.assertEqual(ctx.result["steps"]["android-cache-recovery"]["status"], "passed")

    def test_missing_plugin_after_pub_get_is_a_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {}, host="windows")
            ctx.workspace.mkdir(parents=True)
            with patch.object(ctx, "command"):
                with self.assertRaisesRegex(ReleaseError, "plugin paths"):
                    dependencies(ctx)
