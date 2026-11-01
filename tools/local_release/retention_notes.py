"""Small cross-OS tombstones in a Git notes ref, without a branch or Release."""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from .core import ReleaseError, hidden_flags, lock, read_json

REF = 'refs/notes/ai11-local-retention'


def merge(left, right):
    if left and left['request'] != right['request']:
        raise ReleaseError('Conflicting deletion tombstone; preserve both records for inspection')
    return {'request': right['request'], 'acks': {**(left or {}).get('acks', {}), **right.get('acks', {})}}


class Notes:
    def __init__(self, project, *, remote='origin', check_origin=True):
        self.project = project
        self.repo = Path(project['repo'])
        self.remote = remote
        self.profile = read_json(Path(project['profile']))
        if check_origin:
            repository = re.escape(self.profile['repository'])
            origin = self.git('remote', 'get-url', remote)
            if not re.fullmatch(r'(?:https://github\.com/|git@github\.com:)' + repository + r'(?:\.git)?', origin):
                raise ReleaseError('Retention notes origin differs from the registered GitHub repository')
        self.head, self.records = None, None

    def git(self, *args, stdin=None, required=True):
        env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never',
                   GIT_AUTHOR_NAME='AI11 local releases', GIT_AUTHOR_EMAIL='local-builds@ai11.link',
                   GIT_COMMITTER_NAME='AI11 local releases', GIT_COMMITTER_EMAIL='local-builds@ai11.link')
        # mktree/objects require exact LF bytes, including from Windows pythonw.
        result = subprocess.run(['git', '-C', str(self.repo), *args], input=stdin.encode('utf-8') if stdin is not None else None,
            capture_output=True, env=env, creationflags=hidden_flags())
        result.stdout = result.stdout.decode('utf-8', errors='replace')
        result.stderr = result.stderr.decode('utf-8', errors='replace')
        if required and result.returncode:
            raise ReleaseError('Git retention ' + args[0] + ' failed; remote delivery is not confirmed: ' + result.stderr[-1500:])
        return result.stdout.strip() if required else result

    def read(self):
        self.records = {}
        remote = self.git('ls-remote', self.remote, REF)
        self.head = remote.split()[0] if remote else None
        if not self.head:
            return self.records
        local = self.git('rev-parse', '--verify', REF, required=False)
        if local.returncode or local.stdout.strip() != self.head:
            # Only this tool-owned ref is updated; owner branches/index are untouched.
            self.git('fetch', '--no-tags', self.remote, '+' + REF + ':' + REF)
        lines = self.git('ls-tree', '-r', self.head).splitlines()
        if len(lines) > 4096:
            raise ReleaseError('Retention notes exceed the small control-data envelope')
        from .retention import validate
        for line in lines:
            metadata, path = line.split('\t', 1)
            mode, kind, oid = metadata.split()
            sha = path.replace('/', '')
            if mode != '100644' or kind != 'blob' or not re.fullmatch('[a-f0-9]{40}', sha):
                raise ReleaseError('Unexpected object in the owned retention notes ref')
            if int(self.git('cat-file', '-s', oid)) > 65536:
                raise ReleaseError('Oversized retention note')
            value = json.loads(self.git('cat-file', 'blob', oid))
            validate(value['request'], self.project)
            if value['request']['sha'] != sha or any(host not in ('windows', 'macos') or passed is not True
                    for host, passed in value.get('acks', {}).items()):
                raise ReleaseError('Retention note identity/receipt mismatch')
            self.records[sha] = value
        return self.records

    def sync(self, record):
        value = {'request': record['request'], 'acks': {k: v for k, v in record.get('acks', {}).items() if k != 'linux'}}
        from .retention import validate
        validate(value['request'], self.project)
        if any(host not in ('windows', 'macos') or passed is not True for host, passed in value['acks'].items()):
            raise ReleaseError('Invalid persistent-host deletion receipt')
        sha = value['request']['sha']
        with lock(Path(self.project['catalogue']) / '.retention-notes.lock', timeout=5):
            for _ in range(3):
                records = self.read()
                combined = merge(records.get(sha), value)
                if records.get(sha) == combined:
                    return self.receipt(combined)
                records[sha] = combined
                rows = []
                for source, item in sorted(records.items()):
                    payload = json.dumps(item, ensure_ascii=False, sort_keys=True) + '\n'
                    oid = self.git('hash-object', '-w', '--stdin', stdin=payload)
                    rows.append(f'100644 blob {oid}\t{source}\n')
                tree = self.git('mktree', stdin=''.join(rows))
                code = self.profile.get('retention_task_code', '')
                if not re.fullmatch('[A-Z]+[0-9]+', code):
                    raise ReleaseError('Project profile needs its real retention_task_code before control commits')
                parent = ['-p', self.head] if self.head else []
                commit = self.git('commit-tree', tree, *parent,
                    stdin=f'[{code}] Preserve local-release deletion markers [skip ci]\n')
                pushed = self.git('push', self.remote, commit + ':' + REF, required=False)
                if pushed.returncode:
                    continue  # Refetch and reconcile concurrent appends; never force-push.
                self.git('update-ref', REF, commit)
                verified = self.read()
                if verified.get(sha) != combined:
                    # A concurrent writer may have added receipts; request must remain identical.
                    if merge(verified.get(sha), combined) != verified.get(sha):
                        raise ReleaseError('Retention notes read-back differs from the sent record')
                return self.receipt(verified[sha])
        raise ReleaseError('Retention notes push was not confirmed; packages preserved for retry')

    def receipt(self, value):
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
        return {'transport': 'git-notes', 'ref': REF, 'commit': self.head,
                'sha256': hashlib.sha256(payload).hexdigest()}


def store(project):
    return Notes(project)
