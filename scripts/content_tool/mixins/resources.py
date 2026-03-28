from __future__ import annotations

import base64
import datetime as dt
import io
import mimetypes
import re
import sqlite3
import subprocess
import tempfile
import urllib.parse
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

from ..compat import Image, ImageTk
from ..models import ResourceRow


class ResourcesMixin:
        def _build_resources_tab(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(0, weight=1)

            pane = self._new_split_pane(parent)
            pane.grid(row=0, column=0, sticky="nsew")

            left = ttk.Frame(pane, padding=8)
            right = ttk.Frame(pane, padding=8)
            pane.add(left, stretch="always")
            pane.add(right, stretch="always")
            self._set_initial_split(pane, ratio=0.5)

            left.columnconfigure(0, weight=1)
            left.rowconfigure(0, weight=1)

            self.resources_tree = ttk.Treeview(
                left,
                columns=("key", "mime", "size", "file"),
                show="headings",
                selectmode="browse",
            )
            self.resources_tree.heading("key", text="Ключ")
            self.resources_tree.heading("mime", text="MIME")
            self.resources_tree.heading("size", text="Размер")
            self.resources_tree.heading("file", text="Имя файла")
            self.resources_tree.column("key", width=280, anchor="w")
            self.resources_tree.column("mime", width=170, anchor="w")
            self.resources_tree.column("size", width=95, anchor="e")
            self.resources_tree.column("file", width=240, anchor="w")
            self.resources_tree.grid(row=0, column=0, sticky="nsew")
            self.resources_tree.bind("<<TreeviewSelect>>", self._on_resource_selected)

            resources_scroll = ttk.Scrollbar(left, orient="vertical", command=self.resources_tree.yview)
            resources_scroll.grid(row=0, column=1, sticky="ns")
            self.resources_tree.configure(yscrollcommand=resources_scroll.set)

            resources_buttons = ttk.Frame(left)
            resources_buttons.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_add_resource = ttk.Button(
                resources_buttons,
                **self._button_kwargs("add", "Новый из файла"),
                command=self._add_resource_from_file,
            )
            self.btn_add_resource.pack(side="left")
            self.btn_delete_resource = ttk.Button(
                resources_buttons,
                **self._button_kwargs("delete", "Удалить ресурс"),
                command=self._delete_resource,
            )
            self.btn_delete_resource.pack(side="left", padx=(8, 0))
            self.btn_open_resource = ttk.Button(
                resources_buttons,
                **self._button_kwargs("open_resource", "Открыть ресурс"),
                command=self._open_resource_external,
            )
            self.btn_open_resource.pack(side="left", padx=(8, 0))
            self.btn_export_resource = ttk.Button(
                resources_buttons,
                **self._button_kwargs("publish", "Экспорт..."),
                command=self._export_resource_to_file,
            )
            self.btn_export_resource.pack(side="left", padx=(8, 0))
            self.btn_vacuum_resources = ttk.Button(
                resources_buttons,
                **self._button_kwargs("refresh", "Сжать БД (VACUUM)"),
                command=self._vacuum_common_resources_db,
            )
            self.btn_vacuum_resources.pack(side="left", padx=(8, 0))

            right.columnconfigure(1, weight=1)
            right.rowconfigure(5, weight=1)

            ttk.Label(right, text="Ключ ресурса:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_resource_key = ttk.Entry(right, textvariable=self.resource_key_var)
            self.entry_resource_key.grid(row=0, column=1, sticky="ew", pady=4)

            ttk.Label(right, text="Имя файла:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_resource_name = ttk.Entry(right, textvariable=self.resource_file_name_var)
            self.entry_resource_name.grid(row=1, column=1, sticky="ew", pady=4)

            ttk.Label(right, text="MIME тип:").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_resource_mime = ttk.Entry(right, textvariable=self.resource_mime_var)
            self.entry_resource_mime.grid(row=2, column=1, sticky="ew", pady=4)

            ttk.Label(right, text="Размер:").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
            ttk.Label(right, textvariable=self.resource_size_var).grid(row=3, column=1, sticky="w", pady=4)

            resource_actions = ttk.Frame(right)
            resource_actions.grid(row=4, column=1, sticky="w", pady=(4, 8))
            self.btn_pick_resource_file = ttk.Button(
                resource_actions,
                **self._button_kwargs("replace_file", "Заменить файл"),
                command=self._pick_file_for_resource_editor,
            )
            self.btn_pick_resource_file.pack(side="left")
            self.btn_apply_resource = ttk.Button(
                resource_actions,
                **self._button_kwargs("save", "Сохранить"),
                command=self._apply_resource_changes,
            )
            self.btn_apply_resource.pack(side="left", padx=(8, 0))
            self.btn_cancel_resource = ttk.Button(
                resource_actions,
                **self._button_kwargs("cancel", "Отменить"),
                command=self._reload_selected_resource,
            )
            self.btn_cancel_resource.pack(side="left", padx=(8, 0))

            preview_frame = ttk.LabelFrame(right, text="Просмотр ресурса")
            preview_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")
            preview_frame.columnconfigure(0, weight=1)
            preview_frame.rowconfigure(0, weight=1)

            self.resource_preview_image_label = tk.Label(
                preview_frame,
                text="Предпросмотр ресурса недоступен.\nВыберите запись из списка.",
                justify="center",
                anchor="center",
                relief="solid",
                borderwidth=1,
                padx=8,
                pady=8,
            )
            self.resource_preview_image_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)


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
                self._refresh_primary_source_preview_options()
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
            self._refresh_primary_source_preview_options()
            self._update_section_db_labels()

        def _refresh_resources_tree(self) -> None:
            self.resources_tree.delete(*self.resources_tree.get_children())
            for idx, row in enumerate(self.common_resources):
                self.resources_tree.insert(
                    "",
                    "end",
                    iid=str(idx),
                    values=(
                        row.key,
                        row.mime_type,
                        self._format_size(row.size_bytes),
                        row.file_name,
                    ),
                )


        def _on_resource_selected(self, _event: object) -> None:
            selection = self.resources_tree.selection()
            if not selection:
                self.selected_resource_index = None
                return
            self.selected_resource_index = int(selection[0])
            self._reload_selected_resource()

        def _reload_selected_resource(self) -> None:
            if self.selected_resource_index is None:
                self._clear_resource_editor()
                return
            if self.selected_resource_index < 0 or self.selected_resource_index >= len(self.common_resources):
                self._clear_resource_editor()
                return

            row = self.common_resources[self.selected_resource_index]
            payload = self._load_resource_payload_by_key(row.key)
            if payload is None:
                self._set_status(f"Не удалось загрузить ресурс '{row.key}' из общей БД.")
                return
            data, mime, file_name = payload
            self.selected_resource_original_key = row.key
            self.resource_data_buffer = data
            self.resource_key_var.set(row.key)
            self.resource_file_name_var.set(file_name)
            self.resource_mime_var.set(mime)
            self.resource_size_var.set(self._format_size(len(data)))
            self._render_resource_preview(data, mime, file_name, row.key)

        def _clear_resource_editor(self) -> None:
            self.selected_resource_index = None
            self.selected_resource_original_key = None
            self.resource_data_buffer = b""
            self.resource_key_var.set("")
            self.resource_file_name_var.set("")
            self.resource_mime_var.set("")
            self.resource_size_var.set("-")
            self.resource_preview_image = None
            self.resource_preview_image_label.configure(
                image="",
                text="Предпросмотр ресурса недоступен.\nВыберите запись из списка.",
            )

        def _add_resource_from_file(self) -> None:
            selected = filedialog.askopenfilename(
                parent=self,
                title="Выберите файл ресурса",
                initialdir=str(self.work_dir),
            )
            if not selected:
                return
            if not self._load_resource_file_into_editor(Path(selected), suggest_new_key=True):
                return
            selection = self.resources_tree.selection()
            if selection:
                self.resources_tree.selection_remove(*selection)
            self.selected_resource_index = None
            self.selected_resource_original_key = None
            self._set_status("Новый ресурс подготовлен. Проверьте поля и нажмите 'Сохранить'.")

        def _pick_file_for_resource_editor(self) -> None:
            selected = filedialog.askopenfilename(
                parent=self,
                title="Выберите файл ресурса",
                initialdir=str(self.work_dir),
            )
            if not selected:
                return
            if self._load_resource_file_into_editor(Path(selected), suggest_new_key=False):
                self._set_status("Файл ресурса обновлен. Нажмите 'Сохранить'.")

        def _load_resource_file_into_editor(self, path: Path, *, suggest_new_key: bool) -> bool:
            try:
                data = path.read_bytes()
            except OSError as exc:
                messagebox.showerror("Ошибка чтения", f"Не удалось прочитать файл:\n{exc}", parent=self)
                return False

            file_name = path.name
            mime = self._guess_mime_type(file_name)
            if suggest_new_key:
                key = self._suggest_resource_key(file_name, mime)
            else:
                key = self.resource_key_var.get().strip()
                if not key:
                    key = self._suggest_resource_key(file_name, mime)

            self.resource_data_buffer = data
            self.resource_key_var.set(key)
            self.resource_file_name_var.set(file_name)
            self.resource_mime_var.set(mime)
            self.resource_size_var.set(self._format_size(len(data)))
            self._render_resource_preview(data, mime, file_name, key)
            return True

        def _suggest_resource_key(self, file_name: str, mime_type: str) -> str:
            safe_file_name = re.sub(r"[^0-9A-Za-z._-]+", "_", file_name).strip("._")
            if not safe_file_name:
                safe_file_name = "resource.bin"
            folder = "topic-media" if self._is_graphic_resource(mime_type, file_name) else "files"
            base_key = f"{folder}/{safe_file_name}"
            return self._make_unique_resource_key(base_key, ignore_key=None)

        def _make_unique_resource_key(self, key: str, ignore_key: str | None) -> str:
            normalized_key = key.replace("\\", "/").lstrip("/")
            if not normalized_key:
                normalized_key = "resource.bin"
            existing = {row.key for row in self.common_resources}
            if ignore_key:
                existing.discard(ignore_key)
            if normalized_key not in existing:
                return normalized_key

            path_obj = Path(normalized_key)
            parent = "" if str(path_obj.parent) in ("", ".") else str(path_obj.parent).replace("\\", "/")
            stem = path_obj.stem or path_obj.name or "resource"
            suffix = path_obj.suffix
            counter = 2
            while True:
                candidate_name = f"{stem}_{counter}{suffix}"
                candidate_key = f"{parent}/{candidate_name}" if parent else candidate_name
                if candidate_key not in existing:
                    return candidate_key
                counter += 1

        def _apply_resource_changes(self) -> None:
            if self.common_connection is None or self.common_db_path is None:
                messagebox.showwarning("Нет общей БД", "Общая БД с ресурсами недоступна.", parent=self)
                return

            key = self.resource_key_var.get().strip().replace("\\", "/")
            if key.lower().startswith("dbres:"):
                key = key[len("dbres:"):].strip()
            key = key.lstrip("/")
            file_name = self.resource_file_name_var.get().strip()
            mime = self.resource_mime_var.get().strip().lower()

            if not key:
                messagebox.showwarning("Ошибка", "Ключ ресурса не может быть пустым.", parent=self)
                return
            if not file_name:
                file_name = Path(key).name or "resource.bin"
                self.resource_file_name_var.set(file_name)
            if not mime:
                mime = self._guess_mime_type(file_name)
                self.resource_mime_var.set(mime)

            data = self.resource_data_buffer
            if not data and self.selected_resource_original_key:
                payload = self._load_resource_payload_by_key(self.selected_resource_original_key)
                if payload is not None:
                    data = payload[0]
                    self.resource_data_buffer = data
            if not data:
                messagebox.showwarning(
                    "Нет файла",
                    "Для сохранения ресурса сначала выберите файл кнопкой 'Заменить файл' или 'Новый из файла'.",
                    parent=self,
                )
                return

            old_key = self.selected_resource_original_key
            duplicate = next((row for row in self.common_resources if row.key == key), None)
            if duplicate is not None and old_key != key:
                messagebox.showwarning(
                    "Дубликат",
                    f"Ресурс с ключом '{key}' уже существует в общей БД.",
                    parent=self,
                )
                return

            affected_topics = 0
            try:
                with self.common_connection:
                    if old_key and old_key != key:
                        self.common_connection.execute("DELETE FROM common_resources WHERE key = ?", (old_key,))
                    self.common_connection.execute(
                        """
                        INSERT OR REPLACE INTO common_resources(key, file_name, mime_type, data)
                        VALUES(?, ?, ?, ?)
                        """,
                        (key, file_name, mime, sqlite3.Binary(data)),
                    )
                    self._touch_common_db_data_version(connection=self.common_connection)
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить ресурс:\n{exc}", parent=self)
                return

            if old_key and old_key != key:
                for topic in self.articles:
                    if topic.id_icon == old_key:
                        topic.id_icon = key
                        affected_topics += 1
            topics_sync_failed = False
            if affected_topics > 0:
                if self.selected_article_index is not None:
                    self._reload_selected_article()
                if self.connection is not None and self.current_db_path is not None:
                    if not self._save_all(silent=True):
                        topics_sync_failed = True
                        self._restore_local_rows_after_save_error()

            self._load_common_resources()
            self._select_resource_by_key(key)
            self._update_file_info()
            self._set_status(
                (
                    f"Ресурс '{key}' сохранен в {self.common_db_path.stem}."
                    if affected_topics == 0
                    else (
                        f"Ресурс '{key}' сохранен. Обновлено иконок статей главного окна: {affected_topics}."
                        if not topics_sync_failed
                        else (
                            f"Ресурс '{key}' сохранен, но обновление иконок "
                            "в локализованной БД не удалось."
                        )
                    )
                )
            )

        def _delete_resource(self) -> None:
            if self.selected_resource_index is None:
                return
            if self.selected_resource_index < 0 or self.selected_resource_index >= len(self.common_resources):
                return

            row = self.common_resources[self.selected_resource_index]
            if not messagebox.askyesno(
                "Удаление ресурса",
                (
                    f"Удалить ресурс '{row.key}' из общей БД?\n\n"
                    "Если он используется в markdown или иконках, ссылки станут недействительными."
                ),
                parent=self,
            ):
                return

            if self.common_connection is None:
                messagebox.showwarning("Нет общей БД", "Общая БД с ресурсами недоступна.", parent=self)
                return

            try:
                with self.common_connection:
                    self.common_connection.execute("DELETE FROM common_resources WHERE key = ?", (row.key,))
                    self._touch_common_db_data_version(connection=self.common_connection)
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить ресурс:\n{exc}", parent=self)
                return

            affected_topics = 0
            for topic in self.articles:
                if topic.id_icon == row.key:
                    topic.id_icon = ""
                    affected_topics += 1
            topics_sync_failed = False
            if affected_topics > 0:
                if self.selected_article_index is not None:
                    self._reload_selected_article()
                if self.connection is not None and self.current_db_path is not None:
                    if not self._save_all(silent=True):
                        topics_sync_failed = True
                        self._restore_local_rows_after_save_error()

            self._load_common_resources()
            self._clear_resource_editor()
            self._update_file_info()
            suffix = (
                ""
                if affected_topics == 0
                else (
                    f" Иконки сброшены у {affected_topics} статьи(ей) главного окна."
                    if not topics_sync_failed
                    else " Но сохранить изменения иконок в локализованной БД не удалось."
                )
            )
            self._set_status(f"Ресурс '{row.key}' удален.{suffix}")

        def _select_resource_by_key(self, key: str) -> None:
            for idx, row in enumerate(self.common_resources):
                if row.key == key:
                    self.resources_tree.selection_set(str(idx))
                    self.resources_tree.focus(str(idx))
                    self.resources_tree.see(str(idx))
                    self.selected_resource_index = idx
                    self._reload_selected_resource()
                    return

        def _load_resource_payload_by_key(self, key: str) -> tuple[bytes, str, str] | None:
            if not key or self.common_connection is None:
                return None
            try:
                row = self.common_connection.execute(
                    """
                    SELECT data, mime_type, file_name
                    FROM common_resources
                    WHERE key = ?
                    LIMIT 1
                    """,
                    (key,),
                ).fetchone()
            except sqlite3.DatabaseError:
                return None
            if row is None:
                return None
            data = bytes(row["data"]) if row["data"] is not None else b""
            file_name = (row["file_name"] or "").strip() or (Path(key).name or "resource.bin")
            mime = (row["mime_type"] or "").strip().lower()
            if not mime:
                mime = self._guess_mime_type(file_name)
            return data, mime, file_name

        def _convert_svg_to_png_for_preview(self, svg_data: bytes) -> tuple[bytes | None, str | None]:
            try:
                cairosvg_module = __import__("cairosvg")
            except ModuleNotFoundError:
                return (
                    None,
                    "SVG предпросмотр недоступен: пакет cairosvg не установлен.\n"
                    "Установите: pip install cairosvg",
                )
            except Exception as exc:
                return None, self._format_svg_preview_error(exc)

            try:
                return cairosvg_module.svg2png(bytestring=svg_data), None
            except Exception as exc:
                return None, self._format_svg_preview_error(exc)

        def _format_svg_preview_error(self, exc: Exception) -> str:
            error_text = str(exc).strip()
            low = error_text.lower()
            if "cairo" in low and ("no library called" in low or "cannot load library" in low):
                return (
                    "SVG предпросмотр недоступен: пакет cairosvg найден, но системная библиотека Cairo недоступна.\n"
                    "Установите Cairo (Windows: libcairo-2.dll, например через GTK Runtime)."
                )
            if not error_text:
                return "SVG предпросмотр недоступен из-за ошибки рендера SVG."
            short_error = error_text.splitlines()[0]
            return f"SVG предпросмотр недоступен: {short_error}"

        def _convert_pdf_to_png_for_preview(self, pdf_data: bytes) -> tuple[bytes | None, str | None]:
            try:
                fitz_module = __import__("fitz")
            except ModuleNotFoundError:
                return (
                    None,
                    "PDF предпросмотр недоступен: пакет PyMuPDF не установлен.\n"
                    "Установите: pip install pymupdf",
                )
            except Exception as exc:
                return None, self._format_pdf_preview_error(exc)

            doc = None
            try:
                doc = fitz_module.open(stream=pdf_data, filetype="pdf")
                if doc.page_count == 0:
                    return None, "PDF предпросмотр недоступен: документ не содержит страниц."
                page = doc.load_page(0)
                matrix = fitz_module.Matrix(1.6, 1.6)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                return pix.tobytes("png"), None
            except Exception as exc:
                return None, self._format_pdf_preview_error(exc)
            finally:
                if doc is not None:
                    doc.close()

        def _format_pdf_preview_error(self, exc: Exception) -> str:
            error_text = str(exc).strip()
            if not error_text:
                return "PDF предпросмотр недоступен из-за ошибки рендера PDF."
            short_error = error_text.splitlines()[0]
            return f"PDF предпросмотр недоступен: {short_error}"

        def _try_set_preview_image_from_bytes(self, image_data: bytes) -> bool:
            if not image_data:
                return False

            if Image is not None and ImageTk is not None:
                try:
                    with Image.open(io.BytesIO(image_data)) as pil_image:
                        # Keep preview reasonably sized for the editor pane.
                        max_size = (860, 380)
                        resampling = (
                            Image.Resampling.LANCZOS
                            if hasattr(Image, "Resampling")
                            else Image.LANCZOS
                        )
                        preview_image = pil_image.copy()
                        preview_image.thumbnail(max_size, resampling)
                    self.resource_preview_image = ImageTk.PhotoImage(preview_image)
                    self.resource_preview_image_label.configure(image=self.resource_preview_image, text="")
                    return True
                except Exception:
                    pass

            try:
                encoded = base64.b64encode(image_data).decode("ascii")
                self.resource_preview_image = tk.PhotoImage(data=encoded)
                self.resource_preview_image_label.configure(image=self.resource_preview_image, text="")
                return True
            except tk.TclError:
                return False

        def _render_resource_preview(self, data: bytes, mime: str, file_name: str, key: str) -> None:
            self.resource_preview_image = None
            self.resource_preview_image_label.configure(image="")

            lower_mime = (mime or "").lower()
            is_pdf = lower_mime == "application/pdf" or Path(file_name).suffix.lower() == ".pdf"

            if self._is_graphic_resource(mime, file_name) and data:
                lower_mime = (mime or "").lower()
                is_svg = lower_mime.startswith("image/svg") or Path(file_name).suffix.lower() == ".svg"
                preview_data = data
                svg_error_message: str | None = None
                if is_svg:
                    converted_png, svg_error_message = self._convert_svg_to_png_for_preview(data)
                    if converted_png is not None:
                        preview_data = converted_png

                preview_loaded = self._try_set_preview_image_from_bytes(preview_data)

                if not preview_loaded:
                    if is_svg and svg_error_message:
                        self.resource_preview_image_label.configure(
                            text=svg_error_message,
                        )
                    else:
                        self.resource_preview_image_label.configure(
                            text=(
                                "Встроенный предпросмотр этого изображения недоступен в Tk.\n"
                                "Используйте кнопку 'Открыть ресурс'."
                            )
                        )
            elif is_pdf and data:
                png_data, pdf_error_message = self._convert_pdf_to_png_for_preview(data)
                preview_loaded = False
                if png_data is not None:
                    preview_loaded = self._try_set_preview_image_from_bytes(png_data)

                if not preview_loaded:
                    if pdf_error_message:
                        self.resource_preview_image_label.configure(text=pdf_error_message)
                    else:
                        self.resource_preview_image_label.configure(
                            text=(
                                "PDF предпросмотр недоступен во встроенном просмотре.\n"
                                "Используйте кнопку 'Открыть ресурс'."
                            )
                        )
            else:
                self.resource_preview_image_label.configure(
                    text=(
                        "Для этого типа файла используйте кнопки\n"
                        "'Открыть ресурс' или 'Экспорт...'."
                    )
                )

        def _resource_payload_from_editor_or_db(self) -> tuple[bytes, str, str, str] | None:
            key = self.resource_key_var.get().strip()
            file_name = self.resource_file_name_var.get().strip() or (Path(key).name if key else "resource.bin")
            mime = self.resource_mime_var.get().strip().lower() or self._guess_mime_type(file_name)
            data = self.resource_data_buffer
            if not data and key:
                payload = self._load_resource_payload_by_key(key)
                if payload is not None:
                    data, mime_from_db, file_name_from_db = payload
                    file_name = file_name_from_db
                    if not self.resource_mime_var.get().strip():
                        mime = mime_from_db
            if not data:
                return None
            return data, mime, file_name, key

        def _open_resource_external(self) -> None:
            payload = self._resource_payload_from_editor_or_db()
            if payload is None:
                messagebox.showinfo("Нет ресурса", "Выберите ресурс или загрузите файл в редактор.", parent=self)
                return
            data, mime, file_name, key = payload

            suffix = Path(file_name).suffix
            if not suffix:
                guessed_suffix = mimetypes.guess_extension(mime)
                suffix = guessed_suffix or ".bin"
            safe_name = re.sub(r"[^0-9A-Za-z._-]+", "_", Path(file_name).stem or "resource")
            temp_path = Path(tempfile.gettempdir()) / f"revelation_{safe_name}_{int(dt.datetime.now().timestamp())}{suffix}"
            try:
                temp_path.write_bytes(data)
            except OSError as exc:
                messagebox.showerror("Ошибка записи", f"Не удалось подготовить временный файл:\n{exc}", parent=self)
                return

            webbrowser.open(temp_path.resolve().as_uri())
            label = key or file_name
            self._set_status(f"Ресурс '{label}' открыт во внешнем приложении: {temp_path}")

        def _export_resource_to_file(self) -> None:
            payload = self._resource_payload_from_editor_or_db()
            if payload is None:
                messagebox.showinfo("Нет ресурса", "Выберите ресурс или загрузите файл в редактор.", parent=self)
                return
            data, _mime, file_name, key = payload

            target = filedialog.asksaveasfilename(
                parent=self,
                title="Сохранить ресурс как",
                initialdir=str(self.work_dir),
                initialfile=file_name,
                defaultextension=Path(file_name).suffix,
            )
            if not target:
                return
            try:
                Path(target).write_bytes(data)
            except OSError as exc:
                messagebox.showerror("Ошибка записи", f"Не удалось сохранить файл:\n{exc}", parent=self)
                return
            label = key or file_name
            self._set_status(f"Ресурс '{label}' сохранен в {target}")

        def _vacuum_common_resources_db(self) -> None:
            if self.common_connection is None or self.common_db_path is None:
                messagebox.showwarning("Нет общей БД", "Общая БД с ресурсами недоступна.", parent=self)
                return

            db_path = self.common_db_path
            before_stats = self._collect_sqlite_space_stats(
                db_path,
                connection=self.common_connection,
            )
            if not messagebox.askyesno(
                "Сжать БД",
                (
                    f"Выполнить VACUUM для '{db_path.name}'?\n\n"
                    "Операция перепакует файл БД и может занять время.\n"
                    "На время выполнения интерфейс будет недоступен."
                ),
                parent=self,
            ):
                return

            selected_key: str | None = None
            if self.selected_resource_index is not None and 0 <= self.selected_resource_index < len(self.common_resources):
                selected_key = self.common_resources[self.selected_resource_index].key

            try:
                _before, after_stats = self._run_vacuum_for_db(
                    db_path,
                    connection=self.common_connection,
                )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка VACUUM", f"Не удалось сжать БД:\n{exc}", parent=self)
                return

            self._load_common_resources()
            if selected_key:
                self._select_resource_by_key(selected_key)
            self._update_file_info()
            self._show_vacuum_result_dialog(
                db_path,
                before_stats,
                after_stats,
                title="VACUUM: общая БД",
            )

            before_size = int(before_stats["size_bytes"])
            after_size = int(after_stats["size_bytes"])
            reduced_size = before_size - after_size
            if reduced_size > 0:
                self._set_status(
                    (
                        f"VACUUM завершен: {db_path.stem}. "
                        f"{self._format_size(before_size)} -> {self._format_size(after_size)} "
                        f"(освобождено {self._format_size(reduced_size)})."
                    )
                )
                return

            self._set_status(
                (
                    f"VACUUM завершен: {db_path.stem}. "
                    f"{self._format_size(before_size)} -> {self._format_size(after_size)}."
                )
            )

        def _vacuum_current_localized_db(self) -> None:
            db_key = self.db_var.get()
            db_path = self.db_files.get(db_key)
            if db_path is None:
                db_path = self.current_db_path
            if db_path is None:
                messagebox.showwarning(
                    "Нет локализованной БД",
                    "Откройте локализованную БД, чтобы выполнить VACUUM.",
                    parent=self,
                )
                return

            local_connection: sqlite3.Connection | None = None
            if self.connection is not None and self.current_db_path == db_path:
                local_connection = self.connection

            before_stats = self._collect_sqlite_space_stats(
                db_path,
                connection=local_connection,
            )

            if not messagebox.askyesno(
                "Сжать локализованную БД",
                (
                    f"Выполнить VACUUM для '{db_path.name}'?\n\n"
                    "Операция перепакует файл БД и может занять время.\n"
                    "На время выполнения интерфейс будет недоступен."
                ),
                parent=self,
            ):
                return

            try:
                _before, after_stats = self._run_vacuum_for_db(
                    db_path,
                    connection=local_connection,
                )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror("Ошибка VACUUM", f"Не удалось сжать БД:\n{exc}", parent=self)
                return

            self._update_file_info()
            self._show_vacuum_result_dialog(
                db_path,
                before_stats,
                after_stats,
                title="VACUUM: локализованная БД",
            )

            before_size = int(before_stats["size_bytes"])
            after_size = int(after_stats["size_bytes"])
            reduced_size = before_size - after_size
            if reduced_size > 0:
                self._set_status(
                    (
                        f"VACUUM завершен: {db_path.stem}. "
                        f"{self._format_size(before_size)} -> {self._format_size(after_size)} "
                        f"(освобождено {self._format_size(reduced_size)})."
                    )
                )
                return

            self._set_status(
                (
                    f"VACUUM завершен: {db_path.stem}. "
                    f"{self._format_size(before_size)} -> {self._format_size(after_size)}."
                )
            )

        def _collect_sqlite_space_stats(
            self,
            db_path: Path,
            connection: sqlite3.Connection | None = None,
        ) -> dict[str, float]:
            con = connection
            own_connection = False
            if con is None:
                con = sqlite3.connect(db_path)
                own_connection = True

            try:
                page_size = int(con.execute("PRAGMA page_size").fetchone()[0])
                page_count = int(con.execute("PRAGMA page_count").fetchone()[0])
                freelist_count = int(con.execute("PRAGMA freelist_count").fetchone()[0])
            finally:
                if own_connection:
                    con.close()

            try:
                file_size = int(db_path.stat().st_size)
            except OSError:
                file_size = page_size * page_count

            free_bytes = page_size * freelist_count
            free_pct_pages = (100.0 * freelist_count / page_count) if page_count else 0.0
            free_pct_file = (100.0 * free_bytes / file_size) if file_size else 0.0

            return {
                "file_size": float(file_size),
                "page_size": float(page_size),
                "page_count": float(page_count),
                "freelist_count": float(freelist_count),
                "free_bytes": float(free_bytes),
                "free_pct_pages": free_pct_pages,
                "free_pct_file": free_pct_file,
                "size_bytes": float(file_size),
            }

        def _run_vacuum_for_db(
            self,
            db_path: Path,
            connection: sqlite3.Connection | None = None,
        ) -> tuple[dict[str, float], dict[str, float]]:
            before_stats = self._collect_sqlite_space_stats(db_path, connection=connection)

            con = connection
            own_connection = False
            if con is None:
                con = sqlite3.connect(db_path)
                own_connection = True

            try:
                con.commit()
                con.execute("VACUUM")
                if db_path.name.lower() == "revelation.sqlite":
                    self._touch_common_db_data_version(connection=con, db_path=db_path)
                else:
                    self._touch_localized_db_data_version(connection=con, db_path=db_path)
                con.commit()
            finally:
                if own_connection:
                    con.close()

            after_stats = self._collect_sqlite_space_stats(db_path, connection=connection)
            return before_stats, after_stats

        def _show_vacuum_result_dialog(
            self,
            db_path: Path,
            before_stats: dict[str, float],
            after_stats: dict[str, float],
            *,
            title: str = "VACUUM",
        ) -> None:
            before_size = int(before_stats["size_bytes"])
            after_size = int(after_stats["size_bytes"])
            reduced_size = before_size - after_size
            reduced_pct = (100.0 * reduced_size / before_size) if before_size > 0 and reduced_size > 0 else 0.0

            before_free_bytes = int(before_stats["free_bytes"])
            after_free_bytes = int(after_stats["free_bytes"])

            lines = [
                f"БД: {db_path.name}",
                "",
                (
                    "Размер файла: "
                    f"{self._format_size(before_size)} -> {self._format_size(after_size)}"
                ),
                (
                    "Свободных страниц: "
                    f"{self._format_size(before_free_bytes)} ({before_stats['free_pct_pages']:.2f}% страниц) -> "
                    f"{self._format_size(after_free_bytes)} ({after_stats['free_pct_pages']:.2f}% страниц)"
                ),
            ]
            if reduced_size > 0:
                lines.append(
                    f"Освобождено: {self._format_size(reduced_size)} ({reduced_pct:.2f}% от файла)."
                )
            else:
                lines.append("Освобождено: 0 B.")

            messagebox.showinfo(title, "\n".join(lines), parent=self)

        def _format_size(self, size_bytes: int) -> str:
            if size_bytes < 1024:
                return f"{size_bytes} B"
            size_kb = size_bytes / 1024
            if size_kb < 1024:
                return f"{size_kb:.1f} KB"
            size_mb = size_kb / 1024
            if size_mb < 1024:
                return f"{size_mb:.2f} MB"
            size_gb = size_mb / 1024
            return f"{size_gb:.2f} GB"


        def _load_common_resource(self, key: str) -> tuple[bytes, str] | None:
            if not key or self.common_connection is None:
                return None

            candidates = [key, key.lstrip("/")]
            for candidate in candidates:
                if not candidate:
                    continue
                try:
                    row = self.common_connection.execute(
                        """
                        SELECT data, mime_type, file_name
                        FROM common_resources
                        WHERE key = ?
                        LIMIT 1
                        """,
                        (candidate,),
                    ).fetchone()
                except sqlite3.DatabaseError:
                    return None
                if row is None:
                    continue
                data = bytes(row["data"]) if row["data"] is not None else b""
                mime = (row["mime_type"] or "").strip()
                if not mime:
                    mime = self._guess_mime_type(row["file_name"] or candidate)
                return data, mime
            return None

        def _load_project_asset(self, raw_path: str) -> tuple[bytes, str] | None:
            if not raw_path:
                return None
            normalized = urllib.parse.unquote(raw_path).replace("\\", "/").lstrip("/")
            relative_to_assets = normalized.removeprefix("assets/").lstrip("/")
            candidates = [
                self.project_root / normalized,
                self.project_root / "assets" / relative_to_assets,
            ]
            for path in candidates:
                if not path.exists() or not path.is_file():
                    continue
                try:
                    data = path.read_bytes()
                except OSError:
                    continue
                mime = self._guess_mime_type(path.name)
                return data, mime
            return None

        def _guess_mime_type(self, file_name: str) -> str:
            mime, _ = mimetypes.guess_type(file_name)
            return mime or "application/octet-stream"

        def _to_data_uri(self, data: bytes, mime_type: str) -> str:
            encoded = base64.b64encode(data).decode("ascii")
            mime = mime_type or "application/octet-stream"
            return f"data:{mime};base64,{encoded}"

        def _placeholder_image_data_uri(self, source: str) -> str:
            safe_source = source.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if len(safe_source) > 80:
                safe_source = f"{safe_source[:77]}..."
            svg = (
                "<svg xmlns='http://www.w3.org/2000/svg' width='820' height='90'>"
                "<rect width='100%' height='100%' fill='#fff4f4'/>"
                "<text x='12' y='30' fill='#9b1c1c' font-size='16'>Image source is unavailable</text>"
                f"<text x='12' y='58' fill='#5f5f5f' font-size='13'>{safe_source}</text>"
                "</svg>"
            )
            return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"
