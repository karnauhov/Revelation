from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError, atomic_json, digest, read_json
from local_release.runtime_update import install


class RuntimeInvalidationTest(unittest.TestCase):
    def test_audited_acceptance_repair_preserves_build_test_and_package_checkpoints(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            job, incoming = root / "job", root / "incoming"
            recipe = "local_release/profiles/linux_release.py"
            for target, content in ((job, "old acceptance"), (incoming, "new acceptance")):
                (target / "runtime" / recipe).parent.mkdir(parents=True)
                (target / "runtime" / recipe).write_text(content)
            old = {"project": "fixture", "sha": "a" * 40, "run_id": "fixture-a", "schema": 1,
                "preparation_revision": 14, "required_steps": {"linux": ["linux", "snap", "integration-linux", "verify-linux", "publish-proof"]},
                "step_dependencies": {"publish-proof": ["verify-linux"]},
                "runtime_sha256": {recipe: digest(job / "runtime" / recipe)}}
            new = {**deepcopy(old), "preparation_revision": 15,
                "runtime_sha256": {recipe: digest(incoming / "runtime" / recipe)},
                "tooling_changes": [{"reason": "Only install/smoke acceptance changed", "invalidate_steps": {"linux": ["verify-linux"]}}]}
            atomic_json(job / "job.json", old)
            atomic_json(incoming / "job.json", new)
            envelope = {"previous_job_sha256": digest(job / "job.json"), "job_sha256": digest(incoming / "job.json"),
                "invalidate_steps": {"linux": ["verify-linux"]}}
            atomic_json(incoming / "runtime-update.json", envelope)
            steps = {name: {"status": "passed", "outputs": {}} for name in old["required_steps"]["linux"]}
            atomic_json(job / "results/linux.json", {"status": "failed", "runtime_revision": 14, "steps": steps})
            package = job / "packages/test.snap"
            package.parent.mkdir()
            package.write_bytes(b"keep the real package")
            install(job, incoming)
            result = read_json(job / "results/linux.json")
            self.assertEqual(set(result["steps"]), {"linux", "snap", "integration-linux"})
            self.assertEqual(result["attempt_runtime_revision"], 14)
            self.assertEqual(result["pending_runtime_revision"], 15)
            self.assertEqual(package.read_bytes(), b"keep the real package")
            self.assertEqual(read_json(job / "job.json")["required_steps"], old["required_steps"])

    def test_audited_snap_rebuild_demotes_only_its_package_and_preserves_remote_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            job, incoming = root / "job", root / "incoming"
            recipe = "local_release/profiles/linux_release.py"
            for target in (job, incoming):
                (target / "runtime" / recipe).parent.mkdir(parents=True)
                (target / "runtime" / recipe).write_text(target.name)
            old = {"schema": 1, "sha": "a" * 40, "preparation_revision": 14,
                "required_steps": {"linux": ["snap", "inspect-snap", "verify-linux", "linux-tar", "integration-linux"]},
                "step_dependencies": {"inspect-snap": ["snap"], "verify-linux": ["snap", "inspect-snap"]},
                "runtime_sha256": {recipe: digest(job / "runtime" / recipe)}}
            new = {**deepcopy(old), "preparation_revision": 15,
                "runtime_sha256": {recipe: digest(incoming / "runtime" / recipe)},
                "tooling_changes": [{"invalidate_steps": {"linux": ["snap"]}}]}
            atomic_json(job / "job.json", old)
            atomic_json(incoming / "job.json", new)
            atomic_json(incoming / "runtime-update.json", {"previous_job_sha256": digest(job / "job.json"),
                "job_sha256": digest(incoming / "job.json"), "invalidate_steps": {"linux": ["snap"]}})
            package = job / "packages/test.snap"
            package.parent.mkdir()
            package.write_bytes(b"original package still in the owned draft")
            record = {"path": "packages/test.snap", "sha256": digest(package), "source_asset_id": 123, "size": package.stat().st_size}
            atomic_json(job / "manifest.json", {"packages": {"test.snap": record}, "status": "incomplete"})
            steps = {name: {"status": "passed", "outputs": {}} for name in old["required_steps"]["linux"]}
            steps["snap"]["outputs"] = {"packages/test.snap": digest(package)}
            atomic_json(job / "results/linux.json", {"runtime_revision": 14, "status": "failed", "steps": steps})
            install(job, incoming)
            result = read_json(job / "results/linux.json")
            self.assertEqual(set(result["steps"]), {"linux-tar", "integration-linux"})
            manifest = read_json(job / "manifest.json")
            self.assertNotIn("test.snap", manifest["packages"])
            self.assertEqual(manifest["unverified_packages"]["test.snap"]["source_asset_id"], 123)
            self.assertEqual(digest(package), record["sha256"])

    def test_overlay_change_cannot_preserve_old_builds_with_a_scoped_repair(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            job, incoming = root / "job", root / "incoming"
            old = {"schema": 1, "sha": "a" * 40, "preparation_revision": 1,
                "required_steps": {"linux": ["verify-linux"]}, "runtime_sha256": {}, "generated_source_overlays": {"recipe": "old"}}
            new = {**deepcopy(old), "preparation_revision": 2, "generated_source_overlays": {"recipe": "new"},
                "tooling_changes": [{"invalidate_steps": {"linux": ["verify-linux"]}}]}
            atomic_json(job / "job.json", old)
            atomic_json(incoming / "job.json", new)
            atomic_json(incoming / "runtime-update.json", {"previous_job_sha256": digest(job / "job.json"),
                "job_sha256": digest(incoming / "job.json"), "invalidate_steps": {"linux": ["verify-linux"]}})
            with self.assertRaisesRegex(ReleaseError, "overlay change"):
                install(job, incoming)
            self.assertEqual(read_json(job / "job.json"), old)
