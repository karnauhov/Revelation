"""Audited coordinator repair without changing a release's source SHA/build."""

import json
import gzip
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import time
import uuid

from .core import ReleaseError, atomic_json, digest, inside, lock, read_json, verify_runtime
from .protocol import VERSION, validate_upgrade


def unpack(path, destination, maximum=512 * 1024**2):
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        if len(members) > 150 or sum(m.size for m in members) > maximum:
            raise ReleaseError("Exchange archive exceeds its bounded contract")
        for member in members:
            if not member.isfile():
                raise ReleaseError("Exchange archive must contain regular files only")
            target = inside(destination, member.name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def install(directory, extracted):
    old, new = read_json(directory / "job.json"), read_json(extracted / "job.json")
    validate_upgrade(old, new)
    verify_runtime(extracted)
    envelope = read_json(extracted / "runtime-update.json")
    if envelope["previous_job_sha256"] != digest(directory / "job.json"):
        raise ReleaseError("Runtime update predecessor differs from this checkpoint")
    if envelope["job_sha256"] != digest(extracted / "job.json"):
        raise ReleaseError("Runtime update metadata digest mismatch")
    metadata_paths = ("job.json", "runtime-update.json", "results/linux.json")
    previous = {name: (directory / name).read_bytes() if (directory / name).exists() else None
                for name in metadata_paths}
    # Refuse a live builder on either OS. Updates never interrupt running jobs.
    with lock(directory / ".windows.lock"), lock(directory / ".linux.lock"), lock(directory / ".exchange.lock"):
        destination = directory / "runtime"
        backup = directory / (".runtime-" + uuid.uuid4().hex)
        staged = directory / (".runtime-next-" + uuid.uuid4().hex)
        shutil.copytree(extracted / "runtime", staged)
        try:
            os.replace(destination, backup)
            os.replace(staged, destination)
            atomic_json(directory / "job.json", new)
            atomic_json(directory / "runtime-update.json", envelope)
            linux_recipe_changed = (old["runtime_sha256"].get("local_release/profiles/linux_release.py") !=
                                    new["runtime_sha256"].get("local_release/profiles/linux_release.py") or
                                    old.get("generated_source_overlays") != new.get("generated_source_overlays"))
            linux_result = directory / "results/linux.json"
            if linux_recipe_changed and linux_result.exists():
                result = read_json(linux_result)
                for name in list(result["steps"]):
                    if name in ("linux", "sentry-linux", "linux-tar", "snap", "inspect-snap", "inspect-linux-tar", "verify-linux", "integration-linux") or name.startswith("integration-linux-"):
                        result["steps"].pop(name)
                result.update(status="pending", current_step=None, runtime_revision=new["preparation_revision"])
                atomic_json(linux_result, result)
        except BaseException:
            if backup.exists():
                if destination.exists():
                    shutil.rmtree(destination)
                os.replace(backup, destination)
                for name, content in previous.items():
                    path = directory / name
                    if content is None:
                        path.unlink(missing_ok=True)
                    else:
                        replacement = path.with_name(path.name + ".rollback")
                        replacement.write_bytes(content)
                        os.replace(replacement, path)
            raise
        finally:
            for temporary in (backup, staged):
                if temporary.exists() and temporary.parent.resolve() == directory.resolve():
                    shutil.rmtree(temporary)


def prepare_update(directory, config, coordinator_sha):
    import importlib
    old = read_json(directory / "job.json")
    publication = directory / "publication.json"
    if publication.exists() and read_json(publication).get("published"):
        raise ReleaseError("Published releases are immutable; use the version helper for a new build")
    adapter = importlib.import_module(old["profile"]["adapter"])
    context = __import__("local_release.core", fromlist=["Context"]).Context(directory, config)
    # Metadata is still derived from the original source commit, not current main.
    metadata = adapter.metadata(context.workspace, old["sha"], old["profile"])
    with tempfile.TemporaryDirectory(prefix="release-runtime-update-") as folder:
        staged = Path(folder)
        runtime = staged / "runtime/local_release"
        runtime.mkdir(parents=True)
        source = Path(__file__).parent
        for path in source.glob("*.py"):
            shutil.copy2(path, runtime / path.name)
        shutil.copytree(source / "profiles", runtime / "profiles", ignore=shutil.ignore_patterns("__pycache__"))
        new = {**old, **metadata, "protocol_version": VERSION,
               "preparation_revision": old.get("preparation_revision", 1) + 1,
               "coordinator_source_sha": coordinator_sha,
               "runtime_sha256": {p.relative_to(staged / "runtime").as_posix(): digest(p) for p in runtime.rglob("*.py")}}
        new.setdefault("tooling_changes", []).append({"revision": new["preparation_revision"], "time": time.time(),
            "reason": "Protocol repair: independent partial results, Linux catalogue recovery and noninteractive packaging; source/version/build unchanged"})
        atomic_json(staged / "job.json", new)
        atomic_json(staged / "runtime-update.json", {"schema": 1, "protocol_version": VERSION,
            "run_id": old["run_id"], "previous_job_sha256": digest(directory / "job.json"),
            "job_sha256": digest(staged / "job.json"), "revision": new["preparation_revision"],
            "coordinator_source_sha": coordinator_sha})
        install(directory, staged)
    return new


def send_update(ctx):
    from .transport import connection, prefix
    api, release = connection(ctx)
    verify_runtime(ctx.directory)
    with tempfile.TemporaryDirectory(prefix="release-runtime-send-") as folder:
        name = prefix(ctx.job) + f"runtime-v{ctx.job['preparation_revision']}.tar.gz"
        path = Path(folder) / name
        names = ["job.json", "runtime-update.json", *["runtime/" + key for key in ctx.job["runtime_sha256"]]]
        with path.open("wb") as output, gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed, tarfile.open(fileobj=compressed, mode="w") as archive:
            for relative in names:
                source = inside(ctx.directory, relative)
                info = tarfile.TarInfo(relative)
                info.size, info.mode, info.mtime = source.stat().st_size, 0o644, 0
                with source.open("rb") as stream:
                    archive.addfile(info, stream)
        record = api.upload_verified(release, path)
        atomic_json(ctx.directory / "results/runtime-update-sent.json", record)
        return record
