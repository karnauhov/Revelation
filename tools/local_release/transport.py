"""Bounded GitHub transport between isolated Windows and Linux builders.

Temporary exchange assets never contain credentials or distributed packages.
Only IDs recorded for this exact run are deleted, after durable local receipt.
"""

from __future__ import annotations

import io
import base64
import json
from pathlib import Path
import tarfile
import tempfile
import zipfile

from .core import (Context, ReleaseError, atomic_json, digest, host_name, inside,
                   lock, read_json, verify_runtime)
from .catalogue import catalogue_job, release_directory
from .github import GitHub, credential


def connection(ctx):
    token = credential(ctx.config)
    ctx.refresh_redaction([token])
    api = GitHub(ctx.job["repository"], token)
    release = api.ensure_release(ctx.job, ctx.job["release_notes"])
    return api, release


def prefix(job):
    return "local-transfer-" + job["run_id"] + "-"


def replace_exchange(api, release, path, job):
    """Replace only this run's explicitly mutable exchange metadata."""
    if not path.name.startswith(prefix(job)):
        raise ReleaseError("Refusing to replace a package or foreign exchange asset")
    assets = api.pages(f"/releases/{release['id']}/assets")
    old = next((a for a in assets if a["name"] == path.name), None)
    if old and old.get("digest") == "sha256:" + digest(path):
        return api.upload_verified(release, path)
    if old:
        api.request("DELETE", f"/releases/assets/{old['id']}")
    return api.upload_verified(release, path)


def handoff(ctx):
    api, release = connection(ctx)
    with lock(ctx.directory / ".exchange.lock"), tempfile.TemporaryDirectory(prefix="release-handoff-") as folder:
        path = Path(folder) / (prefix(ctx.job) + "job.tar.gz")
        # Freeze the transport payload only once. Subsequent status goes separately.
        names = ["job.json", "source.bundle", "release_notes.txt"]
        names += ["runtime/" + name for name in sorted(ctx.job["runtime_sha256"])]
        with tarfile.open(path, "w:gz") as archive:
            for name in names:
                source = inside(ctx.directory, name)
                info = tarfile.TarInfo(name)
                info.size, info.mode, info.mtime = source.stat().st_size, 0o644, 0
                with source.open("rb") as stream:
                    archive.addfile(info, stream)
        # gzip header timestamps differ; an existing immutable job asset is reused
        # only after inspecting its embedded job identity and all payload hashes.
        assets = api.pages(f"/releases/{release['id']}/assets")
        old = next((a for a in assets if a["name"] == path.name), None)
        if old:
            received = Path(folder) / "existing.tar.gz"
            actual = api.download_asset(old, received)
            with tarfile.open(received) as archive:
                saved = json.load(archive.extractfile("job.json"))
                if saved != ctx.job:
                    raise ReleaseError("Existing handoff belongs to a different prepared job")
            record = {"id": old["id"], "sha256": actual, "url": old["browser_download_url"]}
        else:
            record = api.upload_verified(release, path)
        atomic_json(ctx.directory / "exchange.json", {"release_id": release["id"], "job_asset": record,
                                                       "source_sha": ctx.job["sha"], "run_id": ctx.job["run_id"]})
        return release


def send_result(ctx):
    api, release = connection(ctx)
    with lock(ctx.directory / ".exchange.lock"), tempfile.TemporaryDirectory(prefix="release-result-") as folder:
        # Upload only outputs whose producing and host verification gates passed.
        required = ctx.job["required_steps"][ctx.host]
        verified = all(ctx.result["steps"].get(s, {}).get("status") == "passed" for s in required)
        package_records = {}
        if verified:
            for name in ctx.job["artifacts"]:
                path = ctx.output / name
                if path.is_file():
                    package_records[name] = api.upload_verified(release, path, allow_upload=release["draft"])
        log_path = Path(folder) / (prefix(ctx.job) + ctx.host + "-logs.zip")
        with zipfile.ZipFile(log_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted((ctx.directory / "logs" / ctx.host).glob("*.log")):
                # Redact again before export, including credentials loaded after preflight.
                archive.writestr(path.name, ctx.redact(path.read_text(encoding="utf-8")))
        logs = replace_exchange(api, release, log_path, ctx.job)
        status_path = Path(folder) / (prefix(ctx.job) + ctx.host + "-status.json")
        evidence = {}
        for step in ctx.result["steps"].values():
            if step.get("status") == "passed":
                for relative, expected in step.get("outputs", {}).items():
                    if relative.startswith("results/"):
                        source = inside(ctx.directory, relative)
                        if digest(source) != expected or source.stat().st_size > 20 * 1024**2:
                            raise ReleaseError("Invalid result evidence")
                        evidence[relative] = base64.b64encode(source.read_bytes()).decode("ascii")
        payload = {"schema": 1, "run_id": ctx.job["run_id"], "sha": ctx.job["sha"],
                   "version": ctx.job["version"], "build": ctx.job["build"], "host": ctx.host,
                   "result": ctx.result, "packages": package_records, "logs": logs, "evidence": evidence,
                   "receipts": {}}
        received_job = ctx.directory / "received.json"
        if received_job.exists():
            payload["receipts"]["job"] = read_json(received_job)
        for peer in ctx.job["required_steps"]:
            receipt = ctx.directory / "results" / f"{peer}-received.json"
            if peer != ctx.host and receipt.exists():
                payload["receipts"][peer] = read_json(receipt)
        atomic_json(status_path, json.loads(ctx.redact(json.dumps(payload))))
        status = replace_exchange(api, release, status_path, ctx.job)
        atomic_json(ctx.directory / "results" / f"{ctx.host}-sent.json", {"status": status, "logs": logs})
        (ctx.directory / "results" / f"{ctx.host}-outbox.json").unlink(missing_ok=True)


def receive_jobs(profile, root, config, tag=None):
    api = GitHub(profile["repository"], credential(config))
    received = []
    for release in api.pages("/releases"):
        if tag and release["tag_name"] != tag:
            continue
        marker = "<!-- local-release:" + profile["project"] + "-"
        if marker not in (release.get("body") or ""):
            continue
        assets = api.pages(f"/releases/{release['id']}/assets")
        asset = next((a for a in assets if a["name"].startswith("local-transfer-" + profile["project"] + "-")
                      and a["name"].endswith("-job.tar.gz")), None)
        if not asset:
            continue
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="release-receive-") as folder:
            downloaded = Path(folder) / "job.tar.gz"
            transport_digest = api.download_asset(asset, downloaded)
            extracted = Path(folder) / "extracted"
            extracted.mkdir()
            with tarfile.open(downloaded) as archive:
                members = archive.getmembers()
                if sum(m.size for m in members) > 1024**3 or len(members) > 100:
                    raise ReleaseError("Unexpected handoff size")
                for member in members:
                    if not member.isfile():
                        raise ReleaseError("Handoff must contain regular files only")
                    destination = inside(extracted, member.name)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as source, destination.open("wb") as stream:
                        __import__("shutil").copyfileobj(source, stream)
            job = read_json(extracted / "job.json")
            if job["profile"] != profile or job["repository"] != profile["repository"]:
                raise ReleaseError("Received profile differs from this project")
            if f"<!-- local-release:{job['run_id']} -->" not in release["body"] or job["tag"] != release["tag_name"]:
                raise ReleaseError("Received job does not match the draft release")
            if release["target_commitish"] != job["sha"] and api.tag_sha(job["tag"]) != job["sha"]:
                raise ReleaseError("Received source SHA differs from release")
            verify_runtime(extracted)
            if digest(extracted / "source.bundle") != job["source_bundle_sha256"]:
                raise ReleaseError("Received source bundle digest mismatch")
            destination = release_directory(root, job["project"], job["version"], job["build"], job["sha"])
            if (destination / "job.json").exists():
                if read_json(destination / "job.json") != job:
                    raise ReleaseError("Local job differs from received immutable job")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    raise ReleaseError("Local catalogue exists without matching job; reconcile before receiving")
                __import__("shutil").copytree(extracted, destination)
            atomic_json(destination / "received.json", {"asset_id": asset["id"], "sha256": transport_digest,
                                                        "release_id": release["id"], "run_id": job["run_id"]})
            received.append(destination)
    return received


def sync_results(ctx, *, cleanup=False):
    api, release = connection(ctx)
    assets = api.pages(f"/releases/{release['id']}/assets")
    by_id = {a["id"]: a for a in assets}
    imported = []
    for host in ctx.job["required_steps"]:
        if host == ctx.host:
            continue
        name = prefix(ctx.job) + host + "-status.json"
        status = next((a for a in assets if a["name"] == name), None)
        if not status:
            continue
        with tempfile.TemporaryDirectory(prefix="release-sync-") as folder:
            path = Path(folder) / "status.json"
            status_digest = api.download_asset(status, path)
            payload = read_json(path)
            if (payload["run_id"], payload["sha"], payload["version"], payload["build"], payload["host"]) != (
                    ctx.job["run_id"], ctx.job["sha"], ctx.job["version"], ctx.job["build"], host):
                raise ReleaseError("Remote result belongs to a different build")
            result = payload["result"]
            if (result["run_id"], result["sha"], result["host"]) != (ctx.job["run_id"], ctx.job["sha"], host):
                raise ReleaseError("Remote result identity mismatch")
            expected_evidence = {relative: expected for step in result["steps"].values()
                                 if step.get("status") == "passed"
                                 for relative, expected in step.get("outputs", {}).items()
                                 if relative.startswith("results/")}
            if set(payload.get("evidence", {})) != set(expected_evidence):
                raise ReleaseError("Remote result evidence is incomplete")
            for relative, value in payload.get("evidence", {}).items():
                content = base64.b64decode(value, validate=True)
                if len(content) > 20 * 1024**2 or __import__("hashlib").sha256(content).hexdigest() != expected_evidence[relative]:
                    raise ReleaseError("Remote evidence digest mismatch")
                target = inside(ctx.directory, relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            for package_name, record in payload["packages"].items():
                if package_name not in ctx.job["artifacts"]:
                    raise ReleaseError("Unexpected remote package")
                asset = by_id.get(record["id"])
                if not asset or asset["name"] != package_name:
                    raise ReleaseError("Remote package asset ID mismatch")
                local = inside(ctx.output, package_name)
                if local.exists():
                    if digest(local) != record["sha256"]:
                        raise ReleaseError("Local package collision; existing file preserved")
                else:
                    if api.download_asset(asset, local) != record["sha256"]:
                        raise ReleaseError("Remote package hash mismatch")
            logs = by_id.get(payload["logs"]["id"])
            if not logs or logs["name"] != prefix(ctx.job) + host + "-logs.zip":
                raise ReleaseError("Remote log asset ID mismatch")
            log_zip = Path(folder) / "logs.zip"
            if api.download_asset(logs, log_zip) != payload["logs"]["sha256"]:
                raise ReleaseError("Remote logs digest mismatch")
            with zipfile.ZipFile(log_zip) as archive:
                if sum(i.file_size for i in archive.infolist()) > 512 * 1024**2:
                    raise ReleaseError("Remote log archive is unexpectedly large")
                for item in archive.infolist():
                    if Path(item.filename).name != item.filename or not item.filename.endswith(".log"):
                        raise ReleaseError("Unsafe log path")
                    target = inside(ctx.directory / "logs" / host, item.filename)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(item))
            atomic_json(ctx.directory / "results" / f"{host}.json", result)
            receipt = {"run_id": ctx.job["run_id"], "sha": ctx.job["sha"], "host": host,
                       "status_asset_id": status["id"], "status_sha256": status_digest,
                       "log_asset_id": logs["id"], "logs_sha256": payload["logs"]["sha256"]}
            atomic_json(ctx.directory / "results" / f"{host}-received.json", receipt)
            imported.append(receipt)
            if cleanup and ctx.host == "windows":
                # A failed Linux run can return before receiving Windows
                # results. Delete forward payloads only with exact acknowledgments.
                owned = [status, logs]
                acknowledgments = payload.get("receipts", {})
                job_ack = acknowledgments.get("job", {})
                exchange_path = ctx.directory / "exchange.json"
                if exchange_path.exists():
                    exchange = read_json(exchange_path)
                    sent_job = exchange["job_asset"]
                    asset = by_id.get(sent_job["id"])
                    if (asset and asset["name"] == prefix(ctx.job) + "job.tar.gz"
                            and job_ack.get("asset_id") == sent_job["id"]
                            and job_ack.get("sha256") == sent_job["sha256"]
                            and job_ack.get("release_id") == release["id"]
                            and job_ack.get("run_id") == ctx.job["run_id"]):
                        owned.append(asset)
                own_sent = ctx.directory / "results/windows-sent.json"
                if own_sent.exists():
                    sent = read_json(own_sent)
                    peer_ack = acknowledgments.get("windows", {})
                    acknowledged = (peer_ack.get("run_id") == ctx.job["run_id"]
                                    and peer_ack.get("sha") == ctx.job["sha"]
                                    and peer_ack.get("host") == "windows"
                                    and peer_ack.get("status_asset_id") == sent["status"]["id"]
                                    and peer_ack.get("status_sha256") == sent["status"]["sha256"]
                                    and peer_ack.get("log_asset_id") == sent["logs"]["id"]
                                    and peer_ack.get("logs_sha256") == sent["logs"]["sha256"])
                    if acknowledged:
                        for key, suffix in (("status", "windows-status.json"), ("logs", "windows-logs.zip")):
                            asset = by_id.get(sent[key]["id"])
                            if asset and asset["name"] == prefix(ctx.job) + suffix:
                                owned.append(asset)
                for asset in owned:
                    api.request("DELETE", f"/releases/assets/{asset['id']}")
                atomic_json(ctx.directory / "results/exchange-cleanup.json", {
                    "run_id": ctx.job["run_id"], "removed_asset_ids": [a["id"] for a in owned],
                    "receipt": receipt, "packages_preserved": True})
    catalogue_job(ctx)
    return imported
