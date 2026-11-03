"""TAP44 identity, privacy, checkpoint and publication-gate regressions."""
from pathlib import Path
import sys
import json
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from contextlib import nullcontext
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json
from local_release.github import complete_results, release_metadata
from local_release.profiles import tapnibbles


class TapNibblesProfileTests(unittest.TestCase):
    def metadata(self, changelog='## [1.0.0]\nRelease notes\n'):
        values = {'pubspec.yaml': 'version: 1.0.0+12',
                  'CHANGELOG.md': changelog,
                  'android/app/build.gradle.kts': 'android {\n    buildTypes {\n'
                      '        release { signingConfig = signingConfigs.getByName("debug") }\n    }\n}\n'}
        with patch.object(tapnibbles, 'git', side_effect=lambda repo, _, path: values[path.split(':', 1)[1]]):
            return tapnibbles.metadata(None, 'a' * 40, {})

    def test_prerelease_notes_use_committed_pending_changes_or_the_version_section(self):
        for heading in ['Unreleased', '[Unreleased]']:
            job = self.metadata(f'## {heading}\n\n- Play the practice game.\n\n## [1.0.0]\nOld scaffold.\n')
            self.assertIn('## 1.0.0+12', job['release_notes'])
            self.assertIn('- Play the practice game.', job['release_notes'])
            self.assertNotIn('Old scaffold.', job['release_notes'])
        self.assertIn('Release notes', self.metadata('## Unreleased\n\n## [1.0.0]\nRelease notes\n')['release_notes'])
        with self.assertRaisesRegex(ReleaseError, 'changelog section'):
            self.metadata('## Unreleased\n- Pending change.\n')

    def test_four_release_packages_windows_only_and_sentry_explicitly_deferred(self):
        job = self.metadata()
        self.assertEqual(list(job['required_steps']), ['windows'])
        self.assertEqual(len(job['artifacts']), 4)
        self.assertEqual({Path(n).suffix for n in job['artifacts']}, {'.apk', '.aab', '.zip'})
        self.assertEqual(job['build_mode'], 'release')
        self.assertEqual(job['sentry']['status'], 'deferred')
        self.assertIn('integration-windows', job['required_steps']['windows'])
        self.assertFalse(any('linux' in n or 'ios' in n or 'macos' in n for n in job['artifacts']))

    def test_public_zip_excludes_private_symbols_and_map_references(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'web'
            source.mkdir()
            for name in ['secret.map', 'app.pdb', 'private.dart', 'key.keystore']:
                (source / name).write_text('private-fixture')
            (source / 'main.dart.js').write_text('release-runtime\n//# sourceMappingURL=secret.map\n', newline='\n')
            tapnibbles.pack(source, root / 'release.zip')
            with zipfile.ZipFile(root / 'release.zip') as archive:
                self.assertEqual(archive.namelist(), ['main.dart.js'])
                self.assertEqual(archive.read('main.dart.js'), b'release-runtime\n')

    def test_release_signing_recipe_has_no_debug_fallback(self):
        recipe = Path(__file__).resolve().parents[4] / 'Tapnibbles/android/app/build.gradle.kts'
        with patch.object(tapnibbles, 'git', return_value=recipe.read_text(encoding='utf-8').strip()):
            actual = tapnibbles.signing_gradle(None, 'a' * 40)
        self.assertNotIn('signingConfigs.getByName("debug")', actual)
        self.assertIn('signingConfigs.getByName("release")', actual)
        self.assertIn('key.properties', actual)

    def test_missing_certificate_and_changed_keystore_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            key = Path(folder) / 'key'
            key.write_bytes(b'fixture')
            with self.assertRaises(ReleaseError):
                tapnibbles.input_metadata({'signing_store_file': str(key)})
            config = {'signing_store_file': str(key), 'expected_signing_certificate_sha256': 'a' * 64}
            before = tapnibbles.input_metadata(config)
            key.write_bytes(b'replaced')
            self.assertNotEqual(before['signing_keystore_sha256'], tapnibbles.input_metadata(config)['signing_keystore_sha256'])

    def test_project_command_plan_must_match_source_and_selects_only_aab(self):
        job = {'sha': 'a' * 40, 'version': '1.0.0', 'build': 12}
        plan = {'metadata': dict(job), 'commands': [['flutter', 'build', 'apk', '--release'],
                                                   ['flutter', 'build', 'appbundle', '--release']]}
        calls = []
        ctx = SimpleNamespace(job=job, command=lambda argv: calls.append(argv) or json.dumps(plan))
        tapnibbles.compile_target(ctx, 'android', 'appbundle')
        self.assertEqual(calls[-1][2], 'appbundle')
        plan['metadata']['sha'] = 'b' * 40
        with self.assertRaises(ReleaseError):
            tapnibbles.compile_target(ctx, 'android', 'apk')

    def test_preflight_routes_adb_to_dedicated_server_from_persistent_root(self):
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            workspace = root / 'checkout'
            (workspace / 'android/app').mkdir(parents=True)
            key = root / 'key'
            key.write_bytes(b'fixture-key')
            config = {'signing_store_file': str(key), 'expected_signing_certificate_sha256': 'a' * 64,
                'java_home': str(root / 'java'), 'flutter_sdk': str(root / 'flutter'),
                'android_sdk': str(root / 'sdk'), 'adb_server_port': 5053}
            recipe = 'fixture signed Gradle recipe\n'
            job = {**tapnibbles.input_metadata(config), 'sha': 'a' * 40,
                'generated_source_overlays': {'android/app/build.gradle.kts': hashlib.sha256(recipe.encode()).hexdigest()}}
            calls = []
            ctx = SimpleNamespace(config=config, job=job, workspace=workspace, root=root,
                env={k: 'fixture-only' for k in ['SIGNING_KEY_ALIAS', 'SIGNING_KEY_PASSWORD', 'SIGNING_STORE_PASSWORD']},
                command=lambda argv, **kw: calls.append((argv, kw)), refresh_redaction=lambda values: None)
            with patch.object(tapnibbles, 'signing_gradle', return_value=recipe):
                tapnibbles.configure(ctx)
            self.assertEqual(ctx.env['ADB_SERVER_SOCKET'], 'tcp:127.0.0.1:5053')
            self.assertEqual(calls[0][1]['cwd'], root)
            self.assertEqual(calls[0][0][-1], 'start-server')
            config['adb_server_port'] = 5037
            with self.assertRaises(ReleaseError):
                tapnibbles.configure(ctx)

    def test_missing_platform_gate_prevents_finalization(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            job = {**self.metadata(), 'sha': 'a' * 40, 'run_id': 'tapnibbles-fixture'}
            result = {'sha': job['sha'], 'run_id': job['run_id'], 'steps': {
                name: {'status': 'passed'} for name in job['required_steps']['windows']}}
            atomic_json(root / 'results/windows.json', result)
            self.assertTrue(complete_results(root, job))
            result['steps']['integration-android']['status'] = 'failed'
            atomic_json(root / 'results/windows.json', result)
            self.assertFalse(complete_results(root, job))

    def test_public_release_manifest_keeps_signing_facts_and_excludes_credentials(self):
        job = {**self.metadata(), 'signing_certificate_sha256': 'a' * 64,
               'environment': {'SIGNING_STORE_PASSWORD': 'private-fixture'},
               'signing_store_file': 'private-location', 'github_token': 'private-fixture'}
        public = release_metadata(job)
        self.assertEqual(public['build_mode'], 'release')
        self.assertEqual(public['signing_certificate_sha256'], 'a' * 64)
        self.assertEqual(public['sentry']['status'], 'deferred')
        self.assertNotIn('private-', json.dumps(public))

    def test_retry_preserves_verified_output_and_repeats_failed_step(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root / 'releases/tapnibbles/1.0.0+12' / ('a' * 40)
            job = {**self.metadata(), 'schema': 1, 'project': 'tapnibbles', 'sha': 'a' * 40,
                   'run_id': 'tapnibbles-fixture'}
            atomic_json(directory / 'job.json', job)
            ctx = Context(directory, {}, host='windows')
            calls = []
            def package():
                calls.append('package')
                (ctx.output / 'verified.zip').write_bytes(b'verified-fixture')
            ctx.stage('web-zip', package, ['packages/verified.zip'])
            with self.assertRaises(ReleaseError):
                ctx.stage('verify-apk', lambda: (_ for _ in ()).throw(ReleaseError('fixture failure')))
            resumed = Context(directory, {}, host='windows')
            resumed.stage('web-zip', package, ['packages/verified.zip'])
            resumed.stage('verify-apk', lambda: calls.append('retry'))
            self.assertEqual(calls, ['package', 'retry'])
            self.assertEqual((ctx.output / 'verified.zip').read_bytes(), b'verified-fixture')

    def test_android_disconnect_cleanup_keeps_original_vm_error_and_removes_generated_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'integration_test').mkdir()
            (root / 'integration_test/app_smoke_test.dart').write_text('void main() {}')
            calls = []
            def invoke(argv, **kwargs):
                calls.append(argv)
                if argv[0] == 'flutter':
                    raise ReleaseError('original VM failure')
                if '--remove' in argv:
                    raise ReleaseError('device disconnected during cleanup')
            ctx = SimpleNamespace(workspace=root, root=root, config={
                'android_sdk': str(root / 'sdk'), 'adb_server_port': 5053,
                'android_device': 'emulator-5590', 'auth_port': 19099, 'worker_port': 18878}, command=invoke)
            with patch('local_release.prerequisites.android_device', return_value=nullcontext()), \
                    patch('local_release.prerequisites.child', return_value=nullcontext()):
                with self.assertRaisesRegex(ReleaseError, 'original VM failure'):
                    tapnibbles.integration(ctx, 'android')
            self.assertEqual(sum('--remove' in argv for argv in calls), 2)
            self.assertFalse((root / 'integration_test/tap44_release_test.dart').exists())

    def test_web_widget_input_runs_with_assertions_while_package_mode_remains_release(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'integration_test').mkdir()
            (root / 'integration_test/app_smoke_test.dart').write_text('void main() {}')
            calls = []
            job = self.metadata()
            job['sha'] = 'a' * 40
            ctx = SimpleNamespace(workspace=root, root=root, directory=root, job=job,
                config={'chromedriver_port': 18884, 'web_port': 18881},
                command=lambda argv: calls.append(argv))
            with patch('local_release.prerequisites.chrome_driver', return_value=nullcontext()):
                tapnibbles.integration(ctx, 'web')
            self.assertIn('--debug', calls[0])
            self.assertNotIn('--release', calls[0])
            target = next(arg.removeprefix('--target=') for arg in calls[0] if arg.startswith('--target='))
            self.assertEqual(Path(target).parent, Path('.'))  # DDC can resolve both integration_test and test/helpers.
            self.assertEqual(job['build_mode'], 'release')
            receipt = json.loads((root / 'results/integration-web.json').read_text())
            self.assertEqual(receipt['test_build_mode'], 'debug')


if __name__ == '__main__':
    unittest.main()
