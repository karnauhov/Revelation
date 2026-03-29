from __future__ import annotations

import re
import sqlite3
import urllib.parse
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Any

from ..compat import (
    HtmlFrameWidget,
    HtmlNotebookWidget,
    md_to_html,
)
from ..models import ArticleRow, MarkdownTemplateSpec
from ..widgets import MarkdownTemplateToolbar, revelation_markdown_template_sections


class ArticlesMixin:
        def _build_articles_tab(self, parent: ttk.Frame) -> None:
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

            self.articles_tree = ttk.Treeview(
                left,
                columns=("route", "name", "sort", "visible"),
                show="headings",
                selectmode="browse",
            )
            self.articles_tree.heading("route", text="Маршрут")
            self.articles_tree.heading("name", text="Заголовок статьи")
            self.articles_tree.heading("sort", text="Порядок")
            self.articles_tree.heading("visible", text="На главной")
            self.articles_tree.column("route", width=200, anchor="w")
            self.articles_tree.column("name", width=260, anchor="w")
            self.articles_tree.column("sort", width=90, anchor="center")
            self.articles_tree.column("visible", width=110, anchor="center")
            self.articles_tree.grid(row=0, column=0, sticky="nsew")
            self.articles_tree.bind("<<TreeviewSelect>>", self._on_article_selected)
            self.articles_tree.tag_configure(self.UNBOUND_TAG, foreground=self.ALERT_COLOR)

            topics_scroll = ttk.Scrollbar(left, orient="vertical", command=self.articles_tree.yview)
            topics_scroll.grid(row=0, column=1, sticky="ns")
            self.articles_tree.configure(yscrollcommand=topics_scroll.set)

            topics_buttons = ttk.Frame(left)
            topics_buttons.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            self.btn_add_article = ttk.Button(
                topics_buttons,
                **self._button_kwargs("add", "Добавить статью"),
                command=self._add_article,
            )
            self.btn_add_article.pack(side="left")
            self.btn_delete_article = ttk.Button(
                topics_buttons,
                **self._button_kwargs("delete", "Удалить статью"),
                command=self._delete_article,
            )
            self.btn_delete_article.pack(side="left", padx=(8, 0))
            self.btn_vacuum_localized_db = ttk.Button(
                topics_buttons,
                **self._button_kwargs("refresh", "Сжать локализованную БД (VACUUM)"),
                command=self._vacuum_current_localized_db,
            )
            self.btn_vacuum_localized_db.pack(side="left", padx=(8, 0))

            right.columnconfigure(1, weight=1)
            right.rowconfigure(8, weight=1)

            self.article_route_label = tk.Label(right, text="Маршрут:")
            self.article_route_label.grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 4))
            self.article_route_label_default_fg = self.article_route_label.cget("fg")
            self.article_route_entry = tk.Entry(
                right,
                textvariable=self.topic_route_var,
            )
            self.article_route_entry.grid(row=0, column=1, sticky="ew", pady=(0, 4))
            self.article_route_entry.bind("<KeyRelease>", self._on_article_route_changed)
            self.article_route_default_fg = self.article_route_entry.cget("foreground") or "black"

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
                **self._button_kwargs("save", "Сохранить"),
                command=self._apply_article_changes,
            )
            self.btn_apply_topic.pack(side="left")
            self.btn_cancel_topic = ttk.Button(
                topic_actions,
                **self._button_kwargs("cancel", "Отменить"),
                command=self._reload_selected_article,
            )
            self.btn_cancel_topic.pack(side="left", padx=(8, 0))

            if HtmlNotebookWidget is not None:
                self.md_tabs = HtmlNotebookWidget(right)
            else:
                self.md_tabs = ttk.Notebook(right)
            self.md_tabs.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
            self.md_tabs.bind("<<NotebookTabChanged>>", self._on_md_tab_changed)

            edit_tab = ttk.Frame(self.md_tabs)
            preview_tab = ttk.Frame(self.md_tabs)
            edit_tab.columnconfigure(0, weight=1)
            edit_tab.rowconfigure(1, weight=1)
            preview_tab.columnconfigure(0, weight=1)
            preview_tab.rowconfigure(0, weight=1)
            self.md_tabs.add(edit_tab, text="Редактирование")
            self.md_tabs.add(preview_tab, text="MD просмотр")

            self.md_template_toolbar = MarkdownTemplateToolbar(
                edit_tab,
                sections=revelation_markdown_template_sections(),
                icon_resolver=lambda icon_name: self.ui_icons.get(icon_name),
                on_insert=self._insert_markdown_template,
            )
            self.md_template_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

            self.markdown_text = tk.Text(edit_tab, wrap="word", undo=True)
            self.markdown_text.grid(row=1, column=0, sticky="nsew")
            md_scroll = ttk.Scrollbar(edit_tab, orient="vertical", command=self.markdown_text.yview)
            md_scroll.grid(row=1, column=1, sticky="ns")
            self.markdown_text.configure(yscrollcommand=md_scroll.set)
            self.markdown_text.bind("<<Modified>>", self._on_markdown_modified)

            if HtmlFrameWidget is not None and HtmlNotebookWidget is not None and md_to_html is not None:
                self.preview_html = HtmlFrameWidget(
                    preview_tab,
                    horizontal_scrollbar="auto",
                    messages_enabled=False,
                )
                self.preview_html.grid(row=0, column=0, sticky="nsew")
            else:
                missing_packages = []
                if md_to_html is None:
                    missing_packages.append("markdown")
                if HtmlFrameWidget is None:
                    missing_packages.append("tkinterweb")

                if missing_packages:
                    self.preview_unavailable_reason = (
                        "Полный MD-предпросмотр недоступен. Установите: pip install "
                        + " ".join(missing_packages)
                    )
                    if HtmlNotebookWidget is None:
                        self.preview_unavailable_reason += (
                            "\nТакже требуется версия tkinterweb с поддержкой класса Notebook."
                        )
                else:
                    self.preview_unavailable_reason = "Полный MD-предпросмотр недоступен."
                self.preview_text = tk.Text(preview_tab, wrap="word", state="disabled")
                self.preview_text.grid(row=0, column=0, sticky="nsew")
                preview_scroll = ttk.Scrollbar(preview_tab, orient="vertical", command=self.preview_text.yview)
                preview_scroll.grid(row=0, column=1, sticky="ns")
                self.preview_text.configure(yscrollcommand=preview_scroll.set)


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


        def _on_article_route_changed(self, _event: object | None = None) -> None:
            route = self._route_value_from_editor()
            self._update_article_route_visual_state(route, selection_exists=self.selected_article_index is not None)

        def _route_value_from_editor(self) -> str:
            value = self.topic_route_var.get().strip()
            if not value or value == self.NO_ARTICLE_OPTION:
                return ""
            return value

        def _display_route_value(self, route: str) -> str:
            return route if route else self.NO_ARTICLE_OPTION

        def _update_article_route_visual_state(self, route: str, *, selection_exists: bool) -> None:
            is_unbound = selection_exists and not route
            color = self.ALERT_COLOR if is_unbound else self.article_route_default_fg
            self.article_route_entry.configure(foreground=color)
            self.article_route_label.configure(
                fg=self.ALERT_COLOR if is_unbound else self.article_route_label_default_fg
            )

        def _on_article_selected(self, _event: object) -> None:
            selection = self.articles_tree.selection()
            if not selection:
                self.selected_article_index = None
                self._update_article_route_visual_state("", selection_exists=False)
                return
            self.selected_article_index = int(selection[0])
            self._reload_selected_article()

        def _reload_selected_article(self) -> None:
            if self.selected_article_index is None:
                self._clear_article_editor()
                return
            row = self.articles[self.selected_article_index]
            self.topic_route_var.set(self._display_route_value(row.route))
            self.topic_name_var.set(row.name)
            self.topic_description_var.set(row.description)
            self.topic_icon_var.set(self._display_icon_value(row.id_icon))
            self._refresh_topic_icon_options()
            self.topic_sort_var.set(str(row.sort_order))
            self.topic_visible_var.set(row.is_visible)
            self.markdown_change_internal = True
            self.markdown_text.delete("1.0", tk.END)
            self.markdown_text.insert("1.0", row.markdown)
            self.markdown_text.edit_modified(False)
            self.markdown_change_internal = False
            self._refresh_preview()
            self._update_article_route_visual_state(row.route, selection_exists=True)

        def _clear_article_editor(self) -> None:
            self.selected_article_index = None
            self.topic_route_var.set("")
            self.topic_name_var.set("")
            self.topic_description_var.set("")
            self.topic_icon_var.set(self.NO_ICON_OPTION)
            self._refresh_topic_icon_options()
            self.topic_sort_var.set("0")
            self.topic_visible_var.set(True)
            self.markdown_change_internal = True
            self.markdown_text.delete("1.0", tk.END)
            self.markdown_text.edit_modified(False)
            self.markdown_change_internal = False
            self._render_preview_content("")
            self._update_article_route_visual_state("", selection_exists=False)

        def _restore_local_rows_after_save_error(self) -> None:
            if self.connection is None:
                return
            try:
                self._load_rows()
            except sqlite3.DatabaseError as exc:
                messagebox.showerror(
                    "Ошибка чтения",
                    f"Не удалось перечитать локализованную БД после ошибки сохранения:\n{exc}",
                    parent=self,
                )
                self._clear_local_views()

        def _save_articles_immediately(
            self,
            *,
            success_status: str,
            article_route: str | None = None,
        ) -> bool:
            if self._save_all(status_text=success_status):
                return True
            self._restore_local_rows_after_save_error()
            if article_route is not None:
                self._select_article_by_route(article_route)
            return False

        def _add_article(self) -> None:
            route = simpledialog.askstring(
                "Новая статья",
                "Введите маршрут для новой статьи:",
                parent=self,
            )
            if route is None:
                return
            route = route.strip()
            if not route:
                messagebox.showwarning(
                    "Пустой маршрут",
                    "Маршрут не может быть пустым.",
                    parent=self,
                )
                return
            if any(t.route == route for t in self.articles):
                messagebox.showwarning(
                    "Дубликат",
                    f"Статья с маршрутом '{route}' уже существует.",
                    parent=self,
                )
                return

            next_sort = max((t.sort_order for t in self.articles), default=-1) + 1
            self.articles.append(
                ArticleRow(
                    route=route,
                    name=route or "Новая статья",
                    description="",
                    id_icon="",
                    sort_order=next_sort,
                    is_visible=True,
                    markdown="",
                )
            )
            self._sort_articles()
            self._refresh_articles_tree()
            self._select_article_by_route(route)
            self._save_articles_immediately(
                success_status=f"Статья с маршрутом '{route}' добавлена.",
                article_route=route,
            )

        def _delete_article(self) -> None:
            if self.selected_article_index is None:
                return
            row = self.articles[self.selected_article_index]
            if not messagebox.askyesno(
                "Удаление статьи",
                f"Удалить статью с маршрутом '{row.route}'?",
                parent=self,
            ):
                return
            del self.articles[self.selected_article_index]
            self._refresh_articles_tree()
            self._clear_article_editor()
            self._save_articles_immediately(
                success_status=f"Статья с маршрутом '{row.route}' удалена."
            )

        def _apply_article_changes(self) -> None:
            if self.selected_article_index is None:
                messagebox.showinfo("Нет выбора", "Сначала выберите запись в статьях главного окна.", parent=self)
                return
            row = self.articles[self.selected_article_index]

            route = self._route_value_from_editor()
            name = self.topic_name_var.get().strip()
            description = self.topic_description_var.get().strip()
            icon = self._icon_value_from_editor()
            sort_raw = self.topic_sort_var.get().strip()
            markdown = self.markdown_text.get("1.0", "end-1c")

            if not route:
                messagebox.showwarning("Ошибка", "Маршрут не может быть пустым.", parent=self)
                return

            if any(i != self.selected_article_index and t.route == route for i, t in enumerate(self.articles)):
                messagebox.showwarning(
                    "Дубликат",
                    f"Маршрут '{route}' уже существует.",
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
            row.markdown = markdown

            self._sort_articles()
            self._refresh_articles_tree()
            self._select_article_by_route(route)
            self._update_article_route_visual_state(route, selection_exists=True)
            self._save_articles_immediately(
                success_status=f"Изменения для статьи с маршрутом '{route}' сохранены.",
                article_route=route,
            )

        def _sort_articles(self) -> None:
            self.articles.sort(key=lambda item: (item.sort_order, item.route))

        def _select_article_by_route(self, route: str) -> None:
            if not route:
                return
            for idx, row in enumerate(self.articles):
                if row.route != route:
                    continue
                item_id = str(idx)
                self.articles_tree.selection_set(item_id)
                self.articles_tree.focus(item_id)
                self.articles_tree.see(item_id)
                self.selected_article_index = idx
                self._reload_selected_article()
                return


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

