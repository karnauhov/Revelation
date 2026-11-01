"""AI11's single Windows builder: personal signed APK, Web and Windows ZIPs."""

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

QUALITY = ['dependencies', 'analyze', 'tests', 'architecture', 'changelog', 'workflow-parity', 'tool-tests']
BUILD = ['apk', 'verify-apk', 'windows', 'windows-zip', 'verify-windows', 'web', 'web-zip', 'verify-web']


def metadata(repo, sha, profile):
    match = re.search(r'^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$', git(repo, 'show', sha + ':pubspec.yaml'), re.M)
    if not match:
        raise ReleaseError('Cannot parse committed AI11 version')
    version, build = match[1], int(match[2])
    notes = re.search(r'(^## \[' + re.escape(version) + r'\].*?)(?=\n## |\Z)',
                      git(repo, 'show', sha + ':CHANGELOG.md'), re.M | re.S)
    if not notes:
        raise ReleaseError('Missing AI11 changelog section')
    names = [f'ai11-{version}+{build}.apk', f'ai11-windows-x64-{version}+{build}.zip', f'ai11-web-{version}+{build}.zip']
    tags = [t for t in git(repo, 'tag', '--points-at', sha).splitlines() if t.startswith('v')]
    tag = tags[0] if tags else f'auto-v{version}-b{build}-{sha[:8]}'
    return dict(version=version, build=build, tag=tag, artifacts=names,
                release_notes=notes[1].strip() + '\n\nAndroid and Windows packages are for the owner. Android uses the configured release keystore. No store submission.',
                release_prerelease=not bool(tags), release_make_latest='true' if tags else 'false',
                required_steps={'windows': ['preflight', *QUALITY, *BUILD]},
                artifact_specs={n: {'host': 'windows', 'gates': [g]} for n, g in zip(names, ['verify-apk', 'verify-windows', 'verify-web'])},
                architectures={'android': ['armeabi-v7a', 'arm64-v8a', 'x86_64'], 'windows': ['x64'], 'web': ['javascript']},
                step_dependencies={'verify-apk': ['apk'], 'windows-zip': ['windows'], 'verify-windows': ['windows-zip'],
                                   'web-zip': ['web'], 'verify-web': ['web-zip']})


def compile_defines(config):
    values = read_json(Path(config['defines_file']))
    required = ['SUPABASE_URL', 'SUPABASE_PUBLISHABLE_KEY']
    if any(not isinstance(values.get(k), str) or not values[k].strip() for k in required):
        raise ReleaseError('AI11 requires Supabase URL and client publishable key')
    key = values[required[1]]
    if key.startswith('sb_secret_'):
        raise ReleaseError('Server credentials cannot enter a client build')
    if key.count('.') == 2:
        try:
            payload = json.loads(base64.urlsafe_b64decode(key.split('.')[1] + '==='))
        except (ValueError, UnicodeError):
            raise ReleaseError('Invalid client key') from None
        if payload.get('role') != 'anon':
            raise ReleaseError('Only an anon/publishable client key is allowed')
    return {k: values[k] for k in required}


def input_metadata(config):
    certificate = config.get('expected_signing_certificate_sha256', '').lower().replace(':', '')
    if not re.fullmatch('[a-f0-9]{64}', certificate):
        raise ReleaseError('Pin the release signing certificate SHA-256 in the host config')
    return {'compile_defines_sha256': hashlib.sha256(json.dumps(compile_defines(config), sort_keys=True).encode()).hexdigest(),
            'signing_certificate_sha256': certificate,
            'signing_keystore_sha256': digest(Path(config['signing_store_file']))}


def configure(ctx):
    for k, value in input_metadata(ctx.config).items():
        if ctx.job.get(k) != value:
            raise ReleaseError('Prepared AI11 compile/signing input changed: ' + k)
    ctx.result['compile_defines_sha256'] = ctx.job['compile_defines_sha256']
    for name in ['SIGNING_KEY_ALIAS', 'SIGNING_KEY_PASSWORD', 'SIGNING_STORE_PASSWORD']:
        if not ctx.env.get(name):
            raise ReleaseError('Missing signing environment variable: ' + name)
    ctx.env['JAVA_HOME'] = ctx.config['java_home']
    ctx.env['ANDROID_HOME'] = ctx.config['android_sdk']
    ctx.env['PATH'] = os.pathsep.join([str(Path(ctx.config['java_home']) / 'bin'),
                                     str(Path(ctx.config['flutter_sdk']) / 'bin'), ctx.env.get('PATH', '')])
    ctx.refresh_redaction([*compile_defines(ctx.config).values(), ctx.env['SIGNING_KEY_ALIAS']])
    atomic_json(ctx.workspace / 'env/dart_defines.json', compile_defines(ctx.config))
    # The existing Gradle release config reads this host-only file. It is never bundled.
    def escaped(value):
        return str(value).replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')
    values = {'storeFile': Path(ctx.config['signing_store_file']).as_posix(),
              'keyAlias': ctx.env['SIGNING_KEY_ALIAS'], 'keyPassword': ctx.env['SIGNING_KEY_PASSWORD'],
              'storePassword': ctx.env['SIGNING_STORE_PASSWORD']}
    (ctx.workspace / 'android/key.properties').write_text(''.join(k + '=' + escaped(v) + '\n' for k, v in values.items()), encoding='utf-8')
    flutter_sdk = Path(ctx.config['flutter_sdk']).as_posix()
    android_sdk = Path(ctx.config['android_sdk']).as_posix()
    (ctx.workspace / 'android/local.properties').write_text(f'sdk.dir={android_sdk}\nflutter.sdk={flutter_sdk}\n', encoding='utf-8')


def tools(ctx):
    candidates = [p for p in (Path(ctx.config['android_sdk']) / 'build-tools').iterdir()
                  if re.fullmatch(r'\d+(\.\d+)+', p.name)]
    latest = max(candidates, key=lambda p: tuple(map(int, p.name.split('.'))))
    return latest / 'aapt.exe', latest / 'apksigner.bat'


def preflight(ctx):
    configure(ctx)
    flutter = json.loads(ctx.command(['flutter', '--version', '--machine']))
    if flutter['frameworkVersion'] != ctx.job['profile']['flutter']:
        raise ReleaseError('Flutter differs from the pinned AI11 profile')
    java = ctx.command(['java', '-version'])
    if not re.search(r'version "17[.\"]', java):
        raise ReleaseError('AI11 Android builds require the existing Java 17 toolchain')
    ctx.command(['flutter', 'doctor', '-v'])
    if git(ctx.workspace, 'show', 'HEAD:pubspec.yaml') != (ctx.workspace / 'pubspec.yaml').read_text(encoding='utf-8').strip():
        raise ReleaseError('Builder pubspec differs from pinned source')
    ctx.command(['keytool', '-list', '-keystore', ctx.config['signing_store_file'],
                 '-alias', ctx.env['SIGNING_KEY_ALIAS'], '-storepass:env', 'SIGNING_STORE_PASSWORD'])
    atomic_json(ctx.directory / 'results/windows-environment.json', {'sha': ctx.job['sha'], 'flutter': flutter,
        'java': java.strip(), 'platforms': ['web', 'android', 'windows'], 'signing': 'release-keystore',
        'certificate_sha256': ctx.job['signing_certificate_sha256']})


def pack(source, target):
    if not source.is_dir():
        raise ReleaseError('Missing bundle directory: ' + str(source))
    partial = target.with_suffix(target.suffix + '.partial')
    try:
        with zipfile.ZipFile(partial, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(source.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(source).as_posix())
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)


def verify_zip(path, required):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() or not set(required) <= set(archive.namelist()):
            raise ReleaseError('Incomplete/corrupt package: ' + path.name)
        if any(n.startswith('/') or '..' in n.split('/') or '\\' in n for n in archive.namelist()):
            raise ReleaseError('Unsafe archive entry')


def verify_apk(ctx, path):
    aapt, signer = tools(ctx)
    badging = ctx.command([aapt, 'dump', 'badging', path])
    if not re.search(r"package: name='link.ai11' versionCode='" + str(ctx.job['build']) + r"' versionName='" + re.escape(ctx.job['version']) + "'", badging):
        raise ReleaseError('APK package/version/build mismatch')
    if not all("'" + abi + "'" in badging for abi in ctx.job['architectures']['android']):
        raise ReleaseError('APK omits a required ABI')
    signed = ctx.command([signer, 'verify', '--verbose', '--print-certs', path])
    cert = re.search(r'Signer #1 certificate SHA-256 digest: ([a-fA-F0-9]+)', signed)
    if not cert or cert[1].lower() != ctx.job['signing_certificate_sha256']:
        raise ReleaseError('APK release certificate differs from configured keystore')
    atomic_json(ctx.directory / 'results/android-signing.json', {'package': 'link.ai11', 'version': ctx.job['version'],
        'build': ctx.job['build'], 'sha': ctx.job['sha'], 'certificate_sha256': cert[1].lower(), 'signing': 'release-keystore',
        'personal_use': True, 'apk_sha256': digest(path)})


def verify_windows(ctx, path):
    verify_zip(path, ['ai11.exe', 'flutter_windows.dll', 'data/app.so', 'data/icudtl.dat'])
    with zipfile.ZipFile(path) as archive:
        exe = archive.read('ai11.exe')
        offset = struct.unpack_from('<I', exe, 0x3c)[0]
        if exe[offset:offset + 4] != b'PE\0\0' or struct.unpack_from('<H', exe, offset + 4)[0] != 0x8664:
            raise ReleaseError('Windows executable is not x64')
    executable = ctx.workspace / 'build/windows/x64/runner/Release/ai11.exe'
    version = ctx.command(['powershell', '-NoProfile', '-Command',
        "(Get-Item -LiteralPath '" + str(executable).replace("'", "''") + "').VersionInfo.ProductVersion"])
    if version.strip() != f"{ctx.job['version']}+{ctx.job['build']}":
        raise ReleaseError('Windows executable version/build mismatch')


def verify_web(ctx, path):
    verify_zip(path, ['index.html', '404.html', 'main.dart.js', 'flutter_bootstrap.js', 'version.json'])
    with zipfile.ZipFile(path) as archive:
        version = json.loads(archive.read('version.json'))
        if (version.get('version'), str(version.get('build_number'))) != (ctx.job['version'], str(ctx.job['build'])):
            raise ReleaseError('Web package version/build mismatch')


def run(ctx):
    if ctx.host != 'windows':
        raise ReleaseError('AI11 requires only its Windows builder')
    try:
        ctx.stage('preflight', lambda: preflight(ctx), always=True)
        commands = {
            'dependencies': ['flutter', 'pub', 'get'], 'analyze': ['dart', 'analyze'],
            'tests': ['flutter', 'test', '--no-pub', '--reporter=expanded'],
            'architecture': ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'tool/check_architecture_guard.ps1'],
            'changelog': ['python', 'tool/extract_changelog_section.py', '--check-only'],
            'workflow-parity': ['python', 'tool/local_release/inventory.py', '--check'],
            'tool-tests': ['python', '-m', 'unittest', 'discover', '-s', 'test/tool', '-v'],
        }
        for name, argv in commands.items():
            ctx.stage(name, lambda argv=argv: ctx.command(argv, cwd=ctx.workspace))
        # A restored checkout may need dependencies even with valid historical quality checkpoints.
        if not (ctx.workspace / '.dart_tool/package_config.json').exists():
            ctx.command(['flutter', 'pub', 'get'], cwd=ctx.workspace)
        apk, windows, web = [ctx.output / name for name in ctx.job['artifacts']]
        flags = ['--release', '--no-pub', '--dart-define-from-file=env/dart_defines.json']
        def build_apk():
            ctx.command(['flutter', 'build', 'apk', *flags], cwd=ctx.workspace)
            shutil.copy2(ctx.workspace / 'build/app/outputs/flutter-apk/app-release.apk', apk)
        ctx.stage('apk', build_apk, ['packages/' + apk.name])
        ctx.stage('verify-apk', lambda: verify_apk(ctx, apk), ['results/android-signing.json'])
        ctx.stage('windows', lambda: ctx.command(['flutter', 'build', 'windows', *flags]))
        ctx.stage('windows-zip', lambda: pack(ctx.workspace / 'build/windows/x64/runner/Release', windows), ['packages/' + windows.name])
        ctx.stage('verify-windows', lambda: verify_windows(ctx, windows))
        ctx.stage('web', lambda: ctx.command(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'tool/build_web_release.ps1'], cwd=ctx.workspace))
        ctx.stage('web-zip', lambda: pack(ctx.workspace / 'build/web', web), ['packages/' + web.name])
        ctx.stage('verify-web', lambda: verify_web(ctx, web))
    finally:
        # Keep the signing inputs only for the duration of the attempt.
        for relative in ['android/key.properties', 'env/dart_defines.json']:
            (ctx.workspace / relative).unlink(missing_ok=True)
