"""TAP44 release packages, built on Windows by the shared coordinator."""
import hashlib
from contextlib import contextmanager, ExitStack
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys
import subprocess
from urllib.request import urlopen
import zipfile

from ..core import ReleaseError, atomic_json, digest, git, hidden_flags
from .ai11 import tools, verify_zip
from .playas import manifest_attributes

QUALITY = ['workflow-parity', 'release-metadata', 'app-names', 'node-tests',
           'tool-tests', 'dependencies', 'format', 'analyze', 'tests']
BUILD = ['web', 'web-zip', 'verify-web', 'apk', 'verify-apk', 'aab', 'verify-aab',
         'windows', 'windows-zip', 'verify-windows', 'package-metadata']
WORKFLOWS = {
    '.github/workflows/builds.yml': '4d5f7b1fdac55f9ede8995853a935aa376247ee3',
    '.github/workflows/checks.yml': '995f5c3ce28d1f7ce9835b1e4ae1c8299a47c6b9',
}


def metadata(repo, sha, profile):
    match = re.search(r'^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$',
                      git(repo, 'show', sha + ':pubspec.yaml'), re.M)
    if not match:
        raise ReleaseError('Cannot parse committed TapNibbles version')
    version, build = match[1], int(match[2])
    changelog = git(repo, 'show', sha + ':CHANGELOG.md')
    notes = re.search(r'(^## \[' + re.escape(version) + r'\].*?)(?=\n## |\Z)',
                      changelog, re.M | re.S)
    if not notes:
        raise ReleaseError('Missing TapNibbles changelog section')
    # Automatic prereleases include the implemented changes committed under
    # Unreleased while v1 is still being developed. Never read the dirty tree.
    pending = re.search(r'^## (?:Unreleased|\[Unreleased\])[^\n]*\n(.*?)(?=\n## |\Z)',
                        changelog, re.M | re.S)
    release_notes = (f'## {version}+{build}\n\n' + pending[1].strip()
                     if pending and pending[1].strip() else notes[1].strip())
    names = [f'tapnibbles-web-{version}+{build}.zip', f'tapnibbles-{version}+{build}.apk',
             f'tapnibbles-{version}+{build}.aab', f'tapnibbles-windows-x64-{version}+{build}.zip']
    return dict(version=version, build=build, tag=f'auto-v{version}-b{build}-{sha[:8]}',
        artifacts=names, release_prerelease=True, release_make_latest='false',
        release_notes=release_notes + '\n\nRelease-mode packages: Web, signed Android APK/AAB, Windows x64 portable ZIP. '
            'No store submission. Sentry integration is deferred to TAP27 by owner decision.',
        build_mode='release', store_ready=False, source_dirty=False, signing='Android release-keystore / unsigned Windows',
        sentry={'status': 'deferred', 'task': 'TAP27', 'owner_decision': '2026-11-03'},
        generated_source_overlays={'android/app/build.gradle.kts': hashlib.sha256(signing_gradle(repo, sha).encode()).hexdigest()},
        generated_output_paths=['linux/flutter/generated_plugin_registrant.cc',
            'linux/flutter/generated_plugins.cmake', 'macos/Flutter/GeneratedPluginRegistrant.swift',
            'windows/flutter/generated_plugin_registrant.cc', 'windows/flutter/generated_plugins.cmake'],
        required_steps={'windows': ['preflight', *QUALITY, 'backend-dependencies', 'integration-android', 'integration-web',
                                   'integration-windows', *BUILD]},
        artifact_specs={n: {'host': 'windows', 'gates': [g, 'package-metadata']} for n, g in
                        zip(names, ['verify-web', 'verify-apk', 'verify-aab', 'verify-windows'])},
        architectures={'android': ['armeabi-v7a', 'arm64-v8a', 'x86_64'],
                       'windows': ['x64'], 'web': ['javascript']},
        step_dependencies={'web-zip': ['web'], 'verify-web': ['web-zip'], 'verify-apk': ['apk'],
                           'verify-aab': ['aab'], 'windows-zip': ['windows'],
                           'verify-windows': ['windows-zip'], 'package-metadata': BUILD[:-1]})


def input_metadata(config):
    certificate = config.get('expected_signing_certificate_sha256', '').lower().replace(':', '')
    if not re.fullmatch('[a-f0-9]{64}', certificate):
        raise ReleaseError('Pin the owner Android release certificate')
    return {'signing_certificate_sha256': certificate,
            'signing_keystore_sha256': digest(Path(config['signing_store_file']))}


def signing_gradle(repo, sha):
    source = git(repo, 'show', sha + ':android/app/build.gradle.kts').rstrip() + '\n'
    if 'signingConfigs.getByName("debug")' not in source:
        if 'signingConfigs.getByName("release")' not in source:
            raise ReleaseError('Unknown Android signing recipe')
        return source
    # Deterministic signing-only adaptation allows the existing committed TAP10
    # source to serve as the trial without committing the owner's TAP13 work.
    source = 'import java.util.Properties\n\n' + source
    source = source.replace('android {', 'val releaseKey = Properties()\n'
        'val releaseKeyFile = rootProject.file("key.properties")\n'
        'if (releaseKeyFile.exists()) releaseKeyFile.inputStream().use { releaseKey.load(it) }\n\nandroid {', 1)
    source = source.replace('    buildTypes {', '    signingConfigs {\n        create("release") {\n'
        '            if (releaseKeyFile.exists()) {\n'
        '                storeFile = file(releaseKey.getProperty("storeFile"))\n'
        '                storePassword = releaseKey.getProperty("storePassword")\n'
        '                keyAlias = releaseKey.getProperty("keyAlias")\n'
        '                keyPassword = releaseKey.getProperty("keyPassword")\n'
        '            }\n        }\n    }\n\n    buildTypes {', 1)
    source = source.replace('            // TODO: Add your own signing config for the release build.\n'
        '            // Signing with the debug keys for now, so `flutter run --release` works.\n', '')
    return source.replace('signingConfigs.getByName("debug")', 'signingConfigs.getByName("release")')


def configure(ctx):
    for key, value in input_metadata(ctx.config).items():
        if ctx.job.get(key) != value:
            raise ReleaseError('Prepared TapNibbles signing input changed: ' + key)
    for name in ['SIGNING_KEY_ALIAS', 'SIGNING_KEY_PASSWORD', 'SIGNING_STORE_PASSWORD']:
        if not ctx.env.get(name):
            raise ReleaseError('Missing signing environment variable: ' + name)
    ctx.refresh_redaction([ctx.env['SIGNING_KEY_ALIAS']])
    ctx.env.update(JAVA_HOME=ctx.config['java_home'], ANDROID_HOME=ctx.config['android_sdk'])
    ctx.env['AI11_LOCAL_RELEASE_ENGINE'] = str(Path(__file__).resolve().parents[1])
    port = ctx.config.get('adb_server_port')
    if type(port) is not int or not 1024 <= port <= 65535 or port == 5037:
        raise ReleaseError('Configure a non-global TapNibbles adb_server_port')
    ctx.env.update(ANDROID_ADB_SERVER_PORT=str(port), ADB_SERVER_SOCKET=f'tcp:127.0.0.1:{port}')
    ctx.env['PATH'] = os.pathsep.join([str(Path(ctx.config['java_home']) / 'bin'),
        str(Path(ctx.config['flutter_sdk']) / 'bin'), ctx.env.get('PATH', '')])
    (ctx.workspace / 'android/local.properties').write_text(
        'sdk.dir=' + Path(ctx.config['android_sdk']).as_posix() + '\nflutter.sdk=' +
        Path(ctx.config['flutter_sdk']).as_posix() + '\n', encoding='utf-8')
    ctx.command([Path(ctx.config['android_sdk']) / 'platform-tools/adb.exe', '-P', str(port), 'start-server'], cwd=ctx.root)
    source = signing_gradle(ctx.workspace, ctx.job['sha'])
    if hashlib.sha256(source.encode()).hexdigest() != ctx.job['generated_source_overlays']['android/app/build.gradle.kts']:
        raise ReleaseError('Android signing overlay differs from pinned recipe')
    (ctx.workspace / 'android/app/build.gradle.kts').write_text(source, encoding='utf-8', newline='\n')
    def escaped(value):
        return str(value).replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')
    values = {'storeFile': Path(ctx.config['signing_store_file']).as_posix(),
        'keyAlias': ctx.env['SIGNING_KEY_ALIAS'], 'keyPassword': ctx.env['SIGNING_KEY_PASSWORD'],
        'storePassword': ctx.env['SIGNING_STORE_PASSWORD']}
    (ctx.workspace / 'android/key.properties').write_text(
        ''.join(k + '=' + escaped(v) + '\n' for k, v in values.items()), encoding='utf-8')


def preflight(ctx):
    configure(ctx)
    if sys.version_info[:2] != (3, 12):
        raise ReleaseError('TapNibbles pins Python 3.12')
    flutter = json.loads(ctx.command(['flutter', '--version', '--machine']))
    java = ctx.command(['java', '-version'])
    node = ctx.command(['node', '--version']).strip()
    node_version = re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)', node)
    if not node_version or tuple(map(int, node_version.groups())) < (22, 12, 0):
        raise ReleaseError('TapNibbles local backend requires Node >=22.12.0')
    if flutter['frameworkVersion'] != ctx.job['profile']['flutter'] or not re.search(r'version "17[.\"]', java):
        raise ReleaseError('TapNibbles requires Flutter 3.47.2 and JDK 17')
    ctx.command(['flutter', 'doctor', '-v'])
    atomic_json(ctx.directory / 'results/windows-environment.json', dict(
        sha=ctx.job['sha'], flutter=flutter, java=java, node=node, python=sys.version,
        platforms=['web', 'android', 'windows'], build_mode='release', store_ready=False,
        sentry=ctx.job['sentry'], signing_certificate_sha256=ctx.job['signing_certificate_sha256']))


def workflow_parity(ctx):
    # Read the original blobs even after the replaced YAML files are removed.
    for path, blob in WORKFLOWS.items():
        ctx.command(['git', 'cat-file', '-e', blob], cwd=ctx.workspace)
        current = ctx.workspace / path
        if current.exists() and git(ctx.workspace, 'hash-object', path) != blob:
            raise ReleaseError('Workflow changed; review the full local parity inventory: ' + path)
    atomic_json(ctx.directory / 'results/workflow-parity.json', {'source_blobs': WORKFLOWS,
        'quality_steps': QUALITY, 'build_steps': BUILD, 'excluded_targets': ['linux', 'macos', 'ios'],
        'owner_scope_decision': '2026-11-03', 'status': 'passed'})


def private_file(name):
    return Path(name).suffix.lower() in {'.map', '.pdb', '.debug', '.dSYM', '.jks', '.keystore', '.pem'} or name.endswith('.dart')


def pack(source, target):
    partial = target.with_suffix(target.suffix + '.partial')
    try:
        with zipfile.ZipFile(partial, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(source.rglob('*')):
                relative = path.relative_to(source).as_posix()
                if path.is_file() and not private_file(relative):
                    data = path.read_bytes()
                    if path.suffix == '.js':
                        data = re.sub(rb'(?m)^//# sourceMappingURL=.*\r?\n?', b'', data)
                    archive.writestr(relative, data)
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)


def verify_web(ctx, path):
    verify_zip(path, ['index.html', 'main.dart.js', 'flutter_bootstrap.js', 'version.json'])
    with zipfile.ZipFile(path) as archive:
        if any(private_file(n) for n in archive.namelist()):
            raise ReleaseError('Private debug/source data in public package')
        version = json.loads(archive.read('version.json'))
        if (version.get('version'), str(version.get('build_number'))) != (ctx.job['version'], str(ctx.job['build'])):
            raise ReleaseError('Web version/build mismatch')


def verify_apk(ctx, path):
    aapt, signer = tools(ctx)
    badging = ctx.command([aapt, 'dump', 'badging', path])
    expected = f"package: name='click.tapnibbles' versionCode='{ctx.job['build']}' versionName='{ctx.job['version']}'"
    if expected not in badging or not all("'" + abi + "'" in badging for abi in ctx.job['architectures']['android']):
        raise ReleaseError('APK identity/version/ABIs mismatch')
    signed = ctx.command([signer, 'verify', '--verbose', '--print-certs', path])
    certificate = re.search(r'Signer #1 certificate SHA-256 digest: ([a-fA-F0-9]+)', signed)
    if not certificate or certificate[1].lower() != ctx.job['signing_certificate_sha256']:
        raise ReleaseError('APK certificate differs from pinned owner release key')
    atomic_json(ctx.directory / 'results/android-signing.json', dict(
        sha=ctx.job['sha'], apk_sha256=digest(path), certificate_sha256=certificate[1].lower(),
        signing='release-keystore', build_mode='release', store_ready=False))


def verify_aab(ctx, path):
    verify_zip(path, ['BundleConfig.pb', 'base/manifest/AndroidManifest.xml', 'base/dex/classes.dex'])
    with zipfile.ZipFile(path) as archive:
        attrs = manifest_attributes(archive.read('base/manifest/AndroidManifest.xml'))
        expected = {'package': 'click.tapnibbles', 'versionName': ctx.job['version'], 'versionCode': str(ctx.job['build'])}
        if any(attrs.get(k) != v for k, v in expected.items()) or not all(
                any(n.startswith('base/lib/' + abi + '/') for n in archive.namelist())
                for abi in ctx.job['architectures']['android']):
            raise ReleaseError('AAB identity/version/ABIs mismatch')
    if 'jar verified.' not in ctx.command(['jarsigner', '-verify', path]):
        raise ReleaseError('AAB signature invalid')
    cert = re.search(r'SHA256:\s*([A-Fa-f0-9:]+)', ctx.command(['keytool', '-printcert', '-jarfile', path]))
    if not cert or cert[1].lower().replace(':', '') != ctx.job['signing_certificate_sha256']:
        raise ReleaseError('AAB certificate mismatch')
    atomic_json(ctx.directory / 'results/aab-signing.json', dict(aab_sha256=digest(path), signing='release-keystore'))


def verify_windows(ctx, path):
    verify_zip(path, ['tapnibbles.exe', 'flutter_windows.dll', 'data/app.so', 'data/icudtl.dat'])
    with zipfile.ZipFile(path) as archive:
        exe = archive.read('tapnibbles.exe')
        offset = struct.unpack_from('<I', exe, 0x3c)[0]
        if exe[offset:offset + 4] != b'PE\0\0' or struct.unpack_from('<H', exe, offset + 4)[0] != 0x8664:
            raise ReleaseError('Windows executable is not x64')
    executable = ctx.workspace / 'build/windows/x64/runner/Release/tapnibbles.exe'
    version = ctx.command(['powershell', '-NoProfile', '-Command',
        "(Get-Item -LiteralPath '" + str(executable).replace("'", "''") + "').VersionInfo.ProductVersion"])
    if version.strip() != f"{ctx.job['version']}+{ctx.job['build']}":
        raise ReleaseError('Windows executable version mismatch')


def integration(ctx, platform):
    from ..prerequisites import android_device, chrome_driver, child
    # DDC roots relative imports at the entrypoint directory. Web test files
    # share fixtures from ../test, so its generated entrypoint must be at the
    # project root. Native flutter test retains its integration_test target.
    target = 'tap44_web_integration.dart' if platform == 'web' else 'integration_test/tap44_release_test.dart'
    generated = ctx.workspace / target
    if generated.exists():
        raise ReleaseError('Generated integration entrypoint already exists')
    # Interactive real-account OAuth is accepted in TAP9, not replayed by an
    # unattended development build. All other test entrypoints are discovered.
    tests = sorted(p for p in (ctx.workspace / 'integration_test').glob('*_test.dart')
                   if p.name != 'google_flow_test.dart')
    if not tests:
        raise ReleaseError('No TapNibbles integration tests')
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
      // Flutter diagnostic trees can be empty in release mode. Preserve the
      // actual test exception and stack without changing its failure status.
      binding.results[description] = integration_common.Failure(
        description, '${details.exception}\n${details.stack ?? ""}',
      );
    }
  };
}
''', encoding='utf-8')
    try:
        if platform == 'android':
            # Finish Gradle before starting the emulator on the 16 GB host.
            # Concurrent cold boot/compilation caused system-service ANRs and
            # lost ADB forwards before the test isolate could start.
            defines = ['--dart-define-from-file=env/tap44.local.json',
                       '--dart-define=INTEGRATION_TEST_SHOULD_REPORT_RESULTS_TO_NATIVE=false']
            ctx.command(['flutter', 'build', 'apk', '--debug', '--target=' + target, *defines])
            test_apk = ctx.workspace / 'build/app/outputs/flutter-apk/app-debug.apk'
            if not test_apk.is_file():
                raise ReleaseError('Android integration APK was not produced before AVD startup')
            with android_device(ctx):
                adb = Path(ctx.config['android_sdk']) / 'platform-tools/adb.exe'
                prefix = [adb, '-P', str(ctx.config['adb_server_port']), '-s', ctx.config['android_device']]
                ports = [ctx.config['auth_port'], ctx.config['worker_port']]
                for port in ports:
                    ctx.command([*prefix, 'reverse', f'tcp:{port}', f'tcp:{port}'], cwd=ctx.root)
                try:
                    with child(ctx, [*prefix, 'logcat', '-v', 'threadtime', '-s',
                            'AndroidRuntime:E', 'libc:F', 'lmkd:I', 'ActivityManager:E'], 'android-system'):
                        ctx.command(['flutter', 'drive', '--debug', '--driver=test_driver/design_shell.dart',
                            '--target=' + target, '-d', ctx.config['android_device'], *defines,
                            '--use-application-binary=' + str(test_apk), '--keep-app-running'])
                finally:
                    try:
                        ctx.command([*prefix, 'shell', 'am', 'force-stop', 'click.tapnibbles'],
                                    cwd=ctx.root, cancellable=False)
                    except ReleaseError:
                        pass
                    for port in ports:
                        # A disconnected emulator must not replace the original
                        # Flutter/VM failure with a secondary cleanup error.
                        try:
                            ctx.command([*prefix, 'reverse', '--remove', f'tcp:{port}'], cwd=ctx.root, cancellable=False)
                        except ReleaseError:
                            pass
        elif platform == 'web':
            with chrome_driver(ctx):
                # WidgetTester text injection uses the debug-only client -1,
                # and keyboard simulation needs debug key names. Package
                # compilation remains release; all native test runners also
                # use debug mode for these same input scenarios.
                ctx.command(['flutter', 'drive', '--debug', '--driver=test_driver/design_shell.dart',
                    '--target=' + target, '-d', 'web-server', '--browser-name=chrome', '--headless',
                    '--dart-define-from-file=env/tap44.local.json',
                    '--driver-port=' + str(ctx.config['chromedriver_port']), '--web-port=' + str(ctx.config['web_port']),
                    '--web-browser-flag=--incognito', '--web-browser-flag=--user-data-dir=' +
                    str(ctx.root / ('w/chrome-TapNibbles-TAP44-' + ctx.job['sha'][:8]))])
        else:
            ctx.command(['flutter', 'test', target, '-d', 'windows',
                         '--dart-define-from-file=env/tap44.local.json', '--reporter=expanded'])
        atomic_json(ctx.directory / ('results/integration-' + platform + '.json'), dict(
            sha=ctx.job['sha'], platform=platform, test_build_mode='debug',
            **({'prebuilt_test_apk_sha256': digest(test_apk)} if platform == 'android' else {}),
            tests=[p.name for p in tests], status='passed'))
    finally:
        generated.unlink(missing_ok=True)


@contextmanager
def local_backend(ctx):
    from ..prerequisites import port_free, wait_ready
    from ..processes import terminate_tree
    backend = ctx.workspace / 'backend'
    ports = [ctx.config[k] for k in ['auth_port', 'worker_port', 'hub_port', 'logging_port']]
    if not all(port_free(p) for p in ports):
        raise ReleaseError('Dedicated TAP44 backend ports occupied; existing processes preserved')
    auth, worker, hub, logging = ports
    firebase = backend / '.tap44-firebase.json'
    atomic_json(firebase, {'emulators': {'auth': {'host': '127.0.0.1', 'port': auth},
        'hub': {'host': '127.0.0.1', 'port': hub}, 'logging': {'host': '127.0.0.1', 'port': logging},
        'ui': {'enabled': False}, 'singleProjectMode': True}})
    defines = ctx.workspace / 'env/tap44.local.json'
    atomic_json(defines, {'APP_ENV': 'local', 'BACKEND_API_URL': f'http://127.0.0.1:{worker}',
        'FIREBASE_PROJECT_ID': 'demo-tapnibbles', 'FIREBASE_API_KEY': 'LOCAL_EMULATOR_PLACEHOLDER',
        'FIREBASE_AUTH_EMULATOR_URL': f'http://127.0.0.1:{auth}'})
    node = shutil.which('node', path=ctx.env['PATH'])
    wrangler = backend / 'node_modules/wrangler/bin/wrangler.js'
    ctx.command([node, wrangler, 'd1', 'migrations', 'apply', 'DB', '--env', 'local', '--local'], cwd=backend)
    @contextmanager
    def launch(argv, name, url):
        log = ctx.directory / 'logs/windows' / (name + '.log')
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open('a', encoding='utf-8') as stream:
            process = subprocess.Popen([str(v) for v in argv], cwd=backend, env=ctx.env,
                stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT, creationflags=hidden_flags())
            try:
                def ready():
                    try:
                        with urlopen(url, timeout=1) as response:
                            return response.status == 200
                    except OSError:
                        return False
                wait_ready(ctx, ready, process, name, 90)
                yield
            finally:
                terminate_tree(process)
                process.wait(timeout=15)
    try:
        with ExitStack() as stack:
            stack.enter_context(launch([node, backend / 'node_modules/firebase-tools/lib/bin/firebase.js',
                'emulators:start', '--only', 'auth', '--project', 'demo-tapnibbles', '--config', firebase],
                'auth-emulator', f'http://127.0.0.1:{auth}/'))
            stack.enter_context(launch([node, wrangler, 'dev', '--env', 'local', '--ip', '127.0.0.1',
                '--port', str(worker), '--var', f'AUTH_EMULATOR_HOST:127.0.0.1:{auth}', '--var',
                f'ALLOWED_ORIGINS:http://localhost:{ctx.config["web_port"]},http://127.0.0.1:{ctx.config["web_port"]}'],
                'local-worker', f'http://127.0.0.1:{worker}/healthz'))
            yield
    finally:
        firebase.unlink(missing_ok=True)
        defines.unlink(missing_ok=True)


def package_metadata(ctx):
    atomic_json(ctx.directory / 'results/release-packages.json', dict(
        sha=ctx.job['sha'], version=ctx.job['version'], build=ctx.job['build'], source_dirty=False,
        build_mode='release', store_ready=False, signing=ctx.job['signing'], sentry=ctx.job['sentry'],
        packages={name: {'sha256': digest(ctx.output / name), 'size': (ctx.output / name).stat().st_size}
                  for name in ctx.job['artifacts']}))


def compile_target(ctx, target, kind=None):
    # Keep the project's existing build helper as the command source of truth.
    plan = json.loads(ctx.command(['python', 'tools/build.py', target, '--dry-run']))
    actual = plan['metadata']
    if any(actual[k] != ctx.job[k] for k in ['sha', 'version', 'build']):
        raise ReleaseError('Project build helper differs from the immutable job')
    commands = [c for c in plan['commands'] if kind is None or c[2] == kind]
    if len(commands) != 1:
        raise ReleaseError('Unexpected project build command plan')
    ctx.command(commands[0])


def _run(ctx):
    if ctx.host != 'windows':
        raise ReleaseError('TAP44 supports only its Windows builder')
    ctx.stage('preflight', lambda: preflight(ctx), always=True)
    ctx.stage('workflow-parity', lambda: workflow_parity(ctx), ['results/workflow-parity.json'])
    commands = {
        'release-metadata': ['python', 'tools/release.py', 'check'],
        'app-names': ['python', 'tools/sync_app_names.py', '--check'],
        'node-tests': ['node', '--test', 'tools/tests/app_names.test.cjs'],
        'tool-tests': ['python', '-m', 'unittest', 'discover', '-s', 'tools/tests', '-v'],
        'dependencies': ['flutter', 'pub', 'get'],
        'format': ['dart', 'format', '--output=none', '--set-exit-if-changed', 'lib', 'test'],
        'analyze': ['flutter', 'analyze'], 'tests': ['flutter', 'test', '--reporter=expanded'],
    }
    for name, argv in commands.items():
        ctx.stage(name, lambda argv=argv: ctx.command(argv))
    if not (ctx.workspace / '.dart_tool/package_config.json').exists():
        ctx.command(['flutter', 'pub', 'get'])
    phases = set(ctx.config.get('phases', ['quality', 'integration', 'build']))
    if 'integration' in phases:
        ctx.stage('backend-dependencies', lambda: ctx.command(['npm', 'ci'], cwd=ctx.workspace / 'backend'))
        with local_backend(ctx):
            for target in ['android', 'web', 'windows']:
                ctx.stage('integration-' + target, lambda target=target: integration(ctx, target),
                          ['results/integration-' + target + '.json'])
    if 'build' not in phases:
        return
    web, apk, aab, windows = [ctx.output / name for name in ctx.job['artifacts']]
    # pub runs again to restore production plugin registrants after integration_test.
    ctx.stage('web', lambda: compile_target(ctx, 'web'))
    ctx.stage('web-zip', lambda: pack(ctx.workspace / 'build/web', web), ['packages/' + web.name])
    ctx.stage('verify-web', lambda: verify_web(ctx, web))
    def android(kind, source, destination):
        compile_target(ctx, 'android', kind)
        shutil.copy2(ctx.workspace / source, destination)
    ctx.stage('apk', lambda: android('apk', 'build/app/outputs/flutter-apk/app-release.apk', apk), ['packages/' + apk.name])
    ctx.stage('verify-apk', lambda: verify_apk(ctx, apk), ['results/android-signing.json'])
    ctx.stage('aab', lambda: android('appbundle', 'build/app/outputs/bundle/release/app-release.aab', aab), ['packages/' + aab.name])
    ctx.stage('verify-aab', lambda: verify_aab(ctx, aab), ['results/aab-signing.json'])
    ctx.stage('windows', lambda: compile_target(ctx, 'windows'))
    ctx.stage('windows-zip', lambda: pack(ctx.workspace / 'build/windows/x64/runner/Release', windows), ['packages/' + windows.name])
    ctx.stage('verify-windows', lambda: verify_windows(ctx, windows))
    ctx.stage('package-metadata', lambda: package_metadata(ctx), ['results/release-packages.json'])


def run(ctx):
    try:
        _run(ctx)
    finally:
        (ctx.workspace / 'android/key.properties').unlink(missing_ok=True)
