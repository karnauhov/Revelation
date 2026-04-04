#!/usr/bin/env python3
"""Generate a startup loader manifest for Flutter web builds.

The manifest is consumed by `web/flutter_bootstrap.js` to render a
more realistic splash progress bar based on startup resources.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

try:
    import brotli  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    brotli = None


FIXED_REQUIRED_PATHS = (
    "main.dart.js",
    "version.json",
)

OPTIONAL_STARTUP_GROUPS = {
    "asset_manifest": (
        "assets/AssetManifest.bin",
        "assets/AssetManifest.bin.json",
        "assets/AssetManifest.json",
    ),
    "renderer_js": (
        "canvaskit/canvaskit.js",
        "canvaskit/chromium/canvaskit.js",
        "canvaskit/skwasm.js",
        "canvaskit/skwasm_heavy.js",
    ),
    "renderer_wasm": (
        "canvaskit/canvaskit.wasm",
        "canvaskit/chromium/canvaskit.wasm",
        "canvaskit/skwasm.wasm",
        "canvaskit/skwasm_heavy.wasm",
    ),
}

BROWSER_DEFAULT_STARTUP_CANDIDATES = ("favicon.ico",)

STARTUP_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".ico"}
COMPRESSIBLE_EXTENSIONS = {
    ".css",
    ".frag",
    ".html",
    ".ico",
    ".js",
    ".json",
    ".mjs",
    ".otf",
    ".svg",
    ".ttf",
    ".txt",
    ".wasm",
    ".woff",
    ".xml",
}

INDEX_RESOURCE_PATTERN = re.compile(
    r"""(?:src|href)\s*=\s*["']([^"']+)["']""",
    re.IGNORECASE,
)
INDEX_CSS_URL_PATTERN = re.compile(
    r"""url\(\s*(['"]?)([^)'"]+)\1\s*\)""",
    re.IGNORECASE,
)

FIREBASE_REMOTE_SIZE_FALLBACKS = {
    "app": 30_000,
    "auth": 50_000,
    "firestore": 125_000,
    "storage": 170_000,
}
GOOGLE_GSI_CLIENT_FALLBACK_BYTES = 100_000
GOOGLE_HOSTED_FONT_BUDGET_BYTES = 96_000


@dataclass(frozen=True)
class SizeEstimate:
    estimated_transfer_size_bytes: int
    raw_size_bytes: int
    gzip_size_bytes: int | None = None
    brotli_size_bytes: int | None = None


@dataclass(frozen=True)
class Resource:
    path: str
    size_bytes: int
    raw_size_bytes: int
    gzip_size_bytes: int | None = None
    brotli_size_bytes: int | None = None

    def to_json(self) -> dict[str, int | str]:
        payload: dict[str, int | str] = {
            "path": self.path,
            "size_bytes": self.size_bytes,
            "raw_size_bytes": self.raw_size_bytes,
        }
        if self.gzip_size_bytes is not None:
            payload["gzip_size_bytes"] = self.gzip_size_bytes
        if self.brotli_size_bytes is not None:
            payload["brotli_size_bytes"] = self.brotli_size_bytes
        return payload


@dataclass(frozen=True)
class ExternalResource:
    url: str
    size_bytes: int

    def to_json(self) -> dict[str, int | str]:
        return {
            "url": self.url,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class ExternalMatchGroup:
    id: str
    url_prefixes: tuple[str, ...]
    extensions: tuple[str, ...]
    max_matches: int
    max_candidate_bytes: int

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "url_prefixes": list(self.url_prefixes),
            "extensions": list(self.extensions),
            "max_matches": self.max_matches,
            "max_candidate_bytes": self.max_candidate_bytes,
        }


def normalize_posix_path(relative_path: str | Path) -> str:
    return str(relative_path).replace("\\", "/").lstrip("/")


def normalize_local_reference(raw_reference: str) -> str | None:
    reference = raw_reference.strip()
    if not reference or reference.startswith("#"):
        return None
    if reference.startswith("//"):
        return None

    parsed = urlparse(reference)
    if parsed.scheme or parsed.netloc:
        return None

    normalized_path = normalize_posix_path(unquote(parsed.path))
    if normalized_path in {"", "."}:
        return None

    return normalized_path


def is_compressible_resource(file_path: Path) -> bool:
    return file_path.suffix.lower() in COMPRESSIBLE_EXTENSIONS


def estimate_file_size(file_path: Path) -> SizeEstimate | None:
    raw_bytes = file_path.read_bytes()
    raw_size_bytes = len(raw_bytes)
    if raw_size_bytes <= 0:
        return None

    gzip_size_bytes: int | None = None
    brotli_size_bytes: int | None = None
    size_candidates = [raw_size_bytes]

    if is_compressible_resource(file_path):
        gzip_size_bytes = len(gzip.compress(raw_bytes, compresslevel=9))
        size_candidates.append(gzip_size_bytes)
        if brotli is not None:
            brotli_size_bytes = len(brotli.compress(raw_bytes, quality=11))
            size_candidates.append(brotli_size_bytes)

    return SizeEstimate(
        estimated_transfer_size_bytes=min(size_candidates),
        raw_size_bytes=raw_size_bytes,
        gzip_size_bytes=gzip_size_bytes,
        brotli_size_bytes=brotli_size_bytes,
    )


def resolve_resource(build_dir: Path, relative_path: str) -> Resource | None:
    normalized_path = normalize_posix_path(relative_path)
    candidate_path = build_dir / Path(normalized_path)
    if not candidate_path.is_file():
        return None

    size_estimate = estimate_file_size(candidate_path)
    if size_estimate is None:
        return None

    return Resource(
        path=normalized_path,
        size_bytes=size_estimate.estimated_transfer_size_bytes,
        raw_size_bytes=size_estimate.raw_size_bytes,
        gzip_size_bytes=size_estimate.gzip_size_bytes,
        brotli_size_bytes=size_estimate.brotli_size_bytes,
    )


def collect_resources(build_dir: Path, candidates: tuple[str, ...]) -> list[Resource]:
    resources: list[Resource] = []
    for relative_path in candidates:
        resource = resolve_resource(build_dir, relative_path)
        if resource is not None:
            resources.append(resource)
    return resources


def collect_local_resources_from_index(build_dir: Path) -> list[Resource]:
    index_path = build_dir / "index.html"
    if not index_path.is_file():
        return []

    index_text = index_path.read_text(encoding="utf-8")
    referenced_paths: dict[str, None] = {}

    for match in INDEX_RESOURCE_PATTERN.finditer(index_text):
        normalized_reference = normalize_local_reference(match.group(1))
        if normalized_reference is not None:
            referenced_paths.setdefault(normalized_reference, None)

    for match in INDEX_CSS_URL_PATTERN.finditer(index_text):
        normalized_reference = normalize_local_reference(match.group(2))
        if normalized_reference is not None:
            referenced_paths.setdefault(normalized_reference, None)

    return collect_resources(build_dir, tuple(referenced_paths.keys()))


def collect_manifest_linked_icons(
    build_dir: Path,
    index_resources: list[Resource],
) -> list[Resource]:
    resources: list[Resource] = []
    manifest_paths = {
        resource.path
        for resource in index_resources
        if Path(resource.path).name.lower() == "manifest.json"
    }

    for manifest_path in sorted(manifest_paths):
        manifest_file = build_dir / Path(manifest_path)
        if not manifest_file.is_file():
            continue

        payload = json.loads(manifest_file.read_text(encoding="utf-8"))
        icons = payload.get("icons", [])
        if not isinstance(icons, list):
            continue

        for icon in icons:
            icon_src = icon.get("src")
            if not isinstance(icon_src, str):
                continue

            normalized_reference = normalize_local_reference(icon_src)
            if normalized_reference is None:
                continue

            resource = resolve_resource(build_dir, normalized_reference)
            if resource is not None:
                resources.append(resource)

    return resources


def collect_font_manifest_resources(build_dir: Path) -> list[Resource]:
    font_manifest_resource = resolve_resource(build_dir, "assets/FontManifest.json")
    if font_manifest_resource is None:
        return []

    resources = [font_manifest_resource]
    font_manifest_path = build_dir / "assets" / "FontManifest.json"
    payload = json.loads(font_manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        return resources

    for family in payload:
        fonts = family.get("fonts", [])
        if not isinstance(fonts, list):
            continue

        for font in fonts:
            asset_path = font.get("asset")
            if not isinstance(asset_path, str):
                continue

            normalized_asset_path = normalize_local_reference(f"assets/{asset_path}")
            if normalized_asset_path is None:
                continue

            resource = resolve_resource(build_dir, normalized_asset_path)
            if resource is not None:
                resources.append(resource)

    return resources


def collect_top_level_startup_images(build_dir: Path) -> list[Resource]:
    image_directory = build_dir / "assets" / "assets" / "images"
    if not image_directory.is_dir():
        return []

    resources: list[Resource] = []
    for candidate in sorted(image_directory.iterdir()):
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() not in STARTUP_IMAGE_EXTENSIONS:
            continue
        lower_name = candidate.name.lower()
        if (
            candidate.suffix.lower() != ".svg"
            and not lower_name.startswith("logo")
            and "splash" not in lower_name
        ):
            continue

        resource = resolve_resource(
            build_dir,
            normalize_posix_path(candidate.relative_to(build_dir)),
        )
        if resource is not None:
            resources.append(resource)

    return resources


def ensure_required_core_files(required_resources: list[Resource]) -> None:
    required_paths = {resource.path for resource in required_resources}
    for must_exist in ("main.dart.js", "version.json"):
        if must_exist not in required_paths:
            raise RuntimeError(
                f"Could not build loader manifest: missing required startup file '{must_exist}'."
            )


def add_unique_resources(
    resource_index: dict[str, Resource],
    resources: list[Resource],
) -> None:
    for resource in resources:
        resource_index.setdefault(resource.path, resource)


def load_package_roots(project_root: Path) -> dict[str, Path]:
    package_config_path = project_root / ".dart_tool" / "package_config.json"
    if not package_config_path.is_file():
        return {}

    payload = json.loads(package_config_path.read_text(encoding="utf-8"))
    package_roots: dict[str, Path] = {}
    for package in payload.get("packages", []):
        name = package.get("name")
        root_uri = package.get("rootUri")
        if not isinstance(name, str) or not isinstance(root_uri, str):
            continue

        package_root = resolve_root_uri(project_root, root_uri)
        if package_root is not None:
            package_roots[name] = package_root

    return package_roots


def resolve_root_uri(project_root: Path, root_uri: str) -> Path | None:
    parsed = urlparse(root_uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path.lstrip("/"))).resolve()

    if parsed.scheme:
        return None

    return (project_root / unquote(root_uri)).resolve()


def read_package_text(
    package_roots: dict[str, Path],
    package_name: str,
    relative_path: str,
) -> str | None:
    package_root = package_roots.get(package_name)
    if package_root is None:
        return None

    file_path = package_root / relative_path
    if not file_path.is_file():
        return None

    return file_path.read_text(encoding="utf-8")


def detect_firebase_sdk_version(package_roots: dict[str, Path]) -> str | None:
    sdk_version_source = read_package_text(
        package_roots,
        "firebase_core_web",
        "lib/src/firebase_sdk_version.dart",
    )
    if sdk_version_source is None:
        return None

    match = re.search(
        r"supportedFirebaseJsSdkVersion\s*=\s*'([^']+)'",
        sdk_version_source,
    )
    return match.group(1) if match else None


def detect_external_resources(
    package_roots: dict[str, Path],
) -> tuple[list[ExternalResource], list[ExternalMatchGroup]]:
    external_resources: list[ExternalResource] = []
    external_match_groups: list[ExternalMatchGroup] = []

    firebase_version = detect_firebase_sdk_version(package_roots)
    if firebase_version:
        firebase_services = ["app"]
        if "firebase_auth_web" in package_roots:
            firebase_services.append("auth")
        if "cloud_firestore_web" in package_roots:
            firebase_services.append("firestore")
        if "firebase_storage_web" in package_roots:
            firebase_services.append("storage")

        for service in firebase_services:
            url = (
                f"https://www.gstatic.com/firebasejs/{firebase_version}/"
                f"firebase-{service}.js"
            )
            size_bytes = probe_remote_resource_size(
                url,
                FIREBASE_REMOTE_SIZE_FALLBACKS.get(service, 80_000),
            )
            external_resources.append(
                ExternalResource(url=url, size_bytes=size_bytes)
            )

    if (
        "google_sign_in_web" in package_roots
        or "google_identity_services_web" in package_roots
    ):
        external_resources.append(
            ExternalResource(
                url="https://accounts.google.com/gsi/client",
                size_bytes=probe_remote_resource_size(
                    "https://accounts.google.com/gsi/client",
                    GOOGLE_GSI_CLIENT_FALLBACK_BYTES,
                ),
            )
        )

    if "google_fonts" in package_roots:
        external_match_groups.append(
            ExternalMatchGroup(
                id="google_hosted_font",
                url_prefixes=("https://fonts.gstatic.com/",),
                extensions=(".woff", ".woff2", ".ttf", ".otf"),
                max_matches=1,
                max_candidate_bytes=GOOGLE_HOSTED_FONT_BUDGET_BYTES,
            )
        )

    return external_resources, external_match_groups


def probe_remote_resource_size(url: str, fallback_size_bytes: int) -> int:
    request_headers = {"Accept-Encoding": "br, gzip"}

    head_request = Request(url, method="HEAD", headers=request_headers)
    try:
        with urlopen(head_request, timeout=5) as response:
            content_length = response.headers.get("Content-Length")
            if content_length:
                parsed = int(content_length)
                if parsed > 0:
                    return parsed
    except (HTTPError, URLError, TimeoutError, ValueError):
        pass

    range_request = Request(
        url,
        method="GET",
        headers={
            "Accept-Encoding": "br, gzip",
            "Range": "bytes=0-0",
        },
    )
    try:
        with urlopen(range_request, timeout=5) as response:
            content_range = response.headers.get("Content-Range", "")
            content_range_match = re.search(r"/(\d+)$", content_range)
            if content_range_match:
                parsed = int(content_range_match.group(1))
                if parsed > 0:
                    return parsed

            content_length = response.headers.get("Content-Length")
            if content_length:
                parsed = int(content_length)
                if parsed > 0:
                    return parsed
    except (HTTPError, URLError, TimeoutError, ValueError):
        pass

    return fallback_size_bytes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate build/web/loader_manifest.json for splash progress tracking."
    )
    parser.add_argument(
        "--web-build-dir",
        default="build/web",
        help="Path to flutter web build directory (default: build/web).",
    )
    parser.add_argument(
        "--output-file",
        default="loader_manifest.json",
        help="Manifest output file name/path (default: loader_manifest.json in web build dir).",
    )
    return parser.parse_args()


def build_payload(
    *,
    navigation_document: Resource | None,
    required_resources: list[Resource],
    optional_groups: list[dict[str, object]],
    external_resources: list[ExternalResource],
    external_match_groups: list[ExternalMatchGroup],
) -> dict[str, Any]:
    required_total_bytes = sum(resource.size_bytes for resource in required_resources)
    optional_max_total_bytes = sum(
        int(group["max_candidate_bytes"]) for group in optional_groups
    )
    external_total_bytes = sum(resource.size_bytes for resource in external_resources)
    external_pattern_budget_bytes = sum(
        group.max_matches * group.max_candidate_bytes
        for group in external_match_groups
    )
    navigation_document_bytes = navigation_document.size_bytes if navigation_document else 0

    return {
        "schema_version": 2,
        "generated_at_utc": (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        ),
        "estimated_startup_total_bytes": (
            navigation_document_bytes
            + required_total_bytes
            + optional_max_total_bytes
            + external_total_bytes
            + external_pattern_budget_bytes
        ),
        "navigation_document": (
            navigation_document.to_json() if navigation_document else None
        ),
        "required_resources": [resource.to_json() for resource in required_resources],
        "optional_groups": optional_groups,
        "external_resources": [resource.to_json() for resource in external_resources],
        "external_match_groups": [
            group.to_json() for group in external_match_groups
        ],
    }


def append_optional_group(
    optional_groups: list[dict[str, object]],
    group_id: str,
    resources: list[Resource],
) -> None:
    if not resources:
        return

    max_candidate_bytes = max(resource.size_bytes for resource in resources)
    optional_groups.append(
        {
            "id": group_id,
            "max_candidate_bytes": max_candidate_bytes,
            "candidates": [resource.to_json() for resource in resources],
        }
    )


def main() -> int:
    args = parse_args()
    web_build_dir = Path(args.web_build_dir).resolve()
    if not web_build_dir.is_dir():
        raise RuntimeError(f"Web build directory does not exist: {web_build_dir}")

    project_root = web_build_dir.parent.parent.resolve()
    package_roots = load_package_roots(project_root)

    navigation_document = resolve_resource(web_build_dir, "index.html")

    required_resource_index: dict[str, Resource] = {}
    add_unique_resources(
        required_resource_index,
        collect_resources(web_build_dir, FIXED_REQUIRED_PATHS),
    )

    index_resources = collect_local_resources_from_index(web_build_dir)
    add_unique_resources(required_resource_index, index_resources)
    add_unique_resources(
        required_resource_index,
        collect_resources(web_build_dir, BROWSER_DEFAULT_STARTUP_CANDIDATES),
    )
    add_unique_resources(
        required_resource_index,
        collect_font_manifest_resources(web_build_dir),
    )
    add_unique_resources(
        required_resource_index,
        collect_top_level_startup_images(web_build_dir),
    )

    required_resources = sorted(
        required_resource_index.values(),
        key=lambda resource: resource.path,
    )
    ensure_required_core_files(required_resources)

    optional_groups: list[dict[str, object]] = []
    append_optional_group(
        optional_groups,
        "pwa_icon",
        collect_manifest_linked_icons(web_build_dir, index_resources),
    )
    for group_id, candidates in OPTIONAL_STARTUP_GROUPS.items():
        group_resources = collect_resources(web_build_dir, candidates)
        append_optional_group(optional_groups, group_id, group_resources)

    external_resources, external_match_groups = detect_external_resources(package_roots)

    output_file = Path(args.output_file)
    output_path = (
        output_file if output_file.is_absolute() else (web_build_dir / output_file)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        manifest_relative_path = normalize_posix_path(output_path.relative_to(web_build_dir))
    except ValueError:
        manifest_relative_path = None

    if manifest_relative_path:
        required_resource_index.pop(manifest_relative_path, None)
        required_resources = sorted(
            required_resource_index.values(),
            key=lambda resource: resource.path,
        )

    payload = build_payload(
        navigation_document=navigation_document,
        required_resources=required_resources,
        optional_groups=optional_groups,
        external_resources=external_resources,
        external_match_groups=external_match_groups,
    )
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if manifest_relative_path:
        manifest_resource = resolve_resource(web_build_dir, manifest_relative_path)
        if manifest_resource is not None:
            required_resource_index[manifest_relative_path] = manifest_resource
            required_resources = sorted(
                required_resource_index.values(),
                key=lambda resource: resource.path,
            )
            payload = build_payload(
                navigation_document=navigation_document,
                required_resources=required_resources,
                optional_groups=optional_groups,
                external_resources=external_resources,
                external_match_groups=external_match_groups,
            )
            output_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    print(
        "web-loader-manifest: wrote "
        f"{output_path} (estimated_startup={payload['estimated_startup_total_bytes']} bytes)"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
