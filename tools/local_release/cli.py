"""Standalone CLI. Also runs from a prepared job after a dual-boot switch."""

from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

# Resolve the same package both in tools/ and in a job's runtime/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from local_release.core import (ReleaseError, atomic_json, discover, host_name,
                                prepare, queue_install, read_json, run_job, worker, hidden_flags)


def parser():
    result = argparse.ArgumentParser(description="Shared local release coordinator")
    sub = result.add_subparsers(dest="command", required=True)
    from local_release.agent import registry_path
    for name in ("serve", "install-service", "start-service", "stop-service"):
        service = sub.add_parser(name, help="Shared loopback build dashboard")
        service.add_argument("--registry", type=Path, default=registry_path())
        service.add_argument("--port", type=int, default=8877)
        service.add_argument("--no-sync", action="store_true")
    register_parser = sub.add_parser("register-project", help="Connect one explicit project to the shared service")
    register_parser.add_argument("--registry", type=Path, default=registry_path())
    for field in ("repo", "profile", "root", "config"):
        register_parser.add_argument("--" + field, type=Path, required=True)
    dispatcher = sub.add_parser("agent", help="One sequential registry dispatch cycle")
    dispatcher.add_argument("--registry", type=Path, default=registry_path())
    dispatcher.add_argument("--role", choices=("windows", "linux"), default=host_name())
    prepare_parser = sub.add_parser("prepare", help="Freeze one source SHA and portable job")
    prepare_parser.add_argument("--repo", type=Path, required=True)
    prepare_parser.add_argument("--profile", type=Path, required=True)
    prepare_parser.add_argument("--root", type=Path, required=True)
    prepare_parser.add_argument("--sha", default="HEAD")
    prepare_parser.add_argument("--config", type=Path)
    repair = sub.add_parser("refresh-runtime", help="Audited protocol repair preserving source SHA/build and package files")
    repair.add_argument("--job", type=Path, required=True)
    repair.add_argument("--config", type=Path, required=True)
    repair.add_argument("--coordinator-sha", required=True)
    repair.add_argument("--reason", default="Audited coordinator repair; source/version/build unchanged")
    repair.add_argument("--invalidate-step", action="append", help="Audited checkpoint to repeat, e.g. linux:verify-linux; otherwise use full recipe invalidation")
    repair.add_argument("--send", action="store_true")
    for command in ("install-version-hook", "remove-version-hook", "version-commit", "version-finalize"):
        counter = sub.add_parser(command)
        counter.add_argument("--repo", type=Path, required=True)
        if command != "remove-version-hook":
            counter.add_argument("--profile", type=Path, required=True)
        if command == "version-commit":
            counter.add_argument("--message", type=Path, required=True)
    run = sub.add_parser("run", help="Resume this OS's stages of a prepared job")
    run.add_argument("--job", type=Path, required=True)
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--publish", action="store_true")
    run.add_argument("--phase", action="append", choices=["quality", "integration", "build"])
    status = sub.add_parser("status")
    status.add_argument("--job", type=Path, required=True)
    install = sub.add_parser("init-queue", help="Save a historical boundary without activation")
    for key in ("repo", "root", "profile", "config"):
        install.add_argument("--" + key, type=Path, required=True)
    install.add_argument("--test-mode", action="store_true")
    for command in ("scan", "worker", "notify"):
        action = sub.add_parser(command)
        action.add_argument("--queue", type=Path, required=True)
        if command == "notify":
            action.add_argument("--sha", default="HEAD")
        if command == "worker":
            action.add_argument("--once", action="store_true")
    hooks = sub.add_parser("install-trigger", help="Activate only after full verified trial publication")
    hooks.add_argument("--queue", type=Path, required=True)
    hooks.add_argument("--proof", type=Path)
    hooks.add_argument("--test-mode", action="store_true")
    remove = sub.add_parser("remove-trigger")
    remove.add_argument("--queue", type=Path, required=True)
    drain = sub.add_parser("drain", help="Resume all prepared jobs on this OS, without the Windows checkout")
    drain.add_argument("--root", type=Path, required=True)
    drain.add_argument("--config", type=Path, required=True)
    drain.add_argument("--publish", action="store_true")
    archive = sub.add_parser("archive", help="Download all historical GitHub Release assets")
    archive.add_argument("--profile", type=Path, required=True)
    archive.add_argument("--root", type=Path, required=True)
    archive.add_argument("--config", type=Path, required=True)
    verify = sub.add_parser("verify-packages", help="Verify the primary local deployment catalogue")
    verify.add_argument("directory", type=Path)
    retry = sub.add_parser("retry", help="Explicitly resume one failed/waiting SHA")
    retry.add_argument("--queue", type=Path, required=True)
    retry.add_argument("--sha", required=True)
    for name in ("handoff", "send-result", "sync"):
        command = sub.add_parser(name)
        command.add_argument("--job", type=Path, required=True)
        command.add_argument("--config", type=Path, required=True)
        if name == "sync":
            command.add_argument("--cleanup", action="store_true")
    receive = sub.add_parser("receive", help="Receive prepared jobs from this project's own draft releases")
    receive.add_argument("--profile", type=Path, required=True)
    receive.add_argument("--root", type=Path, required=True)
    receive.add_argument("--config", type=Path, required=True)
    receive.add_argument("--tag")
    return result


def spawn_worker(queue):
    log = queue.parent / f"{queue.stem}-observer.log"
    argv = [sys.executable, str(Path(__file__).resolve()), "worker", "--queue", str(queue.resolve())]
    options = {"start_new_session": True} if os.name != "nt" else {
        "creationflags": subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
    with log.open("a", encoding="utf-8") as stream:
        subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stream, stderr=stream, **options)


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command in ("serve", "install-service", "start-service", "stop-service"):
        from local_release import service
        if args.command == "serve":
            service.serve(args.registry, args.port, not args.no_sync)
        elif args.command == "stop-service":
            service.stop(args.registry, args.port)
        else:
            if args.command == "install-service":
                service.install_startup(args.registry, args.port)
            print(service.start(args.registry, args.port, not args.no_sync))
    elif args.command == "register-project":
        from local_release.agent import register
        register(args.registry, args.repo, args.profile, args.root, args.config)
    elif args.command == "agent":
        from local_release.agent import cycle
        cycle(args.registry, args.role)
    elif args.command == "prepare":
        print(prepare(args.repo, args.profile, args.root, args.sha, read_json(args.config) if args.config else None))
    elif args.command == "refresh-runtime":
        from local_release.runtime_update import prepare_update, send_update
        from local_release.core import Context, git
        repository = Path(__file__).resolve().parents[2]
        if git(repository, "rev-parse", "HEAD") != args.coordinator_sha or git(repository, "status", "--porcelain", "--", "tools/local_release"):
            raise ReleaseError("Commit the coordinator repair before publishing a runtime update")
        config = read_json(args.config)
        invalidations = None
        if args.invalidate_step:
            invalidations = {}
            for value in args.invalidate_step:
                role, separator, step = value.partition(":")
                if not separator or not step:
                    raise ReleaseError("--invalidate-step must be host:step")
                invalidations.setdefault(role, []).append(step)
        prepare_update(args.job.resolve(), config, args.coordinator_sha, reason=args.reason, invalidate_steps=invalidations)
        if args.send:
            send_update(Context(args.job.resolve(), config))
    elif args.command in ("install-version-hook", "remove-version-hook", "version-commit", "version-finalize"):
        from local_release import versioning
        if args.command == "install-version-hook":
            versioning.install(args.repo.resolve(), args.profile.resolve())
        elif args.command == "remove-version-hook":
            versioning.remove(args.repo.resolve())
        elif args.command == "version-finalize":
            versioning.finalize(args.repo.resolve(), args.profile.resolve())
        else:
            versioning.commit(args.repo.resolve(), args.profile.resolve(), args.message.resolve())
    elif args.command == "run":
        frozen_cli = args.job.resolve() / "runtime/local_release/cli.py"
        if Path(__file__).resolve() != frozen_cli:
            # All hosts execute exactly the frozen coordinator shipped in the job.
            command = [sys.executable, str(frozen_cli), "run", "--job", str(args.job.resolve()), "--config", str(args.config.resolve())]
            if args.publish:
                command.append("--publish")
            for phase in args.phase or []:
                command.extend(["--phase", phase])
            result = subprocess.run(command, check=False, creationflags=hidden_flags())
            if result.returncode:
                raise ReleaseError("Prepared builder exited " + str(result.returncode))
            return
        config = read_json(args.config)
        if args.phase:
            config["phases"] = args.phase
        run_job(args.job.resolve(), config, args.publish)
    elif args.command == "status":
        job = read_json(args.job / "job.json")
        results = {p.stem: read_json(p) for p in (args.job / "results").glob("*.json")}
        publication = args.job / "publication.json"
        print(json.dumps({"run_id": job["run_id"], "sha": job["sha"], "version": job["version"],
                          "build": job["build"], "results": results,
                          "publication": read_json(publication) if publication.exists() else None}, indent=2))
    elif args.command == "init-queue":
        print(queue_install(args.repo, args.root, args.profile, args.config, test_mode=args.test_mode))
    elif args.command == "archive":
        from local_release.archive import archive_releases
        archive_releases(read_json(args.profile), args.root.resolve(), read_json(args.config))
    elif args.command == "verify-packages":
        from local_release.catalogue import verify_catalogue
        print(json.dumps(verify_catalogue(args.directory), indent=2))
    elif args.command == "retry":
        from local_release.core import update_queue
        data = read_json(args.queue)
        row = data["commits"].get(args.sha)
        if not row or row["status"] in ("skipped", "published"):
            raise ReleaseError("Only a known failed/waiting commit can be retried")
        update_queue(args.queue.parent, args.queue, args.sha, status="queued", error=None)
    elif args.command in ("handoff", "send-result", "sync"):
        from local_release.core import Context
        from local_release import transport
        context = Context(args.job.resolve(), read_json(args.config))
        if args.command == "sync":
            transport.sync_results(context, cleanup=args.cleanup)
        elif args.command == "handoff":
            transport.handoff(context)
        else:
            transport.send_result(context)
    elif args.command == "receive":
        from local_release.transport import receive_jobs
        for path in receive_jobs(read_json(args.profile), args.root.resolve(), read_json(args.config), args.tag):
            print(path)
    elif args.command in ("scan", "notify"):
        data = read_json(args.queue)
        if args.command == "notify":
            from local_release.core import record_commit_event
            record_commit_event(Path(data["repo"]), args.queue, args.sha)
        try:
            data = discover(Path(data["repo"]), args.queue.parent, args.queue)
        except ReleaseError as error:
            if args.command != "notify" or not str(error).startswith("Busy operation:"):
                raise
            # Another observer will drain the durable spool after its lock releases.
        if args.command == "notify" and (data["enabled"] or data["test_mode"]):
            spawn_worker(args.queue)
        if sys.stdout:
            print(json.dumps({sha: row["status"] for sha, row in data["commits"].items()}))
    elif args.command == "worker":
        worker(args.queue, once=args.once)
    elif args.command == "install-trigger":
        from local_release.hooks import install
        install(args.queue, args.proof, args.test_mode)
        if not args.test_mode:
            spawn_worker(args.queue)
    elif args.command == "remove-trigger":
        from local_release.hooks import remove
        remove(args.queue)
    elif args.command == "drain":
        failures = []
        for job in sorted((args.root / "releases").glob("*/*/*/job.json")):
            specification = read_json(job)
            if host_name() not in specification["required_steps"]:
                continue
            publication = job.parent / "publication.json"
            if publication.exists() and read_json(publication).get("published"):
                continue
            try:
                from local_release.core import execute_prepared
                execute_prepared(job.parent, args.config.resolve(), args.publish)
            except Exception as error:
                failures.append(str(error))
        if failures:
            raise ReleaseError("; ".join(failures))


if __name__ == "__main__":
    try:
        main()
    except (ReleaseError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
