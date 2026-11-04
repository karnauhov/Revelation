"""PLA299: private symbols, immutable inputs and resumable Sentry gates."""
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys
import zipfile
from urllib.parse import urlsplit

from ..core import ReleaseError, atomic_json, digest, read_json
from . import playas_android_symbols

PROJECT_ID = '4512369838456912'
SYMBOLS = list(playas_android_symbols.ABI_SYMBOLS.values())


def sentry_defines(values):
    dsn = str(values.get('SENTRY_DSN', '')).strip()
    parsed = urlsplit(dsn)
    if parsed.scheme != 'https' or not parsed.username or parsed.password or parsed.path != '/' + PROJECT_ID:
        raise ReleaseError('SENTRY_DSN must identify the dedicated Playas project')
    if parsed.hostname != 'o4511324523921408.ingest.de.sentry.io' or parsed.query or parsed.fragment:
        raise ReleaseError('Unexpected Playas Sentry ingest endpoint')
    if values.get('SENTRY_ENVIRONMENT') != 'production':
        raise ReleaseError('Set SENTRY_ENVIRONMENT=production explicitly')
    try:
        rate = float(values.get('SENTRY_TRACES_SAMPLE_RATE', ''))
    except (TypeError, ValueError):
        raise ReleaseError('SENTRY_TRACES_SAMPLE_RATE must be in 0..1') from None
    if not math.isfinite(rate) or not 0 <= rate <= 1:
        raise ReleaseError('SENTRY_TRACES_SAMPLE_RATE must be in 0..1')
    return {'SENTRY_DSN': dsn, 'SENTRY_ENVIRONMENT': 'production', 'SENTRY_TRACES_SAMPLE_RATE': str(rate)}


def pinned_cli(config):
    cli = Path(config.get('sentry_cli', ''))
    expected = config.get('sentry_cli_sha256', '')
    if not cli.is_file() or not re.fullmatch('[a-f0-9]{64}', expected) or digest(cli) != expected:
        raise ReleaseError('Pin and verify the Sentry CLI binary')
    return cli


def configure(ctx):
    if not ctx.config.get('sentry_required'):
        raise ReleaseError('This source requires Sentry-enabled host configuration')
    if ctx.config.get('sentry_privacy_approved') is not True:
        raise ReleaseError('Owner-approved privacy texts and Data Safety are required before production Sentry')
    pinned_cli(ctx.config)
    token = ctx.env.get('SENTRY_AUTH_TOKEN')
    if not token and ctx.config.get('sentry_properties'):
        source = Path(ctx.config['sentry_properties']).read_text(encoding='utf-8')
        match = re.search(r'^auth_token\s*[=:]\s*(\S+)', source, re.M)
        token = match[1] if match else None
    if not token:
        raise ReleaseError('Missing host-local Sentry upload credential')
    ctx.env.update(SENTRY_AUTH_TOKEN=token, SENTRY_ORG='ai11-link', SENTRY_PROJECT='playas-flutter',
                   SENTRY_RELEASE=f"playas@{ctx.job['version']}+{ctx.job['build']}", SENTRY_DIST=str(ctx.job['build']))
    ctx.refresh_redaction([token])


def private_file(name):
    parts = Path(name).parts
    return (any(part.startswith('.') or part.endswith('.dSYM') for part in parts)
            or Path(name).suffix.lower() in {'.map', '.symbols', '.pdb', '.debug', '.dart', '.bundle'}
            or Path(name).name in {'sentry.properties', 'sentry.read', 'source.bundle',
                                   'mapping.txt', 'native-symbols.json'})


def tree_hashes(root):
    if not root.is_dir():
        raise ReleaseError('Missing retained build output')
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_file():
            if not path.resolve().is_relative_to(root.resolve()):
                raise ReleaseError('Build output escapes retained directory')
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def identity(ctx):
    return {'sha': ctx.job['sha'], 'build': ctx.job['build'], 'version': ctx.job['version'],
            'defines': ctx.job['compile_defines_sha256'],
            'uploader': ctx.config.get('sentry_cli_sha256')}


def record(ctx, platform):
    root = ctx.workspace / 'build/web' if platform == 'web' else ctx.directory / 'private/android'
    files = tree_hashes(root)
    if not files or (platform == 'web' and not {'main.dart.js', 'main.dart.js.map', 'index.html'} <= files.keys()):
        raise ReleaseError('Missing final build or source maps')
    path = ctx.directory / f'results/sentry-{platform}-inputs.json'
    atomic_json(path, {'identity': identity(ctx), 'files': files})
    if platform == 'web' and ctx.result['steps'].get('web', {}).get('status') == 'passed':
        ctx.result['steps']['web']['outputs'] = {str(path.relative_to(ctx.directory).as_posix()): digest(path)}
        ctx.save()


def current(ctx, platform):
    try:
        saved = read_json(ctx.directory / f'results/sentry-{platform}-inputs.json')
        root = ctx.workspace / 'build/web' if platform == 'web' else ctx.directory / 'private/android'
        return saved['identity'] == identity(ctx) and saved['files'] == tree_hashes(root)
    except (OSError, KeyError, ValueError, ReleaseError):
        return False


def upload(ctx, platform):
    android_receipts = None
    args = ['dart', 'run', 'sentry_dart_plugin', '--sentry-define=bin_path=' + ctx.config['sentry_cli'],
            '--sentry-define=commits=false',
            '--sentry-define=wait_for_processing=true',
            '--sentry-define=upload_source_maps=' + str(platform == 'web').lower(),
            '--sentry-define=upload_debug_symbols=' + str(platform == 'android').lower()]
    if platform == 'android':
        root = ctx.directory / 'private/android'
        for target in ('apk', 'aab'):
            if not all((root / target / 'aot' / name).is_file() for name in SYMBOLS):
                raise ReleaseError('Missing AOT symbols for final ' + target + ' ABI set')
    else:
        root = ctx.workspace / 'build/web'
        # sourcesContent already embeds all app/package sources. upload_sources
        # adds './' in plugin 3.4.0 and scans unrelated maps across the checkout.
        args.extend(['--sentry-define=upload_sources=false',
                     '--sentry-define=web_build_path=' + str(root),
                     '--sentry-define=symbols_path=' + str(root),
                     '--sentry-define=build_path=' + str(root)])
    try:
        bounded = [ctx.config.get('python', sys.executable),
                   'tools/local_release/run_sentry_upload.py', '--timeout', '600', '--']
        if platform == 'android':
            android_receipts = playas_android_symbols.upload(ctx, root)
            for target in ('apk', 'aab'):
                aot = str(root / target / 'aot')
                ctx.command([*bounded, *args, '--sentry-define=symbols_path=' + aot,
                             '--sentry-define=build_path=' + aot])
            playas_android_symbols.verify_registry(ctx, android_receipts)
        else:
            ctx.command([*bounded, *args])
    finally:
        # Uploaders can inject Debug IDs into JS even when upload fails. Retain
        # that exact paired output for retry instead of forcing recompilation.
        record(ctx, platform)
    receipt = {
        'identity': identity(ctx), 'release': ctx.env['SENTRY_RELEASE'], 'dist': ctx.env['SENTRY_DIST'],
        'project': 'playas-flutter', 'processing': 'completed',
        'input_sha256': digest(ctx.directory / f'results/sentry-{platform}-inputs.json')}
    if android_receipts is not None:
        receipt['packages'] = android_receipts
    atomic_json(ctx.directory / f'results/sentry-{platform}.json', receipt)


def pack_web(ctx, target):
    root = ctx.workspace / 'build/web'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob('*')):
            name = path.relative_to(root).as_posix()
            if path.is_file() and not private_file(name):
                archive.write(path, name)


def verify_public_package(ctx, path):
    with zipfile.ZipFile(path) as archive:
        if any(private_file(name) for name in archive.namelist()):
            raise ReleaseError('Private diagnostics in public Playas package')
        token = ctx.env.get('SENTRY_AUTH_TOKEN')
        if token and any(token.encode() in archive.read(name) for name in archive.namelist()):
            raise ReleaseError('Host credential in public Playas package')


def build(ctx):
    from .playas import verify_apk, verify_aab, verify_web
    apk, aab, web = [ctx.output / name for name in ctx.job['artifacts']]
    flags = ['--release', '--dart-define-from-file=env/dart_defines.release.ci.json']
    native_root = ctx.directory / 'private/android'
    if not current(ctx, 'android'):
        for stage in ('apk', 'aab'):
            ctx.result['steps'].pop(stage, None)
            ctx.invalidate_dependents(stage)
    for name, command, source, target in [('apk','apk','build/app/outputs/flutter-apk/app-release.apk',apk),
            ('aab','appbundle','build/app/outputs/bundle/release/app-release.aab',aab)]:
        symbol_dir = native_root / name
        private = 'private/android/' + name + '/'
        outputs = ['packages/' + target.name, private + 'native-symbols.json', private + 'mapping.txt']
        outputs.extend(private + 'aot/' + symbol for symbol in SYMBOLS)
        def compile_native(command=command, source=source, target=target, symbol_dir=symbol_dir):
            aot = symbol_dir / 'aot'
            aot.mkdir(parents=True, exist_ok=True)
            ctx.command(['flutter', 'build', command, *flags, '--split-debug-info=' + str(aot)],
                        cwd=ctx.workspace, env={'SENTRY_EXCLUDE_AAB_MAPPING': 'true'})
            shutil.copy2(ctx.workspace / source, target)
            playas_android_symbols.retain(ctx, target, symbol_dir)
            record(ctx, 'android')
        ctx.stage(name, compile_native, outputs)
    record(ctx, 'android')
    ctx.stage('sentry-android', lambda: upload(ctx, 'android'), ['results/sentry-android.json'])
    for name, path, verifier in [('apk',apk,verify_apk), ('aab',aab,verify_aab)]:
        ctx.stage('verify-' + name, lambda path=path, verifier=verifier: verifier(ctx,path))
    if not current(ctx, 'web'):
        ctx.result['steps'].pop('web', None)
        ctx.invalidate_dependents('web')
    def compile_web():
        ctx.command(['flutter','build','web',*flags,'--source-maps','--no-wasm-dry-run','--no-tree-shake-icons'],cwd=ctx.workspace)
        record(ctx, 'web')
    ctx.stage('web', compile_web, ['results/sentry-web-inputs.json'])
    def sources():
        ctx.command(['dart','run','tools/prepare_sentry_web_source_maps.dart'],cwd=ctx.workspace)
        record(ctx, 'web')
    ctx.stage('web-sources', sources)
    ctx.stage('sentry-web', lambda: upload(ctx, 'web'), ['results/sentry-web.json'])
    # Recompute existing Flutter offline hashes after uploader mutation.
    def manifest():
        root = ctx.workspace / 'build/web'
        refresh_service_worker(root)
        hashes = {k:v for k,v in tree_hashes(root).items() if not private_file(k) and k != 'sentry-assets.json'}
        atomic_json(root / 'sentry-assets.json', {'release':ctx.env['SENTRY_RELEASE'],'dist':ctx.env['SENTRY_DIST'],'sha':ctx.job['sha'],'files':hashes})
        record(ctx, 'web')
    ctx.stage('web-manifest', manifest)
    ctx.stage('web-zip', lambda: pack_web(ctx, web), ['packages/' + web.name])
    ctx.stage('verify-web', lambda: verify_web(ctx, web))


def refresh_service_worker(root):
    worker = root / 'flutter_service_worker.js'
    if not worker.is_file():
        return False
    text = worker.read_text(encoding='utf-8')
    match = re.search(r'const RESOURCES = (\{.*?\});', text, re.S)
    if not match:
        # New Flutter builds ship a worker that unregisters the legacy cache.
        # It has no resource hashes, so preserve its exact generated bytes.
        if ('await self.registration.unregister();' in text and
                not re.search(r'\bcaches\.|addEventListener\s*\(\s*[\'\"]fetch[\'\"]', text)):
            return False
        raise ReleaseError('Unrecognized Flutter service worker resource manifest')
    bootstrap = root / 'flutter_bootstrap.js'
    if bootstrap.is_file():
        value = hashlib.md5((root / 'main.dart.js').read_bytes()).hexdigest()
        source = bootstrap.read_text(encoding='utf-8')
        source = re.sub(r'(serviceWorkerVersion\s*:\s*)["\'][^"\']*["\']', lambda m: m[1] + json.dumps(value), source)
        bootstrap.write_text(source, encoding='utf-8', newline='\n')
    previous = json.loads(match[1])
    hashes = {}
    for name in previous:
        path = root / ('index.html' if name == '/' else name)
        if not path.resolve().is_relative_to(root.resolve()):
            raise ReleaseError('Unsafe service worker resource')
        if path.is_file() and not private_file(name):
            hashes[name] = hashlib.md5(path.read_bytes()).hexdigest()
    text = text[:match.start(1)] + json.dumps(hashes, separators=(',', ':')) + text[match.end(1):]
    worker.write_text(text, encoding='utf-8', newline='\n')
    return True
