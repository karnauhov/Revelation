#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Content of Revelation: GUI tool for managing localized articles."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import mimetypes
import re
import sqlite3
import shutil
import tempfile
import urllib.parse
import webbrowser
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import TYPE_CHECKING, Any

try:
    from markdown import markdown as md_to_html
except ImportError:
    md_to_html = None

if TYPE_CHECKING:
    from tkinterweb import HtmlFrame as HtmlFrameType
else:
    HtmlFrameType = Any

try:
    from tkinterweb import HtmlFrame as HtmlFrameWidget
except ImportError:
    HtmlFrameWidget = None


@dataclass
class TopicRow:
    route: str
    name: str
    description: str
    id_icon: str
    sort_order: int
    is_visible: bool


@dataclass
class TopicTextRow:
    route: str
    markdown: str


@dataclass
class ResourceRow:
    key: str
    file_name: str
    mime_type: str
    size_bytes: int


def default_work_dir() -> Path:
    preferred = Path(r"C:\Users\karna\OneDrive\Documents\revelation\db")
    if preferred.exists():
        return preferred
    return Path.home() / "OneDrive" / "Documents" / "revelation" / "db"


class TopicContentTool(tk.Tk):
    BASE_TITLE = "Content of Revelation"
    NO_ARTICLE_OPTION = "(без статьи)"
    NO_ICON_OPTION = "(без иконки)"
    UNBOUND_TAG = "unbound_row"
    ALERT_COLOR = "#c1121f"
    OK_COLOR = "#1f7a3f"
    ICON_PNG_BASE64 = {
        "choose_folder": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAR0lEQVQ4y2NgGC7AneExw38kWE9Iw30U5URo+YuhARM+ZvAgTcN/hkeoGgiB/8hqaK/h30jU8J/mGh6RmjQ80JI3wcQ3tAEA40iFo4b69OwAAAAASUVORK5CYII=",
        "refresh": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAv0lEQVQ4y92TPQrCQBCFvybaxMpTmDQWwZ/Cs+UEUdyInV5ET6Gks7QULAJCdHEsDBLdXUzafNsN77Ezs2+hjYQsyMjJyZgTlNXYLvZYoZHK0Sg8YsQu3yMUKCb4+ExZc0c4IXaDQjgz/KqNyMu7DAI0xY8c4k9zBgmCcsothgPC2Cm3GK4IvSb7b2wwW/qDbeg3G4Sk7lohQqMZ1H24iAvC0pWkajT6zNjyQNjRcc1hhu9JSrdevG8cSQnb+INfa9dgs2rwKa8AAAAASUVORK5CYII=",
        "save": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAXklEQVQ4y2NgGLTAk+Exw38csB6bhkc4lePQAhLGBnBqIaQBQwthDf+poIEQHEoafjKUM0gAYTmQRZSGMrhoGXEaJOGikjTSQLKTiPL0I4KB+oj4DASCjxk8Bm3mBwATwvSdhoWVegAAAABJRU5ErkJggg==",
        "publish": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAPElEQVQ4y2NgGDKgHghJUv4fCOtJU060FoRyorSgKieoBVM5Xi3YlRPhMGSlRIERqYF24D8eSB0NQxUAAMVCcIlDCOtfAAAAAElFTkSuQmCC",
        "add": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAH0lEQVQ4y2NgGAVw8B8IRzXgUoQLUkfDaDyQqmFYAwDqLDPNE6CZygAAAABJRU5ErkJggg==",
        "delete": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAOElEQVQ4y2NgGAJAgeE+w38ovA/k4QH/8UDqaCADkGz+qIZRDTjAI6zKH+HW4MHwGEP5Y6Do4AYAnknHV/9dX/AAAAAASUVORK5CYII=",
        "apply": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAASUlEQVQ4jWNgGAU4gQZpygMZfjHUk6b8P/Eaho5yFoaVQAUkmB4OlPyFpIUIx9QjaSHS7TAtJHgVooWkkAFpIUE5RAtJykcEAABPQC0fT3oYggAAAABJRU5ErkJggg==",
        "cancel": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAVUlEQVQ4y+WSuREAIAgEtwm6sP+MKixIAwPfUS6WEHZn+ODzSDi2ZQ0nnQWnkBfFyBT8LLTiqOyZq/LEZyiEj0oQ70oYlwWxJXFoca3y4eTXkJ/vm6g9L0LBODY4BgAAAABJRU5ErkJggg==",
        "warning": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAvElEQVR4Ae3NIQyCUABFUedmsdiMVrN99NmDfaMH+kYP9I0e6Bt9o49sJdIoBAI8b2CiKMiHb9K7nfa2t/q5zsB32uDa2sB6HtTyYLU9CqhVYA9rhVBPCCudUEM9NU5YXAINSLCoCzSOzcy2yCAAXXqQYQvjfAjjB4APow4oDQ5KHDC5CDI4ECJMykEDGWrgYLQ1UmimFGsM5kKDujTCxdt2yC0c5NjhpQCyJMBTR1SQJRWOuBdDlsX497kb/qTEM/V7+dsAAAAASUVORK5CYII=",
        "status_clean": "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAaElEQVR4nGNgIBMwYhP8////FhRFjIw+6GpYsGlQqHbwxiaObAAjsiS6BnTwoPXAVphmJnwK8QEmYm1jYIB4AeZsymykv0ZGRkafB60HthJSTJVQRUk5uBIAzDVYEwA2A+CKsCQ5sgEAf94w7gNYzG8AAAAASUVORK5CYII=",
        "status_dirty": "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAaElEQVR4nGNgIBMwYhP8////FhRFjIw+6GpYsGk4JKzgjU0c2QBGZEl0DejA7u2DrTDNTPgU4gNMxNrGwADxAszZlNlIf42MjIw+dm8fbCWkmCqhipJycCUAmGuwJgBsBsAVYUlyZAMA9wwxCIraexcAAAAASUVORK5CYII=",
    }

    def __init__(self, start_dir: Path) -> None:
        super().__init__()
        self.title(self.BASE_TITLE)
        self.geometry("1500x920")
        self.minsize(1200, 760)

        self.project_root = Path(__file__).resolve().parent.parent
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

        self.topics: list[TopicRow] = []
        self.topic_texts: list[TopicTextRow] = []
        self.common_resources: list[ResourceRow] = []
        self.selected_topic_index: int | None = None
        self.selected_text_index: int | None = None
        self.selected_resource_index: int | None = None
        self.selected_resource_original_key: str | None = None
        self.resource_data_buffer = b""
        self.resource_preview_image: tk.PhotoImage | None = None

        self.folder_var = tk.StringVar(value=str(self.work_dir))
        self.db_var = tk.StringVar()
        self.file_info_var = tk.StringVar(value="Файл: -")
        self.status_var = tk.StringVar(value="Выберите локализованную БД для начала работы.")

        self.topic_route_var = tk.StringVar(value=self.NO_ARTICLE_OPTION)
        self.topic_name_var = tk.StringVar()
        self.topic_description_var = tk.StringVar()
        self.topic_icon_var = tk.StringVar(value=self.NO_ICON_OPTION)
        self.topic_sort_var = tk.StringVar(value="0")
        self.topic_visible_var = tk.BooleanVar(value=True)

        self.text_route_var = tk.StringVar()
        self.resource_key_var = tk.StringVar()
        self.resource_file_name_var = tk.StringVar()
        self.resource_mime_var = tk.StringVar()
        self.resource_size_var = tk.StringVar(value="-")
        self.preview_unavailable_reason = ""
        self.preview_html: HtmlFrameType | None = None
        self.preview_text: tk.Text | None = None
        self.ui_icons: dict[str, tk.PhotoImage] = {}
        self.status_indicator_image: tk.PhotoImage | None = None

        self._build_ui()
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
            **self._button_kwargs("choose_folder", "Выбрать папку"),
            command=self._choose_folder,
        )
        self.btn_choose_folder.grid(row=0, column=2, padx=(8, 0))
        self.btn_refresh = ttk.Button(
            header,
            **self._button_kwargs("refresh", "Обновить список"),
            command=self._refresh_db_list,
        )
        self.btn_refresh.grid(row=0, column=3, padx=(8, 0))

        ttk.Label(header, text="Локализованная БД:").grid(row=1, column=0, sticky="w", pady=(8, 0), padx=(0, 8))
        self.db_combo = ttk.Combobox(header, textvariable=self.db_var, state="readonly")
        self.db_combo.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        self.db_combo.bind("<<ComboboxSelected>>", self._on_db_combo_selected)
        self.btn_save = ttk.Button(
            header,
            **self._button_kwargs("save", "Сохранить изменения"),
            command=self._save_all,
        )
        self.btn_save.grid(row=1, column=2, padx=(8, 0), pady=(8, 0))
        self.btn_publish = ttk.Button(
            header,
            **self._button_kwargs("publish", "Переписать в web/db"),
            command=self._copy_to_web_db,
        )
        self.btn_publish.grid(row=1, column=3, padx=(8, 0), pady=(8, 0))

        self.sections = ttk.Notebook(self)
        self.sections.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 6))

        self.topics_tab = ttk.Frame(self.sections)
        self.texts_tab = ttk.Frame(self.sections)
        self.resources_tab = ttk.Frame(self.sections)
        self.sections.add(self.topics_tab, text="Статьи главного окна")
        self.sections.add(self.texts_tab, text="Все статьи")
        self.sections.add(self.resources_tab, text="Ресурсы")

        self._build_topics_tab(self.topics_tab)
        self._build_texts_tab(self.texts_tab)
        self._build_resources_tab(self.resources_tab)

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
        self.status_indicator_image = self.ui_icons.get("status_clean")
        self.dirty_indicator_label = tk.Label(
            file_info_wrap,
            image=self.status_indicator_image,
            text="",
            padx=6,
        )
        self.dirty_indicator_label.grid(row=0, column=1, sticky="e")
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
            widget.configure(state="normal" if enabled else "disabled")
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

    def _set_editor_controls_enabled(self, localized_enabled: bool, resources_enabled: bool) -> None:
        localized_widgets: list[tuple[tk.Widget, bool]] = [
            (self.btn_save, False),
            (self.btn_publish, False),
            (self.topics_tree, False),
            (self.btn_add_topic, False),
            (self.btn_delete_topic, False),
            (self.topic_route_combo, True),
            (self.entry_topic_name, False),
            (self.entry_topic_description, False),
            (self.topic_icon_combo, True),
            (self.entry_topic_sort, False),
            (self.check_topic_visible, False),
            (self.btn_apply_topic, False),
            (self.btn_cancel_topic, False),
            (self.btn_add_text, False),
            (self.btn_delete_text, False),
            (self.entry_text_route, False),
            (self.btn_apply_text, False),
            (self.btn_cancel_text, False),
            (self.md_tabs, False),
        ]
        for widget, readonly_when_enabled in localized_widgets:
            self._set_ttk_widget_enabled(
                widget,
                localized_enabled,
                readonly_when_enabled=readonly_when_enabled,
            )

        self.texts_list.configure(state="normal" if localized_enabled else "disabled")
        self.markdown_text.configure(state="normal" if localized_enabled else "disabled")
        if self.preview_text is not None:
            self.preview_text.configure(state="disabled")

        resource_widgets: list[tuple[tk.Widget, bool]] = [
            (self.resources_tree, False),
            (self.btn_add_resource, False),
            (self.btn_delete_resource, False),
            (self.btn_open_resource, False),
            (self.btn_export_resource, False),
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
        self.resource_preview_text.configure(state="disabled")
        if not resources_enabled:
            self.resource_preview_image_label.configure(
                image="",
                text="Загрузите локализованную и общую БД для работы с ресурсами.",
            )
        elif self.selected_resource_index is None and not self.resource_data_buffer:
            self.resource_preview_image_label.configure(
                image="",
                text="Предпросмотр ресурса недоступен.\nВыберите запись из списка.",
            )

    def _update_ui_availability(self) -> None:
        has_loaded_db = self.connection is not None and self.current_db_path is not None
        has_common_db = self.common_connection is not None and self.common_db_path is not None
        self.db_combo.configure(state="readonly" if self.db_files else "disabled")
        self._set_editor_controls_enabled(
            localized_enabled=has_loaded_db,
            resources_enabled=has_loaded_db and has_common_db,
        )

    def _build_topics_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        pane = ttk.Panedwindow(parent, orient="horizontal")
        pane.grid(row=0, column=0, sticky="nsew")

        left = ttk.Frame(pane, padding=8)
        right = ttk.Frame(pane, padding=8)
        pane.add(left, weight=2)
        pane.add(right, weight=3)

        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        self.topics_tree = ttk.Treeview(
            left,
            columns=("route", "name", "sort", "visible"),
            show="headings",
            selectmode="browse",
        )
        self.topics_tree.heading("route", text="Маршрут")
        self.topics_tree.heading("name", text="Заголовок статьи")
        self.topics_tree.heading("sort", text="Порядок")
        self.topics_tree.heading("visible", text="Показывать")
        self.topics_tree.column("route", width=200, anchor="w")
        self.topics_tree.column("name", width=260, anchor="w")
        self.topics_tree.column("sort", width=90, anchor="center")
        self.topics_tree.column("visible", width=110, anchor="center")
        self.topics_tree.grid(row=0, column=0, sticky="nsew")
        self.topics_tree.bind("<<TreeviewSelect>>", self._on_topic_selected)
        self.topics_tree.tag_configure(self.UNBOUND_TAG, foreground=self.ALERT_COLOR)

        topics_scroll = ttk.Scrollbar(left, orient="vertical", command=self.topics_tree.yview)
        topics_scroll.grid(row=0, column=1, sticky="ns")
        self.topics_tree.configure(yscrollcommand=topics_scroll.set)

        topics_buttons = ttk.Frame(left)
        topics_buttons.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.btn_add_topic = ttk.Button(
            topics_buttons,
            **self._button_kwargs("add", "Добавить статью"),
            command=self._add_topic,
        )
        self.btn_add_topic.pack(side="left")
        self.btn_delete_topic = ttk.Button(
            topics_buttons,
            **self._button_kwargs("delete", "Удалить статью"),
            command=self._delete_topic,
        )
        self.btn_delete_topic.pack(side="left", padx=(8, 0))

        right.columnconfigure(1, weight=1)

        self.topic_route_label = tk.Label(right, text="Маршрут:")
        self.topic_route_label.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 4))
        self.topic_route_label_default_fg = self.topic_route_label.cget("fg")
        self.topic_route_combo = ttk.Combobox(
            right,
            textvariable=self.topic_route_var,
            state="readonly",
        )
        self.topic_route_combo.grid(row=0, column=1, sticky="ew", pady=(0, 4))
        self.topic_route_combo.bind("<<ComboboxSelected>>", self._on_topic_route_changed)
        self.topic_route_default_fg = self.topic_route_combo.cget("foreground") or "black"

        ttk.Label(right, text="Заголовок статьи:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.entry_topic_name = ttk.Entry(right, textvariable=self.topic_name_var)
        self.entry_topic_name.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(right, text="Описание:").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        self.entry_topic_description = ttk.Entry(right, textvariable=self.topic_description_var)
        self.entry_topic_description.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(right, text="Иконка:").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        self.topic_icon_combo = ttk.Combobox(
            right,
            textvariable=self.topic_icon_var,
            state="readonly",
        )
        self.topic_icon_combo.grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(right, text="Порядок:").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=4)
        self.entry_topic_sort = ttk.Entry(right, textvariable=self.topic_sort_var)
        self.entry_topic_sort.grid(row=4, column=1, sticky="w", pady=4)

        self.check_topic_visible = ttk.Checkbutton(
            right,
            text="Показывать на главной",
            variable=self.topic_visible_var,
        )
        self.check_topic_visible.grid(
            row=5,
            column=1,
            sticky="w",
            pady=(4, 8),
        )

        topic_actions = ttk.Frame(right)
        topic_actions.grid(row=6, column=1, sticky="w")
        self.btn_apply_topic = ttk.Button(
            topic_actions,
            **self._button_kwargs("apply", "Применить к записи"),
            command=self._apply_topic_changes,
        )
        self.btn_apply_topic.pack(side="left")
        self.btn_cancel_topic = ttk.Button(
            topic_actions,
            **self._button_kwargs("cancel", "Отменить изменения"),
            command=self._reload_selected_topic,
        )
        self.btn_cancel_topic.pack(side="left", padx=(8, 0))

    def _build_texts_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        pane = ttk.Panedwindow(parent, orient="horizontal")
        pane.grid(row=0, column=0, sticky="nsew")

        left = ttk.Frame(pane, padding=8)
        right = ttk.Frame(pane, padding=8)
        pane.add(left, weight=2)
        pane.add(right, weight=4)

        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        self.texts_list = tk.Listbox(left, exportselection=False)
        self.texts_list.grid(row=0, column=0, sticky="nsew")
        self.texts_list.bind("<<ListboxSelect>>", self._on_text_selected)

        texts_scroll = ttk.Scrollbar(left, orient="vertical", command=self.texts_list.yview)
        texts_scroll.grid(row=0, column=1, sticky="ns")
        self.texts_list.configure(yscrollcommand=texts_scroll.set)

        text_buttons = ttk.Frame(left)
        text_buttons.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.btn_add_text = ttk.Button(
            text_buttons,
            **self._button_kwargs("add", "Добавить статью"),
            command=self._add_text,
        )
        self.btn_add_text.pack(side="left")
        self.btn_delete_text = ttk.Button(
            text_buttons,
            **self._button_kwargs("delete", "Удалить статью"),
            command=self._delete_text,
        )
        self.btn_delete_text.pack(side="left", padx=(8, 0))

        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        ttk.Label(right, text="Маршрут:").grid(row=0, column=0, sticky="w")
        self.entry_text_route = ttk.Entry(right, textvariable=self.text_route_var)
        self.entry_text_route.grid(row=1, column=0, sticky="ew", pady=(2, 8))

        self.md_tabs = ttk.Notebook(right)
        self.md_tabs.grid(row=2, column=0, sticky="nsew")
        self.md_tabs.bind("<<NotebookTabChanged>>", self._on_md_tab_changed)

        edit_tab = ttk.Frame(self.md_tabs)
        preview_tab = ttk.Frame(self.md_tabs)
        edit_tab.columnconfigure(0, weight=1)
        edit_tab.rowconfigure(0, weight=1)
        preview_tab.columnconfigure(0, weight=1)
        preview_tab.rowconfigure(0, weight=1)
        self.md_tabs.add(edit_tab, text="Редактирование")
        self.md_tabs.add(preview_tab, text="MD просмотр")

        self.markdown_text = tk.Text(edit_tab, wrap="word", undo=True)
        self.markdown_text.grid(row=0, column=0, sticky="nsew")
        md_scroll = ttk.Scrollbar(edit_tab, orient="vertical", command=self.markdown_text.yview)
        md_scroll.grid(row=0, column=1, sticky="ns")
        self.markdown_text.configure(yscrollcommand=md_scroll.set)
        self.markdown_text.bind("<<Modified>>", self._on_markdown_modified)

        if HtmlFrameWidget is not None and md_to_html is not None:
            self.preview_html = HtmlFrameWidget(
                preview_tab,
                horizontal_scrollbar="auto",
                messages_enabled=False,
            )
            self.preview_html.grid(row=0, column=0, sticky="nsew")
        else:
            missing = []
            if md_to_html is None:
                missing.append("markdown")
            if HtmlFrameWidget is None:
                missing.append("tkinterweb")
            self.preview_unavailable_reason = (
                "Полный MD-предпросмотр недоступен. Установите: pip install "
                + " ".join(missing)
            )
            self.preview_text = tk.Text(preview_tab, wrap="word", state="disabled")
            self.preview_text.grid(row=0, column=0, sticky="nsew")
            preview_scroll = ttk.Scrollbar(preview_tab, orient="vertical", command=self.preview_text.yview)
            preview_scroll.grid(row=0, column=1, sticky="ns")
            self.preview_text.configure(yscrollcommand=preview_scroll.set)

        text_actions = ttk.Frame(right)
        text_actions.grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.btn_apply_text = ttk.Button(
            text_actions,
            **self._button_kwargs("apply", "Применить к записи"),
            command=self._apply_text_changes,
        )
        self.btn_apply_text.pack(side="left")
        self.btn_cancel_text = ttk.Button(
            text_actions,
            **self._button_kwargs("cancel", "Отменить изменения"),
            command=self._reload_selected_text,
        )
        self.btn_cancel_text.pack(side="left", padx=(8, 0))

    def _build_resources_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        pane = ttk.Panedwindow(parent, orient="horizontal")
        pane.grid(row=0, column=0, sticky="nsew")

        left = ttk.Frame(pane, padding=8)
        right = ttk.Frame(pane, padding=8)
        pane.add(left, weight=2)
        pane.add(right, weight=3)

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
            **self._button_kwargs("refresh", "Открыть ресурс"),
            command=self._open_resource_external,
        )
        self.btn_open_resource.pack(side="left", padx=(8, 0))
        self.btn_export_resource = ttk.Button(
            resources_buttons,
            **self._button_kwargs("save", "Сохранить как"),
            command=self._export_resource_to_file,
        )
        self.btn_export_resource.pack(side="left", padx=(8, 0))

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
            **self._button_kwargs("choose_folder", "Заменить файл"),
            command=self._pick_file_for_resource_editor,
        )
        self.btn_pick_resource_file.pack(side="left")
        self.btn_apply_resource = ttk.Button(
            resource_actions,
            **self._button_kwargs("apply", "Применить к ресурсу"),
            command=self._apply_resource_changes,
        )
        self.btn_apply_resource.pack(side="left", padx=(8, 0))
        self.btn_cancel_resource = ttk.Button(
            resource_actions,
            **self._button_kwargs("cancel", "Отменить изменения"),
            command=self._reload_selected_resource,
        )
        self.btn_cancel_resource.pack(side="left", padx=(8, 0))

        preview_frame = ttk.LabelFrame(right, text="Просмотр ресурса")
        preview_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)

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
        self.resource_preview_image_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6, 4))

        self.resource_preview_text = tk.Text(preview_frame, height=6, wrap="word", state="disabled")
        self.resource_preview_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        resource_preview_scroll = ttk.Scrollbar(
            preview_frame,
            orient="vertical",
            command=self.resource_preview_text.yview,
        )
        resource_preview_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 6))
        self.resource_preview_text.configure(yscrollcommand=resource_preview_scroll.set)

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

        values = list(self.db_files.keys())
        self.db_combo["values"] = values
        if not values:
            self.db_var.set("")
            self._close_connection()
            self.current_db_path = None
            self._clear_all_db_views()
            self._set_file_info("Файл: локализованные БД не найдены.")
            self._set_status("В выбранной папке нет файлов вида revelation_<lang>.sqlite.")
            self._update_ui_availability()
            return

        previous = self.db_var.get()
        if previous in self.db_files:
            self.db_var.set(previous)
            if initial_select:
                self._load_db(self.db_files[previous])
            else:
                self._update_ui_availability()
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
        self._close_connection()
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.current_db_path = db_path
        self._open_common_connection()

        self._ensure_schema()
        self._load_rows()
        self._set_dirty(False)
        self._update_file_info()
        self._set_status(f"Открыта БД: {db_path.name}")
        self._update_ui_availability()

    def _open_common_connection(self) -> None:
        if self.common_connection is not None:
            self.common_connection.close()
            self.common_connection = None
            self.common_db_path = None

        for index, path in enumerate(self._common_db_candidates()):
            if index > 0 and not path.exists():
                continue
            con: sqlite3.Connection | None = None
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                con = sqlite3.connect(path)
                con.row_factory = sqlite3.Row
                self._ensure_common_schema_on_connection(con)
                self.common_connection = con
                self.common_db_path = path.resolve()
                return
            except (sqlite3.DatabaseError, OSError):
                if con is not None:
                    con.close()
                continue

    def _common_db_candidates(self) -> list[Path]:
        candidates = [
            self.work_dir / "revelation.sqlite",
            self.project_root / "web" / "db" / "revelation.sqlite",
        ]
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
            """
        )
        self.connection.commit()

    def _ensure_common_schema_on_connection(self, connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS common_resources (
              key TEXT NOT NULL PRIMARY KEY,
              file_name TEXT NOT NULL,
              mime_type TEXT NOT NULL,
              data BLOB NOT NULL
            );
            """
        )
        connection.commit()

    def _load_rows(self) -> None:
        assert self.connection is not None

        topic_rows = self.connection.execute(
            """
            SELECT route, name, description, id_icon, sort_order, is_visible
            FROM topics
            ORDER BY sort_order ASC, route ASC
            """
        ).fetchall()
        self.topics = [
            TopicRow(
                route=row["route"],
                name=row["name"],
                description=row["description"],
                id_icon=row["id_icon"],
                sort_order=int(row["sort_order"]),
                is_visible=bool(row["is_visible"]),
            )
            for row in topic_rows
        ]

        text_rows = self.connection.execute(
            """
            SELECT route, markdown
            FROM topic_texts
            ORDER BY route ASC
            """
        ).fetchall()
        self.topic_texts = [TopicTextRow(route=row["route"], markdown=row["markdown"]) for row in text_rows]

        self._load_common_resources()
        self._refresh_topics_tree()
        self._refresh_texts_list()
        self._refresh_topic_route_options()
        self._refresh_topic_icon_options()
        self._clear_topic_editor()
        self._clear_text_editor()
        self._clear_resource_editor()

    def _clear_all_db_views(self) -> None:
        self.topics.clear()
        self.topic_texts.clear()
        self.common_resources.clear()
        self._refresh_topics_tree()
        self._refresh_texts_list()
        self._refresh_resources_tree()
        self._clear_topic_editor()
        self._clear_text_editor()
        self._clear_resource_editor()
        self._refresh_topic_route_options()
        self._refresh_topic_icon_options()

    def _refresh_topics_tree(self) -> None:
        self.topics_tree.delete(*self.topics_tree.get_children())
        for idx, row in enumerate(self.topics):
            route_display = row.route if row.route else self.NO_ARTICLE_OPTION
            tags = (self.UNBOUND_TAG,) if not row.route else ()
            self.topics_tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(route_display, row.name, row.sort_order, "Да" if row.is_visible else "Нет"),
                tags=tags,
            )

    def _refresh_topic_route_options(self) -> None:
        article_routes = sorted({row.route for row in self.topic_texts if row.route.strip()})
        current = self.topic_route_var.get().strip()
        if current and current != self.NO_ARTICLE_OPTION and current not in article_routes:
            article_routes.append(current)
            article_routes.sort()
        self.topic_route_combo["values"] = [self.NO_ARTICLE_OPTION, *article_routes]

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

    def _on_topic_route_changed(self, _event: object | None = None) -> None:
        route = self._route_value_from_editor()
        self._update_topic_route_visual_state(route, selection_exists=self.selected_topic_index is not None)

    def _route_value_from_editor(self) -> str:
        value = self.topic_route_var.get().strip()
        if not value or value == self.NO_ARTICLE_OPTION:
            return ""
        return value

    def _display_route_value(self, route: str) -> str:
        return route if route else self.NO_ARTICLE_OPTION

    def _update_topic_route_visual_state(self, route: str, *, selection_exists: bool) -> None:
        is_unbound = selection_exists and not route
        color = self.ALERT_COLOR if is_unbound else self.topic_route_default_fg
        self.topic_route_combo.configure(foreground=color)
        self.topic_route_label.configure(
            fg=self.ALERT_COLOR if is_unbound else self.topic_route_label_default_fg
        )

    def _refresh_texts_list(self) -> None:
        self.texts_list.delete(0, tk.END)
        for row in self.topic_texts:
            self.texts_list.insert(tk.END, row.route)

    def _on_topic_selected(self, _event: object) -> None:
        selection = self.topics_tree.selection()
        if not selection:
            self.selected_topic_index = None
            self._update_topic_route_visual_state("", selection_exists=False)
            return
        self.selected_topic_index = int(selection[0])
        self._reload_selected_topic()

    def _reload_selected_topic(self) -> None:
        if self.selected_topic_index is None:
            self._clear_topic_editor()
            return
        row = self.topics[self.selected_topic_index]
        self.topic_route_var.set(self._display_route_value(row.route))
        self.topic_name_var.set(row.name)
        self.topic_description_var.set(row.description)
        self.topic_icon_var.set(self._display_icon_value(row.id_icon))
        self._refresh_topic_icon_options()
        self.topic_sort_var.set(str(row.sort_order))
        self.topic_visible_var.set(row.is_visible)
        self._update_topic_route_visual_state(row.route, selection_exists=True)

    def _clear_topic_editor(self) -> None:
        self.selected_topic_index = None
        self.topic_route_var.set(self.NO_ARTICLE_OPTION)
        self.topic_name_var.set("")
        self.topic_description_var.set("")
        self.topic_icon_var.set(self.NO_ICON_OPTION)
        self._refresh_topic_icon_options()
        self.topic_sort_var.set("0")
        self.topic_visible_var.set(True)
        self._update_topic_route_visual_state("", selection_exists=False)

    def _add_topic(self) -> None:
        route = simpledialog.askstring(
            "Новая статья",
            "Введите маршрут для новой статьи главного окна.\n"
            "Оставьте пустым для варианта (без статьи):",
            parent=self,
        )
        if route is None:
            return
        route = route.strip()
        if any(t.route == route for t in self.topics):
            duplicate_route = self._display_route_value(route)
            messagebox.showwarning(
                "Дубликат",
                f"Статья с маршрутом '{duplicate_route}' уже существует в списке главного окна.",
                parent=self,
            )
            return

        next_sort = max((t.sort_order for t in self.topics), default=-1) + 1
        self.topics.append(
            TopicRow(
                route=route,
                name=route or "Новая статья",
                description="",
                id_icon="",
                sort_order=next_sort,
                is_visible=True,
            )
        )
        self._sort_topics()
        self._refresh_topics_tree()
        self._refresh_topic_route_options()
        self._select_topic_by_route(route)
        self._set_dirty(True)
        self._set_status(
            f"Добавлена статья с маршрутом '{self._display_route_value(route)}' в список главного окна."
        )

    def _delete_topic(self) -> None:
        if self.selected_topic_index is None:
            return
        row = self.topics[self.selected_topic_index]
        if not messagebox.askyesno(
            "Удаление статьи",
            (
                f"Удалить статью с маршрутом '{self._display_route_value(row.route)}' "
                "только из списка главного окна?\n\n"
                "Содержимое статьи не изменяется."
            ),
            parent=self,
        ):
            return
        del self.topics[self.selected_topic_index]
        self._refresh_topics_tree()
        self._clear_topic_editor()
        self._set_dirty(True)
        self._set_status(
            f"Статья с маршрутом '{self._display_route_value(row.route)}' удалена из списка главного окна."
        )

    def _apply_topic_changes(self) -> None:
        if self.selected_topic_index is None:
            messagebox.showinfo("Нет выбора", "Сначала выберите запись в статьях главного окна.", parent=self)
            return
        row = self.topics[self.selected_topic_index]

        route = self._route_value_from_editor()
        name = self.topic_name_var.get().strip()
        description = self.topic_description_var.get().strip()
        icon = self._icon_value_from_editor()
        sort_raw = self.topic_sort_var.get().strip()

        if any(i != self.selected_topic_index and t.route == route for i, t in enumerate(self.topics)):
            messagebox.showwarning(
                "Дубликат",
                (
                    f"Маршрут '{self._display_route_value(route)}' уже существует "
                    "в статьях главного окна."
                ),
                parent=self,
            )
            return
        if not name:
            messagebox.showwarning("Ошибка", "Заголовок (name) не может быть пустым.", parent=self)
            return
        try:
            sort_order = int(sort_raw)
        except ValueError:
            messagebox.showwarning("Ошибка", "sort_order должен быть целым числом.", parent=self)
            return

        row.route = route
        row.name = name
        row.description = description
        row.id_icon = icon
        row.sort_order = sort_order
        row.is_visible = bool(self.topic_visible_var.get())

        self._sort_topics()
        self._refresh_topics_tree()
        self._refresh_topic_route_options()
        self._select_topic_by_route(route)
        self._update_topic_route_visual_state(route, selection_exists=True)
        self._set_dirty(True)
        self._set_status(
            (
                "Изменения для статьи с маршрутом "
                f"'{self._display_route_value(route)}' применены в списке главного окна."
            )
        )

    def _sort_topics(self) -> None:
        self.topics.sort(key=lambda item: (item.sort_order, item.route))

    def _select_topic_by_route(self, route: str) -> None:
        for idx, row in enumerate(self.topics):
            if row.route == route:
                self.topics_tree.selection_set(str(idx))
                self.topics_tree.focus(str(idx))
                self.topics_tree.see(str(idx))
                self.selected_topic_index = idx
                self._reload_selected_topic()
                return

    def _on_text_selected(self, _event: object) -> None:
        selection = self.texts_list.curselection()
        if not selection:
            self.selected_text_index = None
            return
        self.selected_text_index = int(selection[0])
        self._reload_selected_text()

    def _reload_selected_text(self) -> None:
        if self.selected_text_index is None:
            self._clear_text_editor()
            return
        row = self.topic_texts[self.selected_text_index]
        self.text_route_var.set(row.route)
        self.markdown_change_internal = True
        self.markdown_text.delete("1.0", tk.END)
        self.markdown_text.insert("1.0", row.markdown)
        self.markdown_text.edit_modified(False)
        self.markdown_change_internal = False
        self._refresh_preview()

    def _clear_text_editor(self) -> None:
        self.selected_text_index = None
        self.text_route_var.set("")
        self.markdown_change_internal = True
        self.markdown_text.delete("1.0", tk.END)
        self.markdown_text.edit_modified(False)
        self.markdown_change_internal = False
        self._render_preview_content("")

    def _add_text(self) -> None:
        route = simpledialog.askstring("Новая статья", "Введите маршрут для новой статьи:", parent=self)
        if route is None:
            return
        route = route.strip()
        if not route:
            messagebox.showwarning("Пустой маршрут", "Маршрут не может быть пустым.", parent=self)
            return
        if any(t.route == route for t in self.topic_texts):
            messagebox.showwarning(
                "Дубликат",
                f"Статья с маршрутом '{route}' уже существует в общем списке статей.",
                parent=self,
            )
            return

        self.topic_texts.append(TopicTextRow(route=route, markdown=""))
        self._sort_topic_texts()
        self._refresh_texts_list()
        self._refresh_topic_route_options()
        self._select_text_by_route(route)
        self._set_dirty(True)
        self._set_status(f"Добавлена статья с маршрутом '{route}' в общий список статей.")

    def _delete_text(self) -> None:
        if self.selected_text_index is None:
            return
        row = self.topic_texts[self.selected_text_index]
        if not messagebox.askyesno(
            "Удаление статьи",
            f"Удалить статью с маршрутом '{row.route}' только из общего списка статей?\n\nСписок главного окна не изменяется.",
            parent=self,
        ):
            return
        del self.topic_texts[self.selected_text_index]
        self._refresh_texts_list()
        self._refresh_topic_route_options()
        self._clear_text_editor()
        self._set_dirty(True)
        self._set_status(f"Статья с маршрутом '{row.route}' удалена из общего списка статей.")

    def _apply_text_changes(self) -> None:
        if self.selected_text_index is None:
            messagebox.showinfo("Нет выбора", "Сначала выберите запись из всех статей.", parent=self)
            return

        row = self.topic_texts[self.selected_text_index]
        route = self.text_route_var.get().strip()
        markdown = self.markdown_text.get("1.0", "end-1c")

        if not route:
            messagebox.showwarning("Ошибка", "Маршрут не может быть пустым.", parent=self)
            return
        if any(i != self.selected_text_index and t.route == route for i, t in enumerate(self.topic_texts)):
            messagebox.showwarning(
                "Дубликат",
                f"Маршрут '{route}' уже существует в общем списке статей.",
                parent=self,
            )
            return

        row.route = route
        row.markdown = markdown
        self._sort_topic_texts()
        self._refresh_texts_list()
        self._refresh_topic_route_options()
        self._select_text_by_route(route)
        self._refresh_preview()
        self._set_dirty(True)
        self._set_status(f"Изменения для статьи с маршрутом '{route}' применены.")

    def _sort_topic_texts(self) -> None:
        self.topic_texts.sort(key=lambda item: item.route)

    def _select_text_by_route(self, route: str) -> None:
        for idx, row in enumerate(self.topic_texts):
            if row.route == route:
                self.texts_list.selection_clear(0, tk.END)
                self.texts_list.selection_set(idx)
                self.texts_list.see(idx)
                self.selected_text_index = idx
                self._reload_selected_text()
                return

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
        self._set_resource_preview_text("")

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
        self._set_status("Новый ресурс подготовлен. Проверьте поля и нажмите 'Применить к ресурсу'.")

    def _pick_file_for_resource_editor(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self,
            title="Выберите файл ресурса",
            initialdir=str(self.work_dir),
        )
        if not selected:
            return
        if self._load_resource_file_into_editor(Path(selected), suggest_new_key=False):
            self._set_status("Файл ресурса обновлен. Нажмите 'Применить к ресурсу' для сохранения.")

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
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить ресурс:\n{exc}", parent=self)
            return

        if old_key and old_key != key:
            for topic in self.topics:
                if topic.id_icon == old_key:
                    topic.id_icon = key
                    affected_topics += 1
            if affected_topics > 0:
                self._set_dirty(True)
                if self.selected_topic_index is not None:
                    self._reload_selected_topic()

        self._load_common_resources()
        self._select_resource_by_key(key)
        self._set_status(
            (
                f"Ресурс '{key}' сохранен в {self.common_db_path.name}."
                if affected_topics == 0
                else (
                    f"Ресурс '{key}' сохранен. Обновлено иконок статей главного окна: {affected_topics}."
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
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка удаления", f"Не удалось удалить ресурс:\n{exc}", parent=self)
            return

        affected_topics = 0
        for topic in self.topics:
            if topic.id_icon == row.key:
                topic.id_icon = ""
                affected_topics += 1
        if affected_topics > 0:
            self._set_dirty(True)
            if self.selected_topic_index is not None:
                self._reload_selected_topic()

        self._load_common_resources()
        self._clear_resource_editor()
        suffix = (
            ""
            if affected_topics == 0
            else f" Иконки сброшены у {affected_topics} статьи(ей) главного окна."
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

    def _render_resource_preview(self, data: bytes, mime: str, file_name: str, key: str) -> None:
        self.resource_preview_image = None
        self.resource_preview_image_label.configure(image="")

        info_lines = [
            f"Ключ: {key}",
            f"Имя файла: {file_name}",
            f"MIME: {mime or self._guess_mime_type(file_name)}",
            f"Размер: {self._format_size(len(data))}",
        ]

        if self._is_graphic_resource(mime, file_name) and data:
            try:
                encoded = base64.b64encode(data).decode("ascii")
                self.resource_preview_image = tk.PhotoImage(data=encoded)
                self.resource_preview_image_label.configure(image=self.resource_preview_image, text="")
                info_lines.append("Предпросмотр: изображение показано выше.")
            except tk.TclError:
                self.resource_preview_image_label.configure(
                    text=(
                        "Встроенный предпросмотр этого изображения недоступен в Tk.\n"
                        "Используйте кнопку 'Открыть ресурс'."
                    )
                )
                info_lines.append("Предпросмотр: формат изображения не поддерживается встроенно.")
        else:
            self.resource_preview_image_label.configure(
                text=(
                    "Для этого типа файла используйте кнопки\n"
                    "'Открыть ресурс' или 'Сохранить как'."
                )
            )
            info_lines.append("Предпросмотр: встроенно отображаются только поддерживаемые изображения.")

        self._set_resource_preview_text("\n".join(info_lines))

    def _set_resource_preview_text(self, text: str) -> None:
        self.resource_preview_text.configure(state="normal")
        self.resource_preview_text.delete("1.0", tk.END)
        if text:
            self.resource_preview_text.insert("1.0", text)
        self.resource_preview_text.configure(state="disabled")

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

    def _on_md_tab_changed(self, _event: object) -> None:
        selected_index = self.md_tabs.index(self.md_tabs.select())
        if selected_index == 1:
            self._refresh_preview()

    def _on_markdown_modified(self, _event: object) -> None:
        if not self.markdown_text.edit_modified():
            return
        self.markdown_text.edit_modified(False)
        if self.markdown_change_internal:
            return
        self._schedule_preview_refresh()

    def _schedule_preview_refresh(self) -> None:
        if self.preview_after_id is not None:
            self.after_cancel(self.preview_after_id)
        self.preview_after_id = self.after(180, self._refresh_preview)

    def _refresh_preview(self) -> None:
        self.preview_after_id = None
        markdown = self.markdown_text.get("1.0", "end-1c")
        self._render_preview_content(markdown)

    def _render_preview_content(self, markdown: str) -> None:
        if self.preview_html is not None and md_to_html is not None:
            body = md_to_html(
                markdown,
                extensions=["extra", "tables", "fenced_code", "sane_lists", "nl2br"],
                output_format="html5",
            )
            body = self._transform_custom_image_sources(body)
            html_doc = f"""
            <html>
            <head>
              <meta charset="utf-8" />
              <style>
                body {{ font-family: Segoe UI, Arial, sans-serif; margin: 14px; line-height: 1.5; }}
                pre {{ background: #f3f3f3; padding: 8px; border-radius: 4px; overflow-x: auto; }}
                code {{ background: #f3f3f3; padding: 1px 3px; border-radius: 3px; }}
                blockquote {{ border-left: 4px solid #c8c8c8; margin-left: 0; padding-left: 10px; color: #444; }}
                table, th, td {{ border: 1px solid #b9b9b9; border-collapse: collapse; padding: 6px; }}
                img {{ max-width: 100%; height: auto; }}
              </style>
            </head>
            <body>{body}</body>
            </html>
            """
            self.preview_html.load_html(html_doc)
            return

        if self.preview_text is None:
            return
        text = markdown
        if self.preview_unavailable_reason:
            text = f"{self.preview_unavailable_reason}\n\n{text}"
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", text)
        self.preview_text.configure(state="disabled")

    def _transform_custom_image_sources(self, html_content: str) -> str:
        pattern = re.compile(r"""(<img\b[^>]*\bsrc=)(["'])(.+?)\2""", flags=re.IGNORECASE)

        def replace(match: re.Match[str]) -> str:
            prefix, quote, source = match.groups()
            source = source.strip()
            low = source.lower()
            if low.startswith("dbres:") or low.startswith("resource:"):
                source = self._resolve_custom_image_uri(source)
            return f"{prefix}{quote}{source}{quote}"

        return pattern.sub(replace, html_content)

    def _resolve_custom_image_uri(self, source: str) -> str:
        lower_source = source.lower()
        if lower_source.startswith("dbres:"):
            key = source[len("dbres:"):].strip()
            payload = self._load_common_resource(key)
            if payload is None:
                return self._placeholder_image_data_uri(f"dbres:{key}")
            data, mime = payload
            return self._to_data_uri(data, mime)

        if lower_source.startswith("resource:"):
            raw_path = source[len("resource:"):].strip()
            payload = self._load_project_asset(raw_path)
            if payload is None:
                return self._placeholder_image_data_uri(f"resource:{raw_path}")
            data, mime = payload
            return self._to_data_uri(data, mime)

        return source

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

    def _save_all(self) -> bool:
        if self.connection is None or self.current_db_path is None:
            messagebox.showwarning("Нет БД", "Сначала откройте локализованную БД.", parent=self)
            return False

        try:
            with self.connection:
                self.connection.execute("DELETE FROM topics")
                self.connection.executemany(
                    """
                    INSERT INTO topics(route, name, description, id_icon, sort_order, is_visible)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            row.route,
                            row.name,
                            row.description,
                            row.id_icon,
                            row.sort_order,
                            1 if row.is_visible else 0,
                        )
                        for row in self.topics
                    ],
                )

                self.connection.execute("DELETE FROM topic_texts")
                self.connection.executemany(
                    """
                    INSERT INTO topic_texts(route, markdown)
                    VALUES(?, ?)
                    """,
                    [(row.route, row.markdown) for row in self.topic_texts],
                )
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить изменения:\n{exc}", parent=self)
            return False

        self._set_dirty(False)
        self._update_file_info()
        self._set_status(f"Сохранено: {self.current_db_path.name}")
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

        enabled_tests = self._find_enabled_test_articles(source_dir)
        if enabled_tests and not self._confirm_copy_with_enabled_tests(enabled_tests):
            self._set_status("Копирование в web/db отменено из-за включенных тестовых статей.")
            return

        files = sorted(source_dir.glob("revelation*.sqlite"))
        if not files:
            messagebox.showwarning("Нет БД", "В рабочей папке не найдены файлы revelation*.sqlite.", parent=self)
            return

        if not messagebox.askyesno(
            "Подтверждение",
            f"Переписать {len(files)} файл(ов) из:\n{source_dir}\n\nв:\n{target_dir}\n\nЭто только копирование файлов в web/db.",
            parent=self,
        ):
            return

        target_dir.mkdir(parents=True, exist_ok=True)
        for src in files:
            shutil.copy2(src, target_dir / src.name)

        self._set_status(f"Файлы переписаны в {target_dir}")
        self._show_centered_info("Готово", f"Скопировано файлов: {len(files)}")

    def _find_enabled_test_articles(self, source_dir: Path) -> list[str]:
        found: list[str] = []
        db_files = sorted(source_dir.glob("revelation_*.sqlite"))
        for db_file in db_files:
            try:
                with sqlite3.connect(db_file) as con:
                    rows = con.execute(
                        """
                        SELECT route
                        FROM topics
                        WHERE is_visible = 1
                        AND lower(route) LIKE '%test%'
                        ORDER BY route ASC
                        """
                    ).fetchall()
            except sqlite3.DatabaseError:
                continue
            for row in rows:
                found.append(f"{db_file.name}: {row[0]}")
        return sorted(found)

    def _confirm_copy_with_enabled_tests(self, routes: list[str]) -> bool:
        dialog = tk.Toplevel(self)
        dialog.title("Предупреждение")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=14)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)

        routes_text = "\n".join(f"- {route}" for route in routes)
        warning_text = (
            "Обнаружены включенные тестовые статьи.\n"
            "Они будут опубликованы после копирования в web/db.\n\n"
            f"{routes_text}\n\n"
            "Продолжить копирование?"
        )
        ttk.Label(
            frame,
            text=warning_text,
            justify="left",
            anchor="w",
            wraplength=560,
        ).grid(row=0, column=0, sticky="w")

        result = {"confirmed": False}

        def on_continue() -> None:
            result["confirmed"] = True
            dialog.destroy()

        def on_cancel() -> None:
            dialog.destroy()

        buttons_row = ttk.Frame(frame)
        buttons_row.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        buttons_row.columnconfigure(0, weight=1)
        centered_buttons = ttk.Frame(buttons_row)
        centered_buttons.grid(row=0, column=0)

        continue_btn = ttk.Button(
            centered_buttons,
            **self._button_kwargs("warning", "Все равно копировать"),
            command=on_continue,
        )
        continue_btn.pack(side="left")
        cancel_btn = ttk.Button(
            centered_buttons,
            **self._button_kwargs("cancel", "Отмена"),
            command=on_cancel,
        )
        cancel_btn.pack(side="left", padx=(10, 0))

        self._fit_and_center_toplevel(
            dialog,
            min_width=500,
            max_width=680,
            min_height=200,
            max_height=340,
            pad_x=16,
            pad_y=16,
        )

        # Default action is cancel.
        cancel_btn.focus_set()
        dialog.bind("<Escape>", lambda _e: on_cancel())
        dialog.bind("<Return>", lambda _e: on_cancel())
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        self.wait_window(dialog)
        return bool(result["confirmed"])

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
        if self.current_db_path is not None:
            title = f"{title} | {self.current_db_path.name}"
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

    def _update_file_info(self) -> None:
        icon_key = "status_dirty" if self.dirty else "status_clean"
        self.status_indicator_image = self.ui_icons.get(icon_key)
        if self.status_indicator_image is not None:
            self.dirty_indicator_label.configure(image=self.status_indicator_image, text="")
        else:
            indicator_color = self.ALERT_COLOR if self.dirty else self.OK_COLOR
            self.dirty_indicator_label.configure(image="", text="●", fg=indicator_color)
        if self.current_db_path is None or not self.current_db_path.exists():
            suffix = "есть" if self.dirty else "нет"
            self._set_file_info(f"Файл: - | Несохраненные изменения: {suffix}")
            return
        stat = self.current_db_path.stat()
        modified = dt.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size_kb = stat.st_size / 1024
        dirty_text = "есть" if self.dirty else "нет"
        self._set_file_info(
            (
                f"Файл: {self.current_db_path} | Изменен: {modified} | Размер: {size_kb:.1f} KB | "
                f"Несохраненные изменения: {dirty_text}"
            )
        )

    def _on_close(self) -> None:
        if not self._allow_switch_when_dirty():
            return
        self._close_connection()
        self.destroy()

    def _close_connection(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        if self.common_connection is not None:
            self.common_connection.close()
            self.common_connection = None
            self.common_db_path = None
        self._update_ui_availability()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Content of Revelation.")
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=default_work_dir(),
        help="Path to folder with SQLite DB files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = TopicContentTool(args.work_dir)
    app.mainloop()


if __name__ == "__main__":
    main()
