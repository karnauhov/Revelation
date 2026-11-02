"""ClearFix: one Windows host, Web ZIP, signed APK/AAB, Windows ZIP/Store MSIX."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import zipfile

from ..core import ReleaseError, atomic_json, digest, git, read_json
from .ai11 import pack, tools, verify_zip
from .playas import manifest_attributes

SENTRY_CLI_SHA256 = '99c1bf7a3d18df2b62ee5052f7e8f5d1e065e218442cdf0cfa2ede0b9cf7b938'

QUALITY = ['dependencies', 'firebase-config', 'analyze', 'legacy', 'legal-html',
           'workflow-parity', 'apple-config', 'tool-tests', 'tests', 'coverage',
           'coverage-threshold', 'changelog', 'store-config']
BUILD = ['reset-web', 'web', 'web-manifest', 'sentry-web', 'web-zip', 'verify-web',
         'reset-android', 'apk', 'verify-apk', 'aab', 'verify-aab', 'sentry-android',
         'windows-dependencies', 'windows-patches', 'windows', 'sentry-windows',
         'windows-zip', 'verify-windows', 'msix', 'verify-msix']
KEYS = {
    'android': ['CFX_FIREBASE_ANDROID_API_KEY', 'SENTRY_DSN', 'SENTRY_ENVIRONMENT', 'SENTRY_TRACES_SAMPLE_RATE'],
    'web': ['CFX_FIREBASE_WEB_API_KEY', 'CFX_WEB_PUSH_VAPID_PUBLIC_KEY', 'SENTRY_DSN', 'SENTRY_ENVIRONMENT', 'SENTRY_TRACES_SAMPLE_RATE'],
    'windows': ['CFX_FIREBASE_WEB_API_KEY', 'CFX_WINDOWS_GOOGLE_CLIENT_ID', 'CFX_WINDOWS_GOOGLE_CLIENT_SECRET',
                'CFX_WINDOWS_FACEBOOK_APP_ID', 'CFX_WINDOWS_FACEBOOK_APP_SECRET', 'CFX_WINDOWS_OAUTH_REDIRECT_HOST',
                'CFX_WINDOWS_OAUTH_REDIRECT_PORT', 'SENTRY_DSN', 'SENTRY_ENVIRONMENT', 'SENTRY_TRACES_SAMPLE_RATE'],
}


def metadata(repo, sha, profile):
    pubspec = git(repo, 'show', sha + ':pubspec.yaml')
    match = re.search(r'^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$', pubspec, re.M)
    if not match:
        raise ReleaseError('Cannot parse committed ClearFix version')
    version, build = match[1], int(match[2])
    major, minor, patch = map(int, version.split('.'))
    msix = f'{major}.{minor}.{patch + build}.0'
    if not re.search(r'^  msix_version: ' + re.escape(msix) + r'\s*$', pubspec, re.M):
        raise ReleaseError('ClearFix Store version is not synchronized')
    notes = re.search(r'(^##[ \t]+(?:\[' + re.escape(version) + r'\]|' + re.escape(version) + r')(?=[ \t\r\n]|$).*?)(?=\n##[ \t]+|\Z)',
                      git(repo, 'show', sha + ':CHANGELOG.md'), re.M | re.S)
    if not notes:
        raise ReleaseError('Missing ClearFix changelog section')
    names = [f'clear_fix-web-{version}+{build}.zip', f'clear_fix-{version}+{build}.apk',
             f'clear_fix-{version}+{build}.aab', f'clear_fix-windows-x64-{version}+{build}.zip',
             f'clear_fix-windows-store-x64-{msix}.msix']
    tags = [tag for tag in git(repo, 'tag', '--points-at', sha).splitlines() if tag.startswith('v')]
    return dict(version=version, build=build, msix_version=msix,
        tag=tags[0] if tags else f'auto-v{version}-b{build}-{sha[:8]}', artifacts=names,
        release_notes=notes[1].strip().removesuffix('---').strip(),
        release_prerelease=not bool(tags), release_make_latest='true' if tags else 'false',
        required_steps={'windows': ['preflight', *QUALITY, *BUILD]},
        generated_output_paths=['coverage/lcov.info'],
        artifact_specs={name: {'host': 'windows', 'gates': [gate]} for name, gate in
                        zip(names, ['verify-web', 'verify-apk', 'verify-aab', 'verify-windows', 'verify-msix'])},
        architectures={'android': ['armeabi-v7a', 'arm64-v8a', 'x86_64'], 'windows': ['x64'], 'web': ['javascript']},
        step_dependencies={'web-manifest': ['web'], 'sentry-web': ['web-manifest'], 'web-zip': ['sentry-web'],
            'verify-web': ['web-zip'], 'verify-apk': ['apk'], 'verify-aab': ['aab'],
            'sentry-android': ['apk', 'aab'], 'windows-patches': ['windows-dependencies'],
            'windows': ['windows-patches'], 'sentry-windows': ['windows'], 'windows-zip': ['sentry-windows'],
            'verify-windows': ['windows-zip'], 'msix': ['windows'], 'verify-msix': ['msix']})


def compile_defines(config):
    values = read_json(Path(config['defines_file']))
    values['SENTRY_ENVIRONMENT'] = 'production'
    result = {}
    for platform, keys in KEYS.items():
        if any(not str(values.get(key, '')).strip() for key in (keys[0], 'SENTRY_DSN')):
            raise ReleaseError('Missing ClearFix Firebase/Sentry client configuration for ' + platform)
        result[platform] = {key: values[key] for key in keys if key in values}
    return result


def input_metadata(config):
    certificate = config.get('expected_signing_certificate_sha256', '').lower().replace(':', '')
    if not re.fullmatch('[a-f0-9]{64}', certificate):
        raise ReleaseError('Pin the existing ClearFix Android release certificate')
    if digest(Path(config['sentry_cli'])) != SENTRY_CLI_SHA256:
        raise ReleaseError('ClearFix Sentry CLI differs from the audited Windows x64 2.58.6 binary')
    return dict(compile_defines_sha256=hashlib.sha256(json.dumps(compile_defines(config), sort_keys=True).encode()).hexdigest(),
                signing_certificate_sha256=certificate, signing_keystore_sha256=digest(Path(config['signing_store_file'])),
                firebase_config_sha256=digest(Path(config['firebase_config_file'])),
                sentry_cli_sha256=digest(Path(config['sentry_cli'])))


def configure(ctx):
    if any(ctx.job.get(key) != value for key, value in input_metadata(ctx.config).items()):
        raise ReleaseError('Prepared ClearFix compile/signing/tool input changed')
    values = compile_defines(ctx.config)
    ctx.result['compile_defines_sha256'] = ctx.job['compile_defines_sha256']
    token = ctx.env.get('SENTRY_AUTH_TOKEN')
    if not token:
        source = Path(ctx.config['sentry_properties']).read_text(encoding='utf-8')
        match = re.search(r'^auth_token\s*[=:]\s*(.+?)\s*$', source, re.M)
        token = match[1] if match else None
    if not token:
        raise ReleaseError('ClearFix requires Sentry upload authentication')
    ctx.env['SENTRY_AUTH_TOKEN'] = token
    for key in ['SIGNING_KEY_ALIAS', 'SIGNING_KEY_PASSWORD', 'SIGNING_STORE_PASSWORD']:
        if not ctx.env.get(key):
            raise ReleaseError('Missing Android release signing variable: ' + key)
    ctx.env.update(JAVA_HOME=ctx.config['java_home'], ANDROID_HOME=ctx.config['android_sdk'],
                   AI11_LOCAL_RELEASE_ENGINE=str(Path(__file__).resolve().parents[1]))
    ctx.env['PATH'] = os.pathsep.join([str(Path(ctx.config['java_home']) / 'bin'),
                                     str(Path(ctx.config['flutter_sdk']) / 'bin'), ctx.env.get('PATH', '')])
    secrets = [token, ctx.env['SIGNING_KEY_ALIAS'], *[value for defines in values.values() for value in defines.values()]]
    ctx.refresh_redaction([*secrets, *[base64.b64encode(f'{key}={value}'.encode()).decode()
        for defines in values.values() for key, value in defines.items()]])
    for platform, defines in values.items():
        atomic_json(ctx.workspace / f'env/dart_defines.{platform}.ci.json', defines)
    def escaped(value):
        return str(value).replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')
    properties = dict(storeFile=Path(ctx.config['signing_store_file']).as_posix(), keyAlias=ctx.env['SIGNING_KEY_ALIAS'],
                      keyPassword=ctx.env['SIGNING_KEY_PASSWORD'], storePassword=ctx.env['SIGNING_STORE_PASSWORD'])
    (ctx.workspace / 'android/key.properties').write_text(''.join(key + '=' + escaped(value) + '\n' for key, value in properties.items()), encoding='utf-8')
    (ctx.workspace / 'android/local.properties').write_text('sdk.dir=' + Path(ctx.config['android_sdk']).as_posix() +
        '\nflutter.sdk=' + Path(ctx.config['flutter_sdk']).as_posix() + '\n', encoding='utf-8')
    shutil.copy2(ctx.config['firebase_config_file'], ctx.workspace / 'android/app/google-services.json')


def disk(ctx, minimum=4, estimated=0):
    ctx.command(['python', 'tool/check_ci_disk_headroom.py', '--path', ctx.workspace,
                 '--minimum-free-gib', str(minimum), '--estimated-consumption-gib', str(estimated),
                 '--label', ctx.result.get('current_step', 'preflight')], cwd=ctx.workspace)


def preflight(ctx):
    configure(ctx)
    flutter = json.loads(ctx.command(['flutter', '--version', '--machine'], cwd=ctx.workspace))
    if flutter['frameworkVersion'] != ctx.job['profile']['flutter']:
        raise ReleaseError('Flutter differs from pinned ClearFix profile')
    java = ctx.command(['java', '-version'], cwd=ctx.workspace)
    if not re.search(r'version "17[.\"]', java):
        raise ReleaseError('ClearFix requires JDK17')
    cli = ctx.command([ctx.config['sentry_cli'], '--version'], cwd=ctx.workspace)
    if '2.58.6' not in cli:
        raise ReleaseError('ClearFix requires the audited Sentry CLI 2.58.6')
    disk(ctx, 4, 14)
    atomic_json(ctx.directory / 'results/windows-environment.json', dict(sha=ctx.job['sha'], flutter=flutter,
        java=java, sentry_cli=cli, platforms=['web', 'android', 'windows']))


def coverage(ctx):
    hit = total = 0
    active = False
    path = ctx.workspace / 'coverage/lcov.info'
    for line in path.read_text().splitlines():
        if line.startswith('SF:'):
            active = '/lib/' in '/' + line[3:].replace('\\', '/')
        if active and line.startswith('DA:'):
            total += 1
            hit += int(line.split(',')[1]) > 0
    if not total or hit / total < .70:
        raise ReleaseError(f'ClearFix coverage {hit}/{total} is below 70%')
    shutil.copy2(path, ctx.directory / 'results/windows-lcov.info')
    atomic_json(ctx.directory / 'results/coverage.json', dict(hit=hit, total=total, percent=100 * hit / total, threshold=70))


def verify_apk(ctx, path):
    aapt, signer = tools(ctx)
    badging = ctx.command([aapt, 'dump', 'badging', path], cwd=ctx.workspace)
    expected = f"package: name='click.clearfix' versionCode='{ctx.job['build']}' versionName='{ctx.job['version']}'"
    if expected not in badging or not all("'" + abi + "'" in badging for abi in ctx.job['architectures']['android']):
        raise ReleaseError('ClearFix APK identity/version/ABIs mismatch')
    signed = ctx.command([signer, 'verify', '--verbose', '--print-certs', path], cwd=ctx.workspace)
    cert = re.search(r'Signer #1 certificate SHA-256 digest: ([a-fA-F0-9]+)', signed)
    if not cert or cert[1].lower() != ctx.job['signing_certificate_sha256']:
        raise ReleaseError('ClearFix APK certificate mismatch')
    atomic_json(ctx.directory / 'results/android-signing.json', dict(package='click.clearfix', version=ctx.job['version'],
        build=ctx.job['build'], sha=ctx.job['sha'], certificate_sha256=cert[1].lower(), apk_sha256=digest(path)))


def verify_aab(ctx, path):
    verify_zip(path, ['BundleConfig.pb', 'base/manifest/AndroidManifest.xml', 'base/dex/classes.dex'])
    with zipfile.ZipFile(path) as archive:
        attrs = manifest_attributes(archive.read('base/manifest/AndroidManifest.xml'))
        expected = dict(package='click.clearfix', versionName=ctx.job['version'], versionCode=str(ctx.job['build']))
        if any(attrs.get(key) != value for key, value in expected.items()):
            raise ReleaseError('ClearFix AAB identity/version mismatch')
        if not all(any(name.startswith('base/lib/' + abi + '/') for name in archive.namelist()) for abi in ctx.job['architectures']['android']):
            raise ReleaseError('ClearFix AAB omits ABI')
    if 'jar verified.' not in ctx.command(['jarsigner', '-verify', path], cwd=ctx.workspace):
        raise ReleaseError('ClearFix AAB signature invalid')
    cert = ctx.command(['keytool', '-printcert', '-jarfile', path], cwd=ctx.workspace)
    match = re.search(r'SHA256:\s*([A-Fa-f0-9:]+)', cert)
    if not match or match[1].lower().replace(':', '') != ctx.job['signing_certificate_sha256']:
        raise ReleaseError('ClearFix AAB certificate mismatch')


def pack_web(ctx, path):
    # Retain source maps for recovery/Sentry, exclude them from the public package.
    temporary = path.with_suffix('.zip.partial')
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            root = ctx.workspace / 'build/web'
            for source in sorted(root.rglob('*')):
                if source.is_file() and source.suffix != '.map':
                    archive.write(source, source.relative_to(root).as_posix())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def verify_web(ctx, path):
    verify_zip(path, ['index.html', '404.html', '.nojekyll', 'main.dart.js', 'flutter_bootstrap.js',
                     'version.json', 'loader_manifest.json', 'privacy_policy.html', 'license_agreement.html'])
    with zipfile.ZipFile(path) as archive:
        if any(name.endswith('.map') for name in archive.namelist()):
            raise ReleaseError('Public ClearFix Web package contains source maps')
        version = json.loads(archive.read('version.json'))
        if (version.get('version'), str(version.get('build_number'))) != (ctx.job['version'], str(ctx.job['build'])):
            raise ReleaseError('ClearFix Web version/build mismatch')


def verify_windows(ctx, path):
    verify_zip(path, ['clear_fix.exe', 'flutter_windows.dll', 'data/app.so', 'data/icudtl.dat'])
    with zipfile.ZipFile(path) as archive:
        exe = archive.read('clear_fix.exe')
        offset = struct.unpack_from('<I', exe, 0x3c)[0]
        if exe[offset:offset + 4] != b'PE\0\0' or struct.unpack_from('<H', exe, offset + 4)[0] != 0x8664:
            raise ReleaseError('ClearFix Windows executable is not x64')
    executable = ctx.workspace / 'build/windows/x64/runner/Release/clear_fix.exe'
    actual = ctx.command(['powershell', '-NoProfile', '-Command',
        "(Get-Item -LiteralPath '" + str(executable).replace("'", "''") + "').VersionInfo.ProductVersion"], cwd=ctx.workspace)
    if actual.strip() != f"{ctx.job['version']}+{ctx.job['build']}":
        raise ReleaseError('ClearFix Windows executable version/build mismatch')


def reset(ctx):
    # Flutter state from tests must not leak dev-only plugins into release builds.
    ctx.command(['flutter', 'clean'], cwd=ctx.workspace)
    ctx.command(['flutter', 'pub', 'get'], cwd=ctx.workspace)
    disk(ctx, 6)


def sentry(ctx, platform):
    disk(ctx, 1)
    ctx.command(['dart', 'run', 'sentry_dart_plugin', '--sentry-define=bin_path=' + ctx.config['sentry_cli'],
        '--sentry-define=' + ('upload_debug_symbols=false' if platform == 'web' else 'upload_source_maps=false')], cwd=ctx.workspace)


def powershell(ctx, script):
    ctx.command(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script])


def run(ctx):
    if ctx.host != 'windows':
        raise ReleaseError('ClearFix uses only its Windows builder')
    try:
        ctx.stage('preflight', lambda: preflight(ctx), always=True)
        phases = set(ctx.config.get('phases', ['quality', 'build']))
        if 'quality' in phases:
            commands = {
                'dependencies': ['flutter', 'pub', 'get'],
                'firebase-config': ['python', 'tool/validate_google_services_config.py', 'android/app/google-services.json.example', 'android/app/google-services.json'],
                'analyze': ['dart', 'analyze'], 'legacy': ['python', 'tool/check_ui_legacy_violations.py'],
                'legal-html': ['python', 'tool/check_legal_document_html_sync.py'],
                'workflow-parity': ['python', 'tool/check_release_workflow.py'],
                'apple-config': ['python', 'tool/check_apple_project.py'],
                'tool-tests': ['python', '-m', 'unittest', 'discover', '-s', 'tool/tests', '-v'],
                'tests': ['flutter', 'test', '--no-pub', '--reporter=expanded'],
                'coverage': ['flutter', 'test', '--no-pub', '--coverage', '--reporter=expanded'],
                'changelog': ['python', 'tool/extract_changelog_section.py', '--check-only'],
                'store-config': ['python', 'tool/windows_msix.py'],
            }
            for name, argv in commands.items():
                ctx.stage(name, lambda argv=argv: ctx.command(argv, cwd=ctx.workspace))
            ctx.stage('coverage-threshold', lambda: coverage(ctx), ['results/coverage.json', 'results/windows-lcov.info'])
        if 'build' not in phases:
            return
        web, apk, aab, windows, msix = [ctx.output / name for name in ctx.job['artifacts']]
        ctx.stage('reset-web', lambda: reset(ctx))
        ctx.stage('web', lambda: ctx.command(['flutter', 'build', 'web', '--release', '--source-maps', '--no-wasm-dry-run',
            '--no-pub', '--dart-define-from-file=env/dart_defines.web.ci.json'], cwd=ctx.workspace))
        ctx.stage('web-manifest', lambda: ctx.command(['python', 'tool/generate_web_loader_manifest.py', '--web-build-dir', 'build/web'], cwd=ctx.workspace))
        ctx.stage('sentry-web', lambda: sentry(ctx, 'web'))
        ctx.stage('web-zip', lambda: pack_web(ctx, web), ['packages/' + web.name])
        ctx.stage('verify-web', lambda: verify_web(ctx, web))
        ctx.stage('reset-android', lambda: reset(ctx))
        for name, command, source, dest in [('apk', 'apk', 'build/app/outputs/flutter-apk/app-release.apk', apk),
                                            ('aab', 'appbundle', 'build/app/outputs/bundle/release/app-release.aab', aab)]:
            def build(command=command, source=source, dest=dest):
                disk(ctx, 4)
                flags = ['--no-pub'] if command == 'appbundle' else []
                ctx.command(['flutter', 'build', command, '--release', *flags,
                    '--dart-define-from-file=env/dart_defines.android.ci.json'], cwd=ctx.workspace)
                shutil.copy2(ctx.workspace / source, dest)
            ctx.stage(name, build, ['packages/' + dest.name])
            verifier = verify_apk if name == 'apk' else verify_aab
            ctx.stage('verify-' + name, lambda verifier=verifier, dest=dest: verifier(ctx, dest))
        ctx.stage('sentry-android', lambda: sentry(ctx, 'android'))
        ctx.stage('windows-dependencies', lambda: ctx.command(['flutter', 'pub', 'get']))
        ctx.stage('windows-patches', lambda: powershell(ctx, 'tool/patch_windows_firebase_cpp_sdk.ps1'))
        ctx.stage('windows', lambda: ctx.command(['flutter', 'build', 'windows', '--release', '--no-tree-shake-icons',
            '--dart-define-from-file=env/dart_defines.windows.ci.json']))
        ctx.stage('sentry-windows', lambda: sentry(ctx, 'windows'))
        ctx.stage('windows-zip', lambda: pack(ctx.workspace / 'build/windows/x64/runner/Release', windows), ['packages/' + windows.name])
        ctx.stage('verify-windows', lambda: verify_windows(ctx, windows))
        def package_msix():
            powershell(ctx, 'tool/pack_windows_msix.ps1')
            shutil.copy2(ctx.workspace / 'release' / msix.name, msix)
        ctx.stage('msix', package_msix, ['packages/' + msix.name])
        ctx.stage('verify-msix', lambda: ctx.command(['python', 'tool/windows_msix.py', '--package', msix], cwd=ctx.workspace))
    finally:
        for relative in ['android/key.properties', *[f'env/dart_defines.{platform}.ci.json' for platform in KEYS]]:
            (ctx.workspace / relative).unlink(missing_ok=True)
