"""Confirmed build deletion, with durable cross-OS tombstones and receipts."""

from __future__ import annotations

import importlib
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import time
import uuid

from .core import Context, ReleaseError, atomic_json, digest, git, host_name, lock, read_json
from .catalogue import release_directory
from .github import GitHub, GitHubHTTPError, credential


def marker(project):
    return f"<!-- local-release-retention:{project}:1 -->"


def record_path(root, project, sha):
    if not re.fullmatch(r"[a-z0-9-]+", project) or not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ReleaseError("Invalid deletion identity")
    root = Path(root).resolve()
    path = root / "deletions" / project / (sha + ".json")
    if path.resolve() != path.absolute() or not path.resolve().is_relative_to(root):
        raise ReleaseError("Deletion registry escapes its catalogue")
    return path


def deleted(root, project, sha):
    return record_path(root, project, sha).exists()


def ensure_allowed(root, project, sha):
    if deleted(root, project, sha):
        raise ReleaseError("This build was deleted by the owner; its tombstone prevents rebuilding or restoring it")


def ensure_job_allowed(directory):
    directory = Path(directory).resolve()
    ensure_allowed(directory.parents[3], directory.parents[1].name, directory.name)


def api_for(project):
    profile = read_json(Path(project["profile"]))
    if profile["project"] != project["project"]:
        raise ReleaseError("Registered deletion profile differs")
    return GitHub(profile["repository"], credential(read_json(Path(project["config"]))))


def validate(request, project):
    profile = read_json(Path(project["profile"]))
    if (request.get("schema") != 1 or request.get("project") != project["project"]
            or request.get("repository") != profile["repository"]
            or not re.fullmatch(r"[a-f0-9]{32}", request.get("request_id", ""))
            or type(request.get("build")) is not int or request["build"] < 0
            or not isinstance(request.get("hosts"), list)
            or not request["hosts"] or set(request["hosts"]) - {"windows", "linux", "macos"}):
        raise ReleaseError("Invalid deletion request")
    expected = release_directory(Path(project["catalogue"]).resolve(), request["project"],
                                 request["version"], request["build"], request["sha"])
    if request.get("release_tag") != f"v{request['version']}+{request['build']}":
        raise ReleaseError("Deletion tag differs from its build")
    if request.get("release_id") is not None and (type(request["release_id"]) is not int or request["release_id"] <= 0):
        raise ReleaseError("Invalid deletion release ID")
    return expected


def control_release(api, project, *, create_sha=None):
    name = project["project"]
    tag = "ai11-local-retention-" + name
    matches = [r for r in api.pages("/releases") if r["tag_name"] == tag]
    if len(matches) > 1:
        raise ReleaseError("Multiple build-retention control releases; preserve and reconcile them")
    if matches:
        release = matches[0]
        if not release["draft"] or marker(name) not in (release.get("body") or ""):
            raise ReleaseError("Build-retention tag is occupied by a foreign release")
        return release
    if create_sha is None:
        return None
    branch = api.request("GET", "")["default_branch"]
    return api.request("POST", "/releases", {"tag_name": tag, "target_commitish": branch,
        "name": "Local build retention - " + name, "draft": True, "prerelease": True,
        "make_latest": "false", "body": marker(name) + "\nSmall deletion requests and OS receipts. Keep this private control draft so removed builds cannot return."})


def matching_release(api, request):
    matches = [r for r in api.pages("/releases") if r["tag_name"] == request["release_tag"]]
    if len(matches) > 1:
        raise ReleaseError("Multiple GitHub releases match this version")
    if not matches:
        return None
    release = matches[0]
    actual = api.tag_sha(request["release_tag"])
    if actual is None and release["draft"]:
        actual = release.get("target_commitish")
    if actual != request["sha"]:
        raise ReleaseError("GitHub release belongs to a different source SHA; it will not be deleted")
    if request.get("release_id") is not None and request["release_id"] != release["id"]:
        raise ReleaseError("GitHub release ID changed after deletion preview")
    return release


def preview(project, directory, *, api=None):
    directory = Path(directory).resolve()
    source = read_json(directory / ("job.json" if (directory / "job.json").exists() else "manifest.json"))
    request = {"schema": 1, "project": project["project"], "repository": read_json(Path(project["profile"]))["repository"],
        "version": source["version"], "build": source["build"], "sha": source["sha"],
        "request_id": uuid.uuid4().hex, "created": time.time(), "hosts": list(project["hosts"]),
        "release_tag": f"v{source['version']}+{source['build']}", "release_id": None}
    expected = validate(request, project)
    if expected != directory:
        raise ReleaseError("Deletion preview is outside the canonical build directory")
    api = api or api_for(project)
    release = matching_release(api, request)
    request["release_id"] = release["id"] if release else None
    asset_count = len(api.pages(f"/releases/{release['id']}/assets")) if release else 0
    packages = directory / "packages"
    sizes = [p.stat().st_size for p in packages.iterdir() if p.is_file()] if packages.exists() else []
    return {"request": request, "package_count": len(sizes), "package_bytes": sum(sizes),
            "github_release": release.get("html_url") if release else None,
            "github_asset_count": asset_count}


def mark_queue(project, request):
    root = Path(project["catalogue"])
    queue = root / (project["project"] + "-queue.json")
    if queue.exists():
        with lock(root / ".queue.lock"):
            data = read_json(queue)
            entry = data["commits"].setdefault(request["sha"], {"sequence": len(data["commits"]) + 1})
            entry.update(status="deleted", reason="Owner-confirmed deletion", deletion_request=request["request_id"])
            atomic_json(queue, data)


def verify_local_identity(directory, request):
    metadata = directory / ("job.json" if (directory / "job.json").exists() else "manifest.json")
    if metadata.exists():
        value = read_json(metadata)
        if any(value.get(key) != request[key] for key in ("project", "version", "build", "sha")):
            raise ReleaseError("Local build identity changed after deletion preview; files preserved")


def request_deletion(project, prepared):
    request = prepared["request"]
    directory = validate(request, project)
    path = record_path(project["catalogue"], request["project"], request["sha"])
    with lock(path.with_suffix(".lock")):
        verify_local_identity(directory, request)
        if path.exists():
            record = read_json(path)
        else:
            # This entry is written before stopping a builder or touching GitHub.
            record = {"request": request, "confirmed": time.time(), "status": "pending", "acks": {}}
            atomic_json(path, record)
        mark_queue(project, record["request"])
        if directory.exists():
            atomic_json(directory / "stop-request.json", {"source": "owner-confirmed deletion", "requested": time.time()})
    return record


def busy(directory):
    if not directory.exists():
        return False
    for host in ("windows", "linux", "macos"):
        try:
            with lock(directory / ("." + host + ".lock")):
                pass
        except ReleaseError as error:
            if str(error).startswith("Busy operation:"):
                return True
            raise
    return False


def safe_remove(root, target, expected_relative):
    """The caller supplies an engine-constructed path, never a request path."""
    root, target = Path(root).resolve(), Path(target)
    expected = root / expected_relative
    if target.absolute() != expected.absolute() or target.resolve() != expected.absolute() or not target.resolve().is_relative_to(root):
        raise ReleaseError("Refusing deletion outside the exact managed build path")
    if target.exists():
        def writable_owned_file(function, filename, error):
            candidate = Path(filename)
            if (not isinstance(error[1], PermissionError) or candidate.is_symlink()
                    or not candidate.resolve().is_relative_to(target.resolve())):
                raise error[1]
            # Git pack files can have the Windows readonly attribute. Only
            # this exact managed tree can have that attribute cleared.
            os.chmod(candidate, candidate.stat().st_mode | stat.S_IWRITE)
            function(filename)
        shutil.rmtree(target, onerror=writable_owned_file)


def cleanup_local(project, request, role):
    directory = validate(request, project)
    root = Path(project["catalogue"]).resolve()
    if busy(directory):
        if directory.exists():
            atomic_json(directory / "stop-request.json", {"source": "owner-confirmed deletion", "requested": time.time()})
        return False
    snapshot = root / "w" / request["sha"][:12]
    if snapshot.exists():
        if snapshot.resolve() != snapshot.absolute() or not snapshot.resolve().is_relative_to(root):
            raise ReleaseError("Builder snapshot is linked outside the catalogue")
        for child in snapshot.iterdir():
            if child.name not in {"w", "l", "m", "snap-input", "snap-cli", "snap-acceptance", "windows-test-state", "linux-test-state", "macos-test-state"}:
                raise ReleaseError("Unrecognized files in the builder snapshot; preserved for inspection")
            if (child / ".git").exists() and git(child, "rev-parse", "HEAD") != request["sha"]:
                raise ReleaseError("Builder snapshot belongs to another source SHA")
        journals = [snapshot / name / "restore.json" for name in ("windows-test-state", "linux-test-state", "macos-test-state", "snap-acceptance")]
        journals = [path for path in journals if path.exists()]
        if journals:
            if not (directory / "job.json").exists():
                raise ReleaseError("Owner-data recovery journal has no matching job; preserved")
            job = read_json(directory / "job.json")
            profile = read_json(Path(project["profile"]))
            if job["profile"]["adapter"] != profile["adapter"]:
                raise ReleaseError("Recovery adapter differs from the registered project")
            adapter = importlib.import_module(profile["adapter"])
            if not hasattr(adapter, "recover_for_deletion"):
                raise ReleaseError("Owner-data recovery must finish before deleting this build")
            adapter.recover_for_deletion(Context(directory, read_json(Path(project["config"])), host=role))
            if any(path.exists() for path in journals):
                raise ReleaseError("Owner-data recovery is still pending; build preserved")
    safe_remove(root, snapshot, Path("w") / request["sha"][:12])
    safe_remove(root, directory, directory.relative_to(root))
    if directory.parent.exists() and not any(directory.parent.iterdir()):
        directory.parent.rmdir()
    index = root / "github-index.json"
    if index.exists() and request.get("release_id"):
        with lock(root / ".archive.lock"):
            value = read_json(index)
            value.get("releases", {}).pop(str(request["release_id"]), None)
            value["current_release_ids"] = [identifier for identifier in value.get("current_release_ids", []) if identifier != request["release_id"]]
            atomic_json(index, value)
    return True


def upload_json(api, release, name, value):
    with tempfile.TemporaryDirectory(prefix="release-retention-") as folder:
        path = Path(folder) / name
        atomic_json(path, value)
        return api.upload_verified(release, path)


def process(project, sha, *, role=None, api=None):
    role = role or host_name()
    path = record_path(project["catalogue"], project["project"], sha)
    with lock(path.with_suffix(".lock")):
        record = read_json(path)
        request = record["request"]
        if request["sha"] != sha:
            raise ReleaseError("Deletion record belongs to a different source SHA")
        directory = validate(request, project)
        try:
            verify_local_identity(directory, request)
            api = api or api_for(project)
            control = control_release(api, project, create_sha=request["sha"])
            if not record.get("request_sent"):
                record["request_sent"] = upload_json(api, control, "delete-" + request["request_id"] + ".json", request)
                atomic_json(path, record)
            if busy(directory):
                record.update(status="stopping", error=None)
                atomic_json(path, record)
                return record
            if not record.get("github_deleted"):
                release = matching_release(api, request)
                if release:
                    api.request("DELETE", f"/releases/{release['id']}")
                    try:
                        api.request("GET", f"/releases/{release['id']}")
                    except GitHubHTTPError as error:
                        if error.status != 404:
                            raise
                    else:
                        raise ReleaseError("GitHub still returns the deleted release")
                record["github_deleted"] = True
                atomic_json(path, record)
            if not record.get("local_deleted"):
                if not cleanup_local(project, request, role):
                    record.update(status="stopping", error=None)
                    atomic_json(path, record)
                    return record
                record["local_deleted"] = True
                atomic_json(path, record)
            ack = {"schema": 1, "project": request["project"], "request_id": request["request_id"],
                   "sha": sha, "host": role, "deleted": True}
            if not record.get("ack_sent"):
                record["ack_sent"] = upload_json(api, control, f"ack-{request['request_id']}-{role}.json", ack)
            record.setdefault("acks", {})[role] = True
            record.update(status="complete" if set(request["hosts"]) <= set(record["acks"]) else "waiting_other_hosts", error=None)
            mark_queue(project, request)
        except Exception as error:
            record.update(status="failed", error=str(error))
        atomic_json(path, record)
        return record


def read_asset(api, asset):
    if asset["size"] > 64 * 1024:
        raise ReleaseError("Deletion control asset exceeds its bounded contract")
    with tempfile.TemporaryDirectory(prefix="release-retention-receive-") as folder:
        path = Path(folder) / "record.json"
        api.download_asset(asset, path)
        return read_json(path)


def synchronize(project, role=None, *, api=None):
    """Apply deletion requests before discovering or receiving any build jobs."""
    role = role or host_name()
    api = api or api_for(project)
    control = control_release(api, project)
    root = Path(project["catalogue"])
    known = {value["request"]["request_id"]: value for path in (root / "deletions" / project["project"]).glob("*.json")
             for value in [read_json(path)]}
    def metadata(asset):
        return {key: asset.get(key) for key in ("id", "size", "digest")}
    if control:
        assets = api.pages(f"/releases/{control['id']}/assets")
        owner = read_json(Path(project["profile"]))["repository"].split("/")[0]
        actor = read_json(Path(project["config"])).get("retention_actor", owner)
        for asset in assets:
            if not re.fullmatch(r"delete-[a-f0-9]{32}\.json", asset["name"]):
                continue
            if asset.get("uploader", {}).get("login") != actor:
                raise ReleaseError("Deletion request uploader is not the trusted repository owner")
            cached = known.get(asset["name"][7:-5])
            request = (cached["request"] if cached and asset.get("digest") and cached.get("control_asset") == metadata(asset)
                       else read_asset(api, asset))
            validate(request, project)
            if asset["name"] != "delete-" + request["request_id"] + ".json":
                raise ReleaseError("Deletion request ID differs from its asset")
            path = record_path(root, project["project"], request["sha"])
            with lock(path.with_suffix(".lock")):
                if path.exists():
                    record = read_json(path)
                    if record["request"] != request:
                        raise ReleaseError("Conflicting deletion tombstone; preserve and inspect")
                else:
                    record = {"request": request, "received": time.time(), "request_sent": {"id": asset["id"]}, "status": "pending", "acks": {}}
                record["control_asset"] = metadata(asset)
                for ack_asset in assets:
                    match = re.fullmatch(r"ack-" + request["request_id"] + r"-(windows|linux|macos)\.json", ack_asset["name"])
                    if match:
                        if ack_asset.get("uploader", {}).get("login") != actor:
                            raise ReleaseError("Deletion receipt uploader is not trusted")
                        cached_ack = record.setdefault("ack_assets", {}).get(match[1])
                        ack = ({"schema": 1, "project": request["project"], "request_id": request["request_id"],
                                "sha": request["sha"], "host": match[1], "deleted": True}
                               if ack_asset.get("digest") and cached_ack == metadata(ack_asset) else read_asset(api, ack_asset))
                        if ack != {"schema": 1, "project": request["project"], "request_id": request["request_id"],
                                   "sha": request["sha"], "host": match[1], "deleted": True}:
                            raise ReleaseError("Deletion receipt differs from the requested build")
                        record.setdefault("acks", {})[match[1]] = True
                        record["ack_assets"][match[1]] = metadata(ack_asset)
                atomic_json(path, record)
    results = []
    for path in (root / "deletions" / project["project"]).glob("*.json"):
        record = read_json(path)
        validate(record["request"], project)
        if path.stem != record["request"]["sha"]:
            raise ReleaseError("Deletion registry filename differs from its source SHA")
        if role in record["request"]["hosts"]:
            if record.get("local_deleted") and record.get("ack_sent"):
                record["status"] = "complete" if set(record["request"]["hosts"]) <= set(record.get("acks", {})) else "waiting_other_hosts"
                atomic_json(path, record)
                mark_queue(project, record["request"])
            else:
                record = process(project, record["request"]["sha"], role=role, api=api)
            results.append(record)
    return results


def summary(project):
    result = []
    for path in (Path(project["catalogue"]) / "deletions" / project["project"]).glob("*.json"):
        record = read_json(path)
        request = record["request"]
        validate(request, project)
        result.append({"sha": request["sha"], "version": request["version"], "build": request["build"],
            "status": record["status"], "local_deleted": bool(record.get("local_deleted")),
            "github_deleted": bool(record.get("github_deleted")),
            "waiting_hosts": [host for host in request["hosts"] if host not in record.get("acks", {})], "error": record.get("error")})
    return sorted(result, key=lambda value: value["build"], reverse=True)
