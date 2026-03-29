from __future__ import annotations

import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import scripts.content_tool.mixins.core_db as core_db_module
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


class _FakeUrlopenResponse:
    def __enter__(self) -> "_FakeUrlopenResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        return b"{}"


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
                    "target_snapshot": {
                        "data_version": 4,
                    },
                    "planned_data_version": 5,
                    "changed_tables": ["articles", "topics"],
                },
                {
                    "name": "revelation.sqlite",
                    "target_snapshot": {
                        "data_version": 8,
                    },
                    "planned_data_version": 8,
                    "changed_tables": [],
                },
            ]
        )

        self.assertEqual(subject, "Update published web databases [skip ci]")
        self.assertIn("revelation_ru.sqlite: data_version 4 -> 5; tables: articles, topics", body)
        self.assertIn("revelation.sqlite: data_version 8 -> 8; tables: metadata only", body)

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
                "revelation_ru.sqlite: data_version 4 -> 5; tables: articles, topics"
            ),
        )

        self.assertIn("Подготовленное сообщение коммита Git:", confirmation_text)
        self.assertIn("Update published web databases [skip ci]", confirmation_text)
        self.assertIn("revelation_ru.sqlite: data_version 4 -> 5; tables: articles, topics", confirmation_text)

    def test_confirmation_message_highlight_specs_marks_save_and_publish_actions(self) -> None:
        harness = _CoreDbHarness()

        save_text = harness._build_publish_confirmation_text(
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
            prepared_git_commit_message=None,
        )
        publish_text = harness._build_release_publish_confirmation_text(
            target_dir=Path("web/db"),
            local_entries={
                "revelation.sqlite": {
                    "schema_version": 4,
                    "data_version": 5,
                    "date_iso": "2026-03-29T12:00:00Z",
                    "size_bytes": 1000,
                }
            },
            web_target_state={
                "configured": True,
                "error": None,
                "manifest_url": "https://example.com/web/manifest.json",
                "plan": [
                    {
                        "name": "revelation.sqlite",
                        "remote_snapshot": {
                            "schema_version": 4,
                            "data_version": 4,
                            "date_iso": "2026-03-20T12:00:00Z",
                            "size_bytes": 900,
                        },
                        "needs_publish": True,
                        "reasons": ["data_version", "дата", "размер"],
                        "remote_only": False,
                    }
                ],
            },
            supabase_target_state={
                "configured": True,
                "error": None,
                "manifest_url": "https://example.com/supabase/manifest.json",
                "plan": [],
            },
        )

        save_highlights = {
            save_text.splitlines()[line_number - 1]: tag_name
            for line_number, tag_name in harness._confirmation_message_highlight_specs(save_text)
        }
        publish_highlights = {
            publish_text.splitlines()[line_number - 1]: tag_name
            for line_number, tag_name in harness._confirmation_message_highlight_specs(publish_text)
        }

        self.assertEqual(save_highlights["Найдено БД: 1. Будут переписаны: 1."], "accent_primary")
        self.assertEqual(save_highlights["revelation_ru.sqlite [ПЕРЕПИСАТЬ]"], "accent_primary")
        self.assertEqual(save_highlights["  план data_version: 4 -> 5"], "accent_secondary")
        self.assertEqual(save_highlights["  таблицы: articles, topics"], "accent_secondary")
        self.assertEqual(publish_highlights["Удаленный web: будет публикация"], "accent_primary")
        self.assertEqual(publish_highlights["  публикация в web: ДА (data_version, дата, размер)"], "accent_primary")

    def test_collect_manifest_comparison_plan_detects_publish_differences(self) -> None:
        harness = _CoreDbHarness()

        plan = harness._collect_manifest_comparison_plan(
            local_entries={
                "revelation.sqlite": {
                    "schema_version": 4,
                    "data_version": 5,
                    "date_iso": "2026-03-29T12:00:00Z",
                    "size_bytes": 1000,
                },
                "revelation_ru.sqlite": {
                    "schema_version": 6,
                    "data_version": 9,
                    "date_iso": "2026-03-29T12:00:00Z",
                    "size_bytes": 2000,
                },
            },
            remote_entries={
                "revelation.sqlite": {
                    "schema_version": 4,
                    "data_version": 4,
                    "date_iso": "2026-03-20T12:00:00Z",
                    "size_bytes": 900,
                },
                "revelation_extra.sqlite": {
                    "schema_version": 6,
                    "data_version": 1,
                    "date_iso": "2026-03-10T12:00:00Z",
                    "size_bytes": 777,
                },
            },
        )

        by_name = {entry["name"]: entry for entry in plan}
        self.assertTrue(bool(by_name["revelation.sqlite"]["needs_publish"]))
        self.assertEqual(
            by_name["revelation.sqlite"]["reasons"],
            ["data_version", "дата", "размер"],
        )
        self.assertTrue(bool(by_name["revelation_ru.sqlite"]["needs_publish"]))
        self.assertEqual(by_name["revelation_ru.sqlite"]["reasons"], ["файл отсутствует"])
        self.assertTrue(bool(by_name["revelation_extra.sqlite"]["remote_only"]))

    def test_release_publish_required_env_keys_cover_manifest_and_publish_targets(self) -> None:
        harness = _CoreDbHarness()

        keys = harness._release_publish_required_env_keys()

        self.assertIn("REVELATION_CONTENT_TOOL_REMOTE_WEB_MANIFEST_URL", keys)
        self.assertIn("REVELATION_CONTENT_TOOL_REMOTE_SUPABASE_MANIFEST_URL", keys)
        self.assertIn("REVELATION_CONTENT_TOOL_WEB_PUBLISH_REPO_PATH", keys)
        self.assertIn("REVELATION_CONTENT_TOOL_SUPABASE_SERVICE_ROLE_KEY", keys)

    def test_build_release_publish_confirmation_text_reports_both_targets(self) -> None:
        harness = _CoreDbHarness()

        text = harness._build_release_publish_confirmation_text(
            target_dir=Path("web/db"),
            local_entries={
                "revelation.sqlite": {
                    "schema_version": 4,
                    "data_version": 5,
                    "date_iso": "2026-03-29T12:00:00Z",
                    "size_bytes": 1000,
                }
            },
            web_target_state={
                "configured": True,
                "error": None,
                "manifest_url": "https://example.com/web/manifest.json",
                "plan": [
                    {
                        "name": "revelation.sqlite",
                        "remote_snapshot": {
                            "schema_version": 4,
                            "data_version": 4,
                            "date_iso": "2026-03-20T12:00:00Z",
                            "size_bytes": 900,
                        },
                        "needs_publish": True,
                        "reasons": ["data_version", "дата", "размер"],
                        "remote_only": False,
                    }
                ],
            },
            supabase_target_state={
                "configured": True,
                "error": None,
                "manifest_url": "https://example.com/supabase/manifest.json",
                "plan": [
                    {
                        "name": "revelation.sqlite",
                        "remote_snapshot": {
                            "schema_version": 4,
                            "data_version": 5,
                            "date_iso": "2026-03-29T12:00:00Z",
                            "size_bytes": 1000,
                        },
                        "needs_publish": False,
                        "reasons": [],
                        "remote_only": False,
                    }
                ],
            },
        )

        self.assertIn("Удаленный web: будет публикация", text)
        self.assertIn("Удаленный Supabase: публикация не требуется", text)
        self.assertIn("публикация в web: ДА", text)
        self.assertIn("публикация в Supabase: НЕТ", text)

    def test_build_release_web_commit_message_lists_new_versions(self) -> None:
        harness = _CoreDbHarness()

        subject, body = harness._build_release_web_commit_message(
            local_entries={
                "revelation.sqlite": {"data_version": 8},
                "revelation_ru.sqlite": {"data_version": 5},
            },
            target_state={
                "plan": [
                    {
                        "name": "revelation_ru.sqlite",
                        "needs_publish": True,
                    },
                    {
                        "name": "revelation.sqlite",
                        "needs_publish": True,
                    },
                    {
                        "name": "revelation_es.sqlite",
                        "needs_publish": False,
                    },
                ]
            },
        )

        self.assertEqual(subject, "Update published website databases [skip ci]")
        self.assertIn("revelation.sqlite: new data_version 8", body)
        self.assertIn("revelation_ru.sqlite: new data_version 5", body)

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

    def test_publish_files_to_external_git_repo_pushes_only_selected_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            remote_dir = root / "remote.git"
            website_repo_dir = root / "website"
            publish_source_dir = root / "publish_source"

            self._run_git(["init", "--bare", str(remote_dir)], cwd=root)
            self._run_git(["init", "-b", "main", str(website_repo_dir)], cwd=root)
            self._run_git(["config", "user.name", "Website Publish Test"], cwd=website_repo_dir)
            self._run_git(["config", "user.email", "website-publish-test@example.com"], cwd=website_repo_dir)
            self._run_git(["remote", "add", "origin", str(remote_dir)], cwd=website_repo_dir)

            repo_db = website_repo_dir / "db"
            repo_db.mkdir(parents=True, exist_ok=True)
            (repo_db / "revelation_ru.sqlite").write_text("old-db\n", encoding="utf-8")
            (repo_db / "manifest.json").write_text('{"version":1}\n', encoding="utf-8")
            (website_repo_dir / "README.md").write_text("website readme\n", encoding="utf-8")
            self._run_git(["add", "."], cwd=website_repo_dir)
            self._run_git(["commit", "-m", "Initial"], cwd=website_repo_dir)
            self._run_git(["push", "-u", "origin", "main"], cwd=website_repo_dir)

            publish_source_dir.mkdir(parents=True, exist_ok=True)
            local_db_path = publish_source_dir / "revelation_ru.sqlite"
            local_manifest_path = publish_source_dir / "manifest.json"
            local_db_path.write_text("new-db\n", encoding="utf-8")
            local_manifest_path.write_text('{"version":2}\n', encoding="utf-8")

            harness = _CoreDbHarness()

            with mock.patch.object(
                core_db_module,
                "ALLOWED_WEB_PUBLISH_REMOTE_URLS",
                {harness._normalize_git_remote_url(str(remote_dir))},
            ):
                result = harness._publish_files_to_external_git_repo(
                    repo_source=str(website_repo_dir),
                    branch_name="main",
                    remote_name="origin",
                    repo_db_dir="db",
                    paths_to_publish=[local_db_path, local_manifest_path],
                    commit_subject="Update published website databases [skip ci]",
                    commit_body="revelation_ru.sqlite: new data_version 5",
                )

            self.assertTrue(bool(result["performed"]))
            self.assertEqual(result["branch_name"], "main")
            self.assertEqual(result["remote_name"], "origin")

            remote_subject = self._run_git(
                ["log", "-1", "--pretty=%s", "refs/heads/main"],
                git_dir=remote_dir,
            )
            remote_body = self._run_git(
                ["log", "-1", "--pretty=%b", "refs/heads/main"],
                git_dir=remote_dir,
            )
            remote_db = self._run_git(
                ["show", "refs/heads/main:db/revelation_ru.sqlite"],
                git_dir=remote_dir,
            )
            remote_manifest = self._run_git(
                ["show", "refs/heads/main:db/manifest.json"],
                git_dir=remote_dir,
            )
            remote_readme = self._run_git(
                ["show", "refs/heads/main:README.md"],
                git_dir=remote_dir,
            )

            self.assertEqual(remote_subject, "Update published website databases [skip ci]")
            self.assertIn("revelation_ru.sqlite: new data_version 5", remote_body)
            self.assertEqual(remote_db, "new-db")
            self.assertEqual(remote_manifest, '{"version":2}')
            self.assertEqual(remote_readme, "website readme")

    def test_supabase_publish_uploads_db_files_before_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_one = root / "revelation.sqlite"
            db_two = root / "revelation_ru.sqlite"
            manifest_path = root / "manifest.json"
            db_one.write_bytes(b"db-one")
            db_two.write_bytes(b"db-two")
            manifest_path.write_text('{"version":2}\n', encoding="utf-8")

            captured_requests: list[dict[str, object]] = []

            def fake_urlopen(request, timeout=0):
                captured_requests.append(
                    {
                        "url": request.full_url,
                        "headers": {key.lower(): value for key, value in request.header_items()},
                        "body": request.data,
                    }
                )
                return _FakeUrlopenResponse()

            harness = _CoreDbHarness()
            with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
                supabase_result = harness._publish_db_files_to_supabase(
                    supabase_url="https://example.supabase.co/",
                    service_role_key="secret-key",
                    bucket_name="db",
                    db_prefix="",
                    db_paths=[db_one, db_two],
                )
                manifest_object = harness._publish_manifest_to_supabase(
                    supabase_url="https://example.supabase.co/",
                    service_role_key="secret-key",
                    bucket_name="db",
                    manifest_object_path="manifest.json",
                    manifest_path=manifest_path,
                )

            self.assertTrue(bool(supabase_result["performed"]))
            self.assertEqual(
                supabase_result["published_objects"],
                ["revelation.sqlite", "revelation_ru.sqlite"],
            )
            self.assertEqual(manifest_object, "manifest.json")
            self.assertEqual(len(captured_requests), 3)
            self.assertTrue(str(captured_requests[0]["url"]).endswith("/storage/v1/object/db/revelation.sqlite"))
            self.assertTrue(str(captured_requests[1]["url"]).endswith("/storage/v1/object/db/revelation_ru.sqlite"))
            self.assertTrue(str(captured_requests[2]["url"]).endswith("/storage/v1/object/db/manifest.json"))
            self.assertEqual(captured_requests[0]["headers"]["x-upsert"], "true")
            self.assertEqual(captured_requests[2]["headers"]["content-type"], "application/json; charset=utf-8")

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
