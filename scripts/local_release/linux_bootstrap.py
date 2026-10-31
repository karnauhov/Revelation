"""One Linux entrypoint; Windows disks, sessions and processes are unnecessary."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

from local_release.core import ReleaseError, atomic_json, read_json
from local_release.transport import receive_jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO / ".local-releases")
    parser.add_argument("--config", type=Path, default=Path.home() / ".config/ai11-local-release/revelation.json")
    parser.add_argument("--tag")
    args = parser.parse_args()
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    if sys.platform != "linux":
        raise ReleaseError("Run this entrypoint under native Linux")
    if not args.config.exists():
        # Paths only. Reuse this Linux checkout's private files, never Windows secrets.
        atomic_json(args.config, {"defines_file": str(REPO / "api-keys.json"),
                                  "sentry_properties": str(REPO / "sentry.properties"),
                                  "github_git_credential": True})
        os.chmod(args.config, 0o600)
    config = read_json(args.config)
    profile = read_json(REPO / "scripts/local_release/revelation.json")
    received = receive_jobs(profile, root, config, args.tag)
    jobs = {path for path in received}
    for path in (root / "releases/revelation").glob("*/*/job.json"):
        publication = path.parent / "publication.json"
        if not publication.exists() or not read_json(publication).get("published"):
            jobs.add(path.parent)
    if not jobs:
        raise ReleaseError("No pending prepared Revelation job was found in GitHub Releases or the local catalogue")
    failures = []
    for job in sorted(jobs):
        command = [sys.executable, str(job / "runtime/local_release/cli.py"), "run", "--job", str(job),
                   "--config", str(args.config.resolve()), "--publish"]
        # The prepared runtime uploads status/logs even after a build/test failure.
        code = subprocess.run(command, check=False).returncode
        if code:
            failures.append({"job": str(job), "exit_code": code})
    atomic_json(root / "linux-bootstrap-result.json", {"finished": time.time(), "jobs": [str(j) for j in sorted(jobs)],
                                                       "failures": failures, "status": "failed" if failures else "completed"})
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        # Authentication/network failure cannot be reported remotely before access
        # is restored. This durable local outbox is retried by the same command.
        root = REPO / ".local-releases"
        atomic_json(root / "linux-bootstrap-result.json", {"status": "failed-before-job", "reason": str(error),
                                                           "action": "Restore Linux authentication/network/config and rerun run-linux.sh"})
        print(str(error), file=sys.stderr)
        sys.exit(1)
