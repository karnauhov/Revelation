from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

from ..helpers import LANGUAGE_NAME_RU_BY_CODE
from ..models import ArticleRow, PrimarySourceSummary, ResourceRow, StrongRow
from ..web_db_manifest import write_web_db_manifest

COMMON_DB_SCHEMA_VERSION = 4
LOCALIZED_DB_SCHEMA_VERSION = 6
ALLOWED_GIT_PUBLISH_REMOTE_URLS = {
    "https://github.com/karnauhov/revelation",
}
DB_METADATA_TABLE_NAME = "db_metadata"
DB_METADATA_SCHEMA_VERSION_KEY = "schema_version"
DB_METADATA_DATA_VERSION_KEY = "data_version"
DB_METADATA_DATE_KEY = "date"


class CoreDbMixin:
        def _db_schema_version_for_path(self, db_path: Path) -> int:
            if db_path.name.lower() == "revelation.sqlite":
                return COMMON_DB_SCHEMA_VERSION
            return LOCALIZED_DB_SCHEMA_VERSION

        def _db_lang_code_from_path(self, db_path: Path | None) -> str:
            if db_path is None:
                return ""
            stem = db_path.stem
            if "_" not in stem:
                return ""
            raw_lang = stem.split("_", maxsplit=1)[1].strip().lower()
            if not raw_lang:
                return ""
            return raw_lang[:2]

        def _lang_sort_key(self, lang_code: str) -> tuple[int, str]:
            normalized = lang_code.strip().lower()[:2]
            return (0 if normalized == "ru" else 1, normalized)

        def _localized_db_path_sort_key(self, db_path: Path) -> tuple[int, str, str]:
            lang_code = self._db_lang_code_from_path(db_path)
            return (*self._lang_sort_key(lang_code), db_path.name.lower())

        def _active_connection_for_db_path(self, db_path: Path) -> sqlite3.Connection | None:
            resolved = db_path.resolve()
            if self.common_connection is not None and self.common_db_path is not None:
                if self.common_db_path.resolve() == resolved:
                    return self.common_connection
            if self.connection is not None and self.current_db_path is not None:
                if self.current_db_path.resolve() == resolved:
                    return self.connection
            return None

        def _metadata_now_iso(self) -> str:
            return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

        def _ensure_db_metadata_table_on_connection(
            self,
            connection: sqlite3.Connection,
            *,
            schema_version: int,
        ) -> int:
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {DB_METADATA_TABLE_NAME} (
                  key TEXT NOT NULL PRIMARY KEY,
                  value TEXT NOT NULL
                )
                """
            )
            current_user_version = int(connection.execute("PRAGMA user_version").fetchone()[0] or 0)
            effective_schema_version = max(current_user_version, schema_version)
            if current_user_version < effective_schema_version:
                connection.execute(f"PRAGMA user_version = {effective_schema_version}")
            connection.execute(
                f"""
                INSERT INTO {DB_METADATA_TABLE_NAME}(key, value)
                VALUES(?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (DB_METADATA_SCHEMA_VERSION_KEY, str(effective_schema_version)),
            )
            return effective_schema_version

        def _read_db_version_snapshot(
            self,
            db_path: Path | None,
            *,
            connection: sqlite3.Connection | None = None,
        ) -> dict[str, object] | None:
            if db_path is None or not db_path.exists():
                return None

            con = connection
            own_connection = False
            if con is None:
                con = self._active_connection_for_db_path(db_path)
            if con is None:
                con = sqlite3.connect(str(db_path))
                con.row_factory = sqlite3.Row
                own_connection = True

            try:
                user_version = int(con.execute("PRAGMA user_version").fetchone()[0] or 0)
                schema_version: int | None = user_version if user_version > 0 else None
                data_version: int | None = None
                date_iso: str | None = None

                if self._table_exists(con, DB_METADATA_TABLE_NAME):
                    rows = con.execute(
                        f"""
                        SELECT key, value
                        FROM {DB_METADATA_TABLE_NAME}
                        WHERE key IN (?, ?, ?)
                        """,
                        (
                            DB_METADATA_SCHEMA_VERSION_KEY,
                            DB_METADATA_DATA_VERSION_KEY,
                            DB_METADATA_DATE_KEY,
                        ),
                    ).fetchall()
                    values = {str(row["key"]): str(row["value"]) for row in rows}
                    if values.get(DB_METADATA_SCHEMA_VERSION_KEY, "").isdigit():
                        schema_version = int(values[DB_METADATA_SCHEMA_VERSION_KEY])
                    if values.get(DB_METADATA_DATA_VERSION_KEY, "").isdigit():
                        data_version = int(values[DB_METADATA_DATA_VERSION_KEY])
                    date_iso = values.get(DB_METADATA_DATE_KEY) or None

                return {
                    "path": db_path,
                    "schema_version": schema_version,
                    "data_version": data_version,
                    "date_iso": date_iso,
                    "size_bytes": int(db_path.stat().st_size),
                }
            finally:
                if own_connection:
                    con.close()

        def _touch_db_data_version(
            self,
            db_path: Path,
            *,
            schema_version: int,
            connection: sqlite3.Connection | None = None,
            increment_data_version: bool = False,
            next_data_version: int | None = None,
            commit: bool = False,
        ) -> dict[str, object] | None:
            con = connection
            own_connection = False
            if con is None:
                con = sqlite3.connect(str(db_path))
                con.row_factory = sqlite3.Row
                own_connection = True

            try:
                def apply_touch(active_connection: sqlite3.Connection) -> None:
                    effective_schema_version = self._ensure_db_metadata_table_on_connection(
                        active_connection,
                        schema_version=schema_version,
                    )
                    row = active_connection.execute(
                        f"""
                        SELECT value
                        FROM {DB_METADATA_TABLE_NAME}
                        WHERE key = ?
                        LIMIT 1
                        """,
                        (DB_METADATA_DATA_VERSION_KEY,),
                    ).fetchone()
                    current_data_version = int(str(row[0]).strip()) if row and str(row[0]).strip().isdigit() else 0
                    resolved_data_version = current_data_version
                    if increment_data_version:
                        if next_data_version is not None:
                            resolved_data_version = max(next_data_version, 1)
                        else:
                            resolved_data_version = current_data_version + 1
                    if resolved_data_version <= 0:
                        resolved_data_version = 1
                    now_iso = self._metadata_now_iso()
                    active_connection.executemany(
                        f"""
                        INSERT INTO {DB_METADATA_TABLE_NAME}(key, value)
                        VALUES(?, ?)
                        ON CONFLICT(key) DO UPDATE SET value = excluded.value
                        """,
                        [
                            (DB_METADATA_SCHEMA_VERSION_KEY, str(effective_schema_version)),
                            (DB_METADATA_DATA_VERSION_KEY, str(resolved_data_version)),
                            (DB_METADATA_DATE_KEY, now_iso),
                        ],
                    )

                if own_connection:
                    with con:
                        apply_touch(con)
                else:
                    apply_touch(con)
                    if commit:
                        con.commit()

                return self._read_db_version_snapshot(db_path, connection=con)
            finally:
                if own_connection:
                    con.close()

        def _touch_common_db_data_version(
            self,
            *,
            connection: sqlite3.Connection | None = None,
            db_path: Path | None = None,
        ) -> dict[str, object] | None:
            target_path = db_path or self.common_db_path
            if target_path is None:
                return None
            return self._touch_db_data_version(
                target_path,
                schema_version=COMMON_DB_SCHEMA_VERSION,
                connection=connection,
            )

        def _touch_localized_db_data_version(
            self,
            *,
            connection: sqlite3.Connection | None = None,
            db_path: Path | None = None,
        ) -> dict[str, object] | None:
            target_path = db_path or self.current_db_path
            if target_path is None:
                return None
            return self._touch_db_data_version(
                target_path,
                schema_version=LOCALIZED_DB_SCHEMA_VERSION,
                connection=connection,
            )

        def _choose_folder(self) -> None:
            chosen = filedialog.askdirectory(initialdir=str(self.work_dir), title="Выберите папку с БД")
            if not chosen:
                return
            new_dir = Path(chosen)
            if new_dir == self.work_dir:
                return
            if not self._allow_switch_when_dirty():
                return
            self.work_dir = new_dir
            self.folder_var.set(str(self.work_dir))
            self._close_connection()
            self.current_db_path = None
            self._clear_all_db_views()
            self._set_dirty(False)
            self._refresh_db_list(initial_select=True)

        def _refresh_db_list(self, initial_select: bool = False) -> None:
            self.db_files.clear()
            if self.work_dir.exists():
                for db_path in sorted(
                    self.work_dir.glob("revelation_*.sqlite"),
                    key=self._localized_db_path_sort_key,
                ):
                    key = self._display_key_for_db(db_path)
                    self.db_files[key] = db_path

            self._rebuild_strong_tree_columns()
            self._rebuild_strong_localized_editors()

            self._open_common_connection()
            self._load_common_resources()
            self._load_strong_rows()
            self._update_section_db_labels()

            values = list(self.db_files.keys())
            self.db_combo["values"] = values
            if not values:
                self.db_var.set("")
                self._close_local_connection()
                self.current_db_path = None
                self._clear_local_views()
                self._set_dirty(False)
                self._set_status("В выбранной папке нет файлов вида revelation_<lang>.sqlite.")
                self._update_ui_availability()
                self._update_file_info()
                return

            previous = self.db_var.get()
            if previous in self.db_files:
                self.db_var.set(previous)
                if initial_select:
                    self._load_db(self.db_files[previous])
                else:
                    self._load_strong_rows()
                    self._update_ui_availability()
                    self._update_section_db_labels()
                    self._update_file_info()
                return

            self.db_var.set(values[0])
            self._load_db(self.db_files[values[0]])

        def _display_key_for_db(self, db_path: Path) -> str:
            stem = db_path.stem
            language = stem.split("_", maxsplit=1)[1] if "_" in stem else stem
            return f"{language}  ({db_path.name})"

        def _on_db_combo_selected(self, _event: object) -> None:
            key = self.db_var.get()
            db_path = self.db_files.get(key)
            if db_path is None:
                return
            if self.current_db_path == db_path:
                return
            if not self._allow_switch_when_dirty():
                if self.current_db_path is not None:
                    current_key = self._display_key_for_db(self.current_db_path)
                    self.db_var.set(current_key)
                return
            self._load_db(db_path)

        def _load_db(self, db_path: Path) -> None:
            self._close_local_connection()
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row
            self.current_db_path = db_path
            self._open_common_connection()

            # NOTE: Disabled by request to keep DB file modification time stable on open.
            # self._ensure_schema()
            self._load_rows()
            self._set_dirty(False)
            self._update_section_db_labels()
            self._update_file_info()
            self._update_ui_availability()

        def _open_common_connection(self) -> None:
            if self.common_connection is not None:
                self.common_connection.close()
                self.common_connection = None
                self.common_db_path = None

            for path in self._common_db_candidates():
                if not path.exists():
                    continue
                con: sqlite3.Connection | None = None
                try:
                    con = sqlite3.connect(path)
                    con.row_factory = sqlite3.Row
                    cur = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='common_resources'")
                    if cur.fetchone() is None:
                        con.close()
                        continue
                    # NOTE: Disabled by request to keep DB file modification time stable on open.
                    # self._ensure_common_schema_on_connection(con)
                    self.common_connection = con
                    self.common_db_path = path.resolve()
                    return
                except (sqlite3.DatabaseError, OSError):
                    if con is not None:
                        con.close()
                    continue

        def _common_db_candidates(self) -> list[Path]:
            candidates = [self.work_dir / "revelation.sqlite"]
            unique: list[Path] = []
            for path in candidates:
                resolved = path.resolve()
                if resolved not in unique:
                    unique.append(resolved)
            return unique

        def _ensure_schema(self) -> None:
            if self.connection is None:
                return
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS articles (
                  route TEXT NOT NULL PRIMARY KEY,
                  name TEXT NOT NULL,
                  description TEXT NOT NULL,
                  id_icon TEXT NOT NULL,
                  sort_order INTEGER NOT NULL DEFAULT 0,
                  is_visible INTEGER NOT NULL DEFAULT 1,
                  markdown TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS topic_texts (
                  route TEXT NOT NULL PRIMARY KEY,
                  markdown TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS topics (
                  route TEXT NOT NULL PRIMARY KEY,
                  name TEXT NOT NULL,
                  description TEXT NOT NULL,
                  id_icon TEXT NOT NULL,
                  sort_order INTEGER NOT NULL DEFAULT 0,
                  is_visible INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS greek_descs (
                  id INTEGER NOT NULL PRIMARY KEY,
                  "desc" TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS db_metadata (
                  key TEXT NOT NULL PRIMARY KEY,
                  value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS primary_source_texts (
                  source_id TEXT NOT NULL PRIMARY KEY,
                  title_markup TEXT NOT NULL,
                  date_label TEXT NOT NULL,
                  content_label TEXT NOT NULL,
                  material_text TEXT NOT NULL,
                  text_style_text TEXT NOT NULL,
                  found_text TEXT NOT NULL,
                  classification_text TEXT NOT NULL,
                  current_location_text TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS primary_source_link_texts (
                  source_id TEXT NOT NULL,
                  link_id TEXT NOT NULL,
                  title TEXT NOT NULL,
                  PRIMARY KEY (source_id, link_id)
                );
                """
            )
            self.connection.executescript(
                """
                INSERT INTO articles(route, name, description, id_icon, sort_order, is_visible, markdown)
                SELECT
                  t.route,
                  t.name,
                  t.description,
                  t.id_icon,
                  t.sort_order,
                  t.is_visible,
                  COALESCE(tt.markdown, '')
                FROM topics t
                LEFT JOIN topic_texts tt ON tt.route = t.route
                WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'topics')
                  AND EXISTS (SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'topic_texts')
                  AND NOT EXISTS (
                    SELECT 1
                    FROM articles a
                    WHERE a.route = t.route
                  );

                INSERT INTO articles(route, name, description, id_icon, sort_order, is_visible, markdown)
                SELECT
                  tt.route,
                  tt.route,
                  '',
                  '',
                  0,
                  0,
                  tt.markdown
                FROM topic_texts tt
                WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'topic_texts')
                  AND NOT EXISTS (
                    SELECT 1
                    FROM articles a
                    WHERE a.route = tt.route
                  );

                DROP TABLE IF EXISTS topics;
                DROP TABLE IF EXISTS topic_texts;
                """
            )
            self._ensure_db_metadata_table_on_connection(
                self.connection,
                schema_version=LOCALIZED_DB_SCHEMA_VERSION,
            )
            self.connection.commit()

        def _ensure_common_schema_on_connection(self, connection: sqlite3.Connection) -> None:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS greek_words (
                  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                  word TEXT NOT NULL,
                  category TEXT NOT NULL,
                  synonyms TEXT NOT NULL,
                  origin TEXT NOT NULL,
                  usage TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS common_resources (
                  key TEXT NOT NULL PRIMARY KEY,
                  file_name TEXT NOT NULL,
                  mime_type TEXT NOT NULL,
                  data BLOB NOT NULL
                );

                CREATE TABLE IF NOT EXISTS db_metadata (
                  key TEXT NOT NULL PRIMARY KEY,
                  value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS primary_sources (
                  id TEXT NOT NULL PRIMARY KEY,
                  family TEXT NOT NULL,
                  number INTEGER NOT NULL,
                  group_kind TEXT NOT NULL,
                  sort_order INTEGER NOT NULL DEFAULT 0,
                  verses_count INTEGER NOT NULL DEFAULT 0,
                  preview_resource_key TEXT NOT NULL,
                  default_max_scale REAL NOT NULL DEFAULT 3.0,
                  can_show_images INTEGER NOT NULL DEFAULT 1,
                  images_are_monochrome INTEGER NOT NULL DEFAULT 0,
                  notes TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS primary_source_links (
                  source_id TEXT NOT NULL,
                  link_id TEXT NOT NULL,
                  sort_order INTEGER NOT NULL DEFAULT 0,
                  link_role TEXT NOT NULL,
                  url TEXT NOT NULL,
                  PRIMARY KEY (source_id, link_id)
                );

                CREATE TABLE IF NOT EXISTS primary_source_attributions (
                  source_id TEXT NOT NULL,
                  attribution_id TEXT NOT NULL,
                  sort_order INTEGER NOT NULL DEFAULT 0,
                  text TEXT NOT NULL,
                  url TEXT NOT NULL,
                  PRIMARY KEY (source_id, attribution_id)
                );

                CREATE TABLE IF NOT EXISTS primary_source_pages (
                  source_id TEXT NOT NULL,
                  page_name TEXT NOT NULL,
                  sort_order INTEGER NOT NULL DEFAULT 0,
                  content_ref TEXT NOT NULL,
                  image_path TEXT NOT NULL,
                  PRIMARY KEY (source_id, page_name)
                );

                CREATE TABLE IF NOT EXISTS primary_source_words (
                  source_id TEXT NOT NULL,
                  page_name TEXT NOT NULL,
                  word_index INTEGER NOT NULL,
                  text TEXT NOT NULL,
                  strong_number INTEGER,
                  strong_pronounce INTEGER NOT NULL DEFAULT 0,
                  strong_x_shift REAL NOT NULL DEFAULT 0.0,
                  missing_char_indexes_json TEXT NOT NULL DEFAULT '[]',
                  rectangles_json TEXT NOT NULL DEFAULT '[]',
                  PRIMARY KEY (source_id, page_name, word_index)
                );

                CREATE TABLE IF NOT EXISTS primary_source_verses (
                  source_id TEXT NOT NULL,
                  page_name TEXT NOT NULL,
                  verse_index INTEGER NOT NULL,
                  chapter_number INTEGER NOT NULL,
                  verse_number INTEGER NOT NULL,
                  label_x REAL NOT NULL,
                  label_y REAL NOT NULL,
                  word_indexes_json TEXT NOT NULL DEFAULT '[]',
                  contours_json TEXT NOT NULL DEFAULT '[]',
                  PRIMARY KEY (source_id, page_name, verse_index)
                );
                """
            )
            self._ensure_db_metadata_table_on_connection(
                connection,
                schema_version=COMMON_DB_SCHEMA_VERSION,
            )
            connection.commit()

        def _load_rows(self) -> None:
            assert self.connection is not None

            article_rows = self.connection.execute(
                """
                SELECT route, name, description, id_icon, sort_order, is_visible, markdown
                FROM articles
                ORDER BY sort_order ASC, route ASC
                """
            ).fetchall()
            self.articles = [
                ArticleRow(
                    route=row["route"],
                    name=row["name"],
                    description=row["description"],
                    id_icon=row["id_icon"],
                    sort_order=int(row["sort_order"]),
                    is_visible=bool(row["is_visible"]),
                    markdown=row["markdown"] or "",
                )
                for row in article_rows
            ]

            self._load_common_resources()
            self._load_strong_rows()
            self._load_primary_sources()
            self._refresh_articles_tree()
            self._refresh_topic_icon_options()
            self._clear_article_editor()
            self._clear_resource_editor()

        def _clear_all_db_views(self) -> None:
            self._clear_local_views()
            self.common_resources.clear()
            self._refresh_resources_tree()
            self._clear_resource_editor()
            self.strong_rows.clear()
            self.strong_filtered_indices.clear()
            self._refresh_strong_tree()
            self._clear_strong_editor()
            self.primary_sources.clear()
            self.primary_source_pages.clear()
            self.primary_source_link_rows.clear()
            self.primary_source_attribution_rows.clear()
            self.primary_source_word_rows.clear()
            self.primary_source_verse_rows.clear()
            self._refresh_primary_sources_tree()
            self._clear_primary_source_editor()
            self._refresh_topic_icon_options()

        def _clear_local_views(self) -> None:
            self.articles.clear()
            self._refresh_articles_tree()
            self._clear_article_editor()
            self.primary_sources.clear()
            self.primary_source_pages.clear()
            self.primary_source_link_rows.clear()
            self.primary_source_attribution_rows.clear()
            self.primary_source_word_rows.clear()
            self.primary_source_verse_rows.clear()
            self._refresh_primary_sources_tree()
            self._clear_primary_source_editor()
            self._refresh_topic_icon_options()

        def _refresh_articles_tree(self) -> None:
            self.articles_tree.delete(*self.articles_tree.get_children())
            for idx, row in enumerate(self.articles):
                route_display = row.route if row.route else self.NO_ARTICLE_OPTION
                tags = (self.UNBOUND_TAG,) if not row.route else ()
                self.articles_tree.insert(
                    "",
                    "end",
                    iid=str(idx),
                    values=(route_display, row.name, row.sort_order, "Да" if row.is_visible else "Нет"),
                    tags=tags,
                )

        def _refresh_topic_icon_options(self) -> None:
            image_keys = sorted(
                {
                    row.key
                    for row in self.common_resources
                    if self._is_graphic_resource(row.mime_type, row.file_name)
                }
            )
            current = self._icon_value_from_editor()
            if current and current not in image_keys:
                image_keys.append(current)
                image_keys.sort()
            self.topic_icon_combo["values"] = [self.NO_ICON_OPTION, *image_keys]

        def _icon_value_from_editor(self) -> str:
            value = self.topic_icon_var.get().strip()
            if not value or value == self.NO_ICON_OPTION:
                return ""
            return value

        def _display_icon_value(self, icon_key: str) -> str:
            return icon_key if icon_key else self.NO_ICON_OPTION

        def _is_graphic_resource(self, mime_type: str, file_name: str) -> bool:
            mime = (mime_type or "").strip().lower()
            if mime.startswith("image/"):
                return True
            ext = Path(file_name or "").suffix.lower()
            return ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".tif", ".tiff"}

        def _load_common_resources(self) -> None:
            self.common_resources.clear()
            if self.common_connection is None:
                self._refresh_resources_tree()
                self._refresh_topic_icon_options()
                self._update_section_db_labels()
                return
            try:
                rows = self.common_connection.execute(
                    """
                    SELECT key, file_name, mime_type, length(data) AS size_bytes
                    FROM common_resources
                    ORDER BY key ASC
                    """
                ).fetchall()
            except sqlite3.DatabaseError:
                rows = []
            self.common_resources = [
                ResourceRow(
                    key=row["key"],
                    file_name=row["file_name"],
                    mime_type=row["mime_type"],
                    size_bytes=int(row["size_bytes"] or 0),
                )
                for row in rows
            ]
            self._refresh_resources_tree()
            self._refresh_topic_icon_options()
            self._update_section_db_labels()


        def _save_all(self, *, status_text: str | None = None, silent: bool = False) -> bool:
            if self.connection is None or self.current_db_path is None:
                messagebox.showwarning("Нет БД", "Сначала откройте локализованную БД.", parent=self)
                return False

            try:
                with self.connection:
                    self.connection.execute("DELETE FROM articles")
                    self.connection.executemany(
                        """
                        INSERT INTO articles(route, name, description, id_icon, sort_order, is_visible, markdown)
                        VALUES(?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            (
                                row.route,
                                row.name,
                                row.description,
                                row.id_icon,
                                row.sort_order,
                                1 if row.is_visible else 0,
                                row.markdown,
                            )
                            for row in self.articles
                        ],
                    )
                    self._touch_localized_db_data_version(connection=self.connection)
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить изменения:\n{exc}", parent=self)
                return False

            self._set_dirty(False)
            self._update_file_info()
            if not silent:
                self._set_status(status_text or f"Сохранено: {self.current_db_path.stem}")
            return True

        def _add_localized_language_db(self) -> None:
            source_dir = self.work_dir
            if not source_dir.exists():
                messagebox.showwarning("Нет папки", "Рабочая папка не существует.", parent=self)
                return

            source_db = self._english_localized_db_path()
            if source_db is None:
                messagebox.showwarning(
                    "Нет английской БД",
                    "Не найден файл revelation_en.sqlite. Сначала добавьте или скопируйте английскую локализованную БД.",
                    parent=self,
                )
                return

            selected_code = self._prompt_new_language_code()
            if selected_code is None:
                return

            target_code = selected_code.strip().lower()
            if target_code == "en":
                messagebox.showwarning(
                    "Недопустимый код",
                    "Код 'en' уже используется как исходная английская БД.",
                    parent=self,
                )
                return

            if not re.fullmatch(r"[a-z]{2}", target_code):
                messagebox.showwarning(
                    "Некорректный код",
                    "Используйте двухбуквенный код языка (только латиница), например: es, ru, uk.",
                    parent=self,
                )
                return

            target_db = source_dir / f"revelation_{target_code}.sqlite"
            if target_db.exists():
                replace_existing = messagebox.askyesno(
                    "Файл уже существует",
                    (
                        f"Файл {target_db.name} уже существует.\n"
                        "Пересоздать его из английской БД и очистить переводимые поля?"
                    ),
                    parent=self,
                )
                if not replace_existing:
                    return

            if (
                self.dirty
                and self.current_db_path is not None
                and self.current_db_path.resolve() == source_db.resolve()
            ):
                answer = messagebox.askyesnocancel(
                    "Несохраненные изменения",
                    (
                        "В английской БД есть несохраненные изменения.\n"
                        "Сохранить их перед созданием новой локализованной БД?"
                    ),
                    parent=self,
                )
                if answer is None:
                    return
                if answer and not self._save_all(silent=True):
                    return

            try:
                target_db.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_db, target_db)
                translated_tests = self._initialize_new_localized_db(target_db, target_code=target_code)
            except (sqlite3.DatabaseError, OSError) as exc:
                messagebox.showerror(
                    "Ошибка создания БД",
                    f"Не удалось создать '{target_db.name}':\n{exc}",
                    parent=self,
                )
                return

            self._refresh_db_list(initial_select=False)
            self._set_status(
                (
                    f"Создана локализованная БД: {target_db.name}. "
                    f"Переводимые поля очищены, тестовых страниц переведено: {translated_tests}."
                )
            )

        def _english_localized_db_path(self) -> Path | None:
            preferred = self.work_dir / "revelation_en.sqlite"
            if preferred.exists():
                return preferred.resolve()

            for db_path in sorted(self.work_dir.glob("revelation_*.sqlite")):
                stem = db_path.stem
                lang = stem.split("_", maxsplit=1)[1] if "_" in stem else ""
                if lang.strip().lower().startswith("en"):
                    return db_path.resolve()
            return None

        def _prompt_new_language_code(self) -> str | None:
            existing_codes = {lang for lang, _ in self._localized_db_entries()}
            available_options = [
                (code, name)
                for code, name in LANGUAGE_NAME_RU_BY_CODE.items()
                if code != "en" and code not in existing_codes
            ]
            options = sorted(
                available_options,
                key=lambda item: (*self._lang_sort_key(item[0]), item[1].lower()),
            )
            labels = [f"{code.upper()} - {name}" for code, name in options]
            code_by_label = {label: code for label, (code, _name) in zip(labels, options)}

            dialog = tk.Toplevel(self)
            dialog.title("Добавить язык")
            dialog.transient(self)
            dialog.grab_set()
            dialog.resizable(False, False)

            frame = ttk.Frame(dialog, padding=12)
            frame.grid(row=0, column=0, sticky="nsew")
            frame.columnconfigure(1, weight=1)

            selection_var = tk.StringVar(value=labels[0] if labels else "")
            custom_code_var = tk.StringVar(value="")
            result: dict[str, str | None] = {"code": None}

            ttk.Label(
                frame,
                text="Выберите язык из списка или введите свой двухбуквенный код.",
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

            ttk.Label(frame, text="Язык:").grid(row=1, column=0, sticky="w", padx=(0, 8))
            combo = ttk.Combobox(
                frame,
                state="readonly",
                textvariable=selection_var,
                values=labels,
                width=42,
            )
            combo.grid(row=1, column=1, sticky="ew")

            ttk.Label(frame, text="Код вручную:").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
            code_entry = ttk.Entry(frame, textvariable=custom_code_var, width=10)
            code_entry.grid(row=2, column=1, sticky="w", pady=(8, 0))
            ttk.Label(frame, text="Например: fr, de, it").grid(
                row=3,
                column=1,
                sticky="w",
                pady=(4, 0),
            )

            buttons = ttk.Frame(frame)
            buttons.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))

            def submit() -> None:
                manual_code = custom_code_var.get().strip().lower()
                selected_code = code_by_label.get(selection_var.get().strip(), "")
                code = manual_code or selected_code
                if not re.fullmatch(r"[a-z]{2}", code):
                    messagebox.showwarning(
                        "Некорректный код",
                        "Укажите двухбуквенный код языка (латиница), например: es, ru, uk.",
                        parent=dialog,
                    )
                    return
                result["code"] = code
                dialog.destroy()

            ttk.Button(buttons, text="Создать", command=submit).pack(side="left")
            ttk.Button(buttons, text="Отмена", command=dialog.destroy).pack(side="left", padx=(8, 0))

            dialog.bind("<Return>", lambda _event: submit())
            dialog.bind("<Escape>", lambda _event: dialog.destroy())

            self._fit_and_center_toplevel(
                dialog,
                min_width=560,
                max_width=720,
                min_height=220,
                max_height=280,
            )
            if labels:
                combo.focus_set()
            else:
                code_entry.focus_set()

            self.wait_window(dialog)
            return result["code"]

        def _initialize_new_localized_db(self, db_path: Path, *, target_code: str) -> int:
            translated_test_rows = 0
            with sqlite3.connect(str(db_path)) as con:
                con.row_factory = sqlite3.Row

                if self._table_exists(con, "articles"):
                    test_rows = con.execute(
                        """
                        SELECT route, name, description, markdown
                        FROM articles
                        WHERE lower(route) LIKE '%test%'
                        ORDER BY sort_order ASC, route ASC
                        """
                    ).fetchall()
                    con.execute("UPDATE articles SET name = '', description = '', markdown = ''")

                    for row in test_rows:
                        translated_name = self._translate_with_google(str(row["name"] or ""), target_code=target_code)
                        translated_description = self._translate_with_google(
                            str(row["description"] or ""),
                            target_code=target_code,
                        )
                        translated_markdown = self._translate_with_google(
                            str(row["markdown"] or ""),
                            target_code=target_code,
                        )
                        con.execute(
                            """
                            UPDATE articles
                            SET name = ?, description = ?, markdown = ?
                            WHERE route = ?
                            """,
                            (
                                translated_name,
                                translated_description,
                                translated_markdown,
                                str(row["route"]),
                            ),
                        )
                        translated_test_rows += 1

                if self._table_exists(con, "topic_texts"):
                    con.execute("UPDATE topic_texts SET markdown = ''")
                if self._table_exists(con, "topics"):
                    con.execute("UPDATE topics SET name = '', description = ''")
                if self._table_exists(con, "greek_descs"):
                    con.execute('UPDATE greek_descs SET "desc" = ""')
                if self._table_exists(con, "primary_source_texts"):
                    con.execute(
                        """
                        UPDATE primary_source_texts
                        SET
                            title_markup = '',
                            date_label = '',
                            content_label = '',
                            material_text = '',
                            text_style_text = '',
                            found_text = '',
                            classification_text = '',
                            current_location_text = ''
                        """
                    )
                if self._table_exists(con, "primary_source_link_texts"):
                    con.execute("UPDATE primary_source_link_texts SET title = ''")

                self._touch_localized_db_data_version(connection=con, db_path=db_path)
                con.commit()

            return translated_test_rows

        def _table_exists(self, connection: sqlite3.Connection, table_name: str) -> bool:
            row = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1",
                (table_name,),
            ).fetchone()
            return row is not None

        def _translate_with_google(self, text: str, *, target_code: str) -> str:
            source_text = text.strip()
            if not source_text:
                return ""
            query = urllib.parse.urlencode(
                {
                    "client": "gtx",
                    "sl": "en",
                    "tl": target_code,
                    "dt": "t",
                    "q": source_text,
                }
            )
            request = urllib.request.Request(
                f"https://translate.googleapis.com/translate_a/single?{query}",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
                return source_text

            if not isinstance(payload, list) or not payload:
                return source_text
            segments = payload[0]
            if not isinstance(segments, list):
                return source_text
            translated = "".join(
                segment[0]
                for segment in segments
                if isinstance(segment, list) and segment and isinstance(segment[0], str)
            ).strip()
            return translated or source_text

        def _web_db_manifest_path(self, target_dir: Path) -> Path:
            return target_dir / "manifest.json"

        def _git_publish_env_path(self) -> Path:
            return self.project_root / "env" / "content_tool_git_publish.env"

        def _parse_env_file(self, env_path: Path) -> dict[str, str]:
            values: dict[str, str] = {}
            if not env_path.exists():
                return values
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", maxsplit=1)
                values[key.strip()] = value.strip()
            return values

        def _env_flag_is_enabled(self, value: str | None) -> bool:
            if value is None:
                return False
            return value.strip().lower() in {"1", "true", "yes", "on"}

        def _run_git_command(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            completed = subprocess.run(
                ["git", *args],
                cwd=str(cwd or self.project_root),
                text=True,
                capture_output=True,
                check=False,
            )
            if check and completed.returncode != 0:
                error_text = (completed.stderr or completed.stdout or "").strip()
                if not error_text:
                    error_text = f"git exited with code {completed.returncode}"
                raise RuntimeError(error_text)
            return completed

        def _quote_sqlite_identifier(self, identifier: str) -> str:
            return '"' + identifier.replace('"', '""') + '"'

        def _db_table_names(self, connection: sqlite3.Connection) -> list[str]:
            rows = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                  AND name <> ?
                ORDER BY name COLLATE NOCASE ASC
                """,
                (DB_METADATA_TABLE_NAME,),
            ).fetchall()
            return [str(row[0]) for row in rows]

        def _db_table_sql(self, connection: sqlite3.Connection, table_name: str) -> str:
            row = connection.execute(
                """
                SELECT COALESCE(sql, '')
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                LIMIT 1
                """,
                (table_name,),
            ).fetchone()
            return str(row[0]) if row is not None else ""

        def _hash_sqlite_value(self, digest: Any, value: object) -> None:
            if value is None:
                digest.update(b"N")
                return
            if isinstance(value, bytes):
                digest.update(b"B")
                digest.update(len(value).to_bytes(8, byteorder="big", signed=False))
                digest.update(value)
                return
            if isinstance(value, str):
                encoded = value.encode("utf-8")
                digest.update(b"S")
                digest.update(len(encoded).to_bytes(8, byteorder="big", signed=False))
                digest.update(encoded)
                return
            if isinstance(value, int):
                digest.update(b"I")
                digest.update(str(value).encode("ascii"))
                return
            if isinstance(value, float):
                digest.update(b"F")
                digest.update(repr(value).encode("ascii"))
                return
            encoded = repr(value).encode("utf-8")
            digest.update(b"R")
            digest.update(len(encoded).to_bytes(8, byteorder="big", signed=False))
            digest.update(encoded)

        def _table_content_digest(self, connection: sqlite3.Connection, table_name: str) -> str:
            quoted_table = self._quote_sqlite_identifier(table_name)
            cursor = connection.execute(f"SELECT * FROM {quoted_table}")
            row_digests: list[bytes] = []
            row_count = 0

            for row in cursor:
                row_digest = hashlib.sha256()
                for value in row:
                    self._hash_sqlite_value(row_digest, value)
                    row_digest.update(b"\x1f")
                row_digests.append(row_digest.digest())
                row_count += 1

            row_digests.sort()
            digest = hashlib.sha256()
            digest.update(self._db_table_sql(connection, table_name).encode("utf-8"))
            digest.update(b"\x1e")
            digest.update(str(row_count).encode("ascii"))
            digest.update(b"\x1e")
            for row_digest in row_digests:
                digest.update(row_digest)
            return digest.hexdigest()

        def _compare_db_tables(self, source_db_path: Path, target_db_path: Path | None) -> list[str]:
            if target_db_path is None or not target_db_path.exists():
                source_con = sqlite3.connect(str(source_db_path))
                try:
                    return self._db_table_names(source_con)
                finally:
                    source_con.close()

            source_con = sqlite3.connect(str(source_db_path))
            target_con = sqlite3.connect(str(target_db_path))
            try:
                source_tables = self._db_table_names(source_con)
                target_tables = self._db_table_names(target_con)
                all_tables = sorted(set(source_tables) | set(target_tables), key=str.lower)
                changed_tables: list[str] = []

                for table_name in all_tables:
                    if table_name not in source_tables or table_name not in target_tables:
                        changed_tables.append(table_name)
                        continue
                    if self._db_table_sql(source_con, table_name) != self._db_table_sql(target_con, table_name):
                        changed_tables.append(table_name)
                        continue
                    if self._table_content_digest(source_con, table_name) != self._table_content_digest(target_con, table_name):
                        changed_tables.append(table_name)

                return changed_tables
            finally:
                source_con.close()
                target_con.close()

        def _relative_repo_path(self, path: Path) -> Path:
            return path.resolve().relative_to(self.project_root.resolve())

        def _normalize_git_remote_url(self, remote_url: str) -> str:
            normalized = remote_url.strip()
            if normalized.startswith("git@github.com:"):
                normalized = "https://github.com/" + normalized.split(":", maxsplit=1)[1]
            normalized = normalized.rstrip("/")
            if normalized.endswith(".git"):
                normalized = normalized[:-4]
            return normalized.lower()

        def _git_publish_settings(self) -> dict[str, str] | None:
            env_path = self._git_publish_env_path()
            values = self._parse_env_file(env_path)
            if not self._env_flag_is_enabled(values.get("REVELATION_CONTENT_TOOL_GIT_PUBLISH_ENABLED")):
                return None
            remote_name = values.get("REVELATION_CONTENT_TOOL_GIT_REMOTE", "").strip() or "origin"
            return {
                "remote_name": remote_name,
                "env_path": str(env_path),
            }

        def _git_publish_option_state(self) -> dict[str, Any]:
            env_path = self._git_publish_env_path()
            settings = self._git_publish_settings()
            if settings is None:
                return {
                    "enabled": False,
                    "reason": (
                        "Git-публикация по умолчанию отключена.\n"
                        f"Создайте локальный файл: {env_path}\n"
                        "со следующим содержимым:\n"
                        "REVELATION_CONTENT_TOOL_GIT_PUBLISH_ENABLED=1\n"
                        "REVELATION_CONTENT_TOOL_GIT_REMOTE=origin"
                    ),
                }

            try:
                repo_root = Path(
                    self._run_git_command(["rev-parse", "--show-toplevel"]).stdout.strip()
                ).resolve()
                if repo_root != self.project_root.resolve():
                    return {
                        "enabled": False,
                        "reason": f"Корень Git-репозитория не совпадает с project_root: {repo_root}",
                    }
                remote_names = [
                    line.strip()
                    for line in self._run_git_command(["remote"]).stdout.splitlines()
                    if line.strip()
                ]
                remote_name = settings["remote_name"]
                if remote_name not in remote_names:
                    return {
                        "enabled": False,
                        "reason": f"Настроенный remote '{remote_name}' не найден в этом репозитории.",
                    }
                remote_url = self._run_git_command(["remote", "get-url", remote_name]).stdout.strip()
                normalized_remote_url = self._normalize_git_remote_url(remote_url)
                if normalized_remote_url not in ALLOWED_GIT_PUBLISH_REMOTE_URLS:
                    return {
                        "enabled": False,
                        "reason": (
                            "Git-публикация разрешена только для официального remote репозитория Revelation.\n"
                            f"Текущий URL remote: {remote_url}"
                        ),
                    }
                branches = [
                    line.strip()
                    for line in self._run_git_command(
                        ["for-each-ref", "--format=%(refname:short)", "refs/heads"]
                    ).stdout.splitlines()
                    if line.strip()
                ]
                current_branch = self._run_git_command(["branch", "--show-current"]).stdout.strip()
            except RuntimeError as exc:
                return {
                    "enabled": False,
                    "reason": f"Git-публикация недоступна: {exc}",
                }

            ordered_branches: list[str] = []
            for branch_name in [current_branch, *branches]:
                if branch_name and branch_name not in ordered_branches:
                    ordered_branches.append(branch_name)

            if not ordered_branches:
                return {
                    "enabled": False,
                    "reason": "Для Git-публикации не найдено ни одной локальной ветки.",
                }

            return {
                "enabled": True,
                "remote_name": settings["remote_name"],
                "remote_url": remote_url,
                "branches": ordered_branches,
                "default_branch": current_branch or ordered_branches[0],
                "env_path": settings["env_path"],
            }

        def _build_git_publish_commit_message(
            self,
            *,
            successful_results: list[dict[str, Any]],
        ) -> tuple[str, str]:
            subject = "Update published web databases [skip ci]"
            body_lines: list[str] = []
            for result in successful_results:
                changed_tables = [str(name) for name in result.get("changed_tables", [])]
                table_text = ", ".join(changed_tables) if changed_tables else "metadata only"
                body_lines.append(f"{result['name']}: {table_text}")
            body = "\n".join(body_lines)
            return subject, body

        def _format_git_commit_message_preview(self, *, subject: str, body: str) -> str:
            lines = [subject]
            if body.strip():
                lines.append("")
                lines.extend(body.splitlines())
            return "\n".join(lines)

        def _publish_files_to_git_branch(
            self,
            *,
            branch_name: str,
            remote_name: str,
            paths_to_publish: list[Path],
            successful_results: list[dict[str, Any]],
            commit_subject: str | None = None,
            commit_body: str | None = None,
        ) -> dict[str, str]:
            subject = commit_subject
            body = commit_body
            if subject is None or body is None:
                subject, body = self._build_git_publish_commit_message(successful_results=successful_results)
            relative_paths = [self._relative_repo_path(path) for path in paths_to_publish]

            with tempfile.TemporaryDirectory(prefix="revelation-content-tool-git-") as temp_dir_str:
                temp_dir = Path(temp_dir_str)
                self._run_git_command(
                    ["worktree", "add", "--detach", str(temp_dir), f"refs/heads/{branch_name}"]
                )
                try:
                    for relative_path in relative_paths:
                        source_path = self.project_root / relative_path
                        destination_path = temp_dir / relative_path
                        destination_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, destination_path)

                    add_args = ["add", "--", *[str(path) for path in relative_paths]]
                    self._run_git_command(add_args, cwd=temp_dir)

                    staged_names = [
                        line.strip()
                        for line in self._run_git_command(
                            ["diff", "--cached", "--name-only", "--", *[str(path) for path in relative_paths]],
                            cwd=temp_dir,
                        ).stdout.splitlines()
                        if line.strip()
                    ]
                    if not staged_names:
                        raise RuntimeError("Не удалось подготовить изменения для Git-публикации.")

                    commit_args = ["commit", "-m", subject]
                    if body:
                        commit_args.extend(["-m", body])
                    self._run_git_command(commit_args, cwd=temp_dir)
                    commit_hash = self._run_git_command(["rev-parse", "HEAD"], cwd=temp_dir).stdout.strip()
                    self._run_git_command(
                        ["push", remote_name, f"HEAD:refs/heads/{branch_name}"],
                        cwd=temp_dir,
                    )
                finally:
                    self._run_git_command(["worktree", "remove", "--force", str(temp_dir)], check=False)

            return {
                "branch_name": branch_name,
                "remote_name": remote_name,
                "commit_hash": commit_hash,
                "subject": subject,
            }

        def _ask_publish_confirmation_dialog(
            self,
            *,
            title: str,
            message: str,
            git_option_state: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            decision: dict[str, Any] = {
                "confirmed": False,
                "git_publish": False,
                "branch_name": "",
            }

            dialog = tk.Toplevel(self)
            dialog.title(title)
            dialog.transient(self)
            dialog.grab_set()
            dialog.minsize(960, 480)

            container = ttk.Frame(dialog, padding=10)
            container.grid(row=0, column=0, sticky="nsew")
            dialog.columnconfigure(0, weight=1)
            dialog.rowconfigure(0, weight=1)
            container.columnconfigure(0, weight=1)
            container.rowconfigure(0, weight=1)

            text_widget = tk.Text(container, wrap="word", undo=False)
            text_widget.grid(row=0, column=0, sticky="nsew")
            scroll_y = ttk.Scrollbar(container, orient="vertical", command=text_widget.yview)
            scroll_y.grid(row=0, column=1, sticky="ns")
            text_widget.configure(yscrollcommand=scroll_y.set)
            text_widget.insert("1.0", message)
            text_widget.configure(state="disabled")

            publish_after_save_var = tk.BooleanVar(value=False)
            branch_var = tk.StringVar()
            branch_combo: ttk.Combobox | None = None

            if git_option_state is not None:
                git_frame = ttk.LabelFrame(container, text="Git-публикация", padding=10)
                git_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
                git_frame.columnconfigure(1, weight=1)

                if bool(git_option_state.get("enabled")):
                    branches = [str(item) for item in git_option_state.get("branches", [])]
                    default_branch = str(git_option_state.get("default_branch", "") or "")
                    branch_var.set(default_branch)

                    ttk.Checkbutton(
                        git_frame,
                        text="После сохранения выполнить commit и push только измененных файлов публикации",
                        variable=publish_after_save_var,
                    ).grid(row=0, column=0, columnspan=2, sticky="w")
                    ttk.Label(git_frame, text="Целевая ветка:").grid(
                        row=1,
                        column=0,
                        sticky="w",
                        padx=(0, 8),
                        pady=(8, 0),
                    )
                    branch_combo = ttk.Combobox(
                        git_frame,
                        textvariable=branch_var,
                        values=branches,
                        state="disabled",
                    )
                    branch_combo.grid(row=1, column=1, sticky="ew", pady=(8, 0))
                    ttk.Label(
                        git_frame,
                        text=f"Удаленный репозиторий (remote): {git_option_state['remote_name']}",
                    ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

                    def sync_git_controls() -> None:
                        assert branch_combo is not None
                        branch_combo.configure(state="readonly" if publish_after_save_var.get() else "disabled")

                    publish_after_save_var.trace_add("write", lambda *_args: sync_git_controls())
                    sync_git_controls()
                else:
                    ttk.Label(
                        git_frame,
                        text=str(git_option_state.get("reason", "Git-публикация недоступна.")),
                        justify="left",
                    ).grid(row=0, column=0, sticky="w")

            buttons = ttk.Frame(container)
            buttons.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 0))

            def confirm() -> None:
                if bool(git_option_state and git_option_state.get("enabled")) and publish_after_save_var.get():
                    selected_branch = branch_var.get().strip()
                    branches = [str(item) for item in git_option_state.get("branches", [])]
                    if selected_branch not in branches:
                        messagebox.showwarning(
                            "Некорректная ветка",
                            "Перед Git-публикацией выберите целевую ветку из списка.",
                            parent=dialog,
                        )
                        return
                    decision["git_publish"] = True
                    decision["branch_name"] = selected_branch
                decision["confirmed"] = True
                dialog.destroy()

            def decline() -> None:
                dialog.destroy()

            btn_confirm = ttk.Button(buttons, text="Подтвердить", command=confirm)
            btn_confirm.pack(side="left")
            ttk.Button(buttons, text="Отмена", command=decline).pack(side="left", padx=(8, 0))

            dialog.bind("<Return>", lambda _event: confirm())
            dialog.bind("<Escape>", lambda _event: decline())
            dialog.protocol("WM_DELETE_WINDOW", decline)

            # Intentionally ~1.5x wider than regular text dialogs for publish details.
            self._fit_and_center_toplevel(
                dialog,
                min_width=960,
                max_width=1560,
                min_height=480,
                max_height=980,
                pad_x=140,
                pad_y=120,
            )
            btn_confirm.focus_set()
            self.wait_window(dialog)
            return decision

        def _show_publish_result_dialog(self, *, title: str, message: str) -> None:
            dialog = tk.Toplevel(self)
            dialog.title(title)
            dialog.transient(self)
            dialog.grab_set()
            dialog.minsize(960, 420)

            container = ttk.Frame(dialog, padding=10)
            container.grid(row=0, column=0, sticky="nsew")
            dialog.columnconfigure(0, weight=1)
            dialog.rowconfigure(0, weight=1)
            container.columnconfigure(0, weight=1)
            container.rowconfigure(0, weight=1)

            text_widget = tk.Text(container, wrap="word", undo=False)
            text_widget.grid(row=0, column=0, sticky="nsew")
            scroll_y = ttk.Scrollbar(container, orient="vertical", command=text_widget.yview)
            scroll_y.grid(row=0, column=1, sticky="ns")
            text_widget.configure(yscrollcommand=scroll_y.set)
            text_widget.insert("1.0", message)
            text_widget.configure(state="disabled")

            buttons = ttk.Frame(container)
            buttons.grid(row=1, column=0, columnspan=2, sticky="e", pady=(10, 0))
            ok_button = ttk.Button(buttons, text="OK", command=dialog.destroy)
            ok_button.pack(side="left")

            dialog.bind("<Return>", lambda _event: dialog.destroy())
            dialog.bind("<Escape>", lambda _event: dialog.destroy())
            dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

            # Intentionally ~1.5x wider than regular text dialogs for publish details.
            self._fit_and_center_toplevel(
                dialog,
                min_width=960,
                max_width=1560,
                min_height=420,
                max_height=980,
                pad_x=140,
                pad_y=120,
            )
            ok_button.focus_set()
            self.wait_window(dialog)

        def _push_wait_cursor(self) -> str:
            try:
                previous_cursor = str(self.cget("cursor") or "")
            except tk.TclError:
                previous_cursor = ""
            try:
                self.configure(cursor="watch")
                self.update_idletasks()
            except tk.TclError:
                pass
            return previous_cursor

        def _pop_wait_cursor(self, previous_cursor: str) -> None:
            try:
                self.configure(cursor=previous_cursor)
                self.update_idletasks()
            except tk.TclError:
                pass

        def _vacuum_db_before_publish(
            self,
            db_path: Path,
            *,
            connection: sqlite3.Connection | None = None,
        ) -> None:
            con = connection
            own_connection = False
            if con is None:
                con = sqlite3.connect(str(db_path))
                own_connection = True
            try:
                con.commit()
                con.execute("VACUUM")
                if not own_connection:
                    con.commit()
            finally:
                if own_connection:
                    con.close()

        def _snapshot_data_version(self, snapshot: dict[str, object] | None) -> int | None:
            if snapshot is None:
                return None
            value = snapshot.get("data_version")
            if value is None:
                return None
            try:
                parsed = int(str(value).strip())
            except (TypeError, ValueError):
                return None
            if parsed <= 0:
                return None
            return parsed

        def _snapshot_size_bytes(self, snapshot: dict[str, object] | None) -> int | None:
            if snapshot is None:
                return None
            value = snapshot.get("size_bytes")
            if value is None:
                return None
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        def _snapshot_date_iso(self, snapshot: dict[str, object] | None) -> str | None:
            if snapshot is None:
                return None
            value = snapshot.get("date_iso")
            if value is None:
                return None
            text = str(value).strip()
            return text or None

        def _format_publish_snapshot_data_version(self, snapshot: dict[str, object] | None) -> str:
            data_version = self._snapshot_data_version(snapshot)
            return str(data_version) if data_version is not None else "-"

        def _format_publish_snapshot_size(self, snapshot: dict[str, object] | None) -> str:
            size_bytes = self._snapshot_size_bytes(snapshot)
            return f"{size_bytes} байт" if size_bytes is not None else "-"

        def _format_publish_snapshot_date(self, snapshot: dict[str, object] | None) -> str:
            date_iso = self._snapshot_date_iso(snapshot)
            return self._format_db_date_for_ui(date_iso)

        def _format_publish_size_delta(
            self,
            before_snapshot: dict[str, object] | None,
            after_snapshot: dict[str, object] | None,
        ) -> str:
            before_size = self._snapshot_size_bytes(before_snapshot)
            after_size = self._snapshot_size_bytes(after_snapshot)
            if after_size is None:
                return "-"
            if before_size is None:
                return f"+{after_size} байт"
            delta = after_size - before_size
            if delta == 0:
                return "0 байт"
            return f"{delta:+d} байт"

        def _collect_web_db_publish_plan(
            self,
            *,
            files: list[Path],
            target_dir: Path,
        ) -> list[dict[str, Any]]:
            plan: list[dict[str, Any]] = []
            for source_path in files:
                source_snapshot = self._read_db_version_snapshot(source_path)
                if source_snapshot is None:
                    raise ValueError(f"Не удалось прочитать метаданные {source_path.name}.")
                target_path = target_dir / source_path.name
                target_snapshot = self._read_db_version_snapshot(target_path)

                source_size = self._snapshot_size_bytes(source_snapshot)
                target_size = self._snapshot_size_bytes(target_snapshot)
                source_date = self._snapshot_date_iso(source_snapshot)
                target_date = self._snapshot_date_iso(target_snapshot)

                size_differs = target_snapshot is None or source_size != target_size
                date_differs = target_snapshot is None or source_date != target_date
                needs_copy = target_snapshot is None or size_differs or date_differs

                web_data_version = self._snapshot_data_version(target_snapshot)
                source_data_version = self._snapshot_data_version(source_snapshot)
                if web_data_version is not None:
                    planned_data_version = web_data_version + 1
                elif source_data_version is not None:
                    planned_data_version = source_data_version + 1
                else:
                    planned_data_version = 1

                changed_tables: list[str] = []
                if needs_copy:
                    changed_tables = self._compare_db_tables(source_path, target_path if target_path.exists() else None)

                plan.append(
                    {
                        "name": source_path.name,
                        "source_path": source_path,
                        "target_path": target_path,
                        "source_snapshot": source_snapshot,
                        "target_snapshot": target_snapshot,
                        "size_differs": size_differs,
                        "date_differs": date_differs,
                        "needs_copy": needs_copy,
                        "planned_data_version": planned_data_version,
                        "changed_tables": changed_tables,
                    }
                )

            return plan

        def _build_publish_confirmation_text(
            self,
            *,
            source_dir: Path,
            target_dir: Path,
            plan: list[dict[str, Any]],
            test_enabled_db_files: list[str],
            prepared_git_commit_message: str | None = None,
        ) -> str:
            changed = [entry for entry in plan if bool(entry["needs_copy"])]
            unchanged_count = len(plan) - len(changed)
            lines: list[str] = [
                f"Рабочая папка: {source_dir}",
                f"Папка проекта: {target_dir}",
                "",
                f"Найдено БД: {len(plan)}. Будут переписаны: {len(changed)}.",
            ]
            if unchanged_count > 0:
                lines.append(f"Без изменений: {unchanged_count}.")

            lines.append("")
            lines.append("Сравнение web/db -> рабочая БД:")

            for entry in plan:
                source_snapshot = entry["source_snapshot"]
                target_snapshot = entry["target_snapshot"]
                name = str(entry["name"])
                status = "ПЕРЕПИСАТЬ" if bool(entry["needs_copy"]) else "без изменений"
                lines.append("")
                lines.append(f"{name} [{status}]")
                if target_snapshot is None:
                    lines.append("  web/db: файл отсутствует")
                else:
                    lines.append(
                        "  web/db: "
                        f"data_version={self._format_publish_snapshot_data_version(target_snapshot)}; "
                        f"date={self._format_publish_snapshot_date(target_snapshot)}; "
                        f"size={self._format_publish_snapshot_size(target_snapshot)}"
                    )
                lines.append(
                    "  рабочая: "
                    f"data_version={self._format_publish_snapshot_data_version(source_snapshot)}; "
                    f"date={self._format_publish_snapshot_date(source_snapshot)}; "
                    f"size={self._format_publish_snapshot_size(source_snapshot)}"
                )

                if bool(entry["needs_copy"]):
                    reasons: list[str] = []
                    if bool(entry["size_differs"]):
                        reasons.append("размер")
                    if bool(entry["date_differs"]):
                        reasons.append("дата")
                    reasons_text = ", ".join(reasons) if reasons else "явное отличие"
                    lines.append(f"  причина: отличается {reasons_text}")
                    lines.append(
                        "  план data_version: "
                        f"{self._format_publish_snapshot_data_version(target_snapshot)} -> "
                        f"{entry['planned_data_version']}"
                    )
                    changed_tables = [str(name) for name in entry.get("changed_tables", [])]
                    if changed_tables:
                        lines.append("  таблицы: " + ", ".join(changed_tables))
                    else:
                        lines.append("  таблицы: только db_metadata")

            if test_enabled_db_files:
                lines.append("")
                lines.append("ВНИМАНИЕ: найдены локализованные БД с включенными тестовыми статьями:")
                for file_name in test_enabled_db_files:
                    lines.append(f"- {file_name}")

            if prepared_git_commit_message is not None:
                lines.append("")
                lines.append("Подготовленное сообщение коммита Git:")
                lines.append(prepared_git_commit_message)

            lines.append("")
            lines.append("Продолжить сохранение в проект?")
            return "\n".join(lines)

        def _build_publish_noop_text(
            self,
            *,
            target_dir: Path,
            plan: list[dict[str, Any]],
        ) -> str:
            lines: list[str] = [
                "Сохранение не требуется.",
                "",
                "Все файлы БД в рабочей папке и в web/db совпадают по размеру и дате.",
                f"Папка web/db: {target_dir}",
                "",
                "Проверенные файлы:",
            ]
            for entry in plan:
                source_snapshot = entry["source_snapshot"]
                lines.append(
                    f"- {entry['name']}: "
                    f"size={self._format_publish_snapshot_size(source_snapshot)}, "
                    f"date={self._format_publish_snapshot_date(source_snapshot)}"
                )
            return "\n".join(lines)

        def _build_publish_result_text(
            self,
            *,
            target_dir: Path,
            successful_results: list[dict[str, Any]],
            failed_results: list[str],
            manifest_error: str | None,
            git_result: dict[str, str] | None = None,
            git_error: str | None = None,
        ) -> str:
            lines: list[str] = [f"Папка web/db: {target_dir}", ""]

            if successful_results:
                lines.append(f"Успешно переписано: {len(successful_results)}")
                for result in successful_results:
                    before_snapshot = result["before_snapshot"]
                    after_snapshot = result["after_snapshot"]
                    lines.append("")
                    lines.append(f"{result['name']}:")
                    lines.append(
                        "  data_version: "
                        f"{self._format_publish_snapshot_data_version(before_snapshot)} -> "
                        f"{self._format_publish_snapshot_data_version(after_snapshot)}"
                    )
                    lines.append(
                        "  date: "
                        f"{self._format_publish_snapshot_date(before_snapshot)} -> "
                        f"{self._format_publish_snapshot_date(after_snapshot)}"
                    )
                    lines.append(
                        "  size: "
                        f"{self._format_publish_snapshot_size(before_snapshot)} -> "
                        f"{self._format_publish_snapshot_size(after_snapshot)} "
                        f"({self._format_publish_size_delta(before_snapshot, after_snapshot)})"
                    )
                    changed_tables = [str(name) for name in result.get("changed_tables", [])]
                    lines.append(
                        "  таблицы: " + (", ".join(changed_tables) if changed_tables else "только db_metadata")
                    )
            else:
                lines.append("Не удалось переписать ни одной БД.")

            if failed_results:
                lines.append("")
                lines.append(f"Ошибки ({len(failed_results)}):")
                for item in failed_results:
                    lines.append(f"- {item}")

            if manifest_error is not None:
                lines.append("")
                lines.append("manifest.json не обновлен:")
                lines.append(manifest_error)

            if git_result is not None:
                lines.append("")
                lines.append("Git-публикация:")
                lines.append(f"ветка: {git_result['branch_name']}")
                lines.append(f"remote: {git_result['remote_name']}")
                lines.append(f"коммит: {git_result['commit_hash']}")
                lines.append(git_result["subject"])
                lines.append(
                    "примечание: удаленная ветка обновлена; текущая локальная ветка в рабочем дереве не изменялась в целях безопасности"
                )

            if git_error is not None:
                lines.append("")
                lines.append("Ошибка Git-публикации:")
                lines.append(git_error)

            return "\n".join(lines)

        def _copy_to_web_db(self) -> None:
            source_dir = self.work_dir
            target_dir = self.project_root / "web" / "db"
            if not source_dir.exists():
                messagebox.showwarning("Нет папки", "Рабочая папка не существует.", parent=self)
                return

            if self.dirty:
                answer = messagebox.askyesnocancel(
                    "Несохраненные изменения",
                    "Перед сохранением в проект есть несохраненные изменения.\nСохранить сейчас?",
                    parent=self,
                )
                if answer is None:
                    return
                if answer and not self._save_all():
                    return

            files = sorted(source_dir.glob("revelation*.sqlite"))
            if not files:
                messagebox.showwarning("Нет БД", "В рабочей папке не найдены файлы revelation*.sqlite.", parent=self)
                return

            prepare_error: str | None = None
            test_enabled_db_files: list[str] = []
            publish_plan: list[dict[str, Any]] = []
            files_to_copy: list[dict[str, Any]] = []
            git_option_state: dict[str, Any] = {"enabled": False}
            prepared_git_commit_subject: str | None = None
            prepared_git_commit_body: str | None = None
            prepared_git_commit_message: str | None = None
            confirmation_text: str | None = None

            previous_cursor = self._push_wait_cursor()
            try:
                test_enabled_db_files = self._find_localized_dbs_with_enabled_tests(source_dir)
                publish_plan = self._collect_web_db_publish_plan(files=files, target_dir=target_dir)
                files_to_copy = [entry for entry in publish_plan if bool(entry["needs_copy"])]
                if files_to_copy:
                    git_option_state = self._git_publish_option_state()
                    if bool(git_option_state.get("enabled")):
                        prepared_git_commit_subject, prepared_git_commit_body = self._build_git_publish_commit_message(
                            successful_results=files_to_copy
                        )
                        prepared_git_commit_message = self._format_git_commit_message_preview(
                            subject=prepared_git_commit_subject,
                            body=prepared_git_commit_body,
                        )

                    confirmation_text = self._build_publish_confirmation_text(
                        source_dir=source_dir,
                        target_dir=target_dir,
                        plan=publish_plan,
                        test_enabled_db_files=test_enabled_db_files,
                        prepared_git_commit_message=prepared_git_commit_message,
                    )
            except (OSError, sqlite3.DatabaseError, ValueError) as exc:
                prepare_error = str(exc)
            finally:
                self._pop_wait_cursor(previous_cursor)

            if prepare_error is not None:
                messagebox.showerror(
                    "Ошибка сравнения БД",
                    (
                        "Не удалось сравнить рабочие БД и web/db.\n"
                        f"{prepare_error}"
                    ),
                    parent=self,
                )
                return

            if not files_to_copy:
                self._show_publish_result_dialog(
                    title="Сохранение не требуется",
                    message=self._build_publish_noop_text(target_dir=target_dir, plan=publish_plan),
                )
                self._set_status("Сохранение в проект не требуется: БД уже синхронизированы.")
                return

            confirmation_result = self._ask_publish_confirmation_dialog(
                title="Подтверждение сохранения",
                message=confirmation_text or "",
                git_option_state=git_option_state,
            )
            if not bool(confirmation_result.get("confirmed")):
                return

            target_dir.mkdir(parents=True, exist_ok=True)
            successful_results: list[dict[str, Any]] = []
            failed_results: list[str] = []

            for entry in files_to_copy:
                source_path = Path(entry["source_path"])
                target_path = Path(entry["target_path"])
                previous_web_snapshot = entry["target_snapshot"]
                active_connection = self._active_connection_for_db_path(source_path)
                try:
                    self._vacuum_db_before_publish(source_path, connection=active_connection)
                    updated_source_snapshot = self._touch_db_data_version(
                        source_path,
                        schema_version=self._db_schema_version_for_path(source_path),
                        connection=active_connection,
                        increment_data_version=True,
                        next_data_version=int(entry["planned_data_version"]),
                        commit=active_connection is not None,
                    )
                    if updated_source_snapshot is None:
                        raise ValueError(
                            f"Не удалось обновить db_metadata.{DB_METADATA_DATA_VERSION_KEY}."
                        )
                    shutil.copy2(source_path, target_path)
                    copied_snapshot = self._read_db_version_snapshot(target_path)
                    if copied_snapshot is None:
                        raise ValueError("Не удалось прочитать переписанный файл.")
                    successful_results.append(
                        {
                            "name": source_path.name,
                            "before_snapshot": previous_web_snapshot,
                            "after_snapshot": copied_snapshot,
                            "changed_tables": list(entry.get("changed_tables", [])),
                        }
                    )
                except (OSError, sqlite3.DatabaseError, ValueError) as exc:
                    failed_results.append(f"{source_path.name}: {exc}")

            manifest_error: str | None = None
            if successful_results:
                manifest_path = self._web_db_manifest_path(target_dir)
                manifest_db_paths = [
                    target_dir / source_path.name
                    for source_path in files
                    if (target_dir / source_path.name).exists()
                ]
                try:
                    write_web_db_manifest(manifest_path, db_paths=manifest_db_paths)
                except (OSError, sqlite3.DatabaseError, ValueError) as exc:
                    manifest_error = str(exc)

            git_publish_result: dict[str, str] | None = None
            git_publish_error: str | None = None
            if bool(confirmation_result.get("git_publish")):
                branch_name = str(confirmation_result.get("branch_name", "")).strip()
                remote_name = str(git_option_state.get("remote_name", "")).strip()
                if not branch_name or not remote_name:
                    git_publish_error = "Настройки Git-публикации заполнены не полностью."
                elif failed_results or manifest_error is not None:
                    git_publish_error = (
                        "Git-публикация пропущена, потому что сохранение БД завершилось с ошибками или manifest.json не был обновлен."
                    )
                else:
                    manifest_path = self._web_db_manifest_path(target_dir)
                    paths_to_publish = [Path(result["after_snapshot"]["path"]) for result in successful_results]
                    if manifest_path.exists():
                        paths_to_publish.append(manifest_path)
                    try:
                        git_publish_result = self._publish_files_to_git_branch(
                            branch_name=branch_name,
                            remote_name=remote_name,
                            paths_to_publish=paths_to_publish,
                            successful_results=successful_results,
                            commit_subject=prepared_git_commit_subject,
                            commit_body=prepared_git_commit_body,
                        )
                    except RuntimeError as exc:
                        git_publish_error = str(exc)

            result_text = self._build_publish_result_text(
                target_dir=target_dir,
                successful_results=successful_results,
                failed_results=failed_results,
                manifest_error=manifest_error,
                git_result=git_publish_result,
                git_error=git_publish_error,
            )

            if successful_results and not failed_results and manifest_error is None and git_publish_error is None:
                self._show_publish_result_dialog(title="Сохранение завершено", message=result_text)
                status = (
                    "Сохранение в проект завершено: "
                    f"{len(successful_results)} БД, manifest.json обновлен."
                )
                if git_publish_result is not None:
                    status += f" Commit и push выполнены в ветку {git_publish_result['branch_name']}."
                self._set_status(status)
            elif successful_results:
                self._show_publish_result_dialog(
                    title="Сохранение завершено с предупреждениями",
                    message=result_text,
                )
                status = f"Сохранено в проект: {len(successful_results)} БД"
                if failed_results:
                    status += f", ошибок: {len(failed_results)}"
                if manifest_error is not None:
                    status += ", manifest.json не обновлен"
                if git_publish_error is not None:
                    status += ", ошибка Git-публикации"
                self._set_status(status + ".")
            else:
                self._show_publish_result_dialog(title="Сохранение не выполнено", message=result_text)
                self._set_status("Не удалось сохранить БД в проект.")

        def _find_localized_dbs_with_enabled_tests(self, source_dir: Path) -> list[str]:
            found: list[str] = []
            db_files = sorted(source_dir.glob("revelation_*.sqlite"))
            for db_file in db_files:
                try:
                    with sqlite3.connect(db_file) as con:
                        rows = con.execute(
                            """
                            SELECT route
                            FROM articles
                            WHERE is_visible = 1
                            AND lower(route) LIKE '%test%'
                            ORDER BY route ASC
                            """
                        ).fetchall()
                except sqlite3.DatabaseError:
                    continue
                if rows:
                    found.append(db_file.name)
            return sorted(found)


        def _on_close(self) -> None:
            if not self._allow_switch_when_dirty():
                return
            self._close_connection()
            self.destroy()

        def _close_local_connection(self) -> None:
            if self.connection is not None:
                self.connection.close()
                self.connection = None

        def _close_connection(self) -> None:
            self._close_local_connection()
            if self.common_connection is not None:
                self.common_connection.close()
                self.common_connection = None
                self.common_db_path = None
            self._update_section_db_labels()
            self._update_ui_availability()
