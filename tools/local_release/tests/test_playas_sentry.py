import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, digest
from local_release.profiles import playas, playas_sentry as sentry
from local_release.profiles import playas_android_symbols as android


class PlayasSentryTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        job = root / 'releases/playas/1.2.1+60' / ('a' * 40)
        dependencies = {'sentry-android':['apk','aab'], 'verify-apk':['apk','sentry-android'],
            'verify-aab':['aab','sentry-android'], 'web-sources':['web'], 'sentry-web':['web-sources'],
            'web-manifest':['sentry-web'], 'web-zip':['web-manifest'], 'verify-web':['web-zip']}
        atomic_json(job / 'job.json', {'schema':1, 'sha':'a'*40, 'run_id':'fixture', 'project':'playas',
            'version':'1.2.1', 'build':60, 'compile_defines_sha256':'fixture', 'sentry_required':True,
            'artifacts':['app.apk','app.aab','web.zip'], 'step_dependencies':dependencies})
        self.ctx = Context(job, {'sentry_cli':'fixture-cli', 'sentry_cli_sha256':'b'*64}, host='windows')
        self.ctx.workspace.mkdir(parents=True)
        self.ctx.env.update(SENTRY_RELEASE='playas@1.2.1+60', SENTRY_DIST='60')
        self.calls = []
        self.fail_upload = True
        self.fail_ndk_upload = False
        self.ctx.command = self.command
        registry_patch = patch.object(android, 'verify_registry')
        self.registry = registry_patch.start()
        self.addCleanup(registry_patch.stop)
        for name in ['verify_apk','verify_aab','verify_web']:
            mocked = patch.object(playas, name)
            mocked.start()
            self.addCleanup(mocked.stop)

    def command(self, argv, **kwargs):
        self.calls.append(argv)
        if argv[:2] == ['flutter','build']:
            if argv[2] == 'web':
                root = self.ctx.workspace / 'build/web'
                root.mkdir(parents=True, exist_ok=True)
                for name, value in {'index.html':'<html>', 'main.dart.js':'compiled', 'main.dart.js.map':'{}',
                    'flutter_bootstrap.js':'bootstrap', 'version.json':'{}'}.items():
                    (root / name).write_text(value)
            else:
                path = 'build/app/outputs/flutter-apk/app-release.apk' if argv[2] == 'apk' else 'build/app/outputs/bundle/release/app-release.aab'
                target = self.ctx.workspace / path
                target.parent.mkdir(parents=True, exist_ok=True)
                mapping = self.ctx.workspace / 'build/app/outputs/mapping/release/mapping.txt'
                mapping.parent.mkdir(parents=True, exist_ok=True)
                mapping.write_text('# pg_map_hash: SHA-256 '
                                   'd0d02d04eea8d701b935fb66ece97b5341dfe7558434608d36e868bf56afe3f3\n'
                                   'Example -> a:\n')
                prefix = 'base/' if argv[2] == 'appbundle' else ''
                with zipfile.ZipFile(target, 'w') as archive:
                    archive.writestr(prefix + android.MAPPING_ASSET,
                                     'io.sentry.ProguardUuids=f412bab7-e923-3b0e-956e-de9d0bb3c384\n')
                    for abi in android.ABI_SYMBOLS:
                        archive.writestr(f'{prefix}lib/{abi}/libapp.so', b'private AOT')
                        archive.writestr(f'{prefix}lib/{abi}/libnative.so', b'private ELF')
                        merged = self.ctx.workspace / ('build/app/intermediates/merged_native_libs/release/'
                                                       'mergeReleaseNativeLibs/out/lib') / abi
                        merged.mkdir(parents=True, exist_ok=True)
                        (merged / 'libnative.so').write_bytes(b'private ELF')
                symbol_dir = Path(next(a.split('=',1)[1] for a in argv if a.startswith('--split-debug-info=')))
                for name in sentry.SYMBOLS:
                    (symbol_dir / name).write_bytes(b'private AOT')
        if argv[1:4] == ['debug-files', 'check', '--json']:
            value = digest(Path(argv[-1]))
            return json.dumps({'type': 'elf', 'is_usable': True, 'features': 'symtab, debug',
                               'variants': [{'debug_id': value[:32], 'code_id': value, 'arch': 'fixture'}]})
        if 'sentry_dart_plugin' in argv and '--sentry-define=upload_source_maps=true' in argv:
            (self.ctx.workspace / 'build/web/main.dart.js').write_text('compiled with Debug ID')
            if self.fail_upload:
                raise ReleaseError('fixture upload failed')
        if 'debug-files' in argv and 'upload' in argv and self.fail_ndk_upload:
            raise ReleaseError('fixture NDK upload failed')
        return ''

    def test_retry_upload_preserves_signed_packages_and_web_without_recompile(self):
        with self.assertRaisesRegex(ReleaseError, 'upload failed'):
            sentry.build(self.ctx)
        hashes = {n:digest(self.ctx.output/n) for n in ['app.apk','app.aab']}
        self.fail_upload = False
        sentry.build(self.ctx)
        builds = [args[2] for args in self.calls if args[:2] == ['flutter','build']]
        self.assertEqual(builds, ['apk','appbundle','web'])
        web_uploads = [args for args in self.calls if 'sentry_dart_plugin' in args and '--sentry-define=upload_source_maps=true' in args]
        for args in web_uploads:
            self.assertIn('--sentry-define=upload_sources=false', args)
            self.assertIn('--sentry-define=commits=false', args)
            self.assertIn('--sentry-define=web_build_path=' + str(self.ctx.workspace/'build/web'), args)
        self.assertEqual(hashes, {n:digest(self.ctx.output/n) for n in hashes})
        mappings = [args for args in self.calls if 'upload-proguard' in args]
        self.assertEqual(len(mappings), 1)
        self.assertIn(android.mapping_uuid(self.ctx.directory / 'private/android/apk/mapping.txt'), mappings[0])
        ndk = [args for args in self.calls if 'debug-files' in args and 'upload' in args]
        self.assertEqual(len(ndk), 1)
        self.assertIn('--wait-for', ndk[0])
        self.registry.assert_called_once()
        with zipfile.ZipFile(self.ctx.output/'web.zip') as archive:
            self.assertIn('main.dart.js', archive.namelist())
            self.assertIn('sentry-assets.json', archive.namelist())
            self.assertNotIn('main.dart.js.map', archive.namelist())
            manifest = json.loads(archive.read('sentry-assets.json'))
            self.assertEqual(manifest['files']['main.dart.js'], hashlib.sha256(archive.read('main.dart.js')).hexdigest())
        calls = len(self.calls)
        sentry.build(self.ctx)
        self.assertEqual(len(self.calls), calls)

    def test_lost_web_map_invalidates_only_web_branch(self):
        self.fail_upload = False
        sentry.build(self.ctx)
        (self.ctx.workspace/'build/web/main.dart.js.map').unlink()
        sentry.build(self.ctx)
        builds = [args[2] for args in self.calls if args[:2] == ['flutter','build']]
        self.assertEqual(builds, ['apk','appbundle','web','web'])

    def test_retry_native_upload_reuses_both_signed_packages(self):
        self.fail_upload = False
        self.fail_ndk_upload = True
        with self.assertRaisesRegex(ReleaseError, 'NDK upload failed'):
            sentry.build(self.ctx)
        packages = [self.ctx.output / name for name in ('app.apk', 'app.aab')]
        hashes = [digest(package) for package in packages]
        self.fail_ndk_upload = False
        sentry.build(self.ctx)
        builds = [args[2] for args in self.calls if args[:2] == ['flutter','build']]
        self.assertEqual(builds, ['apk','appbundle','web'])
        self.assertEqual(hashes, [digest(package) for package in packages])

    def test_missing_abi_symbols_cannot_mark_upload_passed(self):
        root = self.ctx.directory/'private/android/apk'
        root.mkdir(parents=True)
        with self.assertRaisesRegex(ReleaseError,'Missing AOT symbols'):
            sentry.upload(self.ctx,'android')
        self.assertEqual(self.calls, [])

    def test_different_elf_build_id_blocks_upload(self):
        self.fail_upload = False
        sentry.build(self.ctx)
        private = self.ctx.directory / 'private/android/apk'
        (private / 'aot/app.android-x64.symbols').write_bytes(b'symbols from another build')
        with self.assertRaisesRegex(ReleaseError, 'Symbols do not match'):
            android.retain(self.ctx, self.ctx.output / 'app.apk', private)

    def test_mapping_cannot_be_changed_before_retry(self):
        self.fail_upload = False
        sentry.build(self.ctx)
        root = self.ctx.directory / 'private/android'
        (root / 'apk/mapping.txt').write_text('Different -> b:\n')
        with self.assertRaisesRegex(ReleaseError, 'symbol inputs changed'):
            android.upload(self.ctx, root)

    def test_mapping_from_a_different_build_fails_before_upload(self):
        self.fail_upload = False
        sentry.build(self.ctx)
        mapping = self.ctx.workspace / 'build/app/outputs/mapping/release/mapping.txt'
        mapping.write_text('# pg_map_hash: SHA-256 ' + 'b' * 64 + '\nDifferent -> b:\n')
        private = self.ctx.directory / 'private/android/apk'
        with self.assertRaisesRegex(ReleaseError, 'mapping UUID does not match'):
            android.retain(self.ctx, self.ctx.output / 'app.apk', private)

    def test_production_preflight_refuses_unapproved_privacy_and_missing_credentials(self):
        with self.assertRaisesRegex(ReleaseError,'Sentry-enabled'):
            sentry.configure(self.ctx)
        self.ctx.config['sentry_required'] = True
        with self.assertRaisesRegex(ReleaseError,'Owner-approved'):
            sentry.configure(self.ctx)
        self.ctx.config['sentry_privacy_approved'] = True
        with self.assertRaisesRegex(ReleaseError,'CLI binary'):
            sentry.configure(self.ctx)

    def test_defines_reject_other_project_nonproduction_and_invalid_rate(self):
        values = {'SENTRY_DSN':'https://public@o4511324523921408.ingest.de.sentry.io/'+sentry.PROJECT_ID,
                  'SENTRY_ENVIRONMENT':'production','SENTRY_TRACES_SAMPLE_RATE':'0'}
        self.assertEqual(sentry.sentry_defines(values)['SENTRY_ENVIRONMENT'],'production')
        for patch_values in [{'SENTRY_DSN':'https://public@example.com/1'}, {'SENTRY_ENVIRONMENT':'qa'},
                             {'SENTRY_TRACES_SAMPLE_RATE':'NaN'}, {'SENTRY_TRACES_SAMPLE_RATE':'1.1'}]:
            with self.subTest(patch=patch_values), self.assertRaises(ReleaseError):
                sentry.sentry_defines({**values, **patch_values})

    def test_service_worker_hashes_are_deterministic_after_debug_id_injection(self):
        root = self.ctx.workspace/'fixture'
        root.mkdir()
        (root/'main.dart.js').write_text('final JS')
        (root/'flutter_bootstrap.js').write_text('serviceWorkerVersion: "old"')
        (root/'flutter_service_worker.js').write_text('const RESOURCES = {"main.dart.js":"old","flutter_bootstrap.js":"old","main.dart.js.map":"old"};')
        sentry.refresh_service_worker(root)
        hashes = sentry.tree_hashes(root)
        sentry.refresh_service_worker(root)
        self.assertEqual(hashes, sentry.tree_hashes(root))
        text = (root/'flutter_service_worker.js').read_text()
        self.assertIn(hashlib.md5((root/'main.dart.js').read_bytes()).hexdigest(), text)
        self.assertIn(hashlib.md5((root/'flutter_bootstrap.js').read_bytes()).hexdigest(), text)
        self.assertNotIn('main.dart.js.map', text)

    def test_flutter_cleanup_worker_stays_unchanged_and_unknown_cache_fails(self):
        root = self.ctx.workspace / 'fixture'
        root.mkdir()
        worker = root / 'flutter_service_worker.js'
        bootstrap = root / 'flutter_bootstrap.js'
        bootstrap.write_text('serviceWorkerVersion: "old"')
        worker.write_text("self.addEventListener('activate', async () => {"
                          'await self.registration.unregister();});')
        before = sentry.tree_hashes(root)
        self.assertFalse(sentry.refresh_service_worker(root))
        self.assertEqual(before, sentry.tree_hashes(root))
        worker.write_text("self.addEventListener('fetch', () => caches.open('unknown'));")
        with self.assertRaisesRegex(ReleaseError, 'Unrecognized Flutter service worker'):
            sentry.refresh_service_worker(root)

    def test_metadata_keeps_legacy_jobs_and_requires_new_sentry_gates(self):
        def source(repo, *args):
            if args[0] == 'tag': return ''
            return 'version: 1.2.1+60' if 'pubspec' in args[-1] else '## [1.2.1]\nNotes'
        with patch.object(playas,'git',side_effect=source):
            legacy = playas.metadata(None,'a'*40,{})
            current = playas.metadata(None,'a'*40,{'sentry':{'required':True}})
        self.assertNotIn('sentry-web', legacy['required_steps']['windows'])
        self.assertIn('sentry-web', current['required_steps']['windows'])
        self.assertIn('sentry-android', current['step_dependencies']['verify-apk'])
        self.assertEqual(current['step_dependencies']['web-zip'],['web-manifest'])

    def test_public_package_gate_rejects_symbols_and_upload_credentials(self):
        target = self.ctx.output/'unsafe.zip'
        self.ctx.env['SENTRY_AUTH_TOKEN'] = 'private-upload-fixture'
        for name, payload in [('main.dart.js.map', b'{}'), ('app.symbols', b'private'),
                              ('main.dart.js', b'private-upload-fixture')]:
            with self.subTest(name=name):
                with zipfile.ZipFile(target, 'w') as archive:
                    archive.writestr(name, payload)
                with self.assertRaises(ReleaseError):
                    sentry.verify_public_package(self.ctx, target)

    def test_compile_defines_never_include_upload_credential_or_override_source_sha(self):
        source = self.ctx.directory/'defines.json'
        values = {'IP2LOCATION_API_KEY':'client-one','GEOCODING_API_KEY':'client-two',
            'SENTRY_DSN':'https://public@o4511324523921408.ingest.de.sentry.io/'+sentry.PROJECT_ID,
            'SENTRY_ENVIRONMENT':'production','SENTRY_TRACES_SAMPLE_RATE':'0',
            'SENTRY_AUTH_TOKEN':'never compile this', 'SENTRY_SOURCE_SHA':'untrusted override',
            'SENTRY_APP_VERSION':'untrusted version', 'SENTRY_APP_BUILD':'untrusted build'}
        atomic_json(source, values)
        compiled = playas.compile_defines({'defines_file':str(source),'sentry_required':True})
        self.assertNotIn('SENTRY_AUTH_TOKEN', compiled)
        self.assertNotIn('SENTRY_SOURCE_SHA', compiled)
        self.assertNotIn('SENTRY_APP_VERSION', compiled)
        self.assertNotIn('SENTRY_APP_BUILD', compiled)
        self.assertEqual(compiled['SENTRY_ENVIRONMENT'],'production')


class AndroidRegistryTests(unittest.TestCase):
    def test_readback_accepts_existing_symbols_and_rejects_missing_elf(self):
        ctx = type('Context', (), {'env': {'SENTRY_AUTH_TOKEN': 'fixture-token'}})()
        receipts = {'apk': {'r8_uuid': 'mapping-id',
                            'images': {'x86_64/libapp.so': {'debug_id': 'elf-id'}}}}

        def response(debug_id, kind):
            return io.BytesIO(json.dumps([{'debugId': debug_id, 'symbolType': kind}]).encode())

        with patch.object(android, 'urlopen', side_effect=[response('mapping-id', 'proguard'),
                                                          response('elf-id', 'elf')]):
            android.verify_registry(ctx, receipts)
        with patch.object(android, 'urlopen', side_effect=[response('mapping-id', 'proguard'),
                                                          response('elf-id', 'sourcebundle')]):
            with self.assertRaisesRegex(ReleaseError, 'missing elf debug ID elf-id'):
                android.verify_registry(ctx, receipts)


if __name__ == '__main__':
    unittest.main()
