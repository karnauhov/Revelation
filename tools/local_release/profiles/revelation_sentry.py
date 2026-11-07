"""REV305: keep native Dart symbols private and gate each final build on upload."""
from ..core import ReleaseError, atomic_json, digest


def build_flags(target):
    return ['--split-debug-info=build/sentry/' + target]


def identity_args(ctx):
    return ['--sentry-define=org=ai11-link', '--sentry-define=project=revelation-flutter',
            '--sentry-define=release=revelation@' + ctx.job['version'] + '+' + str(ctx.job['build']),
            '--sentry-define=dist=' + str(ctx.job['build']),
            '--sentry-define=commits=false', '--sentry-define=wait_for_processing=true']


def upload_native(ctx, target):
    root = ctx.workspace / 'build/sentry' / target
    expected = (['app.android-arm.symbols', 'app.android-arm64.symbols', 'app.android-x64.symbols']
                if target in ('apk', 'aab') else ['app.' + target + '-x64.symbols'])
    files = [root / name for name in expected]
    if any(not path.is_file() or path.stat().st_size == 0 for path in files):
        raise ReleaseError('Missing final ' + target + ' Dart debug symbols; rebuild that target')
    build = 'build/app' if target in ('apk', 'aab') else 'build/' + target
    ctx.command(['dart', 'run', 'sentry_dart_plugin', *identity_args(ctx),
                 '--sentry-define=upload_source_maps=false',
                 '--sentry-define=upload_debug_symbols=true',
                 '--sentry-define=symbols_path=build/sentry/' + target,
                 '--sentry-define=build_path=' + build])
    # A receipt exists only after a successful uploader, and is tied to source
    # identity and exact symbol bytes. Packaging never includes this directory.
    atomic_json(ctx.directory / ('results/sentry-' + target + '.json'), {
        'sha': ctx.job['sha'], 'release': 'revelation@' + ctx.job['version'] + '+' + str(ctx.job['build']),
        'dist': str(ctx.job['build']), 'target': target,
        'symbols': {path.name: digest(path) for path in files}, 'processing': 'completed',
    })
