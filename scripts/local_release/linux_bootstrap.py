"""Register this host once, then drain every registered Linux project at login."""

import argparse
import os
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
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
    sync_project_catalogue(args.registry, REPO / "scripts/local_release/projects.json", allow_clone=True)
    install_linux_startup(REPO, args.registry)
    print("Login dispatcher installed. Future Linux runs start automatically after graphical login.", flush=True)
    report = cycle(args.registry, "linux")
    return 0 if report["status"] == "finished" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        atomic_json(REPO / ".local-releases/linux-bootstrap-result.json", {
            "status": "failed-before-job", "reason": str(error),
            "action": "Restore local configuration/authentication and retry; no shell text from logs was executed"})
        print(str(error), file=sys.stderr)
        sys.exit(1)
