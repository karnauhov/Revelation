"""Register this host once, then drain every registered Linux project at login."""

import os
import sys

import argparse
from pathlib import Path
import runpy

REPO = Path(__file__).resolve().parents[2]
ENGINE = Path(os.environ.get('AI11_LOCAL_RELEASE_ENGINE', str(REPO.parent / 'ai11/tools/local_release')))
if not (ENGINE / 'cli.py').is_file():
    # The old already-loaded login bootstrap may pull the migration and then
    # launch this file. Acquire ai11 here as well, before importing the engine.
    compatibility = runpy.run_path(str(REPO / 'scripts/local_release/agent_bootstrap.py'))
    compatibility['ensure_engine']()
with (ENGINE / 'python_bootstrap.py').open('rb') as source:
    exec(compile(source.read(), str(ENGINE / 'python_bootstrap.py'), 'exec'), {'__name__': '_ai11_python_startup'})
sys.path.insert(0, str(ENGINE.parent))
from local_release.agent import cycle, install_linux_startup, register, registry_path, sync_project_catalogue
from local_release.core import ReleaseError, atomic_json, read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO / ".local-releases")
    parser.add_argument("--config", type=Path, default=Path.home() / ".config/ai11-local-release/revelation.json")
    parser.add_argument("--registry", type=Path, default=registry_path())
    args = parser.parse_args()
    if sys.platform != "linux":
        raise ReleaseError("Run this entrypoint under native Linux")
    config = read_json(args.config) if args.config.exists() else {}
    for key, value in {"defines_file": str(REPO / "api-keys.json"), "sentry_properties": str(REPO / "sentry.properties"),
                       "github_git_credential": True, "auto_provision_flutter": True, "stream_output": True}.items():
        config.setdefault(key, value)
    atomic_json(args.config, config)
    os.chmod(args.config, 0o600)
    register(args.registry, REPO, REPO / "scripts/local_release/revelation.json", args.root, args.config)
    sync_project_catalogue(args.registry, ENGINE / "projects.json", allow_clone=True)
    from local_release.relocation import plan, apply
    changes = plan(args.registry, REPO / 'tools/local_release')
    if changes:
        apply(args.registry, changes)
    from local_release.versioning import install as install_version_hook
    install_version_hook(REPO, REPO / "scripts/local_release/revelation.json")
    install_linux_startup(REPO, args.registry)
    from local_release.service import start
    print("Local dashboard: " + start(args.registry, sync=False), flush=True)
    print("Login dispatcher installed. Future Linux runs start automatically after graphical login.", flush=True)
    report = cycle(args.registry, "linux")
    return 0 if report["status"] == "finished" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        from local_release.host_reports import report_failure
        report_failure({'project': 'revelation', 'profile': str(REPO / 'scripts/local_release/revelation.json'),
                        'config': str(Path.home() / '.config/ai11-local-release/revelation.json'),
                        'catalogue': str(REPO / '.local-releases')}, error)
        print(str(error), file=sys.stderr)
        sys.exit(1)
