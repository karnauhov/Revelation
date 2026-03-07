from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from .models import MarkdownTemplateSpec

def revelation_markdown_template_sections() -> list[tuple[str, tuple[MarkdownTemplateSpec, ...]]]:
    return [
        (
            "Ссылки",
            (
                MarkdownTemplateSpec(
                    key="external_link",
                    label="URL",
                    icon_name="open_in_new",
                    template="[Текст ссылки](https://example.com)",
                    title="Внешняя markdown-ссылка",
                    example="[Apache Licenses](https://www.apache.org/licenses/)",
                    note=(
                        "Подходит для обычных http/https ссылок и прямых ссылок на "
                        "скачиваемые файлы из интернета."
                    ),
                ),
                MarkdownTemplateSpec(
                    key="db_file_link",
                    label="DB файл",
                    icon_name="download",
                    template="[Файл из БД](dbfile:topic-media/sample.pdf)",
                    title="Скачивание файла из общей БД ресурсов",
                    example="[From our DB](dbfile:topic-media/sample.pdf)",
                    note="Формат: dbfile:<resource_key>.",
                ),
                MarkdownTemplateSpec(
                    key="asset_file_link",
                    label="Asset файл",
                    icon_name="file_download",
                    template="[Файл из assets](resource:assets/images/UI/app_icon.png)",
                    title="Скачивание файла из assets проекта",
                    example="[Иконка приложения](resource:assets/images/UI/app_icon.png)",
                    note="Формат: resource:assets/<path/to/file>.",
                ),
                MarkdownTemplateSpec(
                    key="screen_link",
                    label="Экран",
                    icon_name="open_in_app",
                    template='[Экран "О программе"](screen:about)',
                    title="Переход на экран приложения",
                    example='["About" screen](screen:about)',
                    note="Формат: screen:<route_without_leading_slash>.",
                ),
                MarkdownTemplateSpec(
                    key="topic_link",
                    label="Статья",
                    icon_name="article",
                    template='[Статья "Лицензия"](topic:license)',
                    title="Переход на markdown-статью приложения",
                    example='[Page "License"](topic:license)',
                    note="Формат: topic:<article_route>.",
                ),
                MarkdownTemplateSpec(
                    key="bible_link",
                    label="Библия",
                    icon_name="menu_book",
                    template="[Откр. 9:11](bible:Rev9:11)",
                    title="Ссылка на стих в онлайн-Библии",
                    example="[Rev 9:11](bible:Rev9:11)",
                    note="Формат: bible:<BookCode><Chapter>[:Verse].",
                ),
                MarkdownTemplateSpec(
                    key="word_link",
                    label="Word",
                    icon_name="auto_stories",
                    template="[Первоисточник](word:U001:325v:2)",
                    title="Переход к слову/странице первоисточника",
                    example="[Codex Sinaiticus](word:U001:325v:2)",
                    note="Формат: word:<sourceId>[:pageName[:wordIndex]].",
                ),
                MarkdownTemplateSpec(
                    key="strong_link",
                    label="Strong",
                    icon_name="tag",
                    template="[Словарь G602](strong:G602)",
                    title="Ссылка на номер Стронга",
                    example="[Dictionary entry H87](strong:H87)",
                    note="Поддерживаются Greek G### и Hebrew H###.",
                ),
                MarkdownTemplateSpec(
                    key="strong_picker_link",
                    label="Пикер Strong",
                    icon_name="numbers",
                    template="[Пикер G333](strong_picker:G333)",
                    title="Открытие пикера по номеру Стронга",
                    example="[Strong’s number picker dialog G333](strong_picker:G333)",
                    note="Формат: strong_picker:G###.",
                ),
            ),
        ),
        (
            "Изображения",
            (
                MarkdownTemplateSpec(
                    key="external_image",
                    label="URL img",
                    icon_name="image",
                    template="![alt](https://images.unsplash.com/2/03.jpg)",
                    title="Изображение по внешнему URL",
                    example="![road](https://images.unsplash.com/2/03.jpg)",
                    note="Рендерится как обычная markdown-картинка из сети.",
                ),
                MarkdownTemplateSpec(
                    key="asset_image",
                    label="Asset img",
                    icon_name="photo",
                    template="![icon](resource:assets/images/UI/app_icon.png)",
                    title="Изображение из assets проекта",
                    example="![icon](resource:assets/images/UI/app_icon.png)",
                    note="Формат: resource:assets/<path/to/image>.",
                ),
                MarkdownTemplateSpec(
                    key="db_image",
                    label="DB img",
                    icon_name="collections",
                    template="![codex](dbres:topic-media/preface01.png)",
                    title="Изображение из общей БД ресурсов",
                    example="![codex](dbres:topic-media/preface01.png)",
                    note="Формат: dbres:<resource_key>.",
                ),
            ),
        ),
    ]

class _ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self._widget = widget
        self._text = text
        self._after_id: str | None = None
        self._window: tk.Toplevel | None = None
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")
        widget.bind("<Destroy>", self._on_leave, add="+")

    def _on_enter(self, _event: tk.Event[tk.Misc]) -> None:
        self._cancel_scheduled_show()
        self._after_id = self._widget.after(350, self._show)

    def _on_leave(self, _event: object | None = None) -> None:
        self._cancel_scheduled_show()
        if self._window is not None:
            self._window.destroy()
            self._window = None

    def _cancel_scheduled_show(self) -> None:
        if self._after_id is None:
            return
        try:
            self._widget.after_cancel(self._after_id)
        except tk.TclError:
            pass
        self._after_id = None

    def _show(self) -> None:
        self._after_id = None
        if self._window is not None:
            return
        if not self._widget.winfo_exists():
            return

        window = tk.Toplevel(self._widget)
        window.wm_overrideredirect(True)
        try:
            window.attributes("-topmost", True)
        except tk.TclError:
            pass
        window.configure(background="#fff8db")

        label = tk.Label(
            window,
            text=self._text,
            justify="left",
            background="#fff8db",
            foreground="#202020",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=6,
        )
        label.pack()

        x = self._widget.winfo_rootx() + 18
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 6
        window.geometry(f"+{x}+{y}")
        self._window = window


class MarkdownTemplateToolbar(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        *,
        sections: list[tuple[str, tuple[MarkdownTemplateSpec, ...]]],
        icon_resolver: Any,
        on_insert: Any,
    ) -> None:
        super().__init__(parent, borderwidth=1, relief="solid", padding=(4, 3))
        self._buttons: list[ttk.Button] = []
        self._tooltips: list[_ToolTip] = []
        for section_index, (_section_title, items) in enumerate(sections):
            if section_index > 0:
                separator = ttk.Separator(self, orient="vertical")
                separator.pack(side="left", fill="y", padx=4, pady=1)

            section_frame = ttk.Frame(self)
            section_frame.pack(side="left")

            for item in items:
                icon = icon_resolver(item.icon_name)
                button_kwargs: dict[str, object] = {
                    "command": lambda spec=item: on_insert(spec),
                    "style": "Toolbutton",
                    "padding": 1,
                }
                if icon is not None:
                    button_kwargs["image"] = icon
                    button_kwargs["compound"] = "image"
                else:
                    button_kwargs["text"] = item.label
                button = ttk.Button(section_frame, **button_kwargs)
                button.pack(side="left", padx=1, pady=0)
                self._buttons.append(button)
                self._tooltips.append(_ToolTip(button, self._tooltip_text_for_item(item)))

    def _tooltip_text_for_item(self, item: MarkdownTemplateSpec) -> str:
        lines = [
            item.title,
            "",
            "Пример:",
            item.example,
        ]
        if item.note:
            lines.extend(["", item.note])
        return "\n".join(lines)

    def set_enabled(self, enabled: bool) -> None:
        state = "!disabled" if enabled else "disabled"
        for button in self._buttons:
            button.state([state])

