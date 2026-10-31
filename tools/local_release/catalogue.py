"""Local package catalogue is the primary deployment source; GitHub is a mirror."""

from pathlib import Path
import re
import shutil

from .core import ReleaseError, atomic_json, digest, inside, read_json


def release_directory(root, project, version, build, sha):
    if not re.fullmatch(r"[a-z0-9-]+", project) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ReleaseError("Invalid catalogue project/version")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ReleaseError("Catalogue requires a verified source commit SHA")
    return root / "releases" / project / f"{version}+{int(build)}" / sha


def retain_file(source, destination):
    expected = digest(source)
    if destination.exists():
        if digest(destination) != expected:
            raise ReleaseError("Local package collision; existing file preserved: " + str(destination))
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(destination.name + ".partial")
        try:
            shutil.copy2(source, partial)
            if digest(partial) != expected:
                raise ReleaseError("Local package copy digest mismatch")
            partial.replace(destination)
        finally:
            partial.unlink(missing_ok=True)
    return {"name": destination.name, "size": destination.stat().st_size, "sha256": expected}


def catalogue_job(context):
    from .github import complete_results
    job = context.job
    directory = context.directory
    manifest_path = directory / "manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {
        "schema": 1, "project": job["project"], "version": job["version"], "build": job["build"],
        "sha": job["sha"], "run_id": job["run_id"], "packages": {}, "source": "local-build"}
    for host in job["required_steps"]:
        result_path = context.directory / "results" / f"{host}.json"
        if not result_path.exists():
            continue
        result = read_json(result_path)
        if (result["sha"], result["run_id"]) != (job["sha"], job["run_id"]):
            raise ReleaseError("Mixed catalogue results")
        for step in result["steps"].values():
            if step.get("status") != "passed":
                continue
            for relative, expected in step.get("outputs", {}).items():
                source = inside(context.directory, relative)
                if source.parent != context.output or source.name not in job["artifacts"]:
                    continue
                if digest(source) != expected:
                    raise ReleaseError("Changed build output cannot enter the catalogue")
                manifest["packages"][source.name] = {
                    "name": source.name, "path": source.relative_to(directory).as_posix(),
                    "size": source.stat().st_size, "sha256": expected}
    manifest["status"] = "ready" if complete_results(context.directory, job) and set(manifest["packages"]) == set(job["artifacts"]) else "incomplete"
    atomic_json(manifest_path, manifest)
    return directory


def verify_catalogue(directory):
    manifest = read_json(directory / "manifest.json")
    for name, record in {**manifest["packages"], **manifest.get("metadata", {})}.items():
        path = inside(directory, record["path"])
        if not path.is_file() or path.stat().st_size != record["size"] or digest(path) != record["sha256"]:
            raise ReleaseError("Local release package verification failed: " + name)
    return manifest
