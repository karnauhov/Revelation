from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json
from local_release.profiles.revelation import integration_files


class IntegrationRunnerTest(unittest.TestCase):
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
