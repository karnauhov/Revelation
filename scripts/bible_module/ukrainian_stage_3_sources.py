from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import ssl
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode, urlparse

from .fetch_sources import sha256_file


PACKAGE_DIR = Path(__file__).resolve().parent
REPORT_DIR = PACKAGE_DIR / "reports" / "ukrainian_stage_3_20260801"
SOURCE_LOCK_PATH = REPORT_DIR / "source_lock.json"
FETCH_LOG_PATH = REPORT_DIR / "fetch_log.json"
SOURCE_FILES_CSV_PATH = REPORT_DIR / "source_files.csv"
SOURCE_CACHE_DIR = PACKAGE_DIR / "source_cache"

LOCK_SCHEMA_VERSION = 1
FETCH_LOG_SCHEMA_VERSION = 1
USER_AGENT = "Revelation Ukrainian Bible source locker/3"
LOCKED_ON = "2026-08-01"
MAX_ATTEMPTS = 4
MAX_REDIRECTS = 5
MEDIAWIKI_DISCOVERY_INTERVAL_SECONDS = 1.0
MEDIAWIKI_REVISION_INTERVAL_SECONDS = 6.5
RETRYABLE_HTTP_STATUSES = frozenset({429, 500, 502, 503, 504})

STEPBIBLE_COMMIT = "b9dcc831a98e0fd6f3c7e122be9ff68377c310c0"
OSHB_TAG = "v.2.2"
OSHB_COMMIT = "6a5db284c715c18b239422e57bb89684e6a19f00"
UGNT_TAG = "v0.34"
UGNT_COMMIT = "fc95b2b8aad08bb65ab54628ab685413a1139e97"
CROSSWIRE_KJV_VERSION = "3.1 (2023-07-19)"
CROSSWIRE_KJV_COMMIT = "d490be7e34762deb2c76cb2c1306d4808e27890d"
COMMONS_SHA1 = "8995dec8cfd20c212dc48e91868f115d3b8d17cc"
COMMONS_SHA256 = "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34"
COMMONS_BYTES = 83_637_482
INTERNET_ARCHIVE_SHA256 = (
    "39d34d366554a2c798e180d0fce05a4ca11fc8c10901c174848e37f30468cee8"
)

WIKISOURCE_API_URL = "https://uk.wikisource.org/w/api.php"
WIKISOURCE_ROOT_TITLE = "Біблія"
WIKISOURCE_INDEX_TITLE = "Індекс:Ivan Ohienko Bible.djvu"
WIKISOURCE_PAGE_PREFIX = "Сторінка:Ivan Ohienko Bible.djvu/"
WIKISOURCE_PAGE_COUNT = 1538
WIKISOURCE_EXPECTED_ROOT_REVISION = 442425
WIKISOURCE_EXPECTED_INDEX_REVISION = 960013
WIKISOURCE_EXPECTED_PAGE_ONE_REVISION = 107971
WIKISOURCE_EXPECTED_LAST_PAGE_REVISION = 108567
WIKISOURCE_REVISION_LOCK_SHA256 = (
    "ecce2e6d48a07f7baac96b393b1147a4f3b28c5eba6ac757f4de8f5b8a697dc9"
)
WIKISOURCE_BUNDLE_BYTES = 8_372_816
WIKISOURCE_BUNDLE_SHA256 = (
    "c7bc09ffdb232ded0abae6b631e382d896396750e3d3931ba5ee07e22c3e0702"
)

REQUIRED_ROLES = frozenset(
    {
        "ukrainian_print_reference",
        "ukrainian_machine_transcription",
        "ukrainian_dependent_scan_control",
        "primary_ot_strong_morphology",
        "primary_nt_strong_morphology",
        "dependent_ot_strong_crosscheck",
        "independent_ot_surface_control",
        "independent_nt_strong_control",
        "classic_strong_audit_control",
        "versification_traditions_control",
    }
)

EXPECTED_SOURCE_IDS = frozenset(
    {
        "commons_ohienko_1988_scan",
        "crosswire_kjv_3_1",
        "internet_archive_ohienko_1988_scan",
        "openscriptures_oshb_v2_2",
        "step_tagnt_act_rev",
        "step_tagnt_mat_jhn",
        "step_tahot_gen_deu",
        "step_tahot_isa_mal",
        "step_tahot_job_sng",
        "step_tahot_jos_est",
        "step_tvtms",
        "tanach_us_uxlc_2_5_27_6",
        "unfoldingword_ugnt_v0_34",
        "wikisource_ohienko_1988_revisions",
    }
)

REQUIRED_ENTRY_FIELDS = frozenset(
    {
        "source_id",
        "dataset_id",
        "title",
        "role_id",
        "role",
        "independence",
        "source_page_url",
        "download_url",
        "version",
        "pin",
        "retrieved_on",
        "bytes",
        "sha256",
        "license",
        "license_url",
        "local_path",
        "dependencies",
        "acquisition",
    }
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
_UNPINNED_URL_PATTERNS = (
    re.compile(r"(?:^|[/=?&_-])latest(?:$|[/=?&#_-])", re.IGNORECASE),
    re.compile(r"/(?:main|master|head)(?:/|$)", re.IGNORECASE),
    re.compile(r"[?&](?:ref|revision|version)=(?:main|master|head|latest)(?:&|$)", re.IGNORECASE),
)


class SourceLockError(RuntimeError):
    """Raised when a source cannot be obtained exactly as locked."""


class _AttemptError(SourceLockError):
    def __init__(
        self,
        message: str,
        *,
        retryable: bool,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.details = dict(details or {})


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _manifest_local_path(target_path: Path, manifest_path: Path) -> str:
    try:
        return Path(
            os.path.relpath(target_path.resolve(), start=manifest_path.parent.resolve())
        ).as_posix()
    except (OSError, ValueError):
        return target_path.as_posix()


def _resolve_local_path(
    entry: Mapping[str, object],
    *,
    manifest_path: Path,
    cache_dir_override: Path | None,
) -> Path:
    local_path_value = entry.get("local_path")
    if not isinstance(local_path_value, str) or not local_path_value:
        raise SourceLockError(f"{entry.get('source_id', '<unknown>')}: missing local_path")
    if cache_dir_override is not None:
        return cache_dir_override / Path(local_path_value).name
    local_path = Path(local_path_value)
    if local_path.is_absolute():
        return local_path
    return manifest_path.parent / local_path


def _download_once(
    *,
    url: str,
    target_path: Path,
    expected_bytes: int,
    max_redirects: int,
) -> dict[str, object]:
    return _curl_request_once(
        url=url,
        target_path=target_path,
        max_redirects=max_redirects,
        expected_bytes=expected_bytes,
    )


def _read_json_once(*, url: str, max_redirects: int) -> tuple[object, dict[str, object]]:
    temp_handle = tempfile.NamedTemporaryFile("wb", delete=False, suffix=".json")
    temp_path = Path(temp_handle.name)
    temp_handle.close()
    try:
        metadata = _curl_request_once(
            url=url,
            target_path=temp_path,
            max_redirects=max_redirects,
            expected_bytes=None,
        )
        payload = temp_path.read_bytes()
        try:
            return json.loads(payload), metadata
        except json.JSONDecodeError as error:
            raise _AttemptError(
                f"invalid JSON from {url}: {error}",
                retryable=False,
                details=metadata,
            ) from error
    finally:
        temp_path.unlink(missing_ok=True)


def _parse_curl_header_blocks(raw_headers: str) -> list[dict[str, object]]:
    responses: list[dict[str, object]] = []
    normalized = raw_headers.replace("\r\n", "\n")
    for raw_block in normalized.split("\n\n"):
        lines = [line for line in raw_block.splitlines() if line]
        if not lines or not lines[0].startswith("HTTP/"):
            continue
        status_parts = lines[0].split(maxsplit=2)
        if len(status_parts) < 2 or not status_parts[1].isdigit():
            continue
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if ":" not in line:
                continue
            name, value = line.split(":", 1)
            headers[name.strip().lower()] = value.strip()
        responses.append(
            {
                "status": int(status_parts[1]),
                "location": headers.get("location"),
                "content_type": headers.get("content-type"),
                "content_length": headers.get("content-length"),
                "etag": headers.get("etag"),
                "last_modified": headers.get("last-modified"),
            }
        )
    return responses


def _leaf_certificate_summary(certs: object) -> dict[str, object]:
    if not isinstance(certs, str) or not certs:
        return {"available": False}
    fields: dict[str, object] = {"available": True}
    for line in certs.splitlines():
        if line.startswith("-----BEGIN CERTIFICATE-----"):
            break
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        normalized_name = name.strip().lower().replace(" ", "_")
        if normalized_name in {
            "subject",
            "issuer",
            "start_date",
            "expire_date",
            "serial_number",
            "signature_algorithm",
        }:
            fields[normalized_name] = value.strip()
    return fields


def _curl_request_once(
    *,
    url: str,
    target_path: Path,
    max_redirects: int,
    expected_bytes: int | None,
) -> dict[str, object]:
    if urlparse(url).scheme.lower() != "https":
        raise _AttemptError(
            f"non-HTTPS URL rejected: {url}",
            retryable=False,
            details={"requested_url": url},
        )
    header_handle = tempfile.NamedTemporaryFile("wb", delete=False, suffix=".headers")
    header_path = Path(header_handle.name)
    header_handle.close()
    command = [
        "curl.exe" if os.name == "nt" else "curl",
        "--location",
        "--max-redirs",
        str(max_redirects),
        "--proto",
        "=https",
        "--proto-redir",
        "=https",
        "--connect-timeout",
        "30",
        "--max-time",
        "120",
        "--silent",
        "--show-error",
        "--fail-with-body",
        "--user-agent",
        USER_AGENT,
        "--dump-header",
        str(header_path),
        "--output",
        str(target_path),
        "--write-out",
        "%{json}",
    ]
    if expected_bytes is not None:
        command.extend(["--max-filesize", str(expected_bytes)])
    command.append(url)
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=135,
        )
        try:
            curl_json = json.loads(completed.stdout) if completed.stdout else {}
        except json.JSONDecodeError:
            curl_json = {}
        header_responses = _parse_curl_header_blocks(
            header_path.read_text(encoding="iso-8859-1", errors="replace")
        )
        redirects = [
            response
            for response in header_responses
            if int(response["status"]) in {301, 302, 303, 307, 308}
        ]
        metadata: dict[str, object] = {
            "requested_url": url,
            "final_url": curl_json.get("url_effective"),
            "status": curl_json.get("http_code"),
            "redirect_chain": redirects,
            "redirect_count": curl_json.get("num_redirects"),
            "downloaded_bytes": curl_json.get("size_download"),
            "response_headers": header_responses[-1] if header_responses else {},
            "tls": {
                "backend": str(curl_json.get("curl_version", "unknown")),
                "verify_result": curl_json.get("ssl_verify_result"),
                "peer_certificate": _leaf_certificate_summary(
                    curl_json.get("certs")
                ),
            },
            "remote_ip": curl_json.get("remote_ip"),
            "http_version": curl_json.get("http_version"),
            "elapsed_seconds": curl_json.get("time_total"),
        }
        if completed.returncode != 0:
            status = curl_json.get("http_code")
            retryable = (
                isinstance(status, int) and status in RETRYABLE_HTTP_STATUSES
            ) or completed.returncode in {5, 6, 7, 18, 28, 35, 52, 55, 56, 92}
            metadata["curl_exit_code"] = completed.returncode
            metadata["error"] = completed.stderr.strip() or curl_json.get("errormsg")
            raise _AttemptError(
                f"curl failed for {url}: {metadata['error']}",
                retryable=retryable,
                details=metadata,
            )
        return metadata
    except subprocess.TimeoutExpired as error:
        raise _AttemptError(
            f"curl timed out for {url}",
            retryable=True,
            details={"requested_url": url, "error": str(error)},
        ) from error
    except FileNotFoundError as error:
        raise _AttemptError(
            "curl executable is required for verified system TLS on this host",
            retryable=False,
            details={"requested_url": url, "error": str(error)},
        ) from error
    finally:
        header_path.unlink(missing_ok=True)


def _with_retries(
    action: Callable[[], dict[str, object]],
    *,
    max_attempts: int,
    sleep: Callable[[float], None],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    attempts: list[dict[str, object]] = []
    for attempt_number in range(1, max_attempts + 1):
        started_at = _utc_now_iso()
        try:
            result = action()
            attempts.append(
                {
                    "attempt": attempt_number,
                    "started_at_utc": started_at,
                    "finished_at_utc": _utc_now_iso(),
                    "result": "success",
                    **result,
                }
            )
            return result, attempts
        except _AttemptError as error:
            attempts.append(
                {
                    "attempt": attempt_number,
                    "started_at_utc": started_at,
                    "finished_at_utc": _utc_now_iso(),
                    "result": "error",
                    "retryable": error.retryable,
                    "error": str(error),
                    **error.details,
                }
            )
            if not error.retryable or attempt_number == max_attempts:
                raise SourceLockError(str(error)) from error
            sleep(float(2**attempt_number))
    raise AssertionError("retry loop exhausted unexpectedly")


def _verify_locked_file(path: Path, entry: Mapping[str, object]) -> None:
    source_id = str(entry.get("source_id", "<unknown>"))
    expected_bytes = entry.get("bytes")
    expected_sha256 = entry.get("sha256")
    if not isinstance(expected_bytes, int) or expected_bytes <= 0:
        raise SourceLockError(f"{source_id}: invalid locked bytes")
    if not isinstance(expected_sha256, str) or not _SHA256_RE.fullmatch(
        expected_sha256
    ):
        raise SourceLockError(f"{source_id}: invalid locked SHA-256")
    if not path.exists():
        raise SourceLockError(f"{source_id}: cached source is missing: {path}")
    actual_bytes = path.stat().st_size
    if actual_bytes != expected_bytes:
        raise SourceLockError(
            f"{source_id}: size mismatch: expected {expected_bytes}, got {actual_bytes}"
        )
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise SourceLockError(
            f"{source_id}: checksum mismatch: expected {expected_sha256}, "
            f"got {actual_sha256}"
        )


def _fetch_https_file(
    entry: Mapping[str, object],
    *,
    target_path: Path,
    force: bool,
    offline: bool,
    max_attempts: int,
    sleep: Callable[[float], None],
) -> dict[str, object]:
    source_id = str(entry["source_id"])
    if target_path.exists() and not force:
        _verify_locked_file(target_path, entry)
        return {
            "source_id": source_id,
            "status": "cache_hit",
            "local_path": str(target_path),
            "bytes": target_path.stat().st_size,
            "sha256": sha256_file(target_path),
            "attempts": [],
        }
    if offline:
        if target_path.exists():
            _verify_locked_file(target_path, entry)
        raise SourceLockError(f"{source_id}: offline cache miss: {target_path}")

    expected_bytes = int(entry["bytes"])
    acquisition = entry.get("acquisition")
    if not isinstance(acquisition, Mapping):
        raise SourceLockError(f"{source_id}: invalid acquisition metadata")
    max_redirects = int(acquisition.get("max_redirects", MAX_REDIRECTS))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_handle = tempfile.NamedTemporaryFile(
        "wb",
        delete=False,
        dir=str(target_path.parent),
        prefix=f".{target_path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_handle.name)
    temp_handle.close()
    try:
        _, attempts = _with_retries(
            lambda: _download_once(
                url=str(entry["download_url"]),
                target_path=temp_path,
                expected_bytes=expected_bytes,
                max_redirects=max_redirects,
            ),
            max_attempts=max_attempts,
            sleep=sleep,
        )
        _verify_locked_file(temp_path, entry)
        os.replace(temp_path, target_path)
        return {
            "source_id": source_id,
            "status": "downloaded",
            "local_path": str(target_path),
            "bytes": target_path.stat().st_size,
            "sha256": sha256_file(target_path),
            "attempts": attempts,
        }
    finally:
        temp_path.unlink(missing_ok=True)


def _request_json_with_retries(
    *,
    url: str,
    max_redirects: int,
    max_attempts: int,
    sleep: Callable[[float], None],
) -> tuple[object, list[dict[str, object]]]:
    payload_holder: dict[str, object] = {}

    def action() -> dict[str, object]:
        payload, metadata = _read_json_once(url=url, max_redirects=max_redirects)
        payload_holder["payload"] = payload
        return metadata

    _, attempts = _with_retries(
        action,
        max_attempts=max_attempts,
        sleep=sleep,
    )
    return payload_holder["payload"], attempts


def _wikisource_title_sort_key(title: str) -> tuple[int, int]:
    if title == WIKISOURCE_ROOT_TITLE:
        return (0, 0)
    if title == WIKISOURCE_INDEX_TITLE:
        return (1, 0)
    if title.startswith(WIKISOURCE_PAGE_PREFIX):
        return (2, int(title.removeprefix(WIKISOURCE_PAGE_PREFIX)))
    raise SourceLockError(f"unexpected Wikisource title: {title}")


def _expected_wikisource_titles() -> list[str]:
    return [
        WIKISOURCE_ROOT_TITLE,
        WIKISOURCE_INDEX_TITLE,
        *[
            f"{WIKISOURCE_PAGE_PREFIX}{page_number}"
            for page_number in range(1, WIKISOURCE_PAGE_COUNT + 1)
        ],
    ]


def discover_wikisource_revision_lock() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    records: list[dict[str, object]] = []
    requests: list[dict[str, object]] = []
    root_url = f"{WIKISOURCE_API_URL}?{urlencode(
        {
            'action': 'query',
            'prop': 'revisions',
            'rvprop': 'ids|timestamp|sha1|size',
            'titles': f'{WIKISOURCE_ROOT_TITLE}|{WIKISOURCE_INDEX_TITLE}',
            'format': 'json',
            'formatversion': '2',
        }
    )}"
    pending_urls: list[str] = [root_url]
    continue_parameters: dict[str, str] = {}
    while pending_urls:
        url = pending_urls.pop(0)
        payload, attempts = _request_json_with_retries(
            url=url,
            max_redirects=MAX_REDIRECTS,
            max_attempts=MAX_ATTEMPTS,
            sleep=time.sleep,
        )
        requests.extend(attempts)
        time.sleep(MEDIAWIKI_DISCOVERY_INTERVAL_SECONDS)
        if not isinstance(payload, Mapping):
            raise SourceLockError("invalid Wikisource discovery response")
        query = payload.get("query")
        pages = query.get("pages") if isinstance(query, Mapping) else None
        if not isinstance(pages, list):
            raise SourceLockError("Wikisource discovery response has no pages")
        for page in pages:
            if not isinstance(page, Mapping) or page.get("missing") is True:
                raise SourceLockError("missing Wikisource page in discovery response")
            revisions = page.get("revisions")
            if not isinstance(revisions, list) or len(revisions) != 1:
                raise SourceLockError(f"invalid latest revision for {page.get('title')}")
            revision = revisions[0]
            if not isinstance(revision, Mapping):
                raise SourceLockError(f"invalid revision for {page.get('title')}")
            records.append(
                {
                    "page_id": int(page["pageid"]),
                    "namespace": int(page["ns"]),
                    "title": str(page["title"]),
                    "revision_id": int(revision["revid"]),
                    "parent_revision_id": int(revision["parentid"]),
                    "timestamp": str(revision["timestamp"]),
                    "size": int(revision["size"]),
                    "sha1": str(revision["sha1"]),
                }
            )
        if url == root_url:
            generator_parameters = {
                "action": "query",
                "generator": "allpages",
                "gapnamespace": "250",
                "gapprefix": "Ivan Ohienko Bible.djvu/",
                "gaplimit": "max",
                "prop": "revisions",
                "rvprop": "ids|timestamp|sha1|size",
                "format": "json",
                "formatversion": "2",
            }
            pending_urls.append(f"{WIKISOURCE_API_URL}?{urlencode(generator_parameters)}")
        elif isinstance(payload.get("continue"), Mapping):
            continue_parameters = {
                str(key): str(value)
                for key, value in payload["continue"].items()
            }
            generator_parameters = {
                "action": "query",
                "generator": "allpages",
                "gapnamespace": "250",
                "gapprefix": "Ivan Ohienko Bible.djvu/",
                "gaplimit": "max",
                "prop": "revisions",
                "rvprop": "ids|timestamp|sha1|size",
                "format": "json",
                "formatversion": "2",
                **continue_parameters,
            }
            pending_urls.append(f"{WIKISOURCE_API_URL}?{urlencode(generator_parameters)}")
    records.sort(key=lambda record: _wikisource_title_sort_key(str(record["title"])))
    titles = _expected_wikisource_titles()
    if [record["title"] for record in records] != titles:
        raise SourceLockError("Wikisource discovery did not return the complete title set")
    if records[0]["revision_id"] != WIKISOURCE_EXPECTED_ROOT_REVISION:
        raise SourceLockError("unexpected Wikisource root revision")
    if records[1]["revision_id"] != WIKISOURCE_EXPECTED_INDEX_REVISION:
        raise SourceLockError("unexpected Wikisource index revision")
    return records, requests


def _revision_lock_sha256(records: Sequence[Mapping[str, object]]) -> str:
    lines = []
    for record in records:
        lines.append(
            "\t".join(
                str(record[field])
                for field in (
                    "page_id",
                    "namespace",
                    "title",
                    "revision_id",
                    "parent_revision_id",
                    "timestamp",
                    "size",
                    "sha1",
                )
            )
        )
    return _sha256_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def _materialize_wikisource_bundle(
    *,
    revision_records: Sequence[Mapping[str, object]],
    target_path: Path,
    max_redirects: int,
    max_attempts: int,
    sleep: Callable[[float], None],
) -> list[dict[str, object]]:
    expected_by_revision = {
        int(record["revision_id"]): record for record in revision_records
    }
    content_records: list[dict[str, object]] = []
    request_attempts: list[dict[str, object]] = []
    revision_ids = list(expected_by_revision)
    for offset in range(0, len(revision_ids), 50):
        revision_batch = revision_ids[offset : offset + 50]
        url = f"{WIKISOURCE_API_URL}?{urlencode(
            {
                'action': 'query',
                'prop': 'revisions',
                'revids': '|'.join(str(revision_id) for revision_id in revision_batch),
                'rvprop': 'ids|timestamp|sha1|size|content',
                'rvslots': 'main',
                'format': 'json',
                'formatversion': '2',
            }
        )}"
        payload, attempts = _request_json_with_retries(
            url=url,
            max_redirects=max_redirects,
            max_attempts=max_attempts,
            sleep=sleep,
        )
        request_attempts.extend(attempts)
        sleep(MEDIAWIKI_REVISION_INTERVAL_SECONDS)
        if not isinstance(payload, Mapping):
            raise SourceLockError("invalid Wikisource revision response")
        query = payload.get("query")
        pages = query.get("pages") if isinstance(query, Mapping) else None
        if not isinstance(pages, list):
            raise SourceLockError("Wikisource revision response has no pages")
        for page in pages:
            if not isinstance(page, Mapping):
                raise SourceLockError("invalid Wikisource page response")
            revisions = page.get("revisions")
            if not isinstance(revisions, list) or len(revisions) != 1:
                raise SourceLockError("invalid Wikisource pinned revision response")
            revision = revisions[0]
            if not isinstance(revision, Mapping):
                raise SourceLockError("invalid Wikisource revision object")
            revision_id = int(revision["revid"])
            expected = expected_by_revision.get(revision_id)
            if expected is None:
                raise SourceLockError(f"unexpected Wikisource revision {revision_id}")
            actual_metadata = {
                "page_id": int(page["pageid"]),
                "namespace": int(page["ns"]),
                "title": str(page["title"]),
                "revision_id": revision_id,
                "parent_revision_id": int(revision["parentid"]),
                "timestamp": str(revision["timestamp"]),
                "size": int(revision["size"]),
                "sha1": str(revision["sha1"]),
            }
            if actual_metadata != dict(expected):
                raise SourceLockError(
                    f"Wikisource metadata mismatch for revision {revision_id}"
                )
            slots = revision.get("slots")
            main_slot = slots.get("main") if isinstance(slots, Mapping) else None
            if not isinstance(main_slot, Mapping) or not isinstance(
                main_slot.get("content"), str
            ):
                raise SourceLockError(
                    f"Wikisource revision {revision_id} has no main-slot content"
                )
            content_records.append(
                {
                    **actual_metadata,
                    "content_model": str(main_slot.get("contentmodel", "wikitext")),
                    "content_format": str(main_slot.get("contentformat", "text/x-wiki")),
                    "content": str(main_slot["content"]),
                }
            )
    content_records.sort(
        key=lambda record: _wikisource_title_sort_key(str(record["title"]))
    )
    if [int(record["revision_id"]) for record in content_records] != revision_ids:
        raise SourceLockError("Wikisource content bundle is incomplete or reordered")
    bundle = {
        "schema_version": 1,
        "source_id": "wikisource_ohienko_1988_revisions",
        "api_url": WIKISOURCE_API_URL,
        "revision_lock_sha256": _revision_lock_sha256(revision_records),
        "revision_count": len(content_records),
        "revisions": content_records,
    }
    target_path.write_bytes(_json_bytes(bundle))
    return request_attempts


def _fetch_wikisource_bundle(
    entry: Mapping[str, object],
    *,
    target_path: Path,
    force: bool,
    offline: bool,
    max_attempts: int,
    sleep: Callable[[float], None],
) -> dict[str, object]:
    source_id = str(entry["source_id"])
    if target_path.exists() and not force:
        _verify_locked_file(target_path, entry)
        return {
            "source_id": source_id,
            "status": "cache_hit",
            "local_path": str(target_path),
            "bytes": target_path.stat().st_size,
            "sha256": sha256_file(target_path),
            "attempts": [],
        }
    if offline:
        if target_path.exists():
            _verify_locked_file(target_path, entry)
        raise SourceLockError(f"{source_id}: offline cache miss: {target_path}")
    revision_lock = entry.get("revision_lock")
    if not isinstance(revision_lock, list):
        raise SourceLockError(f"{source_id}: missing revision_lock")
    acquisition = entry.get("acquisition")
    if not isinstance(acquisition, Mapping):
        raise SourceLockError(f"{source_id}: invalid acquisition metadata")
    max_redirects = int(acquisition.get("max_redirects", MAX_REDIRECTS))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_handle = tempfile.NamedTemporaryFile(
        "wb",
        delete=False,
        dir=str(target_path.parent),
        prefix=f".{target_path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_handle.name)
    temp_handle.close()
    try:
        attempts = _materialize_wikisource_bundle(
            revision_records=revision_lock,
            target_path=temp_path,
            max_redirects=max_redirects,
            max_attempts=max_attempts,
            sleep=sleep,
        )
        _verify_locked_file(temp_path, entry)
        os.replace(temp_path, target_path)
        return {
            "source_id": source_id,
            "status": "downloaded",
            "local_path": str(target_path),
            "bytes": target_path.stat().st_size,
            "sha256": sha256_file(target_path),
            "attempts": attempts,
        }
    finally:
        temp_path.unlink(missing_ok=True)


def _contains_unpinned_latest(url: str) -> bool:
    return any(pattern.search(url) for pattern in _UNPINNED_URL_PATTERNS)


def validate_source_lock(manifest: Mapping[str, object]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != LOCK_SCHEMA_VERSION:
        errors.append("unsupported source lock schema_version")
    if manifest.get("stage") != 3:
        errors.append("source lock must declare stage 3")
    if manifest.get("status") != "stage_3_complete_sources_locked":
        errors.append("source lock status must declare completed stage 3")
    policy = manifest.get("edition_policy")
    if not isinstance(policy, Mapping):
        errors.append("missing edition_policy")
    else:
        if policy.get("translation_id") != "ohienko_1988":
            errors.append("edition_policy must lock ohienko_1988")
        if policy.get("edition_year") != 1988:
            errors.append("edition_policy must lock the 1988 edition")
        if policy.get("forbid_ubt_editions_after_year") != 1990:
            errors.append("edition_policy must forbid UBT editions after 1990")

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        return [*errors, "sources must be a list"]
    source_ids: list[str] = []
    roles: set[str] = set()
    for index, raw_entry in enumerate(sources):
        if not isinstance(raw_entry, Mapping):
            errors.append(f"sources[{index}] must be an object")
            continue
        source_id = raw_entry.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"sources[{index}] has invalid source_id")
            source_id = f"sources[{index}]"
        else:
            source_ids.append(source_id)
        missing = sorted(REQUIRED_ENTRY_FIELDS - set(raw_entry))
        if missing:
            errors.append(f"{source_id}: missing fields: {', '.join(missing)}")
        role_id = raw_entry.get("role_id")
        if isinstance(role_id, str):
            roles.add(role_id)
        else:
            errors.append(f"{source_id}: invalid role_id")
        for url_field in ("source_page_url", "download_url", "license_url"):
            url = raw_entry.get(url_field)
            if not isinstance(url, str) or urlparse(url).scheme.lower() != "https":
                errors.append(f"{source_id}: {url_field} must be HTTPS")
            elif url_field == "download_url" and _contains_unpinned_latest(url):
                errors.append(f"{source_id}: unpinned latest/branch URL is forbidden")
        expected_bytes = raw_entry.get("bytes")
        if not isinstance(expected_bytes, int) or expected_bytes <= 0:
            errors.append(f"{source_id}: bytes must be a positive integer")
        sha256 = raw_entry.get("sha256")
        if not isinstance(sha256, str) or not _SHA256_RE.fullmatch(sha256):
            errors.append(f"{source_id}: invalid SHA-256")
        if raw_entry.get("retrieved_on") != LOCKED_ON:
            errors.append(f"{source_id}: retrieved_on must equal {LOCKED_ON}")
        license_name = raw_entry.get("license")
        if not isinstance(license_name, str) or not license_name.strip():
            errors.append(f"{source_id}: missing license")
        dependencies = raw_entry.get("dependencies")
        if not isinstance(dependencies, list):
            errors.append(f"{source_id}: dependencies must be a list")
        pin = raw_entry.get("pin")
        if not isinstance(pin, Mapping) or not pin:
            errors.append(f"{source_id}: missing immutable/version pin")
        acquisition = raw_entry.get("acquisition")
        if not isinstance(acquisition, Mapping):
            errors.append(f"{source_id}: invalid acquisition")
        elif acquisition.get("max_redirects") != MAX_REDIRECTS:
            errors.append(f"{source_id}: max_redirects must be {MAX_REDIRECTS}")

        if role_id in {
            "ukrainian_print_reference",
            "ukrainian_machine_transcription",
            "ukrainian_dependent_scan_control",
        }:
            if raw_entry.get("edition_year") != 1988:
                errors.append(f"{source_id}: Ukrainian text source must be edition 1988")
            if raw_entry.get("translation_id") != "ohienko_1988":
                errors.append(f"{source_id}: late/mixed UBT source is forbidden")

    duplicates = sorted(
        source_id for source_id in set(source_ids) if source_ids.count(source_id) > 1
    )
    if duplicates:
        errors.append(f"duplicate source_id values: {', '.join(duplicates)}")
    actual_source_ids = set(source_ids)
    missing_source_ids = sorted(EXPECTED_SOURCE_IDS - actual_source_ids)
    unexpected_source_ids = sorted(actual_source_ids - EXPECTED_SOURCE_IDS)
    if missing_source_ids:
        errors.append(f"missing required source_id values: {', '.join(missing_source_ids)}")
    if unexpected_source_ids:
        errors.append(f"unexpected source_id values: {', '.join(unexpected_source_ids)}")
    missing_roles = sorted(REQUIRED_ROLES - roles)
    if missing_roles:
        errors.append(f"missing required roles: {', '.join(missing_roles)}")
    known_source_ids = set(source_ids)
    for raw_entry in sources:
        if not isinstance(raw_entry, Mapping):
            continue
        for dependency in raw_entry.get("dependencies", []):
            if not isinstance(dependency, Mapping):
                errors.append(f"{raw_entry.get('source_id')}: invalid dependency")
                continue
            dependency_id = dependency.get("source_id")
            if dependency_id not in known_source_ids:
                errors.append(
                    f"{raw_entry.get('source_id')}: unknown dependency {dependency_id}"
                )

    by_id = {
        str(entry.get("source_id")): entry
        for entry in sources
        if isinstance(entry, Mapping)
    }
    _validate_exact_pins(by_id, errors)

    manual_controls = manifest.get("manual_controls")
    if not isinstance(manual_controls, list) or not manual_controls:
        errors.append("manual_controls must list independent/manual-only controls")
    else:
        for control in manual_controls:
            if not isinstance(control, Mapping):
                errors.append("manual control must be an object")
                continue
            if control.get("machine_input") is not False:
                errors.append(f"{control.get('control_id')}: manual control misclassified")
            if "local_path" in control or "sha256" in control:
                errors.append(
                    f"{control.get('control_id')}: manual control must not masquerade as a locked file"
                )

    placeholders = manifest.get("resolved_placeholders")
    if not isinstance(placeholders, Mapping):
        errors.append("missing resolved_placeholders")
    else:
        if placeholders.get("commons_scan_sha256") != COMMONS_SHA256:
            errors.append("commons_scan_sha256 placeholder is not resolved exactly")
        revision_value = placeholders.get("wikisource_revision_lock")
        if (
            not isinstance(revision_value, str)
            or "1540 revisions" not in revision_value
            or WIKISOURCE_REVISION_LOCK_SHA256 not in revision_value
        ):
            errors.append("wikisource_revision_lock placeholder is not resolved")
    return errors


def _validate_exact_pins(
    by_id: Mapping[str, Mapping[str, object]], errors: list[str]
) -> None:
    exact_pin_expectations: dict[str, dict[str, object]] = {
        "commons_ohienko_1988_scan": {
            "type": "mediawiki_file_sha1",
            "value": COMMONS_SHA1,
        },
        "step_tahot_gen_deu": {"type": "git_commit", "value": STEPBIBLE_COMMIT},
        "step_tahot_jos_est": {"type": "git_commit", "value": STEPBIBLE_COMMIT},
        "step_tahot_job_sng": {"type": "git_commit", "value": STEPBIBLE_COMMIT},
        "step_tahot_isa_mal": {"type": "git_commit", "value": STEPBIBLE_COMMIT},
        "step_tagnt_mat_jhn": {"type": "git_commit", "value": STEPBIBLE_COMMIT},
        "step_tagnt_act_rev": {"type": "git_commit", "value": STEPBIBLE_COMMIT},
        "step_tvtms": {"type": "git_commit", "value": STEPBIBLE_COMMIT},
        "openscriptures_oshb_v2_2": {
            "type": "git_tag_commit",
            "tag": OSHB_TAG,
            "value": OSHB_COMMIT,
        },
        "unfoldingword_ugnt_v0_34": {
            "type": "git_tag_commit",
            "tag": UGNT_TAG,
            "value": UGNT_COMMIT,
        },
        "crosswire_kjv_3_1": {
            "type": "git_commit",
            "value": CROSSWIRE_KJV_COMMIT,
        },
        "internet_archive_ohienko_1988_scan": {
            "type": "internet_archive_file_sha1",
            "value": "baf96568afa4c964f692cbf6509f50d69fbf4289",
            "md5": "29ca8fc8bf1593a50511be9d526ed291",
        },
        "tanach_us_uxlc_2_5_27_6": {
            "type": "product_version_build_sha256",
            "version": "UXLC 2.5",
            "build": "27.6",
            "text_date": "2026-04-01",
        },
    }
    for source_id, expected in exact_pin_expectations.items():
        entry = by_id.get(source_id)
        if entry is None:
            errors.append(f"missing required exact source {source_id}")
            continue
        if entry.get("pin") != expected:
            errors.append(f"{source_id}: exact revision/commit/tag pin changed")

    wikisource = by_id.get("wikisource_ohienko_1988_revisions")
    if wikisource is None:
        errors.append("missing Wikisource revision source")
        return
    revision_lock = wikisource.get("revision_lock")
    if not isinstance(revision_lock, list) or len(revision_lock) != 1540:
        errors.append("Wikisource revision lock must contain 1540 revisions")
        return
    try:
        if revision_lock[0]["revision_id"] != WIKISOURCE_EXPECTED_ROOT_REVISION:
            errors.append("Wikisource root revision changed")
        if revision_lock[1]["revision_id"] != WIKISOURCE_EXPECTED_INDEX_REVISION:
            errors.append("Wikisource index revision changed")
        if revision_lock[2]["revision_id"] != WIKISOURCE_EXPECTED_PAGE_ONE_REVISION:
            errors.append("Wikisource page 1 revision changed")
        if revision_lock[-1]["revision_id"] != WIKISOURCE_EXPECTED_LAST_PAGE_REVISION:
            errors.append("Wikisource page 1538 revision changed")
        expected_titles = _expected_wikisource_titles()
        if [record["title"] for record in revision_lock] != expected_titles:
            errors.append("Wikisource revision title set/order changed")
        for record in revision_lock:
            if not _SHA1_RE.fullmatch(str(record.get("sha1", ""))):
                errors.append("Wikisource revision has invalid SHA-1")
                break
        pin = wikisource.get("pin")
        lock_sha256 = _revision_lock_sha256(revision_lock)
        if not isinstance(pin, Mapping) or pin.get("revision_lock_sha256") != lock_sha256:
            errors.append("Wikisource revision-lock digest changed")
        if lock_sha256 != WIKISOURCE_REVISION_LOCK_SHA256:
            errors.append("Wikisource revision-lock digest is not the approved stage-3 lock")
        if wikisource.get("bytes") != WIKISOURCE_BUNDLE_BYTES:
            errors.append("Wikisource bundle size changed")
        if wikisource.get("sha256") != WIKISOURCE_BUNDLE_SHA256:
            errors.append("Wikisource bundle SHA-256 changed")
    except (KeyError, TypeError, ValueError):
        errors.append("Wikisource revision lock has invalid structure")


def load_source_lock(path: Path = SOURCE_LOCK_PATH) -> dict[str, object]:
    if not path.exists():
        raise SourceLockError(f"missing source lock: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceLockError(f"source lock root must be an object: {path}")
    return value


def _tool_versions() -> dict[str, object]:
    curl_command = "curl.exe" if os.name == "nt" else "curl"
    try:
        curl_version = subprocess.run(
            [curl_command, "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        ).stdout.splitlines()[0]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        curl_version = "unavailable"
    return {
        "python": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "openssl": ssl.OPENSSL_VERSION,
        "curl": curl_version,
        "platform": platform.platform(),
        "fetcher": "scripts.bible_module.ukrainian_stage_3_sources schema 1",
        "user_agent": USER_AGENT,
    }


def _write_or_append_fetch_log(
    *,
    log_path: Path,
    manifest_path: Path,
    run: Mapping[str, object],
) -> None:
    if log_path.exists():
        existing = json.loads(log_path.read_text(encoding="utf-8"))
    else:
        existing = {
            "schema_version": FETCH_LOG_SCHEMA_VERSION,
            "stage": 3,
            "source_lock": _manifest_local_path(manifest_path, log_path),
            "tool_versions": _tool_versions(),
            "network_policy": {
                "https_only": True,
                "max_attempts": MAX_ATTEMPTS,
                "retry_backoff_seconds": [2, 4, 8],
                "retryable_http_statuses": sorted(RETRYABLE_HTTP_STATUSES),
                "max_redirects": MAX_REDIRECTS,
                "https_downgrade_redirects_rejected": True,
                "atomic_replace_after_size_and_sha256": True,
            },
            "known_limitations": [
                "gpg is not installed; no new dependency was added because the approved stage-3 inputs are pinned by exact revision plus SHA-256 and the rejected eBible candidates are not inputs.",
                "Tanach.us exposes UXLC 2.5 build 27.6 at a mutable product URL; exact version metadata, byte size and SHA-256 are locked, so any upstream replacement fails closed.",
                "curl/Schannel verifies TLS on this Windows host because the bundled Python/OpenSSL trust path rejected Wikimedia's valid 2026 chain; peer-certificate dates and ssl_verify_result are recorded, but Schannel does not expose the negotiated cipher through curl write-out.",
            ],
            "runs": [],
        }
    runs = existing.get("runs")
    if not isinstance(runs, list):
        raise SourceLockError(f"invalid existing fetch log: {log_path}")
    runs.append(dict(run))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_bytes(_json_bytes(existing))


def fetch_locked_sources(
    *,
    manifest_path: Path = SOURCE_LOCK_PATH,
    log_path: Path = FETCH_LOG_PATH,
    cache_dir_override: Path | None = None,
    offline: bool = False,
    force: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    manifest = load_source_lock(manifest_path)
    validation_errors = validate_source_lock(manifest)
    if validation_errors:
        raise SourceLockError("invalid source lock:\n- " + "\n- ".join(validation_errors))
    sources = manifest["sources"]
    assert isinstance(sources, list)
    run_started = _utc_now_iso()
    run: dict[str, object] = {
        "started_at_utc": run_started,
        "finished_at_utc": None,
        "mode": "offline" if offline else ("force" if force else "normal"),
        "cache_dir_override": str(cache_dir_override) if cache_dir_override else None,
        "status": "running",
        "sources": [],
        "errors": [],
    }
    source_results = run["sources"]
    errors = run["errors"]
    assert isinstance(source_results, list)
    assert isinstance(errors, list)
    try:
        for entry in sources:
            assert isinstance(entry, Mapping)
            target_path = _resolve_local_path(
                entry,
                manifest_path=manifest_path,
                cache_dir_override=cache_dir_override,
            )
            acquisition = entry["acquisition"]
            assert isinstance(acquisition, Mapping)
            try:
                if acquisition.get("kind") == "https_file":
                    result = _fetch_https_file(
                        entry,
                        target_path=target_path,
                        force=force,
                        offline=offline,
                        max_attempts=max_attempts,
                        sleep=sleep,
                    )
                elif acquisition.get("kind") == "mediawiki_revision_bundle":
                    result = _fetch_wikisource_bundle(
                        entry,
                        target_path=target_path,
                        force=force,
                        offline=offline,
                        max_attempts=max_attempts,
                        sleep=sleep,
                    )
                else:
                    raise SourceLockError(
                        f"{entry['source_id']}: unsupported acquisition kind"
                    )
                source_results.append(result)
            except SourceLockError as error:
                errors.append({"source_id": entry["source_id"], "error": str(error)})
                raise
        run["status"] = "pass"
        return run
    except SourceLockError:
        run["status"] = "fail"
        raise
    finally:
        run["finished_at_utc"] = _utc_now_iso()
        _write_or_append_fetch_log(
            log_path=log_path,
            manifest_path=manifest_path,
            run=run,
        )


def _common_entry(
    *,
    source_id: str,
    dataset_id: str,
    title: str,
    role_id: str,
    role: str,
    independence: str,
    source_page_url: str,
    download_url: str,
    version: str,
    pin: Mapping[str, object],
    filename: str,
    bytes_count: int,
    sha256: str,
    license_name: str,
    license_url: str,
    dependencies: Sequence[Mapping[str, object]],
    notes: str,
    translation_source: bool = False,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "source_id": source_id,
        "dataset_id": dataset_id,
        "title": title,
        "role_id": role_id,
        "role": role,
        "independence": independence,
        "source_page_url": source_page_url,
        "download_url": download_url,
        "version": version,
        "pin": dict(pin),
        "retrieved_on": LOCKED_ON,
        "bytes": bytes_count,
        "sha256": sha256,
        "license": license_name,
        "license_url": license_url,
        "local_path": _manifest_local_path(SOURCE_CACHE_DIR / filename, SOURCE_LOCK_PATH),
        "dependencies": [dict(dependency) for dependency in dependencies],
        "acquisition": {
            "kind": "https_file",
            "max_attempts": MAX_ATTEMPTS,
            "max_redirects": MAX_REDIRECTS,
            "retryable_http_statuses": sorted(RETRYABLE_HTTP_STATUSES),
            "verify_before_replace": ["bytes", "sha256"],
        },
        "notes": notes,
    }
    if translation_source:
        entry["translation_id"] = "ohienko_1988"
        entry["edition_year"] = 1988
    return entry


def _approved_static_sources() -> list[dict[str, object]]:
    step_license_url = (
        "https://github.com/STEPBible/STEPBible-Data/blob/"
        f"{STEPBIBLE_COMMIT}/README.md#stepbible-data-repository--cc-by-40"
    )
    step_base = (
        "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/"
        f"{STEPBIBLE_COMMIT}/"
    )
    step_page_base = (
        "https://github.com/STEPBible/STEPBible-Data/blob/"
        f"{STEPBIBLE_COMMIT}/"
    )
    step_entries = [
        (
            "step_tahot_gen_deu",
            "TAHOT Gen-Deu",
            "primary_ot_strong_morphology",
            "Основная Hebrew OT цепочка токенов, морфологии и extended Strong (Genesis–Deuteronomy).",
            "Translators%20Amalgamated%20OT%2BNT/TAHOT%20Gen-Deu%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
            "step_tahot_gen_deu.txt",
            18_190_455,
            "e9b8546ee48fe0bfc57c3b70f5f40e98d96580e803526d19026224e31753368b",
        ),
        (
            "step_tahot_jos_est",
            "TAHOT Jos-Est",
            "primary_ot_strong_morphology",
            "Основная Hebrew OT цепочка токенов, морфологии и extended Strong (Joshua–Esther).",
            "Translators%20Amalgamated%20OT%2BNT/TAHOT%20Jos-Est%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
            "step_tahot_jos_est.txt",
            24_500_317,
            "195fee1dc3653bab33701f170734eb894ed647c10cd08cc61749375fe8b73775",
        ),
        (
            "step_tahot_job_sng",
            "TAHOT Job-Sng",
            "primary_ot_strong_morphology",
            "Основная Hebrew OT цепочка токенов, морфологии и extended Strong (Job–Song).",
            "Translators%20Amalgamated%20OT%2BNT/TAHOT%20Job-Sng%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
            "step_tahot_job_sng.txt",
            9_540_133,
            "84e118a97e5725e3847cdfdd593873513021c790c63cc91a0d41fca2b5db2ed5",
        ),
        (
            "step_tahot_isa_mal",
            "TAHOT Isa-Mal",
            "primary_ot_strong_morphology",
            "Основная Hebrew OT цепочка токенов, морфологии и extended Strong (Isaiah–Malachi).",
            "Translators%20Amalgamated%20OT%2BNT/TAHOT%20Isa-Mal%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
            "step_tahot_isa_mal.txt",
            17_977_518,
            "f3ded203d2a74d6368932c97ae550d1d0754b271af491dc0dedf36fe3ba0bcc5",
        ),
        (
            "step_tagnt_mat_jhn",
            "TAGNT Mat-Jhn",
            "primary_nt_strong_morphology",
            "Основная Greek NT цепочка токенов, морфологии и extended Strong (Matthew–John).",
            "Translators%20Amalgamated%20OT%2BNT/TAGNT%20Mat-Jhn%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt",
            "step_tagnt_mat_jhn.txt",
            14_189_032,
            "ab8eaaeb68e17a1dcfa34e1e9350358f22f03bc2a97244d848750ad81044bc8e",
        ),
        (
            "step_tagnt_act_rev",
            "TAGNT Act-Rev",
            "primary_nt_strong_morphology",
            "Основная Greek NT цепочка токенов, морфологии и extended Strong (Acts–Revelation).",
            "Translators%20Amalgamated%20OT%2BNT/TAGNT%20Act-Rev%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt",
            "step_tagnt_act_rev.txt",
            15_939_932,
            "524e32375361e6d3fa2f7ef00b87605fdc4317a762f395651a05fdc31ad031b7",
        ),
        (
            "step_tvtms",
            "TVTMS",
            "versification_traditions_control",
            "Контроль традиций версификации; не доказывает карту Огиенко без постиховой проверки.",
            "Versification/TVTMS%20-%20Translators%20Versification%20Traditions%20with%20Methodology%20for%20Standardisation%20for%20Eng%2BHeb%2BLat%2BGrk%2BOthers%20-%20STEPBible.org%20CC%20BY.txt",
            "step_tvtms.txt",
            5_790_928,
            "8851a8b5a2575b2be9cc6a1bb57284c91c610154a7a259397fbfaffe37db796a",
        ),
    ]
    result: list[dict[str, object]] = []
    for (
        source_id,
        title,
        role_id,
        role,
        encoded_path,
        filename,
        bytes_count,
        sha256,
    ) in step_entries:
        result.append(
            _common_entry(
                source_id=source_id,
                dataset_id=(
                    "stepbible_tahot_tagnt"
                    if role_id in {"primary_ot_strong_morphology", "primary_nt_strong_morphology"}
                    else "stepbible_tvtms"
                ),
                title=f"STEPBible {title}",
                role_id=role_id,
                role=role,
                independence=(
                    "primary_chain_dependent_on_wlc_openscriptures"
                    if role_id == "primary_ot_strong_morphology"
                    else "primary_chain"
                ),
                source_page_url=step_page_base + encoded_path,
                download_url=step_base + encoded_path,
                version=f"STEPBible-Data commit {STEPBIBLE_COMMIT}",
                pin={"type": "git_commit", "value": STEPBIBLE_COMMIT},
                filename=filename,
                bytes_count=bytes_count,
                sha256=sha256,
                license_name="Creative Commons Attribution 4.0 International (CC BY 4.0)",
                license_url=step_license_url,
                dependencies=(
                    [
                        {
                            "source_id": "openscriptures_oshb_v2_2",
                            "relation": "shared_WLC_OpenScriptures_lineage_not_independent",
                        }
                    ]
                    if role_id == "primary_ot_strong_morphology"
                    else []
                ),
                notes="Машинный вход; номера нельзя механически переносить на украинские слова.",
            )
        )
    return result


def _build_lock(
    *,
    revision_records: Sequence[Mapping[str, object]],
    wikisource_bundle_path: Path,
) -> dict[str, object]:
    revision_digest = _revision_lock_sha256(revision_records)
    commons_license_url = (
        "https://commons.wikimedia.org/wiki/"
        "File:Ivan_Ohienko_Bible.djvu#Licensing"
    )
    sources: list[dict[str, object]] = [
        _common_entry(
            source_id="commons_ohienko_1988_scan",
            dataset_id="ohienko_1988_print_scan",
            title="Wikimedia Commons DjVu: Ivan Ohienko Bible, jubilee edition 1988",
            role_id="ukrainian_print_reference",
            role="Основной печатный эталон точного юбилейного издания 1988 года.",
            independence="primary_print_reference",
            source_page_url="https://commons.wikimedia.org/wiki/File:Ivan_Ohienko_Bible.djvu",
            download_url="https://upload.wikimedia.org/wikipedia/commons/f/f9/Ivan_Ohienko_Bible.djvu",
            version="MediaWiki file timestamp 2014-07-10T17:11:34Z; 1538 pages",
            pin={"type": "mediawiki_file_sha1", "value": COMMONS_SHA1},
            filename="commons_ohienko_1988.djvu",
            bytes_count=COMMONS_BYTES,
            sha256=COMMONS_SHA256,
            license_name="Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
            license_url=commons_license_url,
            dependencies=[],
            notes="Точный Commons-бинарник; не добавляется в Git.",
            translation_source=True,
        ),
        {
            **_common_entry(
                source_id="wikisource_ohienko_1988_revisions",
                dataset_id="ohienko_1988_wikisource_transcription",
                title="Ukrainian Wikisource pinned ProofreadPage transcription bundle",
                role_id="ukrainian_machine_transcription",
                role="Базовая машинная транскрипция, проверяемая по Commons DjVu.",
                independence="derived_from_commons_scan_not_independent",
                source_page_url="https://uk.wikisource.org/wiki/Індекс:Ivan_Ohienko_Bible.djvu",
                download_url=(
                    "https://uk.wikisource.org/w/api.php?action=query&prop=revisions&"
                    "revids={locked_revision_ids}&rvprop=ids%7Ctimestamp%7Csha1%7Csize%7Ccontent&"
                    "rvslots=main&format=json&formatversion=2"
                ),
                version=(
                    f"1540 pinned revisions: root, index, and ProofreadPage pages 1-{WIKISOURCE_PAGE_COUNT}"
                ),
                pin={
                    "type": "mediawiki_revision_set",
                    "revision_count": len(revision_records),
                    "revision_lock_sha256": revision_digest,
                },
                filename="wikisource_ohienko_1988_revisions.json",
                bytes_count=wikisource_bundle_path.stat().st_size,
                sha256=sha256_file(wikisource_bundle_path),
                license_name="Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
                license_url=commons_license_url,
                dependencies=[
                    {
                        "source_id": "commons_ohienko_1988_scan",
                        "relation": "transcription_derived_from_same_scan_not_independent",
                    }
                ],
                notes="Полный список revision ID встроен в source_lock.json; содержимое находится только в локальном кэше.",
                translation_source=True,
            ),
            "revision_lock": [dict(record) for record in revision_records],
            "acquisition": {
                "kind": "mediawiki_revision_bundle",
                "api_url": WIKISOURCE_API_URL,
                "batch_size": 50,
                "max_attempts": MAX_ATTEMPTS,
                "max_redirects": MAX_REDIRECTS,
                "retryable_http_statuses": sorted(RETRYABLE_HTTP_STATUSES),
                "verify_before_replace": ["revision_metadata", "bytes", "sha256"],
            },
        },
        _common_entry(
            source_id="internet_archive_ohienko_1988_scan",
            dataset_id="ohienko_1988_dependent_scan_control",
            title="Internet Archive Ohienko Bible DjVu derivative",
            role_id="ukrainian_dependent_scan_control",
            role="Зависимый контроль скана/OCR; не независимая редакция.",
            independence="dependent_derivative_not_independent",
            source_page_url="https://archive.org/details/BibleOhienko",
            download_url="https://archive.org/download/BibleOhienko/Ohienko_Bible.djvu",
            version="Internet Archive item BibleOhienko; file mtime 1404934060; public date 2014-07-08",
            pin={
                "type": "internet_archive_file_sha1",
                "value": "baf96568afa4c964f692cbf6509f50d69fbf4289",
                "md5": "29ca8fc8bf1593a50511be9d526ed291",
            },
            filename="internet_archive_ohienko_1988.djvu",
            bytes_count=41_818_741,
            sha256=INTERNET_ARCHIVE_SHA256,
            license_name="Creative Commons Attribution-ShareAlike 4.0 International (inherited exact-edition permission)",
            license_url=commons_license_url,
            dependencies=[
                {
                    "source_id": "commons_ohienko_1988_scan",
                    "relation": "same_edition_derivative_control_not_independent",
                }
            ],
            notes="Не считать зеркалом независимой редакции; бинарник отличается от Commons.",
            translation_source=True,
        ),
    ]
    sources.extend(_approved_static_sources())
    sources.extend(
        [
            _common_entry(
                source_id="openscriptures_oshb_v2_2",
                dataset_id="openscriptures_oshb",
                title="Open Scriptures Hebrew Bible morphhb v.2.2",
                role_id="dependent_ot_strong_crosscheck",
                role="Зависимая OT-проверка augmented Strong, lemma и morphology.",
                independence="dependent_on_same_WLC_OpenScriptures_lineage_as_TAHOT",
                source_page_url=f"https://github.com/openscriptures/morphhb/tree/{OSHB_COMMIT}",
                download_url=f"https://codeload.github.com/openscriptures/morphhb/zip/{OSHB_COMMIT}",
                version=f"tag {OSHB_TAG}; commit {OSHB_COMMIT}",
                pin={"type": "git_tag_commit", "tag": OSHB_TAG, "value": OSHB_COMMIT},
                filename="openscriptures_morphhb_v2_2.zip",
                bytes_count=20_869_248,
                sha256="dac2d0325c59f6cd22839f2ef6345544a85b50c9d657788672e7638fa11abecb",
                license_name="WLC text Public Domain; lemma and morphology CC BY 4.0",
                license_url=f"https://github.com/openscriptures/morphhb/blob/{OSHB_COMMIT}/LICENSE.md",
                dependencies=[
                    {
                        "source_id": "step_tahot_gen_deu",
                        "relation": "shared_WLC_OpenScriptures_lineage_not_independent",
                    },
                    {
                        "source_id": "step_tahot_jos_est",
                        "relation": "shared_WLC_OpenScriptures_lineage_not_independent",
                    },
                    {
                        "source_id": "step_tahot_job_sng",
                        "relation": "shared_WLC_OpenScriptures_lineage_not_independent",
                    },
                    {
                        "source_id": "step_tahot_isa_mal",
                        "relation": "shared_WLC_OpenScriptures_lineage_not_independent",
                    },
                ],
                notes="Не засчитывается как независимая OT Strong-цепочка.",
            ),
            _common_entry(
                source_id="tanach_us_uxlc_2_5_27_6",
                dataset_id="tanach_us_uxlc",
                title="Tanach.us Unicode/XML Leningrad Codex",
                role_id="independent_ot_surface_control",
                role="Независимый OT-контроль поверхности, границ и соответствия рукописным снимкам; не Strong-слой.",
                independence="independently_corrected_surface_control_from_WLC_fork",
                source_page_url="https://www.tanach.us/Pages/About.html",
                download_url="https://www.tanach.us/Books/Tanach.xml.zip",
                version="UXLC 2.5; build 27.6; text date 1 Apr 2026; build time 31 Mar 2026 12:00",
                pin={
                    "type": "product_version_build_sha256",
                    "version": "UXLC 2.5",
                    "build": "27.6",
                    "text_date": "2026-04-01",
                },
                filename="tanach_us_uxlc_2_5_27_6.zip",
                bytes_count=2_365_002,
                sha256="1bc6e006f43d3b18f2f718cefa3aa4774cac2c54092c28d173dd61996c43a050",
                license_name="Biblical Hebrew text may be viewed or copied without restriction",
                license_url="https://www.tanach.us/License.html",
                dependencies=[],
                notes="Mutable upstream URL is pinned fail-closed by embedded version/build plus exact size and SHA-256.",
            ),
            _common_entry(
                source_id="unfoldingword_ugnt_v0_34",
                dataset_id="unfoldingword_ugnt",
                title="unfoldingWord Greek New Testament v0.34",
                role_id="independent_nt_strong_control",
                role="Независимый NT-контроль lemma, morphology и Strong.",
                independence="independent_from_STEPBible_TAGNT",
                source_page_url=f"https://git.door43.org/unfoldingWord/el-x-koine_ugnt/src/commit/{UGNT_COMMIT}",
                download_url=f"https://git.door43.org/unfoldingWord/el-x-koine_ugnt/archive/{UGNT_COMMIT}.zip",
                version=f"tag {UGNT_TAG}; commit {UGNT_COMMIT}; manifest version 0.34",
                pin={"type": "git_tag_commit", "tag": UGNT_TAG, "value": UGNT_COMMIT},
                filename="unfoldingword_ugnt_v0_34.zip",
                bytes_count=1_252_605,
                sha256="07318be27d0027146a62363c20ffedd0db695d7680f4b32c8ae8bd3020a29d00",
                license_name="Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
                license_url=f"https://git.door43.org/unfoldingWord/el-x-koine_ugnt/src/commit/{UGNT_COMMIT}/LICENSE.md",
                dependencies=[],
                notes="Основан на Bunning; не заменяет TAGNT или украинский текст.",
            ),
            _common_entry(
                source_id="crosswire_kjv_3_1",
                dataset_id="crosswire_kjv",
                title="CrossWire KJV 3.1 OSIS with word-level Strong markup",
                role_id="classic_strong_audit_control",
                role="Дополнительный независимый classic-Strong multiset-аудит; не источник украинского текста.",
                independence="independent_classic_strong_audit_control",
                source_page_url="https://crosswire.org/sword/modules/ModInfo.jsp?modName=KJV",
                download_url=(
                    "https://gitlab.com/crosswire-bible-society/kjv/-/raw/"
                    f"{CROSSWIRE_KJV_COMMIT}/kjvfull.xml"
                ),
                version=f"{CROSSWIRE_KJV_VERSION}; commit {CROSSWIRE_KJV_COMMIT}",
                pin={"type": "git_commit", "value": CROSSWIRE_KJV_COMMIT},
                filename="crosswire_kjvfull.xml",
                bytes_count=28_630_975,
                sha256="d5114fc1ab17b1e141ff5c035ef3a4354437fd24b4b8ee34f4c925915c0374ef",
                license_name="GNU General Public License / CrossWire general public use grant",
                license_url="https://crosswire.org/sword/modules/ModInfo.jsp?modName=KJV",
                dependencies=[],
                notes="Только аудит classic Strong; текст KJV не переносится в украинский модуль.",
            ),
        ]
    )
    sources.sort(key=lambda entry: str(entry["source_id"]))
    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "stage": 3,
        "status": "stage_3_complete_sources_locked",
        "locked_on": LOCKED_ON,
        "edition_policy": {
            "translation_id": "ohienko_1988",
            "translation": "Біблія або Книги Святого Письма Старого і Нового Заповіту, переклад Івана Огієнка",
            "edition": "ювілейне видання 1988 року",
            "edition_year": 1988,
            "canon": "protestant_66",
            "language": "uk",
            "forbid_ubt_editions_after_year": 1990,
            "forbid_text_substitution_from_later_editions": True,
        },
        "cache_policy": {
            "directory": _manifest_local_path(SOURCE_CACHE_DIR, SOURCE_LOCK_PATH),
            "git_ignored": True,
            "full_text_and_binaries_must_not_be_committed": True,
            "verify_size_and_sha256_before_use": True,
            "mismatch_behavior": "fail_closed_before_atomic_replace_or_parse",
        },
        "resolved_placeholders": {
            "commons_scan_sha256": COMMONS_SHA256,
            "wikisource_revision_lock": (
                f"1540 revisions: Біблія={WIKISOURCE_EXPECTED_ROOT_REVISION}; "
                f"Індекс={WIKISOURCE_EXPECTED_INDEX_REVISION}; "
                f"Сторінка 1-{WIKISOURCE_PAGE_COUNT} full list; "
                f"revision-list SHA-256 {revision_digest}"
            ),
        },
        "sources": sources,
        "manual_controls": [
            {
                "control_id": "physical_or_library_ohienko_1988",
                "title": "Физический или библиотечный экземпляр точного юбилейного издания 1988 года",
                "role": "Независимое разрешение спорных чтений после сравнения машинных источников.",
                "machine_input": False,
                "independence": "independent_copy_of_same_exact_print_edition",
                "restriction": "Не допускает подмену текстом поздних редакций УБТ.",
            },
            {
                "control_id": "leningrad_codex_color_images",
                "title": "Цветные снимки Ленинградского кодекса, доступные через ссылки Tanach.us",
                "role": "Ручной контроль спорных чтений поверхности UXLC; не загружаемый Strong-вход.",
                "machine_input": False,
                "source_page_url": "https://www.tanach.us/Pages/LC%20images.html",
                "independence": "manuscript_image_control",
            },
        ],
        "dependency_policy": {
            "internet_archive_not_independent_from_commons": True,
            "wikisource_not_independent_from_commons": True,
            "oshb_not_independent_from_tahot_wlc_lineage": True,
            "mirrors_of_same_file_count_once": True,
        },
    }


def write_source_files_csv(
    manifest: Mapping[str, object], path: Path = SOURCE_FILES_CSV_PATH
) -> None:
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise SourceLockError("source lock has no sources")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(
            output,
            lineterminator="\n",
            fieldnames=[
                "source_id",
                "dataset_id",
                "role_id",
                "version",
                "pin",
                "retrieved_on",
                "bytes",
                "sha256",
                "source_page_url",
                "download_url",
                "license",
                "license_url",
                "dependencies",
                "local_path",
            ],
        )
        writer.writeheader()
        for entry in sources:
            assert isinstance(entry, Mapping)
            writer.writerow(
                {
                    "source_id": entry["source_id"],
                    "dataset_id": entry["dataset_id"],
                    "role_id": entry["role_id"],
                    "version": entry["version"],
                    "pin": json.dumps(entry["pin"], ensure_ascii=False, sort_keys=True),
                    "retrieved_on": entry["retrieved_on"],
                    "bytes": entry["bytes"],
                    "sha256": entry["sha256"],
                    "source_page_url": entry["source_page_url"],
                    "download_url": entry["download_url"],
                    "license": entry["license"],
                    "license_url": entry["license_url"],
                    "dependencies": json.dumps(
                        entry["dependencies"], ensure_ascii=False, sort_keys=True
                    ),
                    "local_path": entry["local_path"],
                }
            )


def bootstrap_source_lock(
    *,
    manifest_path: Path = SOURCE_LOCK_PATH,
    source_files_csv_path: Path = SOURCE_FILES_CSV_PATH,
) -> dict[str, object]:
    revision_records, _ = discover_wikisource_revision_lock()
    bundle_path = SOURCE_CACHE_DIR / "wikisource_ohienko_1988_revisions.json"
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    _materialize_wikisource_bundle(
        revision_records=revision_records,
        target_path=bundle_path,
        max_redirects=MAX_REDIRECTS,
        max_attempts=MAX_ATTEMPTS,
        sleep=time.sleep,
    )
    lock = _build_lock(
        revision_records=revision_records,
        wikisource_bundle_path=bundle_path,
    )
    errors = validate_source_lock(lock)
    if errors:
        raise SourceLockError("generated invalid source lock:\n- " + "\n- ".join(errors))
    for entry in lock["sources"]:
        assert isinstance(entry, Mapping)
        local_path = _resolve_local_path(
            entry,
            manifest_path=manifest_path,
            cache_dir_override=None,
        )
        _verify_locked_file(local_path, entry)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(_json_bytes(lock))
    write_source_files_csv(lock, source_files_csv_path)
    return lock


def verify_locked_cache(
    *, manifest_path: Path = SOURCE_LOCK_PATH, cache_dir_override: Path | None = None
) -> list[str]:
    manifest = load_source_lock(manifest_path)
    errors = validate_source_lock(manifest)
    if errors:
        return errors
    sources = manifest["sources"]
    assert isinstance(sources, list)
    for entry in sources:
        assert isinstance(entry, Mapping)
        try:
            local_path = _resolve_local_path(
                entry,
                manifest_path=manifest_path,
                cache_dir_override=cache_dir_override,
            )
            _verify_locked_file(local_path, entry)
        except SourceLockError as error:
            errors.append(str(error))
    return errors


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lock and fail-closed fetch approved Ukrainian Bible stage-3 sources."
    )
    parser.add_argument("--manifest", type=Path, default=SOURCE_LOCK_PATH)
    parser.add_argument("--fetch-log", type=Path, default=FETCH_LOG_PATH)
    parser.add_argument("--source-files-csv", type=Path, default=SOURCE_FILES_CSV_PATH)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--bootstrap-lock", action="store_true")
    action.add_argument("--fetch", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--verify-clean-cache", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--offline", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        if args.bootstrap_lock:
            lock = bootstrap_source_lock(
                manifest_path=args.manifest,
                source_files_csv_path=args.source_files_csv,
            )
            print(f"Locked {len(lock['sources'])} Ukrainian stage-3 source files")
            return 0
        if args.check:
            errors = verify_locked_cache(manifest_path=args.manifest)
            if errors:
                for error in errors:
                    print(error)
                return 1
            print(f"Verified Ukrainian stage-3 source lock and cache: {args.manifest}")
            return 0
        if args.verify_clean_cache:
            with tempfile.TemporaryDirectory(
                prefix="revelation_ukrainian_stage3_"
            ) as temp_dir:
                cache_dir = Path(temp_dir)
                fetch_locked_sources(
                    manifest_path=args.manifest,
                    log_path=args.fetch_log,
                    cache_dir_override=cache_dir,
                    force=False,
                    offline=False,
                )
                fetch_locked_sources(
                    manifest_path=args.manifest,
                    log_path=args.fetch_log,
                    cache_dir_override=cache_dir,
                    force=False,
                    offline=True,
                )
            print("Verified clean fetch and offline cache hit for all locked sources")
            return 0
        fetch_locked_sources(
            manifest_path=args.manifest,
            log_path=args.fetch_log,
            force=args.force,
            offline=args.offline,
        )
        print("Fetched and verified all locked Ukrainian stage-3 sources")
        return 0
    except SourceLockError as error:
        print(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
