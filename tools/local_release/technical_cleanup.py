"""Archive verified release logs once, then retire owned technical drafts."""

import base64
import json
from pathlib import Path
import re
import tempfile
import zipfile

from .core import Redactor, ReleaseError, atomic_json, digest, lock, read_json
from .github import GitHub, GitHubHTTPError, complete_results, credential
from .host_reports import redactor, receive


def _upload_log_archive(api, release, entries, index, redact, previous):
    with tempfile.TemporaryDirectory(prefix='ai11-final-logs-') as folder:
        path = Path(folder) / 'logs.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, source in sorted(entries.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, redact(source.read_text(encoding='utf-8', errors='replace')).encode('utf-8'))
            info = zipfile.ZipInfo('index.json', date_time=(1980, 1, 1, 0, 0, 0))
            archive.writestr(info, json.dumps(index, sort_keys=True))
        checksum = digest(path)
        path = path.rename(path.with_name('build-logs-' + checksum[:12] + '.zip'))
        api.verified_assets = {previous['archive']['id']: previous['archive']} if previous.get('archive') else {}
        uploaded = api.upload_verified(release, path)
        if uploaded.get('sha256', checksum) != checksum:
            raise ReleaseError('Uploaded diagnostic checksum mismatch')
        return {**uploaded, 'sha256': checksum, 'asset_name': path.name}


def archive_job(ctx, api, release):
    """Archive verified logs/results before retiring final transport payloads."""
    job = ctx.job
    publication = read_json(ctx.directory / 'publication.json')
    if (not publication.get('published') or release.get('draft') or release['id'] != publication.get('release_id')
            or release['tag_name'] != job['tag'] or publication.get('sha') != job['sha']
            or not complete_results(ctx.directory, job)):
        raise ReleaseError('Log archival requires the complete verified published source')
    values = list(redactor(ctx.config).values) + [getattr(api, 'token', '')]
    values.extend(str(value) for key, value in ctx.config.get('environment', {}).items() if re.search('TOKEN|PASSWORD|SECRET|BASE64|KEY', key))
    defines = Path(ctx.config['defines_file']) if ctx.config.get('defines_file') else None
    if defines and defines.is_file():
        values.extend(base64.b64encode((key + '=' + str(value)).encode()).decode() for key, value in read_json(defines).items())
    clean = Redactor(values)
    receipt_path = ctx.directory / 'results/build-logs.json'
    outbox = ctx.directory / 'results/build-logs-outbox.json'
    try:
        with lock(ctx.directory / '.build-logs.lock', timeout=5):
            previous = read_json(receipt_path) if receipt_path.exists() else {}
            if previous and previous.get('sha') != job['sha']:
                raise ReleaseError('Log archive receipt belongs to another source')
            saved = previous.get('archive', {})
            if previous.get('closed') and saved:
                asset = next((a for a in api.pages(f"/releases/{release['id']}/assets") if a['id'] == saved['id']), None)
                if asset:
                    if (asset['name'] != 'build-logs-' + saved['sha256'][:12] + '.zip' or asset['size'] != saved['size']
                            or asset.get('digest') and asset['digest'] != 'sha256:' + saved['sha256']):
                        raise ReleaseError('Published log archive differs from its verified receipt')
                    if not asset.get('digest'):
                        with tempfile.TemporaryDirectory(prefix='ai11-logs-readback-') as folder:
                            if api.download_asset(asset, Path(folder) / 'logs.zip') != saved['sha256']:
                                raise ReleaseError('Published log archive read-back mismatch')
                    outbox.unlink(missing_ok=True)
                    return previous
                if previous.get('reports'):
                    raise ReleaseError('Missing archived host reports require verified restoration; exchange preserved')
            entries = {}
            excluded = {'build-logs.json', 'build-logs-outbox.json', 'exchange-closed.json', 'exchange-cleanup.json'}
            for branch in ('logs', 'results'):
                for path in sorted((ctx.directory / branch).rglob('*')):
                    if not path.is_file() or path.name in excluded or path.suffix not in ('.log', '.json', '.info', '.html', '.csv', '.txt'):
                        continue
                    if not path.resolve().is_relative_to(ctx.directory.resolve()):
                        raise ReleaseError('Diagnostic path escapes the release catalogue')
                    if path.stat().st_size > 32 * 1024**2:
                        raise ReleaseError('Diagnostic file exceeds the bounded archive contract')
                    entries[path.relative_to(ctx.directory).as_posix()] = path
            if sum(p.stat().st_size for p in entries.values()) > 512 * 1024**2:
                raise ReleaseError('Diagnostic archive exceeds its bounded contract')
            index = {key: job[key] for key in ('project', 'sha', 'run_id', 'version', 'build')}
            index.update(schema=1, files=sorted(entries))
            uploaded = _upload_log_archive(api, release, entries, index, clean, previous)
            record = {'schema': 1, 'sha': job['sha'], 'archive': uploaded, 'reports': {},
                      'release_id': release['id'], 'read_back_verified': True, 'closed': True}
            atomic_json(receipt_path, record)
            outbox.unlink(missing_ok=True)
            return record
    except Exception as error:
        atomic_json(outbox, {'pending': True, 'sha': job['sha'], 'error': clean(str(error)),
                            'action': 'Retry published log archival; source logs and transfer assets are preserved'})
        raise


def finish(project, *, api=None):
    root = Path(project['catalogue'])
    profile, config = read_json(Path(project['profile'])), read_json(Path(project['config']))
    jobs = [p.parent for p in (root / 'releases' / project['project']).glob('*/*/job.json')]
    if not jobs:
        return False
    from .retention import deleted
    jobs = [p for p in jobs if not deleted(root, project['project'], p.name)]
    if not jobs or any(not (p / 'publication.json').exists() or not read_json(p / 'publication.json').get('published')
                       or not (p / 'results/exchange-closed.json').exists()
                       or not read_json(p / 'results/exchange-closed.json').get('closed') for p in jobs):
        return False
    api = api or GitHub(profile['repository'], credential(config))
    drafts = [r for r in api.pages('/releases') if r['tag_name'] == 'ai11-local-reports-' + project['project']]
    if not drafts:
        return True
    draft = drafts[0]
    marker = '<!-- ai11-host-reports:' + project['project'] + ':1 -->'
    if len(drafts) != 1 or not draft['draft'] or marker not in (draft.get('body') or ''):
        raise ReleaseError('Diagnostic draft ownership mismatch; preserved')
    receive(project)
    latest = root / 'host-reports/linux.json'
    diagnostic = read_json(latest) if latest.exists() else {}
    if diagnostic.get('phase') != 'cleaned' or diagnostic.get('status') != 'built':
        return False  # Keep actionable bootstrap/build/Stop/transfer failures.
    directory = next((p for p in jobs if p.name == diagnostic.get('sha')), None)
    if not directory:
        return False
    job = read_json(directory / 'job.json')
    if not complete_results(directory, job):
        raise ReleaseError('Cannot retire diagnostics with incomplete release gates')
    with lock(directory / '.build-logs.lock', timeout=5):
        assets = api.pages(f"/releases/{draft['id']}/assets")
        entries = {}
        report_ids = {}
        for asset in assets:
            name = asset['name']
            if name != 'latest-linux.json' and not re.fullmatch(r'report-linux-(?:[a-f0-9]{40}|bootstrap)-\d+-[a-f0-9]{32}\.json', name):
                raise ReleaseError('Unknown diagnostic asset; draft preserved')
            path = root / 'host-reports' / ('linux.json' if name == 'latest-linux.json' else name)
            receipt = read_json(path.with_suffix('.receipt.json'))
            if receipt['id'] != asset['id'] or asset.get('digest') != 'sha256:' + digest(path):
                raise ReleaseError('Diagnostic Windows receipt differs from the remote draft')
            entries['host-reports/' + name] = path
            report_ids[name] = {'id': asset['id'], 'sha256': receipt['sha256']}
        for path in sorted((directory / 'logs').glob('*/*.log')):
            if not path.resolve().is_relative_to(directory.resolve()):
                raise ReleaseError('Log path escapes the release catalogue')
            entries[path.relative_to(directory).as_posix()] = path
        for host in job['required_steps']:
            entries['results/' + host + '.json'] = directory / 'results' / (host + '.json')
        for name in ('linux-packages.json', 'linux-snap-script.json'):
            if (directory / 'results' / name).is_file():
                entries['results/' + name] = directory / 'results' / name
        redact = redactor(config)
        redact.values.append(api.token)
        record_path = directory / 'results/build-logs.json'
        previous = read_json(record_path) if record_path.exists() else {}
        publication = read_json(directory / 'publication.json')
        release = api.request('GET', f"/releases/{publication['release_id']}")
        if release['draft'] or release['tag_name'] != job['tag']:
            raise ReleaseError('Logs require the verified published release')
        uploaded = _upload_log_archive(api, release, entries,
            {'schema': 1, 'project': job['project'], 'sha': job['sha'], 'run_id': job['run_id'],
             'version': job['version'], 'build': job['build'], 'reports': report_ids}, redact, previous)
        # Receipt is durable before deleting any old draft/archive. There is no
        # permanent second local ZIP: canonical Windows logs remain individual.
        record = {'schema': 1, 'sha': job['sha'], 'archive': uploaded, 'reports': report_ids,
                  'draft_id': draft['id'], 'closed': False}
        atomic_json(record_path, record)
        current = api.pages(f"/releases/{draft['id']}/assets")
        if {(a['id'], a.get('digest')) for a in current} != {(a['id'], a.get('digest')) for a in assets}:
            return False  # Linux sent fresh data during verification; receive it next cycle.
        api.request('DELETE', f"/releases/{draft['id']}")
        try:
            api.request('GET', f"/releases/{draft['id']}")
        except GitHubHTTPError as error:
            if error.status != 404:
                raise
        else:
            raise ReleaseError('Diagnostic draft still exists after deletion')
        old = previous.get('archive')
        if old and old['id'] != uploaded['id']:
            api.request('DELETE', f"/releases/assets/{old['id']}")
        record['closed'] = True
        atomic_json(record_path, record)
    return True
