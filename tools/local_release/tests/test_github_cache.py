from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import digest, ReleaseError
from local_release.github import GitHub


class GitHubReadbackCacheTest(unittest.TestCase):
    def test_only_a_durable_receipt_and_fresh_matching_digest_skip_a_second_download(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.zip"
            path.write_bytes(b"approved package")
            expected = digest(path)
            api = GitHub("owner/repo", "fixture")
            asset = {"id": 7, "name": path.name, "size": path.stat().st_size,
                "digest": "sha256:" + expected, "browser_download_url": "https://example.invalid/7"}
            release = {"id": 1}
            with patch.object(api, "pages", return_value=[asset]), patch.object(api, "download_asset", return_value=expected) as download:
                api.upload_verified(release, path)
                download.assert_called_once()  # The initial receipt still requires real read-back.
            api.verified_assets = {7: {"sha256": expected, "size": path.stat().st_size}}
            with patch.object(api, "pages", return_value=[asset]), patch.object(api, "download_asset") as download:
                self.assertEqual(api.upload_verified(release, path)["sha256"], expected)
                download.assert_not_called()
            asset["digest"] = "sha256:" + "f" * 64
            with patch.object(api, "pages", return_value=[asset]), patch.object(api, "download_asset", return_value="f" * 64):
                with self.assertRaisesRegex(ReleaseError, "digest mismatch"):
                    api.upload_verified(release, path)
