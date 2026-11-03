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
    def test_untagged_owned_draft_is_reused_instead_of_creating_another_release(self):
        api = GitHub('owner/repo', 'fixture')
        job = {'sha': 'a' * 40, 'tag': 'auto-fixture', 'run_id': 'fixture-a'}
        marker = '<!-- local-release:fixture-a -->'
        draft = {'id': 7, 'tag_name': 'untagged-ab123', 'target_commitish': job['sha'],
                 'draft': True, 'body': 'notes\n\n' + marker}
        with patch.object(api, 'require_source'), patch.object(api, 'tag_sha', return_value=None), \
                patch.object(api, 'pages', return_value=[draft]), patch.object(api, 'request') as request:
            api.ensure_release(job, 'Current notes')
            request.assert_called_once_with('PATCH', '/releases/7', {
                'tag_name': 'auto-fixture', 'body': 'Current notes\n\n' + marker})
        public = {**draft, 'id': 8, 'tag_name': job['tag'], 'draft': False}
        with patch.object(api, 'require_source'), patch.object(api, 'tag_sha', return_value=job['sha']), \
                patch.object(api, 'pages', return_value=[draft, public]), patch.object(api, 'request') as request:
            self.assertEqual(api.ensure_release(job, 'notes'), public)
            request.assert_not_called()
        for changed in [{**draft, 'target_commitish': 'b' * 40}, {**draft, 'draft': False},
                        {**draft, 'tag_name': 'other-version'}]:
            with patch.object(api, 'require_source'), patch.object(api, 'tag_sha', return_value=None), \
                    patch.object(api, 'pages', return_value=[changed]), patch.object(api, 'request') as request:
                with self.assertRaisesRegex(ReleaseError, 'different source/tag'):
                    api.ensure_release(job, 'notes')
                request.assert_not_called()
        with patch.object(api, 'require_source'), patch.object(api, 'tag_sha', return_value=None), \
                patch.object(api, 'pages', return_value=[draft, {**draft, 'id': 8}]), patch.object(api, 'request') as request:
            with self.assertRaisesRegex(ReleaseError, 'Ambiguous owned'):
                api.ensure_release(job, 'notes')
            request.assert_not_called()

    def test_incomplete_owned_draft_upload_recovers_from_the_preserved_local_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.aab'
            path.write_bytes(b'verified local package')
            api = GitHub('owner/repo', 'fixture')
            release = {'id': 1, 'draft': True, 'body': '<!-- local-release:fixture-a -->',
                       'upload_url': 'https://uploads.github.com/fixture{?name}'}
            starter = {'id': 7, 'name': path.name, 'size': path.stat().st_size, 'state': 'starter'}
            uploaded = {**starter, 'id': 8, 'state': 'uploaded', 'browser_download_url': 'https://example.invalid/8'}
            with patch.object(api, 'pages', return_value=[starter]), \
                    patch.object(api, 'request', side_effect=[None, uploaded]) as request, \
                    patch.object(api, 'verify_asset') as verify:
                receipt = api.upload_verified(release, path)
                self.assertEqual(receipt['recovered_incomplete_asset_id'], 7)
                self.assertEqual(receipt['sha256'], digest(path))
                self.assertEqual(path.read_bytes(), b'verified local package')
                self.assertEqual(request.call_args_list[0].args, ('DELETE', '/releases/assets/7'))
                verify.assert_called_once_with(uploaded, digest(path))
            for changed in [{**release, 'draft': False}, {**release, 'body': 'foreign draft'}]:
                with patch.object(api, 'pages', return_value=[starter]), patch.object(api, 'request') as request:
                    with self.assertRaisesRegex(ReleaseError, 'Refusing recovery'):
                        api.upload_verified(changed, path)
                    request.assert_not_called()

    def test_binary_upload_uses_a_longer_bounded_socket_timeout(self):
        api = GitHub('owner/repo', 'fixture')
        for method, content_type, expected in [('POST', 'application/octet-stream', 600), ('GET', 'application/json', 180)]:
            with patch.object(api.opener, 'open', return_value=BytesIO(b'{}')) as request:
                api.request(method, '/fixture', content_type=content_type)
                self.assertEqual(request.call_args.kwargs['timeout'], expected)

    def test_repaired_notes_update_only_an_owned_unpublished_draft(self):
        api = GitHub('owner/repo', 'fixture')
        job = {'sha': 'a' * 40, 'tag': 'auto-fixture', 'run_id': 'fixture-a'}
        marker = '<!-- local-release:fixture-a -->'
        release = {'id': 7, 'tag_name': job['tag'], 'target_commitish': job['sha'],
                   'draft': True, 'body': 'Old notes\n\n' + marker}
        with patch.object(api, 'require_source'), patch.object(api, 'tag_sha', return_value=job['sha']), \
                patch.object(api, 'pages', return_value=[release]), patch.object(api, 'request') as request:
            api.ensure_release(job, 'Current committed notes')
            request.assert_called_once_with('PATCH', '/releases/7', {'body': 'Current committed notes\n\n' + marker})
            request.reset_mock()
            release['draft'] = False
            self.assertEqual(api.ensure_release(job, 'Another note'), release)
            request.assert_not_called()

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
