from __future__ import annotations

import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from ..bible_map import BibleBook, BibleCatalog
from ..models import BibleModuleRow, BibleVerseRow


BIBLE_MODULE_DB_SCHEMA_VERSION = 3
BIBLE_INFO_FIELDS = (
    "code",
    "module_id",
    "title",
    "language",
    "canon",
    "versification",
    "license",
)


def bible_project_root() -> Path:
    """Return the repository root used by the content tool's Bible assets."""

    return Path(__file__).resolve().parents[3]


class BiblesMixin:
    def __init__(self, start_dir: Path) -> None:
        self.bible_catalog = BibleCatalog.load(bible_project_root())
        self.bible_files: dict[str, Path] = {}
        self.bible_connection: sqlite3.Connection | None = None
        self.current_bible_path: Path | None = None
        self.bible_module_info: BibleModuleRow | None = None
        self.bible_verse_rows: list[BibleVerseRow] = []
        self.bible_selected_verse_key: str | None = None
        self.bible_original_info_code = ""
        self.bible_pending_changes = False
        self._loading_bible_ui = False
        self._bible_controls: list[tuple[tk.Widget, bool]] = []
        super().__init__(start_dir)

    def _build_bibles_tab(self, parent: ttk.Frame) -> None:
        self.bible_module_var = tk.StringVar()
        self.bible_book_var = tk.StringVar()
        self.bible_chapter_var = tk.StringVar()
        self.bible_verse_var = tk.StringVar()
        self.bible_filter_var = tk.StringVar()
        self.bible_status_var = tk.StringVar(value="Модуль не выбран.")
        self.bible_info_vars = {field: tk.StringVar() for field in BIBLE_INFO_FIELDS}

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        module_frame = ttk.Frame(parent, padding=(8, 8, 8, 0))
        module_frame.grid(row=0, column=0, sticky="ew")
        module_frame.columnconfigure(1, weight=1)
        ttk.Label(module_frame, text="Библейский модуль:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.bible_module_combo = ttk.Combobox(
            module_frame,
            textvariable=self.bible_module_var,
            state="readonly",
        )
        self.bible_module_combo.grid(row=0, column=1, sticky="ew")
        self.bible_module_combo.bind("<<ComboboxSelected>>", self._on_bible_module_selected)
        self.btn_reload_bibles = ttk.Button(module_frame, text="Перечитать модули", command=self._reload_bibles_section)
        self.btn_reload_bibles.grid(row=0, column=2, padx=(8, 0))

        metadata_frame = ttk.LabelFrame(parent, text="Метаданные модуля", padding=8)
        metadata_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(8, 0))
        for column in (1, 3, 5):
            metadata_frame.columnconfigure(column, weight=1)
        metadata_labels = (
            ("code", "Код"),
            ("module_id", "ID модуля"),
            ("title", "Название"),
            ("language", "Язык"),
            ("canon", "Канон"),
            ("versification", "Версификация"),
            ("license", "Лицензия"),
        )
        for index, (field, label) in enumerate(metadata_labels):
            row, column = divmod(index, 3)
            ttk.Label(metadata_frame, text=f"{label}:").grid(
                row=row,
                column=column * 2,
                sticky="w",
                padx=(0, 6),
                pady=2,
            )
            entry = ttk.Entry(metadata_frame, textvariable=self.bible_info_vars[field])
            entry.grid(row=row, column=column * 2 + 1, sticky="ew", padx=(0, 12), pady=2)
            self._bible_controls.append((entry, False))

        long_metadata = ttk.Frame(metadata_frame)
        long_metadata.grid(row=3, column=0, columnspan=6, sticky="ew", pady=(4, 0))
        long_metadata.columnconfigure(1, weight=1)
        long_metadata.columnconfigure(3, weight=1)
        ttk.Label(long_metadata, text="Описание:").grid(row=0, column=0, sticky="nw", padx=(0, 6))
        self.bible_description_text = tk.Text(long_metadata, height=3, wrap="word", undo=True)
        self.bible_description_text.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        ttk.Label(long_metadata, text="Источники:").grid(row=0, column=2, sticky="nw", padx=(0, 6))
        self.bible_source_summary_text = tk.Text(long_metadata, height=3, wrap="word", undo=True)
        self.bible_source_summary_text.grid(row=0, column=3, sticky="ew")
        self._bible_controls.extend(
            [
                (self.bible_description_text, False),
                (self.bible_source_summary_text, False),
            ]
        )
        self.bible_description_text.bind("<<Modified>>", self._on_bible_text_modified)
        self.bible_source_summary_text.bind("<<Modified>>", self._on_bible_text_modified)
        for variable in self.bible_info_vars.values():
            variable.trace_add("write", self._on_bible_field_changed)

        reference_frame = ttk.Frame(parent, padding=(8, 8, 8, 0))
        reference_frame.grid(row=2, column=0, sticky="ew")
        reference_frame.columnconfigure(1, weight=2)
        reference_frame.columnconfigure(3, weight=1)
        reference_frame.columnconfigure(5, weight=1)
        reference_frame.columnconfigure(7, weight=1)
        ttk.Label(reference_frame, text="Книга:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.bible_book_combo = ttk.Combobox(reference_frame, textvariable=self.bible_book_var, state="readonly")
        self.bible_book_combo.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.bible_book_combo.bind("<<ComboboxSelected>>", self._on_bible_book_changed)
        ttk.Label(reference_frame, text="Глава:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.bible_chapter_combo = ttk.Combobox(reference_frame, textvariable=self.bible_chapter_var, state="readonly")
        self.bible_chapter_combo.grid(row=0, column=3, sticky="ew", padx=(0, 12))
        self.bible_chapter_combo.bind("<<ComboboxSelected>>", self._on_bible_chapter_changed)
        ttk.Label(reference_frame, text="Стих:").grid(row=0, column=4, sticky="w", padx=(0, 6))
        self.bible_verse_combo = ttk.Combobox(reference_frame, textvariable=self.bible_verse_var, state="readonly")
        self.bible_verse_combo.grid(row=0, column=5, sticky="ew", padx=(0, 12))
        self.bible_verse_combo.bind("<<ComboboxSelected>>", self._on_bible_verse_changed)
        ttk.Label(reference_frame, text="Фильтр:").grid(row=0, column=6, sticky="w", padx=(0, 6))
        self.bible_filter_entry = ttk.Entry(reference_frame, textvariable=self.bible_filter_var)
        self.bible_filter_entry.grid(row=0, column=7, sticky="ew")
        self.bible_filter_var.trace_add("write", self._on_bible_filter_changed)

        body = ttk.Panedwindow(parent, orient="vertical")
        body.grid(row=3, column=0, sticky="nsew", padx=8, pady=8)
        verses_frame = ttk.Frame(body)
        verses_frame.columnconfigure(0, weight=1)
        verses_frame.rowconfigure(0, weight=1)
        self.bible_verses_tree = ttk.Treeview(
            verses_frame,
            columns=("key", "reference", "text"),
            show="headings",
            selectmode="browse",
        )
        self.bible_verses_tree.heading("key", text="Ключ")
        self.bible_verses_tree.heading("reference", text="Ссылка")
        self.bible_verses_tree.heading("text", text="Текст")
        self.bible_verses_tree.column("key", width=80, stretch=False)
        self.bible_verses_tree.column("reference", width=210, stretch=False)
        self.bible_verses_tree.column("text", width=700, stretch=True)
        self.bible_verses_tree.grid(row=0, column=0, sticky="nsew")
        verse_scroll = ttk.Scrollbar(verses_frame, orient="vertical", command=self.bible_verses_tree.yview)
        verse_scroll.grid(row=0, column=1, sticky="ns")
        self.bible_verses_tree.configure(yscrollcommand=verse_scroll.set)
        self.bible_verses_tree.bind("<<TreeviewSelect>>", self._on_bible_tree_selected)
        body.add(verses_frame, weight=4)

        editor_frame = ttk.Frame(body, padding=(0, 8, 0, 0))
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(1, weight=1)
        ttk.Label(editor_frame, text="Редактирование текста выбранного стиха:").grid(row=0, column=0, sticky="w")
        self.bible_verse_text = tk.Text(editor_frame, height=5, wrap="word", undo=True)
        self.bible_verse_text.grid(row=1, column=0, sticky="nsew")
        self.bible_verse_text.bind("<<Modified>>", self._on_bible_text_modified)
        body.add(editor_frame, weight=1)

        actions = ttk.Frame(parent, padding=(8, 0, 8, 8))
        actions.grid(row=4, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        ttk.Label(actions, textvariable=self.bible_status_var, anchor="w").grid(row=0, column=0, sticky="ew")
        self.btn_save_bible = ttk.Button(actions, text="Сохранить модуль", command=self._save_bible_module)
        self.btn_save_bible.grid(row=0, column=1, padx=(8, 0))
        self.btn_reload_bible = ttk.Button(actions, text="Перечитать выбранный модуль", command=self._reload_selected_bible)
        self.btn_reload_bible.grid(row=0, column=2, padx=(8, 0))
        self._bible_controls.extend(
            [
                (self.bible_filter_entry, True),
                (self.btn_save_bible, False),
                (self.btn_reload_bible, True),
            ]
        )

    def _refresh_bible_list(self, initial_select: bool = False) -> None:
        self.bible_files = {
            path.name: path.resolve()
            for path in sorted(self.work_dir.glob("bible_*.sqlite"), key=lambda item: item.name.lower())
        }
        values = list(self.bible_files)
        self.bible_module_combo["values"] = values
        if not values:
            self._close_bible_connection()
            self.bible_module_var.set("")
            self._clear_bible_views()
            self.bible_status_var.set("В рабочей папке нет файлов bible_*.sqlite.")
            self._update_section_db_labels()
            self._set_bibles_controls_enabled(False)
            return

        previous = self.bible_module_var.get()
        selected = previous if previous in self.bible_files else values[0]
        self.bible_module_var.set(selected)
        if initial_select or self.current_bible_path is None or self.current_bible_path.name != selected:
            self._load_bible_db(self.bible_files[selected])

    def _on_bible_module_selected(self, _event: object | None = None) -> None:
        file_name = self.bible_module_var.get()
        path = self.bible_files.get(file_name)
        if path is None or (self.current_bible_path is not None and path == self.current_bible_path):
            return
        if not self._allow_switch_when_dirty():
            if self.current_bible_path is not None:
                self.bible_module_var.set(self.current_bible_path.name)
            return
        self._load_bible_db(path)

    def _load_bible_db(self, db_path: Path) -> None:
        self._close_bible_connection()
        try:
            connection = sqlite3.connect(str(db_path))
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """
                SELECT code, module_id, title, description, language, canon,
                       versification, license, source_summary
                FROM info
                LIMIT 1
                """
            ).fetchone()
            if row is None:
                raise ValueError("таблица info пуста")
        except (OSError, sqlite3.DatabaseError, ValueError) as exc:
            if "connection" in locals():
                connection.close()
            messagebox.showerror("Ошибка загрузки библейского модуля", f"{db_path.name}: {exc}", parent=self)
            self._clear_bible_views()
            return

        self.bible_connection = connection
        self.current_bible_path = db_path.resolve()
        self.bible_module_info = BibleModuleRow(
            file_name=db_path.name,
            code=str(row["code"]),
            module_id=str(row["module_id"]),
            title=str(row["title"]),
            description=str(row["description"]),
            language=str(row["language"]),
            canon=str(row["canon"]),
            versification=str(row["versification"]),
            license=str(row["license"]),
            source_summary=str(row["source_summary"]),
        )
        self.bible_original_info_code = self.bible_module_info.code
        self._loading_bible_ui = True
        try:
            for field in BIBLE_INFO_FIELDS:
                self.bible_info_vars[field].set(getattr(self.bible_module_info, field))
            self._replace_text(self.bible_description_text, self.bible_module_info.description)
            self._replace_text(self.bible_source_summary_text, self.bible_module_info.source_summary)
            self.bible_book_combo["values"] = [book.display_label() for book in self.bible_catalog.books]
            if self.bible_catalog.books:
                self.bible_book_var.set(self.bible_catalog.books[0].display_label())
            self._populate_bible_chapters()
        finally:
            self._loading_bible_ui = False
        self.bible_pending_changes = False
        self._set_dirty(False)
        self.bible_status_var.set(
            f"{self.bible_module_info.title} | {self.bible_module_info.language} | {self.current_bible_path.name}"
        )
        self._update_section_db_labels()
        self._set_bibles_controls_enabled(True)
        self._update_file_info()

    def _populate_bible_chapters(self) -> None:
        book = self._selected_bible_book()
        if book is None:
            self.bible_chapter_combo["values"] = []
            self.bible_verse_combo["values"] = []
            self.bible_chapter_var.set("")
            self.bible_verse_var.set("")
            self._refresh_bible_verse_rows()
            return
        self._loading_bible_ui = True
        try:
            self.bible_chapter_combo["values"] = [str(index) for index in range(1, book.chapter_count + 1)]
            self.bible_chapter_var.set("1")
            self._populate_bible_verses()
        finally:
            self._loading_bible_ui = False

    def _populate_bible_verses(self) -> None:
        book = self._selected_bible_book()
        try:
            chapter = int(self.bible_chapter_var.get())
        except ValueError:
            chapter = 0
        if book is None or chapter < 1 or chapter > book.chapter_count:
            self.bible_verse_combo["values"] = []
            self.bible_verse_var.set("")
            self._refresh_bible_verse_rows()
            return
        values = [str(index) for index in range(1, book.chapters[chapter - 1] + 1)]
        self._loading_bible_ui = True
        try:
            self.bible_verse_combo["values"] = values
            self.bible_verse_var.set(values[0] if values else "")
        finally:
            self._loading_bible_ui = False
        self._refresh_bible_verse_rows()

    def _refresh_bible_verse_rows(self) -> None:
        self.bible_verses_tree.delete(*self.bible_verses_tree.get_children())
        self.bible_verse_rows = []
        book = self._selected_bible_book()
        try:
            chapter = int(self.bible_chapter_var.get())
        except ValueError:
            chapter = 0
        if self.bible_connection is None or book is None or chapter < 1:
            self._clear_bible_verse_editor()
            return
        keys = self.bible_catalog.verse_keys_for_chapter(book_id=book.id, chapter=chapter)
        if not keys:
            return
        rows = self.bible_connection.execute(
            "SELECT verse_key, text FROM verses WHERE verse_key >= ? AND verse_key <= ? ORDER BY verse_key",
            (keys[0], keys[-1]),
        ).fetchall()
        text_by_key = {str(row["verse_key"]): str(row["text"] or "") for row in rows}
        filter_text = self.bible_filter_var.get().strip().casefold()
        selected_key = None
        try:
            selected_verse = int(self.bible_verse_var.get())
        except ValueError:
            selected_verse = 0
        for index, key in enumerate(keys, start=1):
            text = text_by_key.get(key, "")
            reference = f"{book.name} {chapter}:{index}"
            if filter_text and filter_text not in f"{key} {reference} {text}".casefold():
                continue
            row = BibleVerseRow(verse_key=key, reference=reference, text=text)
            self.bible_verse_rows.append(row)
            self.bible_verses_tree.insert("", "end", iid=key, values=(key, reference, text))
            if index == selected_verse:
                selected_key = key

        if selected_key is None and self.bible_verse_rows:
            selected_key = self.bible_verse_rows[0].verse_key
        if selected_key is not None:
            self._loading_bible_ui = True
            try:
                self.bible_verse_var.set(str(self.bible_catalog.reference_for_key(selected_key)[2]))
                self.bible_verses_tree.selection_set(selected_key)
                self.bible_verses_tree.focus(selected_key)
                self.bible_verses_tree.see(selected_key)
            finally:
                self._loading_bible_ui = False
            self._load_bible_verse_editor(selected_key)
        else:
            self._clear_bible_verse_editor()

    def _load_bible_verse_editor(self, verse_key: str) -> None:
        row = next((item for item in self.bible_verse_rows if item.verse_key == verse_key), None)
        if row is None:
            return
        self.bible_selected_verse_key = verse_key
        self._replace_text(self.bible_verse_text, row.text)

    def _on_bible_tree_selected(self, _event: object | None = None) -> None:
        selection = self.bible_verses_tree.selection()
        if not selection:
            return
        verse_key = selection[0]
        reference = self.bible_catalog.reference_for_key(verse_key)
        if reference is None:
            return
        if self.bible_pending_changes and not self._allow_switch_when_dirty():
            if self.bible_selected_verse_key:
                self.bible_verses_tree.selection_set(self.bible_selected_verse_key)
            return
        self._loading_bible_ui = True
        try:
            self.bible_verse_var.set(str(reference[2]))
        finally:
            self._loading_bible_ui = False
        self._load_bible_verse_editor(verse_key)

    def _on_bible_module_changed_after_navigation(self) -> None:
        if self.bible_pending_changes:
            self._save_bible_module(silent=True)

    def _on_bible_book_changed(self, _event: object | None = None) -> None:
        if self._loading_bible_ui:
            return
        if self.bible_pending_changes and not self._allow_switch_when_dirty():
            return
        self._populate_bible_chapters()

    def _on_bible_chapter_changed(self, _event: object | None = None) -> None:
        if self._loading_bible_ui:
            return
        if self.bible_pending_changes and not self._allow_switch_when_dirty():
            return
        self._populate_bible_verses()

    def _on_bible_verse_changed(self, _event: object | None = None) -> None:
        if self._loading_bible_ui:
            return
        if self.bible_pending_changes and not self._allow_switch_when_dirty():
            return
        self._refresh_bible_verse_rows()

    def _on_bible_filter_changed(self, *_args: object) -> None:
        if not self._loading_bible_ui:
            self._refresh_bible_verse_rows()

    def _on_bible_field_changed(self, *_args: object) -> None:
        if not self._loading_bible_ui:
            self._mark_bible_pending_change()

    def _on_bible_text_modified(self, event: tk.Event[tk.Text]) -> None:
        widget = event.widget
        try:
            modified = bool(widget.edit_modified())
            widget.edit_modified(False)
        except tk.TclError:
            return
        if modified and not self._loading_bible_ui:
            self._mark_bible_pending_change()

    def _mark_bible_pending_change(self) -> None:
        if self.current_bible_path is None:
            return
        self.bible_pending_changes = True
        self._set_dirty(True)
        self.bible_status_var.set("Есть несохранённые изменения библейского модуля.")

    def _save_bible_module(self, *, silent: bool = False) -> bool:
        if self.bible_connection is None or self.current_bible_path is None or self.bible_module_info is None:
            if not silent:
                messagebox.showwarning("Нет модуля", "Сначала выберите библейский модуль.", parent=self)
            return False
        values = {field: self.bible_info_vars[field].get().strip() for field in BIBLE_INFO_FIELDS}
        if any(not values[field] for field in BIBLE_INFO_FIELDS):
            if not silent:
                messagebox.showwarning("Неполные метаданные", "Поля метаданных не должны быть пустыми.", parent=self)
            return False
        description = self.bible_description_text.get("1.0", "end-1c")
        source_summary = self.bible_source_summary_text.get("1.0", "end-1c")
        verse_key = self.bible_selected_verse_key
        verse_text = self.bible_verse_text.get("1.0", "end-1c")
        try:
            with self.bible_connection:
                self.bible_connection.execute(
                    """
                    UPDATE info
                    SET code = ?, module_id = ?, title = ?, description = ?, language = ?,
                        canon = ?, versification = ?, license = ?, source_summary = ?
                    WHERE code = ?
                    """,
                    (
                        values["code"],
                        values["module_id"],
                        values["title"],
                        description,
                        values["language"],
                        values["canon"],
                        values["versification"],
                        values["license"],
                        source_summary,
                        self.bible_original_info_code,
                    ),
                )
                if verse_key is not None:
                    self.bible_connection.execute(
                        "UPDATE verses SET text = ? WHERE verse_key = ?",
                        (verse_text, verse_key),
                    )
                self._touch_db_data_version(
                    self.current_bible_path,
                    schema_version=BIBLE_MODULE_DB_SCHEMA_VERSION,
                    connection=self.bible_connection,
                    increment_data_version=True,
                )
        except (sqlite3.DatabaseError, ValueError) as exc:
            if not silent:
                messagebox.showerror("Ошибка сохранения", str(exc), parent=self)
            return False

        self.bible_original_info_code = values["code"]
        self.bible_pending_changes = False
        self._set_dirty(False)
        self._load_bible_db(self.current_bible_path)
        if not silent:
            self._set_status(f"Сохранено: {self.current_bible_path.name}")
        return True

    def _save_bible_pending_changes(self, *, silent: bool = False) -> bool:
        if not self.bible_pending_changes:
            return True
        return self._save_bible_module(silent=silent)

    def _reload_bibles_section(self) -> None:
        if self.bible_pending_changes and not self._allow_switch_when_dirty():
            return
        self._refresh_bible_list(initial_select=True)
        self._set_status(f"Библейские модули перечитаны: {len(self.bible_files)}.")

    def _reload_selected_bible(self) -> None:
        if self.current_bible_path is None:
            return
        if self.bible_pending_changes and not self._allow_switch_when_dirty():
            return
        self._load_bible_db(self.current_bible_path)

    def _selected_bible_book(self) -> BibleBook | None:
        return self.bible_catalog.book_for_value(self.bible_book_var.get())

    def _clear_bible_verse_editor(self) -> None:
        self.bible_selected_verse_key = None
        self._replace_text(self.bible_verse_text, "")

    def _clear_bible_views(self) -> None:
        self.bible_module_info = None
        self.bible_selected_verse_key = None
        self.bible_verse_rows = []
        self._loading_bible_ui = True
        try:
            self.bible_book_combo["values"] = []
            self.bible_chapter_combo["values"] = []
            self.bible_verse_combo["values"] = []
            self.bible_book_var.set("")
            self.bible_chapter_var.set("")
            self.bible_verse_var.set("")
            for field in BIBLE_INFO_FIELDS:
                self.bible_info_vars[field].set("")
            self._replace_text(self.bible_description_text, "")
            self._replace_text(self.bible_source_summary_text, "")
            self._replace_text(self.bible_verse_text, "")
        finally:
            self._loading_bible_ui = False
        self.bible_verses_tree.delete(*self.bible_verses_tree.get_children())

    def _replace_text(self, widget: tk.Text, value: str) -> None:
        previous_state = str(widget.cget("state"))
        if previous_state == "disabled":
            widget.configure(state="normal")
        try:
            widget.delete("1.0", "end")
            widget.insert("1.0", value)
            widget.edit_modified(False)
        finally:
            if previous_state == "disabled":
                widget.configure(state="disabled")

    def _close_bible_connection(self) -> None:
        if self.bible_connection is not None:
            self.bible_connection.close()
            self.bible_connection = None
        self.current_bible_path = None

    def _set_bibles_controls_enabled(self, enabled: bool) -> None:
        for widget, readonly_when_enabled in self._bible_controls:
            if isinstance(widget, ttk.Combobox):
                widget.configure(state="readonly" if enabled else "disabled")
            elif isinstance(widget, ttk.Entry):
                widget.configure(state="normal" if enabled else "disabled")
            elif isinstance(widget, tk.Text):
                widget.configure(state="normal" if enabled else "disabled")
            else:
                widget.configure(state="normal" if enabled else "disabled")
        for widget in (self.bible_module_combo, self.bible_book_combo, self.bible_chapter_combo, self.bible_verse_combo):
            widget.configure(state="readonly" if enabled else "disabled")
        self.btn_reload_bibles.configure(state="normal")
