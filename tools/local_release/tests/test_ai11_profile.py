"""AI11 adapter regression tests, without Flutter, keystores or network writes."""
import base64
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError, atomic_json, capture, git
from local_release.profiles import ai11
from local_release.agent import register
from local_release.versioning import install


class Ai11ProfileTest(unittest.TestCase):
    def test_profile_has_three_packages_and_one_host(self):
        def source(repo, *args):
            return {'show': 'version: 1.0.0+26' if 'pubspec' in args[-1] else '## [1.0.0] - 2026-11-01\nNotes', 'tag': ''}[args[0]]
        with patch.object(ai11, 'git', side_effect=source):
            job = ai11.metadata(None, 'a' * 40, {})
        self.assertEqual(set(job['required_steps']), {'windows'})
        self.assertEqual(len(job['artifacts']), 3)
        self.assertFalse(any(n.endswith('.aab') for n in job['artifacts']))
        self.assertTrue(job['release_prerelease'])

    def test_server_keys_rejected_and_client_fingerprint_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = {'defines_file': str(root / 'defines.json'), 'signing_store_file': str(root / 'key'),
                      'expected_signing_certificate_sha256': 'a' * 64}
            (root / 'key').write_bytes(b'fixture-only')
            for key in ['sb_secret_abc', 'x.' + base64.urlsafe_b64encode(b'{"role":"service_role"}').decode() + '.x']:
                atomic_json(root / 'defines.json', {'SUPABASE_URL': 'https://example.invalid', 'SUPABASE_PUBLISHABLE_KEY': key})
                with self.assertRaises(ReleaseError):
                    ai11.input_metadata(config)
            atomic_json(root / 'defines.json', {'SUPABASE_URL': 'https://example.invalid', 'SUPABASE_PUBLISHABLE_KEY': 'sb_publishable_fixture'})
            first = ai11.input_metadata(config)
            (root / 'key').write_bytes(b'different-key')
            self.assertNotEqual(first['signing_keystore_sha256'], ai11.input_metadata(config)['signing_keystore_sha256'])

    def test_archive_integrity_and_missing_bundle_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'bundle'
            source.mkdir()
            (source / 'ai11.exe').write_bytes(b'fixture')
            (source / 'data').mkdir()
            (source / 'data/app.so').write_bytes(b'fixture')
            ai11.pack(source, root / 'bundle.zip')
            ai11.verify_zip(root / 'bundle.zip', ['ai11.exe', 'data/app.so'])
            with self.assertRaises(ReleaseError):
                ai11.verify_zip(root / 'bundle.zip', ['flutter_windows.dll'])
            with zipfile.ZipFile(root / 'bad.zip', 'w') as archive:
                archive.writestr('../outside', 'fixture')
            with self.assertRaises(ReleaseError):
                ai11.verify_zip(root / 'bad.zip', [])

    def test_host_registration_does_not_add_linux_and_preserves_other_project(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            atomic_json(root / 'profile.json', {'project': 'ai11', 'hosts': ['windows']})
            atomic_json(root / 'registry.json', {'schema': 1, 'projects': {'revelation': {'unchanged': True}}})
            with patch('local_release.agent.git', return_value='a' * 40), patch('local_release.agent.install_local_excludes'):
                register(root / 'registry.json', root, root / 'profile.json', root / 'catalogue', root / 'config')
            registry = json.loads((root / 'registry.json').read_text())
            self.assertEqual(registry['projects']['ai11']['hosts'], ['windows'])
            self.assertEqual(registry['projects']['revelation'], {'unchanged': True})

    def test_real_ai11_helper_with_normal_skip_body_amend_and_signing_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder) / 'repo with spaces'
            capture(['git', 'init', repo])
            git(repo, 'config', 'user.name', 'Fixture')
            git(repo, 'config', 'user.email', 'fixture@example.invalid')
            git(repo, 'config', 'core.autocrlf', 'false')
            (repo / 'tool').mkdir()
            helper = Path(__file__).resolve().parents[4] / 'ai11/tool/sync_pubspec_build_number.py'
            shutil.copy2(helper, repo / 'tool/helper.py')
            (repo / 'pubspec.yaml').write_text('name: ai11\nversion: 1.0.0+25\n')
            atomic_json(repo / 'profile.json', {'versioning': {'helper': 'tool/helper.py', 'files': ['pubspec.yaml']}})
            git(repo, 'add', '.')
            git(repo, 'commit', '-m', 'baseline')
            install(repo, repo / 'profile.json')
            def build():
                return git(repo, 'show', 'HEAD:pubspec.yaml')
            git(repo, 'commit', '--allow-empty', '-m', 'normal')
            self.assertIn('+26', build())
            for message in ['[skip ci] title', 'body skip\n\n[skip ci]']:
                git(repo, 'commit', '--allow-empty', '-m', message)
                self.assertIn('+26', build())
            for _ in range(2):
                with self.assertRaises(ReleaseError):
                    git(repo, '-c', 'commit.gpgsign=true', '-c', 'gpg.program=false', 'commit', '--allow-empty', '-m', 'failure')
            git(repo, 'commit', '--allow-empty', '-m', 'retry')
            self.assertIn('+27', build())
            git(repo, 'commit', '--amend', '--no-edit')
            self.assertIn('+28', build())
            self.assertEqual(git(repo, 'status', '--porcelain'), '')


if __name__ == '__main__':
    unittest.main()
