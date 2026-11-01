"""Bounded host telemetry independent of a valid job or writable build disk.

Quality gates remain authoritative in the normal result protocol. This channel
reports bootstrap, transfer and cleanup failures, never a fabricated passing gate.
"""

import json
import os
from pathlib import Path
import re
import tempfile
import time
import uuid

from .core import Redactor, ReleaseError, atomic_json, read_json
from .github import GitHub, credential


def settings(project):
    return (project['_config'] if '_config' in project else read_json(Path(project['config'])),
            project['_profile'] if '_profile' in project else read_json(Path(project['profile'])))


def redactor(config):
    values = [v for k, v in os.environ.items() if re.search('TOKEN|PASSWORD|SECRET|BASE64', k)]
    values.extend(v for k, v in config.get('environment', {}).items() if re.search('TOKEN|PASSWORD|SECRET|BASE64', k))
    for key in ('defines_file', 'github_token_file', 'sentry_properties'):
        path = Path(config[key]) if config.get(key) else None
        if not path or not path.is_file():
            continue
        content = path.read_text(encoding='utf-8').strip()
        if key == 'defines_file':
            values.extend(str(v) for v in json.loads(content).values())
        elif key == 'sentry_properties':
            values.extend(re.findall(r'(?m)^auth_token\s*[=:]\s*(.+)$', content))
        else:
            values.append(content)
    return Redactor(values)


def control(api, project):
    tag = 'ai11-local-reports-' + project
    marker = '<!-- ai11-host-reports:' + project + ':1 -->'
    release = next((r for r in api.pages('/releases') if r['tag_name'] == tag), None)
    if release:
        if not release['draft'] or marker not in (release.get('body') or ''):
            raise ReleaseError('Host report release ownership mismatch')
        return release
    return api.request('POST', '/releases', {'tag_name': tag, 'target_commitish': 'main',
        'name': 'Local builder diagnostics - ' + project, 'draft': True, 'body': marker})


def replace(api, release, name, payload):
    # RAM-backed on Ubuntu even when the persistent filesystem is full.
    folder = '/dev/shm' if os.name != 'nt' and Path('/dev/shm').is_dir() else None
    with tempfile.TemporaryDirectory(prefix='ai11-report-', dir=folder) as directory:
        path = Path(directory) / name
        atomic_json(path, payload)
        old = next((a for a in api.pages(f"/releases/{release['id']}/assets") if a['name'] == name), None)
        if old:
            api.request('DELETE', f"/releases/assets/{old['id']}")
        return api.upload_verified(release, path)


def publish(project, payload):
    config, profile = settings(project)
    token = credential(config)
    redact = redactor(config)
    redact.values.append(token)
    api = GitHub(profile['repository'], token)
    value = {**payload, 'schema': 1, 'project': profile['project'], 'host': 'linux', 'updated': time.time()}
    value = json.loads(redact(json.dumps(value, ensure_ascii=False)))
    if len(json.dumps(value).encode()) > 512 * 1024:
        raise ReleaseError('Host telemetry exceeds its bounded envelope')
    release = control(api, profile['project'])
    if value.get('phase') != 'building':
        # Final/bootstrap reports cannot be overwritten while Windows is offline.
        sha = value.get('sha', '')
        identity = sha if re.fullmatch(r'[a-f0-9]{40}', sha) else 'bootstrap'
        identifier = identity + '-' + str(time.time_ns()) + '-' + uuid.uuid4().hex
        replace(api, release, 'report-linux-' + identifier + '.json', value)
    return replace(api, release, 'latest-linux.json', value)


def report_failure(project, error, *, phase='bootstrap'):
    value = {'status': 'failed', 'phase': phase, 'error': str(error)}
    try:
        publish(project, value)
        return True
    except Exception as transfer_error:
        # One bounded outbox per project. Never spawn more attempts over it.
        value['transfer_error'] = str(transfer_error)
        try:
            redact = redactor(settings(project)[0])
        except (KeyError, OSError, ValueError):
            redact = redactor({})
        value = json.loads(redact(json.dumps(value)))
        try:
            atomic_json(outbox_path(project), value)
        except (OSError, KeyError):
            pass
        print('DIAGNOSTICS NOT DELIVERED: ' + value['transfer_error'], flush=True)
        return False


def outbox_path(project):
    return (Path(project['config']).with_suffix('.linux-outbox.json') if project.get('config') else
            Path(project['catalogue']) / 'linux-diagnostic-outbox.json')


def drain(project):
    for path in {outbox_path(project), Path(project['catalogue']) / 'linux-diagnostic-outbox.json'}:
        if path.exists():
            publish(project, read_json(path))
            path.unlink()


def collect_previous(project):
    path = Path(project['catalogue']) / 'linux-bootstrap-result.json'
    if path.exists():
        if path.stat().st_size > 512 * 1024:
            raise ReleaseError('Legacy bootstrap report exceeds its expected envelope; preserved')
        previous = read_json(path)
        publish(project, {'phase': 'previous-bootstrap', 'status': previous.get('status', 'failed'),
                          'error': str(previous.get('reason', 'Previous bootstrap failed'))})
        path.unlink()  # Only after verified remote history delivery.


def receive(project):
    config, profile = read_json(Path(project['config'])), read_json(Path(project['profile']))
    api = GitHub(profile['repository'], credential(config))
    marker = '<!-- ai11-host-reports:' + profile['project'] + ':1 -->'
    release = next((r for r in api.pages('/releases') if r['tag_name'] == 'ai11-local-reports-' + profile['project']), None)
    if not release:
        return
    if not release['draft'] or marker not in (release.get('body') or ''):
        raise ReleaseError('Host report release ownership mismatch')
    assets = [a for a in api.pages(f"/releases/{release['id']}/assets") if a['name'] == 'latest-linux.json' or
              re.fullmatch(r'report-linux-(?:[a-f0-9]{40}|bootstrap)-\d+-[a-f0-9]{32}\.json', a['name'])]
    for asset in assets:
        if asset['size'] > 512 * 1024:
            raise ReleaseError('Oversized host diagnostic')
        root = Path(project['catalogue']) / 'host-reports'
        destination = root / ('linux.json' if asset['name'] == 'latest-linux.json' else asset['name'])
        receipt = destination.with_suffix('.receipt.json')
        old = read_json(receipt) if receipt.exists() else {}
        if old.get('id') == asset['id'] and asset.get('digest') == 'sha256:' + old.get('sha256', ''):
            continue
        with tempfile.TemporaryDirectory(prefix='ai11-report-receive-') as folder:
            path = Path(folder) / 'report.json'
            checksum = api.download_asset(asset, path)
            value = read_json(path)
            if (value.get('schema'), value.get('project'), value.get('host')) != (1, profile['project'], 'linux'):
                raise ReleaseError('Host diagnostic identity mismatch')
            from .retention import deleted
            if re.fullmatch(r'[a-f0-9]{40}', value.get('sha', '')) and deleted(Path(project['catalogue']), profile['project'], value['sha']):
                continue
            atomic_json(destination, value)
            atomic_json(receipt, {'id': asset['id'], 'sha256': checksum})


def purge_build(project, sha, api):
    """Confirmed deletion also removes this SHA's diagnostic history."""
    name = project['project']
    release = next((r for r in api.pages('/releases') if r['tag_name'] == 'ai11-local-reports-' + name), None)
    expression = re.compile(r'report-linux-' + re.escape(sha) + r'-\d+-[a-f0-9]{32}\.json$')
    if release:
        if not release['draft'] or '<!-- ai11-host-reports:' + name + ':1 -->' not in (release.get('body') or ''):
            raise ReleaseError('Diagnostic release ownership mismatch; deletion preserved')
        for asset in api.pages(f"/releases/{release['id']}/assets"):
            remove = bool(expression.fullmatch(asset['name']))
            if asset['name'] == 'latest-linux.json' and asset['size'] <= 512 * 1024:
                with tempfile.TemporaryDirectory(prefix='ai11-report-delete-') as folder:
                    path = Path(folder) / 'report.json'
                    api.download_asset(asset, path)
                    remove = read_json(path).get('sha') == sha
            if remove:
                api.request('DELETE', f"/releases/assets/{asset['id']}")
    from .core import inside
    root = Path(project['catalogue']) / 'host-reports'
    if root.exists():
        for path in root.glob('*.json'):
            filename = path.name.replace('.receipt.json', '.json')
            remove = bool(expression.fullmatch(filename))
            if path.name == 'linux.json':
                remove = read_json(path).get('sha') == sha
                if remove:
                    inside(root, 'linux.receipt.json').unlink(missing_ok=True)
            if remove:
                inside(root, path.name).unlink(missing_ok=True)
