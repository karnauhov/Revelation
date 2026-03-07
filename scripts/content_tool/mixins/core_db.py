from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any

from ..models import ArticleRow, PrimarySourceSummary, ResourceRow, StrongRow


class CoreDbMixin:
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
                for db_path in sorted(self.work_dir.glob("revelation_*.sqlite")):
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

            self._ensure_schema()
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
                    self._ensure_common_schema_on_connection(con)
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
                  mobile_image_path TEXT,
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
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить изменения:\n{exc}", parent=self)
                return False

            self._set_dirty(False)
            self._update_file_info()
            if not silent:
                self._set_status(status_text or f"Сохранено: {self.current_db_path.stem}")
            return True

        def _copy_to_web_db(self) -> None:
            source_dir = self.work_dir
            target_dir = self.project_root / "web" / "db"
            if not source_dir.exists():
                messagebox.showwarning("Нет папки", "Рабочая папка не существует.", parent=self)
                return

            if self.dirty:
                answer = messagebox.askyesnocancel(
                    "Несохраненные изменения",
                    "Перед копированием есть несохраненные изменения.\nСохранить сейчас?",
                    parent=self,
                )
                if answer is None:
                    return
                if answer and not self._save_all():
                    return

            test_enabled_db_files = self._find_localized_dbs_with_enabled_tests(source_dir)

            files = sorted(source_dir.glob("revelation*.sqlite"))
            if not files:
                messagebox.showwarning("Нет БД", "В рабочей папке не найдены файлы revelation*.sqlite.", parent=self)
                return

            confirmation_text = (
                f"Переписать {len(files)} файл(ов) из:\n{source_dir}\n\n"
                f"в:\n{target_dir}\n\n"
                "Это только копирование файлов в web/db."
            )
            if test_enabled_db_files:
                test_block = "\n".join(f"- {name}" for name in test_enabled_db_files)
                confirmation_text += (
                    "\n\n"
                    "ВНИМАНИЕ: найдены локализованные БД с включенными тестовыми статьями.\n"
                    "Они тоже будут опубликованы:\n"
                    f"{test_block}"
                )

            if not messagebox.askyesno(
                "Подтверждение",
                confirmation_text,
                parent=self,
            ):
                return

            target_dir.mkdir(parents=True, exist_ok=True)
            for src in files:
                shutil.copy2(src, target_dir / src.name)

            self._set_status(f"Файлы переписаны в {target_dir}. Скопировано файлов: {len(files)}")

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
