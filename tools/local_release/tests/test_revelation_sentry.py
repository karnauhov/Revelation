from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError, read_json
from local_release.profiles import revelation_sentry as sentry


class RevelationSentryTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        self.commands = []
        self.ctx = SimpleNamespace(workspace=root / 'source', directory=root / 'job',
            job={'sha': 'a' * 40, 'version': '1.0.8', 'build': 174},
            command=lambda args: self.commands.append(args))

    def symbols(self, target):
        root = self.ctx.workspace / 'build/sentry' / target
        root.mkdir(parents=True)
        names = ['app.android-' + abi + '.symbols' for abi in ('arm', 'arm64', 'x64')] if target in ('apk', 'aab') else ['app.' + target + '-x64.symbols']
        for name in names:
            (root / name).write_bytes(b'fixture symbols ' + name.encode())
        return root

    def test_each_final_target_requires_its_own_symbols_and_persists_identity(self):
        for target in ('apk', 'aab', 'windows', 'linux'):
            with self.subTest(target=target):
                self.symbols(target)
                sentry.upload_native(self.ctx, target)
                receipt = read_json(self.ctx.directory / ('results/sentry-' + target + '.json'))
                self.assertEqual(receipt['release'], 'revelation@1.0.8+174')
                self.assertEqual(receipt['sha'], 'a' * 40)
                self.assertIn('--sentry-define=wait_for_processing=true', self.commands[-1])
                self.assertIn('--sentry-define=upload_source_maps=false', self.commands[-1])
                self.assertIn('--sentry-define=symbols_path=build/sentry/' + target, self.commands[-1])

    def test_missing_abi_or_wrong_target_does_not_upload_or_write_receipt(self):
        root = self.symbols('apk')
        (root / 'app.android-arm64.symbols').unlink()
        for target in ('apk', 'aab'):
            with self.assertRaises(ReleaseError): sentry.upload_native(self.ctx, target)
        self.assertEqual(self.commands, [])
        self.assertFalse((self.ctx.directory / 'results').exists())

    def test_upload_failure_remains_retryable_without_success_receipt(self):
        self.symbols('windows')
        def fail(args): raise ReleaseError('upload failed')
        self.ctx.command = fail
        with self.assertRaises(ReleaseError): sentry.upload_native(self.ctx, 'windows')
        self.assertFalse((self.ctx.directory / 'results/sentry-windows.json').exists())

    def test_build_symbols_are_separate_from_distribution_and_identity_is_explicit(self):
        self.assertEqual(sentry.build_flags('aab'), ['--split-debug-info=build/sentry/aab'])
        self.assertIn('--sentry-define=project=revelation-flutter', sentry.identity_args(self.ctx))


if __name__ == '__main__': unittest.main()
