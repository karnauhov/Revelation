"""TAP150 buildable reset base, using the existing shared package verifier."""
import hashlib
import json
from pathlib import Path
import re
import sys

from ..core import ReleaseError, atomic_json, digest, git
from . import tapnibbles as packages

QUALITY = ['release-metadata', 'app-names', 'node-tests', 'tool-tests',
           'dependencies', 'format', 'analyze', 'tests']
BUILD = packages.BUILD
SOURCE = 'tools/local_release/bootstrap_profile.py'
LOADED_ADAPTER_SHA256 = digest(Path(__file__))


def metadata(repo, sha, profile):
    expected = profile.get('adapter_sha256')
    if profile.get('adapter_source') != SOURCE or not re.fullmatch('[a-f0-9]{64}', str(expected)):
        raise ReleaseError('Pin the versioned TapNibbles reset adapter')
    committed = (git(repo, 'show', sha + ':' + SOURCE) + '\n').encode('utf-8')
    if hashlib.sha256(committed).hexdigest() != expected or LOADED_ADAPTER_SHA256 != expected:
        raise ReleaseError('Committed, installed and profile-pinned TapNibbles adapters differ')
    result = packages.metadata(repo, sha, profile)
    result['required_steps'] = {'windows': ['preflight', *QUALITY,
        'integration-android', 'integration-web', 'integration-windows', *BUILD]}
    result['baseline'] = 'ui-reset'
    result['adapter_source_sha256'] = expected
    result['release_notes'] = result['release_notes'].replace(
        'Sentry integration is deferred to TAP27 by owner decision.',
        'This build contains the empty rebuild base; product UI is implemented incrementally. '
        'Sentry is not connected in this base.')
    result['sentry'] = {'status': 'not_implemented', 'scope': 'new UI-led implementation'}
    return result


input_metadata = packages.input_metadata


def preflight(ctx):
    packages.configure(ctx)
    if sys.version_info[:2] != (3, 12):
        raise ReleaseError('TapNibbles pins Python 3.12')
    flutter = json.loads(ctx.command(['flutter', '--version', '--machine']))
    java = ctx.command(['java', '-version'])
    node = ctx.command(['node', '--version']).strip()
    match = re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)', node)
    if not match or tuple(map(int, match.groups())) < (22, 12, 0):
        raise ReleaseError('TapNibbles packaging checks require Node >=22.12.0')
    if flutter['frameworkVersion'] != ctx.job['profile']['flutter'] or not re.search(r'version "17[.\"]', java):
        raise ReleaseError('TapNibbles requires Flutter 3.47.2 and JDK 17')
    ctx.command(['flutter', 'doctor', '-v'])
    atomic_json(ctx.directory / 'results/windows-environment.json', dict(
        sha=ctx.job['sha'], flutter=flutter, java=java, node=node, python=sys.version,
        platforms=['web', 'android', 'windows'], build_mode='release', store_ready=False,
        baseline='ui-reset', sentry=ctx.job['sentry'],
        adapter_source_sha256=ctx.job['adapter_source_sha256'],
        signing_certificate_sha256=ctx.job['signing_certificate_sha256']))


def integration(ctx, platform):
    from ..prerequisites import android_device, chrome_driver
    target = 'tap150_web_integration.dart' if platform == 'web' else 'integration_test/tap150_release_test.dart'
    generated = ctx.workspace / target
    if generated.exists():
        raise ReleaseError('Generated integration entrypoint already exists')
    tests = sorted((ctx.workspace / 'integration_test').glob('*_test.dart'))
    if not tests:
        raise ReleaseError('No committed startup integration tests')
    generated.write_text(
        "import 'package:flutter_test/flutter_test.dart' show reportTestException;\n"
        "import 'package:integration_test/integration_test.dart' show IntegrationTestWidgetsFlutterBinding;\n"
        "import 'package:integration_test/common.dart' as integration_common;\n" +
        '\n'.join("import '" + ('integration_test/' if platform == 'web' else '') + p.name +
                  "' as t" + str(i) + ';' for i, p in enumerate(tests)) +
        '\nvoid main() {\n' + ''.join('t' + str(i) + '.main();\n' for i in range(len(tests))) + r'''
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  final previousReporter = reportTestException;
  reportTestException = (details, description) {
    try {
      previousReporter(details, description);
    } finally {
      binding.results[description] = integration_common.Failure(
        description, '${details.exception}\n${details.stack ?? ""}',
      );
    }
  };
}
''', encoding='utf-8')
    try:
        if platform == 'android':
            defines = ['--dart-define=INTEGRATION_TEST_SHOULD_REPORT_RESULTS_TO_NATIVE=false']
            ctx.command(['flutter', 'build', 'apk', '--debug', '--target-platform=android-x64', '--target=' + target, *defines])
            test_apk = ctx.workspace / 'build/app/outputs/flutter-apk/app-debug.apk'
            if not test_apk.is_file():
                raise ReleaseError('Android startup test APK is missing')
            with android_device(ctx):
                adb = Path(ctx.config['android_sdk']) / 'platform-tools/adb.exe'
                prefix = [adb, '-P', str(ctx.config['adb_server_port']), '-s', ctx.config['android_device']]
                try:
                    ctx.command(['flutter', 'drive', '--debug', '--driver=test_driver/integration_test.dart',
                        '--target=' + target, '-d', ctx.config['android_device'], *defines,
                        '--use-application-binary=' + str(test_apk), '--keep-app-running'])
                finally:
                    try:
                        ctx.command([*prefix, 'shell', 'am', 'force-stop', 'click.tapnibbles'],
                                    cwd=ctx.root, cancellable=False)
                    except ReleaseError:
                        pass
        elif platform == 'web':
            with chrome_driver(ctx):
                ctx.command(['flutter', 'drive', '--debug', '--driver=test_driver/integration_test.dart',
                    '--target=' + target, '-d', 'web-server', '--browser-name=chrome', '--headless',
                    '--driver-port=' + str(ctx.config['chromedriver_port']), '--web-port=' + str(ctx.config['web_port']),
                    '--web-browser-flag=--incognito', '--web-browser-flag=--user-data-dir=' +
                    str(ctx.root / ('w/chrome-TapNibbles-TAP150-' + ctx.job['sha'][:8]))])
        else:
            ctx.command(['flutter', 'test', target, '-d', 'windows', '--reporter=expanded'])
        atomic_json(ctx.directory / ('results/integration-' + platform + '.json'), dict(
            sha=ctx.job['sha'], platform=platform, test_build_mode='debug',
            **({'prebuilt_test_apk_sha256': digest(test_apk)} if platform == 'android' else {}),
            tests=[p.name for p in tests], status='passed',
            scope='Committed first-frame tests; product scenarios are added with their UI tasks'))
    finally:
        generated.unlink(missing_ok=True)


def run(ctx):
    try:
        if ctx.host != 'windows':
            raise ReleaseError('This TapNibbles profile uses its existing Windows builder')
        ctx.stage('preflight', lambda: preflight(ctx), always=True)
        commands = {
            'release-metadata': ['python', 'tools/release.py', 'check'],
            'app-names': ['python', 'tools/sync_app_names.py', '--check'],
            'node-tests': ['node', '--test', 'tools/tests/app_names.test.cjs'],
            'tool-tests': ['python', '-m', 'unittest', 'discover', '-s', 'tools/tests', '-v'],
            'dependencies': ['flutter', 'pub', 'get'],
            'format': ['dart', 'format', '--output=none', '--set-exit-if-changed', 'lib', 'test', 'integration_test', 'test_driver'],
            'analyze': ['flutter', 'analyze'],
            'tests': ['flutter', 'test', '--reporter=expanded'],
        }
        for name, argv in commands.items():
            ctx.stage(name, lambda argv=argv: ctx.command(argv))
        phases = set(ctx.config.get('phases', ['quality', 'integration', 'build']))
        if 'integration' in phases:
            for target in ['android', 'web', 'windows']:
                ctx.stage('integration-' + target, lambda target=target: integration(ctx, target),
                          ['results/integration-' + target + '.json'])
        if 'build' not in phases:
            return
        web, apk, aab, windows = [ctx.output / name for name in ctx.job['artifacts']]
        ctx.stage('web', lambda: packages.compile_target(ctx, 'web'))
        ctx.stage('web-zip', lambda: packages.pack(ctx.workspace / 'build/web', web), ['packages/' + web.name])
        ctx.stage('verify-web', lambda: packages.verify_web(ctx, web))
        def android(kind, source, destination):
            packages.compile_target(ctx, 'android', kind)
            import shutil
            shutil.copy2(ctx.workspace / source, destination)
        ctx.stage('apk', lambda: android('apk', 'build/app/outputs/flutter-apk/app-release.apk', apk), ['packages/' + apk.name])
        ctx.stage('verify-apk', lambda: packages.verify_apk(ctx, apk), ['results/android-signing.json'])
        ctx.stage('aab', lambda: android('appbundle', 'build/app/outputs/bundle/release/app-release.aab', aab), ['packages/' + aab.name])
        ctx.stage('verify-aab', lambda: packages.verify_aab(ctx, aab), ['results/aab-signing.json'])
        ctx.stage('windows', lambda: packages.compile_target(ctx, 'windows'))
        ctx.stage('windows-zip', lambda: packages.pack(ctx.workspace / 'build/windows/x64/runner/Release', windows), ['packages/' + windows.name])
        ctx.stage('verify-windows', lambda: packages.verify_windows(ctx, windows))
        ctx.stage('package-metadata', lambda: packages.package_metadata(ctx), ['results/release-packages.json'])
    finally:
        (ctx.workspace / 'android/key.properties').unlink(missing_ok=True)
