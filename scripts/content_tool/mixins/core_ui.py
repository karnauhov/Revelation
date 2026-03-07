from __future__ import annotations

import argparse
import ast
import base64
import datetime as dt
import io
import json
import mimetypes
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import tempfile
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any

from ..compat import HtmlFrameType, HtmlFrameWidget
from ..helpers import default_primary_sources_dir
from ..models import ArticleRow, PrimarySourcePageSummary, PrimarySourceSummary, ResourceRow, StrongRow
from ..widgets import MarkdownTemplateToolbar, revelation_markdown_template_sections


class CoreUiMixin:
        def __init__(self, start_dir: Path) -> None:
            super().__init__()
            self.title(self.BASE_TITLE)
            self.geometry("1500x920")
            self.minsize(1200, 760)

            self.project_root = Path(__file__).resolve().parents[3]
            self.work_dir = start_dir
            self.connection: sqlite3.Connection | None = None
            self.common_connection: sqlite3.Connection | None = None
            self.common_db_path: Path | None = None
            self.current_db_path: Path | None = None
            self.db_files: dict[str, Path] = {}
            self.dirty = False
            self.message_log: list[tuple[str, str]] = []
            self.preview_after_id: str | None = None
            self.markdown_change_internal = False
            self.supabase_storage_config_cache: tuple[str, str] | None = None

            self.articles: list[ArticleRow] = []
            self.common_resources: list[ResourceRow] = []
            self.strong_rows: list[StrongRow] = []
            self.strong_filtered_indices: list[int] = []
            self.selected_article_index: int | None = None
            self.selected_resource_index: int | None = None
            self.selected_resource_original_key: str | None = None
            self.selected_strong_index: int | None = None
            self.resource_data_buffer = b""
            self.resource_preview_image: tk.PhotoImage | None = None

            self.folder_var = tk.StringVar(value=str(self.work_dir))
            self.db_var = tk.StringVar()
            self.file_info_var = tk.StringVar(value="-")
            self.status_var = tk.StringVar(value="-")
            self.resources_db_var = tk.StringVar(value="Общая БД: -")
            self.strong_local_db_var = tk.StringVar(value="-")
            self.strong_common_db_var = tk.StringVar(value="-")
            self.sources_local_db_var = tk.StringVar(value="-")
            self.sources_common_db_var = tk.StringVar(value="-")
            self.bibles_local_db_var = tk.StringVar(value="-")
            self.bibles_common_db_var = tk.StringVar(value="-")

            self.topic_route_var = tk.StringVar(value=self.NO_ARTICLE_OPTION)
            self.topic_name_var = tk.StringVar()
            self.topic_description_var = tk.StringVar()
            self.topic_icon_var = tk.StringVar(value=self.NO_ICON_OPTION)
            self.topic_sort_var = tk.StringVar(value="0")
            self.topic_visible_var = tk.BooleanVar(value=True)

            self.resource_key_var = tk.StringVar()
            self.resource_file_name_var = tk.StringVar()
            self.resource_mime_var = tk.StringVar()
            self.resource_size_var = tk.StringVar(value="-")
            self.strong_filter_var = tk.StringVar()
            self.strong_id_var = tk.StringVar(value="-")
            self.strong_word_var = tk.StringVar()
            self.strong_category_var = tk.StringVar()
            self.strong_category_display_var = tk.StringVar(value="-")
            self.strong_category_raw_preview_var = tk.StringVar(value="Сохранится в БД: -")
            self.strong_synonyms_var = tk.StringVar()
            self.strong_languages_var = tk.StringVar(value="-")
            self.preview_unavailable_reason = ""
            self.preview_html: HtmlFrameType | None = None
            self.preview_text: tk.Text | None = None
            self.md_template_toolbar: MarkdownTemplateToolbar | None = None
            self.ui_icons: dict[str, tk.PhotoImage] = {}
            self.status_indicator_image: tk.PhotoImage | None = None
            self.strong_category_labels_by_token: dict[str, str] = self._load_ru_strong_category_labels()
            self.strong_tree_lang_columns: list[str] = []
            self.strong_desc_texts_by_lang: dict[str, tk.Text] = {}
            self.strong_local_db_paths_by_lang: dict[str, Path] = {}
            self.strong_desc_presence_by_lang: dict[str, set[int]] = {}
            self.strong_group_dialog: tk.Toplevel | None = None
            self.strong_group_target_lang_var = tk.StringVar(value="")
            self.strong_group_target_lang_name_var = tk.StringVar(value="-")
            self.strong_group_target_combo: ttk.Combobox | None = None
            self.strong_group_source_info_var = tk.StringVar(value="-")
            self.strong_group_selected_label_var = tk.StringVar(value="Группа не выбрана.")
            self.strong_group_status_labels_by_index: dict[int, ttk.Label] = {}
            self.strong_group_progress_labels_by_index: dict[int, ttk.Label] = {}
            self.strong_group_prompt_text: tk.Text | None = None
            self.strong_group_response_text: tk.Text | None = None
            self.strong_group_current_index: int | None = None
            self.primary_sources: list[PrimarySourceSummary] = []
            self.primary_source_filtered_ids: list[str] = []
            self.primary_source_pages: list[PrimarySourcePageSummary] = []
            self.primary_source_link_rows: list[sqlite3.Row] = []
            self.primary_source_attribution_rows: list[sqlite3.Row] = []
            self.primary_source_word_rows: list[sqlite3.Row] = []
            self.primary_source_verse_rows: list[sqlite3.Row] = []
            self.primary_source_locale_presence_by_lang: dict[str, set[str]] = {}
            self.selected_primary_source_id: str | None = None
            self.selected_primary_source_page_name: str | None = None
            self.selected_primary_source_link_index: int | None = None
            self.selected_primary_source_attribution_index: int | None = None
            self.selected_primary_source_page_index: int | None = None
            self.selected_primary_source_word_index: int | None = None
            self.selected_primary_source_verse_index: int | None = None
            self.primary_source_filter_var = tk.StringVar()
            self.primary_source_group_var = tk.StringVar(value="all")
            self.primary_source_validation_var = tk.StringVar(value="Выберите первоисточник.")
            self.primary_source_locale_info_var = tk.StringVar(value="Локализованная БД: -")
            self.primary_source_images_root_var = tk.StringVar(value=str(default_primary_sources_dir()))
            self.primary_source_force_download_var = tk.BooleanVar(value=False)
            self.primary_source_page_info_var = tk.StringVar(value="Страница не выбрана.")
            self.primary_source_id_var = tk.StringVar()
            self.primary_source_family_var = tk.StringVar()
            self.primary_source_number_var = tk.StringVar(value="0")
            self.primary_source_group_kind_var = tk.StringVar(value="fragment")
            self.primary_source_sort_order_var = tk.StringVar(value="0")
            self.primary_source_verses_count_var = tk.StringVar(value="0")
            self.primary_source_preview_key_var = tk.StringVar()
            self.primary_source_default_max_scale_var = tk.StringVar(value="3.0")
            self.primary_source_can_show_images_var = tk.BooleanVar(value=True)
            self.primary_source_images_are_monochrome_var = tk.BooleanVar(value=False)
            self.primary_source_notes_text: tk.Text | None = None
            self.primary_source_preview_image: tk.PhotoImage | None = None
            self.primary_source_title_markup_var = tk.StringVar()
            self.primary_source_date_label_var = tk.StringVar()
            self.primary_source_content_label_var = tk.StringVar()
            self.primary_source_material_text_var = tk.StringVar()
            self.primary_source_text_style_text_var = tk.StringVar()
            self.primary_source_found_text_var = tk.StringVar()
            self.primary_source_classification_text_var = tk.StringVar()
            self.primary_source_current_location_text_var = tk.StringVar()

            self._build_ui()
            self._install_global_text_shortcuts()
            self.strong_filter_var.trace_add("write", self._on_strong_filter_changed)
            self.primary_source_filter_var.trace_add("write", self._on_primary_source_filter_changed)
            self._refresh_db_list(initial_select=True)
            self.after(0, self._maximize_window)

            self.protocol("WM_DELETE_WINDOW", self._on_close)

        def _build_ui(self) -> None:
            self.columnconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)
            self._prepare_icons()

            header = ttk.Frame(self, padding=10)
            header.grid(row=0, column=0, sticky="ew")
            header.columnconfigure(1, weight=1)

            ttk.Label(header, text="Рабочая папка с БД:").grid(row=0, column=0, sticky="w", padx=(0, 8))
            ttk.Entry(header, textvariable=self.folder_var, state="readonly").grid(row=0, column=1, sticky="ew")
            self.btn_choose_folder = ttk.Button(
                header,
                **self._button_kwargs("choose_folder", "Выбрать папку с БД"),
                command=self._choose_folder,
            )
            self.btn_choose_folder.grid(row=0, column=2, padx=(8, 0))
            self.btn_refresh = ttk.Button(
                header,
                **self._button_kwargs("refresh", "Перечитать файлы БД"),
                command=self._refresh_db_list,
            )
            self.btn_refresh.grid(row=0, column=3, padx=(8, 0))
            self.btn_publish = ttk.Button(
                header,
                **self._button_kwargs("publish", "Скопировать в проект"),
                command=self._copy_to_web_db,
            )
            self.btn_publish.grid(row=0, column=4, padx=(8, 0))

            self.sections = ttk.Notebook(self)
            self.sections.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 6))
            self.sections.bind("<<NotebookTabChanged>>", self._on_main_section_changed)

            self.articles_section = ttk.Frame(self.sections)
            self.resources_section = ttk.Frame(self.sections)
            self.strong_section = ttk.Frame(self.sections)
            self.sources_section = ttk.Frame(self.sections)
            self.bibles_section = ttk.Frame(self.sections)

            self.sections.add(self.articles_section, text="Статьи")
            self.sections.add(self.resources_section, text="Ресурсы")
            self.sections.add(self.strong_section, text="Словарь Стронга")
            self.sections.add(self.sources_section, text="Первоисточники")
            self.sections.add(self.bibles_section, text="Библии")

            self._build_articles_section(self.articles_section)
            self._build_resources_section(self.resources_section)
            self._build_strong_section(self.strong_section)
            self._build_sources_section(self.sources_section)
            self._build_future_section(
                self.bibles_section,
                "Раздел «Библии» скоро будет доступен.",
                local_db_var=self.bibles_local_db_var,
                common_db_var=self.bibles_common_db_var,
            )

            ttk.Separator(self, orient="horizontal").grid(row=2, column=0, sticky="ew")

            status_frame = ttk.Frame(self, padding=(8, 4))
            status_frame.grid(row=3, column=0, sticky="ew")
            status_frame.columnconfigure(0, weight=3)
            status_frame.columnconfigure(2, weight=2)

            file_info_wrap = ttk.Frame(status_frame)
            file_info_wrap.grid(row=0, column=0, sticky="ew")
            file_info_wrap.columnconfigure(0, weight=1)
            ttk.Label(file_info_wrap, textvariable=self.file_info_var, anchor="w").grid(
                row=0,
                column=0,
                sticky="ew",
            )
            ttk.Separator(status_frame, orient="vertical").grid(
                row=0,
                column=1,
                sticky="ns",
                padx=10,
            )
            message_label = ttk.Label(
                status_frame,
                textvariable=self.status_var,
                anchor="e",
                cursor="hand2",
            )
            message_label.grid(row=0, column=2, sticky="ew")
            message_label.bind("<Button-1>", self._open_message_log)
            self._update_ui_availability()
            self._update_section_db_labels()
            self._update_file_info()

        def _build_articles_section(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(1, weight=1)

            top = ttk.Frame(parent, padding=(8, 8, 8, 0))
            top.grid(row=0, column=0, sticky="ew")
            top.columnconfigure(1, weight=1)

            ttk.Label(top, text="Локализованная БД:").grid(row=0, column=0, sticky="w", padx=(0, 8))
            self.db_combo = ttk.Combobox(top, textvariable=self.db_var, state="readonly")
            self.db_combo.grid(row=0, column=1, sticky="ew")
            self.db_combo.bind("<<ComboboxSelected>>", self._on_db_combo_selected)

            articles_body = ttk.Frame(parent)
            articles_body.grid(row=1, column=0, sticky="nsew")
            articles_body.columnconfigure(0, weight=1)
            articles_body.rowconfigure(0, weight=1)
            self._build_articles_tab(articles_body)

        def _build_resources_section(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(1, weight=1)

            top = ttk.Frame(parent, padding=(8, 8, 8, 0))
            top.grid(row=0, column=0, sticky="ew")
            top.columnconfigure(1, weight=1)

            ttk.Label(top, text="Общая БД ресурсов:").grid(row=0, column=0, sticky="w", padx=(0, 8))
            ttk.Label(top, textvariable=self.resources_db_var, anchor="w").grid(row=0, column=1, sticky="ew")

            resources_body = ttk.Frame(parent)
            resources_body.grid(row=1, column=0, sticky="nsew")
            resources_body.columnconfigure(0, weight=1)
            resources_body.rowconfigure(0, weight=1)
            self._build_resources_tab(resources_body)

        def _build_strong_section(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(2, weight=1)

            top = ttk.Frame(parent, padding=(8, 8, 8, 0))
            top.grid(row=0, column=0, sticky="ew")
            top.columnconfigure(1, weight=1)
            top.columnconfigure(3, weight=1)

            ttk.Label(top, text="Общая БД:").grid(
                row=0,
                column=0,
                sticky="w",
                padx=(0, 8),
            )
            ttk.Label(top, textvariable=self.strong_common_db_var, anchor="w").grid(row=0, column=1, sticky="ew")
            ttk.Label(top, text="Локализованные БД:").grid(row=0, column=2, sticky="w", padx=(16, 8))
            self.entry_strong_langs = ttk.Entry(top, textvariable=self.strong_languages_var, state="readonly")
            self.entry_strong_langs.grid(row=0, column=3, sticky="ew")

            filter_row = ttk.Frame(parent, padding=(8, 8, 8, 0))
            filter_row.grid(row=1, column=0, sticky="ew")
            filter_row.columnconfigure(1, weight=1)
            ttk.Label(filter_row, text="Поиск (ID/слово/часть речи/переводы):").grid(
                row=0,
                column=0,
                sticky="w",
                padx=(0, 8),
            )
            self.entry_strong_filter = ttk.Entry(filter_row, textvariable=self.strong_filter_var)
            self.entry_strong_filter.grid(row=0, column=1, sticky="ew")
            self.btn_clear_strong_filter = ttk.Button(
                filter_row,
                text="Очистить",
                command=self._clear_strong_filter,
            )
            self.btn_clear_strong_filter.grid(row=0, column=2, padx=(8, 0))

            body = ttk.Frame(parent)
            body.grid(row=2, column=0, sticky="nsew")
            body.columnconfigure(0, weight=1)
            body.rowconfigure(0, weight=1)

            pane = self._new_split_pane(body)
            pane.grid(row=0, column=0, sticky="nsew")

            left = ttk.Frame(pane, padding=8)
            right = ttk.Frame(pane, padding=8)
            pane.add(left, stretch="always")
            pane.add(right, stretch="always")
            self._set_initial_split(pane, ratio=0.5)

            left.columnconfigure(0, weight=1)
            left.rowconfigure(0, weight=1)
            left.rowconfigure(1, weight=1)

            tree_wrap = ttk.Frame(left)
            tree_wrap.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
            tree_wrap.columnconfigure(0, weight=1)
            tree_wrap.rowconfigure(0, weight=1)

            self.strong_tree = ttk.Treeview(
                tree_wrap,
                columns=("id", "word", "synonyms", "origin", "category"),
                show="headings",
                selectmode="browse",
            )
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
            self.strong_tree.grid(row=0, column=0, sticky="nsew")
            self.strong_tree.bind("<<TreeviewSelect>>", self._on_strong_selected)

            strong_scroll = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.strong_tree.yview)
            strong_scroll.grid(row=0, column=1, sticky="ns")
            self.strong_tree.configure(yscrollcommand=strong_scroll.set)
            self._rebuild_strong_tree_columns()

            common_box = ttk.LabelFrame(left, text="Общая часть")
            common_box.grid(row=1, column=0, sticky="nsew")
            common_box.columnconfigure(1, weight=1)
            common_box.rowconfigure(4, weight=0)
            common_box.rowconfigure(5, weight=1)

            ttk.Label(common_box, text="Слово:").grid(row=0, column=0, sticky="w", padx=(8, 8), pady=(6, 4))
            self.entry_strong_word = ttk.Entry(common_box, textvariable=self.strong_word_var)
            self.entry_strong_word.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(6, 4))

            ttk.Label(common_box, text="Часть речи и форма:").grid(row=1, column=0, sticky="w", padx=(8, 8), pady=4)
            category_wrap = ttk.Frame(common_box)
            category_wrap.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=4)
            category_wrap.columnconfigure(0, weight=1)
            self.entry_strong_category = ttk.Entry(
                category_wrap,
                textvariable=self.strong_category_display_var,
                state="readonly",
            )
            self.entry_strong_category.grid(row=0, column=0, sticky="ew")
            self.btn_pick_strong_category = ttk.Button(
                category_wrap,
                text="Выбрать...",
                command=self._open_strong_category_picker,
            )
            self.btn_pick_strong_category.grid(row=0, column=1, padx=(8, 0))
            ttk.Label(
                common_box,
                textvariable=self.strong_category_raw_preview_var,
                foreground="#5f5f5f",
            ).grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 4))

            ttk.Label(common_box, text="Синонимы:").grid(row=3, column=0, sticky="w", padx=(8, 8), pady=4)
            self.entry_strong_synonyms = ttk.Entry(common_box, textvariable=self.strong_synonyms_var)
            self.entry_strong_synonyms.grid(row=3, column=1, sticky="ew", padx=(0, 8), pady=4)

            ttk.Label(common_box, text="Анализ слова:").grid(
                row=4,
                column=0,
                sticky="nw",
                padx=(8, 8),
                pady=4,
            )
            origin_wrap = ttk.Frame(common_box)
            origin_wrap.grid(row=4, column=1, sticky="ew", padx=(0, 8), pady=4)
            origin_wrap.columnconfigure(0, weight=1)
            self.strong_origin_text = tk.Text(origin_wrap, wrap="word", height=1, undo=True)
            self.strong_origin_text.grid(row=0, column=0, sticky="ew")
            origin_scroll = ttk.Scrollbar(origin_wrap, orient="vertical", command=self.strong_origin_text.yview)
            origin_scroll.grid(row=0, column=1, sticky="ns")
            self.strong_origin_text.configure(yscrollcommand=origin_scroll.set)

            ttk.Label(common_box, text="Использование:").grid(
                row=5,
                column=0,
                sticky="nw",
                padx=(8, 8),
                pady=(4, 8),
            )
            usage_wrap = ttk.Frame(common_box)
            usage_wrap.grid(row=5, column=1, sticky="nsew", padx=(0, 8), pady=(4, 8))
            usage_wrap.columnconfigure(0, weight=1)
            usage_wrap.rowconfigure(0, weight=1)
            self.strong_usage_text = tk.Text(usage_wrap, wrap="word", height=10, undo=True)
            self.strong_usage_text.grid(row=0, column=0, sticky="nsew")
            usage_scroll = ttk.Scrollbar(usage_wrap, orient="vertical", command=self.strong_usage_text.yview)
            usage_scroll.grid(row=0, column=1, sticky="ns")
            self.strong_usage_text.configure(yscrollcommand=usage_scroll.set)

            right.columnconfigure(0, weight=1)
            right.rowconfigure(0, weight=1)

            local_box = ttk.LabelFrame(right, text="Переводы")
            local_box.grid(row=0, column=0, sticky="nsew")
            local_box.columnconfigure(0, weight=1)
            local_box.rowconfigure(0, weight=1)
            self.strong_local_canvas = tk.Canvas(
                local_box,
                highlightthickness=0,
                borderwidth=0,
            )
            self.strong_local_canvas.grid(row=0, column=0, sticky="nsew")
            local_scroll = ttk.Scrollbar(
                local_box,
                orient="vertical",
                command=self.strong_local_canvas.yview,
            )
            local_scroll.grid(row=0, column=1, sticky="ns")
            self.strong_local_canvas.configure(yscrollcommand=local_scroll.set)
            self.strong_local_container = ttk.Frame(self.strong_local_canvas)
            self.strong_local_window_id = self.strong_local_canvas.create_window(
                (0, 0),
                window=self.strong_local_container,
                anchor="nw",
            )
            self.strong_local_container.bind("<Configure>", self._on_strong_local_container_configure)
            self.strong_local_canvas.bind("<Configure>", self._on_strong_local_canvas_configure)
            self._rebuild_strong_localized_editors()

            strong_actions = ttk.Frame(right)
            strong_actions.grid(row=1, column=0, sticky="w", pady=(8, 0))
            self.btn_apply_strong = ttk.Button(
                strong_actions,
                **self._button_kwargs("save", "Сохранить"),
                command=self._apply_strong_changes,
            )
            self.btn_apply_strong.pack(side="left")
            self.btn_cancel_strong = ttk.Button(
                strong_actions,
                **self._button_kwargs("cancel", "Отменить"),
                command=self._reload_selected_strong,
            )
            self.btn_cancel_strong.pack(side="left", padx=(8, 0))
            self.btn_group_translate_strong = ttk.Button(
                strong_actions,
                **self._button_kwargs("translate", "Групповой перевод..."),
                command=self._open_strong_group_translation_dialog,
            )
            self.btn_group_translate_strong.pack(side="left", padx=(16, 0))

        def _build_future_section(
            self,
            parent: ttk.Frame,
            message: str,
            *,
            local_db_var: tk.StringVar,
            common_db_var: tk.StringVar,
        ) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(1, weight=1)

            top = ttk.Frame(parent, padding=(8, 8, 8, 0))
            top.grid(row=0, column=0, sticky="ew")
            top.columnconfigure(1, weight=1)
            top.columnconfigure(3, weight=1)

            ttk.Label(top, text="Локализованная БД:").grid(row=0, column=0, sticky="w", padx=(0, 8))
            ttk.Label(top, textvariable=local_db_var, anchor="w").grid(row=0, column=1, sticky="ew")
            ttk.Label(top, text="Общая БД:").grid(row=0, column=2, sticky="w", padx=(16, 8))
            ttk.Label(top, textvariable=common_db_var, anchor="w").grid(row=0, column=3, sticky="ew")

            body = ttk.Frame(parent, padding=20)
            body.grid(row=1, column=0, sticky="nsew")
            body.columnconfigure(0, weight=1)
            body.rowconfigure(0, weight=1)
            ttk.Label(
                body,
                text=message,
                anchor="center",
                justify="center",
                foreground="#4f4f4f",
            ).grid(row=0, column=0, sticky="nsew")

        def _build_sources_section(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(1, weight=1)

            top = ttk.Frame(parent, padding=(8, 8, 8, 0))
            top.grid(row=0, column=0, sticky="ew")
            top.columnconfigure(1, weight=1)
            top.columnconfigure(3, weight=1)

            ttk.Label(top, text="Локализованная БД:").grid(row=0, column=0, sticky="w", padx=(0, 8))
            ttk.Label(top, textvariable=self.sources_local_db_var, anchor="w").grid(row=0, column=1, sticky="ew")
            ttk.Label(top, text="Общая БД:").grid(row=0, column=2, sticky="w", padx=(16, 8))
            ttk.Label(top, textvariable=self.sources_common_db_var, anchor="w").grid(row=0, column=3, sticky="ew")

            body = ttk.Frame(parent)
            body.grid(row=1, column=0, sticky="nsew")
            body.columnconfigure(0, weight=1)
            body.rowconfigure(0, weight=1)

            pane = self._new_split_pane(body)
            pane.grid(row=0, column=0, sticky="nsew")

            left = ttk.Frame(pane, padding=8)
            right = ttk.Frame(pane, padding=8)
            pane.add(left, stretch="always")
            pane.add(right, stretch="always")
            self._set_initial_split(pane, ratio=0.36)

            left.columnconfigure(0, weight=1)
            left.rowconfigure(1, weight=1)

            filter_row = ttk.Frame(left)
            filter_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
            filter_row.columnconfigure(1, weight=1)
            ttk.Label(filter_row, text="Поиск:").grid(row=0, column=0, sticky="w", padx=(0, 6))
            self.entry_primary_source_filter = ttk.Entry(filter_row, textvariable=self.primary_source_filter_var)
            self.entry_primary_source_filter.grid(row=0, column=1, sticky="ew", padx=(0, 10))
            ttk.Label(filter_row, text="Группа:").grid(row=0, column=2, sticky="w", padx=(0, 6))
            self.combo_primary_source_group = ttk.Combobox(
                filter_row,
                textvariable=self.primary_source_group_var,
                state="readonly",
                width=14,
                values=("all", "full", "significant", "fragment"),
            )
            self.combo_primary_source_group.grid(row=0, column=3, sticky="w")
            self.combo_primary_source_group.bind("<<ComboboxSelected>>", self._on_primary_source_filter_combo_changed)

            self.primary_sources_tree = ttk.Treeview(
                left,
                columns=("id", "title", "group", "pages", "words", "verses", "en", "es", "uk", "ru"),
                show="headings",
                selectmode="browse",
            )
            for column, title, width, anchor in [
                ("id", "ID", 78, "center"),
                ("title", "Заголовок", 220, "w"),
                ("group", "Группа", 110, "center"),
                ("pages", "Стр.", 55, "center"),
                ("words", "Слова", 64, "center"),
                ("verses", "Verse", 64, "center"),
                ("en", "EN", 40, "center"),
                ("es", "ES", 40, "center"),
                ("uk", "UK", 40, "center"),
                ("ru", "RU", 40, "center"),
            ]:
                self.primary_sources_tree.heading(column, text=title)
                self.primary_sources_tree.column(column, width=width, anchor=anchor)
            self.primary_sources_tree.grid(row=1, column=0, sticky="nsew")
            self.primary_sources_tree.bind("<<TreeviewSelect>>", self._on_primary_source_selected)

            sources_scroll = ttk.Scrollbar(left, orient="vertical", command=self.primary_sources_tree.yview)
            sources_scroll.grid(row=1, column=1, sticky="ns")
            self.primary_sources_tree.configure(yscrollcommand=sources_scroll.set)

            source_buttons = ttk.Frame(left)
            source_buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_reload_primary_sources = ttk.Button(
                source_buttons,
                **self._button_kwargs("refresh", "Перечитать"),
                command=self._reload_primary_sources_section,
            )
            self.btn_reload_primary_sources.pack(side="left")
            self.btn_add_primary_source = ttk.Button(
                source_buttons,
                **self._button_kwargs("add", "Добавить"),
                command=self._add_primary_source,
            )
            self.btn_add_primary_source.pack(side="left", padx=(8, 0))
            self.btn_delete_primary_source = ttk.Button(
                source_buttons,
                **self._button_kwargs("delete", "Удалить"),
                command=self._delete_primary_source,
            )
            self.btn_delete_primary_source.pack(side="left", padx=(8, 0))

            secondary_buttons = ttk.Frame(left)
            secondary_buttons.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_download_source_pages = ttk.Button(
                secondary_buttons,
                **self._button_kwargs("download", "Скачать страницы"),
                command=self._download_selected_primary_source_pages,
            )
            self.btn_download_source_pages.pack(side="left")
            ttk.Checkbutton(
                secondary_buttons,
                text="Перекачать",
                variable=self.primary_source_force_download_var,
            ).pack(side="left", padx=(10, 0))
            self.btn_open_primary_sources_root = ttk.Button(
                secondary_buttons,
                **self._button_kwargs("open_resource", "Открыть папку"),
                command=self._open_primary_sources_root_dir,
            )
            self.btn_open_primary_sources_root.pack(side="left", padx=(10, 0))

            ttk.Label(
                left,
                textvariable=self.primary_source_images_root_var,
                foreground="#5f5f5f",
            ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

            right.columnconfigure(0, weight=1)
            right.rowconfigure(0, weight=1)

            self.primary_source_tabs = ttk.Notebook(right)
            self.primary_source_tabs.grid(row=0, column=0, sticky="nsew")

            meta_tab = ttk.Frame(self.primary_source_tabs, padding=8)
            links_tab = ttk.Frame(self.primary_source_tabs, padding=8)
            attribution_tab = ttk.Frame(self.primary_source_tabs, padding=8)
            pages_tab = ttk.Frame(self.primary_source_tabs, padding=8)
            self.primary_source_tabs.add(meta_tab, text="Метаданные")
            self.primary_source_tabs.add(links_tab, text="Ссылки")
            self.primary_source_tabs.add(attribution_tab, text="Атрибуция")
            self.primary_source_tabs.add(pages_tab, text="Страницы / OCR")

            self._build_primary_source_metadata_tab(meta_tab)
            self._build_primary_source_links_tab(links_tab)
            self._build_primary_source_attributions_tab(attribution_tab)
            self._build_primary_source_pages_tab(pages_tab)

        def _build_primary_source_metadata_tab(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=3)
            parent.columnconfigure(1, weight=2)
            parent.rowconfigure(4, weight=1)

            meta_frame = ttk.LabelFrame(parent, text="Общие данные")
            meta_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
            meta_frame.columnconfigure(1, weight=1)

            ttk.Label(meta_frame, text="ID:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_primary_source_id = ttk.Entry(meta_frame, textvariable=self.primary_source_id_var, state="readonly")
            self.entry_primary_source_id.grid(row=0, column=1, sticky="ew", pady=4)

            ttk.Label(meta_frame, text="Family:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
            self.combo_primary_source_family = ttk.Combobox(
                meta_frame,
                textvariable=self.primary_source_family_var,
                state="readonly",
                values=("uncial", "papyrus", "other"),
            )
            self.combo_primary_source_family.grid(row=1, column=1, sticky="ew", pady=4)

            ttk.Label(meta_frame, text="Number:").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_primary_source_number = ttk.Entry(meta_frame, textvariable=self.primary_source_number_var)
            self.entry_primary_source_number.grid(row=2, column=1, sticky="ew", pady=4)

            ttk.Label(meta_frame, text="Group:").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
            self.combo_primary_source_group_kind = ttk.Combobox(
                meta_frame,
                textvariable=self.primary_source_group_kind_var,
                state="readonly",
                values=("full", "significant", "fragment"),
            )
            self.combo_primary_source_group_kind.grid(row=3, column=1, sticky="ew", pady=4)

            ttk.Label(meta_frame, text="Sort order:").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_primary_source_sort_order = ttk.Entry(meta_frame, textvariable=self.primary_source_sort_order_var)
            self.entry_primary_source_sort_order.grid(row=4, column=1, sticky="ew", pady=4)

            ttk.Label(meta_frame, text="Verses count:").grid(row=5, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_primary_source_verses_count = ttk.Entry(meta_frame, textvariable=self.primary_source_verses_count_var)
            self.entry_primary_source_verses_count.grid(row=5, column=1, sticky="ew", pady=4)

            ttk.Label(meta_frame, text="Preview key:").grid(row=6, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_primary_source_preview_key = ttk.Entry(meta_frame, textvariable=self.primary_source_preview_key_var)
            self.entry_primary_source_preview_key.grid(row=6, column=1, sticky="ew", pady=4)

            ttk.Label(meta_frame, text="Max scale:").grid(row=7, column=0, sticky="w", padx=(0, 8), pady=4)
            self.entry_primary_source_default_scale = ttk.Entry(
                meta_frame,
                textvariable=self.primary_source_default_max_scale_var,
            )
            self.entry_primary_source_default_scale.grid(row=7, column=1, sticky="ew", pady=4)

            self.check_primary_source_can_show_images = ttk.Checkbutton(
                meta_frame,
                text="Можно показывать изображения",
                variable=self.primary_source_can_show_images_var,
            )
            self.check_primary_source_can_show_images.grid(row=8, column=1, sticky="w", pady=4)

            self.check_primary_source_images_are_monochrome = ttk.Checkbutton(
                meta_frame,
                text="Изображения монохромные",
                variable=self.primary_source_images_are_monochrome_var,
            )
            self.check_primary_source_images_are_monochrome.grid(row=9, column=1, sticky="w", pady=4)

            ttk.Label(meta_frame, text="Notes:").grid(row=10, column=0, sticky="nw", padx=(0, 8), pady=4)
            self.primary_source_notes_text = tk.Text(meta_frame, wrap="word", height=4)
            self.primary_source_notes_text.grid(row=10, column=1, sticky="nsew", pady=4)
            meta_frame.rowconfigure(10, weight=1)

            meta_actions = ttk.Frame(meta_frame)
            meta_actions.grid(row=11, column=1, sticky="w", pady=(8, 0))
            self.btn_save_primary_source_metadata = ttk.Button(
                meta_actions,
                **self._button_kwargs("save", "Сохранить источник"),
                command=self._save_primary_source_metadata,
            )
            self.btn_save_primary_source_metadata.pack(side="left")
            self.btn_reload_primary_source_metadata = ttk.Button(
                meta_actions,
                **self._button_kwargs("cancel", "Перечитать из БД"),
                command=self._reload_selected_primary_source,
            )
            self.btn_reload_primary_source_metadata.pack(side="left", padx=(8, 0))
            self.btn_import_primary_source_preview = ttk.Button(
                meta_actions,
                **self._button_kwargs("replace_file", "Импорт preview"),
                command=self._import_primary_source_preview_resource,
            )
            self.btn_import_primary_source_preview.pack(side="left", padx=(8, 0))
            self.btn_open_primary_source_preview = ttk.Button(
                meta_actions,
                **self._button_kwargs("open_resource", "Открыть preview"),
                command=self._open_primary_source_preview_resource,
            )
            self.btn_open_primary_source_preview.pack(side="left", padx=(8, 0))

            preview_frame = ttk.LabelFrame(parent, text="Preview")
            preview_frame.grid(row=0, column=1, sticky="nsew")
            preview_frame.columnconfigure(0, weight=1)
            preview_frame.rowconfigure(0, weight=1)
            self.primary_source_preview_label = tk.Label(
                preview_frame,
                text="Preview ресурса пока недоступен.",
                justify="center",
                anchor="center",
                relief="solid",
                borderwidth=1,
                padx=8,
                pady=8,
            )
            self.primary_source_preview_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

            localized_box = ttk.LabelFrame(parent, text="Локализованные поля")
            localized_box.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
            localized_box.columnconfigure(1, weight=1)

            ttk.Label(localized_box, textvariable=self.primary_source_locale_info_var).grid(
                row=0,
                column=0,
                columnspan=2,
                sticky="w",
                pady=(0, 8),
            )

            localized_fields = [
                ("Title markup:", self.primary_source_title_markup_var),
                ("Date label:", self.primary_source_date_label_var),
                ("Content label:", self.primary_source_content_label_var),
                ("Material text:", self.primary_source_material_text_var),
                ("Text style text:", self.primary_source_text_style_text_var),
                ("Found text:", self.primary_source_found_text_var),
                ("Classification text:", self.primary_source_classification_text_var),
                ("Current location text:", self.primary_source_current_location_text_var),
            ]
            for idx, (label, variable) in enumerate(localized_fields, start=1):
                ttk.Label(localized_box, text=label).grid(row=idx, column=0, sticky="w", padx=(0, 8), pady=3)
                ttk.Entry(localized_box, textvariable=variable).grid(row=idx, column=1, sticky="ew", pady=3)

            ttk.Label(
                parent,
                textvariable=self.primary_source_validation_var,
                foreground="#7a4c00",
                justify="left",
                wraplength=760,
            ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        def _build_primary_source_links_tab(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(0, weight=1)

            self.primary_source_links_tree = ttk.Treeview(
                parent,
                columns=("link_id", "sort_order", "role", "title", "url"),
                show="headings",
                selectmode="browse",
            )
            for column, title, width, anchor in [
                ("link_id", "Link ID", 120, "center"),
                ("sort_order", "Sort", 60, "center"),
                ("role", "Role", 110, "center"),
                ("title", "Title", 180, "w"),
                ("url", "URL", 520, "w"),
            ]:
                self.primary_source_links_tree.heading(column, text=title)
                self.primary_source_links_tree.column(column, width=width, anchor=anchor)
            self.primary_source_links_tree.grid(row=0, column=0, sticky="nsew")
            self.primary_source_links_tree.bind("<<TreeviewSelect>>", self._on_primary_source_link_selected)

            links_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.primary_source_links_tree.yview)
            links_scroll.grid(row=0, column=1, sticky="ns")
            self.primary_source_links_tree.configure(yscrollcommand=links_scroll.set)

            actions = ttk.Frame(parent)
            actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_add_primary_source_link = ttk.Button(
                actions,
                **self._button_kwargs("add", "Добавить ссылку"),
                command=self._add_primary_source_link,
            )
            self.btn_add_primary_source_link.pack(side="left")
            self.btn_edit_primary_source_link = ttk.Button(
                actions,
                **self._button_kwargs("save", "Изменить"),
                command=self._edit_primary_source_link,
            )
            self.btn_edit_primary_source_link.pack(side="left", padx=(8, 0))
            self.btn_delete_primary_source_link = ttk.Button(
                actions,
                **self._button_kwargs("delete", "Удалить"),
                command=self._delete_primary_source_link,
            )
            self.btn_delete_primary_source_link.pack(side="left", padx=(8, 0))
            self.btn_open_primary_source_link = ttk.Button(
                actions,
                **self._button_kwargs("open_in_new", "Открыть URL"),
                command=self._open_primary_source_link_url,
            )
            self.btn_open_primary_source_link.pack(side="left", padx=(8, 0))

        def _build_primary_source_attributions_tab(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(0, weight=1)

            self.primary_source_attributions_tree = ttk.Treeview(
                parent,
                columns=("attribution_id", "sort_order", "text", "url"),
                show="headings",
                selectmode="browse",
            )
            for column, title, width, anchor in [
                ("attribution_id", "ID", 120, "center"),
                ("sort_order", "Sort", 60, "center"),
                ("text", "Text", 260, "w"),
                ("url", "URL", 520, "w"),
            ]:
                self.primary_source_attributions_tree.heading(column, text=title)
                self.primary_source_attributions_tree.column(column, width=width, anchor=anchor)
            self.primary_source_attributions_tree.grid(row=0, column=0, sticky="nsew")
            self.primary_source_attributions_tree.bind(
                "<<TreeviewSelect>>",
                self._on_primary_source_attribution_selected,
            )

            attr_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.primary_source_attributions_tree.yview)
            attr_scroll.grid(row=0, column=1, sticky="ns")
            self.primary_source_attributions_tree.configure(yscrollcommand=attr_scroll.set)

            actions = ttk.Frame(parent)
            actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_add_primary_source_attribution = ttk.Button(
                actions,
                **self._button_kwargs("add", "Добавить атрибуцию"),
                command=self._add_primary_source_attribution,
            )
            self.btn_add_primary_source_attribution.pack(side="left")
            self.btn_edit_primary_source_attribution = ttk.Button(
                actions,
                **self._button_kwargs("save", "Изменить"),
                command=self._edit_primary_source_attribution,
            )
            self.btn_edit_primary_source_attribution.pack(side="left", padx=(8, 0))
            self.btn_delete_primary_source_attribution = ttk.Button(
                actions,
                **self._button_kwargs("delete", "Удалить"),
                command=self._delete_primary_source_attribution,
            )
            self.btn_delete_primary_source_attribution.pack(side="left", padx=(8, 0))
            self.btn_open_primary_source_attribution_url = ttk.Button(
                actions,
                **self._button_kwargs("open_in_new", "Открыть URL"),
                command=self._open_primary_source_attribution_url,
            )
            self.btn_open_primary_source_attribution_url.pack(side="left", padx=(8, 0))

        def _build_primary_source_pages_tab(self, parent: ttk.Frame) -> None:
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(1, weight=1)

            pages_box = ttk.LabelFrame(parent, text="Страницы")
            pages_box.grid(row=0, column=0, sticky="nsew")
            pages_box.columnconfigure(0, weight=1)
            pages_box.rowconfigure(0, weight=1)

            self.primary_source_pages_tree = ttk.Treeview(
                pages_box,
                columns=("page_name", "sort_order", "content_ref", "image_path", "local"),
                show="headings",
                selectmode="browse",
                height=9,
            )
            for column, title, width, anchor in [
                ("page_name", "Page", 120, "center"),
                ("sort_order", "Sort", 60, "center"),
                ("content_ref", "Content", 120, "center"),
                ("image_path", "Image path", 430, "w"),
                ("local", "Local", 60, "center"),
            ]:
                self.primary_source_pages_tree.heading(column, text=title)
                self.primary_source_pages_tree.column(column, width=width, anchor=anchor)
            self.primary_source_pages_tree.grid(row=0, column=0, sticky="nsew")
            self.primary_source_pages_tree.bind("<<TreeviewSelect>>", self._on_primary_source_page_selected)

            pages_scroll = ttk.Scrollbar(pages_box, orient="vertical", command=self.primary_source_pages_tree.yview)
            pages_scroll.grid(row=0, column=1, sticky="ns")
            self.primary_source_pages_tree.configure(yscrollcommand=pages_scroll.set)

            page_actions = ttk.Frame(pages_box)
            page_actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_add_primary_source_page = ttk.Button(
                page_actions,
                **self._button_kwargs("add", "Добавить страницу"),
                command=self._add_primary_source_page,
            )
            self.btn_add_primary_source_page.pack(side="left")
            self.btn_edit_primary_source_page = ttk.Button(
                page_actions,
                **self._button_kwargs("save", "Изменить"),
                command=self._edit_primary_source_page,
            )
            self.btn_edit_primary_source_page.pack(side="left", padx=(8, 0))
            self.btn_delete_primary_source_page = ttk.Button(
                page_actions,
                **self._button_kwargs("delete", "Удалить"),
                command=self._delete_primary_source_page,
            )
            self.btn_delete_primary_source_page.pack(side="left", padx=(8, 0))
            self.btn_download_primary_source_page = ttk.Button(
                page_actions,
                **self._button_kwargs("download", "Скачать страницу"),
                command=self._download_selected_primary_source_page,
            )
            self.btn_download_primary_source_page.pack(side="left", padx=(8, 0))
            self.btn_open_primary_source_page = ttk.Button(
                page_actions,
                **self._button_kwargs("open_resource", "Открыть локальный файл"),
                command=self._open_selected_primary_source_page_file,
            )
            self.btn_open_primary_source_page.pack(side="left", padx=(8, 0))
            self.btn_open_primary_source_contours = ttk.Button(
                page_actions,
                **self._button_kwargs("open_in_app", "Contour editor"),
                command=self._open_selected_primary_source_contour_editor,
            )
            self.btn_open_primary_source_contours.pack(side="left", padx=(8, 0))

            ttk.Label(
                pages_box,
                textvariable=self.primary_source_page_info_var,
                foreground="#5f5f5f",
            ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

            lower_pane = self._new_split_pane(parent, orient=tk.HORIZONTAL)
            lower_pane.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

            words_box = ttk.LabelFrame(lower_pane, text="Слова страницы")
            verses_box = ttk.LabelFrame(lower_pane, text="Verse / Contours")
            lower_pane.add(words_box, stretch="always")
            lower_pane.add(verses_box, stretch="always")
            self._set_initial_split(lower_pane, ratio=0.5)

            words_box.columnconfigure(0, weight=1)
            words_box.rowconfigure(0, weight=1)
            self.primary_source_words_tree = ttk.Treeview(
                words_box,
                columns=("word_index", "text", "strong_number", "rectangles"),
                show="headings",
                selectmode="browse",
            )
            for column, title, width, anchor in [
                ("word_index", "#", 56, "center"),
                ("text", "Text", 180, "w"),
                ("strong_number", "Strong", 80, "center"),
                ("rectangles", "Rects", 70, "center"),
            ]:
                self.primary_source_words_tree.heading(column, text=title)
                self.primary_source_words_tree.column(column, width=width, anchor=anchor)
            self.primary_source_words_tree.grid(row=0, column=0, sticky="nsew")
            self.primary_source_words_tree.bind("<<TreeviewSelect>>", self._on_primary_source_word_selected)
            words_scroll = ttk.Scrollbar(words_box, orient="vertical", command=self.primary_source_words_tree.yview)
            words_scroll.grid(row=0, column=1, sticky="ns")
            self.primary_source_words_tree.configure(yscrollcommand=words_scroll.set)

            word_actions = ttk.Frame(words_box)
            word_actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_add_primary_source_word = ttk.Button(
                word_actions,
                **self._button_kwargs("add", "Добавить слово"),
                command=self._add_primary_source_word,
            )
            self.btn_add_primary_source_word.pack(side="left")
            self.btn_edit_primary_source_word = ttk.Button(
                word_actions,
                **self._button_kwargs("save", "Изменить"),
                command=self._edit_primary_source_word,
            )
            self.btn_edit_primary_source_word.pack(side="left", padx=(8, 0))
            self.btn_delete_primary_source_word = ttk.Button(
                word_actions,
                **self._button_kwargs("delete", "Удалить"),
                command=self._delete_primary_source_word,
            )
            self.btn_delete_primary_source_word.pack(side="left", padx=(8, 0))

            verses_box.columnconfigure(0, weight=1)
            verses_box.rowconfigure(0, weight=1)
            self.primary_source_verses_tree = ttk.Treeview(
                verses_box,
                columns=("verse_index", "reference", "word_indexes", "contours"),
                show="headings",
                selectmode="browse",
            )
            for column, title, width, anchor in [
                ("verse_index", "#", 56, "center"),
                ("reference", "Ref", 110, "center"),
                ("word_indexes", "Words", 120, "center"),
                ("contours", "Contours", 70, "center"),
            ]:
                self.primary_source_verses_tree.heading(column, text=title)
                self.primary_source_verses_tree.column(column, width=width, anchor=anchor)
            self.primary_source_verses_tree.grid(row=0, column=0, sticky="nsew")
            self.primary_source_verses_tree.bind("<<TreeviewSelect>>", self._on_primary_source_verse_selected)
            verses_scroll = ttk.Scrollbar(verses_box, orient="vertical", command=self.primary_source_verses_tree.yview)
            verses_scroll.grid(row=0, column=1, sticky="ns")
            self.primary_source_verses_tree.configure(yscrollcommand=verses_scroll.set)

            verse_actions = ttk.Frame(verses_box)
            verse_actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_add_primary_source_verse = ttk.Button(
                verse_actions,
                **self._button_kwargs("add", "Добавить verse"),
                command=self._add_primary_source_verse,
            )
            self.btn_add_primary_source_verse.pack(side="left")
            self.btn_edit_primary_source_verse = ttk.Button(
                verse_actions,
                **self._button_kwargs("save", "Изменить"),
                command=self._edit_primary_source_verse,
            )
            self.btn_edit_primary_source_verse.pack(side="left", padx=(8, 0))
            self.btn_delete_primary_source_verse = ttk.Button(
                verse_actions,
                **self._button_kwargs("delete", "Удалить"),
                command=self._delete_primary_source_verse,
            )
            self.btn_delete_primary_source_verse.pack(side="left", padx=(8, 0))
            self.btn_edit_primary_source_verse_contours = ttk.Button(
                verse_actions,
                **self._button_kwargs("open_in_app", "Contour editor"),
                command=self._open_selected_primary_source_contour_editor,
            )
            self.btn_edit_primary_source_verse_contours.pack(side="left", padx=(8, 0))
            self.btn_import_primary_source_verse_snippet = ttk.Button(
                verse_actions,
                **self._button_kwargs("publish", "Import Verse(...)"),
                command=self._import_primary_source_verse_snippet,
            )
            self.btn_import_primary_source_verse_snippet.pack(side="left", padx=(8, 0))

        def _on_main_section_changed(self, _event: object | None = None) -> None:
            self._update_file_info()

        def _active_section_key(self) -> str:
            selected = self.sections.select()
            if selected == str(self.resources_section):
                return "resources"
            if selected == str(self.strong_section):
                return "strong"
            if selected == str(self.sources_section):
                return "sources"
            if selected == str(self.bibles_section):
                return "bibles"
            return "articles"

        def _reload_resources_section(self) -> None:
            self._open_common_connection()
            self._load_common_resources()
            self._load_strong_rows()
            self._update_ui_availability()
            self._update_file_info()
            if self.common_db_path is None:
                self._set_status("Общая БД ресурсов не найдена.")
            else:
                self._set_status(f"Ресурсы перечитаны из {self.common_db_path.stem}.")

        def _reload_strong_section(self) -> None:
            self._open_common_connection()
            self._load_common_resources()
            self._load_strong_rows()
            self._update_ui_availability()
            self._update_file_info()
            if self.common_db_path is None:
                self._set_status("Общая БД не найдена. Словарь Стронга недоступен.")
                return
            if not self.db_files:
                self._set_status("Локализованные БД не найдены. Словарь Стронга недоступен.")
                return
            self._set_status(
                (
                    "Словарь Стронга перечитан: "
                    f"{self.common_db_path.stem} + {len(self.db_files)} локализованных БД."
                )
            )

        def _update_section_db_labels(self) -> None:
            local_text = "-"
            if self.current_db_path is not None:
                local_text = self.current_db_path.stem
            self.strong_local_db_var.set(local_text)
            self.sources_local_db_var.set(local_text)
            self.bibles_local_db_var.set(local_text)
            self.primary_source_locale_info_var.set(f"Локализованная БД: {local_text}")

            common_text = "-"
            if self.common_db_path is not None:
                common_text = self.common_db_path.stem
            self.resources_db_var.set(common_text)
            self.strong_common_db_var.set(common_text)
            self.sources_common_db_var.set(common_text)
            self.bibles_common_db_var.set(common_text)
            languages = [lang for lang, _ in self._localized_db_entries()]
            self.strong_languages_var.set(", ".join(languages) if languages else "-")
            self.primary_source_images_root_var.set(str(self._primary_sources_root_dir()))


        def _maximize_window(self) -> None:
            try:
                self.state("zoomed")
                return
            except tk.TclError:
                pass
            try:
                self.attributes("-zoomed", True)
                return
            except tk.TclError:
                pass
            width = self.winfo_screenwidth()
            height = self.winfo_screenheight()
            self.geometry(f"{width}x{height}+0+0")

        def _prepare_icons(self) -> None:
            self.ui_icons.clear()
            for key, encoded_png in self.ICON_PNG_BASE64.items():
                try:
                    self.ui_icons[key] = tk.PhotoImage(data=encoded_png)
                except tk.TclError:
                    continue

        def _button_kwargs(self, icon_name: str, text: str) -> dict[str, object]:
            icon = self.ui_icons.get(icon_name)
            if icon is None:
                return {"text": text}
            return {
                "text": text,
                "image": icon,
                "compound": "left",
            }

        def _new_split_pane(
            self,
            parent: tk.Misc,
            *,
            orient: str = tk.HORIZONTAL,
        ) -> tk.PanedWindow:
            pane = tk.PanedWindow(
                parent,
                orient=orient,
                sashwidth=8,
                sashrelief="raised",
                showhandle=True,
                relief="groove",
                bd=1,
                opaqueresize=True,
            )
            try:
                cursor = "sb_h_double_arrow" if orient == tk.HORIZONTAL else "sb_v_double_arrow"
                pane.configure(sashcursor=cursor, handlesize=8, handlepad=2, sashpad=2)
            except tk.TclError:
                pass
            return pane

        def _set_initial_split(self, pane: tk.PanedWindow, *, ratio: float = 0.5) -> None:
            safe_ratio = max(0.1, min(0.9, ratio))

            def apply_split() -> None:
                try:
                    if len(pane.panes()) < 2:
                        return
                    width = pane.winfo_width()
                    if width <= 2:
                        pane.after(50, apply_split)
                        return
                    pane.sash_place(0, int(width * safe_ratio), 1)
                except tk.TclError:
                    return

            pane.after_idle(apply_split)

        def _set_ttk_widget_enabled(
            self,
            widget: tk.Widget,
            enabled: bool,
            *,
            readonly_when_enabled: bool = False,
        ) -> None:
            if isinstance(widget, ttk.Combobox):
                if enabled:
                    widget.configure(state="readonly" if readonly_when_enabled else "normal")
                else:
                    widget.configure(state="disabled")
                return
            if isinstance(widget, ttk.Entry):
                if enabled:
                    widget.configure(state="readonly" if readonly_when_enabled else "normal")
                else:
                    widget.configure(state="disabled")
                return
            if hasattr(widget, "state"):
                try:
                    widget.state(["!disabled"] if enabled else ["disabled"])
                    return
                except tk.TclError:
                    pass
            try:
                widget.configure(state="normal" if enabled else "disabled")
            except tk.TclError:
                pass

        def _set_editor_controls_enabled(
            self,
            localized_enabled: bool,
            resources_enabled: bool,
            strong_enabled: bool,
            sources_enabled: bool,
        ) -> None:
            localized_widgets: list[tuple[tk.Widget, bool]] = [
                (self.articles_tree, False),
                (self.btn_add_article, False),
                (self.btn_delete_article, False),
                (self.btn_vacuum_localized_db, False),
                (self.article_route_entry, False),
                (self.entry_topic_name, False),
                (self.entry_topic_description, False),
                (self.topic_icon_combo, True),
                (self.entry_topic_sort, False),
                (self.check_topic_visible, False),
                (self.btn_apply_topic, False),
                (self.btn_cancel_topic, False),
                (self.md_tabs, False),
            ]
            for widget, readonly_when_enabled in localized_widgets:
                self._set_ttk_widget_enabled(
                    widget,
                    localized_enabled,
                    readonly_when_enabled=readonly_when_enabled,
                )

            self.markdown_text.configure(state="normal" if localized_enabled else "disabled")
            if self.md_template_toolbar is not None:
                self.md_template_toolbar.set_enabled(localized_enabled)
            if self.preview_text is not None:
                self.preview_text.configure(state="disabled")

            resource_widgets: list[tuple[tk.Widget, bool]] = [
                (self.resources_tree, False),
                (self.btn_add_resource, False),
                (self.btn_delete_resource, False),
                (self.btn_open_resource, False),
                (self.btn_export_resource, False),
                (self.btn_vacuum_resources, False),
                (self.entry_resource_key, False),
                (self.entry_resource_name, False),
                (self.entry_resource_mime, False),
                (self.btn_pick_resource_file, False),
                (self.btn_apply_resource, False),
                (self.btn_cancel_resource, False),
            ]
            for widget, readonly_when_enabled in resource_widgets:
                self._set_ttk_widget_enabled(
                    widget,
                    resources_enabled,
                    readonly_when_enabled=readonly_when_enabled,
                )
            if not resources_enabled:
                self.resource_preview_image_label.configure(
                    image="",
                    text="Общая БД ресурсов не найдена в рабочей папке.",
                )
            elif self.selected_resource_index is None and not self.resource_data_buffer:
                self.resource_preview_image_label.configure(
                    image="",
                    text="Предпросмотр ресурса недоступен.\nВыберите запись из списка.",
                )

            strong_widgets: list[tuple[tk.Widget, bool]] = [
                (self.entry_strong_langs, True),
                (self.entry_strong_filter, False),
                (self.btn_clear_strong_filter, False),
                (self.strong_tree, False),
                (self.entry_strong_word, False),
                (self.entry_strong_category, True),
                (self.btn_pick_strong_category, False),
                (self.entry_strong_synonyms, False),
                (self.btn_apply_strong, False),
                (self.btn_cancel_strong, False),
                (self.btn_group_translate_strong, False),
            ]
            for widget, readonly_when_enabled in strong_widgets:
                self._set_ttk_widget_enabled(
                    widget,
                    strong_enabled,
                    readonly_when_enabled=readonly_when_enabled,
                )
            self.strong_origin_text.configure(state="normal" if strong_enabled else "disabled")
            self.strong_usage_text.configure(state="normal" if strong_enabled else "disabled")
            for text_widget in self.strong_desc_texts_by_lang.values():
                text_widget.configure(state="normal" if strong_enabled else "disabled")

            if not strong_enabled:
                self._clear_strong_editor(
                    message="Откройте общую БД для редактирования словаря Стронга.",
                )
            elif self.selected_strong_index is None:
                self._clear_strong_editor()

            source_widgets: list[tuple[tk.Widget, bool]] = [
                (self.entry_primary_source_filter, False),
                (self.combo_primary_source_group, True),
                (self.primary_sources_tree, False),
                (self.btn_reload_primary_sources, False),
                (self.btn_add_primary_source, False),
                (self.btn_delete_primary_source, False),
                (self.btn_download_source_pages, False),
                (self.btn_open_primary_sources_root, False),
                (self.primary_source_tabs, False),
                (self.entry_primary_source_id, True),
                (self.combo_primary_source_family, True),
                (self.entry_primary_source_number, False),
                (self.combo_primary_source_group_kind, True),
                (self.entry_primary_source_sort_order, False),
                (self.entry_primary_source_verses_count, False),
                (self.entry_primary_source_preview_key, False),
                (self.entry_primary_source_default_scale, False),
                (self.check_primary_source_can_show_images, False),
                (self.check_primary_source_images_are_monochrome, False),
                (self.btn_save_primary_source_metadata, False),
                (self.btn_reload_primary_source_metadata, False),
                (self.btn_import_primary_source_preview, False),
                (self.btn_open_primary_source_preview, False),
                (self.primary_source_links_tree, False),
                (self.btn_add_primary_source_link, False),
                (self.btn_edit_primary_source_link, False),
                (self.btn_delete_primary_source_link, False),
                (self.btn_open_primary_source_link, False),
                (self.primary_source_attributions_tree, False),
                (self.btn_add_primary_source_attribution, False),
                (self.btn_edit_primary_source_attribution, False),
                (self.btn_delete_primary_source_attribution, False),
                (self.btn_open_primary_source_attribution_url, False),
                (self.primary_source_pages_tree, False),
                (self.btn_add_primary_source_page, False),
                (self.btn_edit_primary_source_page, False),
                (self.btn_delete_primary_source_page, False),
                (self.btn_download_primary_source_page, False),
                (self.btn_open_primary_source_page, False),
                (self.btn_open_primary_source_contours, False),
                (self.primary_source_words_tree, False),
                (self.btn_add_primary_source_word, False),
                (self.btn_edit_primary_source_word, False),
                (self.btn_delete_primary_source_word, False),
                (self.primary_source_verses_tree, False),
                (self.btn_add_primary_source_verse, False),
                (self.btn_edit_primary_source_verse, False),
                (self.btn_delete_primary_source_verse, False),
                (self.btn_edit_primary_source_verse_contours, False),
                (self.btn_import_primary_source_verse_snippet, False),
            ]
            for widget, readonly_when_enabled in source_widgets:
                self._set_ttk_widget_enabled(
                    widget,
                    sources_enabled,
                    readonly_when_enabled=readonly_when_enabled,
                )
            if self.primary_source_notes_text is not None:
                self.primary_source_notes_text.configure(state="normal" if sources_enabled else "disabled")
            if not sources_enabled:
                self._clear_primary_source_editor()

        def _update_ui_availability(self) -> None:
            has_loaded_db = self.connection is not None and self.current_db_path is not None
            has_common_db = self.common_connection is not None and self.common_db_path is not None
            self.db_combo.configure(state="readonly" if self.db_files else "disabled")
            self.btn_publish.state(["!disabled"])
            self._set_editor_controls_enabled(
                localized_enabled=has_loaded_db,
                resources_enabled=has_common_db,
                strong_enabled=has_common_db,
                sources_enabled=has_loaded_db and has_common_db,
            )

        def _show_centered_info(self, title: str, message: str) -> None:
            dialog = tk.Toplevel(self)
            dialog.title(title)
            dialog.transient(self)
            dialog.grab_set()
            dialog.resizable(False, False)

            self._center_toplevel(dialog, width=460, height=160)

            frame = ttk.Frame(dialog, padding=16)
            frame.pack(fill="both", expand=True)
            ttk.Label(frame, text=message, anchor="center", justify="center").pack(fill="both", expand=True)
            ok_button = ttk.Button(frame, text="OK", command=dialog.destroy)
            ok_button.pack(pady=(8, 0))
            ok_button.focus_set()

            dialog.bind("<Return>", lambda _e: dialog.destroy())
            dialog.bind("<Escape>", lambda _e: dialog.destroy())
            dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
            self.wait_window(dialog)

        def _center_toplevel(self, window: tk.Toplevel, width: int, height: int) -> None:
            window.update_idletasks()
            x = max((window.winfo_screenwidth() - width) // 2, 0)
            y = max((window.winfo_screenheight() - height) // 2, 0)
            window.geometry(f"{width}x{height}+{x}+{y}")

        def _fit_and_center_toplevel(
            self,
            window: tk.Toplevel,
            *,
            min_width: int,
            max_width: int,
            min_height: int,
            max_height: int,
            pad_x: int = 0,
            pad_y: int = 0,
        ) -> None:
            window.update_idletasks()
            width = window.winfo_reqwidth() + pad_x
            height = window.winfo_reqheight() + pad_y
            width = max(min_width, min(width, max_width))
            height = max(min_height, min(height, max_height))
            self._center_toplevel(window, width=width, height=height)

        def _allow_switch_when_dirty(self) -> bool:
            if not self.dirty:
                return True
            answer = messagebox.askyesnocancel(
                "Несохраненные изменения",
                "Есть несохраненные изменения. Сохранить перед переключением?",
                parent=self,
            )
            if answer is None:
                return False
            if answer:
                return self._save_all()
            return True

        def _set_dirty(self, value: bool) -> None:
            self.dirty = value
            title = self.BASE_TITLE
            if self.dirty:
                title = f"* {title}"
            self.title(title)
            self._update_file_info()

        def _set_status(self, text: str) -> None:
            ts = dt.datetime.now().strftime("%H:%M:%S")
            self.message_log.append((ts, text))
            self.status_var.set(text)

        def _open_message_log(self, _event: object | None = None) -> None:
            log_window = tk.Toplevel(self)
            log_window.title("Журнал сообщений")
            log_window.geometry("860x360")
            log_window.minsize(680, 280)

            container = ttk.Frame(log_window, padding=10)
            container.grid(row=0, column=0, sticky="nsew")
            log_window.columnconfigure(0, weight=1)
            log_window.rowconfigure(0, weight=1)
            container.columnconfigure(0, weight=1)
            container.rowconfigure(0, weight=1)

            text_widget = tk.Text(container, wrap="word")
            text_widget.grid(row=0, column=0, sticky="nsew")
            scroll = ttk.Scrollbar(container, orient="vertical", command=text_widget.yview)
            scroll.grid(row=0, column=1, sticky="ns")
            text_widget.configure(yscrollcommand=scroll.set)

            if self.message_log:
                lines = [f"[{ts}] {message}" for ts, message in self.message_log]
            else:
                lines = ["[--:--:--] Сообщений за текущую сессию пока нет."]
            text_widget.insert("1.0", "\n".join(lines))
            text_widget.configure(state="disabled")

        def _set_file_info(self, text: str) -> None:
            self.file_info_var.set(text)

        def _set_status_indicator(self, *, dirty_like: bool) -> None:
            _ = dirty_like
            return

        def _db_short_name(self, path: Path) -> str:
            stem = path.stem
            if stem == "revelation":
                return "rev"
            exact_lang = re.fullmatch(r"revelation_([A-Za-z0-9]{2})", stem)
            if exact_lang is not None:
                return f"_{exact_lang.group(1).lower()}"
            if stem.startswith("revelation_"):
                suffix = stem.split("_", maxsplit=1)[1].strip()
                if suffix:
                    return f"_{suffix.lower()}"
            return stem

        def _format_db_info(self, path: Path | None) -> str:
            if path is None or not path.exists():
                return "-"
            stat = path.stat()
            modified = dt.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size_kb = stat.st_size / 1024
            return f"{self._db_short_name(path)} {modified} 💾 {size_kb:.1f} KB"

        def _compose_db_info_line(self, paths: list[Path | None]) -> str:
            parts: list[str] = []
            seen: set[str] = set()
            for path in paths:
                if path is None:
                    continue
                resolved = str(path.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                if not path.exists():
                    continue
                parts.append(self._format_db_info(path))
            return " | ".join(parts) if parts else "-"

        def _update_file_info(self) -> None:
            self._update_section_db_labels()
            section = self._active_section_key()
            has_local = self.current_db_path is not None and self.current_db_path.exists()
            has_common = self.common_db_path is not None and self.common_db_path.exists()
            localized_entries = self._localized_db_entries()
            localized_paths = [db_path for _, db_path in localized_entries if db_path.exists()]

            if section == "articles":
                self._set_status_indicator(dirty_like=not has_local)
                self._set_file_info(
                    self._compose_db_info_line(
                        [
                            self.current_db_path,
                        ]
                    )
                )
                return

            if section == "resources":
                self._set_status_indicator(dirty_like=not has_common)
                self._set_file_info(
                    self._compose_db_info_line(
                        [
                            self.common_db_path,
                        ]
                    )
                )
                return

            if section == "strong":
                self._set_status_indicator(dirty_like=not (has_common and bool(localized_paths)))
                self._set_file_info(
                    self._compose_db_info_line(
                        [
                            self.common_db_path,
                            *localized_paths,
                        ]
                    )
                )
                return

            self._set_status_indicator(dirty_like=not (has_local and has_common))
            self._set_file_info(
                self._compose_db_info_line(
                    [
                        self.current_db_path,
                        self.common_db_path,
                    ]
                )
            )

