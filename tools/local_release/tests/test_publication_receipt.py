from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, read_json
from local_release.github import reconcile_published


class PublicationReceiptTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / "releases/fixture/1.0.0+1" / ("a" * 40)
        self.job = {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture", "repository": "owner/repo",
            "version": "1.0.0", "build": 1, "tag": "v1.0.0+1", "source_bundle_sha256": "b" * 64,
            "compile_defines_sha256": "c" * 64, "artifacts": ["linux.tar.gz"],
            "required_steps": {"windows": ["integration-web"], "linux": ["verify-linux"]}}
        atomic_json(self.directory / "job.json", self.job)
        atomic_json(self.directory / "publication.json", {"release_id": 1, "published": False})
        self.context = Context(self.directory, {}, host="linux")
        self.summary = {key: self.job[key] for key in ("run_id", "sha", "version", "build", "tag", "source_bundle_sha256", "compile_defines_sha256")}
        self.summary.update(verified_gates=deepcopy(self.job["required_steps"]), packages={"linux.tar.gz": {
            "sha256": hashlib.sha256(b"package").hexdigest(), "size": 7}})
        self.release = {"id": 1, "draft": False, "tag_name": self.job["tag"], "body": "<!-- local-release:fixture-a -->",
                        "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0+1"}

    def run_receipt(self, changed_digest=False):
        manifest = json.dumps(self.summary).encode()
        package = self.summary["packages"]["linux.tar.gz"]
        sums = (package["sha256"] + "  linux.tar.gz\n").encode()
        assets = [
            {"id": 2, "name": "release-manifest.json", "size": len(manifest), "browser_download_url": "https://example.invalid/2"},
            {"id": 3, "name": "linux.tar.gz", **package, "digest": "sha256:" + ("f" * 64 if changed_digest else package["sha256"]), "browser_download_url": "https://example.invalid/3"},
            {"id": 4, "name": "SHA256SUMS", "size": len(sums), "digest": "sha256:" + hashlib.sha256(sums).hexdigest(), "browser_download_url": "https://example.invalid/4"},
        ]
        def download(asset, path):
            self.assertEqual(asset["name"], "release-manifest.json")
            path.write_bytes(manifest)
            return hashlib.sha256(manifest).hexdigest()
        with patch("local_release.github.credential", return_value="fixture"), patch("local_release.github.GitHub") as api:
            api.return_value.request.return_value = self.release
            api.return_value.tag_sha.return_value = self.job["sha"]
            api.return_value.pages.return_value = assets
            api.return_value.download_asset.side_effect = download
            return reconcile_published(self.context)

    def test_peer_recognizes_completed_release_without_transport_or_fabricated_checkpoints(self):
        original = {"sha": self.job["sha"], "run_id": self.job["run_id"], "host": "windows", "status": "incomplete", "steps": {}}
        atomic_json(self.directory / "results/windows.json", original)
        self.assertTrue(self.run_receipt())
        self.assertTrue(read_json(self.directory / "publication.json")["published"])
        self.assertEqual(read_json(self.directory / "results/windows.json"), original)
        self.assertFalse((self.context.output / "linux.tar.gz").exists())  # No duplicate package download.
        self.assertTrue((self.directory / "results/publication-received.json").exists())

    def test_draft_changed_package_or_missing_gates_never_close_the_local_job(self):
        self.release["draft"] = True
        self.assertFalse(self.run_receipt())
        self.release["draft"] = False
        with self.assertRaisesRegex(ReleaseError, "package metadata"):
            self.run_receipt(changed_digest=True)
        self.summary["verified_gates"]["windows"] = []
        with self.assertRaisesRegex(ReleaseError, "omits required"):
            self.run_receipt()
        self.assertFalse(read_json(self.directory / "publication.json")["published"])
