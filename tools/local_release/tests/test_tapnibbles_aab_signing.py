"""TAP148: exercise the actual JDK and the TapNibbles publication gate."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, digest, hidden_flags
from local_release.github import complete_results
from local_release.profiles.tapnibbles import verify_aab


def jdk_bin():
    if os.environ.get('TAP148_JAVA_HOME'):
        return Path(os.environ['TAP148_JAVA_HOME']) / 'bin'
    keytool = shutil.which('keytool')
    return Path(keytool).resolve().parent if keytool else None


class TapNibblesAabSigningTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bin = jdk_bin()
        if not cls.bin or not all(shutil.which(str(cls.bin / name)) for name in ('java', 'jarsigner', 'keytool')):
            raise unittest.SkipTest('JDK 17+ required for real JAR signature fixtures')
        version = cls.jdk('java', '-version').stderr
        if not any(f'version "{major}.' in version or f'version "{major}"' in version for major in range(17, 40)):
            raise unittest.SkipTest('JDK 17+ required for real JAR signature fixtures')

    @classmethod
    def jdk(cls, command, *args):
        return subprocess.run([str(cls.bin / command), *map(str, args)],
                              capture_output=True, text=True, check=True, timeout=60, creationflags=hidden_flags())

    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix='tap148-')
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)

    def context(self, name, pin, build):
        sha = 'a' * 40
        directory = self.root / name / 'releases/tapnibbles' / f'1.0.0+{build}' / sha
        job = dict(schema=1, project='tapnibbles', sha=sha, run_id='tap148-fixture', version='1.0.0', build=build,
                   signing_certificate_sha256=pin, architectures={'android': ['arm64-v8a']},
                   required_steps={'windows': ['verify-aab']})
        atomic_json(directory / 'job.json', job)
        env = {'PATH': str(self.bin) + os.pathsep + os.environ['PATH']}
        context = Context(directory, {'environment': env}, host='windows')
        context.workspace.mkdir(parents=True)
        return context

    def gate(self, name, path, pin, build=1, error=None):
        ctx = self.context(name, pin, build)
        receipt = 'results/aab-signing.json'
        action = lambda: ctx.stage('verify-aab', lambda: verify_aab(ctx, path), [receipt])
        if error:
            with self.assertRaises(ReleaseError):
                action()
            self.assertIn(error, (ctx.directory / 'logs/windows/verify-aab.log').read_text(encoding='utf-8'))
            self.assertFalse((ctx.directory / receipt).exists())
            self.assertFalse(complete_results(ctx.directory, ctx.job))
        else:
            action()
            self.assertTrue((ctx.directory / receipt).is_file())
            self.assertTrue(complete_results(ctx.directory, ctx.job))

    def fixture(self):
        def field(number, value):
            self.assertLess(len(value), 128)
            return bytes([number << 3 | 2, len(value)]) + value

        manifest = field(3, b'manifest')
        for key, value in [(b'package', b'click.tapnibbles'), (b'versionName', b'1.0.0'), (b'versionCode', b'1')]:
            manifest += field(4, field(2, key) + field(3, value))
        path = self.root / 'unsigned.aab'
        with zipfile.ZipFile(path, 'w') as bundle:
            bundle.writestr('base/manifest/AndroidManifest.xml', field(1, manifest))
            bundle.writestr('BundleConfig.pb', b'fixture')
            bundle.writestr('base/dex/classes.dex', b'fixture')
            bundle.writestr('base/lib/arm64-v8a/libfixture.so', b'fixture')
            bundle.writestr('base/assets/empty.txt', b'')
        return path

    def sign(self, original, alias):
        key = self.root / (alias + '.p12')
        cert = self.root / (alias + '.cer')
        signed = self.root / (alias + '.aab')
        self.jdk('keytool', '-genkeypair', '-keystore', key, '-storepass', 'fixture-only', '-keyalg', 'RSA',
                 '-validity', 30, '-alias', alias, '-dname', 'CN=' + alias)
        self.jdk('keytool', '-exportcert', '-keystore', key, '-storepass', 'fixture-only', '-alias', alias, '-file', cert)
        self.jdk('jarsigner', '-keystore', key, '-storepass', 'fixture-only', '-signedjar', signed, original, alias)
        return signed, digest(cert)

    def append_payload(self, original):
        copy = self.root / 'partially-signed.aab'
        shutil.copyfile(original, copy)
        with zipfile.ZipFile(copy, 'a') as bundle:
            bundle.writestr('base/assets/tap148-unsigned.txt', b'added after signing')
        return copy

    def test_gate_accepts_pinned_self_signed_key_and_rejects_unsigned_or_wrong_signer(self):
        unsigned = self.fixture()
        signed, pin = self.sign(unsigned, 'expected')
        other, _ = self.sign(unsigned, 'other')
        self.gate('signed', signed, pin)
        self.gate('appended', self.append_payload(signed), pin, error='Unsigned JAR entry: base/assets/tap148-unsigned.txt')
        self.gate('wrong-signer', other, pin, error='JAR signer pin mismatch:')
        self.gate('unsigned', unsigned, pin, error='Unsigned JAR entry:')
        tampered = self.root / 'tampered.aab'
        with zipfile.ZipFile(signed) as before, zipfile.ZipFile(tampered, 'w') as after:
            for name in before.namelist():
                after.writestr(name, b'changed' if name == 'base/dex/classes.dex' else before.read(name))
        self.gate('tampered', tampered, pin, error='digest error for base/dex/classes.dex')

    @unittest.skipUnless(os.environ.get('TAP148_ORIGINAL_AAB'), 'opt-in original TapNibbles +14 package')
    def test_original_release_and_appended_copy(self):
        original = Path(os.environ['TAP148_ORIGINAL_AAB'])
        self.assertEqual(digest(original), 'baec21b679878a90d7ab7b44668f0902f5f7ff0d60f7f467c4add16bd980af80')
        pin = '7d01739a29bd4a4e1f7aeb4b08b0cc75b4f9fac32a4b4a64cb18f580fd5f7c47'
        self.gate('original', original, pin, build=14)
        copy = self.append_payload(original)
        self.gate('appended-original', copy, pin, build=14, error='Unsigned JAR entry: base/assets/tap148-unsigned.txt')
