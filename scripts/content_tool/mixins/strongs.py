from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from ..helpers import (
    GREEK_DESC_GROUP_RANGES,
    GREEK_DESC_TRANSLATION_PROMPT_HEADER,
    clean_greek_desc_for_prompt,
    target_language_name_ru,
)
from ..models import MarkdownTemplateSpec, StrongRow


class StrongsMixin:
        def _load_ru_strong_category_labels(self) -> dict[str, str]:
            labels: dict[str, str] = {}
            ru_arb_path = self.project_root / "lib" / "l10n" / "app_ru.arb"
            try:
                payload = json.loads(ru_arb_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return labels

            for key, value in payload.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    continue
                if not key.startswith("strong_"):
                    continue
                if key.startswith("@"):
                    continue
                token = key.removeprefix("strong_")
                if token:
                    labels[token] = value.strip()
            return labels

        def _localized_db_entries(self) -> list[tuple[str, Path]]:
            seen_langs: set[str] = set()
            entries: list[tuple[str, Path]] = []
            for display_key, db_path in sorted(self.db_files.items(), key=lambda item: item[0]):
                lang = display_key.split("  ", maxsplit=1)[0].strip().lower()
                if not lang:
                    continue
                lang = lang[:2]
                if lang in seen_langs:
                    continue
                seen_langs.add(lang)
                entries.append((lang, db_path))
            return entries

        def _rebuild_strong_tree_columns(self) -> None:
            if not hasattr(self, "strong_tree"):
                return
            language_columns = [lang for lang, _ in self._localized_db_entries()]
            self.strong_tree_lang_columns = language_columns
            columns: tuple[str, ...] = ("id", "word", "synonyms", "origin", "category", *language_columns)
            try:
                # Reset previous display columns first to avoid stale dynamic indexes.
                self.strong_tree.configure(displaycolumns="#all")
            except tk.TclError:
                pass
            self.strong_tree.configure(columns=columns)
            self.strong_tree.configure(displaycolumns=columns)

            self.strong_tree.heading("id", text="Strong")
            self.strong_tree.heading("word", text="Слово")
            self.strong_tree.heading("synonyms", text="Синонимы")
            self.strong_tree.heading("origin", text="Анализ слова")
            self.strong_tree.heading("category", text="Часть речи и форма")
            base_word_col_width = 160
            self.strong_tree.column("id", width=base_word_col_width // 2, anchor="center")
            self.strong_tree.column("word", width=base_word_col_width, anchor="w")
            self.strong_tree.column("synonyms", width=base_word_col_width, anchor="w")
            self.strong_tree.column("origin", width=base_word_col_width, anchor="w")
            self.strong_tree.column("category", width=base_word_col_width * 2, anchor="w")

            for lang in language_columns:
                self.strong_tree.heading(lang, text=lang.upper())
                self.strong_tree.column(lang, width=base_word_col_width // 4, anchor="center")

        def _rebuild_strong_localized_editors(self) -> None:
            self.strong_desc_texts_by_lang.clear()
            self.strong_local_db_paths_by_lang.clear()

            if not hasattr(self, "strong_local_container"):
                return

            for child in self.strong_local_container.winfo_children():
                child.destroy()

            entries = self._localized_db_entries()
            self.strong_local_container.columnconfigure(0, weight=1)
            if not entries:
                ttk.Label(
                    self.strong_local_container,
                    text="Локализованные БД не найдены.",
                    foreground="#5f5f5f",
                    padding=(6, 6),
                ).grid(row=0, column=0, sticky="w")
                self._on_strong_local_container_configure()
                if self.strong_group_dialog is not None and self.strong_group_dialog.winfo_exists():
                    self._refresh_strong_group_target_options()
                    self._refresh_strong_group_status_rows()
                return

            for idx, (lang, db_path) in enumerate(entries):
                self.strong_local_db_paths_by_lang[lang] = db_path
                row_wrap = ttk.Frame(self.strong_local_container)
                row_wrap.grid(row=idx, column=0, sticky="nsew", padx=4, pady=(0, 8))
                row_wrap.columnconfigure(1, weight=1)
                row_wrap.rowconfigure(0, weight=1)

                ttk.Label(
                    row_wrap,
                    text=lang.upper(),
                    width=4,
                    anchor="nw",
                ).grid(row=0, column=0, sticky="nw", padx=(0, 8), pady=(2, 0))

                text_widget = tk.Text(row_wrap, wrap="word", undo=True, height=6)
                text_widget.grid(row=0, column=1, sticky="nsew")
                scroll = ttk.Scrollbar(row_wrap, orient="vertical", command=text_widget.yview)
                scroll.grid(row=0, column=2, sticky="ns")
                text_widget.configure(yscrollcommand=scroll.set)
                self.strong_desc_texts_by_lang[lang] = text_widget

            self._on_strong_local_container_configure()
            if self.strong_group_dialog is not None and self.strong_group_dialog.winfo_exists():
                self._refresh_strong_group_target_options()
                self._refresh_strong_group_status_rows()

        def _on_strong_local_container_configure(self, _event: object | None = None) -> None:
            if not hasattr(self, "strong_local_canvas"):
                return
            self.strong_local_canvas.configure(scrollregion=self.strong_local_canvas.bbox("all"))

        def _on_strong_local_canvas_configure(self, event: tk.Event[tk.Misc]) -> None:
            if not hasattr(self, "strong_local_canvas"):
                return
            if not hasattr(self, "strong_local_window_id"):
                return
            self.strong_local_canvas.itemconfigure(self.strong_local_window_id, width=event.width)

        def _open_strong_group_translation_dialog(self) -> None:
            entries = self._localized_db_entries()
            if not entries:
                messagebox.showwarning(
                    "Нет локализованных БД",
                    "Сначала подключите локализованные БД, чтобы работать с групповым переводом.",
                    parent=self,
                )
                return

            if self.strong_group_dialog is not None and self.strong_group_dialog.winfo_exists():
                self.strong_group_dialog.deiconify()
                self.strong_group_dialog.lift()
                self.strong_group_dialog.focus_set()
                self._refresh_strong_group_target_options()
                self._refresh_strong_group_status_rows()
                return

            dialog = tk.Toplevel(self)
            self.strong_group_dialog = dialog
            dialog.title("Групповой перевод greek_descs")
            dialog.geometry("1420x860")
            dialog.minsize(1120, 680)
            dialog.transient(self)
            dialog.protocol("WM_DELETE_WINDOW", self._close_strong_group_translation_dialog)

            root = ttk.Frame(dialog, padding=10)
            root.grid(row=0, column=0, sticky="nsew")
            dialog.columnconfigure(0, weight=1)
            dialog.rowconfigure(0, weight=1)
            root.columnconfigure(0, weight=1)
            root.columnconfigure(1, weight=1)
            root.rowconfigure(1, weight=1)

            controls = ttk.Frame(root)
            controls.grid(row=0, column=0, columnspan=2, sticky="ew")
            controls.columnconfigure(1, weight=1)
            controls.columnconfigure(6, weight=1)

            ttk.Label(controls, text="Источник для промпта:").grid(row=0, column=0, sticky="w", padx=(0, 8))
            ttk.Label(controls, textvariable=self.strong_group_source_info_var).grid(row=0, column=1, sticky="w")
            ttk.Label(controls, text="Целевая БД (импорт):").grid(row=0, column=2, sticky="w", padx=(16, 8))
            self.strong_group_target_combo = ttk.Combobox(
                controls,
                textvariable=self.strong_group_target_lang_var,
                state="readonly",
                width=8,
            )
            self.strong_group_target_combo.grid(row=0, column=3, sticky="w")
            self.strong_group_target_combo.bind("<<ComboboxSelected>>", self._on_strong_group_target_lang_changed)
            self._refresh_strong_group_target_options()
            ttk.Label(controls, text="Целевой язык:").grid(row=0, column=4, sticky="w", padx=(12, 6))
            ttk.Entry(
                controls,
                textvariable=self.strong_group_target_lang_name_var,
                state="readonly",
                width=22,
            ).grid(row=0, column=5, sticky="w")
            ttk.Button(
                controls,
                text="Обновить статус групп",
                command=self._refresh_strong_group_status_rows,
            ).grid(row=0, column=6, sticky="e", padx=(16, 0))
            ttk.Label(controls, textvariable=self.strong_group_selected_label_var).grid(
                row=1,
                column=0,
                columnspan=7,
                sticky="w",
                pady=(6, 0),
            )

            body = ttk.Frame(root)
            body.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
            body.columnconfigure(0, weight=1)
            body.columnconfigure(1, weight=1)
            body.rowconfigure(0, weight=1)

            groups_box = ttk.LabelFrame(body, text="Переводы номеров Стронга.")
            groups_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
            groups_box.columnconfigure(0, weight=1)
            groups_box.rowconfigure(0, weight=1)

            groups_canvas = tk.Canvas(groups_box, highlightthickness=0, borderwidth=0)
            groups_canvas.grid(row=0, column=0, sticky="nsew")
            groups_scroll = ttk.Scrollbar(groups_box, orient="vertical", command=groups_canvas.yview)
            groups_scroll.grid(row=0, column=1, sticky="ns")
            groups_canvas.configure(yscrollcommand=groups_scroll.set)

            rows_wrap = ttk.Frame(groups_canvas)
            rows_window = groups_canvas.create_window((0, 0), window=rows_wrap, anchor="nw")
            rows_wrap.bind("<Configure>", lambda _event: groups_canvas.configure(scrollregion=groups_canvas.bbox("all")))
            groups_canvas.bind(
                "<Configure>",
                lambda event: groups_canvas.itemconfigure(rows_window, width=event.width),
            )

            rows_wrap.columnconfigure(2, weight=1)
            rows_wrap.columnconfigure(3, weight=1)
            ttk.Label(rows_wrap, text="✓", anchor="center").grid(row=0, column=0, sticky="ew", padx=(4, 8), pady=(4, 6))
            ttk.Label(rows_wrap, text="#", anchor="center").grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(4, 6))
            ttk.Label(rows_wrap, text="Диапазоны номеров Стронга.", anchor="w").grid(
                row=0,
                column=2,
                sticky="ew",
                padx=(0, 8),
                pady=(4, 6),
            )
            ttk.Label(rows_wrap, text="Переведено", anchor="center").grid(
                row=0,
                column=3,
                sticky="ew",
                padx=(0, 8),
                pady=(4, 6),
            )
            ttk.Label(rows_wrap, text="Действие", anchor="center").grid(
                row=0,
                column=4,
                sticky="ew",
                padx=(0, 8),
                pady=(4, 6),
            )

            self.strong_group_status_labels_by_index.clear()
            self.strong_group_progress_labels_by_index.clear()
            for index, (start_id, end_id) in enumerate(GREEK_DESC_GROUP_RANGES):
                row_index = index + 1
                status_label = ttk.Label(rows_wrap, text="□", anchor="center")
                status_label.grid(row=row_index, column=0, sticky="ew", padx=(4, 8), pady=3)
                self.strong_group_status_labels_by_index[index] = status_label

                ttk.Label(rows_wrap, text=f"{row_index:02d}", anchor="center").grid(
                    row=row_index,
                    column=1,
                    sticky="ew",
                    padx=(0, 8),
                    pady=3,
                )
                ttk.Label(rows_wrap, text=f"{start_id}-{end_id}", anchor="w").grid(
                    row=row_index,
                    column=2,
                    sticky="ew",
                    padx=(0, 8),
                    pady=3,
                )
                progress_label = ttk.Label(rows_wrap, text="-/-", anchor="center")
                progress_label.grid(row=row_index, column=3, sticky="ew", padx=(0, 8), pady=3)
                self.strong_group_progress_labels_by_index[index] = progress_label
                ttk.Button(
                    rows_wrap,
                    text="Подготовить промпт",
                    command=lambda idx=index: self._prepare_strong_group_prompt(idx),
                ).grid(row=row_index, column=4, sticky="ew", padx=(0, 8), pady=2)

            right_column = ttk.Frame(body)
            right_column.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
            right_column.columnconfigure(0, weight=1)
            right_column.rowconfigure(0, weight=1)
            right_column.rowconfigure(1, weight=1)

            prompt_box = ttk.LabelFrame(right_column, text="Готовый промпт")
            prompt_box.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
            prompt_box.columnconfigure(0, weight=1)
            prompt_box.rowconfigure(1, weight=1)
            prompt_actions = ttk.Frame(prompt_box)
            prompt_actions.grid(row=0, column=0, sticky="w", padx=6, pady=(6, 2))
            ttk.Button(prompt_actions, text="Копировать промпт", command=self._copy_strong_group_prompt_to_clipboard).pack(
                side="left"
            )
            self.strong_group_prompt_text = tk.Text(prompt_box, wrap="word", undo=True)
            self.strong_group_prompt_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 6))
            prompt_scroll = ttk.Scrollbar(prompt_box, orient="vertical", command=self.strong_group_prompt_text.yview)
            prompt_scroll.grid(row=1, column=1, sticky="ns", pady=(2, 6), padx=(0, 6))
            self.strong_group_prompt_text.configure(yscrollcommand=prompt_scroll.set)

            response_box = ttk.LabelFrame(right_column, text="Ответ ИИ (вставьте JSON)")
            response_box.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
            response_box.columnconfigure(0, weight=1)
            response_box.rowconfigure(1, weight=1)
            response_actions = ttk.Frame(response_box)
            response_actions.grid(row=0, column=0, sticky="w", padx=6, pady=(6, 2))
            ttk.Button(
                response_actions,
                text="Вставить из буфера",
                command=self._paste_strong_group_response_from_clipboard,
            ).pack(side="left")
            ttk.Button(
                response_actions,
                text="Очистить",
                command=self._clear_strong_group_response_text,
            ).pack(side="left", padx=(8, 0))
            ttk.Button(
                response_actions,
                text="Импортировать ответ в целевую БД",
                command=self._import_strong_group_response,
            ).pack(side="left", padx=(8, 0))
            self.strong_group_response_text = tk.Text(response_box, wrap="word", undo=True)
            self.strong_group_response_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=(2, 6))
            response_scroll = ttk.Scrollbar(response_box, orient="vertical", command=self.strong_group_response_text.yview)
            response_scroll.grid(row=1, column=1, sticky="ns", pady=(2, 6), padx=(0, 6))
            self.strong_group_response_text.configure(yscrollcommand=response_scroll.set)

            bottom = ttk.Frame(root)
            bottom.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))
            ttk.Button(bottom, text="Закрыть", command=self._close_strong_group_translation_dialog).pack(side="right")

            self.strong_group_current_index = None
            self.strong_group_selected_label_var.set("Группа не выбрана.")
            if self.strong_group_prompt_text is not None:
                self._set_text_widget_content(self.strong_group_prompt_text, "")
            if self.strong_group_response_text is not None:
                self._set_text_widget_content(self.strong_group_response_text, "")
            self._refresh_strong_group_status_rows()

        def _close_strong_group_translation_dialog(self) -> None:
            if self.strong_group_dialog is not None and self.strong_group_dialog.winfo_exists():
                self.strong_group_dialog.destroy()
            self.strong_group_dialog = None
            self.strong_group_target_combo = None
            self.strong_group_prompt_text = None
            self.strong_group_response_text = None
            self.strong_group_current_index = None
            self.strong_group_status_labels_by_index.clear()
            self.strong_group_progress_labels_by_index.clear()

        def _refresh_strong_group_target_options(self) -> None:
            if self.strong_group_target_combo is None:
                return
            languages = [lang for lang, _ in self._localized_db_entries() if lang != "en"]
            self.strong_group_target_combo.configure(values=languages)
            if not languages:
                self.strong_group_target_lang_var.set("")
                self.strong_group_target_lang_name_var.set("-")
                return

            current_lang = self.strong_group_target_lang_var.get().strip().lower()
            if current_lang not in languages:
                self.strong_group_target_lang_var.set(self._default_strong_group_target_lang(languages))
            self._sync_strong_group_target_language_name()

        def _default_strong_group_target_lang(self, languages: list[str]) -> str:
            if not languages:
                return ""
            current_lang = self._lang_for_db_path(self.current_db_path)
            if current_lang in languages and current_lang != "en":
                return current_lang
            for lang in languages:
                if lang != "en":
                    return lang
            return languages[0]

        def _lang_for_db_path(self, db_path: Path | None) -> str | None:
            if db_path is None:
                return None
            for lang, path in self._localized_db_entries():
                try:
                    if path.resolve() == db_path.resolve():
                        return lang
                except OSError:
                    continue
            return None

        def _resolve_strong_group_source_db(self) -> tuple[str, Path] | None:
            entries = self._localized_db_entries()
            for lang, db_path in entries:
                if lang == "en":
                    return lang, db_path
            return entries[0] if entries else None

        def _resolve_strong_group_target_db(self) -> tuple[str, Path] | None:
            lang = self.strong_group_target_lang_var.get().strip().lower()
            if not lang or lang == "en":
                return None
            db_path = self.strong_local_db_paths_by_lang.get(lang)
            if db_path is None:
                for candidate_lang, candidate_path in self._localized_db_entries():
                    if candidate_lang == lang:
                        db_path = candidate_path
                        break
            if db_path is None:
                return None
            return lang, db_path

        def _on_strong_group_target_lang_changed(self, _event: object | None = None) -> None:
            self._sync_strong_group_target_language_name()
            self._refresh_strong_group_status_rows()

        def _sync_strong_group_target_language_name(self) -> None:
            lang = self.strong_group_target_lang_var.get().strip().lower()
            self.strong_group_target_lang_name_var.set(target_language_name_ru(lang))

        def _install_global_text_shortcuts(self) -> None:
            for class_name in ("Text", "Entry", "TEntry", "TCombobox"):
                self.bind_class(class_name, "<Control-a>", self._on_text_shortcut_select_all)
                self.bind_class(class_name, "<Control-A>", self._on_text_shortcut_select_all)
                self.bind_class(class_name, "<Control-c>", self._on_text_shortcut_copy)
                self.bind_class(class_name, "<Control-C>", self._on_text_shortcut_copy)
                self.bind_class(class_name, "<Control-v>", self._on_text_shortcut_paste)
                self.bind_class(class_name, "<Control-V>", self._on_text_shortcut_paste)

        def _is_entry_like_widget(self, widget: object) -> bool:
            return isinstance(widget, (tk.Entry, ttk.Entry, ttk.Combobox))

        def _is_text_like_widget(self, widget: object) -> bool:
            return isinstance(widget, tk.Text) or self._is_entry_like_widget(widget)

        def _on_text_shortcut_select_all(self, event: tk.Event[tk.Misc]) -> str | None:
            widget = event.widget
            if not self._is_text_like_widget(widget):
                return None
            if isinstance(widget, tk.Text):
                widget.tag_add("sel", "1.0", "end-1c")
                widget.mark_set("insert", "end-1c")
                widget.see("insert")
                return "break"
            if self._is_entry_like_widget(widget):
                try:
                    widget.selection_range(0, tk.END)
                    widget.icursor(tk.END)
                    if hasattr(widget, "xview_moveto"):
                        widget.xview_moveto(1.0)
                except tk.TclError:
                    pass
                return "break"
            return None

        def _on_text_shortcut_copy(self, event: tk.Event[tk.Misc]) -> str | None:
            widget = event.widget
            if not self._is_text_like_widget(widget):
                return None

            if isinstance(widget, tk.Text):
                try:
                    selection = widget.get("sel.first", "sel.last")
                except tk.TclError:
                    return "break"
            elif self._is_entry_like_widget(widget):
                try:
                    selection = widget.selection_get()
                except tk.TclError:
                    return "break"
            else:
                return None

            self.clipboard_clear()
            self.clipboard_append(selection)
            self.update_idletasks()
            return "break"

        def _on_text_shortcut_paste(self, event: tk.Event[tk.Misc]) -> str | None:
            widget = event.widget
            if not self._is_text_like_widget(widget):
                return None

            try:
                clipboard_text = self.clipboard_get()
            except tk.TclError:
                return "break"

            if isinstance(widget, tk.Text):
                text_state = str(widget.cget("state"))
                if text_state == "disabled":
                    return "break"
                try:
                    widget.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass
                widget.insert("insert", clipboard_text)
                return "break"

            if self._is_entry_like_widget(widget):
                try:
                    entry_state = str(widget.cget("state"))
                except tk.TclError:
                    entry_state = "normal"
                if entry_state in {"disabled", "readonly"}:
                    return "break"
                try:
                    widget.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass
                widget.insert(tk.INSERT, clipboard_text)
                return "break"

            return None

        def _paste_strong_group_response_from_clipboard(self) -> None:
            if self.strong_group_response_text is None:
                return
            self._paste_text_widget_from_clipboard(self.strong_group_response_text, replace_all=True)

        def _clear_strong_group_response_text(self) -> None:
            if self.strong_group_response_text is None:
                return
            self._set_text_widget_content(self.strong_group_response_text, "")
            self.strong_group_response_text.focus_set()

        def _paste_text_widget_from_clipboard(self, widget: tk.Text, *, replace_all: bool) -> None:
            try:
                clipboard_text = self.clipboard_get()
            except tk.TclError:
                messagebox.showwarning("Буфер обмена", "Буфер обмена пуст или недоступен.", parent=self)
                return

            if replace_all:
                self._set_text_widget_content(widget, clipboard_text)
            else:
                try:
                    widget.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass
                widget.insert("insert", clipboard_text)
            widget.focus_set()

        def _copy_strong_group_prompt_to_clipboard(self) -> None:
            if self.strong_group_prompt_text is None:
                return
            prompt = self._text_widget_content(self.strong_group_prompt_text).strip()
            if not prompt:
                messagebox.showinfo("Нет промпта", "Сначала подготовьте промпт по одной из групп.", parent=self)
                return
            self.clipboard_clear()
            self.clipboard_append(prompt)
            self.update_idletasks()
            self._set_status("Промпт скопирован в буфер обмена.")

        def _prepare_strong_group_prompt(self, group_index: int) -> None:
            if group_index < 0 or group_index >= len(GREEK_DESC_GROUP_RANGES):
                return
            source = self._resolve_strong_group_source_db()
            if source is None:
                messagebox.showwarning("Нет БД", "Не удалось определить БД-источник для экспорта группы.", parent=self)
                return
            target = self._resolve_strong_group_target_db()
            if target is None:
                messagebox.showwarning("Нет целевой БД", "Выберите целевую БД (язык) для подготовки промпта.", parent=self)
                return
            target_lang, target_db_path = target
            source_lang, source_db_path = source
            start_id, end_id = GREEK_DESC_GROUP_RANGES[group_index]

            try:
                source_records = self._fetch_group_records_for_prompt(source_db_path, start_id, end_id)
                translated_ids = self._fetch_non_empty_desc_ids_for_group(target_db_path, start_id, end_id)
            except (OSError, sqlite3.DatabaseError) as exc:
                messagebox.showerror(
                    "Ошибка экспорта группы",
                    f"Не удалось прочитать данные из БД:\n{exc}",
                    parent=self,
                )
                return
            if not source_records:
                messagebox.showwarning(
                    "Пустая группа",
                    f"В диапазоне {start_id}-{end_id} нет записей в таблице greek_descs.",
                    parent=self,
                )
                return

            missing_records = [
                record
                for record in source_records
                if int(record["id"]) not in translated_ids
            ]
            if missing_records:
                records = missing_records
                scope_note = (
                    f"В промпт включены только непереведённые ID: {len(records)} из {len(source_records)}."
                )
            else:
                records = source_records
                scope_note = (
                    f"Все ID в группе уже переведены. Сформирован полный список ({len(records)}) для перегенерации."
                )

            prompt_text = self._build_group_translation_prompt(
                source_lang=source_lang,
                target_lang=target_lang,
                start_id=start_id,
                end_id=end_id,
                records=records,
            )
            if self.strong_group_prompt_text is not None:
                self._set_text_widget_content(self.strong_group_prompt_text, prompt_text)
            self.strong_group_current_index = group_index
            self.strong_group_selected_label_var.set(
                f"Группа #{group_index + 1:02d}: {start_id}-{end_id}. {scope_note}"
            )
            self._set_status(
                (
                    f"Подготовлен промпт для группы #{group_index + 1:02d} ({start_id}-{end_id}): "
                    f"{len(records)} записей, цель {target_db_path.name}."
                )
            )

        def _fetch_group_records_for_prompt(self, db_path: Path, start_id: int, end_id: int) -> list[dict[str, Any]]:
            if not db_path.exists():
                raise FileNotFoundError(f"Файл БД не найден: {db_path}")
            with sqlite3.connect(str(db_path)) as con:
                rows = con.execute(
                    """
                    SELECT id, "desc"
                    FROM greek_descs
                    WHERE id BETWEEN ? AND ?
                    ORDER BY id ASC
                    """,
                    (start_id, end_id),
                ).fetchall()
            return [
                {
                    "id": int(row[0]),
                    "desc": clean_greek_desc_for_prompt(row[1]),
                }
                for row in rows
            ]

        def _fetch_non_empty_desc_ids_for_group(self, db_path: Path, start_id: int, end_id: int) -> set[int]:
            if not db_path.exists():
                raise FileNotFoundError(f"Файл БД не найден: {db_path}")
            with sqlite3.connect(str(db_path)) as con:
                rows = con.execute(
                    """
                    SELECT id
                    FROM greek_descs
                    WHERE id BETWEEN ? AND ?
                      AND trim("desc") <> ""
                    ORDER BY id ASC
                    """,
                    (start_id, end_id),
                ).fetchall()
            return {int(row[0]) for row in rows}

        def _build_group_translation_prompt(
            self,
            *,
            source_lang: str,
            target_lang: str,
            start_id: int,
            end_id: int,
            records: list[dict[str, Any]],
        ) -> str:
            payload = json.dumps(records, ensure_ascii=False, indent=2)
            _ = source_lang
            _ = start_id
            _ = end_id
            target_lang_name = self.strong_group_target_lang_name_var.get().strip() or target_language_name_ru(target_lang)
            header = self._normalize_translation_prompt_header_for_target_alias(
                GREEK_DESC_TRANSLATION_PROMPT_HEADER.strip()
            )
            return (
                f"Целевой язык перевода: {target_lang_name}.\n"
                "Ниже в инструкции фраза 'целевой язык' означает именно этот язык.\n\n"
                f"{header}\n\n"
                "JSON для перевода:\n"
                f"{payload}\n"
            )

        def _normalize_translation_prompt_header_for_target_alias(self, header: str) -> str:
            adapted = header
            replacements = [
                ("с английского на украинский язык", "с английского на целевой язык"),
                ("на грамотный, выверенный украинский язык", "на грамотный, выверенный целевой язык"),
                ("украинского языка", "целевого языка"),
                ("украинский язык", "целевой язык"),
                ("по-украински", "на целевом языке"),
                ("украинских", "целевого языка"),
                ("украинской", "целевого языка"),
                ("украинский", "целевой"),
            ]
            for source_text, target_text in replacements:
                adapted = adapted.replace(source_text, target_text)
            return adapted

        def _refresh_strong_group_status_rows(self) -> None:
            if not self.strong_group_status_labels_by_index:
                return
            source = self._resolve_strong_group_source_db()
            target = self._resolve_strong_group_target_db()

            if source is None:
                self.strong_group_source_info_var.set("Источник не найден.")
                for index in self.strong_group_status_labels_by_index:
                    self.strong_group_status_labels_by_index[index].configure(text="?")
                    progress = self.strong_group_progress_labels_by_index.get(index)
                    if progress is not None:
                        progress.configure(text="-/-")
                return

            source_lang, source_db_path = source
            source_text = f"{source_lang.upper()} ({source_db_path.name})"
            if source_lang != "en":
                source_text += " [EN не найдена]"
            self.strong_group_source_info_var.set(source_text)

            if target is None:
                for index in self.strong_group_status_labels_by_index:
                    self.strong_group_status_labels_by_index[index].configure(text="?")
                    progress = self.strong_group_progress_labels_by_index.get(index)
                    if progress is not None:
                        progress.configure(text="-/-")
                return

            _target_lang, target_db_path = target
            try:
                source_counts = self._group_row_counts_by_range(source_db_path, non_empty_only=False)
                translated_counts = self._group_row_counts_by_range(target_db_path, non_empty_only=True)
            except (OSError, sqlite3.DatabaseError):
                for index in self.strong_group_status_labels_by_index:
                    self.strong_group_status_labels_by_index[index].configure(text="!")
                    progress = self.strong_group_progress_labels_by_index.get(index)
                    if progress is not None:
                        progress.configure(text="error")
                return

            for index in self.strong_group_status_labels_by_index:
                source_count = source_counts[index] if index < len(source_counts) else 0
                translated_count = translated_counts[index] if index < len(translated_counts) else 0
                is_complete = source_count > 0 and translated_count >= source_count
                self.strong_group_status_labels_by_index[index].configure(text="✓" if is_complete else "□")
                progress = self.strong_group_progress_labels_by_index.get(index)
                if progress is not None:
                    progress.configure(text=f"{translated_count}/{source_count}")

        def _group_row_counts_by_range(self, db_path: Path, *, non_empty_only: bool) -> list[int]:
            if not db_path.exists():
                raise FileNotFoundError(f"Файл БД не найден: {db_path}")
            condition = 'AND trim("desc") <> ""' if non_empty_only else ""
            query = (
                'SELECT COUNT(*) FROM greek_descs '
                f'WHERE id BETWEEN ? AND ? {condition}'
            )
            counts: list[int] = []
            with sqlite3.connect(str(db_path)) as con:
                for start_id, end_id in GREEK_DESC_GROUP_RANGES:
                    row = con.execute(query, (start_id, end_id)).fetchone()
                    counts.append(int(row[0] or 0) if row is not None else 0)
            return counts

        def _import_strong_group_response(self) -> None:
            if self.strong_group_current_index is None:
                messagebox.showinfo("Группа не выбрана", "Сначала нажмите «Подготовить промпт» у нужной группы.", parent=self)
                return
            if self.strong_group_response_text is None:
                return
            target = self._resolve_strong_group_target_db()
            if target is None:
                messagebox.showwarning("Нет целевой БД", "Выберите целевой язык для импорта.", parent=self)
                return
            target_lang, target_db_path = target
            start_id, end_id = GREEK_DESC_GROUP_RANGES[self.strong_group_current_index]
            response_text = self._text_widget_content(self.strong_group_response_text).strip()
            if not response_text:
                messagebox.showinfo("Пустой ответ", "Вставьте ответ ИИ в правое поле.", parent=self)
                return

            try:
                payload = self._parse_json_payload_from_ai_response(response_text)
                records, duplicate_ids = self._normalize_group_import_records(payload)
            except ValueError as exc:
                messagebox.showerror("Ошибка JSON", str(exc), parent=self)
                return

            if not records:
                messagebox.showwarning("Нет данных", "В JSON нет записей для импорта.", parent=self)
                return
            out_of_range = [record_id for record_id, _desc in records if record_id < start_id or record_id > end_id]
            if out_of_range:
                preview = ", ".join(str(item) for item in out_of_range[:8])
                messagebox.showerror(
                    "ID вне диапазона",
                    (
                        f"В ответе есть ID вне выбранной группы {start_id}-{end_id}: {preview}\n"
                        "Исправьте JSON и повторите импорт."
                    ),
                    parent=self,
                )
                return

            try:
                inserted, updated_existing, table_rows_after = self._upsert_group_records_in_db(target_db_path, records)
                self._touch_localized_db_data_version(db_path=target_db_path)
            except (OSError, sqlite3.DatabaseError) as exc:
                messagebox.showerror("Ошибка импорта", f"Не удалось сохранить переводы:\n{exc}", parent=self)
                return

            self._load_strong_rows()
            self._refresh_strong_group_status_rows()
            self._update_file_info()
            self._set_status(
                (
                    f"Группа #{self.strong_group_current_index + 1:02d} ({start_id}-{end_id}) импортирована в {target_lang}: "
                    f"{len(records)} записей, +{inserted} новых, обновлено {updated_existing}."
                )
            )
            duplicate_note = ""
            if duplicate_ids > 0:
                duplicate_note = f"\nДубликаты ID в ответе: {duplicate_ids} (взят последний вариант)."
            messagebox.showinfo(
                "Импорт завершен",
                (
                    f"Целевая БД: {target_db_path.name}\n"
                    f"Диапазон: {start_id}-{end_id}\n"
                    f"Импортировано уникальных ID: {len(records)}\n"
                    f"Добавлено новых строк: {inserted}\n"
                    f"Обновлено существующих: {updated_existing}\n"
                    f"Всего строк в greek_descs: {table_rows_after}"
                    f"{duplicate_note}"
                ),
                parent=self,
            )

        def _parse_json_payload_from_ai_response(self, text: str) -> object:
            payload_text = text.strip()
            if not payload_text:
                raise ValueError("Ответ пустой.")

            fenced_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", payload_text, re.IGNORECASE)
            if fenced_match is not None:
                payload_text = fenced_match.group(1).strip()

            start_candidates = [pos for pos in (payload_text.find("["), payload_text.find("{")) if pos >= 0]
            if start_candidates:
                payload_text = payload_text[min(start_candidates):]

            decoder = json.JSONDecoder()
            try:
                payload, _end = decoder.raw_decode(payload_text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Не удалось разобрать JSON: {exc.msg} (позиция {exc.pos}).") from exc
            return payload

        def _normalize_group_import_records(self, payload: object) -> tuple[list[tuple[int, str]], int]:
            if not isinstance(payload, list):
                raise ValueError("Ожидался JSON-массив объектов с полями id и desc.")
            by_id: dict[int, str] = {}
            duplicate_ids = 0
            for index, item in enumerate(payload, start=1):
                source = f"ответ#{index}"
                if not isinstance(item, dict):
                    raise ValueError(f"В {source} ожидается объект.")
                if "id" not in item or "desc" not in item:
                    raise ValueError(f"В {source} нужны поля id и desc.")
                record_id = self._normalize_group_record_id(item["id"], source)
                desc = self._normalize_group_record_desc(item["desc"], source)
                if record_id in by_id:
                    duplicate_ids += 1
                by_id[record_id] = desc
            records = sorted(by_id.items(), key=lambda pair: pair[0])
            return records, duplicate_ids

        def _normalize_group_record_id(self, value: object, source: str) -> int:
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                stripped = value.strip()
                if stripped.isdigit():
                    return int(stripped)
            raise ValueError(f"Некорректный id в {source}: {value!r}")

        def _normalize_group_record_desc(self, value: object, source: str) -> str:
            if isinstance(value, str):
                return value
            raise ValueError(f"Некорректный desc в {source}: ожидается строка.")

        def _upsert_group_records_in_db(self, db_path: Path, records: list[tuple[int, str]]) -> tuple[int, int, int]:
            use_active_connection = (
                self.connection is not None
                and self.current_db_path is not None
                and db_path.resolve() == self.current_db_path.resolve()
            )
            local_connection: sqlite3.Connection | None = None
            try:
                if use_active_connection:
                    assert self.connection is not None
                    con = self.connection
                else:
                    local_connection = sqlite3.connect(str(db_path))
                    con = local_connection

                with con:
                    con.execute(
                        """
                        CREATE TABLE IF NOT EXISTS greek_descs (
                          id INTEGER NOT NULL PRIMARY KEY,
                          "desc" TEXT NOT NULL
                        )
                        """
                    )
                    before_count = int(con.execute('SELECT COUNT(*) FROM greek_descs').fetchone()[0])
                    con.executemany(
                        '''
                        INSERT INTO greek_descs (id, "desc")
                        VALUES (?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            "desc" = excluded."desc"
                        ''',
                        records,
                    )
                    after_count = int(con.execute('SELECT COUNT(*) FROM greek_descs').fetchone()[0])

                inserted = after_count - before_count
                updated_existing = len(records) - inserted
                return inserted, updated_existing, after_count
            finally:
                if local_connection is not None:
                    local_connection.close()

        def _extract_category_tokens(self, category_raw: str) -> list[str]:
            found = re.findall(r"@([A-Za-z][A-Za-z0-9_]*)", category_raw or "")
            seen: set[str] = set()
            ordered: list[str] = []
            for token in found:
                if token in seen:
                    continue
                seen.add(token)
                ordered.append(token)
            return ordered

        def _format_strong_category_display(self, category_raw: str) -> str:
            raw = category_raw.strip()
            if not raw:
                return "-"
            tokens = self._extract_category_tokens(raw)
            if not tokens:
                return raw
            labels = [self.strong_category_labels_by_token.get(token, f"@{token}") for token in tokens]
            return ", ".join(labels)

        def _sync_strong_category_visuals(self) -> None:
            raw = self.strong_category_var.get().strip()
            self.strong_category_display_var.set(self._format_strong_category_display(raw))
            preview = raw if raw else "-"
            self.strong_category_raw_preview_var.set(f"Сохранится в БД: {preview}")

        def _open_strong_category_picker(self) -> None:
            options: list[str] = []
            used_tokens: set[str] = set()
            for row in self.strong_rows:
                used_tokens.update(self._extract_category_tokens(row.category))
            if used_tokens:
                options = sorted(
                    used_tokens,
                    key=lambda token: (
                        self.strong_category_labels_by_token.get(token, token).lower(),
                        token.lower(),
                    ),
                )
            elif self.strong_category_labels_by_token:
                options = sorted(
                    self.strong_category_labels_by_token.keys(),
                    key=lambda token: (
                        self.strong_category_labels_by_token.get(token, token).lower(),
                        token.lower(),
                    ),
                )

            if not options:
                messagebox.showinfo(
                    "Нет данных",
                    "Не удалось найти список категорий для выбора.",
                    parent=self,
                )
                return

            dialog = tk.Toplevel(self)
            dialog.title("Категории Стронга")
            dialog.transient(self)
            dialog.grab_set()
            dialog.resizable(True, True)
            dialog.minsize(520, 360)

            body = ttk.Frame(dialog, padding=10)
            body.grid(row=0, column=0, sticky="nsew")
            dialog.columnconfigure(0, weight=1)
            dialog.rowconfigure(0, weight=1)
            body.columnconfigure(0, weight=1)
            body.rowconfigure(1, weight=1)

            ttk.Label(
                body,
                text=(
                    "Выберите нужные категории. В БД будут сохранены @ключи,\n"
                    "а в интерфейсе показываются русские эквиваленты."
                ),
                justify="left",
            ).grid(row=0, column=0, sticky="w", pady=(0, 8))

            list_wrap = ttk.Frame(body)
            list_wrap.grid(row=1, column=0, sticky="nsew")
            list_wrap.columnconfigure(0, weight=1)
            list_wrap.rowconfigure(0, weight=1)
            listbox = tk.Listbox(list_wrap, selectmode="extended", exportselection=False)
            listbox.grid(row=0, column=0, sticky="nsew")
            scroll = ttk.Scrollbar(list_wrap, orient="vertical", command=listbox.yview)
            scroll.grid(row=0, column=1, sticky="ns")
            listbox.configure(yscrollcommand=scroll.set)

            for token in options:
                label = self.strong_category_labels_by_token.get(token, token)
                listbox.insert(tk.END, f"{label} (@{token})")

            current_tokens = set(self._extract_category_tokens(self.strong_category_var.get().strip()))
            for idx, token in enumerate(options):
                if token in current_tokens:
                    listbox.selection_set(idx)

            actions = ttk.Frame(body)
            actions.grid(row=2, column=0, sticky="e", pady=(8, 0))

            def apply_selection() -> None:
                selected_tokens = [options[int(i)] for i in listbox.curselection()]
                raw = ", ".join(f"@{token}" for token in selected_tokens)
                self.strong_category_var.set(raw)
                self._sync_strong_category_visuals()
                dialog.destroy()

            ttk.Button(actions, text="Применить", command=apply_selection).pack(side="left")
            ttk.Button(actions, text="Отмена", command=dialog.destroy).pack(side="left", padx=(8, 0))

            self._fit_and_center_toplevel(
                dialog,
                min_width=520,
                max_width=760,
                min_height=360,
                max_height=680,
            )
            dialog.bind("<Escape>", lambda _e: dialog.destroy())
            listbox.focus_set()

        def _on_strong_filter_changed(self, *_args: object) -> None:
            if not hasattr(self, "strong_tree"):
                return
            selected_id: int | None = None
            if self.selected_strong_index is not None and 0 <= self.selected_strong_index < len(self.strong_rows):
                selected_id = self.strong_rows[self.selected_strong_index].id
            self._apply_strong_filter(keep_selected_id=selected_id)

        def _clear_strong_filter(self) -> None:
            self.strong_filter_var.set("")
            self.entry_strong_filter.focus_set()

        def _set_text_widget_content(self, widget: tk.Text, value: str) -> None:
            previous_state = str(widget.cget("state"))
            if previous_state == "disabled":
                widget.configure(state="normal")
            widget.delete("1.0", tk.END)
            if value:
                widget.insert("1.0", value)
            if previous_state == "disabled":
                widget.configure(state="disabled")

        def _text_widget_content(self, widget: tk.Text) -> str:
            return widget.get("1.0", "end-1c")

        def _insert_markdown_template(self, spec: MarkdownTemplateSpec) -> None:
            widget = self.markdown_text
            if str(widget.cget("state")) == "disabled":
                return

            try:
                selected_text = widget.get("sel.first", "sel.last")
            except tk.TclError:
                selected_text = ""

            template = self._template_text_for_insertion(spec, selected_text)
            widget.focus_set()
            widget.edit_separator()
            try:
                widget.delete("sel.first", "sel.last")
            except tk.TclError:
                pass
            widget.insert("insert", template)
            widget.see("insert")
            widget.edit_separator()

        def _template_text_for_insertion(
            self,
            spec: MarkdownTemplateSpec,
            selected_text: str,
        ) -> str:
            if not selected_text or "\n" in selected_text:
                return spec.template

            template = spec.template
            open_bracket = template.find("[")
            close_bracket = template.find("](")
            if open_bracket == -1 or close_bracket == -1 or close_bracket <= open_bracket:
                return template
            return f"{template[: open_bracket + 1]}{selected_text}{template[close_bracket:]}"

        def _load_localized_desc_from_db(self, db_path: Path, strong_id: int) -> tuple[bool, str, str | None]:
            if not db_path.exists():
                return False, "", "Файл БД не найден."

            local_connection: sqlite3.Connection | None = None
            try:
                use_active_connection = (
                    self.connection is not None
                    and self.current_db_path is not None
                    and db_path.resolve() == self.current_db_path.resolve()
                )
                if use_active_connection:
                    assert self.connection is not None
                    con = self.connection
                else:
                    local_connection = sqlite3.connect(db_path)
                    local_connection.row_factory = sqlite3.Row
                    con = local_connection

                row = con.execute(
                    """
                    SELECT "desc"
                    FROM greek_descs
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (strong_id,),
                ).fetchone()
            except sqlite3.DatabaseError as exc:
                return False, "", f"Ошибка чтения: {exc}"
            finally:
                if local_connection is not None:
                    local_connection.close()

            if row is None:
                return False, "", None
            return True, (row["desc"] or ""), None

        def _upsert_localized_desc_in_db(self, db_path: Path, strong_id: int, desc: str) -> None:
            use_active_connection = (
                self.connection is not None
                and self.current_db_path is not None
                and db_path.resolve() == self.current_db_path.resolve()
            )
            local_connection: sqlite3.Connection | None = None
            try:
                if use_active_connection:
                    assert self.connection is not None
                    con = self.connection
                else:
                    local_connection = sqlite3.connect(db_path)
                    local_connection.row_factory = sqlite3.Row
                    con = local_connection

                with con:
                    con.execute(
                        """
                        CREATE TABLE IF NOT EXISTS greek_descs (
                          id INTEGER NOT NULL PRIMARY KEY,
                          "desc" TEXT NOT NULL
                        )
                        """
                    )
                    con.execute(
                        """
                        INSERT INTO greek_descs(id, "desc")
                        VALUES(?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            "desc" = excluded."desc"
                        """,
                        (strong_id, desc),
                    )
            finally:
                if local_connection is not None:
                    local_connection.close()

        def _restore_localized_desc_in_db(
            self,
            db_path: Path,
            strong_id: int,
            *,
            existed: bool,
            desc: str,
        ) -> None:
            use_active_connection = (
                self.connection is not None
                and self.current_db_path is not None
                and db_path.resolve() == self.current_db_path.resolve()
            )
            local_connection: sqlite3.Connection | None = None
            try:
                if use_active_connection:
                    assert self.connection is not None
                    con = self.connection
                else:
                    local_connection = sqlite3.connect(db_path)
                    local_connection.row_factory = sqlite3.Row
                    con = local_connection

                with con:
                    con.execute(
                        """
                        CREATE TABLE IF NOT EXISTS greek_descs (
                          id INTEGER NOT NULL PRIMARY KEY,
                          "desc" TEXT NOT NULL
                        )
                        """
                    )
                    if existed:
                        con.execute(
                            """
                            INSERT INTO greek_descs(id, "desc")
                            VALUES(?, ?)
                            ON CONFLICT(id) DO UPDATE SET
                                "desc" = excluded."desc"
                            """,
                            (strong_id, desc),
                        )
                    else:
                        con.execute("DELETE FROM greek_descs WHERE id = ?", (strong_id,))
            finally:
                if local_connection is not None:
                    local_connection.close()

        def _load_strong_rows(self) -> None:
            selected_id: int | None = None
            if self.selected_strong_index is not None and 0 <= self.selected_strong_index < len(self.strong_rows):
                selected_id = self.strong_rows[self.selected_strong_index].id

            self.strong_rows.clear()
            common_rows: list[sqlite3.Row] = []
            if self.common_connection is not None:
                try:
                    common_rows = self.common_connection.execute(
                        """
                        SELECT id, word, category, synonyms, origin, usage
                        FROM greek_words
                        ORDER BY id ASC
                        """
                    ).fetchall()
                except sqlite3.DatabaseError:
                    common_rows = []

            self.strong_desc_presence_by_lang = {}
            localized_search_texts_by_id: dict[int, list[str]] = {}
            for lang, db_path in self._localized_db_entries():
                ids: set[int] = set()
                use_active_connection = (
                    self.connection is not None
                    and self.current_db_path is not None
                    and db_path.resolve() == self.current_db_path.resolve()
                )
                local_connection: sqlite3.Connection | None = None
                try:
                    if use_active_connection:
                        assert self.connection is not None
                        con = self.connection
                    else:
                        local_connection = sqlite3.connect(db_path)
                        local_connection.row_factory = sqlite3.Row
                        con = local_connection

                    desc_rows = con.execute(
                        """
                        SELECT id, "desc"
                        FROM greek_descs
                        ORDER BY id ASC
                        """
                    ).fetchall()
                    for desc_row in desc_rows:
                        strong_id = int(desc_row["id"])
                        desc_text = (desc_row["desc"] or "").strip()
                        if not desc_text:
                            continue
                        ids.add(strong_id)
                        localized_search_texts_by_id.setdefault(strong_id, []).append(desc_text.lower())
                except sqlite3.DatabaseError:
                    ids = set()
                finally:
                    if local_connection is not None:
                        local_connection.close()
                self.strong_desc_presence_by_lang[lang] = ids

            self.strong_rows = [
                StrongRow(
                    id=int(row["id"]),
                    word=row["word"] or "",
                    category=row["category"] or "",
                    synonyms=row["synonyms"] or "",
                    origin=row["origin"] or "",
                    usage=row["usage"] or "",
                    localized_flags={
                        lang: int(row["id"]) in ids
                        for lang, ids in self.strong_desc_presence_by_lang.items()
                    },
                    localized_search=" ".join(localized_search_texts_by_id.get(int(row["id"]), [])),
                )
                for row in common_rows
            ]

            self._apply_strong_filter(keep_selected_id=selected_id)

        def _refresh_strong_tree(self) -> None:
            self.strong_tree.delete(*self.strong_tree.get_children())
            for view_idx, row_idx in enumerate(self.strong_filtered_indices):
                row = self.strong_rows[row_idx]
                synonyms = re.sub(r"\s+", " ", row.synonyms.strip())
                origin = re.sub(r"\s+", " ", row.origin.strip())
                values: list[str] = [
                    f"G{row.id}",
                    row.word.strip(),
                    synonyms,
                    origin,
                    self._format_strong_category_display(row.category),
                ]
                for lang in self.strong_tree_lang_columns:
                    values.append("✓" if row.localized_flags.get(lang, False) else "-")
                self.strong_tree.insert(
                    "",
                    "end",
                    iid=str(view_idx),
                    values=tuple(values),
                )

        def _apply_strong_filter(self, *, keep_selected_id: int | None = None) -> None:
            query = self.strong_filter_var.get().strip().lower()
            self.strong_filtered_indices = []

            for idx, row in enumerate(self.strong_rows):
                if not query:
                    self.strong_filtered_indices.append(idx)
                    continue
                haystack = " ".join(
                    [
                        str(row.id),
                        f"g{row.id}",
                        row.word.lower(),
                        row.category.lower(),
                        row.localized_search,
                    ]
                )
                if query in haystack:
                    self.strong_filtered_indices.append(idx)

            self._refresh_strong_tree()
            if keep_selected_id is not None and self._select_strong_by_id(keep_selected_id):
                return
            if self.strong_filtered_indices:
                first_idx = self.strong_filtered_indices[0]
                self.strong_tree.selection_set("0")
                self.strong_tree.focus("0")
                self.strong_tree.see("0")
                self.selected_strong_index = first_idx
                self._reload_selected_strong()
                return

            if self.common_connection is None:
                self._clear_strong_editor(message="Общая БД не подключена.")
                return
            if self.strong_rows and query:
                self._clear_strong_editor(message="По фильтру ничего не найдено.")
                return
            self._clear_strong_editor(message="Нет записей в таблице greek_words.")

        def _on_strong_selected(self, _event: object) -> None:
            selection = self.strong_tree.selection()
            if not selection:
                self.selected_strong_index = None
                return
            view_idx = int(selection[0])
            if view_idx < 0 or view_idx >= len(self.strong_filtered_indices):
                self.selected_strong_index = None
                self._clear_strong_editor()
                return
            self.selected_strong_index = self.strong_filtered_indices[view_idx]
            self._reload_selected_strong()

        def _clear_strong_editor(self, *, message: str = "Локализованная часть: выберите запись из списка.") -> None:
            self.selected_strong_index = None
            self.strong_id_var.set("-")
            self.strong_word_var.set("")
            self.strong_category_var.set("")
            self._sync_strong_category_visuals()
            self.strong_synonyms_var.set("")
            self._set_text_widget_content(self.strong_origin_text, "")
            self._set_text_widget_content(self.strong_usage_text, "")
            for text_widget in self.strong_desc_texts_by_lang.values():
                self._set_text_widget_content(text_widget, "")

        def _reload_selected_strong(self) -> None:
            if self.selected_strong_index is None:
                self._clear_strong_editor()
                return
            if self.selected_strong_index < 0 or self.selected_strong_index >= len(self.strong_rows):
                self._clear_strong_editor()
                return

            row = self.strong_rows[self.selected_strong_index]
            self.strong_id_var.set(f"G{row.id}")
            self.strong_word_var.set(row.word)
            self.strong_category_var.set(row.category)
            self._sync_strong_category_visuals()
            self.strong_synonyms_var.set(row.synonyms)
            self._set_text_widget_content(self.strong_origin_text, row.origin)
            self._set_text_widget_content(self.strong_usage_text, row.usage)

            for lang, db_path in self.strong_local_db_paths_by_lang.items():
                found, desc, error = self._load_localized_desc_from_db(db_path, row.id)
                text_widget = self.strong_desc_texts_by_lang.get(lang)
                if text_widget is None:
                    continue
                if error is not None:
                    self._set_text_widget_content(text_widget, f"[Ошибка чтения] {error}")
                elif not found:
                    self._set_text_widget_content(text_widget, "")
                else:
                    self._set_text_widget_content(text_widget, desc)

        def _select_strong_by_id(self, strong_id: int) -> bool:
            for view_idx, row_idx in enumerate(self.strong_filtered_indices):
                if self.strong_rows[row_idx].id != strong_id:
                    continue
                iid = str(view_idx)
                self.strong_tree.selection_set(iid)
                self.strong_tree.focus(iid)
                self.strong_tree.see(iid)
                self.selected_strong_index = row_idx
                self._reload_selected_strong()
                return True
            return False

        def _apply_strong_changes(self) -> None:
            if self.selected_strong_index is None:
                messagebox.showinfo("Нет выбора", "Сначала выберите статью словаря Стронга.", parent=self)
                return
            if self.selected_strong_index < 0 or self.selected_strong_index >= len(self.strong_rows):
                self._clear_strong_editor()
                return
            if self.common_connection is None or self.common_db_path is None:
                messagebox.showwarning("Нет общей БД", "Общая БД недоступна.", parent=self)
                return

            row = self.strong_rows[self.selected_strong_index]
            strong_id = row.id

            word = self.strong_word_var.get().strip()
            category = self.strong_category_var.get().strip()
            synonyms = self.strong_synonyms_var.get().strip()
            origin = self._text_widget_content(self.strong_origin_text).strip()
            usage = self._text_widget_content(self.strong_usage_text).strip()
            localized_desc_values: dict[str, str] = {
                lang: self._text_widget_content(text_widget).strip()
                for lang, text_widget in self.strong_desc_texts_by_lang.items()
            }

            if not word:
                messagebox.showwarning("Ошибка", "Поле word не может быть пустым.", parent=self)
                return

            old_common = self.common_connection.execute(
                """
                SELECT word, category, synonyms, origin, usage
                FROM greek_words
                WHERE id = ?
                LIMIT 1
                """,
                (strong_id,),
            ).fetchone()

            try:
                with self.common_connection:
                    updated = self.common_connection.execute(
                        """
                        UPDATE greek_words
                        SET word = ?, category = ?, synonyms = ?, origin = ?, usage = ?
                        WHERE id = ?
                        """,
                        (word, category, synonyms, origin, usage, strong_id),
                    )
                    if updated.rowcount == 0:
                        self.common_connection.execute(
                            """
                            INSERT INTO greek_words(id, word, category, synonyms, origin, usage)
                            VALUES(?, ?, ?, ?, ?, ?)
                            """,
                            (strong_id, word, category, synonyms, origin, usage),
                        )
            except sqlite3.DatabaseError as exc:
                messagebox.showerror(
                    "Ошибка сохранения",
                    f"Не удалось сохранить общую часть словаря:\n{exc}",
                    parent=self,
                )
                return

            old_localized_descs: dict[str, tuple[bool, str]] = {}
            for lang, db_path in self.strong_local_db_paths_by_lang.items():
                found, desc_old, _error = self._load_localized_desc_from_db(db_path, strong_id)
                old_localized_descs[lang] = (found, desc_old if found else "")

            localized_saved_order: list[str] = []
            try:
                for lang, db_path in self.strong_local_db_paths_by_lang.items():
                    self._upsert_localized_desc_in_db(
                        db_path,
                        strong_id,
                        localized_desc_values.get(lang, ""),
                    )
                    localized_saved_order.append(lang)
            except sqlite3.DatabaseError as local_exc:
                rollback_ok = True
                try:
                    with self.common_connection:
                        if old_common is None:
                            self.common_connection.execute("DELETE FROM greek_words WHERE id = ?", (strong_id,))
                        else:
                            self.common_connection.execute(
                                """
                                UPDATE greek_words
                                SET word = ?, category = ?, synonyms = ?, origin = ?, usage = ?
                                WHERE id = ?
                                """,
                                (
                                    old_common["word"],
                                    old_common["category"],
                                    old_common["synonyms"],
                                    old_common["origin"],
                                    old_common["usage"],
                                    strong_id,
                                ),
                            )
                except sqlite3.DatabaseError:
                    rollback_ok = False

                for lang in reversed(localized_saved_order):
                    db_path = self.strong_local_db_paths_by_lang.get(lang)
                    if db_path is None:
                        continue
                    existed, old_desc = old_localized_descs.get(lang, (False, ""))
                    try:
                        self._restore_localized_desc_in_db(
                            db_path,
                            strong_id,
                            existed=existed,
                            desc=old_desc,
                        )
                    except sqlite3.DatabaseError:
                        rollback_ok = False

                rollback_note = (
                    "Общая и локализованные части были откатены."
                    if rollback_ok
                    else "Не удалось полностью откатить изменения. Проверьте запись вручную."
                )
                messagebox.showerror(
                    "Ошибка сохранения",
                    f"Не удалось сохранить локализованную часть словаря:\n{local_exc}\n\n{rollback_note}",
                    parent=self,
                )
                return

            self._touch_common_db_data_version(connection=self.common_connection)
            for lang in localized_saved_order:
                db_path = self.strong_local_db_paths_by_lang.get(lang)
                if db_path is None:
                    continue
                self._touch_localized_db_data_version(db_path=db_path)

            self._load_strong_rows()
            self._select_strong_by_id(strong_id)
            self._update_file_info()
            self._set_status(
                (
                    f"Словарная статья G{strong_id} сохранена "
                    f"в {self.common_db_path.stem} и {len(self.strong_local_db_paths_by_lang)} локализованных БД."
                )
            )

