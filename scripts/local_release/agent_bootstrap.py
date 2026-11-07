"""Compatibility login entrypoint for the shared AI11 coordinator."""
import os
from pathlib import Path
import runpy
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
ENGINE = Path(os.environ.get('AI11_LOCAL_RELEASE_ENGINE', str(REPO.parent / 'ai11/tools/local_release')))


def ensure_engine():
    if (ENGINE / 'agent_bootstrap.py').is_file():
        return
    # Acquire only the explicitly selected shared repository on first Linux
    # login. Never clone over an override or a dirty owner checkout.
    if sys.platform != 'linux' or 'AI11_LOCAL_RELEASE_ENGINE' in os.environ:
        raise SystemExit('Shared local release engine is missing: ' + str(ENGINE))
    target = ENGINE.parents[1]
    if not target.exists():
        result = subprocess.run(['git', 'clone', 'https://github.com/karnauhov/ai11.git', str(target)],
                                capture_output=True, check=False)
        if result.returncode:
            raise SystemExit('Cannot acquire the shared ai11 checkout; existing files preserved')
    else:
        def git(*args):
            result = subprocess.run(['git', '-C', str(target), *args], capture_output=True,
                                    text=True, check=False)
            if result.returncode:
                raise SystemExit('Cannot update the shared ai11 checkout; existing files preserved')
            return result.stdout.strip()
        if git('branch', '--show-current') != 'main' or git('status', '--porcelain', '--untracked-files=no'):
            raise SystemExit('Shared ai11 checkout must be clean on main; existing files preserved')
        git('fetch', 'origin')
        git('merge', '--ff-only', 'origin/main')
    if not (ENGINE / 'agent_bootstrap.py').is_file():
        raise SystemExit('Publish REV306 in ai11 before using the migrated Linux startup')


if __name__ == "__main__":
    ensure_engine()
    runpy.run_path(str(ENGINE / 'agent_bootstrap.py'), run_name='__main__')
