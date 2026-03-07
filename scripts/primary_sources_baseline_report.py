#!/usr/bin/env python3
"""Generate a baseline report for the hardcoded primary sources repository."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


METHOD_NAMES = (
    "getFullPrimarySources",
    "getSignificantPrimarySources",
    "getFragmentsPrimarySources",
)


def default_repository_path() -> Path:
    return Path(__file__).resolve().parents[1] / "lib" / "repositories" / "primary_sources_repository.dart"


def extract_method_source_ids(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for method_name in METHOD_NAMES:
        match = re.search(
            rf"List<PrimarySource>\s+{re.escape(method_name)}\(BuildContext context\)\s*\{{(.*?)return sources;",
            text,
            re.DOTALL,
        )
        if not match:
            result[method_name] = []
            continue
        block = match.group(1)
        result[method_name] = re.findall(r'id:\s*"([^"]+)"', block)
    return result


def extract_source_blocks(text: str) -> list[dict[str, object]]:
    pattern = re.compile(
        r"PrimarySource\(\s*id:\s*\"([^\"]+)\"(.*?)permissionsReceived:\s*(true|false),\s*\),",
        re.DOTALL,
    )
    sources: list[dict[str, object]] = []
    for match in pattern.finditer(text):
        source_id = match.group(1)
        block = match.group(2)
        permissions_received = match.group(3) == "true"
        sources.append(
            {
                "id": source_id,
                "permissions_received": permissions_received,
                "pages": len(re.findall(r"model\.Page\(", block)),
                "words": len(re.findall(r"PageWord\(", block)),
                "rectangles": len(re.findall(r"PageRect\(", block)),
                "verses": len(re.findall(r"Verse\(", block)),
            }
        )
    return sources


def build_report(repository_path: Path) -> dict[str, object]:
    text = repository_path.read_text(encoding="utf-8")
    method_source_ids = extract_method_source_ids(text)
    source_blocks = extract_source_blocks(text)

    source_ids_by_group = {
        "full": method_source_ids["getFullPrimarySources"],
        "significant": method_source_ids["getSignificantPrimarySources"],
        "fragment": method_source_ids["getFragmentsPrimarySources"],
    }

    zero_page_sources = [row["id"] for row in source_blocks if row["pages"] == 0]
    overlay_sources = [
        row["id"]
        for row in source_blocks
        if row["words"] > 0 or row["verses"] > 0
    ]

    report = {
        "repository_path": str(repository_path),
        "totals": {
            "sources": len(source_blocks),
            "pages": sum(int(row["pages"]) for row in source_blocks),
            "words": sum(int(row["words"]) for row in source_blocks),
            "rectangles": sum(int(row["rectangles"]) for row in source_blocks),
            "verses": sum(int(row["verses"]) for row in source_blocks),
            "permissions_true": sum(1 for row in source_blocks if row["permissions_received"]),
            "permissions_false": sum(1 for row in source_blocks if not row["permissions_received"]),
            "full_sources": len(source_ids_by_group["full"]),
            "significant_sources": len(source_ids_by_group["significant"]),
            "fragment_sources": len(source_ids_by_group["fragment"]),
        },
        "groups": source_ids_by_group,
        "zero_page_sources": zero_page_sources,
        "overlay_sources": overlay_sources,
        "sources": source_blocks,
    }
    return report


def print_summary(report: dict[str, object]) -> None:
    totals = report["totals"]
    groups = report["groups"]
    print("Primary Sources Baseline")
    print(f"Repository: {report['repository_path']}")
    print(f"Sources: {totals['sources']}")
    print(
        f"Groups: full={totals['full_sources']}, "
        f"significant={totals['significant_sources']}, "
        f"fragment={totals['fragment_sources']}"
    )
    print(
        f"Pages={totals['pages']}, Words={totals['words']}, "
        f"Rectangles={totals['rectangles']}, Verses={totals['verses']}"
    )
    print(
        f"Permissions: true={totals['permissions_true']}, "
        f"false={totals['permissions_false']}"
    )
    print(f"Full IDs: {', '.join(groups['full'])}")
    print(f"Significant IDs: {', '.join(groups['significant'])}")
    print(f"Fragment IDs: {', '.join(groups['fragment'])}")
    print(f"Zero-page sources: {', '.join(report['zero_page_sources']) or '-'}")
    print(f"Overlay sources: {', '.join(report['overlay_sources']) or '-'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a baseline report for primary_sources_repository.dart."
    )
    parser.add_argument(
        "--repository",
        type=Path,
        default=default_repository_path(),
        help="Path to primary_sources_repository.dart",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report as JSON instead of a text summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.repository.resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
