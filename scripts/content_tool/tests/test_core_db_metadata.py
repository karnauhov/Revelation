from __future__ import annotations

import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.content_tool.mixins.core_db import (
    DB_METADATA_DATA_VERSION_KEY,
    DB_METADATA_DATE_KEY,
    DB_METADATA_SCHEMA_VERSION_KEY,
    CoreDbMixin,
    LOCALIZED_DB_SCHEMA_VERSION,
)


class _CoreDbHarness(CoreDbMixin):
    def __init__(self) -> None:
        self.connection: sqlite3.Connection | None = None
        self.current_db_path: Path | None = None
        self.common_connection: sqlite3.Connection | None = None
        self.common_db_path: Path | None = None
        self.project_root = Path.cwd()

    def _format_db_date_for_ui(self, date_iso: object | None) -> str:
        return str(date_iso or "-")


class CoreDbMetadataTests(unittest.TestCase):
    def test_touch_updates_date_without_incrementing_data_version_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "revelation_ru.sqlite"
            self._create_db(
                db_path,
                schema_version=LOCALIZED_DB_SCHEMA_VERSION,
                data_version=7,
                date_iso="2026-03-21T00:00:00Z",
            )
            harness = _CoreDbHarness()

            updated = harness._touch_db_data_version(
                db_path,
                schema_version=LOCALIZED_DB_SCHEMA_VERSION,
            )

            self.assertIsNotNone(updated)
            assert updated is not None
            self.assertEqual(updated["data_version"], 7)
            self.assertNotEqual(updated["date_iso"], "2026-03-21T00:00:00Z")

    def test_publish_plan_uses_web_db_data_version_for_increment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_dir = root / "source"
            target_dir = root / "web" / "db"
            source_dir.mkdir(parents=True)
            target_dir.mkdir(parents=True)

            source_db = source_dir / "revelation_ru.sqlite"
            target_db = target_dir / "revelation_ru.sqlite"
            self._create_db(
                source_db,
                schema_version=LOCALIZED_DB_SCHEMA_VERSION,
                data_version=3,
                date_iso="2026-03-21T00:00:00Z",
            )
            shutil.copy2(source_db, target_db)

            harness = _CoreDbHarness()
            initial_plan = harness._collect_web_db_publish_plan(files=[source_db], target_dir=target_dir)
            self.assertEqual(len(initial_plan), 1)
            self.assertFalse(bool(initial_plan[0]["needs_copy"]))

            updated = harness._touch_db_data_version(
                source_db,
                schema_version=LOCALIZED_DB_SCHEMA_VERSION,
            )
            self.assertIsNotNone(updated)

            changed_plan = harness._collect_web_db_publish_plan(files=[source_db], target_dir=target_dir)
            self.assertEqual(len(changed_plan), 1)
            self.assertTrue(bool(changed_plan[0]["needs_copy"]))
            self.assertTrue(bool(changed_plan[0]["date_differs"]))
            self.assertEqual(changed_plan[0]["planned_data_version"], 4)

    def test_touch_can_set_explicit_publish_data_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "revelation.sqlite"
            self._create_db(
                db_path,
                schema_version=4,
                data_version=5,
                date_iso="2026-03-21T00:00:00Z",
            )
            harness = _CoreDbHarness()

            updated = harness._touch_db_data_version(
                db_path,
                schema_version=4,
                increment_data_version=True,
                next_data_version=12,
            )

            self.assertIsNotNone(updated)
            assert updated is not None
            self.assertEqual(updated["data_version"], 12)

    def test_compare_db_tables_ignores_db_metadata_only_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_db = root / "source.sqlite"
            target_db = root / "target.sqlite"
            self._create_db_with_articles(
                source_db,
                data_version=7,
                date_iso="2026-03-29T10:00:00Z",
                article_title="Same title",
            )
            self._create_db_with_articles(
                target_db,
                data_version=2,
                date_iso="2026-03-20T10:00:00Z",
                article_title="Same title",
            )

            harness = _CoreDbHarness()
            changed_tables = harness._compare_db_tables(source_db, target_db)

            self.assertEqual(changed_tables, [])

    def test_compare_db_tables_reports_changed_user_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_db = root / "source.sqlite"
            target_db = root / "target.sqlite"
            self._create_db_with_articles(
                source_db,
                data_version=3,
                date_iso="2026-03-29T10:00:00Z",
                article_title="New title",
            )
            self._create_db_with_articles(
                target_db,
                data_version=2,
                date_iso="2026-03-20T10:00:00Z",
                article_title="Old title",
            )

            harness = _CoreDbHarness()
            changed_tables = harness._compare_db_tables(source_db, target_db)

            self.assertEqual(changed_tables, ["articles"])

    def test_git_publish_settings_require_local_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            harness = _CoreDbHarness()
            harness.project_root = root

            self.assertIsNone(harness._git_publish_settings())

            env_dir = root / "env"
            env_dir.mkdir(parents=True)
            (env_dir / "content_tool_git_publish.env").write_text(
                "REVELATION_CONTENT_TOOL_GIT_PUBLISH_ENABLED=1\n"
                "REVELATION_CONTENT_TOOL_GIT_REMOTE=origin\n",
                encoding="utf-8",
            )

            settings = harness._git_publish_settings()
            self.assertIsNotNone(settings)
            assert settings is not None
            self.assertEqual(settings["remote_name"], "origin")

    def test_build_git_publish_commit_message_lists_db_files_and_tables(self) -> None:
        harness = _CoreDbHarness()

        subject, body = harness._build_git_publish_commit_message(
            successful_results=[
                {
                    "name": "revelation_ru.sqlite",
                    "changed_tables": ["articles", "topics"],
                },
                {
                    "name": "revelation.sqlite",
                    "changed_tables": [],
                },
            ]
        )

        self.assertEqual(subject, "Update published web databases [skip ci]")
        self.assertIn("revelation_ru.sqlite: articles, topics", body)
        self.assertIn("revelation.sqlite: metadata only", body)

    def test_build_publish_confirmation_text_includes_prepared_git_message(self) -> None:
        harness = _CoreDbHarness()

        confirmation_text = harness._build_publish_confirmation_text(
            source_dir=Path("work/db"),
            target_dir=Path("web/db"),
            plan=[
                {
                    "name": "revelation_ru.sqlite",
                    "source_snapshot": {
                        "data_version": 5,
                        "date_iso": "2026-03-29T10:00:00Z",
                        "size_bytes": 100,
                    },
                    "target_snapshot": {
                        "data_version": 4,
                        "date_iso": "2026-03-20T10:00:00Z",
                        "size_bytes": 90,
                    },
                    "size_differs": True,
                    "date_differs": True,
                    "needs_copy": True,
                    "planned_data_version": 5,
                    "changed_tables": ["articles", "topics"],
                }
            ],
            test_enabled_db_files=[],
            prepared_git_commit_message=(
                "Update published web databases [skip ci]\n\n"
                "revelation_ru.sqlite: articles, topics"
            ),
        )

        self.assertIn("Подготовленное сообщение коммита Git:", confirmation_text)
        self.assertIn("Update published web databases [skip ci]", confirmation_text)
        self.assertIn("revelation_ru.sqlite: articles, topics", confirmation_text)

    def test_publish_files_to_git_branch_pushes_only_selected_publish_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            remote_dir = root / "remote.git"
            repo_dir = root / "repo"

            self._run_git(["init", "--bare", str(remote_dir)], cwd=root)
            self._run_git(["init", "-b", "main", str(repo_dir)], cwd=root)
            self._run_git(["config", "user.name", "Content Tool Test"], cwd=repo_dir)
            self._run_git(["config", "user.email", "content-tool-test@example.com"], cwd=repo_dir)
            self._run_git(["remote", "add", "origin", str(remote_dir)], cwd=repo_dir)

            db_path = repo_dir / "web" / "db" / "revelation_ru.sqlite"
            manifest_path = repo_dir / "web" / "db" / "manifest.json"
            readme_path = repo_dir / "README.md"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_path.write_text("db-v1\n", encoding="utf-8")
            manifest_path.write_text('{"version":1}\n', encoding="utf-8")
            readme_path.write_text("readme-v1\n", encoding="utf-8")
            self._run_git(["add", "."], cwd=repo_dir)
            self._run_git(["commit", "-m", "Initial"], cwd=repo_dir)
            self._run_git(["push", "-u", "origin", "main"], cwd=repo_dir)

            db_path.write_text("db-v2\n", encoding="utf-8")
            manifest_path.write_text('{"version":2}\n', encoding="utf-8")
            readme_path.write_text("readme-dirty-local-change\n", encoding="utf-8")

            harness = _CoreDbHarness()
            harness.project_root = repo_dir

            result = harness._publish_files_to_git_branch(
                branch_name="main",
                remote_name="origin",
                paths_to_publish=[db_path, manifest_path],
                successful_results=[
                    {
                        "name": "revelation_ru.sqlite",
                        "changed_tables": ["articles"],
                    }
                ],
                commit_subject="Prepared preview subject [skip ci]",
                commit_body="revelation_ru.sqlite: articles",
            )

            self.assertEqual(result["branch_name"], "main")
            self.assertEqual(result["remote_name"], "origin")
            self.assertEqual(result["subject"], "Prepared preview subject [skip ci]")

            remote_subject = self._run_git(
                ["log", "-1", "--pretty=%s", "refs/heads/main"],
                git_dir=remote_dir,
            )
            remote_body = self._run_git(
                ["log", "-1", "--pretty=%b", "refs/heads/main"],
                git_dir=remote_dir,
            )
            remote_db = self._run_git(
                ["show", "refs/heads/main:web/db/revelation_ru.sqlite"],
                git_dir=remote_dir,
            )
            remote_manifest = self._run_git(
                ["show", "refs/heads/main:web/db/manifest.json"],
                git_dir=remote_dir,
            )
            remote_readme = self._run_git(
                ["show", "refs/heads/main:README.md"],
                git_dir=remote_dir,
            )

            self.assertEqual(remote_subject, "Prepared preview subject [skip ci]")
            self.assertIn("revelation_ru.sqlite: articles", remote_body)
            self.assertEqual(remote_db, "db-v2")
            self.assertEqual(remote_manifest, '{"version":2}')
            self.assertEqual(remote_readme, "readme-v1")
            self.assertEqual(readme_path.read_text(encoding="utf-8"), "readme-dirty-local-change\n")

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
                    (DB_METADATA_SCHEMA_VERSION_KEY, str(schema_version)),
                    (DB_METADATA_DATA_VERSION_KEY, str(data_version)),
                    (DB_METADATA_DATE_KEY, date_iso),
                ],
            )
            connection.commit()
        finally:
            connection.close()

    def _create_db_with_articles(
        self,
        db_path: Path,
        *,
        data_version: int,
        date_iso: str,
        article_title: str,
    ) -> None:
        connection = sqlite3.connect(str(db_path))
        try:
            connection.execute(f"PRAGMA user_version = {LOCALIZED_DB_SCHEMA_VERSION}")
            connection.execute(
                """
                CREATE TABLE db_metadata (
                    key TEXT NOT NULL PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE articles (
                    route TEXT NOT NULL PRIMARY KEY,
                    name TEXT NOT NULL
                )
                """
            )
            connection.executemany(
                "INSERT INTO db_metadata(key, value) VALUES(?, ?)",
                [
                    (DB_METADATA_SCHEMA_VERSION_KEY, str(LOCALIZED_DB_SCHEMA_VERSION)),
                    (DB_METADATA_DATA_VERSION_KEY, str(data_version)),
                    (DB_METADATA_DATE_KEY, date_iso),
                ],
            )
            connection.execute(
                "INSERT INTO articles(route, name) VALUES(?, ?)",
                ("/sample", article_title),
            )
            connection.commit()
        finally:
            connection.close()

    def _run_git(
        self,
        args: list[str],
        *,
        cwd: Path | None = None,
        git_dir: Path | None = None,
    ) -> str:
        command = ["git"]
        if git_dir is not None:
            command.extend(["--git-dir", str(git_dir)])
        command.extend(args)
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd is not None else None,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            error_text = (completed.stderr or completed.stdout or "").strip()
            raise AssertionError(f"git command failed: {' '.join(command)}\n{error_text}")
        return completed.stdout.strip()


if __name__ == "__main__":
    unittest.main()
