from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.bible_module import fetch_sources
from scripts.bible_module.sources import (
    CROSSWIRE_LXX_LICENSE_NAME,
    SOURCE_SPECS,
    STEPBIBLE_DATA_COMMIT,
    STEPBIBLE_LICENSE_NAME,
)


class BibleSourceManifestTests(unittest.TestCase):
    def test_source_specs_lock_expected_phase_one_sources(self) -> None:
        self.assertEqual(
            [source.source_id for source in SOURCE_SPECS],
            [
                "step_tagnt_mat_jhn",
                "step_tagnt_act_rev",
                "step_tbesg",
                "step_tflsj_0_5624",
                "step_tflsj_extra",
                "step_tegmc",
                "crosswire_lxx",
            ],
        )
        for source in SOURCE_SPECS:
            with self.subTest(source_id=source.source_id):
                self.assertTrue(source.source_url.startswith("https://"))
                self.assertTrue(source.source_page_url.startswith("https://"))
                self.assertTrue(source.license_url.startswith("https://"))

        step_sources = [
            source for source in SOURCE_SPECS if source.source_id.startswith("step_")
        ]
        self.assertTrue(step_sources)
        for source in step_sources:
            with self.subTest(source_id=source.source_id):
                self.assertIn(STEPBIBLE_DATA_COMMIT, source.source_url)
                self.assertEqual(source.source_commit, STEPBIBLE_DATA_COMMIT)
                self.assertEqual(source.license_name, STEPBIBLE_LICENSE_NAME)

        crosswire = next(
            source for source in SOURCE_SPECS if source.source_id == "crosswire_lxx"
        )
        self.assertEqual(crosswire.license_name, CROSSWIRE_LXX_LICENSE_NAME)
        self.assertIn("LXX.zip", crosswire.source_url)

    def test_build_source_manifest_records_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cache_dir = root / "cache"
            manifest_path = root / "source_manifest.lock.json"
            payload_by_url = {
                source.source_url: f"{source.source_id}\n".encode("utf-8")
                for source in SOURCE_SPECS
            }

            def fake_download(url: str, target_path: Path) -> None:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(payload_by_url[url])

            with mock.patch.object(fetch_sources, "_download_to_path", fake_download):
                manifest = fetch_sources.build_source_manifest(
                    cache_dir=cache_dir,
                    manifest_path=manifest_path,
                    generated_at_utc="2026-05-23T00:00:00Z",
                )

            entries = manifest["sources"]
            self.assertIsInstance(entries, list)
            self.assertEqual(len(entries), len(SOURCE_SPECS))
            for entry in entries:
                self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(entry["bytes"], 0)
                self.assertEqual(entry["downloaded_at_utc"], "2026-05-23T00:00:00Z")

    def test_verify_manifest_reports_missing_cache_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "source_manifest.lock.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "sources": [
                            {
                                "source_id": "missing",
                                "local_path": str(root / "missing.txt"),
                                "sha256": "0" * 64,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            errors = fetch_sources.verify_source_manifest(manifest_path=manifest_path)

            self.assertEqual(len(errors), 1)
            self.assertIn("cached source is missing", errors[0])


if __name__ == "__main__":
    unittest.main()

