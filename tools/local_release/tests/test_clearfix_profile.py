"""ClearFix scope, client inputs, packaging and release verification regressions."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError, atomic_json
from local_release.profiles import clearfix


class ClearFixProfileTest(unittest.TestCase):
    def source(self, repo, *args):
        if args[0] == 'tag':
            return ''
        if args[-1].endswith('pubspec.yaml'):
            return 'version: 1.1.0+111\n  msix_version: 1.1.111.0\n'
        return '## [1.1.0] - 2026-11-02\nCurrent notes\n\n## [1.0.0]\nOlder notes'

    def test_five_packages_one_host_and_all_publication_gates(self):
        with patch.object(clearfix, 'git', side_effect=self.source):
            job = clearfix.metadata(None, 'a' * 40, {})
        self.assertEqual(set(job['required_steps']), {'windows'})
        self.assertEqual(len(job['artifacts']), 5)
        self.assertTrue(job['artifacts'][-1].endswith('1.1.111.0.msix'))
        self.assertEqual(job['tag'], 'auto-v1.1.0-b111-aaaaaaaa')
        self.assertNotIn('Older notes', job['release_notes'])
        for spec in job['artifact_specs'].values():
            self.assertEqual(spec['host'], 'windows')
            self.assertTrue(set(spec['gates']) <= set(job['required_steps']['windows']))
        self.assertTrue({'sentry-web', 'sentry-android', 'sentry-windows', 'coverage-threshold'} <= set(job['required_steps']['windows']))

    def test_stale_store_version_blocks_preparation(self):
        with patch.object(clearfix, 'git', return_value='version: 1.1.0+111\n  msix_version: 1.1.110.0'):
            with self.assertRaisesRegex(ReleaseError, 'not synchronized'):
                clearfix.metadata(None, 'a' * 40, {})

    def test_inputs_are_platform_filtered_and_production_does_not_mutate_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            values = dict(CFX_FIREBASE_ANDROID_API_KEY='android-key', CFX_FIREBASE_WEB_API_KEY='web-key',
                CFX_FIREBASE_IOS_API_KEY='excluded-ios', CFX_WINDOWS_GOOGLE_CLIENT_SECRET='windows-secret',
                SENTRY_DSN='https://example.invalid/1', SENTRY_ENVIRONMENT='development')
            atomic_json(root / 'defines.json', values)
            result = clearfix.compile_defines({'defines_file': str(root / 'defines.json')})
            self.assertNotIn('CFX_FIREBASE_IOS_API_KEY', str(result))
            self.assertNotIn('CFX_WINDOWS_GOOGLE_CLIENT_SECRET', result['web'])
            self.assertNotIn('CFX_WINDOWS_GOOGLE_CLIENT_SECRET', result['android'])
            self.assertEqual(result['windows']['CFX_WINDOWS_GOOGLE_CLIENT_SECRET'], 'windows-secret')
            self.assertTrue(all(value['SENTRY_ENVIRONMENT'] == 'production' for value in result.values()))
            self.assertEqual(json.loads((root / 'defines.json').read_text()), values)

    def test_missing_client_keys_and_unpinned_certificate_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'defines.json'
            atomic_json(path, {'SENTRY_DSN': 'dsn'})
            with self.assertRaises(ReleaseError):
                clearfix.compile_defines({'defines_file': str(path)})
            with self.assertRaises(ReleaseError):
                clearfix.input_metadata({'defines_file': str(path)})

    def test_public_web_keeps_hidden_files_and_excludes_maps_without_deleting_them(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            web = root / 'build/web'
            web.mkdir(parents=True)
            for name in ['index.html', '404.html', '.nojekyll', 'main.dart.js', 'flutter_bootstrap.js',
                         'loader_manifest.json', 'privacy_policy.html', 'license_agreement.html', 'main.dart.js.map']:
                (web / name).write_text('fixture', encoding='utf-8')
            atomic_json(web / 'version.json', dict(version='1.1.0', build_number='111'))
            ctx = SimpleNamespace(workspace=root, job=dict(version='1.1.0', build=111))
            package = root / 'web.zip'
            clearfix.pack_web(ctx, package)
            clearfix.verify_web(ctx, package)
            self.assertTrue((web / 'main.dart.js.map').exists())
            with zipfile.ZipFile(package, 'a') as archive:
                archive.writestr('leaked.map', 'fixture')
            with self.assertRaisesRegex(ReleaseError, 'source maps'):
                clearfix.verify_web(ctx, package)

    def test_wrong_android_certificate_cannot_pass(self):
        ctx = SimpleNamespace(workspace=Path('.'), config={}, job=dict(build=111, version='1.1.0',
            signing_certificate_sha256='a' * 64, architectures={'android': ['arm64-v8a']}))
        ctx.command = lambda args, **kwargs: ("package: name='click.clearfix' versionCode='111' versionName='1.1.0'\nnative-code: 'arm64-v8a'"
            if 'badging' in args else 'Signer #1 certificate SHA-256 digest: ' + 'b' * 64)
        with patch.object(clearfix, 'tools', return_value=('aapt', 'apksigner')):
            with self.assertRaisesRegex(ReleaseError, 'certificate mismatch'):
                clearfix.verify_apk(ctx, Path('fixture.apk'))


if __name__ == '__main__':
    unittest.main()
