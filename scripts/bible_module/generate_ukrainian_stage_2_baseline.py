from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.bible_module.ukrainian_stage_2_contract import (
    DEFAULT_BASELINE_PATH,
    DEFAULT_IDENTIFIERS_PATH,
    DEFAULT_REFERENCE_DB_PATH,
    DEFAULT_VERSE_MAP_PATH,
    STAGE_2_GENERATED_ON,
    build_baseline_manifest,
    render_baseline_manifest,
    render_final_identifiers_csv,
    write_stage_2_evidence,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate or verify the Ukrainian Bible stage-2 KJV baseline. "
            "The command reads only repository-local KJV and verse-map files."
        )
    )
    parser.add_argument(
        "--reference-db",
        type=Path,
        default=DEFAULT_REFERENCE_DB_PATH,
    )
    parser.add_argument(
        "--verse-map",
        type=Path,
        default=DEFAULT_VERSE_MAP_PATH,
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE_PATH,
    )
    parser.add_argument(
        "--identifiers",
        type=Path,
        default=DEFAULT_IDENTIFIERS_PATH,
    )
    parser.add_argument("--generated-on", default=STAGE_2_GENERATED_ON)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify checked-in evidence without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    manifest = build_baseline_manifest(
        reference_db_path=args.reference_db,
        verse_map_path=args.verse_map,
        generated_on=args.generated_on,
    )
    if args.check:
        expected_manifest = render_baseline_manifest(manifest)
        expected_identifiers = render_final_identifiers_csv()
        errors: list[str] = []
        if not args.baseline.is_file():
            errors.append(f"Missing baseline manifest: {args.baseline}")
        elif args.baseline.read_text(encoding="utf-8") != expected_manifest:
            errors.append(f"Baseline manifest is stale: {args.baseline}")
        if not args.identifiers.is_file():
            errors.append(f"Missing identifiers table: {args.identifiers}")
        elif (
            args.identifiers.read_text(encoding="utf-8")
            != expected_identifiers
        ):
            errors.append(f"Identifiers table is stale: {args.identifiers}")
        if errors:
            for error in errors:
                print(error)
            return 1
    else:
        write_stage_2_evidence(
            reference_db_path=args.reference_db,
            verse_map_path=args.verse_map,
            baseline_path=args.baseline,
            identifiers_path=args.identifiers,
            generated_on=args.generated_on,
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "check_only": bool(args.check),
                "reference_sha256": manifest["reference_database"]["sha256"],
                "schema_fingerprint_sha256": manifest["reference_database"][
                    "schema"
                ]["fingerprint_sha256"],
                "verse_key_sequence_sha256": manifest["target_grid"][
                    "verse_key_sequence_sha256"
                ],
                "verse_keys": manifest["target_grid"]["verse_keys_count"],
                "baseline": str(args.baseline),
                "identifiers": str(args.identifiers),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
