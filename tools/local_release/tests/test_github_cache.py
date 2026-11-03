from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import digest, ReleaseError
from local_release.github import GitHub


class GitHubReadbackCacheTest(unittest.TestCase):
    def test_canonical_repository_casing_is_accepted_without_trusting_other_asset_urls(self):
        api = GitHub("owner/Tapnibbles", "fixture")
        with patch.object(api.opener, "open", return_value=BytesIO(b"fixture")) as download:
            with api.asset_response({"url": "https://api.github.com/repos/Owner/TapNibbles/releases/assets/7"}) as response:
                self.assertEqual(response.read(), b"fixture")
            self.assertEqual(download.call_count, 1)
            for url in [
                    "https://api.github.com/repos/other/TapNibbles/releases/assets/7",
                    "https://api.github.com/repos/owner/TapNibbles-other/releases/assets/7",
                    "https://api.github.com.evil.invalid/repos/owner/TapNibbles/releases/assets/7",
                    "http://api.github.com/repos/owner/TapNibbles/releases/assets/7",
                    "https://api.github.com/repos/owner/TapNibbles/releases/assets/7/extra",
                    "https://api.github.com/repos/owner/TapNibbles/releases/assets/7?other=1"]:
                with self.subTest(url=url), self.assertRaisesRegex(ReleaseError, "selected repository"):
                    api.asset_response({"url": url})
            self.assertEqual(download.call_count, 1)

    def test_only_a_durable_receipt_and_fresh_matching_digest_skip_a_second_download(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.zip"
            path.write_bytes(b"approved package")
            expected = digest(path)
            api = GitHub("owner/repo", "fixture")
            asset = {"id": 7, "name": path.name, "size": path.stat().st_size,
                "digest": "sha256:" + expected, "browser_download_url": "https://example.invalid/7"}
            release = {"id": 1}
            with patch.object(api, "pages", return_value=[asset]), patch.object(api, "verify_asset", return_value=expected) as download:
                api.upload_verified(release, path)
                download.assert_called_once()  # The initial receipt still requires real read-back.
            api.verified_assets = {7: {"sha256": expected, "size": path.stat().st_size}}
            with patch.object(api, "pages", return_value=[asset]), patch.object(api, "verify_asset") as download:
                self.assertEqual(api.upload_verified(release, path)["sha256"], expected)
                download.assert_not_called()
            asset["digest"] = "sha256:" + "f" * 64
            with patch.object(api, "pages", return_value=[asset]), patch.object(api, "verify_asset", side_effect=ReleaseError("Downloaded asset digest mismatch")):
                with self.assertRaisesRegex(ReleaseError, "digest mismatch"):
                    api.upload_verified(release, path)
