"""Restore legacy hosted auto releases without rebuilding or trusting tag text alone."""
import base64
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.archive import archive_releases
from local_release.core import ReleaseError, read_json


class LegacyArchiveTest(unittest.TestCase):
    def api(self, version='1.1.0+110'):
        payload = b'fixture-package'
        checksum = hashlib.sha256(payload).hexdigest()
        class API:
            downloads = 0
            def pages(self, path):
                if path == '/releases':
                    return [dict(id=1, tag_name='auto-main-v1.1.0-b110', draft=False,
                        html_url='https://example.invalid/release', target_commitish='main', body='hosted')]
                return [dict(id=2, name='clear_fix-1.1.0+110.apk', size=len(payload),
                    digest='sha256:' + checksum, browser_download_url='https://example.invalid/package')]
            def tag_sha(self, tag):
                return 'a' * 40
            def request(self, method, path):
                self_path = '/contents/pubspec.yaml?ref=' + 'a' * 40
                if method != 'GET' or path != self_path:
                    raise AssertionError(path)
                return {'content': base64.b64encode(('version: ' + version).encode()).decode()}
            def download_asset(self, asset, target):
                self.downloads += 1
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
                return checksum
        return API()

    def test_branch_tag_source_and_every_package_are_verified_and_reused(self):
        api = self.api()
        with tempfile.TemporaryDirectory() as folder, patch('local_release.archive.GitHub', return_value=api), patch('local_release.archive.credential', return_value='fixture'):
            root = Path(folder)
            for _ in range(2):
                archive_releases(dict(project='clearfix', repository='fixture/repo'), root, {})
            self.assertEqual(api.downloads, 1)
            path = root / 'releases/clearfix/1.1.0+110' / ('a' * 40)
            manifest = read_json(path / 'manifest.json')
            self.assertEqual(manifest['status'], 'archived')
            self.assertEqual(manifest['source'], 'github-archive')
            self.assertEqual(len(manifest['packages']), 1)

    def test_auto_tag_that_disagrees_with_source_cannot_enter_archive(self):
        api = self.api('1.1.0+109')
        with tempfile.TemporaryDirectory() as folder, patch('local_release.archive.GitHub', return_value=api), patch('local_release.archive.credential', return_value='fixture'):
            with self.assertRaisesRegex(ReleaseError, 'tagged pubspec'):
                archive_releases(dict(project='clearfix', repository='fixture/repo'), Path(folder), {})
            self.assertEqual(api.downloads, 0)


if __name__ == '__main__':
    unittest.main()
