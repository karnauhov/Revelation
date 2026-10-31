"""Restore GitHub assets into the one canonical local release directory."""

from pathlib import Path
import re

from .core import ReleaseError, atomic_json, digest, inside, lock, read_json
from .github import GitHub, credential
from .catalogue import release_directory


def archive_releases(profile, root: Path, config):
    try:
        token = credential(config)
    except ReleaseError:
        if not config.get("allow_public_archive"):
            raise
        token = None
    api = GitHub(profile["repository"], token)
    root.mkdir(parents=True, exist_ok=True)
    with lock(root / ".archive.lock"):
        index_path = root / "github-index.json"
        index = read_json(index_path) if index_path.exists() else {
            "schema": 1, "repository": profile["repository"], "releases": {}}
        if index["repository"] != profile["repository"]:
            raise ReleaseError("Archive belongs to a different repository")
        releases = api.pages("/releases")
        for release in releases:
            release_id = str(release["id"])
            match = re.fullmatch(r"v(\d+\.\d+\.\d+)\+(\d+)", release["tag_name"])
            sha = api.tag_sha(release["tag_name"])
            # An owned draft can exist before GitHub creates its tag. Exchange
            # payloads are not historical package assets and must never be copied.
            target = release.get("target_commitish", "")
            if sha:
                target = sha
            owned = (re.fullmatch(r"[0-9a-f]{40}", target) is not None
                     and f"<!-- local-release:{profile['project']}-{target} -->" in (release.get("body") or ""))
            if not sha and release["draft"] and owned:
                sha = target
            if not match or not sha:
                raise ReleaseError("Historical release needs explicit version/build and source tag SHA: " + release["tag_name"])
            directory = release_directory(root, profile["project"], match.group(1), int(match.group(2)), sha)
            directory.mkdir(parents=True, exist_ok=True)
            atomic_json(directory / "github-release.json", release)
            record = index["releases"].setdefault(release_id, {"tag": release["tag_name"], "assets": {}})
            record.update(url=release["html_url"], draft=release["draft"], catalogue=directory.relative_to(root).as_posix())
            manifest_path = directory / "manifest.json"
            local_manifest = read_json(manifest_path) if manifest_path.exists() else {
                "schema": 1, "project": profile["project"], "version": match.group(1), "build": int(match.group(2)),
                "sha": sha, "source": "github-archive", "status": "incomplete" if release["draft"] else "archived", "packages": {},
            }
            assets = api.pages(f"/releases/{release_id}/assets")
            for asset in assets:
                if owned and asset["name"].startswith(f"local-transfer-{profile['project']}-{target}-"):
                    continue
                if Path(asset["name"]).name != asset["name"] or "\\" in asset["name"]:
                    raise ReleaseError("Unsafe remote asset name")
                metadata = owned and asset["name"] == "release-manifest.json"
                path = inside(directory, asset["name"] if metadata else "packages/" + asset["name"])
                section = local_manifest.setdefault("metadata", {}) if metadata else local_manifest["packages"]
                saved = section.get(asset["name"])
                if path.exists():
                    actual = digest(path)
                    if saved and (actual != saved["sha256"] or path.stat().st_size != asset["size"]):
                        raise ReleaseError("Existing package differs; preserved: " + str(path))
                    publisher_digest = asset.get("digest")
                    if publisher_digest and publisher_digest != "sha256:" + actual:
                        raise ReleaseError("Remote asset changed; existing local package preserved")
                    if not saved or saved.get("asset_id") != asset["id"]:
                        candidate = path.with_name(path.name + ".readback")
                        try:
                            if api.download_asset(asset, candidate) != actual:
                                raise ReleaseError("Unindexed package differs from GitHub")
                        finally:
                            candidate.unlink(missing_ok=True)
                else:
                    actual = api.download_asset(asset, path)
                package = {"name": asset["name"], "size": asset["size"], "sha256": actual,
                           "path": path.relative_to(directory).as_posix(), "asset_id": asset["id"],
                           "publisher_digest": asset.get("digest"), "url": asset["browser_download_url"]}
                section[asset["name"]] = package
                record["assets"][str(asset["id"])] = {"name": asset["name"], "sha256": actual,
                                                      "path": path.relative_to(root).as_posix()}
                atomic_json(manifest_path, local_manifest)
                atomic_json(index_path, index)
                print(f"ARCHIVED {release['tag_name']}/{asset['name']}", flush=True)
            record["current_asset_ids"] = [a["id"] for a in assets]
            atomic_json(index_path, index)
        index["current_release_ids"] = [r["id"] for r in releases]
        atomic_json(index_path, index)
        return index
