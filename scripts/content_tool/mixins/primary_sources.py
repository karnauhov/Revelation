from __future__ import annotations

import base64
import io
import json
import mimetypes
import os
import re
import sqlite3
import tempfile
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

from ..compat import Image, ImageTk
from ..dialogs.primary_source_verse_editor import PrimarySourceVerseEditorDialog
from ..dialogs.primary_source_word_editor import PrimarySourceWordEditorDialog
from ..helpers import default_primary_sources_dir, parse_verse_snippet
from ..models import FormFieldSpec, PrimarySourcePageSummary, PrimarySourceSummary


class PrimarySourcesMixin:
        def _show_form_dialog(
            self,
            title: str,
            field_specs: list[FormFieldSpec],
            *,
            initial: dict[str, object] | None = None,
            message: str = "",
        ) -> dict[str, object] | None:
            dialog = tk.Toplevel(self)
            dialog.title(title)
            dialog.transient(self)
            dialog.grab_set()
            dialog.resizable(True, True)
            dialog.minsize(520, 320)

            root = ttk.Frame(dialog, padding=12)
            root.grid(row=0, column=0, sticky="nsew")
            dialog.columnconfigure(0, weight=1)
            dialog.rowconfigure(0, weight=1)
            root.columnconfigure(1, weight=1)

            initial = initial or {}
            result: dict[str, object] | None = None
            variables: dict[str, tk.Variable] = {}
            text_widgets: dict[str, tk.Text] = {}
            current_row = 0

            if message:
                ttk.Label(
                    root,
                    text=message,
                    foreground="#5f5f5f",
                    justify="left",
                    wraplength=620,
                ).grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0, 10))
                current_row += 1

            for spec in field_specs:
                ttk.Label(root, text=spec.label).grid(
                    row=current_row,
                    column=0,
                    sticky="nw" if spec.kind == "text" else "w",
                    padx=(0, 10),
                    pady=4,
                )
                raw_value = initial.get(spec.key)
                if spec.kind == "text":
                    widget = tk.Text(root, wrap="word", height=spec.height, width=spec.width)
                    widget.grid(row=current_row, column=1, sticky="nsew", pady=4)
                    if raw_value not in (None, ""):
                        widget.insert("1.0", str(raw_value))
                    if spec.readonly:
                        widget.configure(state="disabled")
                    text_widgets[spec.key] = widget
                elif spec.kind == "check":
                    variable = tk.BooleanVar(value=bool(raw_value))
                    variables[spec.key] = variable
                    widget = ttk.Checkbutton(root, variable=variable)
                    widget.grid(row=current_row, column=1, sticky="w", pady=4)
                    if spec.readonly:
                        self._set_ttk_widget_enabled(widget, False)
                else:
                    variable = tk.StringVar(value="" if raw_value is None else str(raw_value))
                    variables[spec.key] = variable
                    if spec.kind == "combo":
                        widget = ttk.Combobox(
                            root,
                            textvariable=variable,
                            values=spec.options,
                            state="readonly" if spec.readonly else "normal",
                            width=spec.width,
                        )
                    else:
                        widget = ttk.Entry(root, textvariable=variable, width=spec.width)
                        if spec.readonly:
                            widget.configure(state="readonly")
                    widget.grid(row=current_row, column=1, sticky="ew", pady=4)
                current_row += 1

            actions = ttk.Frame(root)
            actions.grid(row=current_row, column=0, columnspan=2, sticky="e", pady=(12, 0))

            def submit() -> None:
                nonlocal result
                payload: dict[str, object] = {}
                for spec in field_specs:
                    if spec.kind == "text":
                        payload[spec.key] = text_widgets[spec.key].get("1.0", "end-1c")
                    elif spec.kind == "check":
                        payload[spec.key] = bool(variables[spec.key].get())
                    else:
                        payload[spec.key] = str(variables[spec.key].get()).strip()
                result = payload
                dialog.destroy()

            ttk.Button(actions, text="Сохранить", command=submit).pack(side="left")
            ttk.Button(actions, text="Отмена", command=dialog.destroy).pack(side="left", padx=(8, 0))

            dialog.bind("<Escape>", lambda _event: dialog.destroy())
            dialog.bind("<Control-Return>", lambda _event: submit())
            self.wait_window(dialog)
            return result

        def _parse_required_int(self, raw: object, field_label: str) -> int:
            text = str(raw).strip()
            if not text:
                raise ValueError(f"Поле '{field_label}' не может быть пустым.")
            return int(text)

        def _parse_optional_int(self, raw: object) -> int | None:
            if raw is None:
                return None
            text = str(raw).strip()
            if not text or text.lower() == "none":
                return None
            return int(text)

        def _parse_required_float(self, raw: object, field_label: str) -> float:
            text = str(raw).strip()
            if not text:
                raise ValueError(f"Поле '{field_label}' не может быть пустым.")
            return float(text.replace(",", "."))

        def _parse_json_list(self, raw: object, field_label: str) -> list[object]:
            text = str(raw).strip() or "[]"
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Некорректный JSON в поле '{field_label}': {exc}") from exc
            if not isinstance(payload, list):
                raise ValueError(f"Поле '{field_label}' должно содержать JSON-массив.")
            return payload

        def _parse_int_list_payload(self, raw: object, field_label: str) -> list[int]:
            if isinstance(raw, list):
                payload = raw
            else:
                payload = self._parse_json_list(raw, field_label)
            result: list[int] = []
            for item in payload:
                result.append(int(item))
            return result

        def _parse_word_rectangles_payload(self, raw: object) -> list[list[float]]:
            if isinstance(raw, list):
                payload = raw
            else:
                payload = self._parse_json_list(raw, "Rectangles")
            rectangles: list[list[float]] = []
            for idx, item in enumerate(payload):
                if not isinstance(item, (list, tuple)) or len(item) != 4:
                    raise ValueError(f"Rectangles: элемент #{idx} должен быть массивом из 4 чисел.")
                try:
                    x1, y1, x2, y2 = [float(value) for value in item]
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Rectangles: элемент #{idx} содержит нечисловые значения.") from exc
                left, right = sorted((max(0.0, min(1.0, x1)), max(0.0, min(1.0, x2))))
                top, bottom = sorted((max(0.0, min(1.0, y1)), max(0.0, min(1.0, y2))))
                if right - left < 1e-6 or bottom - top < 1e-6:
                    continue
                rectangles.append([left, top, right, bottom])
            return rectangles

        def _safe_json_loads(self, raw: str, fallback: object) -> object:
            try:
                return json.loads(raw or "")
            except json.JSONDecodeError:
                return fallback

        def _current_primary_source_lang(self) -> str:
            if self.current_db_path is None:
                return ""
            stem = self.current_db_path.stem
            if "_" not in stem:
                return ""
            return stem.split("_", maxsplit=1)[1].strip().lower()[:2]

        def _primary_sources_root_dir(self) -> Path:
            if self.work_dir.name.lower() == "db":
                return (self.work_dir.parent / "primary_sources").resolve()
            return default_primary_sources_dir().resolve()

        def _primary_source_local_path(self, image_path: str) -> Path:
            normalized = image_path.replace("\\", "/").lstrip("/")
            if normalized.startswith("primary_sources/"):
                normalized = normalized[len("primary_sources/"):]
            return self._primary_sources_root_dir() / Path(normalized)

        def _primary_source_page_exists_locally(self, image_path: str) -> bool:
            try:
                return self._primary_source_local_path(image_path).exists()
            except OSError:
                return False

        def _load_supabase_storage_config(self) -> tuple[str, str] | None:
            if self.supabase_storage_config_cache is not None:
                return self.supabase_storage_config_cache

            base_url = os.environ.get("SUPABASE_URL", "").strip()
            api_key = os.environ.get("SUPABASE_KEY", "").strip()
            config_path = self.project_root / "api-keys.json"
            if config_path.exists():
                try:
                    payload = json.loads(config_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    payload = {}
                if isinstance(payload, dict):
                    base_url = str(payload.get("SUPABASE_URL", base_url)).strip()
                    api_key = str(payload.get("SUPABASE_KEY", api_key)).strip()

            if not base_url:
                return None
            self.supabase_storage_config_cache = (base_url.rstrip("/"), api_key)
            return self.supabase_storage_config_cache

        def _primary_source_download_request(self, image_path: str) -> tuple[str, dict[str, str]] | None:
            normalized = image_path.replace("\\", "/").strip().lstrip("/")
            if not normalized or "/" not in normalized:
                return None
            bucket, object_path = normalized.split("/", maxsplit=1)
            config = self._load_supabase_storage_config()
            if config is None:
                return None
            base_url, api_key = config
            url = f"{base_url}/storage/v1/object/public/{bucket}/{urllib.parse.quote(object_path, safe='/')}"
            headers: dict[str, str] = {}
            if api_key:
                headers["apikey"] = api_key
                headers["Authorization"] = f"Bearer {api_key}"
            return url, headers

        def _download_primary_source_image(
            self,
            image_path: str,
            *,
            force: bool,
        ) -> tuple[str, Path, str]:
            local_path = self._primary_source_local_path(image_path)
            try:
                local_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                return "failed", local_path, f"Не удалось создать папку: {exc}"

            if local_path.exists() and not force:
                return "skipped", local_path, "Файл уже существует локально."

            request_info = self._primary_source_download_request(image_path)
            if request_info is None:
                return "failed", local_path, "Не удалось собрать URL для скачивания из storage."
            url, headers = request_info

            try:
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request, timeout=120) as response:
                    data = response.read()
            except Exception as exc:
                return "failed", local_path, f"Ошибка сети: {exc}"

            if not data:
                return "failed", local_path, "Storage вернул пустой ответ."

            try:
                local_path.write_bytes(data)
            except OSError as exc:
                return "failed", local_path, f"Не удалось записать файл: {exc}"
            return "downloaded", local_path, f"Скачано {len(data)} байт."

        def _download_primary_source_page_rows(
            self,
            page_rows: list[PrimarySourcePageSummary],
            *,
            force: bool,
            summary_title: str,
        ) -> None:
            if not page_rows:
                messagebox.showinfo("Нет страниц", "У выбранного первоисточника нет страниц.", parent=self)
                return

            downloaded: list[str] = []
            skipped: list[str] = []
            failed: list[str] = []

            for page_row in page_rows:
                status, local_path, details = self._download_primary_source_image(page_row.image_path, force=force)
                if status == "downloaded":
                    downloaded.append(f"{page_row.page_name} -> {local_path}")
                elif status == "skipped":
                    skipped.append(f"{page_row.page_name} -> {local_path}")
                else:
                    failed.append(f"{page_row.page_name}: {details}")

            selected_page_name = self.selected_primary_source_page_name
            self._load_primary_source_pages()
            if selected_page_name:
                self._select_primary_source_page(selected_page_name)
            self._refresh_primary_source_validation()

            summary_lines = [
                f"Downloaded: {len(downloaded)}",
                f"Skipped: {len(skipped)}",
                f"Failed: {len(failed)}",
                f"Root: {self._primary_sources_root_dir()}",
            ]
            if downloaded:
                summary_lines.append("")
                summary_lines.append("Downloaded files:")
                summary_lines.extend(downloaded[:12])
                if len(downloaded) > 12:
                    summary_lines.append(f"... и еще {len(downloaded) - 12}")
            if skipped:
                summary_lines.append("")
                summary_lines.append("Skipped files:")
                summary_lines.extend(skipped[:12])
                if len(skipped) > 12:
                    summary_lines.append(f"... и еще {len(skipped) - 12}")
            if failed:
                summary_lines.append("")
                summary_lines.append("Failed files:")
                summary_lines.extend(failed[:12])
                if len(failed) > 12:
                    summary_lines.append(f"... и еще {len(failed) - 12}")

            self._set_status(
                f"{summary_title}: downloaded={len(downloaded)}, skipped={len(skipped)}, failed={len(failed)}"
            )
            messagebox.showinfo(summary_title, "\n".join(summary_lines), parent=self)

        def _source_text_row_has_content(self, row: sqlite3.Row) -> bool:
            for key in (
                "title_markup",
                "date_label",
                "content_label",
                "material_text",
                "text_style_text",
                "found_text",
                "classification_text",
                "current_location_text",
            ):
                if str(row[key] or "").strip():
                    return True
            return False

        def _strip_markup_preview(self, text: str) -> str:
            plain = re.sub(r"<[^>]+>", "", text or "")
            return re.sub(r"\s+", " ", plain).strip()

        def _load_primary_source_locale_presence(self) -> None:
            presence: dict[str, set[str]] = {}
            for lang, db_path in self._localized_db_entries():
                con: sqlite3.Connection | None = None
                try:
                    con = sqlite3.connect(str(db_path))
                    con.row_factory = sqlite3.Row
                    rows = con.execute(
                        """
                        SELECT source_id,
                               title_markup,
                               date_label,
                               content_label,
                               material_text,
                               text_style_text,
                               found_text,
                               classification_text,
                               current_location_text
                        FROM primary_source_texts
                        """
                    ).fetchall()
                    presence[lang] = {
                        row["source_id"]
                        for row in rows
                        if self._source_text_row_has_content(row)
                    }
                except sqlite3.DatabaseError:
                    presence[lang] = set()
                finally:
                    if con is not None:
                        con.close()
            self.primary_source_locale_presence_by_lang = presence

        def _load_primary_sources(self) -> None:
            self.primary_sources.clear()

            if self.common_connection is None:
                self._refresh_primary_sources_tree()
                self._clear_primary_source_editor()
                return

            self._load_primary_source_locale_presence()

            localized_titles: dict[str, str] = {}
            if self.connection is not None:
                try:
                    rows = self.connection.execute(
                        "SELECT source_id, title_markup FROM primary_source_texts"
                    ).fetchall()
                    localized_titles = {
                        row["source_id"]: row["title_markup"] or ""
                        for row in rows
                    }
                except sqlite3.DatabaseError:
                    localized_titles = {}

            try:
                rows = self.common_connection.execute(
                    """
                    SELECT
                      ps.id,
                      ps.family,
                      ps.number,
                      ps.group_kind,
                      ps.sort_order,
                      ps.can_show_images,
                      ps.preview_resource_key,
                      (
                        SELECT COUNT(*)
                        FROM primary_source_pages p
                        WHERE p.source_id = ps.id
                      ) AS pages_count,
                      (
                        SELECT COUNT(*)
                        FROM primary_source_words w
                        WHERE w.source_id = ps.id
                      ) AS words_count,
                      (
                        SELECT COUNT(*)
                        FROM primary_source_verses v
                        WHERE v.source_id = ps.id
                      ) AS verse_rows_count
                    FROM primary_sources ps
                    ORDER BY ps.id COLLATE NOCASE ASC
                    """
                ).fetchall()
            except sqlite3.DatabaseError:
                rows = []

            for row in rows:
                source_id = row["id"]
                self.primary_sources.append(
                    PrimarySourceSummary(
                        id=source_id,
                        family=row["family"],
                        number=int(row["number"]),
                        group_kind=row["group_kind"],
                        sort_order=int(row["sort_order"]),
                        pages_count=int(row["pages_count"] or 0),
                        words_count=int(row["words_count"] or 0),
                        verse_rows_count=int(row["verse_rows_count"] or 0),
                        can_show_images=bool(row["can_show_images"]),
                        preview_resource_key=row["preview_resource_key"] or "",
                        title_preview=self._strip_markup_preview(localized_titles.get(source_id, "")),
                        locale_flags={
                            lang: source_id in ids
                            for lang, ids in self.primary_source_locale_presence_by_lang.items()
                        },
                    )
                )

            self._refresh_primary_sources_tree()
            if self.selected_primary_source_id:
                self._select_primary_source_by_id(self.selected_primary_source_id)
            elif self.primary_sources:
                self._select_primary_source_by_id(self.primary_sources[0].id)
            else:
                self._clear_primary_source_editor()

        def _refresh_primary_sources_tree(self) -> None:
            if not hasattr(self, "primary_sources_tree"):
                return
            self.primary_sources_tree.delete(*self.primary_sources_tree.get_children())
            for row in self.primary_sources:
                locale = row.locale_flags
                self.primary_sources_tree.insert(
                    "",
                    "end",
                    iid=row.id,
                    values=(
                        row.id,
                        row.title_preview or row.id,
                        row.group_kind,
                        row.pages_count,
                        row.words_count,
                        row.verse_rows_count,
                        "✓" if locale.get("en") else "",
                        "✓" if locale.get("es") else "",
                        "✓" if locale.get("uk") else "",
                        "✓" if locale.get("ru") else "",
                    ),
                )

        def _select_primary_source_by_id(self, source_id: str, *, reload: bool = True) -> None:
            if not hasattr(self, "primary_sources_tree"):
                return
            if not self.primary_sources_tree.exists(source_id):
                return
            self.primary_sources_tree.selection_set(source_id)
            self.primary_sources_tree.focus(source_id)
            self.primary_sources_tree.see(source_id)
            self.selected_primary_source_id = source_id
            if reload:
                self._reload_selected_primary_source()

        def _on_primary_source_selected(self, _event: object) -> None:
            selection = self.primary_sources_tree.selection()
            if not selection:
                self.selected_primary_source_id = None
                self._clear_primary_source_editor()
                return
            self.selected_primary_source_id = str(selection[0])
            self._reload_selected_primary_source()

        def _clear_primary_source_editor(self) -> None:
            self.selected_primary_source_id = None
            self.selected_primary_source_page_name = None
            self.selected_primary_source_link_index = None
            self.selected_primary_source_attribution_index = None
            self.selected_primary_source_page_index = None
            self.selected_primary_source_word_index = None
            self.selected_primary_source_verse_index = None
            self.primary_source_id_var.set("")
            self.primary_source_family_var.set("")
            self.primary_source_number_var.set("0")
            self.primary_source_group_kind_var.set("fragment")
            self.primary_source_sort_order_var.set("0")
            self.primary_source_verses_count_var.set("0")
            self.primary_source_preview_key_var.set("")
            self.primary_source_default_max_scale_var.set("3.0")
            self.primary_source_can_show_images_var.set(True)
            self.primary_source_images_are_monochrome_var.set(False)
            for key in (
                "title_markup",
                "date_label",
                "content_label",
                "material_text",
                "text_style_text",
                "found_text",
                "classification_text",
                "current_location_text",
            ):
                self._set_primary_source_localized_field(key, "")
            if self.primary_source_notes_text is not None:
                self._set_text_widget_content(self.primary_source_notes_text, "")
            self._refresh_primary_source_preview_options()
            self.primary_source_preview_image = None
            if hasattr(self, "primary_source_preview_label"):
                self.primary_source_preview_label.configure(
                    image="",
                    text="Предпросмотр пока недоступен.",
                )
            self.primary_source_link_rows.clear()
            self.primary_source_attribution_rows.clear()
            self.primary_source_pages.clear()
            self.primary_source_word_rows.clear()
            self.primary_source_verse_rows.clear()
            self._refresh_primary_source_links_tree()
            self._refresh_primary_source_attributions_tree()
            self._refresh_primary_source_pages_tree()
            self._refresh_primary_source_words_tree()
            self._refresh_primary_source_verses_tree()
            self._primary_source_last_validation_log = ""
            self.primary_source_page_info_var.set("Страница не выбрана.")

        def _refresh_primary_source_preview_options(self) -> None:
            if not hasattr(self, "combo_primary_source_preview_key"):
                return
            image_keys = sorted(
                {
                    row.key
                    for row in self.common_resources
                    if self._is_graphic_resource(row.mime_type, row.file_name)
                }
            )
            current = self.primary_source_preview_key_var.get().strip()
            if current and current not in image_keys:
                image_keys.append(current)
                image_keys.sort()
            self.combo_primary_source_preview_key["values"] = ["", *image_keys]

        def _on_primary_source_preview_selected(self, _event: object | None = None) -> None:
            self._render_primary_source_preview()
            self._refresh_primary_source_validation()

        def _refresh_primary_source_locale_db_options(self) -> None:
            entries = [(lang, path) for lang, path in self._localized_db_entries() if path.exists()]
            self.primary_source_locale_db_paths_by_lang = {lang: path for lang, path in entries}
            values = [lang for lang, _path in entries]
            if hasattr(self, "combo_primary_source_locale_db"):
                self.combo_primary_source_locale_db["values"] = values

            current_lang = self.primary_source_locale_db_var.get().strip().lower()
            if current_lang in self.primary_source_locale_db_paths_by_lang:
                return

            preferred_lang = self._current_primary_source_lang()
            if preferred_lang and preferred_lang in self.primary_source_locale_db_paths_by_lang:
                self.primary_source_locale_db_var.set(preferred_lang)
            elif values:
                self.primary_source_locale_db_var.set(values[0])
            else:
                self.primary_source_locale_db_var.set("")

        def _selected_primary_source_locale_db_path(self) -> Path | None:
            lang = self.primary_source_locale_db_var.get().strip().lower()
            path = self.primary_source_locale_db_paths_by_lang.get(lang)
            if path is None or not path.exists():
                return None
            return path

        def _set_primary_source_localized_field(self, key: str, value: str) -> None:
            text_value = value or ""
            variable = getattr(self, f"primary_source_{key}_var", None)
            if variable is not None:
                variable.set(text_value)
            widget = self.primary_source_localized_text_widgets.get(key)
            if widget is not None:
                self._set_text_widget_content(widget, text_value)

        def _primary_source_localized_field_value(self, key: str) -> str:
            widget = self.primary_source_localized_text_widgets.get(key)
            if widget is not None:
                return self._text_widget_content(widget).strip()
            variable = getattr(self, f"primary_source_{key}_var", None)
            if variable is None:
                return ""
            return str(variable.get()).strip()

        def _load_primary_source_common_row(self, source_id: str) -> sqlite3.Row | None:
            if not source_id or self.common_connection is None:
                return None
            try:
                return self.common_connection.execute(
                    "SELECT * FROM primary_sources WHERE id = ? LIMIT 1",
                    (source_id,),
                ).fetchone()
            except sqlite3.DatabaseError:
                return None

        def _apply_primary_source_common_row(self, common_row: sqlite3.Row) -> None:
            self.primary_source_id_var.set(common_row["id"])
            self.primary_source_family_var.set(common_row["family"] or "")
            self.primary_source_number_var.set(str(int(common_row["number"] or 0)))
            self.primary_source_group_kind_var.set(common_row["group_kind"] or "fragment")
            self.primary_source_sort_order_var.set(str(int(common_row["sort_order"] or 0)))
            self.primary_source_verses_count_var.set(str(int(common_row["verses_count"] or 0)))
            self.primary_source_preview_key_var.set(common_row["preview_resource_key"] or "")
            self.primary_source_default_max_scale_var.set(str(float(common_row["default_max_scale"] or 3.0)))
            self.primary_source_can_show_images_var.set(bool(common_row["can_show_images"]))
            self.primary_source_images_are_monochrome_var.set(bool(common_row["images_are_monochrome"]))
            if self.primary_source_notes_text is not None:
                self._set_text_widget_content(self.primary_source_notes_text, common_row["notes"] or "")
            self._refresh_primary_source_preview_options()
            self._render_primary_source_preview()

        def _load_primary_source_localized_row(self, source_id: str, db_path: Path | None) -> sqlite3.Row | None:
            if not source_id or db_path is None:
                return None
            con: sqlite3.Connection | None = None
            try:
                con = sqlite3.connect(str(db_path))
                con.row_factory = sqlite3.Row
                return con.execute(
                    "SELECT * FROM primary_source_texts WHERE source_id = ? LIMIT 1",
                    (source_id,),
                ).fetchone()
            except sqlite3.DatabaseError:
                return None
            finally:
                if con is not None:
                    con.close()

        def _apply_primary_source_localized_row(self, localized_row: sqlite3.Row | None) -> None:
            def localized_value(key: str) -> str:
                if localized_row is None:
                    return ""
                return str(localized_row[key] or "")

            for key in (
                "title_markup",
                "date_label",
                "content_label",
                "material_text",
                "text_style_text",
                "found_text",
                "classification_text",
                "current_location_text",
            ):
                self._set_primary_source_localized_field(key, localized_value(key))

        def _reload_selected_primary_source_common_fields(self) -> None:
            source_id = self.selected_primary_source_id
            common_row = self._load_primary_source_common_row(source_id or "")
            if common_row is None:
                if source_id is None:
                    self._clear_primary_source_editor()
                return
            self._apply_primary_source_common_row(common_row)
            self._refresh_primary_source_validation()

        def _reload_selected_primary_source_localized_fields(self) -> None:
            source_id = self.selected_primary_source_id
            db_path = self._selected_primary_source_locale_db_path()
            localized_row = self._load_primary_source_localized_row(source_id or "", db_path)
            self._apply_primary_source_localized_row(localized_row)

        def _on_primary_source_locale_db_selected(self, _event: object | None = None) -> None:
            self._reload_selected_primary_source_localized_fields()

        def _reload_selected_primary_source(self) -> None:
            source_id = self.selected_primary_source_id
            if not source_id or self.common_connection is None:
                self._clear_primary_source_editor()
                return

            common_row = self._load_primary_source_common_row(source_id)
            if common_row is None:
                self._clear_primary_source_editor()
                return

            self._apply_primary_source_common_row(common_row)
            self._reload_selected_primary_source_localized_fields()
            self._load_primary_source_links()
            self._load_primary_source_attributions()
            previous_page_name = self.selected_primary_source_page_name
            self._load_primary_source_pages()
            if previous_page_name and any(row.page_name == previous_page_name for row in self.primary_source_pages):
                self._select_primary_source_page(previous_page_name)
            elif self.primary_source_pages:
                self._select_primary_source_page(self.primary_source_pages[0].page_name)
            else:
                self.selected_primary_source_page_name = None
                self.primary_source_word_rows.clear()
                self.primary_source_verse_rows.clear()
                self._refresh_primary_source_words_tree()
                self._refresh_primary_source_verses_tree()
                self.primary_source_page_info_var.set("У выбранного первоисточника нет страниц.")
            self._refresh_primary_source_validation()

        def _render_primary_source_preview(self) -> None:
            if not hasattr(self, "primary_source_preview_label"):
                return
            key = self.primary_source_preview_key_var.get().strip()
            payload = self._load_resource_payload_by_key(key)
            self.primary_source_preview_image = None
            self.primary_source_preview_label.configure(image="")
            if payload is None:
                self.primary_source_preview_label.configure(
                    text="Ресурс предпросмотра не найден.",
                )
                return
            data, mime, file_name = payload
            preview_data = data
            error_message: str | None = None
            if self._is_graphic_resource(mime, file_name):
                lower_mime = mime.lower()
                is_svg = lower_mime.startswith("image/svg") or Path(file_name).suffix.lower() == ".svg"
                if is_svg:
                    converted, error_message = self._convert_svg_to_png_for_preview(data)
                    if converted is not None:
                        preview_data = converted
                try:
                    if Image is not None and ImageTk is not None:
                        with Image.open(io.BytesIO(preview_data)) as pil_image:
                            image_copy = pil_image.copy()
                            resampling = (
                                Image.Resampling.LANCZOS
                                if hasattr(Image, "Resampling")
                                else Image.LANCZOS
                            )
                            image_copy.thumbnail((420, 260), resampling)
                        self.primary_source_preview_image = ImageTk.PhotoImage(image_copy)
                        self.primary_source_preview_label.configure(
                            image=self.primary_source_preview_image,
                            text="",
                        )
                        return
                    encoded = base64.b64encode(preview_data).decode("ascii")
                    self.primary_source_preview_image = tk.PhotoImage(data=encoded)
                    self.primary_source_preview_label.configure(
                        image=self.primary_source_preview_image,
                        text="",
                    )
                    return
                except Exception:
                    pass
                if error_message:
                    self.primary_source_preview_label.configure(text=error_message)
                else:
                    self.primary_source_preview_label.configure(
                        text="Не удалось показать предпросмотр.",
                    )
                return
            self.primary_source_preview_label.configure(
                text=f"Ресурс найден, но это не изображение: {mime or file_name}",
            )

        def _load_primary_source_links(self) -> None:
            self.primary_source_link_rows.clear()
            source_id = self.selected_primary_source_id
            if not source_id or self.common_connection is None:
                self._refresh_primary_source_links_tree()
                return
            try:
                self.primary_source_link_rows = self.common_connection.execute(
                    """
                    SELECT source_id, link_id, sort_order, link_role, url
                    FROM primary_source_links
                    WHERE source_id = ?
                    ORDER BY sort_order ASC, link_id ASC
                    """,
                    (source_id,),
                ).fetchall()
            except sqlite3.DatabaseError:
                self.primary_source_link_rows = []
            self._refresh_primary_source_links_tree()

        def _current_primary_source_link_titles(self) -> dict[str, str]:
            source_id = self.selected_primary_source_id
            if not source_id or self.connection is None:
                return {}
            try:
                rows = self.connection.execute(
                    """
                    SELECT link_id, title
                    FROM primary_source_link_texts
                    WHERE source_id = ?
                    """
                    ,
                    (source_id,),
                ).fetchall()
            except sqlite3.DatabaseError:
                return {}
            return {row["link_id"]: row["title"] or "" for row in rows}

        def _link_localized_titles_by_lang(self, link_id: str) -> dict[str, str]:
            source_id = self.selected_primary_source_id
            if not source_id or not link_id:
                return {}
            titles: dict[str, str] = {}
            for lang, db_path in self._localized_db_entries():
                if not db_path.exists():
                    continue
                con: sqlite3.Connection | None = None
                try:
                    con = sqlite3.connect(str(db_path))
                    con.row_factory = sqlite3.Row
                    row = con.execute(
                        """
                        SELECT title
                        FROM primary_source_link_texts
                        WHERE source_id = ?
                          AND link_id = ?
                        LIMIT 1
                        """,
                        (source_id, link_id),
                    ).fetchone()
                except sqlite3.DatabaseError:
                    row = None
                finally:
                    if con is not None:
                        con.close()
                if row is not None:
                    titles[lang] = str(row["title"] or "")
            return titles

        def _refresh_primary_source_links_tree(self) -> None:
            if not hasattr(self, "primary_source_links_tree"):
                return
            self.primary_source_links_tree.delete(*self.primary_source_links_tree.get_children())
            for idx, row in enumerate(self.primary_source_link_rows):
                self.primary_source_links_tree.insert(
                    "",
                    "end",
                    iid=str(idx),
                    values=(
                        row["link_id"],
                        int(row["sort_order"] or 0),
                        row["link_role"],
                        row["url"],
                    ),
                )

        def _load_primary_source_attributions(self) -> None:
            self.primary_source_attribution_rows.clear()
            source_id = self.selected_primary_source_id
            if not source_id or self.common_connection is None:
                self._refresh_primary_source_attributions_tree()
                return
            try:
                self.primary_source_attribution_rows = self.common_connection.execute(
                    """
                    SELECT source_id, attribution_id, sort_order, text, url
                    FROM primary_source_attributions
                    WHERE source_id = ?
                    ORDER BY sort_order ASC, attribution_id ASC
                    """,
                    (source_id,),
                ).fetchall()
            except sqlite3.DatabaseError:
                self.primary_source_attribution_rows = []
            self._refresh_primary_source_attributions_tree()

        def _refresh_primary_source_attributions_tree(self) -> None:
            if not hasattr(self, "primary_source_attributions_tree"):
                return
            self.primary_source_attributions_tree.delete(*self.primary_source_attributions_tree.get_children())
            for idx, row in enumerate(self.primary_source_attribution_rows):
                self.primary_source_attributions_tree.insert(
                    "",
                    "end",
                    iid=str(idx),
                    values=(
                        row["attribution_id"],
                        int(row["sort_order"] or 0),
                        row["text"],
                        row["url"],
                    ),
                )

        def _load_primary_source_pages(self) -> None:
            self.primary_source_pages.clear()
            source_id = self.selected_primary_source_id
            if not source_id or self.common_connection is None:
                self._refresh_primary_source_pages_tree()
                return
            try:
                rows = self.common_connection.execute(
                    """
                    SELECT
                      p.source_id,
                      p.page_name,
                      p.sort_order,
                      p.content_ref,
                      p.image_path,
                      (
                        SELECT COUNT(*)
                        FROM primary_source_words w
                        WHERE w.source_id = p.source_id
                          AND w.page_name = p.page_name
                      ) AS words_count,
                      (
                        SELECT COUNT(*)
                        FROM primary_source_verses v
                        WHERE v.source_id = p.source_id
                          AND v.page_name = p.page_name
                      ) AS verse_rows_count
                    FROM primary_source_pages p
                    WHERE p.source_id = ?
                    ORDER BY p.sort_order ASC, p.page_name ASC
                    """,
                    (source_id,),
                ).fetchall()
            except sqlite3.DatabaseError:
                rows = []
            self.primary_source_pages = [
                PrimarySourcePageSummary(
                    source_id=row["source_id"],
                    page_name=row["page_name"],
                    sort_order=int(row["sort_order"] or 0),
                    content_ref=row["content_ref"] or "",
                    image_path=row["image_path"] or "",
                    words_count=int(row["words_count"] or 0),
                    verse_rows_count=int(row["verse_rows_count"] or 0),
                    local_exists=self._primary_source_page_exists_locally(row["image_path"] or ""),
                )
                for row in rows
            ]
            self._refresh_primary_source_pages_tree()

        def _refresh_primary_source_pages_tree(self) -> None:
            if not hasattr(self, "primary_source_pages_tree"):
                return
            self.primary_source_pages_tree.delete(*self.primary_source_pages_tree.get_children())
            for row in self.primary_source_pages:
                self.primary_source_pages_tree.insert(
                    "",
                    "end",
                    iid=row.page_name,
                    tags=("local_exists" if row.local_exists else "local_missing",),
                    values=(
                        row.page_name,
                        row.sort_order,
                        row.content_ref,
                        row.image_path,
                        "Да" if row.local_exists else "Нет",
                    ),
                )

        def _select_primary_source_page(self, page_name: str) -> None:
            if not hasattr(self, "primary_source_pages_tree"):
                return
            if not self.primary_source_pages_tree.exists(page_name):
                return
            self.primary_source_pages_tree.selection_set(page_name)
            self.primary_source_pages_tree.focus(page_name)
            self.primary_source_pages_tree.see(page_name)
            self.selected_primary_source_page_name = page_name
            self._load_primary_source_page_children()

        def _on_primary_source_page_selected(self, _event: object) -> None:
            selection = self.primary_source_pages_tree.selection()
            if not selection:
                self.selected_primary_source_page_name = None
                self.primary_source_word_rows.clear()
                self.primary_source_verse_rows.clear()
                self._refresh_primary_source_words_tree()
                self._refresh_primary_source_verses_tree()
                self.primary_source_page_info_var.set("Страница не выбрана.")
                return
            self.selected_primary_source_page_name = str(selection[0])
            self._load_primary_source_page_children()

        def _load_primary_source_page_children(self) -> None:
            source_id = self.selected_primary_source_id
            page_name = self.selected_primary_source_page_name
            if not source_id or not page_name or self.common_connection is None:
                self.primary_source_word_rows.clear()
                self.primary_source_verse_rows.clear()
                self._refresh_primary_source_words_tree()
                self._refresh_primary_source_verses_tree()
                return
            try:
                self.primary_source_word_rows = self.common_connection.execute(
                    """
                    SELECT *
                    FROM primary_source_words
                    WHERE source_id = ?
                      AND page_name = ?
                    ORDER BY word_index ASC
                    """,
                    (source_id, page_name),
                ).fetchall()
                self.primary_source_verse_rows = self.common_connection.execute(
                    """
                    SELECT *
                    FROM primary_source_verses
                    WHERE source_id = ?
                      AND page_name = ?
                    ORDER BY verse_index ASC
                    """,
                    (source_id, page_name),
                ).fetchall()
            except sqlite3.DatabaseError:
                self.primary_source_word_rows = []
                self.primary_source_verse_rows = []
            self._refresh_primary_source_words_tree()
            self._refresh_primary_source_verses_tree()
            page_row = next((row for row in self.primary_source_pages if row.page_name == page_name), None)
            if page_row is None:
                self.primary_source_page_info_var.set("Страница не выбрана.")
                return
            local_path = self._primary_source_local_path(page_row.image_path)
            self.primary_source_page_info_var.set(
                f"{page_row.content_ref} | {page_row.image_path} | local: {local_path}"
            )

        def _refresh_primary_source_words_tree(self) -> None:
            if not hasattr(self, "primary_source_words_tree"):
                return
            self.primary_source_words_tree.delete(*self.primary_source_words_tree.get_children())
            for idx, row in enumerate(self.primary_source_word_rows):
                rectangles = self._safe_json_loads(row["rectangles_json"] or "[]", [])
                rect_count = len(rectangles) if isinstance(rectangles, list) else 0
                self.primary_source_words_tree.insert(
                    "",
                    "end",
                    iid=str(idx),
                    values=(
                        int(row["word_index"] or 0),
                        row["text"] or "",
                        "" if row["strong_number"] is None else row["strong_number"],
                        rect_count,
                    ),
                )

        def _refresh_primary_source_verses_tree(self) -> None:
            if not hasattr(self, "primary_source_verses_tree"):
                return
            self.primary_source_verses_tree.delete(*self.primary_source_verses_tree.get_children())
            for idx, row in enumerate(self.primary_source_verse_rows):
                word_indexes = self._safe_json_loads(row["word_indexes_json"] or "[]", [])
                self.primary_source_verses_tree.insert(
                    "",
                    "end",
                    iid=str(idx),
                    values=(
                        int(row["verse_index"] or 0),
                        f"{int(row['chapter_number'] or 0)}:{int(row['verse_number'] or 0)}",
                        len(word_indexes) if isinstance(word_indexes, list) else 0,
                    ),
                )

        def _on_primary_source_link_selected(self, _event: object) -> None:
            selection = self.primary_source_links_tree.selection()
            self.selected_primary_source_link_index = int(selection[0]) if selection else None

        def _on_primary_source_attribution_selected(self, _event: object) -> None:
            selection = self.primary_source_attributions_tree.selection()
            self.selected_primary_source_attribution_index = int(selection[0]) if selection else None

        def _on_primary_source_word_selected(self, _event: object) -> None:
            selection = self.primary_source_words_tree.selection()
            self.selected_primary_source_word_index = int(selection[0]) if selection else None

        def _on_primary_source_verse_selected(self, _event: object) -> None:
            selection = self.primary_source_verses_tree.selection()
            self.selected_primary_source_verse_index = int(selection[0]) if selection else None

        def _select_primary_source_word_by_value(self, word_index: int) -> None:
            if not hasattr(self, "primary_source_words_tree"):
                return
            for idx, row in enumerate(self.primary_source_word_rows):
                if int(row["word_index"] or 0) != word_index:
                    continue
                iid = str(idx)
                if self.primary_source_words_tree.exists(iid):
                    self.primary_source_words_tree.selection_set(iid)
                    self.primary_source_words_tree.focus(iid)
                    self.primary_source_words_tree.see(iid)
                    self.selected_primary_source_word_index = idx
                return

        def _select_primary_source_verse_by_value(self, verse_index: int) -> None:
            if not hasattr(self, "primary_source_verses_tree"):
                return
            for idx, row in enumerate(self.primary_source_verse_rows):
                if int(row["verse_index"] or 0) != verse_index:
                    continue
                iid = str(idx)
                if self.primary_source_verses_tree.exists(iid):
                    self.primary_source_verses_tree.selection_set(iid)
                    self.primary_source_verses_tree.focus(iid)
                    self.primary_source_verses_tree.see(iid)
                    self.selected_primary_source_verse_index = idx
                return

        def _refresh_primary_source_validation(self) -> None:
            source_id = self.selected_primary_source_id
            if not source_id:
                self._primary_source_last_validation_log = ""
                return

            warnings: list[str] = []
            preview_key = self.primary_source_preview_key_var.get().strip()
            if not preview_key:
                warnings.append("Не заполнен preview_resource_key.")
            elif self._load_resource_payload_by_key(preview_key) is None:
                warnings.append(f"Preview ресурс '{preview_key}' отсутствует в common_resources.")

            def collect_duplicate_sort(rows: list[sqlite3.Row], label: str, key_name: str) -> None:
                counts: dict[int, list[str]] = {}
                for row in rows:
                    sort_order = int(row["sort_order"] or 0)
                    counts.setdefault(sort_order, []).append(str(row[key_name]))
                for sort_order, ids in counts.items():
                    if len(ids) > 1:
                        warnings.append(
                            f"{label}: конфликт sort_order={sort_order} для {', '.join(ids)}."
                        )

            collect_duplicate_sort(self.primary_source_link_rows, "Ссылки", "link_id")
            collect_duplicate_sort(self.primary_source_attribution_rows, "Атрибуции", "attribution_id")

            page_sort_counts: dict[int, list[str]] = {}
            page_names: set[str] = set()
            for page in self.primary_source_pages:
                if not page.image_path.strip():
                    warnings.append(f"Страница '{page.page_name}' не содержит image_path.")
                if page.page_name in page_names:
                    warnings.append(f"Дублирующееся имя страницы: {page.page_name}.")
                page_names.add(page.page_name)
                page_sort_counts.setdefault(page.sort_order, []).append(page.page_name)
            for sort_order, names in page_sort_counts.items():
                if len(names) > 1:
                    warnings.append(f"Страницы: конфликт sort_order={sort_order} для {', '.join(names)}.")

            for word_row in self.primary_source_word_rows:
                for key, label in [
                    ("missing_char_indexes_json", "missing_char_indexes_json"),
                    ("rectangles_json", "rectangles_json"),
                ]:
                    try:
                        payload = json.loads(word_row[key] or "[]")
                    except json.JSONDecodeError as exc:
                        warnings.append(
                            f"Страница {word_row['page_name']}, word {word_row['word_index']}: "
                            f"некорректный JSON в {label} ({exc.msg})."
                        )
                        continue
                    if not isinstance(payload, list):
                        warnings.append(
                            f"Страница {word_row['page_name']}, word {word_row['word_index']}: "
                            f"{label} должен быть JSON-массивом."
                        )

            for verse_row in self.primary_source_verse_rows:
                for key, label in [
                    ("word_indexes_json", "word_indexes_json"),
                    ("contours_json", "contours_json"),
                ]:
                    try:
                        payload = json.loads(verse_row[key] or "[]")
                    except json.JSONDecodeError as exc:
                        warnings.append(
                            f"Страница {verse_row['page_name']}, verse {verse_row['verse_index']}: "
                            f"некорректный JSON в {label} ({exc.msg})."
                        )
                        continue
                    if not isinstance(payload, list):
                        warnings.append(
                            f"Страница {verse_row['page_name']}, verse {verse_row['verse_index']}: "
                            f"{label} должен быть JSON-массивом."
                        )

            if not warnings:
                self._primary_source_last_validation_log = ""
                return

            message = f"Валидация '{source_id}': " + "; ".join(warnings)
            if getattr(self, "_primary_source_last_validation_log", "") == message:
                return
            self._primary_source_last_validation_log = message
            self._set_status(message)

        def _ensure_primary_source_section_ready(self) -> bool:
            if self.common_connection is None or self.common_db_path is None:
                messagebox.showwarning("Нет общей БД", "Общая БД недоступна.", parent=self)
                return False
            if self.connection is None or self.current_db_path is None:
                messagebox.showwarning("Нет локализованной БД", "Локализованная БД недоступна.", parent=self)
                return False
            return True

        def _ensure_primary_source_common_ready(self) -> bool:
            if self.common_connection is None or self.common_db_path is None:
                messagebox.showwarning("Нет общей БД", "Общая БД недоступна.", parent=self)
                return False
            return True

        def _ensure_selected_primary_source_locale_db_ready(self) -> Path | None:
            db_path = self._selected_primary_source_locale_db_path()
            if db_path is None:
                messagebox.showwarning(
                    "Нет локализованной БД",
                    "Выберите локализованную БД из списка.",
                    parent=self,
                )
                return None
            return db_path

        def _ensure_primary_source_localized_schema_on_connection(self, connection: sqlite3.Connection) -> None:
            connection.executescript(
                """
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
                """
            )

        def _selected_primary_source_link_row(self) -> sqlite3.Row | None:
            index = self.selected_primary_source_link_index
            if index is None or index < 0 or index >= len(self.primary_source_link_rows):
                return None
            return self.primary_source_link_rows[index]

        def _selected_primary_source_attribution_row(self) -> sqlite3.Row | None:
            index = self.selected_primary_source_attribution_index
            if index is None or index < 0 or index >= len(self.primary_source_attribution_rows):
                return None
            return self.primary_source_attribution_rows[index]

        def _selected_primary_source_page_row(self) -> PrimarySourcePageSummary | None:
            page_name = self.selected_primary_source_page_name
            if not page_name:
                return None
            return next((row for row in self.primary_source_pages if row.page_name == page_name), None)

        def _selected_primary_source_word_row(self) -> sqlite3.Row | None:
            index = self.selected_primary_source_word_index
            if index is None or index < 0 or index >= len(self.primary_source_word_rows):
                return None
            return self.primary_source_word_rows[index]

        def _selected_primary_source_verse_row(self) -> sqlite3.Row | None:
            index = self.selected_primary_source_verse_index
            if index is None or index < 0 or index >= len(self.primary_source_verse_rows):
                return None
            return self.primary_source_verse_rows[index]

        def _save_primary_source_common_metadata(self) -> None:
            if not self._ensure_primary_source_common_ready():
                return

            source_id = self.primary_source_id_var.get().strip()
            if not source_id:
                messagebox.showwarning("Нет источника", "Сначала выберите или создайте первоисточник.", parent=self)
                return

            try:
                number = self._parse_required_int(self.primary_source_number_var.get(), "Индекс")
                sort_order = self._parse_required_int(self.primary_source_sort_order_var.get(), "Порядок")
                verses_count = self._parse_required_int(self.primary_source_verses_count_var.get(), "Кол-во стихов")
                default_max_scale = self._parse_required_float(
                    self.primary_source_default_max_scale_var.get().replace(",", "."),
                    "Max масштаб",
                )
            except ValueError as exc:
                messagebox.showwarning("Ошибка данных", str(exc), parent=self)
                return

            notes = self._text_widget_content(self.primary_source_notes_text) if self.primary_source_notes_text else ""
            preview_key = self.primary_source_preview_key_var.get().strip()
            if not preview_key:
                preview_key = f"primary_sources/previews/{source_id}.png"
                self.primary_source_preview_key_var.set(preview_key)

            try:
                with self.common_connection:
                    self.common_connection.execute(
                        """
                        INSERT INTO primary_sources(
                          id,
                          family,
                          number,
                          group_kind,
                          sort_order,
                          verses_count,
                          preview_resource_key,
                          default_max_scale,
                          can_show_images,
                          images_are_monochrome,
                          notes
                        )
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                          family = excluded.family,
                          number = excluded.number,
                          group_kind = excluded.group_kind,
                          sort_order = excluded.sort_order,
                          verses_count = excluded.verses_count,
                          preview_resource_key = excluded.preview_resource_key,
                          default_max_scale = excluded.default_max_scale,
                          can_show_images = excluded.can_show_images,
                          images_are_monochrome = excluded.images_are_monochrome,
                          notes = excluded.notes
                        """,
                        (
                            source_id,
                            self.primary_source_family_var.get().strip(),
                            number,
                            self.primary_source_group_kind_var.get().strip(),
                            sort_order,
                            verses_count,
                            preview_key,
                            default_max_scale,
                            1 if self.primary_source_can_show_images_var.get() else 0,
                            1 if self.primary_source_images_are_monochrome_var.get() else 0,
                            notes,
                        ),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить источник:\n{exc}", parent=self)
                return

            self._load_primary_sources()
            self._select_primary_source_by_id(source_id)
            self._set_status(f"Первоисточник '{source_id}' сохранен.")

        def _save_primary_source_localized_fields(self) -> None:
            source_id = self.primary_source_id_var.get().strip()
            if not source_id:
                messagebox.showwarning("Нет источника", "Сначала выберите первоисточник.", parent=self)
                return

            db_path = self._ensure_selected_primary_source_locale_db_ready()
            if db_path is None:
                return

            localized_values = {
                "title_markup": self._primary_source_localized_field_value("title_markup"),
                "date_label": self._primary_source_localized_field_value("date_label"),
                "content_label": self._primary_source_localized_field_value("content_label"),
                "material_text": self._primary_source_localized_field_value("material_text"),
                "text_style_text": self._primary_source_localized_field_value("text_style_text"),
                "found_text": self._primary_source_localized_field_value("found_text"),
                "classification_text": self._primary_source_localized_field_value("classification_text"),
                "current_location_text": self._primary_source_localized_field_value("current_location_text"),
            }
            con: sqlite3.Connection | None = None
            try:
                con = sqlite3.connect(str(db_path))
                self._ensure_primary_source_localized_schema_on_connection(con)
                with con:
                    if any(localized_values.values()):
                        con.execute(
                            """
                            INSERT INTO primary_source_texts(
                              source_id,
                              title_markup,
                              date_label,
                              content_label,
                              material_text,
                              text_style_text,
                              found_text,
                              classification_text,
                              current_location_text
                            )
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(source_id) DO UPDATE SET
                              title_markup = excluded.title_markup,
                              date_label = excluded.date_label,
                              content_label = excluded.content_label,
                              material_text = excluded.material_text,
                              text_style_text = excluded.text_style_text,
                              found_text = excluded.found_text,
                              classification_text = excluded.classification_text,
                              current_location_text = excluded.current_location_text
                            """,
                            (
                                source_id,
                                localized_values["title_markup"],
                                localized_values["date_label"],
                                localized_values["content_label"],
                                localized_values["material_text"],
                                localized_values["text_style_text"],
                                localized_values["found_text"],
                                localized_values["classification_text"],
                                localized_values["current_location_text"],
                            ),
                        )
                    else:
                        con.execute(
                            "DELETE FROM primary_source_texts WHERE source_id = ?",
                            (source_id,),
                        )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror(
                    "Ошибка локализации",
                    f"Не удалось сохранить локализованные поля:\n{exc}",
                    parent=self,
                )
                return
            finally:
                if con is not None:
                    con.close()

            self._load_primary_sources()
            self._select_primary_source_by_id(source_id)
            self._set_status(
                f"Локализованные поля '{source_id}' сохранены в {self.primary_source_locale_db_var.get() or '-'}."
            )

        def _add_primary_source(self) -> None:
            if not self._ensure_primary_source_section_ready():
                return

            payload = self._show_form_dialog(
                "Новый первоисточник",
                [
                    FormFieldSpec("id", "ID"),
                    FormFieldSpec("family", "Family", kind="combo", options=("uncial", "papyrus", "other")),
                    FormFieldSpec("number", "Number"),
                    FormFieldSpec("group_kind", "Group", kind="combo", options=("full", "significant", "fragment")),
                    FormFieldSpec("sort_order", "Sort order"),
                    FormFieldSpec("preview_resource_key", "Preview key"),
                ],
                initial={
                    "family": "uncial",
                    "number": "0",
                    "group_kind": "fragment",
                    "sort_order": str(len(self.primary_sources) * 10),
                    "preview_resource_key": "primary_sources/previews/new_source.png",
                },
                message="Создается только каркас записи. Остальные поля можно заполнить после создания.",
            )
            if payload is None:
                return

            source_id = str(payload["id"]).strip()
            if not source_id:
                messagebox.showwarning("Ошибка", "ID не может быть пустым.", parent=self)
                return
            if any(row.id == source_id for row in self.primary_sources):
                messagebox.showwarning("Дубликат", f"Источник '{source_id}' уже существует.", parent=self)
                return

            try:
                number = self._parse_required_int(payload["number"], "Number")
                sort_order = self._parse_required_int(payload["sort_order"], "Sort order")
            except ValueError as exc:
                messagebox.showwarning("Ошибка данных", str(exc), parent=self)
                return

            preview_key = str(payload["preview_resource_key"]).strip()
            if not preview_key or preview_key == "primary_sources/previews/new_source.png":
                preview_key = f"primary_sources/previews/{source_id}.png"

            try:
                with self.common_connection:
                    self.common_connection.execute(
                        """
                        INSERT INTO primary_sources(
                          id,
                          family,
                          number,
                          group_kind,
                          sort_order,
                          verses_count,
                          preview_resource_key,
                          default_max_scale,
                          can_show_images,
                          images_are_monochrome,
                          notes
                        )
                        VALUES(?, ?, ?, ?, ?, 0, ?, 3.0, 1, 0, '')
                        """,
                        (
                            source_id,
                            str(payload["family"]).strip(),
                            number,
                            str(payload["group_kind"]).strip(),
                            sort_order,
                            preview_key,
                        ),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка создания", f"Не удалось создать источник:\n{exc}", parent=self)
                return

            self._load_primary_sources()
            self._select_primary_source_by_id(source_id)
            self._set_status(f"Создан первоисточник '{source_id}'.")

        def _delete_primary_source(self) -> None:
            if not self._ensure_primary_source_section_ready():
                return
            source_id = self.selected_primary_source_id
            if not source_id:
                return
            if not messagebox.askyesno(
                "Удаление первоисточника",
                (
                    f"Удалить '{source_id}' из общей БД и всех localized DB?\n\n"
                    "Будут удалены source metadata, links, attributions, pages, words, verses и localized texts."
                ),
                parent=self,
            ):
                return

            try:
                with self.common_connection:
                    for table in (
                        "primary_source_verses",
                        "primary_source_words",
                        "primary_source_pages",
                        "primary_source_attributions",
                        "primary_source_links",
                    ):
                        self.common_connection.execute(
                            f"DELETE FROM {table} WHERE source_id = ?",
                            (source_id,),
                        )
                    self.common_connection.execute(
                        "DELETE FROM primary_sources WHERE id = ?",
                        (source_id,),
                    )
                for _lang, db_path in self._localized_db_entries():
                    with sqlite3.connect(str(db_path)) as localized_con:
                        localized_con.execute(
                            "DELETE FROM primary_source_link_texts WHERE source_id = ?",
                            (source_id,),
                        )
                        localized_con.execute(
                            "DELETE FROM primary_source_texts WHERE source_id = ?",
                            (source_id,),
                        )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить источник:\n{exc}", parent=self)
                return

            self._load_primary_sources()
            self._set_status(f"Первоисточник '{source_id}' удален.")

        def _import_primary_source_preview_resource(self) -> None:
            if self.common_connection is None or self.common_db_path is None:
                messagebox.showwarning("Нет общей БД", "Общая БД недоступна.", parent=self)
                return
            source_id = self.primary_source_id_var.get().strip()
            if not source_id:
                messagebox.showwarning("Нет источника", "Сначала создайте первоисточник.", parent=self)
                return
            selected = filedialog.askopenfilename(
                parent=self,
                title="Выберите preview изображение",
                initialdir=str(self.work_dir),
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp;*.gif;*.bmp"), ("All files", "*.*")],
            )
            if not selected:
                return
            path = Path(selected)
            try:
                data = path.read_bytes()
            except OSError as exc:
                messagebox.showerror("Ошибка чтения", f"Не удалось прочитать файл:\n{exc}", parent=self)
                return
            preview_key = self.primary_source_preview_key_var.get().strip() or f"primary_sources/previews/{source_id}.png"
            self.primary_source_preview_key_var.set(preview_key)
            mime = self._guess_mime_type(path.name)
            try:
                with self.common_connection:
                    self.common_connection.execute(
                        """
                        INSERT OR REPLACE INTO common_resources(key, file_name, mime_type, data)
                        VALUES(?, ?, ?, ?)
                        """,
                        (preview_key, path.name, mime, sqlite3.Binary(data)),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка записи", f"Не удалось сохранить preview:\n{exc}", parent=self)
                return
            self._load_common_resources()
            self._render_primary_source_preview()
            self._refresh_primary_source_validation()
            self._set_status(f"Preview ресурс '{preview_key}' обновлен.")

        def _open_primary_source_preview_resource(self) -> None:
            key = self.primary_source_preview_key_var.get().strip()
            payload = self._load_resource_payload_by_key(key)
            if payload is None:
                messagebox.showinfo("Нет preview", "Preview ресурс не найден в общей БД.", parent=self)
                return
            data, mime, file_name = payload
            suffix = Path(file_name).suffix or (mimetypes.guess_extension(mime) or ".bin")
            temp_path = Path(tempfile.gettempdir()) / (
                f"revelation_preview_{re.sub(r'[^0-9A-Za-z._-]+', '_', Path(file_name).stem)}{suffix}"
            )
            try:
                temp_path.write_bytes(data)
            except OSError as exc:
                messagebox.showerror("Ошибка записи", f"Не удалось подготовить preview файл:\n{exc}", parent=self)
                return
            webbrowser.open(temp_path.resolve().as_uri())
            self._set_status(f"Preview ресурс '{key}' открыт: {temp_path}")

        def _selected_primary_source_dir(self) -> Path | None:
            source_id = self.selected_primary_source_id
            if not source_id:
                return None

            page_dirs: list[Path] = []
            for row in self.primary_source_pages:
                if row.image_path.strip():
                    page_dirs.append(self._primary_source_local_path(row.image_path).parent)

            if page_dirs:
                try:
                    return Path(os.path.commonpath([str(path.resolve()) for path in page_dirs]))
                except ValueError:
                    return page_dirs[0]

            return self._primary_sources_root_dir() / source_id

        def _open_selected_primary_source_dir(self) -> None:
            root = self._selected_primary_source_dir()
            if root is None:
                messagebox.showinfo(
                    "Нет первоисточника",
                    "Сначала выберите первоисточник.",
                    parent=self,
                )
                return
            try:
                root.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                messagebox.showerror("Ошибка", f"Не удалось создать папку:\n{exc}", parent=self)
                return
            webbrowser.open(root.resolve().as_uri())

        def _link_dialog_payload(self, initial: dict[str, object] | None = None) -> dict[str, object] | None:
            initial = initial or {}

            dialog = tk.Toplevel(self)
            dialog.title("Ссылка первоисточника")
            dialog.transient(self)
            dialog.grab_set()
            dialog.resizable(True, True)
            dialog.minsize(620, 420)

            root = ttk.Frame(dialog, padding=12)
            root.grid(row=0, column=0, sticky="nsew")
            dialog.columnconfigure(0, weight=1)
            dialog.rowconfigure(0, weight=1)
            root.columnconfigure(1, weight=1)

            link_id_var = tk.StringVar(value=str(initial.get("link_id", "")))
            sort_order_var = tk.StringVar(value=str(initial.get("sort_order", "")))
            link_role_var = tk.StringVar(value=str(initial.get("link_role", "external")))
            url_var = tk.StringVar(value=str(initial.get("url", "")))

            ttk.Label(root, text="ID ссылки:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=4)
            ttk.Entry(root, textvariable=link_id_var).grid(row=0, column=1, sticky="ew", pady=4)

            ttk.Label(root, text="Порядок:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=4)
            ttk.Entry(root, textvariable=sort_order_var).grid(row=1, column=1, sticky="ew", pady=4)

            ttk.Label(root, text="Тип:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=4)
            role_combo = ttk.Combobox(
                root,
                textvariable=link_role_var,
                values=("wikipedia", "intf", "image_source", "external"),
                state="readonly",
            )
            role_combo.grid(row=2, column=1, sticky="ew", pady=4)

            ttk.Label(root, text="URL:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=4)
            ttk.Entry(root, textvariable=url_var).grid(row=3, column=1, sticky="ew", pady=4)

            localized_titles_initial = initial.get("localized_titles")
            localized_titles = localized_titles_initial if isinstance(localized_titles_initial, dict) else {}

            titles_box = ttk.LabelFrame(root, text="Текст ссылки")
            titles_box.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
            titles_box.columnconfigure(1, weight=1)
            root.rowconfigure(4, weight=1)

            title_vars: dict[str, tk.StringVar] = {}
            localized_entries = [(lang, db_path) for lang, db_path in self._localized_db_entries() if db_path.exists()]
            if localized_entries:
                for idx, (lang, _db_path) in enumerate(localized_entries):
                    ttk.Label(titles_box, text=f"{lang}:").grid(row=idx, column=0, sticky="w", padx=(0, 8), pady=3)
                    title_var = tk.StringVar(value=str(localized_titles.get(lang, "")))
                    ttk.Entry(titles_box, textvariable=title_var).grid(row=idx, column=1, sticky="ew", pady=3)
                    title_vars[lang] = title_var
            else:
                ttk.Label(
                    titles_box,
                    text="Локализованные БД не найдены.",
                    foreground="#5f5f5f",
                ).grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=4)

            result: dict[str, object] | None = None

            def submit() -> None:
                nonlocal result
                result = {
                    "link_id": link_id_var.get().strip(),
                    "sort_order": sort_order_var.get().strip(),
                    "link_role": link_role_var.get().strip(),
                    "url": url_var.get().strip(),
                    "localized_titles": {lang: var.get().strip() for lang, var in title_vars.items()},
                }
                dialog.destroy()

            actions = ttk.Frame(root)
            actions.grid(row=5, column=0, columnspan=2, sticky="e", pady=(12, 0))
            ttk.Button(actions, text="Сохранить", command=submit).pack(side="left")
            ttk.Button(actions, text="Отмена", command=dialog.destroy).pack(side="left", padx=(8, 0))

            dialog.bind("<Escape>", lambda _event: dialog.destroy())
            dialog.bind("<Control-Return>", lambda _event: submit())
            self.wait_window(dialog)
            return result

        def _add_primary_source_link(self) -> None:
            if not self._ensure_primary_source_section_ready():
                return
            source_id = self.selected_primary_source_id
            if not source_id:
                messagebox.showinfo("Нет источника", "Сначала выберите первоисточник.", parent=self)
                return
            payload = self._link_dialog_payload(
                {
                    "sort_order": str(len(self.primary_source_link_rows)),
                    "link_role": "external",
                }
            )
            if payload is None:
                return
            self._save_primary_source_link_record(payload, previous_link_id=None)

        def _edit_primary_source_link(self) -> None:
            row = self._selected_primary_source_link_row()
            if row is None:
                return
            localized_titles = self._link_localized_titles_by_lang(str(row["link_id"]))
            payload = self._link_dialog_payload(
                {
                    "link_id": row["link_id"],
                    "sort_order": str(int(row["sort_order"] or 0)),
                    "link_role": row["link_role"],
                    "url": row["url"],
                    "localized_titles": localized_titles,
                }
            )
            if payload is None:
                return
            self._save_primary_source_link_record(payload, previous_link_id=str(row["link_id"]))

        def _save_primary_source_link_record(
            self,
            payload: dict[str, object],
            *,
            previous_link_id: str | None,
        ) -> None:
            source_id = self.selected_primary_source_id
            if not source_id or not self._ensure_primary_source_section_ready():
                return
            link_id = str(payload["link_id"]).strip()
            url = str(payload["url"]).strip()
            link_role = str(payload["link_role"]).strip()
            allowed_roles = ("wikipedia", "intf", "image_source", "external")
            if not link_id or not url:
                messagebox.showwarning("Ошибка", "Link ID и URL обязательны.", parent=self)
                return
            if link_role not in allowed_roles:
                messagebox.showwarning(
                    "Ошибка данных",
                    f"Недопустимый тип. Разрешено: {', '.join(allowed_roles)}.",
                    parent=self,
                )
                return
            try:
                sort_order = self._parse_required_int(payload["sort_order"], "Порядок")
            except ValueError as exc:
                messagebox.showwarning("Ошибка данных", str(exc), parent=self)
                return

            duplicate = next(
                (
                    row
                    for row in self.primary_source_link_rows
                    if row["link_id"] == link_id and row["link_id"] != previous_link_id
                ),
                None,
            )
            if duplicate is not None:
                messagebox.showwarning("Дубликат", f"Link ID '{link_id}' уже существует.", parent=self)
                return

            try:
                with self.common_connection:
                    if previous_link_id and previous_link_id != link_id:
                        self.common_connection.execute(
                            "DELETE FROM primary_source_links WHERE source_id = ? AND link_id = ?",
                            (source_id, previous_link_id),
                        )
                    self.common_connection.execute(
                        """
                        INSERT OR REPLACE INTO primary_source_links(
                          source_id,
                          link_id,
                          sort_order,
                          link_role,
                          url
                        )
                        VALUES(?, ?, ?, ?, ?)
                        """,
                        (source_id, link_id, sort_order, link_role, url),
                    )
                if previous_link_id and previous_link_id != link_id:
                    for _lang, db_path in self._localized_db_entries():
                        with sqlite3.connect(str(db_path)) as localized_con:
                            localized_con.execute(
                                """
                                UPDATE primary_source_link_texts
                                SET link_id = ?
                                WHERE source_id = ?
                                  AND link_id = ?
                                """,
                                (link_id, source_id, previous_link_id),
                            )
                localized_titles_payload = payload.get("localized_titles")
                localized_titles = localized_titles_payload if isinstance(localized_titles_payload, dict) else {}
                for lang, db_path in self._localized_db_entries():
                    if not db_path.exists():
                        continue
                    new_title = str(localized_titles.get(lang, "")).strip()
                    localized_con: sqlite3.Connection | None = None
                    try:
                        localized_con = sqlite3.connect(str(db_path))
                        localized_con.row_factory = sqlite3.Row
                        self._ensure_primary_source_localized_schema_on_connection(localized_con)
                        existing_row = localized_con.execute(
                            """
                            SELECT title
                            FROM primary_source_link_texts
                            WHERE source_id = ?
                              AND link_id = ?
                            LIMIT 1
                            """,
                            (source_id, link_id),
                        ).fetchone()
                        existing_title = str(existing_row["title"] or "").strip() if existing_row is not None else ""
                        if not existing_title and not new_title:
                            continue
                        with localized_con:
                            if new_title:
                                localized_con.execute(
                                    """
                                    INSERT OR REPLACE INTO primary_source_link_texts(source_id, link_id, title)
                                    VALUES(?, ?, ?)
                                    """,
                                    (source_id, link_id, new_title),
                                )
                            else:
                                localized_con.execute(
                                    "DELETE FROM primary_source_link_texts WHERE source_id = ? AND link_id = ?",
                                    (source_id, link_id),
                                )
                    finally:
                        if localized_con is not None:
                            localized_con.close()
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить ссылку:\n{exc}", parent=self)
                return

            self._reload_selected_primary_source()
            self._set_status(f"Ссылка '{link_id}' сохранена для '{source_id}'.")

        def _delete_primary_source_link(self) -> None:
            row = self._selected_primary_source_link_row()
            source_id = self.selected_primary_source_id
            if row is None or not source_id or not self._ensure_primary_source_section_ready():
                return
            link_id = str(row["link_id"])
            if not messagebox.askyesno(
                "Удаление ссылки",
                f"Удалить ссылку '{link_id}' из common и всех localized DB?",
                parent=self,
            ):
                return
            try:
                with self.common_connection:
                    self.common_connection.execute(
                        "DELETE FROM primary_source_links WHERE source_id = ? AND link_id = ?",
                        (source_id, link_id),
                    )
                for _lang, db_path in self._localized_db_entries():
                    with sqlite3.connect(str(db_path)) as localized_con:
                        localized_con.execute(
                            "DELETE FROM primary_source_link_texts WHERE source_id = ? AND link_id = ?",
                            (source_id, link_id),
                        )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить ссылку:\n{exc}", parent=self)
                return
            self._reload_selected_primary_source()
            self._set_status(f"Ссылка '{link_id}' удалена.")

        def _open_primary_source_link_url(self) -> None:
            row = self._selected_primary_source_link_row()
            if row is None:
                return
            webbrowser.open(str(row["url"]))

        def _attribution_dialog_payload(self, initial: dict[str, object] | None = None) -> dict[str, object] | None:
            return self._show_form_dialog(
                "Атрибуция / права",
                [
                    FormFieldSpec("attribution_id", "ID"),
                    FormFieldSpec("sort_order", "Порядок"),
                    FormFieldSpec("text", "Текст", width=70),
                    FormFieldSpec("url", "URL", width=70),
                ],
                initial=initial,
            )

        def _add_primary_source_attribution(self) -> None:
            if not self._ensure_primary_source_section_ready():
                return
            if not self.selected_primary_source_id:
                messagebox.showinfo("Нет источника", "Сначала выберите первоисточник.", parent=self)
                return
            payload = self._attribution_dialog_payload(
                {
                    "attribution_id": f"attr_{len(self.primary_source_attribution_rows) + 1}",
                    "sort_order": str(len(self.primary_source_attribution_rows)),
                }
            )
            if payload is None:
                return
            self._save_primary_source_attribution_record(payload, previous_attribution_id=None)

        def _edit_primary_source_attribution(self) -> None:
            row = self._selected_primary_source_attribution_row()
            if row is None:
                return
            payload = self._attribution_dialog_payload(
                {
                    "attribution_id": row["attribution_id"],
                    "sort_order": str(int(row["sort_order"] or 0)),
                    "text": row["text"],
                    "url": row["url"],
                }
            )
            if payload is None:
                return
            self._save_primary_source_attribution_record(
                payload,
                previous_attribution_id=str(row["attribution_id"]),
            )

        def _save_primary_source_attribution_record(
            self,
            payload: dict[str, object],
            *,
            previous_attribution_id: str | None,
        ) -> None:
            source_id = self.selected_primary_source_id
            if not source_id or self.common_connection is None:
                return
            attribution_id = str(payload["attribution_id"]).strip()
            text = str(payload["text"]).strip()
            url = str(payload["url"]).strip()
            if not attribution_id or not text:
                messagebox.showwarning("Ошибка", "ID и Текст обязательны.", parent=self)
                return
            try:
                sort_order = self._parse_required_int(payload["sort_order"], "Порядок")
            except ValueError as exc:
                messagebox.showwarning("Ошибка данных", str(exc), parent=self)
                return

            duplicate = next(
                (
                    row
                    for row in self.primary_source_attribution_rows
                    if row["attribution_id"] == attribution_id and row["attribution_id"] != previous_attribution_id
                ),
                None,
            )
            if duplicate is not None:
                messagebox.showwarning("Дубликат", f"ID '{attribution_id}' уже существует.", parent=self)
                return

            try:
                with self.common_connection:
                    if previous_attribution_id and previous_attribution_id != attribution_id:
                        self.common_connection.execute(
                            "DELETE FROM primary_source_attributions WHERE source_id = ? AND attribution_id = ?",
                            (source_id, previous_attribution_id),
                        )
                    self.common_connection.execute(
                        """
                        INSERT OR REPLACE INTO primary_source_attributions(
                          source_id,
                          attribution_id,
                          sort_order,
                          text,
                          url
                        )
                        VALUES(?, ?, ?, ?, ?)
                        """,
                        (source_id, attribution_id, sort_order, text, url),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить атрибуцию:\n{exc}", parent=self)
                return
            self._reload_selected_primary_source()
            self._set_status(f"Атрибуция '{attribution_id}' сохранена.")

        def _delete_primary_source_attribution(self) -> None:
            row = self._selected_primary_source_attribution_row()
            source_id = self.selected_primary_source_id
            if row is None or not source_id or self.common_connection is None:
                return
            attribution_id = str(row["attribution_id"])
            if not messagebox.askyesno(
                "Удаление атрибуции",
                f"Удалить атрибуцию '{attribution_id}'?",
                parent=self,
            ):
                return
            try:
                with self.common_connection:
                    self.common_connection.execute(
                        "DELETE FROM primary_source_attributions WHERE source_id = ? AND attribution_id = ?",
                        (source_id, attribution_id),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить атрибуцию:\n{exc}", parent=self)
                return
            self._reload_selected_primary_source()
            self._set_status(f"Атрибуция '{attribution_id}' удалена.")

        def _open_primary_source_attribution_url(self) -> None:
            row = self._selected_primary_source_attribution_row()
            if row is None:
                return
            url = str(row["url"] or "").strip()
            if url:
                webbrowser.open(url)

        def _page_dialog_payload(self, initial: dict[str, object] | None = None) -> dict[str, object] | None:
            return self._show_form_dialog(
                "Страница первоисточника",
                [
                    FormFieldSpec("page_name", "Название"),
                    FormFieldSpec("sort_order", "Порядок"),
                    FormFieldSpec("content_ref", "Содержимое"),
                    FormFieldSpec("image_path", "Путь на сервере и локально", width=70),
                ],
                initial=initial,
            )

        def _add_primary_source_page(self) -> None:
            if not self._ensure_primary_source_section_ready():
                return
            if not self.selected_primary_source_id:
                messagebox.showinfo("Нет источника", "Сначала выберите первоисточник.", parent=self)
                return
            payload = self._page_dialog_payload(
                {
                    "sort_order": str(max((row.sort_order for row in self.primary_source_pages), default=-10) + 10),
                }
            )
            if payload is None:
                return
            self._save_primary_source_page_record(payload, previous_page_name=None)

        def _edit_primary_source_page(self) -> None:
            row = self._selected_primary_source_page_row()
            if row is None:
                return
            payload = self._page_dialog_payload(
                {
                    "page_name": row.page_name,
                    "sort_order": str(row.sort_order),
                    "content_ref": row.content_ref,
                    "image_path": row.image_path,
                }
            )
            if payload is None:
                return
            self._save_primary_source_page_record(payload, previous_page_name=row.page_name)

        def _save_primary_source_page_record(
            self,
            payload: dict[str, object],
            *,
            previous_page_name: str | None,
        ) -> None:
            source_id = self.selected_primary_source_id
            if not source_id or self.common_connection is None:
                return
            page_name = str(payload["page_name"]).strip()
            content_ref = str(payload["content_ref"]).strip()
            image_path = str(payload["image_path"]).strip().replace("\\", "/")
            if not page_name or not content_ref:
                messagebox.showwarning("Ошибка", "Название и Содержимое обязательны.", parent=self)
                return
            try:
                sort_order = self._parse_required_int(payload["sort_order"], "Порядок")
            except ValueError as exc:
                messagebox.showwarning("Ошибка данных", str(exc), parent=self)
                return

            duplicate = next(
                (
                    row
                    for row in self.primary_source_pages
                    if row.page_name == page_name and row.page_name != previous_page_name
                ),
                None,
            )
            if duplicate is not None:
                messagebox.showwarning("Дубликат", f"Страница '{page_name}' уже существует.", parent=self)
                return

            try:
                with self.common_connection:
                    if previous_page_name and previous_page_name != page_name:
                        self.common_connection.execute(
                            """
                            UPDATE primary_source_words
                            SET page_name = ?
                            WHERE source_id = ?
                              AND page_name = ?
                            """,
                            (page_name, source_id, previous_page_name),
                        )
                        self.common_connection.execute(
                            """
                            UPDATE primary_source_verses
                            SET page_name = ?
                            WHERE source_id = ?
                              AND page_name = ?
                            """,
                            (page_name, source_id, previous_page_name),
                        )
                        self.common_connection.execute(
                            "DELETE FROM primary_source_pages WHERE source_id = ? AND page_name = ?",
                            (source_id, previous_page_name),
                        )
                    self.common_connection.execute(
                        """
                        INSERT OR REPLACE INTO primary_source_pages(
                          source_id,
                          page_name,
                          sort_order,
                          content_ref,
                          image_path
                        )
                        VALUES(?, ?, ?, ?, ?)
                        """,
                        (
                            source_id,
                            page_name,
                            sort_order,
                            content_ref,
                            image_path,
                        ),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить страницу:\n{exc}", parent=self)
                return
            self._reload_selected_primary_source()
            self._select_primary_source_page(page_name)
            self._set_status(f"Страница '{page_name}' сохранена.")

        def _delete_primary_source_page(self) -> None:
            row = self._selected_primary_source_page_row()
            source_id = self.selected_primary_source_id
            if row is None or not source_id or self.common_connection is None:
                return
            if not messagebox.askyesno(
                "Удаление страницы",
                (
                    f"Удалить страницу '{row.page_name}'?\n\n"
                    "Будут также удалены все слова и verse-разметка этой страницы."
                ),
                parent=self,
            ):
                return
            try:
                with self.common_connection:
                    self.common_connection.execute(
                        "DELETE FROM primary_source_words WHERE source_id = ? AND page_name = ?",
                        (source_id, row.page_name),
                    )
                    self.common_connection.execute(
                        "DELETE FROM primary_source_verses WHERE source_id = ? AND page_name = ?",
                        (source_id, row.page_name),
                    )
                    self.common_connection.execute(
                        "DELETE FROM primary_source_pages WHERE source_id = ? AND page_name = ?",
                        (source_id, row.page_name),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить страницу:\n{exc}", parent=self)
                return
            self._reload_selected_primary_source()
            self._set_status(f"Страница '{row.page_name}' удалена.")

        def _open_selected_primary_source_page_file(self) -> None:
            row = self._selected_primary_source_page_row()
            if row is None:
                return
            path = self._primary_source_local_path(row.image_path)
            if not path.exists():
                messagebox.showinfo("Нет файла", f"Локальный файл не найден:\n{path}", parent=self)
                return
            webbrowser.open(path.resolve().as_uri())

        def _download_selected_primary_source_page(self) -> None:
            page_row = self._selected_primary_source_page_row()
            if page_row is None:
                messagebox.showinfo("Нет страницы", "Сначала выберите страницу.", parent=self)
                return
            self._download_primary_source_page_rows(
                [page_row],
                force=self.primary_source_force_download_var.get(),
                summary_title=f"Скачивание страницы {page_row.page_name}",
            )

        def _download_selected_primary_source_pages(self) -> None:
            source_id = self.selected_primary_source_id
            if not source_id:
                messagebox.showinfo("Нет источника", "Сначала выберите первоисточник.", parent=self)
                return
            self._download_primary_source_page_rows(
                list(self.primary_source_pages),
                force=self.primary_source_force_download_var.get(),
                summary_title=f"Скачивание страниц {source_id}",
            )

        def _open_primary_source_verse_editor(
            self,
            *,
            initial_payload: dict[str, object],
            previous_verse_index: int | None,
        ) -> None:
            if Image is None or ImageTk is None:
                messagebox.showwarning(
                    "Нет Pillow",
                    "Для редактора стиха нужен Pillow: pip install pillow",
                    parent=self,
                )
                return
            page_row = self._selected_primary_source_page_row()
            source_id = self.selected_primary_source_id
            page_name = self.selected_primary_source_page_name
            if page_row is None or not source_id or not page_name:
                messagebox.showinfo("Нет страницы", "Сначала выберите страницу.", parent=self)
                return

            image_path = self._primary_source_local_path(page_row.image_path)
            if not image_path.exists():
                messagebox.showinfo(
                    "Нет изображения",
                    (
                        "Локальный файл страницы не найден.\n"
                        "Скачайте страницу кнопкой из раздела первоисточников."
                    ),
                    parent=self,
                )
                return

            PrimarySourceVerseEditorDialog(
                parent=self,
                image_path=image_path,
                source_id=source_id,
                page_name=page_name,
                initial_payload=initial_payload,
                previous_verse_index=previous_verse_index,
                on_save=lambda payload, previous: self._save_primary_source_verse_record(
                    payload,
                    previous_verse_index=previous,
                ),
            )

        def _strong_entries_for_word_editor(self) -> list[tuple[int, str]]:
            return [(int(row.id), str(row.word or "")) for row in self.strong_rows]

        def _open_primary_source_word_editor(
            self,
            *,
            initial_payload: dict[str, object],
            previous_word_index: int | None,
        ) -> None:
            page_row = self._selected_primary_source_page_row()
            source_id = self.selected_primary_source_id
            page_name = self.selected_primary_source_page_name
            if page_row is None or not source_id or not page_name:
                messagebox.showinfo("Нет страницы", "Сначала выберите страницу.", parent=self)
                return

            image_path = self._primary_source_local_path(page_row.image_path)
            if not image_path.exists():
                messagebox.showinfo(
                    "Нет изображения",
                    (
                        "Локальный файл страницы не найден.\n"
                        "Скачайте страницу кнопкой из раздела первоисточников."
                    ),
                    parent=self,
                )
                return

            PrimarySourceWordEditorDialog(
                parent=self,
                image_path=image_path,
                source_id=source_id,
                page_name=page_name,
                initial_payload=initial_payload,
                previous_word_index=previous_word_index,
                strong_entries=self._strong_entries_for_word_editor(),
                on_save=lambda payload, previous: self._save_primary_source_word_record(
                    payload,
                    previous_word_index=previous,
                ),
            )

        def _add_primary_source_word(self) -> None:
            if not self._ensure_primary_source_section_ready():
                return
            if not self.selected_primary_source_page_name:
                messagebox.showinfo("Нет страницы", "Сначала выберите страницу.", parent=self)
                return
            next_word_index = max((int(row["word_index"] or 0) for row in self.primary_source_word_rows), default=-1) + 1
            self._open_primary_source_word_editor(
                initial_payload={
                    "word_index": next_word_index,
                    "text": "",
                    "strong_number": "",
                    "strong_pronounce": False,
                    "strong_x_shift": "0.0",
                    "missing_char_indexes_json": [],
                    "rectangles_json": [],
                },
                previous_word_index=None,
            )

        def _edit_primary_source_word(self) -> None:
            row = self._selected_primary_source_word_row()
            if row is None:
                return
            self._open_primary_source_word_editor(
                initial_payload={
                    "word_index": str(int(row["word_index"] or 0)),
                    "text": row["text"] or "",
                    "strong_number": "" if row["strong_number"] is None else str(row["strong_number"]),
                    "strong_pronounce": bool(row["strong_pronounce"]),
                    "strong_x_shift": str(float(row["strong_x_shift"] or 0.0)),
                    "missing_char_indexes_json": self._safe_json_loads(row["missing_char_indexes_json"] or "[]", []),
                    "rectangles_json": self._safe_json_loads(row["rectangles_json"] or "[]", []),
                },
                previous_word_index=int(row["word_index"] or 0),
            )

        def _save_primary_source_word_record(
            self,
            payload: dict[str, object],
            *,
            previous_word_index: int | None,
        ) -> bool:
            source_id = self.selected_primary_source_id
            page_name = self.selected_primary_source_page_name
            if not source_id or not page_name or self.common_connection is None:
                return False
            text = str(payload["text"]).strip()
            if not text:
                messagebox.showwarning("Ошибка", "Слово обязательно.", parent=self)
                return False
            try:
                word_index = self._parse_required_int(payload["word_index"], "Word index")
                strong_number = self._parse_optional_int(payload["strong_number"])
                strong_x_shift = self._parse_required_float(payload["strong_x_shift"], "Strong X shift")
                missing_char_indexes = self._parse_int_list_payload(
                    payload.get("missing_char_indexes_json", []),
                    "Missing char indexes",
                )
                rectangles = self._parse_word_rectangles_payload(payload.get("rectangles_json", []))
            except ValueError as exc:
                messagebox.showwarning("Ошибка данных", str(exc), parent=self)
                return False

            duplicate = next(
                (
                    row
                    for row in self.primary_source_word_rows
                    if int(row["word_index"] or 0) == word_index
                    and int(row["word_index"] or 0) != previous_word_index
                ),
                None,
            )
            if duplicate is not None:
                messagebox.showwarning("Дубликат", f"Word index '{word_index}' уже существует.", parent=self)
                return False

            try:
                with self.common_connection:
                    if previous_word_index is not None and previous_word_index != word_index:
                        self.common_connection.execute(
                            """
                            DELETE FROM primary_source_words
                            WHERE source_id = ?
                              AND page_name = ?
                              AND word_index = ?
                            """,
                            (source_id, page_name, previous_word_index),
                        )
                    self.common_connection.execute(
                        """
                        INSERT OR REPLACE INTO primary_source_words(
                          source_id,
                          page_name,
                          word_index,
                          text,
                          strong_number,
                          strong_pronounce,
                          strong_x_shift,
                          missing_char_indexes_json,
                          rectangles_json
                        )
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            source_id,
                            page_name,
                            word_index,
                            text,
                            strong_number,
                            1 if bool(payload["strong_pronounce"]) else 0,
                            strong_x_shift,
                            json.dumps(missing_char_indexes, ensure_ascii=False),
                            json.dumps(rectangles, ensure_ascii=False),
                        ),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить слово:\n{exc}", parent=self)
                return False
            self._load_primary_source_page_children()
            self._select_primary_source_word_by_value(word_index)
            self._refresh_primary_source_validation()
            self._set_status(f"Слово #{word_index} сохранено.")
            return True

        def _delete_primary_source_word(self) -> None:
            row = self._selected_primary_source_word_row()
            source_id = self.selected_primary_source_id
            page_name = self.selected_primary_source_page_name
            if row is None or not source_id or not page_name or self.common_connection is None:
                return
            word_index = int(row["word_index"] or 0)
            if not messagebox.askyesno(
                "Удаление слова",
                f"Удалить слово #{word_index} со страницы '{page_name}'?",
                parent=self,
            ):
                return
            try:
                with self.common_connection:
                    self.common_connection.execute(
                        """
                        DELETE FROM primary_source_words
                        WHERE source_id = ?
                          AND page_name = ?
                          AND word_index = ?
                        """,
                        (source_id, page_name, word_index),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить слово:\n{exc}", parent=self)
                return
            self._load_primary_source_page_children()
            self._refresh_primary_source_validation()
            self._set_status(f"Слово #{word_index} удалено.")

        def _add_primary_source_verse(self) -> None:
            if not self._ensure_primary_source_section_ready():
                return
            if not self.selected_primary_source_page_name:
                messagebox.showinfo("Нет страницы", "Сначала выберите страницу.", parent=self)
                return
            next_verse_index = max((int(row["verse_index"] or 0) for row in self.primary_source_verse_rows), default=-1) + 1
            chapter_number = 1
            verse_number = 1
            if self.primary_source_verse_rows:
                last_row = max(self.primary_source_verse_rows, key=lambda row: int(row["verse_index"] or 0))
                chapter_number = int(last_row["chapter_number"] or 1)
                verse_number = int(last_row["verse_number"] or 0) + 1
            self._open_primary_source_verse_editor(
                initial_payload={
                    "verse_index": next_verse_index,
                    "chapter_number": chapter_number,
                    "verse_number": verse_number,
                    "label_x": 0.0,
                    "label_y": 0.0,
                    "word_indexes": [],
                    "contours": [],
                },
                previous_verse_index=None,
            )

        def _edit_primary_source_verse(self) -> None:
            row = self._selected_primary_source_verse_row()
            if row is None:
                return
            self._open_primary_source_verse_editor(
                initial_payload={
                    "verse_index": str(int(row["verse_index"] or 0)),
                    "chapter_number": str(int(row["chapter_number"] or 0)),
                    "verse_number": str(int(row["verse_number"] or 0)),
                    "label_x": str(float(row["label_x"] or 0.0)),
                    "label_y": str(float(row["label_y"] or 0.0)),
                    "word_indexes": self._safe_json_loads(row["word_indexes_json"] or "[]", []),
                    "contours": self._safe_json_loads(row["contours_json"] or "[]", []),
                },
                previous_verse_index=int(row["verse_index"] or 0),
            )

        def _save_primary_source_verse_record(
            self,
            payload: dict[str, object],
            *,
            previous_verse_index: int | None,
        ) -> bool:
            source_id = self.selected_primary_source_id
            page_name = self.selected_primary_source_page_name
            if not source_id or not page_name or self.common_connection is None:
                return False
            try:
                verse_index = self._parse_required_int(payload["verse_index"], "Verse index")
                chapter_number = self._parse_required_int(payload["chapter_number"], "Chapter number")
                verse_number = self._parse_required_int(payload["verse_number"], "Verse number")
                label_x = self._parse_required_float(payload["label_x"], "Label X")
                label_y = self._parse_required_float(payload["label_y"], "Label Y")
                word_indexes = self._parse_json_list(payload["word_indexes_json"], "Word indexes JSON")
                contours = self._parse_json_list(payload["contours_json"], "Contours JSON")
            except ValueError as exc:
                messagebox.showwarning("Ошибка данных", str(exc), parent=self)
                return False

            duplicate = next(
                (
                    row
                    for row in self.primary_source_verse_rows
                    if int(row["verse_index"] or 0) == verse_index
                    and int(row["verse_index"] or 0) != previous_verse_index
                ),
                None,
            )
            if duplicate is not None:
                messagebox.showwarning("Дубликат", f"Verse index '{verse_index}' уже существует.", parent=self)
                return False

            try:
                with self.common_connection:
                    if previous_verse_index is not None and previous_verse_index != verse_index:
                        self.common_connection.execute(
                            """
                            DELETE FROM primary_source_verses
                            WHERE source_id = ?
                              AND page_name = ?
                              AND verse_index = ?
                            """,
                            (source_id, page_name, previous_verse_index),
                        )
                    self.common_connection.execute(
                        """
                        INSERT OR REPLACE INTO primary_source_verses(
                          source_id,
                          page_name,
                          verse_index,
                          chapter_number,
                          verse_number,
                          label_x,
                          label_y,
                          word_indexes_json,
                          contours_json
                        )
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            source_id,
                            page_name,
                            verse_index,
                            chapter_number,
                            verse_number,
                            label_x,
                            label_y,
                            json.dumps(word_indexes, ensure_ascii=False),
                            json.dumps(contours, ensure_ascii=False),
                        ),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить verse:\n{exc}", parent=self)
                return False
            self._load_primary_source_page_children()
            self._select_primary_source_verse_by_value(verse_index)
            self._refresh_primary_source_validation()
            self._set_status(f"Verse #{verse_index} сохранен.")
            return True

        def _delete_primary_source_verse(self) -> None:
            row = self._selected_primary_source_verse_row()
            source_id = self.selected_primary_source_id
            page_name = self.selected_primary_source_page_name
            if row is None or not source_id or not page_name or self.common_connection is None:
                return
            verse_index = int(row["verse_index"] or 0)
            if not messagebox.askyesno(
                "Удаление verse",
                f"Удалить verse #{verse_index} со страницы '{page_name}'?",
                parent=self,
            ):
                return
            try:
                with self.common_connection:
                    self.common_connection.execute(
                        """
                        DELETE FROM primary_source_verses
                        WHERE source_id = ?
                          AND page_name = ?
                          AND verse_index = ?
                        """,
                        (source_id, page_name, verse_index),
                    )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить verse:\n{exc}", parent=self)
                return
            self._load_primary_source_page_children()
            self._refresh_primary_source_validation()
            self._set_status(f"Verse #{verse_index} удален.")

        def _import_primary_source_verse_snippet(self) -> None:
            if not self.selected_primary_source_page_name:
                messagebox.showinfo("Нет страницы", "Сначала выберите страницу.", parent=self)
                return
            payload = self._show_form_dialog(
                "Import Verse(...) snippet",
                [FormFieldSpec("snippet", "Verse snippet", kind="text", height=12)],
                message="Вставьте блок Verse(...). Данные будут разобраны и записаны в primary_source_verses.",
            )
            if payload is None:
                return
            try:
                parsed = parse_verse_snippet(str(payload["snippet"]))
                label = parsed.get("label") or (0.0, 0.0)
            except ValueError as exc:
                messagebox.showerror("Ошибка разбора", str(exc), parent=self)
                return
            verse_payload = {
                "verse_index": str(
                    max((int(row["verse_index"] or 0) for row in self.primary_source_verse_rows), default=-1) + 1
                ),
                "chapter_number": str(int(parsed["chapter"])),
                "verse_number": str(int(parsed["verse"])),
                "label_x": str(float(label[0])),
                "label_y": str(float(label[1])),
                "word_indexes_json": json.dumps(parsed["word_indexes"], ensure_ascii=False),
                "contours_json": json.dumps(parsed["contours"], ensure_ascii=False),
            }
            self._save_primary_source_verse_record(verse_payload, previous_verse_index=None)

