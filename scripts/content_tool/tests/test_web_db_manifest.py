from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.content_tool.web_db_manifest import (
    build_web_db_manifest_payload_from_paths,
    build_web_db_manifest_version_token,
    write_web_db_manifest,
)


class WebDbManifestTests(unittest.TestCase):
    def test_build_payload_reads_metadata_from_sqlite_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            common_db = root / "revelation.sqlite"
            localized_db = root / "revelation_ru.sqlite"
            self._create_db(
                common_db,
                schema_version=4,
                data_version=2,
                date_iso="2026-03-21T06:09:24Z",
            )
            self._create_db(
                localized_db,
                schema_version=6,
                data_version=3,
                date_iso="2026-03-28T08:30:00Z",
            )

            payload = build_web_db_manifest_payload_from_paths(
                [localized_db, common_db],
                generated_at="2026-03-28T09:00:00Z",
            )

            self.assertEqual(payload["version"], 1)
            self.assertEqual(payload["generatedAt"], "2026-03-28T09:00:00Z")
            self.assertEqual(
                list(payload["databases"].keys()),
                ["revelation.sqlite", "revelation_ru.sqlite"],
            )

            common_entry = payload["databases"]["revelation.sqlite"]
            localized_entry = payload["databases"]["revelation_ru.sqlite"]
            self.assertEqual(common_entry["schemaVersion"], 4)
            self.assertEqual(common_entry["dataVersion"], 2)
            self.assertEqual(common_entry["date"], "2026-03-21T06:09:24Z")
            self.assertEqual(
                common_entry["versionToken"],
                build_web_db_manifest_version_token(
                    schema_version=4,
                    data_version=2,
                    date_iso="2026-03-21T06:09:24Z",
                    file_size_bytes=common_db.stat().st_size,
                ),
            )
            self.assertEqual(localized_entry["schemaVersion"], 6)
            self.assertEqual(localized_entry["dataVersion"], 3)
            self.assertEqual(localized_entry["date"], "2026-03-28T08:30:00Z")

    def test_write_manifest_writes_expected_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_path = root / "revelation_en.sqlite"
            manifest_path = root / "manifest.json"
            self._create_db(
                db_path,
                schema_version=6,
                data_version=2,
                date_iso="2026-03-21T06:09:01Z",
            )

            write_web_db_manifest(
                manifest_path,
                db_paths=[db_path],
                generated_at="2026-03-28T10:00:00Z",
            )

            saved = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["generatedAt"], "2026-03-28T10:00:00Z")
            self.assertIn("revelation_en.sqlite", saved["databases"])

    def test_build_payload_requires_complete_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            broken_db = root / "revelation_es.sqlite"
            connection = sqlite3.connect(str(broken_db))
            try:
                connection.execute("PRAGMA user_version = 6")
                connection.execute(
                    """
                    CREATE TABLE db_metadata (
                        key TEXT NOT NULL PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    "INSERT INTO db_metadata(key, value) VALUES('schema_version', '6')"
                )
                connection.execute(
                    "INSERT INTO db_metadata(key, value) VALUES('date', '2026-03-21T06:09:08Z')"
                )
                connection.commit()
            finally:
                connection.close()

            with self.assertRaisesRegex(
                ValueError,
                r"revelation_es\.sqlite.*db_metadata\.data_version",
            ):
                build_web_db_manifest_payload_from_paths([broken_db])

    def _create_db(
        self,
        db_path: Path,
        *,
        schema_version: int,
        data_version: int,
        date_iso: str,
    ) -> None:
        connection = sqlite3.connect(str(db_path))
        try:
            connection.execute(f"PRAGMA user_version = {schema_version}")
            connection.execute(
                """
                CREATE TABLE db_metadata (
                    key TEXT NOT NULL PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            connection.executemany(
                "INSERT INTO db_metadata(key, value) VALUES(?, ?)",
                [
                    ("schema_version", str(schema_version)),
                    ("data_version", str(data_version)),
                    ("date", date_iso),
                ],
            )
            connection.commit()
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
