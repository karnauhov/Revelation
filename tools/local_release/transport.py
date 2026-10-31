"""Bounded GitHub transport between isolated Windows and Linux builders.

Temporary exchange assets never contain credentials or distributed packages.
Only IDs recorded for this exact run are deleted, after durable local receipt.
"""

from __future__ import annotations

import io
import base64
import json
import re
from pathlib import Path
import tarfile
import tempfile
import zipfile

from .core import (Context, ReleaseError, atomic_json, digest, host_name, inside,
                   lock, read_json, verify_runtime)
from .catalogue import catalogue_job, release_directory
from .github import GitHub, credential
from .protocol import VERSION, draft_packages, same_source


def connection(ctx):
    token = credential(ctx.config)
    ctx.refresh_redaction([token])
    api = GitHub(ctx.job["repository"], token)
    with lock(ctx.directory / ".release.lock"):
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
                if saved != ctx.job and not (same_source(saved, ctx.job) and ctx.job.get("preparation_revision", 1) > saved.get("preparation_revision", 1)):
                    raise ReleaseError("Existing handoff belongs to a different prepared job")
            record = {"id": old["id"], "sha256": actual, "url": old["browser_download_url"]}
        else:
            record = api.upload_verified(release, path)
        atomic_json(ctx.directory / "exchange.json", {"release_id": release["id"], "job_asset": record,
                                                       "source_sha": ctx.job["sha"], "run_id": ctx.job["run_id"]})
        if old and saved != ctx.job:
            from .runtime_update import send_update
            send_update(ctx)
        return release


def send_result(ctx):
    api, release = connection(ctx)
    with lock(ctx.directory / ".exchange.lock"), tempfile.TemporaryDirectory(prefix="release-result-") as folder:
        # Upload only outputs whose producing and host verification gates passed.
        package_records = {}
        for name, inspection in draft_packages(ctx).items():
            asset_name = (prefix(ctx.job) + ctx.host + "-package-" + inspection["sha256"] + "-" + name
                          if ctx.job.get("protocol_version", 1) >= 2 else name)
            package_records[name] = {**api.upload_verified(release, ctx.output / name, allow_upload=release["draft"], asset_name=asset_name),
                                     **inspection}
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
        payload = {"schema": 1, "protocol_version": VERSION, "run_id": ctx.job["run_id"], "sha": ctx.job["sha"],
                   "runtime_revision": ctx.job.get("preparation_revision", 1),
                   "version": ctx.job["version"], "build": ctx.job["build"], "host": ctx.host,
                   "result": ctx.result, "packages": package_records, "logs": logs, "evidence": evidence,
                   "receipts": {}}
        received_job = ctx.directory / "received.json"
        if received_job.exists():
            payload["receipts"]["job"] = read_json(received_job)
        runtime_receipts = ctx.directory / "results/runtime-updates-received.json"
        if runtime_receipts.exists():
            payload["receipts"]["runtime_updates"] = read_json(runtime_receipts)
        for peer in ctx.job["required_steps"]:
            receipt = ctx.directory / "results" / f"{peer}-received.json"
            if peer != ctx.host and receipt.exists():
                payload["receipts"][peer] = read_json(receipt)
        atomic_json(status_path, json.loads(ctx.redact(json.dumps(payload))))
        status = replace_exchange(api, release, status_path, ctx.job)
        atomic_json(ctx.directory / "results" / f"{ctx.host}-sent.json", {"status": status, "logs": logs, "packages": package_records})
        (ctx.directory / "results" / f"{ctx.host}-outbox.json").unlink(missing_ok=True)
        from .catalogue import catalogue_job
        catalogue_job(ctx)


def receive_runtime_updates(api, assets, job, destination, folder):
    from .runtime_update import unpack, install
    expression = re.compile(re.escape(prefix(job)) + r"runtime-v(\d+)\.tar\.gz$")
    updates = sorted((int(match.group(1)), item) for item in assets if (match := expression.fullmatch(item["name"])))
    for revision, item in updates:
        if revision <= read_json(destination / "job.json").get("preparation_revision", 1):
            continue
        patch = Path(folder) / f"runtime-v{revision}.tar.gz"
        patch_digest = api.download_asset(item, patch)
        patch_dir = Path(folder) / f"runtime-v{revision}"
        patch_dir.mkdir()
        unpack(patch, patch_dir, 16 * 1024**2)
        install(destination, patch_dir)
        receipt_path = destination / "results/runtime-updates-received.json"
        receipts = read_json(receipt_path) if receipt_path.exists() else []
        receipts.append({"asset_id": item["id"], "sha256": patch_digest, "revision": revision})
        atomic_json(receipt_path, receipts)


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
        version = re.fullmatch(r"v(\d+\.\d+\.\d+)\+(\d+)", release["tag_name"])
        target_sha = release.get("target_commitish", "")
        if version and re.fullmatch(r"[0-9a-f]{40}", target_sha):
            known = release_directory(root, profile["project"], version[1], int(version[2]), target_sha)
            receipt_path = known / "received.json"
            if (known / "job.json").exists() and receipt_path.exists() and (known / "source.bundle").is_file():
                receipt = read_json(receipt_path)
                if receipt.get("asset_id") == asset["id"] and asset.get("digest", "sha256:" + receipt["sha256"]) == "sha256:" + receipt["sha256"]:
                    current = read_json(known / "job.json")
                    if f"<!-- local-release:{current['run_id']} -->" not in release["body"]:
                        raise ReleaseError("Cached job ownership marker differs")
                    verify_runtime(known)
                    with tempfile.TemporaryDirectory(prefix="release-update-receive-") as folder:
                        receive_runtime_updates(api, assets, current, known, folder)
                    received.append(known)
                    continue
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
            if any(job["profile"].get(key) != profile.get(key) for key in ("project", "repository", "adapter", "flutter")) or job["repository"] != profile["repository"]:
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
                current = read_json(destination / "job.json")
                if current != job and not (same_source(current, job) and current.get("preparation_revision", 1) >= job.get("preparation_revision", 1)):
                    raise ReleaseError("Local job differs from received immutable job")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    raise ReleaseError("Local catalogue exists without matching job; reconcile before receiving")
                __import__("shutil").copytree(extracted, destination)
            atomic_json(destination / "received.json", {"asset_id": asset["id"], "sha256": transport_digest,
                                                        "release_id": release["id"], "run_id": job["run_id"]})
            receive_runtime_updates(api, assets, job, destination, folder)
            received.append(destination)
    return received


def sync_results(ctx, *, cleanup=False):
    with lock(ctx.directory / ".exchange.lock"):
        return _sync_results(ctx, cleanup=cleanup)


def _sync_results(ctx, *, cleanup=False):
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
            if payload.get("protocol_version", 1) > VERSION:
                raise ReleaseError("Unsupported result exchange protocol")
            if (payload["run_id"], payload["sha"], payload["version"], payload["build"], payload["host"]) != (
                    ctx.job["run_id"], ctx.job["sha"], ctx.job["version"], ctx.job["build"], host):
                raise ReleaseError("Remote result belongs to a different build")
            result = payload["result"]
            if (result["run_id"], result["sha"], result["host"]) != (ctx.job["run_id"], ctx.job["sha"], host):
                raise ReleaseError("Remote result identity mismatch")
            local_result_path = ctx.directory / "results" / f"{host}.json"
            if local_result_path.exists() and read_json(local_result_path).get("runtime_revision", 1) > payload.get("runtime_revision", 1):
                continue
            result["runtime_revision"] = payload.get("runtime_revision", 1)
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
                if not any(step.get("status") == "passed" and step.get("outputs", {}).get("packages/" + package_name) == record["sha256"]
                           for step in result["steps"].values()):
                    raise ReleaseError("Remote package is not attested by a producing checkpoint")
                spec = ctx.job.get("artifact_specs", {}).get(package_name)
                if spec and (spec["host"] != host or record.get("verification") == "structure_verified" and any(result["steps"].get(gate, {}).get("status") != "passed" for gate in spec["gates"])):
                    raise ReleaseError("Remote package inspection gates are incomplete")
                asset = by_id.get(record["id"])
                expected_name = (prefix(ctx.job) + host + "-package-" + record["sha256"] + "-" + package_name
                                 if payload.get("protocol_version", 1) >= 2 and ctx.job.get("protocol_version", 1) >= 2 else package_name)
                if not asset or asset["name"] != expected_name:
                    raise ReleaseError("Remote package asset ID mismatch")
                local = inside(ctx.output, package_name)
                if local.exists():
                    if digest(local) != record["sha256"]:
                        manifest_path = ctx.directory / "manifest.json"
                        manifest = read_json(manifest_path) if manifest_path.exists() else {}
                        pending = manifest.get("unverified_packages", {}).get(package_name, {})
                        if pending.get("sha256") != digest(local) or not pending.get("source_asset_id"):
                            raise ReleaseError("Local package collision; existing file preserved")
                        replacement = Path(folder) / package_name
                        if api.download_asset(asset, replacement) != record["sha256"]:
                            raise ReleaseError("Replacement package digest mismatch; original preserved")
                        replacement.replace(local)
                        manifest["unverified_packages"].pop(package_name)
                        atomic_json(manifest_path, manifest)
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
                       "log_asset_id": logs["id"], "logs_sha256": payload["logs"]["sha256"], "packages": payload["packages"]}
            atomic_json(ctx.directory / "results" / f"{host}-received.json", receipt)
            imported.append(receipt)
            if cleanup and ctx.host == "windows":
                from .github import complete_results
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
                    if (complete_results(ctx.directory, ctx.job) and asset and asset["name"] == prefix(ctx.job) + "job.tar.gz"
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
                runtime_sent = ctx.directory / "results/runtime-update-sent.json"
                if runtime_sent.exists() and complete_results(ctx.directory, ctx.job):
                    sent_update = read_json(runtime_sent)
                    for ack in acknowledgments.get("runtime_updates", []):
                        if ack.get("asset_id") == sent_update["id"] and ack.get("sha256") == sent_update["sha256"]:
                            asset = by_id.get(sent_update["id"])
                            if asset and re.fullmatch(re.escape(prefix(ctx.job)) + r"runtime-v\d+\.tar\.gz", asset["name"]):
                                owned.append(asset)
                publication_path = ctx.directory / "publication.json"
                if publication_path.exists() and read_json(publication_path).get("published"):
                    mirror = read_json(publication_path)["assets"]
                    temporary_packages = list(payload["packages"].items())
                    if own_sent.exists():
                        temporary_packages += list(read_json(own_sent).get("packages", {}).items())
                    for name, record in temporary_packages:
                        asset = by_id.get(record["id"])
                        canonical = mirror.get(name, {})
                        if (asset and asset["name"].startswith(prefix(ctx.job))
                                and canonical.get("sha256") == record["sha256"]
                                and canonical.get("id") != record["id"]
                                and digest(ctx.output / name) == record["sha256"]):
                            owned.append(asset)
                owned = list({asset["id"]: asset for asset in owned}.values())
                for asset in owned:
                    api.request("DELETE", f"/releases/assets/{asset['id']}")
                atomic_json(ctx.directory / "results/exchange-cleanup.json", {
                    "run_id": ctx.job["run_id"], "removed_asset_ids": [a["id"] for a in owned],
                    "receipt": receipt, "packages_preserved": True})
    if cleanup and ctx.host == "windows":
        close_published_exchange(ctx, api, release)
    catalogue_job(ctx)
    return imported


def close_published_exchange(ctx, api, release):
    """Close an entire finished exchange after a durable verified final receipt.

    Per-message acknowledgments still govern incomplete releases. Once all gates
    and nine canonical assets are verified, neither OS needs obsolete repairs or
    transport copies. Unknown files and other runs are never deletion candidates.
    """
    from .core import verify_runtime
    from .github import complete_results
    publication_path = ctx.directory / "publication.json"
    if not publication_path.exists():
        return
    published = read_json(publication_path)
    if not published.get("published") or release["draft"] or not complete_results(ctx.directory, ctx.job):
        return
    if published.get("release_id") != release["id"] or published.get("sha") != ctx.job["sha"]:
        raise ReleaseError("Final exchange receipt has a different release identity")
    verify_runtime(ctx.directory)
    if digest(ctx.directory / "source.bundle") != ctx.job["source_bundle_sha256"]:
        raise ReleaseError("Canonical source snapshot changed; temporary exchange retained")
    assets = api.pages(f"/releases/{release['id']}/assets")
    by_id = {asset["id"]: asset for asset in assets}
    records = {**published.get("assets", {}), "SHA256SUMS": published.get("checksums", {}),
               "release-manifest.json": published.get("manifest", {})}
    if set(records) != set(ctx.job["artifacts"]) | {"SHA256SUMS", "release-manifest.json"}:
        raise ReleaseError("Canonical publication is incomplete; temporary exchange retained")
    for name, record in records.items():
        path = ctx.directory / "release-manifest.json" if name == "release-manifest.json" else ctx.output / name
        asset = by_id.get(record.get("id"))
        if (not asset or asset["name"] != name or asset["size"] != record.get("size")
                or not path.is_file() or digest(path) != record.get("sha256")):
            raise ReleaseError("Canonical publication differs from final receipt; exchange retained")
        if asset.get("digest"):
            if asset["digest"] != "sha256:" + record["sha256"]:
                raise ReleaseError("Canonical GitHub digest differs from final receipt")
        else:
            with tempfile.TemporaryDirectory(prefix="release-final-receipt-") as folder:
                if api.download_asset(asset, Path(folder) / name) != record["sha256"]:
                    raise ReleaseError("Canonical GitHub read-back differs from final receipt")
    transport_prefix = prefix(ctx.job)
    candidates = []
    for asset in assets:
        if not asset["name"].startswith(transport_prefix):
            continue
        tail = asset["name"][len(transport_prefix):]
        recognized = tail == "job.tar.gz" or re.fullmatch(r"runtime-v\d+\.tar\.gz|(?:windows|linux)-(?:status\.json|logs\.zip)", tail)
        for name in ctx.job["artifacts"]:
            recognized = recognized or re.fullmatch(r"(?:windows|linux)-package-[0-9a-f]{64}-" + re.escape(name), tail)
        if recognized:
            candidates.append({key: asset.get(key) for key in ("id", "name", "size", "digest")})
    receipt_path = ctx.directory / "results/exchange-closed.json"
    previous = read_json(receipt_path) if receipt_path.exists() else {}
    receipt = {"schema": 1, "run_id": ctx.job["run_id"], "sha": ctx.job["sha"],
        "release_id": release["id"], "published_assets": records, "all_required_gates_passed": True,
        "source_bundle_sha256": ctx.job["source_bundle_sha256"], "temporary_assets": candidates,
        "removed_asset_ids": previous.get("removed_asset_ids", [])}
    # Persist exact IDs and final package/source/gate proofs before the first DELETE.
    atomic_json(receipt_path, receipt)
    for asset in candidates:
        api.request("DELETE", f"/releases/assets/{asset['id']}")
        receipt["removed_asset_ids"].append(asset["id"])
        atomic_json(receipt_path, receipt)
