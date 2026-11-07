from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, digest, read_json
from local_release.profiles.revelation import build_web, web_output_current


class WebPackagingTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        job = Path(folder.name) / 'releases/fixture/1.0.0+1' / ('a' * 40)
        atomic_json(job / 'job.json', {'schema': 1, 'sha': 'a' * 40, 'run_id': 'fixture-a',
            'version': '1.0.0', 'build': 1,
            'project': 'fixture', 'artifacts': ['web.zip'], 'compile_defines_sha256': 'defines',
            'step_dependencies': {'sentry-web': ['web'], 'web-manifest': ['sentry-web'], 'web-zip': ['web-manifest']}})
        self.ctx = Context(job, {}, host='windows')
        self.ctx.command_workspace = Path('R:/fixture')
        self.ctx.command = self.command
        self.calls = []
        self.fail_upload = True
        self.ready = self.ctx.output / 'ready.apk'
        self.ready.write_bytes(b'keep signed package')
        self.ready_hash = digest(self.ready)

    def command(self, argv, *, cwd=None):
        self.calls.append((argv, cwd or self.ctx.command_workspace))
        root = self.ctx.workspace / 'build/web'
        if argv[:3] == ['flutter', 'build', 'web']:
            root.mkdir(parents=True, exist_ok=True)
            for name, value in [('main.dart.js', 'production'), ('main.dart.js.map', '{}'),
                                ('index.html', '<html>'), ('asset.txt', 'release asset')]:
                (root / name).write_text(value)
        elif 'scripts/prepare_sentry_web_source_maps.dart' in argv:
            # Source-map preparation legitimately changes the compiled JS.
            (root / 'main.dart.js').write_text('production with debug ID')
        elif 'sentry_dart_plugin' in argv and self.fail_upload:
            (root / 'main.dart.js').write_text('uploader injected debug ID before failure')
            raise ReleaseError('fixture upload failed')
        elif 'scripts/generate_web_loader_manifest.py' in argv:
            (root / 'loader_manifest.json').write_text('{}')
        return ''

    def first_failure(self):
        with self.assertRaisesRegex(ReleaseError, 'upload failed'):
            build_web(self.ctx, ['--release'])
        self.assertTrue(web_output_current(self.ctx))

    def test_sentry_retry_reuses_web_and_keeps_flutter_physical_and_uploader_short(self):
        self.first_failure()
        self.fail_upload = False
        build_web(self.ctx, ['--release'])
        self.assertEqual(sum(a[:3] == ['flutter', 'build', 'web'] for a, _ in self.calls), 1)
        for argv, cwd in self.calls:
            self.assertEqual(cwd, self.ctx.command_workspace if 'sentry_dart_plugin' in argv else self.ctx.workspace)
        self.assertEqual(digest(self.ready), self.ready_hash)
        self.assertTrue(web_output_current(self.ctx))
        with zipfile.ZipFile(self.ctx.output / 'web.zip') as archive:
            self.assertIn('main.dart.js', archive.namelist())
            self.assertIn('loader_manifest.json', archive.namelist())
            self.assertNotIn('main.dart.js.map', archive.namelist())

    def test_replaced_integration_output_requires_production_rebuild(self):
        self.first_failure()
        (self.ctx.workspace / 'build/web/asset.txt').write_text('integration output')
        self.assertFalse(web_output_current(self.ctx))
        self.fail_upload = False
        build_web(self.ctx, ['--release'])
        self.assertEqual(sum(a[:3] == ['flutter', 'build', 'web'] for a, _ in self.calls), 2)
        self.assertEqual((self.ctx.workspace / 'build/web/asset.txt').read_text(), 'release asset')
        self.assertEqual(digest(self.ready), self.ready_hash)

    def test_missing_source_map_or_different_source_identity_cannot_reuse_output(self):
        self.first_failure()
        path = self.ctx.directory / 'results/windows-web-build.json'
        value = read_json(path)
        value['sha'] = 'b' * 40
        atomic_json(path, value)
        self.ctx.result['steps']['web']['outputs']['results/windows-web-build.json'] = digest(path)
        self.assertFalse(web_output_current(self.ctx))
        value['sha'] = self.ctx.job['sha']
        atomic_json(path, value)
        self.ctx.result['steps']['web']['outputs']['results/windows-web-build.json'] = digest(path)
        (self.ctx.workspace / 'build/web/main.dart.js.map').unlink()
        self.assertFalse(web_output_current(self.ctx))

    def test_verified_zip_does_not_need_old_builder_outputs(self):
        self.fail_upload = False
        build_web(self.ctx, ['--release'])
        calls = len(self.calls)
        expected = digest(self.ctx.output / 'web.zip')
        (self.ctx.workspace / 'build/web/main.dart.js.map').unlink()
        build_web(self.ctx, ['--release'])
        self.assertEqual(len(self.calls), calls)
        self.assertEqual(digest(self.ctx.output / 'web.zip'), expected)


if __name__ == '__main__':
    unittest.main()
