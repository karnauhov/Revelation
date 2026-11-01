"""Remove only newly observed LXD resources belonging to this command session."""

import json
import os
from pathlib import Path
import re
import subprocess
import threading

from .core import ReleaseError, atomic_json, read_json


def lxc(*arguments):
    result = subprocess.run(['lxc', '--project', 'snapcraft', *arguments], capture_output=True,
        text=True, timeout=20, check=False)
    if result.returncode:
        raise ReleaseError('Cannot inventory/clean Snapcraft LXD resources (exit ' + str(result.returncode) + ')')
    return result.stdout


def inventory():
    projects = json.loads(subprocess.run(['lxc', 'project', 'list', '--format=json'],
        capture_output=True, text=True, check=True, timeout=20).stdout)
    if not any(p['name'] == 'snapcraft' for p in projects):
        return {'instances': [], 'images': [], 'project_exists': False}
    return {'instances': json.loads(lxc('list', '--format=json')), 'project_exists': True,
            'images': json.loads(lxc('image', 'list', '--format=json'))}


def baseline(ctx):
    path = ctx.directory / 'results/linux-provider-baseline.json'
    if path.exists():
        ctx.provider_baseline = read_json(path)
        return
    # Only this provider has a verified ownership/cleanup implementation.
    provider = ctx.env.get('SNAPCRAFT_BUILD_ENVIRONMENT', 'lxd')
    if provider not in ('lxd', ''):
        raise ReleaseError('Ephemeral Snap requires LXD; configured provider has no safe cleanup adapter')
    ctx.env['SNAPCRAFT_BUILD_ENVIRONMENT'] = 'lxd'
    ctx.provider_baseline = inventory()
    atomic_json(path, ctx.provider_baseline)


def observe(ctx, process):
    """Capture LXD ownership while the Snapcraft PID still exists."""
    if not getattr(ctx, 'provider_baseline', None) or ctx.result.get('current_step') != 'snap':
        return None
    stop = threading.Event()
    owned = {}
    old = {item['name'] for item in ctx.provider_baseline['instances']}
    def sample():
        while not stop.is_set():
            try:
                for item in json.loads(lxc('list', '--format=json')):
                    name = item['name']
                    pid = int(item.get('config', {}).get('user.craft_providers.pid', 0))
                    if name not in old and pid > 0 and os.getsid(pid) == process.pid:
                        if name.startswith(('base-instance-snapcraft-', 'snapcraft-')):
                            owned[name] = item.get('config', {}).get('volatile.base_image')
            except (OSError, ValueError, ReleaseError, subprocess.SubprocessError):
                pass
            stop.wait(1)
    thread = threading.Thread(target=sample, daemon=True)
    thread.start()
    def finish():
        stop.set()
        thread.join(timeout=25)
        if thread.is_alive():
            raise ReleaseError('Provider inventory has not stopped; cleanup postponed')
        ctx.provider_baseline.setdefault('owned', {}).update(owned)
        atomic_json(ctx.directory / 'results/linux-provider-baseline.json', ctx.provider_baseline)
    return finish


def cleanup(ctx):
    path = ctx.directory / 'results/linux-provider-baseline.json'
    if not path.exists():
        return
    before, after = read_json(path), inventory()
    old_names = {i['name'] for i in before['instances']}
    new = {i['name']: i for i in after['instances'] if i['name'] not in old_names}
    owned = before.get('owned', {})
    if set(new) - set(owned):
        raise ReleaseError('New LXD resources have unproven ownership; preserved for review: ' + ', '.join(sorted(set(new) - set(owned))))
    for name in new:
        # Names come from a live inventory and an observed owned OS session.
        if not re.fullmatch(r'[a-zA-Z0-9-]+', name):
            raise ReleaseError('Unexpected LXD instance identity')
        lxc('delete', '--force', name)
    baseline_images = {i['fingerprint'] for i in before['images']}
    candidates = {i['fingerprint'] for i in after['images']} - baseline_images
    proven = {value for value in owned.values() if value}
    if candidates - proven:
        raise ReleaseError('New LXD images have unproven ownership; preserved for review')
    current = inventory()
    all_instances = (json.loads(subprocess.run(['lxc', 'list', '--all-projects', '--format=json'],
        capture_output=True, text=True, check=True, timeout=20).stdout) if candidates else [])
    for fingerprint in candidates:
        if any(i.get('config', {}).get('volatile.base_image') == fingerprint for i in current['instances'] + all_instances):
            raise ReleaseError('A preserved instance uses the new image; cleanup postponed')
        if not re.fullmatch(r'[0-9a-f]{64}', fingerprint):
            raise ReleaseError('Unexpected LXD image fingerprint')
        lxc('image', 'delete', fingerprint)
    final = inventory()
    if ({i['name'] for i in final['instances']} != old_names or
            {i['fingerprint'] for i in final['images']} != baseline_images):
        raise ReleaseError('LXD inventory differs from its baseline; inspect preserved resources')
    if before.get('project_exists') is False and final.get('project_exists'):
        subprocess.run(['lxc', 'project', 'delete', 'snapcraft'], capture_output=True,
                       text=True, check=True, timeout=20)
