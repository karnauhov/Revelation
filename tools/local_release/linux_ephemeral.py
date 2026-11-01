"""Linux is a disposable executor; Windows/GitHub own durable build history."""

import contextlib
import importlib
import json
import os
from pathlib import Path
import threading
import tempfile
import time

from .core import Context, ReleaseError, atomic_json, digest, inside, read_json, lock


def receipt_path(root, project, sha):
    import re
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', project) or not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ReleaseError('Invalid Linux receipt identity')
    root = Path(root).resolve()
    path = root / 'linux-receipts' / project / (sha + '.json')
    if path.resolve() != path.absolute() or not path.resolve().is_relative_to(root):
        raise ReleaseError('Linux receipt path is linked outside its managed root')
    return path


def already_delivered(root, project, sha, assets):
    path = receipt_path(root, project, sha)
    if not path.exists():
        return False
    record = read_json(path)
    revisions = [int(a['name'].rsplit('-v', 1)[1].split('.', 1)[0]) for a in assets
                 if a['name'].startswith('local-transfer-' + project + '-' + sha + '-runtime-v')]
    if max(revisions, default=1) > record['runtime_revision']:
        return False
    # Failed attempts retry from GitHub; stopped attempts wait for explicit resume.
    if record['status'] not in ('built', 'published', 'stopped'):
        return False
    resume = next((a for a in assets if a['name'] == 'local-transfer-' + project + '-' + sha + '-linux-resume.json'), None)
    if resume and resume['id'] != record.get('resume_id'):
        return False
    return record.get('delivery_verified') is True


@contextlib.contextmanager
def environment(ctx):
    """Redirect new build caches; never clear or mutate preinstalled toolchains."""
    scratch = inside(ctx.root, 'w/' + ctx.job['sha'][:12] + '/linux-scratch')
    scratch.mkdir(parents=True, exist_ok=True)
    values = {name: str(scratch / folder) for name, folder in {
        'TMPDIR': 'tmp', 'TMP': 'tmp', 'TEMP': 'tmp', 'XDG_CACHE_HOME': 'cache',
        'XDG_DATA_HOME': 'data', 'PUB_CACHE': 'pub', 'GRADLE_USER_HOME': 'gradle',
        'CARGO_HOME': 'cargo', 'GOCACHE': 'go', 'NPM_CONFIG_CACHE': 'npm',
        'XDG_STATE_HOME': 'state'}.items()}
    for value in values.values():
        Path(value).mkdir(exist_ok=True)
    previous = {key: os.environ.get(key) for key in values}
    previous_tempdir = tempfile.tempdir
    os.environ.update(values)
    tempfile.tempdir = values['TMPDIR']
    ctx.config['ephemeral_linux'] = True
    ctx.config['linux_scratch'] = str(scratch)
    ctx.env.update(values)
    reserve = scratch / 'emergency-reserve'
    # Free this exact reserve on ENOSPC so status and recovery journals can persist.
    try:
        with reserve.open('wb') as stream:
            for _ in range(32):
                stream.write(b'\0' * 1024**2)
        yield
    finally:
        reserve.unlink(missing_ok=True)
        tempfile.tempdir = previous_tempdir
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def telemetry(ctx, phase, error=None):
    value = read_json(ctx.result_path) if ctx.result_path.exists() else ctx.result
    tail = []
    budget = 192 * 1024
    for path in sorted((ctx.directory / 'logs/linux').glob('*.log'), key=lambda p: p.stat().st_mtime, reverse=True):
        if budget <= 0:
            break
        with path.open('rb') as stream:
            stream.seek(max(0, path.stat().st_size - min(budget, 32768)))
            content = stream.read(min(budget, 32768)).decode('utf-8', errors='replace')
        tail.append({'name': path.name, 'tail': ctx.redact(content)})
        budget -= len(content.encode('utf-8'))
    from .timing import summarize
    return {'sha': ctx.job['sha'], 'run_id': ctx.job['run_id'], 'version': ctx.job['version'],
        'build': ctx.job['build'], 'status': value.get('status'), 'phase': phase,
        'result': value, 'timing': summarize(value, running=phase == 'building'),
        'log_tails': tail, 'error': ctx.redact(str(error)) if error else None}


def purge(ctx):
    """Use deletion's exact path/recovery checks without deleting a GitHub release."""
    from .retention import cleanup_local
    profile = ctx.directory / 'ephemeral-profile.json'
    config = ctx.directory / 'ephemeral-config.json'
    atomic_json(profile, ctx.job['profile'])
    # Config contains local paths only, never its resolved credentials.
    atomic_json(config, ctx.config)
    project = {'project': ctx.job['project'], 'catalogue': str(ctx.root),
               'profile': str(profile), 'config': str(config)}
    request = {'schema': 1, 'project': ctx.job['project'], 'repository': ctx.job['repository'],
        'sha': ctx.job['sha'], 'version': ctx.job['version'], 'build': ctx.job['build'],
        'run_id': ctx.job['run_id'], 'hosts': list(ctx.job['required_steps']),
        'request_id': '0' * 32, 'release_tag': ctx.job['tag']}
    if not cleanup_local(project, request, 'linux', ignore_lifecycle=True):
        raise ReleaseError('Linux builder is still active; cleanup postponed')


def run(directory, config, runner):
    directory = Path(directory).resolve()
    with lock(receipt_path(directory.parents[3], directory.parents[1].name, directory.name).with_suffix('.lock')):
        try:
            return _run(directory, config, runner)
        except BaseException as error:
            if directory.exists() and not (directory / 'results/linux-outbox.json').exists():
                try:
                    failed = Context(directory, config, host='linux')
                    if failed.result.get('status') not in ('built', 'stopped', 'failed'):
                        failed.result.update(status='failed', error=failed.redact(str(error)))
                    else:
                        failed.result['lifecycle_error'] = failed.redact(str(error))
                    failed.save()
                    atomic_json(directory / 'results/linux-outbox.json', {
                        'pending': True, 'bounded': True, 'error': 'Linux lifecycle interrupted; retry delivery/recovery first'})
                except (OSError, ValueError, ReleaseError):
                    pass
            raise


def _run(directory, config, runner):
    """Always report, then purge only after full verified delivery and recovery."""
    from . import host_reports, transport
    config = {**config, 'auto_provision_flutter': True}
    ctx = Context(directory, config, host='linux')
    durable = receipt_path(ctx.root, ctx.job['project'], ctx.job['sha'])
    if durable.exists() and not (directory / 'results/linux-outbox.json').exists():
        previous = read_json(durable)
        resume = directory / 'results/linux-resume.json'
        resume_id = read_json(resume).get('id') if resume.exists() else None
        if (previous.get('delivery_verified') and previous.get('status') in ('built', 'stopped')
                and previous.get('runtime_revision') == ctx.job.get('preparation_revision', 1)
                and previous.get('resume_id') == resume_id):
            from .linux_provider import cleanup
            adapter = importlib.import_module(ctx.job['profile']['adapter'])
            if hasattr(adapter, 'recover_for_deletion'):
                adapter.recover_for_deletion(ctx)
            cleanup(ctx)
            purge(ctx)
            return ctx
    from .github import reconcile_published
    if (directory / 'publication.json').exists() and read_json(directory / 'publication.json').get('published'):
        cleanup_published(ctx)
        return ctx
    if (directory / 'results/linux-outbox.json').exists() and reconcile_published(ctx):
        cleanup_published(ctx)
        return ctx
    project = {'project': ctx.job['project'], 'catalogue': str(ctx.root),
               '_profile': ctx.job['profile'], '_config': config}
    stop = threading.Event()
    report_guard = threading.Lock()
    def report(phase, error=None):
        with report_guard:
            return host_reports.publish(project, telemetry(ctx, phase, error))
    def progress():
        while not stop.wait(60):
            try:
                report('building')
            except Exception:
                pass  # Final delivery is mandatory and decides cleanup.
    failure = None
    with environment(ctx):
        thread = threading.Thread(target=progress, daemon=True)
        thread.start()
        try:
            # Restore only this host's checkpoints/packages; Windows is the archive.
            if not ctx.result_path.exists():
                transport.sync_results(ctx, hosts=['linux'])
            ctx = Context(directory, ctx.config, host='linux')
            runner(directory, ctx.config, False)
        except BaseException as error:
            failure = error
        finally:
            stop.set()
            thread.join(timeout=1)
            reserve = Path(ctx.config['linux_scratch']) / 'emergency-reserve'
            reserve.unlink(missing_ok=True)
        ctx = Context(directory, ctx.config, host='linux')
        ctx.refresh_redaction(host_reports.redactor(ctx.config).values)
        if failure:
            from .processes import JobStopped
            ctx.result.update(status='stopped' if isinstance(failure, JobStopped) else 'failed',
                              error=ctx.redact(str(failure)))
            ctx.save()
        adapter = importlib.import_module(ctx.job['profile']['adapter'])
        cleanup_started = time.monotonic()
        try:
            # Even an owner-recovery failure must return the completed build log.
            transport.send_result(ctx)
            if hasattr(adapter, 'recover_for_deletion'):
                adapter.recover_for_deletion(ctx)
            from .linux_provider import cleanup
            cleanup(ctx)
            ctx.result['cleanup'] = {'provider_verified': True, 'delivery_verified': True}
            ctx.result['cleanup']['duration_seconds'] = time.monotonic() - cleanup_started
            ctx.result.update(current_step=None)
            ctx.save()
            sent = transport.send_result(ctx)
            report('delivered-cleaning', failure)
        except BaseException as transfer_error:
            atomic_json(ctx.directory / 'results/linux-outbox.json', {
                'pending': True, 'error': ctx.redact(str(transfer_error)), 'bounded': True})
            try:
                report('delivery-or-recovery', transfer_error)
            except Exception:
                host_reports.report_failure(project, transfer_error, phase='delivery-or-recovery')
            raise ReleaseError('Linux attempt preserved; no new builds until delivery/recovery succeeds: ' +
                               ctx.redact(str(transfer_error))) from transfer_error
        result = ctx.result
        record = {'schema': 1, 'sha': ctx.job['sha'], 'status': result['status'],
            'runtime_revision': ctx.job.get('preparation_revision', 1), 'delivery_verified': True,
            'sent': sent, 'updated': time.time(),
            'resume_id': read_json(directory / 'results/linux-resume.json').get('id') if (directory / 'results/linux-resume.json').exists() else None}
        receipt = receipt_path(ctx.root, ctx.job['project'], ctx.job['sha'])
        atomic_json(receipt, record)
    # All child commands and file handles have ended before recursive cleanup.
    purge(ctx)
    # Host report cannot reference deleted files. Keep final telemetry in memory.
    try:
        from .timing import summarize
        host_reports.publish(project, {'sha': record['sha'], 'status': record['status'],
            'phase': 'cleaned', 'cleanup': 'verified delivery; managed build data removed',
            'cleanup_seconds': time.monotonic() - cleanup_started,
            'timing': summarize(result), 'result': result})
    except Exception as error:
        host_reports.report_failure(project, error, phase='cleanup-report')
    if failure:
        raise failure
    return ctx


def cleanup_published(ctx):
    """A verified public manifest replaces retired exchange files; never rebuild."""
    from .linux_provider import cleanup
    adapter = importlib.import_module(ctx.job['profile']['adapter'])
    if hasattr(adapter, 'recover_for_deletion'):
        adapter.recover_for_deletion(ctx)
    cleanup(ctx)
    atomic_json(receipt_path(ctx.root, ctx.job['project'], ctx.job['sha']), {
        'schema': 1, 'sha': ctx.job['sha'], 'status': 'published', 'delivery_verified': True,
        'runtime_revision': ctx.job.get('preparation_revision', 1), 'updated': time.time()})
    purge(ctx)


