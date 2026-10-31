"""GitHub Releases transport. Never overwrite an existing asset or foreign tag."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request

from .core import ReleaseError, SourceUnavailable, atomic_json, digest, lock, read_json, hidden_flags


class GitHubHTTPError(ReleaseError):
    def __init__(self, message, status):
        super().__init__(message)
        self.status = status


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def credential(config):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    if config.get("github_token_file"):
        return Path(config["github_token_file"]).read_text(encoding="utf-8").strip()
    if config.get("github_git_credential"):
        # Ask the native credential helper, never the browser or Git config text.
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
        result = subprocess.run(["git", "credential", "fill"],
                                input="protocol=https\nhost=github.com\n\n",
                                capture_output=True, text=True, env=env, check=False, creationflags=hidden_flags())
        fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
        if result.returncode == 0 and fields.get("password"):
            return fields["password"]
    if shutil.which("gh"):
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=False, creationflags=hidden_flags())
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    raise ReleaseError("GitHub release authentication missing on this OS; configure GH_TOKEN or a local token file")


class GitHub:
    def __init__(self, repository, token):
        if not __import__("re").fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ReleaseError("Invalid GitHub repository")
        self.base = "https://api.github.com/repos/" + repository
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect)

    def request(self, method, path, data=None, content_type="application/json", raw=False):
        url = path if path.startswith("https://") else self.base + path
        if urllib.parse.urlparse(url).hostname not in ("api.github.com", "uploads.github.com"):
            raise ReleaseError("Refusing authenticated request to a non-GitHub API host")
        payload = data if isinstance(data, bytes) else (json.dumps(data).encode() if data is not None else None)
        headers = {"Accept": "application/octet-stream" if raw else "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "AI11-local-release",
                   "Content-Type": content_type}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        try:
            response = self.opener.open(urllib.request.Request(url, payload, headers, method=method), timeout=180)
        except urllib.error.HTTPError as error:
            if raw and error.code in (301, 302, 303, 307, 308):
                location = error.headers["Location"]
                parsed = urllib.parse.urlparse(location)
                if parsed.scheme != "https" or not parsed.hostname.endswith(".githubusercontent.com"):
                    raise ReleaseError("Unexpected release asset download redirect") from error
                # Signed download URLs do not receive the GitHub credential.
                response = urllib.request.urlopen(location, timeout=180)
            else:
                raise GitHubHTTPError(f"GitHub {method} {urllib.parse.urlparse(url).path}: HTTP {error.code}", error.code) from None
        with response:
            body = response.read()
        return body if raw else json.loads(body or b"null")

    def pages(self, path):
        result = []
        page = 1
        while True:
            items = self.request("GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
            result.extend(items)
            if len(items) < 100:
                return result
            page += 1

    def download_asset(self, asset, destination):
        """Stream to disk; API credentials never follow signed CDN redirects."""
        url = asset["url"]
        if not url.startswith(self.base + "/releases/assets/"):
            raise ReleaseError("Asset URL does not belong to the selected repository")
        headers = {"Accept": "application/octet-stream", "User-Agent": "AI11-local-release"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        try:
            response = self.opener.open(urllib.request.Request(url, headers=headers), timeout=180)
        except urllib.error.HTTPError as error:
            if error.code not in (301, 302, 303, 307, 308):
                raise ReleaseError(f"Asset {asset['id']}: HTTP {error.code}") from None
            location = error.headers["Location"]
            parsed = urllib.parse.urlparse(location)
            if parsed.scheme != "https" or not parsed.hostname.endswith(".githubusercontent.com"):
                raise ReleaseError("Unexpected asset CDN redirect") from None
            response = urllib.request.urlopen(location, timeout=180)
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(destination.name + ".partial")
        try:
            with response, partial.open("wb") as stream:
                while block := response.read(1024 * 1024):
                    stream.write(block)
                stream.flush()
                os.fsync(stream.fileno())
            if partial.stat().st_size != asset["size"]:
                raise ReleaseError("Downloaded asset size mismatch")
            expected = asset.get("digest")
            actual = digest(partial)
            if expected and expected != "sha256:" + actual:
                raise ReleaseError("Downloaded asset publisher digest mismatch")
            os.replace(partial, destination)
            return actual
        finally:
            partial.unlink(missing_ok=True)

    def tag_sha(self, tag):
        encoded = urllib.parse.quote(tag, safe="")
        try:
            ref = self.request("GET", "/git/ref/tags/" + encoded)["object"]
        except ReleaseError as error:
            if "HTTP 404" in str(error):
                return None
            raise
        while ref["type"] == "tag":
            ref = self.request("GET", "/git/tags/" + ref["sha"])["object"]
        return ref["sha"]

    def require_source(self, sha):
        try:
            self.request("GET", "/commits/" + sha)
        except GitHubHTTPError as error:
            if error.status == 404:
                raise SourceUnavailable("Waiting for exact source SHA to be accessible on GitHub: " + sha) from None
            raise

    def ensure_release(self, job, notes):
        self.require_source(job["sha"])
        tag_sha = self.tag_sha(job["tag"])
        if tag_sha is not None and tag_sha != job["sha"]:
            raise ReleaseError("Release tag collision: different source SHA; use the version helper for a new commit")
        releases = self.pages("/releases")
        existing = [r for r in releases if r["tag_name"] == job["tag"]]
        marker = f"<!-- local-release:{job['run_id']} -->"
        if existing:
            release = existing[0]
            if marker not in (release.get("body") or ""):
                raise ReleaseError("Existing release is foreign; refusing modification")
            if release["target_commitish"] != job["sha"] and tag_sha != job["sha"]:
                raise ReleaseError("Draft release targets a different SHA")
            return release
        return self.request("POST", "/releases", {
            "tag_name": job["tag"], "target_commitish": job["sha"],
            "name": f"Release v{job['version']} ({job['build']})", "body": notes + "\n\n" + marker,
            "draft": True, "prerelease": False,
        })

    def upload_verified(self, release, path, *, allow_upload=True, asset_name=None):
        expected = digest(path)
        name = asset_name or path.name
        assets = self.pages(f"/releases/{release['id']}/assets")
        found = next((a for a in assets if a["name"] == name), None)
        if found:
            if found["size"] != path.stat().st_size:
                raise ReleaseError("Asset collision: " + path.name)
            previous = getattr(self, "verified_assets", {}).get(found["id"], {})
            if (previous.get("sha256") == expected and previous.get("size") == path.stat().st_size
                    and found.get("digest") == "sha256:" + expected):
                # The first upload was downloaded and recorded durably. An
                # unchanged immutable ID plus GitHub's fresh digest reuses it.
                return {"id": found["id"], "url": found["browser_download_url"],
                        "sha256": expected, "size": path.stat().st_size, "asset_name": name}
        else:
            if not allow_upload:
                raise ReleaseError("Published release is missing an expected asset")
            url = release["upload_url"].split("{", 1)[0] + "?name=" + urllib.parse.quote(name)
            found = self.request("POST", url, path.read_bytes(), "application/octet-stream")
        with tempfile.TemporaryDirectory(prefix="local-release-readback-") as temporary:
            actual = self.download_asset(found, Path(temporary) / path.name)
            if actual != expected:
                raise ReleaseError("Downloaded asset digest mismatch: " + path.name)
        return {"id": found["id"], "url": found["browser_download_url"],
                "sha256": expected, "size": path.stat().st_size, "asset_name": name}


def complete_results(directory, job):
    records = {}
    for host, required_steps in job["required_steps"].items():
        path = directory / "results" / f"{host}.json"
        if not path.exists():
            return False
        result = read_json(path)
        if result["sha"] != job["sha"] or result["run_id"] != job["run_id"]:
            raise ReleaseError("Mixed release results")
        if any(result["steps"].get(step, {}).get("status") != "passed" for step in required_steps):
            return False
        if job.get("compile_defines_sha256") and result.get("compile_defines_sha256") != job["compile_defines_sha256"]:
            raise ReleaseError("Builder compile settings differ between operating systems")
        for step in required_steps:
            for relative, expected in result["steps"][step].get("outputs", {}).items():
                from .core import inside
                path = inside(directory, relative)
                if not path.is_file() or digest(path) != expected:
                    raise ReleaseError("Result artifact changed: " + relative)
        records[host] = result
    return True


def reconcile_published(context):
    """An offline peer recognizes final publication after transport cleanup."""
    directory, job = context.directory, context.job
    publication_path = directory / "publication.json"
    saved = read_json(publication_path) if publication_path.exists() else {}
    if saved.get("published"):
        return True
    received = directory / "received.json"
    release_id = saved.get("release_id") or (read_json(received).get("release_id") if received.exists() else None)
    if not release_id:
        return False
    token = credential(context.config)
    context.refresh_redaction([token])
    api = GitHub(job["repository"], token)
    release = api.request("GET", f"/releases/{release_id}")
    if release["draft"]:
        return False
    if (release["tag_name"] != job["tag"] or f"<!-- local-release:{job['run_id']} -->" not in (release.get("body") or "")
            or api.tag_sha(job["tag"]) != job["sha"]):
        raise ReleaseError("Published release identity differs from this local job")
    assets = {asset["name"]: asset for asset in api.pages(f"/releases/{release_id}/assets")}
    manifest = assets.get("release-manifest.json")
    if not manifest or manifest["size"] > 256 * 1024:
        raise ReleaseError("Published release has no bounded final manifest")
    with tempfile.TemporaryDirectory(prefix="release-publication-receipt-") as folder:
        path = Path(folder) / "manifest.json"
        actual = api.download_asset(manifest, path)
        summary = read_json(path)
        manifest_bytes = path.read_bytes()
    if any(summary.get(key) != job.get(key) for key in (
            "run_id", "sha", "version", "build", "tag", "source_bundle_sha256", "compile_defines_sha256")):
        raise ReleaseError("Published manifest differs from the immutable local source")
    if any(not set(gates) <= set(summary.get("verified_gates", {}).get(role, [])) for role, gates in job["required_steps"].items()):
        raise ReleaseError("Published manifest omits required release gates")
    if set(summary.get("packages", {})) != set(job["artifacts"]):
        raise ReleaseError("Published manifest omits expected packages")
    records = {}
    for name, record in summary["packages"].items():
        asset = assets.get(name)
        if not asset or asset["size"] != record["size"] or asset.get("digest") != "sha256:" + record["sha256"]:
            raise ReleaseError("Published package metadata differs from the final manifest")
        local = context.output / name
        if local.exists() and digest(local) != record["sha256"]:
            raise ReleaseError("Local package differs from the completed public release")
        records[name] = {**record, "id": asset["id"], "url": asset["browser_download_url"], "asset_name": name}
    checksum_bytes = "".join(f"{records[name]['sha256']}  {name}\n" for name in sorted(job["artifacts"])).encode()
    checksum_hash = hashlib.sha256(checksum_bytes).hexdigest()
    checksums = assets.get("SHA256SUMS")
    if not checksums or checksums.get("digest") != "sha256:" + checksum_hash or checksums["size"] != len(checksum_bytes):
        raise ReleaseError("Published checksums differ from the final package manifest")
    (directory / "release-manifest.json").write_bytes(manifest_bytes)
    (context.output / "SHA256SUMS").write_bytes(checksum_bytes)
    atomic_json(directory / "results/publication-received.json", {"schema": 1, "run_id": job["run_id"],
        "manifest_asset_id": manifest["id"], "manifest_sha256": actual, "verified_gates": summary["verified_gates"]})
    saved.update(run_id=job["run_id"], sha=job["sha"], tag=job["tag"], release_id=release_id,
        published=True, url=release["html_url"], assets=records, completion_source="verified-public-manifest")
    saved["manifest"] = {"id": manifest["id"], "sha256": actual, "size": manifest["size"], "url": manifest["browser_download_url"]}
    saved["checksums"] = {"id": checksums["id"], "sha256": checksum_hash, "size": checksums["size"], "url": checksums["browser_download_url"]}
    saved.pop("waiting", None)
    atomic_json(publication_path, saved)
    from .catalogue import catalogue_job
    catalogue_job(context)
    return True


def publish_job(context):
    job, directory = context.job, context.directory
    token = credential(context.config)
    context.refresh_redaction([token])
    api = GitHub(job["repository"], token)
    with lock(directory / ".publication.lock"):
        publication_path = directory / "publication.json"
        saved = read_json(publication_path) if publication_path.exists() else {}
        api.verified_assets = {record["id"]: record for record in list(saved.get("assets", {}).values())
                               + [saved.get("checksums", {}), saved.get("manifest", {})] if "id" in record}
        notes = (directory / "release_notes.txt").read_text(encoding="utf-8")
        with lock(directory / ".release.lock"):
            release = api.ensure_release(job, notes)
        saved.update(run_id=job["run_id"], sha=job["sha"], tag=job["tag"],
                     release_id=release["id"], url=release["html_url"], published=False)
        saved.setdefault("assets", {})
        atomic_json(publication_path, saved)
        # Only upload artifacts whose producing stage passed on the same SHA.
        allowed = set()
        for host in job["required_steps"]:
            result_path = directory / "results" / f"{host}.json"
            if result_path.exists():
                result = read_json(result_path)
                if (result["sha"], result["run_id"]) != (job["sha"], job["run_id"]):
                    raise ReleaseError("Mixed release artifacts")
                if any(result["steps"].get(name, {}).get("status") != "passed" for name in job["required_steps"][host]):
                    continue
                for step in result["steps"].values():
                    if step.get("status") == "passed":
                        for relative, expected in step.get("outputs", {}).items():
                            path = directory / relative
                            if path.parent == context.output and path.is_file() and digest(path) == expected:
                                allowed.add(path.name)
        for name in job["artifacts"]:
            if name in allowed:
                saved["assets"][name] = api.upload_verified(release, context.output / name, allow_upload=release["draft"])
                atomic_json(publication_path, saved)
        complete = complete_results(directory, job)
        if complete and set(saved["assets"]) == set(job["artifacts"]):
            checksums = context.output / "SHA256SUMS"
            checksums.write_text("".join(f"{saved['assets'][n]['sha256']}  {n}\n" for n in sorted(job["artifacts"])),
                                 encoding="utf-8", newline="\n")
            saved["checksums"] = api.upload_verified(release, checksums, allow_upload=release["draft"])
            summary = directory / "release-manifest.json"
            atomic_json(summary, {
                "schema": 1, "run_id": job["run_id"], "sha": job["sha"],
                "version": job["version"], "build": job["build"], "tag": job["tag"],
                "verified_gates": job["required_steps"], "architectures": job.get("architectures", {}),
                "runtime_sha256": job["runtime_sha256"], "source_bundle_sha256": job["source_bundle_sha256"],
                "compile_defines_sha256": job.get("compile_defines_sha256"),
                "packages": {name: {"sha256": saved["assets"][name]["sha256"], "size": saved["assets"][name]["size"]}
                             for name in sorted(job["artifacts"])},
            })
            saved["manifest"] = api.upload_verified(release, summary, allow_upload=release["draft"])
            # Re-read asset inventory and tag immediately before making the draft public.
            actual = api.pages(f"/releases/{release['id']}/assets")
            expected = set(job["artifacts"]) | {"SHA256SUMS", "release-manifest.json"}
            transport_prefix = "local-transfer-" + job["run_id"] + "-"
            if {a["name"] for a in actual if not a["name"].startswith(transport_prefix)} != expected:
                raise ReleaseError("Unexpected or missing draft assets")
            if api.tag_sha(job["tag"]) not in (None, job["sha"]):
                raise ReleaseError("Tag changed during publication")
            if release["draft"]:
                release = api.request("PATCH", f"/releases/{release['id']}", {"draft": False, "make_latest": "false"})
            confirmed = api.request("GET", f"/releases/{release['id']}")
            if confirmed["draft"] or api.tag_sha(job["tag"]) != job["sha"]:
                raise ReleaseError("Published release read-back failed")
            saved.pop("waiting", None)
            saved.update(published=True, url=confirmed["html_url"])
        else:
            saved["waiting"] = "Other builders or required gates are incomplete"
        atomic_json(publication_path, saved)
