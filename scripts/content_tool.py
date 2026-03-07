#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Content of Revelation: GUI tool for managing localized articles."""

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
import sqlite3
import subprocess
import shutil
import tempfile
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import TYPE_CHECKING, Any, Callable

try:
    from markdown import markdown as md_to_html
except ImportError:
    md_to_html = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

if TYPE_CHECKING:
    from tkinterweb import HtmlFrame as HtmlFrameType
else:
    HtmlFrameType = Any

try:
    from tkinterweb import HtmlFrame as HtmlFrameWidget
except ImportError:
    HtmlFrameWidget = None


@dataclass
class ArticleRow:
    route: str
    name: str
    description: str
    id_icon: str
    sort_order: int
    is_visible: bool
    markdown: str


@dataclass
class ResourceRow:
    key: str
    file_name: str
    mime_type: str
    size_bytes: int


@dataclass
class StrongRow:
    id: int
    word: str
    category: str
    synonyms: str
    origin: str
    usage: str
    localized_flags: dict[str, bool]
    localized_search: str


@dataclass
class PrimarySourceSummary:
    id: str
    family: str
    number: int
    group_kind: str
    sort_order: int
    pages_count: int
    words_count: int
    verse_rows_count: int
    can_show_images: bool
    preview_resource_key: str
    title_preview: str
    locale_flags: dict[str, bool]


@dataclass
class PrimarySourcePageSummary:
    source_id: str
    page_name: str
    sort_order: int
    content_ref: str
    image_path: str
    mobile_image_path: str
    words_count: int
    verse_rows_count: int
    local_exists: bool


@dataclass(frozen=True)
class FormFieldSpec:
    key: str
    label: str
    kind: str = "entry"
    width: int = 40
    height: int = 4
    options: tuple[str, ...] = ()
    readonly: bool = False


@dataclass(frozen=True)
class MarkdownTemplateSpec:
    key: str
    label: str
    icon_name: str
    template: str
    title: str
    example: str
    note: str = ""


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


Point = tuple[float, float]


def get_windows_documents_dir() -> Path | None:
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "Personal")
        if isinstance(value, str) and value.strip():
            return Path(os.path.expandvars(value.strip()))
    except Exception:
        return None
    return None


def get_documents_dir() -> Path:
    system = platform.system()
    home = Path.home()
    if system == "Windows":
        docs = get_windows_documents_dir()
        if docs is not None:
            return docs
        profile = os.environ.get("USERPROFILE")
        return Path(profile) / "Documents" if profile else home / "Documents"
    if system == "Linux":
        try:
            result = subprocess.run(
                ["xdg-user-dir", "DOCUMENTS"],
                capture_output=True,
                text=True,
                check=False,
            )
            value = result.stdout.strip()
            if result.returncode == 0 and value:
                return Path(value)
        except OSError:
            pass
    return home / "Documents"


def default_primary_sources_dir() -> Path:
    return get_documents_dir() / "revelation" / "primary_sources"


def clamp01(value: float) -> float:
    return 0.0 if value < 0 else 1.0 if value > 1 else value


def parse_indexes(raw: str) -> list[int]:
    raw = raw.strip()
    if not raw:
        return []
    out: list[int] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", maxsplit=1)
            start = int(left.strip())
            end = int(right.strip())
            if end < start:
                raise ValueError(f"Range error: '{token}'")
            out.extend(range(start, end + 1))
        else:
            out.append(int(token))
    return sorted(set(out))


def format_indexes_for_ui(indexes: list[int]) -> str:
    return ", ".join(str(i) for i in indexes)


def find_matching_bracket(text: str, start_index: int) -> int:
    depth = 0
    for idx in range(start_index, len(text)):
        ch = text[idx]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return idx
    raise ValueError("Unbalanced brackets in snippet.")


def extract_list_content(text: str, key: str) -> str:
    pattern = rf"{re.escape(key)}\s*:\s*(?:const\s*)?\["
    match = re.search(pattern, text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Field '{key}' not found.")
    start = match.end() - 1
    end = find_matching_bracket(text, start)
    return text[start + 1 : end]


def split_top_level_lists(body: str) -> list[str]:
    blocks: list[str] = []
    depth = 0
    block_start: int | None = None
    for idx, ch in enumerate(body):
        if ch == "[":
            if depth == 0:
                block_start = idx + 1
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0 and block_start is not None:
                blocks.append(body[block_start:idx])
                block_start = None
    return blocks


def parse_verse_snippet(snippet: str) -> dict[str, object]:
    chapter_match = re.search(r"chapterNumber\s*:\s*(\d+)", snippet)
    verse_match = re.search(r"verseNumber\s*:\s*(\d+)", snippet)
    if not chapter_match or not verse_match:
        raise ValueError("chapterNumber/verseNumber not found.")

    label_match = re.search(
        r"labelPosition\s*:\s*Offset\(\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)\s*\)",
        snippet,
    )
    label: Point | None = None
    if label_match is not None:
        label = (float(label_match.group(1)), float(label_match.group(2)))

    word_indexes_body = extract_list_content(snippet, "wordIndexes")
    word_indexes = [int(value) for value in re.findall(r"\d+", word_indexes_body)]

    contours_body = extract_list_content(snippet, "contours")
    contours: list[list[Point]] = []
    for contour_body in split_top_level_lists(contours_body):
        points: list[Point] = []
        for x_raw, y_raw in re.findall(
            r"Offset\(\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)\s*\)",
            contour_body,
        ):
            points.append((float(x_raw), float(y_raw)))
        if points:
            contours.append(points)
    if not contours:
        raise ValueError("No contour points found in contours.")

    return {
        "chapter": int(chapter_match.group(1)),
        "verse": int(verse_match.group(1)),
        "label": label,
        "word_indexes": word_indexes,
        "contours": contours,
    }


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


GREEK_DESC_GROUP_RANGES: list[tuple[int, int]] = [
    (1, 158),
    (159, 381),
    (382, 574),
    (575, 743),
    (744, 907),
    (908, 1084),
    (1085, 1252),
    (1253, 1408),
    (1409, 1582),
    (1583, 1791),
    (1792, 1949),
    (1950, 2114),
    (2115, 2250),
    (2251, 2415),
    (2416, 2576),
    (2577, 2734),
    (2735, 2896),
    (2897, 3067),
    (3068, 3325),
    (3326, 3489),
    (3490, 3632),
    (3633, 3766),
    (3767, 3887),
    (3888, 4026),
    (4027, 4151),
    (4152, 4278),
    (4279, 4403),
    (4404, 4520),
    (4521, 4659),
    (4660, 4784),
    (4785, 4909),
    (4910, 5034),
    (5035, 5163),
    (5164, 5269),
    (5270, 5403),
    (5404, 5505),
    (5506, 5624),
]
GREEK_DESC_KJV_PATTERN = re.compile(r"; \[in KJV:.*?\]", re.DOTALL)


def clean_greek_desc_for_prompt(text: str | None) -> str:
    if not text:
        return ""
    return GREEK_DESC_KJV_PATTERN.sub("", text)


def _load_greek_desc_translation_prompt_header() -> str:
    fallback = (
        "Ты переводчик-лексикограф словаря Стронга.\n"
        "Переведи текстовые поля (в первую очередь поле 'desc') аккуратно и терминологически последовательно.\n"
        "Верни только валидный JSON-массив, без пояснений и без изменения структуры объектов."
    )
    export_script_path = Path(__file__).resolve().parent / "export_greek_descs_groups.py"
    try:
        source = export_script_path.read_text(encoding="utf-8")
        module = ast.parse(source)
    except (OSError, SyntaxError):
        return fallback

    docstring = ast.get_docstring(module) or ""
    marker = "Промпт для перевода:"
    marker_index = docstring.find(marker)
    if marker_index < 0:
        return fallback

    prompt_text = docstring[marker_index + len(marker):].strip()
    return prompt_text or fallback


GREEK_DESC_TRANSLATION_PROMPT_HEADER = _load_greek_desc_translation_prompt_header()

LANGUAGE_NAME_RU_BY_CODE: dict[str, str] = {
    "af": "Африкаанс",
    "sq": "Албанский",
    "am": "Амхарский",
    "ar": "Арабский",
    "hy": "Армянский",
    "az": "Азербайджанский",
    "eu": "Баскский",
    "be": "Белорусский",
    "bn": "Бенгальский",
    "bs": "Боснийский",
    "bg": "Болгарский",
    "my": "Бирманский",
    "ca": "Каталанский",
    "ug": "Уйгурский",
    "zh": "Китайский",
    "co": "Корсиканский",
    "hr": "Хорватский",
    "cs": "Чешский",
    "da": "Датский",
    "nl": "Нидерландский",
    "en": "Английский",
    "eo": "Эсперанто",
    "et": "Эстонский",
    "fi": "Финский",
    "fr": "Французский",
    "fy": "Фризский",
    "gl": "Галисийский",
    "ka": "Грузинский",
    "de": "Немецкий",
    "el": "Греческий",
    "gu": "Гуджарати",
    "ht": "Гаитянский креольский",
    "ha": "Хауса",
    "uz": "Узбекский",
    "he": "Иврит",
    "hi": "Хинди",
    "vi": "Вьетнамский",
    "hu": "Венгерский",
    "is": "Исландский",
    "ig": "Игбо",
    "id": "Индонезийский",
    "ga": "Ирландский",
    "it": "Итальянский",
    "ja": "Японский",
    "jv": "Яванский",
    "kn": "Каннада",
    "kk": "Казахский",
    "km": "Кхмерский",
    "rw": "Киньяруанда",
    "ko": "Корейский",
    "ku": "Курдский",
    "ky": "Киргизский",
    "lo": "Лаосский",
    "la": "Латынь",
    "lv": "Латышский",
    "lt": "Литовский",
    "lb": "Люксембургский",
    "mk": "Македонский",
    "mg": "Малагасийский",
    "ms": "Малайский",
    "ml": "Малаялам",
    "mt": "Мальтийский",
    "mi": "Маори",
    "mr": "Маратхи",
    "mn": "Монгольский",
    "ne": "Непальский",
    "no": "Норвежский",
    "ny": "Ньянджа",
    "or": "Ория",
    "ps": "Пушту",
    "fa": "Персидский",
    "pl": "Польский",
    "pt": "Португальский",
    "pa": "Панджаби",
    "ro": "Румынский",
    "ru": "Русский",
    "sm": "Самоанский",
    "gd": "Шотландский гэльский",
    "sr": "Сербский",
    "st": "Сесото",
    "sn": "Шона",
    "sd": "Синдхи",
    "si": "Сингальский",
    "sk": "Словацкий",
    "sl": "Словенский",
    "so": "Сомалийский",
    "es": "Испанский",
    "su": "Сунданский",
    "sw": "Суахили",
    "sv": "Шведский",
    "tl": "Тагальский",
    "tg": "Таджикский",
    "ta": "Тамильский",
    "tt": "Татарский",
    "te": "Телугу",
    "th": "Тайский",
    "tr": "Турецкий",
    "tk": "Туркменский",
    "uk": "Украинский",
    "ur": "Урду",
}


def target_language_name_ru(lang_code: str) -> str:
    code = (lang_code or "").strip().lower()
    if code in LANGUAGE_NAME_RU_BY_CODE:
        return LANGUAGE_NAME_RU_BY_CODE[code]
    return f"Код языка: {code.upper()}" if code else "-"


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
        "translate": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAv0lEQVQ4y92TPQrCQBCFvybaxMpTmDQWwZ/Cs+UEUdyInV5ET6Gks7QULAJCdHEsDBLdXUzafNsN77Ezs2+hjYQsyMjJyZgTlNXYLvZYoZHK0Sg8YsQu3yMUKCb4+ExZc0c4IXaDQjgz/KqNyMu7DAI0xY8c4k9zBgmCcsothgPC2Cm3GK4IvSb7b2wwW/qDbeg3G4Sk7lohQqMZ1H24iAvC0pWkajT6zNjyQNjRcc1hhu9JSrdevG8cSQnb+INfa9dgs2rwKa8AAAAASUVORK5CYII=",
        "save": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAXklEQVQ4y2NgGLTAk+Exw38csB6bhkc4lePQAhLGBnBqIaQBQwthDf+poIEQHEoafjKUM0gAYTmQRZSGMrhoGXEaJOGikjTSQLKTiPL0I4KB+oj4DASCjxk8Bm3mBwATwvSdhoWVegAAAABJRU5ErkJggg==",
        "publish": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAPElEQVQ4y2NgGDKgHghJUv4fCOtJU060FoRyorSgKieoBVM5Xi3YlRPhMGSlRIERqYF24D8eSB0NQxUAAMVCcIlDCOtfAAAAAElFTkSuQmCC",
        "open_resource": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAC7klEQVR42uVVz4tURxD+qqt7friRRVkSDQQkDEpGBKHdjW6E0V0IGySSHN7J/Af5FwLjevIi/gMieH54kSXmoIuTQxh/PE/JRIJsEsghGLNRZpM37/XrLg/OhJmd3WT0oAc/KHivu6jvq6ruauBNBo1YFHH/+9WreAk0VX321ts6K3WJctObcl4XlSOpV/fXkhtP+3EFANTEJehbFEVcq902gLooO6TryuoXLiq/MvNqVfkr9XpUGo47TtBsDtZkK4vj2D98+E3W2TfzRRC5yoqnAbxFpCDAz51OvWg0Gv9WRo+pXl4OADA/f3rnE/NUvHNjZSwppf2jRy54vqxYfaZIGRHxAnoMLIeNDctjBFEUcRzHoX50YY6hz3X9P/PkmJjUSJYk4ADKiSQopmkv/i8IviuVK6d8UYwVZCSDWm2pRD67wCV13OXFhgA8aNYgOIi6gMyQYhAICqIDufNZ3isJ8O5mgoE6iuPYY/d6WYBjWZ5t+Irb703vnRx/7/U62wOVvlffNzMVRL5kNpmEsB6Cv2nK5Z0QXvyhvesTkFwFgCRJ/JYZsNZCBVIAquvck9/a7XR4P7jqx8boKwCMhz9FwoeJ1CIJCiD2nTtYHbhue4qkv1YJwQAga60BgP2zjSVj+GsAunC9zx/cabUB2TPcnlptqbxdicbAWgsASZLEHfhw8UTFVK4LUSgKf7pz79traDaVArlhbdPTf4SJCYZ9pCi+D8GvhDw/8+O91evW2h2D4/x/0JM4/ZS0HgP4dDAmgBU36VDZloBDMNZak6YpVatVSdP3CQCq1RUBYKy1SBWpFycQKJD4Tru9PrqRDP84ADg4t9B9fi6EJicg9IjU1AezJ89uauKQBlEECgB9JMGTbOM3Mq4bjYZutVqhPrfwlTGlZWYN0H9PcwkeeZb+7nw41O8TDd/8rd4DZa3lHu8+qTTNeu88BeItZAkEJEARQJce3L3552t9V8cRRWzX1ia5I0iSpNhclleKZ9KpP8l/B+AQAAAAAElFTkSuQmCC",
        "open_in_new": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABCklEQVR4nN3UPUoDQRjG8b8mB3nAIim00MbKyjoBQVHwAB7DvYYHEGIXKyshbWxsBLEQHs+QOqyFs7AZZ/YjWPk0s7sz72/fZZmBP85O/UbSBDiKnwPYLiSNgauEs7C9ABjWsCnw2PDyAhgDt5n5TRA4DOM58JEpegYOgAFwBxzHC+pg9Zmftt9Smu2VpHfgPmDLGN3NdJKMpEHALoEH4CZe0xlMYNfAeiswhdleA1/AGTCr1g6TQjcM2ytg3rnDJizM70sqJRWtYBuWS1OHJ8BFH6wRDFvptA8GLT+l2p99UgfLMI4kda3fi2o3wNcwzuifZXURH19Tfg6JX8dXJiXwYvtpiyb+S74Bv+xcUy0b9DMAAAAASUVORK5CYII=",
        "download": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAvklEQVR4nO2UIQ4CMRBFHwS5h/gXIMEhEFQut+JWIBAgFoHBIBGTcATWg9lNNt12200IQfBV+6fz2mknhQ9rMhSUtAacZx/N7BTLmSU2dMDW87ZAFDhNAEfr94G9O5RUAstm6gI5TlI7vpjZrhvsvbKkAtgDq8RhzkBpZs+u2SvZzGqgBKqxsCAwA1rFYJBubL/8FlbHcgaBHvQFbIZg2ZJUNODvK9Q2V2CRmX8zs3nXCH0OB+CeCXxkrvtrhN751znTYmpUqAAAAABJRU5ErkJggg==",
        "file_download": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAuUlEQVR4nO2UMQoCMRBFn2K5h5gDCLaChSnXU3ksBZu1WMHOxs7i4xW012bFJZtssiBi4e/yM/MmkwyBD2vUt2lmDnCeXUmqYjmTREEHrAN+FDhOAAfr94GdRzGzEpg3SwcsvZA97zs8StqkgAWwBRaJwxyAUtKtbXZalnQHSqAeCgsCM6B1DAbpwfbbf8HusZxeoAd9AKs+WLbMrGjA31dobE7ALDP/LGnaNkKfww64ZAKvmXF/DdAT4wU6bBr/ZL8AAAAASUVORK5CYII=",
        "open_in_app": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA40lEQVR4nO2TTQqBURSGHz9DLMDoXYCJicjYDiyAwg6MsRJKmRlTrMCEUiYmZwtkzsCVmz583RQDp27n9N7zPp3T7cKvR+JWSGoAw0BO08xGAElPVOhUvjcdcbkEDjFBOaDmC1HArpltYo0lFYCtryWf9D4aq5KqcXrfAiVVgBkwc3U4UFIJmANZd+aSykFASRmgAyy4PtLR1W1J2We+qEcBwMxOQMvBN0DazOqvpns5YWh8HOivbC6vJd20gZn1fYOkPtB74OyjgGMgDxS5//Gdywsg5WlTV5+BFTCJu8E/vhAXXpAusowL82gAAAAASUVORK5CYII=",
        "article": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAyUlEQVR4nOWUPQ5BQRSFPyIRjVKUJxGhUGAfHqXdYBN2oWAhnkSjUNzaCpQKJM8zP0x0TjVzZs6XeyeZCz9WpbiRNAHGXzJyM9u9ASVlwDaxsOkTWi2Yo0TYS7bmuXAFThFID2iUTR/wbGbBiiXlwPBTYEvSIlJh22V6gcAyAnTK2zIwi2Q33N/xI2AlcBaUL9QBDr8EXoC1w+8D8ySgma3KpqRpKrAr6ejwmyFYCFgHBrGwS8W/nKcAHto/F+XxlfH9kHgZX3+oG7BAJYV1Brg1AAAAAElFTkSuQmCC",
        "menu_book": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABUElEQVR4nO3TP0iVURjH8c+1m6B3iC6BxMV6gkgCKWpw0TVQaGtrjKagtRahtnBxkXAIGp11dmgLri6S3UWwDvSHqKDUIBrKhveE8nKL921q6Lec5/A853ueH885/OtqRMQAbuA2LpTyP/AUc3l/B5MYKNX1sIBHjYgYx2bFBnawiuc5buEUpvN6qVnDzS08Til9Kyci4j7uQWVgSmkxIoYjYgan0cZnPDtcVxkYEWfz4X28xUecwDq2agOxh+voYgTH8QmvFAOtDWxiFpfRwHccwQo2fhWVx/8nDeIJJhRWW/mSm+Vbq2oHw1hCJ8df8/713wBP4iIeIuE9jiqsX6kNTCn1MNUvFxH1gRHRVnzRqxjHMXzBdu60L/CdAzstnMNozr3IkA+Kr7qreNwdnDkMfIMHWE4prfXp7DzuYgjzKaVun5oxXMPLqo7/6/f6CedWSlkQlOv0AAAAAElFTkSuQmCC",
        "auto_stories": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABFElEQVR4nO3UPyvGYRTG8Y+HDP7GYGE4MWBSFkkmg9cgBpkNJmUzKpNJsXgP8u8FsFFiFGeyGUQWwuAZ9OPR86AsrrqXc119z326uw8/UEQ0FGulH8DasVGsf+hQJawNB2j+Elju2osm3OEiMx8KmVbsYwTnH4ARUcIc5jFU8J8j4hCrmbkdES3Yw2ihyQwasdWAQWxWmK6E8fKpwwTGPsn1YRnH336USvoH1qzT3wRuYbZY/NZPwUpmLn1m1Ap8wUJmrlUK1ArczcynrwJVAyOiE1MRMYlhdOEBl6ivBLzBGW7Rin50l70rtOHe21I4QQd6EO+B11jBDo4y87lwswEseltV6zjMzMdCpgfTyGon/ju9AmCNP1bTpUJfAAAAAElFTkSuQmCC",
        "tag": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAj0lEQVR4nO2RwQnCQBBFn5IyPPwmJCkjoMXYgtbh0UCsIodt4h8MlqGXDZhFV4QcFPMvM/MOnwcDPxtJtaSbpG2OpVlOLVIkVhWwiuc6zkoSGdbb7oZjkRSegM2HUmfb9VNDYA8c414CO+AAdBl2fSwYFdoOQIi2Aw6221cszfyUf3hKrrAHGuDyhs359twBWmNISVAdjoEAAAAASUVORK5CYII=",
        "numbers": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA8UlEQVR4nO2RoU6DMRRGD2wIMjDoiS88AIKEIGfHMCTwKgseiZvdAxAEmqBI+N0UAkcQn5tjAjK1MEyzbKO7RY6EY9qeJv3u7YV1ZyO6lFQHRkBl+3SVm2ezEHgI7ABVwc2oZ6pqA410bKe1Iek8cC+2X2GpZUm7wHsuqMCJ7YdchTXgIu23gFtgAFwHDuCpGCnpWNJUUjdyy0RDaaW1KrgFZi1L2gY6c3dnwBewL6kZuEfbox8PpvS7TOhN4CbAXrZC4C1VAHAAXAF94D5wY9sfmcBFJF2mzz+KXI5VQ2kBn8Bzwf36wSHQsz0puH/+At9C1U5v75qLzQAAAABJRU5ErkJggg==",
        "image": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA6klEQVR4nO2UPUpDQRRGj8GF3E34gyuIAasUKVNZZimxcROClQiKO/Cnik0q8eAGghC0sIjNGxlH8/LytBH8mpn55t7DN8Mw8MvayBcR0QV2Sr9GC+BavfoCjIh94KJlsG6CdjJzuyUMYDdNcmDTY36nj95OXVUb/QNX6gw4qivYrNmbAo9Ar1o/AEPgBdgjeypNEs6BPjAA7oFXoK8+q2+VP1sHeKhO1TlwAAzVSdpUn6q0jYDH6knerJ6WReo5MC79/A4X1TiKiNGS5MuUej8lvFsTkusmTcrvqwdslf6KZLfq5Q/C/HW9Ax5qRmONQ65xAAAAAElFTkSuQmCC",
        "photo": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA6klEQVR4nO2UPUpDQRRGj8GF3E34gyuIAasUKVNZZimxcROClQiKO/Cnik0q8eAGghC0sIjNGxlH8/LytBH8mpn55t7DN8Mw8MvayBcR0QV2Sr9GC+BavfoCjIh94KJlsG6CdjJzuyUMYDdNcmDTY36nj95OXVUb/QNX6gw4qivYrNmbAo9Ar1o/AEPgBdgjeypNEs6BPjAA7oFXoK8+q2+VP1sHeKhO1TlwAAzVSdpUn6q0jYDH6knerJ6WReo5MC79/A4X1TiKiNGS5MuUej8lvFsTkusmTcrvqwdslf6KZLfq5Q/C/HW9Ax5qRmONQ65xAAAAAElFTkSuQmCC",
        "collections": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA+ElEQVR4nOWUPU5CQRSFP4QV0JOcGq0NhSsgJppITOgMvRUNJLQmbIDCPdhJQ2NlxSoOWhAbidHO8FMwz4Y38B5Y6WlmcubON+dOceGXVUgzJT0C5zk478CJ7elRpKCeM1gZqAHEgDF/m4o/FyVdSlpKauwBOjjJPwTOgLtDgGOgG/YLoGm7B9ynFZcypLkGXoAz4Nn2KJzdAsfBz5zwxvbE9jIk6ycHtr+BK+A1S8IvYA60JLUSU1Ja7QdQAT63ATtAH7jY0QGs/3UIPEWBtgfAIANsQwlwHtZapK1U2X6IAcesR1A7Z6CN8VcKL71JqgKnhKnxd7UC5TlAzewv++oAAAAASUVORK5CYII=",
        "replace_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAD/0lEQVR42p1W3WtcVRD/zTnnfuTDTZsoRBC0sH5k11RkmzTEyJKmq9XSah8WLCL42Ad9EEQkKupD++SbKOqLf0CgEsGYiqYGahq3BLTa5EGpCUqDtEnz0Wb33nvOjA+pMU12TdJ5OueeM/Ob+c2cmUuoLoTtiWCnks/nzQ5VaMeHmUy+0e1Kaipqz5PGcp0qlYaX1tmRLQHS6UOB3xy/ScArAOqlBgMk5JRW4lhGJ+9vPoaBgX8v8sa7aj0QN9lQEb2nlLp7C3INM6c8Y45kZ+ZOo1ikDfY2AQAAvGCFWXjRsbvJQZJ2JmqNcfNeZ6LW9WvrqTQgi9Ym8MO6o9mZuS9rgVRLqAcAN5Jk4a/x8XI19+/r6rJNqNcAFqLyyrDvBy9kZua/mCwWj2FgwK3PiarFQcjs5fN5k04fCjKZjJ/JZHygqAHATxp9CEJACFCX4yS+bow5kp2eG3y4u/uuWwBUKwJAQCBgdHTUArD/HUwil8t5i/eYCuai80FY/6SA+tlZWJvA84PDnOBVAKdyuZw3MTGRmBrGucm5cntX30EovZ+tFRE4XYk/m5g4dx2AynQdeN0l9tnERQwogtATIPTRBqdNlcIVInIVnfpKky4YLwC8AMwOTtEbbbnel6Ymzg5Njo+UAJTW3k5n72tKmwIhsjUBnE2RQZQQqEl7fsHG0bx19mMSVADZpz3/eQ0ebNvf+9zUj2eHHunoa9HEOV0xPzi4ujUGapXp2jNSSmwcD4r2Hpwsjbxz6cLIyZAbXnScHCWCVoLTmY6+k56myyLou3ixuyxEulo6bwPQZkkE4rFzlUW9cnxy/Jt5ANi7t9BQ0StXIDjunB1SygR+GPQzOx0HwQfA+0zMsiXAWggQaQmCAMWibtvX97hrtK0QBBAUFOEn0jpxSXyeRfp/Pzd8dVVH0XYBAAALCwAGBpxS/Aks3hbCVUAiAUwQ1nvO2u+mLnz/Yfdq3QuIb1TtKdU7IJmZn0cXsx0Hn/bDoDOulPdA0Gw8X1sbo7y8cAKKfgMgY2Njy0BRE64VmB0Eov4/AgEJJGnv6dkFso9Za9/SFb2HoA4zSwWkTwizRh2X2tt7dmc7e59q71r4WinzDFsLEKmtKEoIEOu8VOjMp7+MnTkFAJce2P2ttfHLBDSYIPwIZf23q/P+IFJnQCg458oEOIhwTYqSqF55RlJEBDj+tawdZToP+FaczU5fU1BqWYSNTWIopepXIxawcwAhVMYjWNd4W2Wu37Q0PARV5yxEHgXgA0SA8K3WJSQIASoDEgFSgUgEkViIyopUJMyjju3n165M/zk7OytY7YY7G5nOpjZ912ZJmlIpKg1vPULvZOhvkHfVdv4I6A6tb/L6H2+T3BgFT/QJAAAAAElFTkSuQmCC",
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
        self.articles_tree.heading("visible", text="Показывать")
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

        self._load_strong_rows()
        self._select_strong_by_id(strong_id)
        self._update_file_info()
        self._set_status(
            (
                f"Словарная статья G{strong_id} сохранена "
                f"в {self.common_db_path.stem} и {len(self.strong_local_db_paths_by_lang)} локализованных БД."
            )
        )

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
        for idx, row in enumerate(self.articles):
            if row.route == route:
                self.articles_tree.selection_set(str(idx))
                self.articles_tree.focus(str(idx))
                self.articles_tree.see(str(idx))
                self.selected_article_index = idx
                self._reload_selected_article()
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
        text = str(raw).strip()
        if not text:
            return None
        return int(text)

    def _parse_required_float(self, raw: object, field_label: str) -> float:
        text = str(raw).strip()
        if not text:
            raise ValueError(f"Поле '{field_label}' не может быть пустым.")
        return float(text)

    def _parse_json_list(self, raw: object, field_label: str) -> list[object]:
        text = str(raw).strip() or "[]"
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Некорректный JSON в поле '{field_label}': {exc}") from exc
        if not isinstance(payload, list):
            raise ValueError(f"Поле '{field_label}' должно содержать JSON-массив.")
        return payload

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
        self.primary_source_filtered_ids.clear()

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
                ORDER BY ps.sort_order ASC, ps.id ASC
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
        search = self.primary_source_filter_var.get().strip().lower()
        group_filter = self.primary_source_group_var.get().strip().lower()
        self.primary_source_filtered_ids.clear()
        self.primary_sources_tree.delete(*self.primary_sources_tree.get_children())
        for row in self.primary_sources:
            haystack = " ".join(
                [
                    row.id,
                    row.family,
                    row.group_kind,
                    row.title_preview,
                    str(row.number),
                ]
            ).lower()
            if group_filter and group_filter != "all" and row.group_kind != group_filter:
                continue
            if search and search not in haystack:
                continue
            self.primary_source_filtered_ids.append(row.id)
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

    def _on_primary_source_filter_changed(self, *_args: object) -> None:
        selected_id = self.selected_primary_source_id
        self._refresh_primary_sources_tree()
        if selected_id:
            self._select_primary_source_by_id(selected_id, reload=False)

    def _on_primary_source_filter_combo_changed(self, _event: object) -> None:
        self._on_primary_source_filter_changed()

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

    def _reload_primary_sources_section(self) -> None:
        self._open_common_connection()
        self._ensure_schema()
        if self.common_connection is not None:
            self._ensure_common_schema_on_connection(self.common_connection)
        self._load_primary_sources()
        self._update_ui_availability()
        self._update_file_info()
        if self.common_db_path is None:
            self._set_status("Общая БД не найдена. Раздел первоисточников недоступен.")
            return
        if self.current_db_path is None:
            self._set_status("Локализованная БД не найдена. Локализованные поля первоисточников недоступны.")
            return
        self._set_status(
            f"Первоисточники перечитаны: {self.common_db_path.stem} + {self.current_db_path.stem}."
        )

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
        self.primary_source_title_markup_var.set("")
        self.primary_source_date_label_var.set("")
        self.primary_source_content_label_var.set("")
        self.primary_source_material_text_var.set("")
        self.primary_source_text_style_text_var.set("")
        self.primary_source_found_text_var.set("")
        self.primary_source_classification_text_var.set("")
        self.primary_source_current_location_text_var.set("")
        if self.primary_source_notes_text is not None:
            self._set_text_widget_content(self.primary_source_notes_text, "")
        self.primary_source_preview_image = None
        if hasattr(self, "primary_source_preview_label"):
            self.primary_source_preview_label.configure(
                image="",
                text="Preview ресурса пока недоступен.",
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
        self.primary_source_validation_var.set("Выберите первоисточник.")
        self.primary_source_page_info_var.set("Страница не выбрана.")

    def _reload_selected_primary_source(self) -> None:
        source_id = self.selected_primary_source_id
        if not source_id or self.common_connection is None:
            self._clear_primary_source_editor()
            return

        common_row = self.common_connection.execute(
            "SELECT * FROM primary_sources WHERE id = ? LIMIT 1",
            (source_id,),
        ).fetchone()
        if common_row is None:
            self._clear_primary_source_editor()
            return

        localized_row: sqlite3.Row | None = None
        if self.connection is not None:
            try:
                localized_row = self.connection.execute(
                    "SELECT * FROM primary_source_texts WHERE source_id = ? LIMIT 1",
                    (source_id,),
                ).fetchone()
            except sqlite3.DatabaseError:
                localized_row = None

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

        def localized_value(key: str) -> str:
            if localized_row is None:
                return ""
            return str(localized_row[key] or "")

        self.primary_source_title_markup_var.set(localized_value("title_markup"))
        self.primary_source_date_label_var.set(localized_value("date_label"))
        self.primary_source_content_label_var.set(localized_value("content_label"))
        self.primary_source_material_text_var.set(localized_value("material_text"))
        self.primary_source_text_style_text_var.set(localized_value("text_style_text"))
        self.primary_source_found_text_var.set(localized_value("found_text"))
        self.primary_source_classification_text_var.set(localized_value("classification_text"))
        self.primary_source_current_location_text_var.set(localized_value("current_location_text"))

        self._render_primary_source_preview()
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
                text="Preview ресурс не найден в common_resources.",
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
                    text="Не удалось отрисовать preview ресурс.",
                )
            return
        self.primary_source_preview_label.configure(
            text=f"Preview ресурс найден, но не является изображением: {mime or file_name}",
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

    def _refresh_primary_source_links_tree(self) -> None:
        if not hasattr(self, "primary_source_links_tree"):
            return
        self.primary_source_links_tree.delete(*self.primary_source_links_tree.get_children())
        localized_titles = self._current_primary_source_link_titles()
        for idx, row in enumerate(self.primary_source_link_rows):
            self.primary_source_links_tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    row["link_id"],
                    int(row["sort_order"] or 0),
                    row["link_role"],
                    localized_titles.get(row["link_id"], ""),
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
                  COALESCE(p.mobile_image_path, '') AS mobile_image_path,
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
                mobile_image_path=row["mobile_image_path"] or "",
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
            contours = self._safe_json_loads(row["contours_json"] or "[]", [])
            self.primary_source_verses_tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    int(row["verse_index"] or 0),
                    f"{int(row['chapter_number'] or 0)}:{int(row['verse_number'] or 0)}",
                    len(word_indexes) if isinstance(word_indexes, list) else 0,
                    len(contours) if isinstance(contours, list) else 0,
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
            self.primary_source_validation_var.set("Выберите первоисточник.")
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

        if warnings:
            self.primary_source_validation_var.set("\n".join(f"• {item}" for item in warnings))
        else:
            self.primary_source_validation_var.set("Валидация: явных проблем не найдено.")

    def _ensure_primary_source_section_ready(self) -> bool:
        if self.common_connection is None or self.common_db_path is None:
            messagebox.showwarning("Нет общей БД", "Общая БД недоступна.", parent=self)
            return False
        if self.connection is None or self.current_db_path is None:
            messagebox.showwarning("Нет локализованной БД", "Локализованная БД недоступна.", parent=self)
            return False
        return True

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

    def _save_primary_source_metadata(self) -> None:
        if not self._ensure_primary_source_section_ready():
            return

        source_id = self.primary_source_id_var.get().strip()
        if not source_id:
            messagebox.showwarning("Нет источника", "Сначала выберите или создайте первоисточник.", parent=self)
            return

        try:
            number = self._parse_required_int(self.primary_source_number_var.get(), "Number")
            sort_order = self._parse_required_int(self.primary_source_sort_order_var.get(), "Sort order")
            verses_count = self._parse_required_int(self.primary_source_verses_count_var.get(), "Verses count")
            default_max_scale = self._parse_required_float(
                self.primary_source_default_max_scale_var.get(),
                "Max scale",
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

        localized_values = {
            "title_markup": self.primary_source_title_markup_var.get().strip(),
            "date_label": self.primary_source_date_label_var.get().strip(),
            "content_label": self.primary_source_content_label_var.get().strip(),
            "material_text": self.primary_source_material_text_var.get().strip(),
            "text_style_text": self.primary_source_text_style_text_var.get().strip(),
            "found_text": self.primary_source_found_text_var.get().strip(),
            "classification_text": self.primary_source_classification_text_var.get().strip(),
            "current_location_text": self.primary_source_current_location_text_var.get().strip(),
        }
        try:
            with self.connection:
                if any(localized_values.values()):
                    self.connection.execute(
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
                    self.connection.execute(
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

        self._load_primary_sources()
        self._select_primary_source_by_id(source_id)
        self._set_status(f"Первоисточник '{source_id}' сохранен.")

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

    def _open_primary_sources_root_dir(self) -> None:
        root = self._primary_sources_root_dir()
        try:
            root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Ошибка", f"Не удалось создать папку:\n{exc}", parent=self)
            return
        webbrowser.open(root.resolve().as_uri())

    def _link_dialog_payload(self, initial: dict[str, object] | None = None) -> dict[str, object] | None:
        return self._show_form_dialog(
            "Ссылка первоисточника",
            [
                FormFieldSpec("link_id", "Link ID"),
                FormFieldSpec("sort_order", "Sort order"),
                FormFieldSpec(
                    "link_role",
                    "Role",
                    kind="combo",
                    options=("wikipedia", "intf", "image_source", "external"),
                ),
                FormFieldSpec("url", "URL", width=70),
                FormFieldSpec(
                    "localized_title",
                    f"Локализованный title ({self._current_primary_source_lang() or '-'})",
                ),
            ],
            initial=initial,
        )

    def _add_primary_source_link(self) -> None:
        if not self._ensure_primary_source_section_ready():
            return
        source_id = self.selected_primary_source_id
        if not source_id:
            messagebox.showinfo("Нет источника", "Сначала выберите первоисточник.", parent=self)
            return
        payload = self._link_dialog_payload(
            {
                "sort_order": str((max((int(row["sort_order"] or 0) for row in self.primary_source_link_rows), default=-10) + 10)),
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
        localized_titles = self._current_primary_source_link_titles()
        payload = self._link_dialog_payload(
            {
                "link_id": row["link_id"],
                "sort_order": str(int(row["sort_order"] or 0)),
                "link_role": row["link_role"],
                "url": row["url"],
                "localized_title": localized_titles.get(row["link_id"], ""),
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
        if not link_id or not url:
            messagebox.showwarning("Ошибка", "Link ID и URL обязательны.", parent=self)
            return
        try:
            sort_order = self._parse_required_int(payload["sort_order"], "Sort order")
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
            localized_title = str(payload.get("localized_title", "")).strip()
            with self.connection:
                if localized_title:
                    self.connection.execute(
                        """
                        INSERT OR REPLACE INTO primary_source_link_texts(source_id, link_id, title)
                        VALUES(?, ?, ?)
                        """,
                        (source_id, link_id, localized_title),
                    )
                else:
                    self.connection.execute(
                        "DELETE FROM primary_source_link_texts WHERE source_id = ? AND link_id = ?",
                        (source_id, link_id),
                    )
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
                FormFieldSpec("attribution_id", "Attribution ID"),
                FormFieldSpec("sort_order", "Sort order"),
                FormFieldSpec("text", "Text", width=70),
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
                "sort_order": str(
                    max((int(row["sort_order"] or 0) for row in self.primary_source_attribution_rows), default=-10) + 10
                ),
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
            messagebox.showwarning("Ошибка", "Attribution ID и Text обязательны.", parent=self)
            return
        try:
            sort_order = self._parse_required_int(payload["sort_order"], "Sort order")
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
            messagebox.showwarning("Дубликат", f"Attribution ID '{attribution_id}' уже существует.", parent=self)
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
                FormFieldSpec("page_name", "Page name"),
                FormFieldSpec("sort_order", "Sort order"),
                FormFieldSpec("content_ref", "Content ref"),
                FormFieldSpec("image_path", "Image path", width=70),
                FormFieldSpec("mobile_image_path", "Mobile image path", width=70),
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
                "mobile_image_path": row.mobile_image_path,
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
        mobile_image_path = str(payload["mobile_image_path"]).strip().replace("\\", "/")
        if not page_name or not content_ref:
            messagebox.showwarning("Ошибка", "Page name и Content ref обязательны.", parent=self)
            return
        try:
            sort_order = self._parse_required_int(payload["sort_order"], "Sort order")
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
                      image_path,
                      mobile_image_path
                    )
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source_id,
                        page_name,
                        sort_order,
                        content_ref,
                        image_path,
                        mobile_image_path or None,
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

    def _open_selected_primary_source_contour_editor(self) -> None:
        if Image is None or ImageTk is None:
            messagebox.showwarning(
                "Нет Pillow",
                "Для contour editor нужен Pillow: pip install pillow",
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
            selected = filedialog.askopenfilename(
                parent=self,
                title="Выберите локальный файл страницы для contour editor",
                initialdir=str(image_path.parent if image_path.parent.exists() else self._primary_sources_root_dir()),
                filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff"), ("All files", "*.*")],
            )
            if not selected:
                messagebox.showinfo(
                    "Нет изображения",
                    (
                        "Локальный image_path страницы не найден.\n"
                        "Откройте файл вручную или скачайте страницу кнопкой из раздела первоисточников."
                    ),
                    parent=self,
                )
                return
            image_path = Path(selected)

        verse_row = self._selected_primary_source_verse_row()
        if verse_row is None:
            next_verse_index = max((int(row["verse_index"] or 0) for row in self.primary_source_verse_rows), default=-1) + 1
            initial_payload = {
                "verse_index": next_verse_index,
                "chapter_number": 1,
                "verse_number": 1,
                "label_x": 0.0,
                "label_y": 0.0,
                "word_indexes": [],
                "contours": [],
            }
            previous_verse_index = None
        else:
            initial_payload = {
                "verse_index": int(verse_row["verse_index"] or 0),
                "chapter_number": int(verse_row["chapter_number"] or 0),
                "verse_number": int(verse_row["verse_number"] or 0),
                "label_x": float(verse_row["label_x"] or 0.0),
                "label_y": float(verse_row["label_y"] or 0.0),
                "word_indexes": self._safe_json_loads(verse_row["word_indexes_json"] or "[]", []),
                "contours": self._safe_json_loads(verse_row["contours_json"] or "[]", []),
            }
            previous_verse_index = int(verse_row["verse_index"] or 0)

        PrimarySourceContourEditorDialog(
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

    def _word_dialog_payload(self, initial: dict[str, object] | None = None) -> dict[str, object] | None:
        return self._show_form_dialog(
            "Слово страницы",
            [
                FormFieldSpec("word_index", "Word index"),
                FormFieldSpec("text", "Text", width=50),
                FormFieldSpec("strong_number", "Strong number"),
                FormFieldSpec("strong_pronounce", "Strong pronounce", kind="check"),
                FormFieldSpec("strong_x_shift", "Strong X shift"),
                FormFieldSpec("missing_char_indexes_json", "Missing char indexes JSON", kind="text", height=3),
                FormFieldSpec("rectangles_json", "Rectangles JSON", kind="text", height=5),
            ],
            initial=initial,
        )

    def _add_primary_source_word(self) -> None:
        if not self._ensure_primary_source_section_ready():
            return
        if not self.selected_primary_source_page_name:
            messagebox.showinfo("Нет страницы", "Сначала выберите страницу.", parent=self)
            return
        payload = self._word_dialog_payload(
            {
                "word_index": str(
                    max((int(row["word_index"] or 0) for row in self.primary_source_word_rows), default=-1) + 1
                ),
                "strong_pronounce": False,
                "strong_x_shift": "0.0",
                "missing_char_indexes_json": "[]",
                "rectangles_json": "[]",
            }
        )
        if payload is None:
            return
        self._save_primary_source_word_record(payload, previous_word_index=None)

    def _edit_primary_source_word(self) -> None:
        row = self._selected_primary_source_word_row()
        if row is None:
            return
        payload = self._word_dialog_payload(
            {
                "word_index": str(int(row["word_index"] or 0)),
                "text": row["text"] or "",
                "strong_number": "" if row["strong_number"] is None else str(row["strong_number"]),
                "strong_pronounce": bool(row["strong_pronounce"]),
                "strong_x_shift": str(float(row["strong_x_shift"] or 0.0)),
                "missing_char_indexes_json": row["missing_char_indexes_json"] or "[]",
                "rectangles_json": row["rectangles_json"] or "[]",
            }
        )
        if payload is None:
            return
        self._save_primary_source_word_record(
            payload,
            previous_word_index=int(row["word_index"] or 0),
        )

    def _save_primary_source_word_record(
        self,
        payload: dict[str, object],
        *,
        previous_word_index: int | None,
    ) -> None:
        source_id = self.selected_primary_source_id
        page_name = self.selected_primary_source_page_name
        if not source_id or not page_name or self.common_connection is None:
            return
        text = str(payload["text"]).strip()
        if not text:
            messagebox.showwarning("Ошибка", "Text обязателен.", parent=self)
            return
        try:
            word_index = self._parse_required_int(payload["word_index"], "Word index")
            strong_number = self._parse_optional_int(payload["strong_number"])
            strong_x_shift = self._parse_required_float(payload["strong_x_shift"], "Strong X shift")
            self._parse_json_list(payload["missing_char_indexes_json"], "Missing char indexes JSON")
            self._parse_json_list(payload["rectangles_json"], "Rectangles JSON")
        except ValueError as exc:
            messagebox.showwarning("Ошибка данных", str(exc), parent=self)
            return

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
            return

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
                        json.dumps(
                            self._parse_json_list(payload["missing_char_indexes_json"], "Missing char indexes JSON"),
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            self._parse_json_list(payload["rectangles_json"], "Rectangles JSON"),
                            ensure_ascii=False,
                        ),
                    ),
                )
        except sqlite3.DatabaseError as exc:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить слово:\n{exc}", parent=self)
            return
        self._load_primary_source_page_children()
        self._refresh_primary_source_validation()
        self._set_status(f"Слово #{word_index} сохранено.")

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

    def _verse_dialog_payload(self, initial: dict[str, object] | None = None) -> dict[str, object] | None:
        return self._show_form_dialog(
            "Verse / contour row",
            [
                FormFieldSpec("verse_index", "Verse index"),
                FormFieldSpec("chapter_number", "Chapter number"),
                FormFieldSpec("verse_number", "Verse number"),
                FormFieldSpec("label_x", "Label X"),
                FormFieldSpec("label_y", "Label Y"),
                FormFieldSpec("word_indexes_json", "Word indexes JSON", kind="text", height=3),
                FormFieldSpec("contours_json", "Contours JSON", kind="text", height=6),
            ],
            initial=initial,
        )

    def _add_primary_source_verse(self) -> None:
        if not self._ensure_primary_source_section_ready():
            return
        if not self.selected_primary_source_page_name:
            messagebox.showinfo("Нет страницы", "Сначала выберите страницу.", parent=self)
            return
        payload = self._verse_dialog_payload(
            {
                "verse_index": str(
                    max((int(row["verse_index"] or 0) for row in self.primary_source_verse_rows), default=-1) + 1
                ),
                "chapter_number": "1",
                "verse_number": "1",
                "label_x": "0.0",
                "label_y": "0.0",
                "word_indexes_json": "[]",
                "contours_json": "[]",
            }
        )
        if payload is None:
            return
        self._save_primary_source_verse_record(payload, previous_verse_index=None)

    def _edit_primary_source_verse(self) -> None:
        row = self._selected_primary_source_verse_row()
        if row is None:
            return
        payload = self._verse_dialog_payload(
            {
                "verse_index": str(int(row["verse_index"] or 0)),
                "chapter_number": str(int(row["chapter_number"] or 0)),
                "verse_number": str(int(row["verse_number"] or 0)),
                "label_x": str(float(row["label_x"] or 0.0)),
                "label_y": str(float(row["label_y"] or 0.0)),
                "word_indexes_json": row["word_indexes_json"] or "[]",
                "contours_json": row["contours_json"] or "[]",
            }
        )
        if payload is None:
            return
        self._save_primary_source_verse_record(
            payload,
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


class PrimarySourceContourEditorDialog(tk.Toplevel):
    def __init__(
        self,
        *,
        parent: TopicContentTool,
        image_path: Path,
        source_id: str,
        page_name: str,
        initial_payload: dict[str, object],
        previous_verse_index: int | None,
        on_save: Callable[[dict[str, object], int | None], bool],
    ) -> None:
        super().__init__(parent)
        self.parent_tool = parent
        self.source_id = source_id
        self.page_name = page_name
        self.start_dir = image_path.parent
        self.on_save = on_save
        self.previous_verse_index = previous_verse_index

        self.title(f"Contour Editor - {source_id} / {page_name}")
        self.geometry("1380x900")
        self.minsize(1040, 720)
        self.transient(parent)
        self.grab_set()

        self.mode = tk.StringVar(value="add")
        self.snap_axis = tk.BooleanVar(value=True)
        self.verse_index_var = tk.IntVar(value=int(initial_payload.get("verse_index") or 0))
        self.chapter = tk.IntVar(value=int(initial_payload.get("chapter_number") or 1))
        self.verse = tk.IntVar(value=int(initial_payload.get("verse_number") or 1))
        self.word_indexes = tk.StringVar(
            value=format_indexes_for_ui([int(v) for v in initial_payload.get("word_indexes", [])])
        )
        self.label_text = tk.StringVar(value="label: not set")
        self.status = tk.StringVar(value="Open image and draw contours.")

        self.image_path: Path | None = None
        self.image: Image.Image | None = None
        self.image_size = (0, 0)
        self.tk_image: ImageTk.PhotoImage | None = None
        self.image_cache_key: tuple[str, int, int] | None = None

        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 9.0
        self.pan_x = 16.0
        self.pan_y = 16.0

        initial_contours = initial_payload.get("contours", [])
        self.contours: list[list[Point]] = []
        for contour in initial_contours if isinstance(initial_contours, list) else []:
            points: list[Point] = []
            if isinstance(contour, list):
                for point in contour:
                    if not isinstance(point, (list, tuple)) or len(point) != 2:
                        continue
                    points.append((clamp01(float(point[0])), clamp01(float(point[1]))))
            if points:
                self.contours.append(points)
        if not self.contours:
            self.contours = [[]]
        self.active_contour = 0
        self.drag_point: tuple[int, int] | None = None
        self.wait_label_pick = False
        self.label_position: Point | None = None
        if "label_x" in initial_payload and "label_y" in initial_payload:
            self.label_position = (
                clamp01(float(initial_payload["label_x"])),
                clamp01(float(initial_payload["label_y"])),
            )
        elif self.contours and self.contours[0]:
            self.label_position = self.contours[0][0]
        self.panning = False
        self.pan_start = (0.0, 0.0)
        self.pan_base = (0.0, 0.0)

        self._build_ui()
        self._bind_events()
        self._refresh_label_text()
        self._refresh_contour_info()
        self.load_image(image_path)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=8)
        top.grid(row=0, column=0, sticky="ew")

        ttk.Label(
            top,
            text=f"{self.source_id} / {self.page_name}",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Button(top, text="Open Image", command=self.open_image).grid(row=0, column=1, padx=2)
        ttk.Button(top, text="Save to DB", command=self.save_to_db).grid(row=0, column=2, padx=(10, 2))
        ttk.Button(top, text="Close", command=self.destroy).grid(row=0, column=3, padx=(2, 10))
        ttk.Button(top, text="New Contour", command=self.new_contour).grid(row=0, column=4, padx=2)
        ttk.Button(top, text="Clear Contour", command=self.clear_contour).grid(row=0, column=5, padx=2)
        ttk.Button(top, text="Delete Contour", command=self.delete_contour).grid(row=0, column=6, padx=2)
        ttk.Button(top, text="Pick Label", command=self.pick_label).grid(row=0, column=7, padx=8)
        ttk.Button(top, text="Copy Contours", command=self.copy_contours).grid(row=0, column=8, padx=2)
        ttk.Button(top, text="Copy Verse", command=self.copy_verse).grid(row=0, column=9, padx=2)
        ttk.Button(top, text="Import Verse", command=self.import_verse_dialog).grid(row=0, column=10, padx=2)
        ttk.Checkbutton(top, text="Snap axis", variable=self.snap_axis).grid(row=0, column=11, padx=8)

        mode_frame = ttk.Frame(top)
        mode_frame.grid(row=0, column=12, padx=8)
        ttk.Label(mode_frame, text="Mode:").grid(row=0, column=0, padx=(0, 4))
        for col, (title, value) in enumerate([("Add", "add"), ("Move", "move"), ("Delete", "delete")], start=1):
            ttk.Radiobutton(mode_frame, text=title, value=value, variable=self.mode).grid(
                row=0,
                column=col,
                padx=2,
            )

        meta = ttk.Frame(top)
        meta.grid(row=1, column=0, columnspan=13, sticky="ew", pady=(8, 0))
        ttk.Label(meta, text="Verse index").grid(row=0, column=0, padx=(0, 4))
        ttk.Spinbox(meta, from_=0, to=9999, textvariable=self.verse_index_var, width=6).grid(row=0, column=1)
        ttk.Label(meta, text="Chapter").grid(row=0, column=2, padx=(10, 4))
        ttk.Spinbox(meta, from_=1, to=999, textvariable=self.chapter, width=5).grid(row=0, column=3)
        ttk.Label(meta, text="Verse").grid(row=0, column=4, padx=(8, 4))
        ttk.Spinbox(meta, from_=1, to=999, textvariable=self.verse, width=5).grid(row=0, column=5)
        ttk.Label(meta, text="Indexes").grid(row=0, column=6, padx=(8, 4))
        ttk.Entry(meta, textvariable=self.word_indexes, width=56).grid(row=0, column=7, sticky="ew")
        ttk.Label(meta, textvariable=self.label_text).grid(row=0, column=8, padx=(10, 0), sticky="w")

        self.canvas = tk.Canvas(self, bg="#1f1f1f", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        ttk.Label(self, textvariable=self.status, anchor="w", padding=(8, 4)).grid(row=2, column=0, sticky="ew")

    def _bind_events(self) -> None:
        self.canvas.bind("<Configure>", lambda _e: self.redraw())
        self.canvas.bind("<Button-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda _e: setattr(self, "drag_point", None))
        self.canvas.bind("<ButtonPress-3>", self.on_pan_start)
        self.canvas.bind("<B3-Motion>", self.on_pan_drag)
        self.canvas.bind("<ButtonRelease-3>", lambda _e: setattr(self, "panning", False))
        self.canvas.bind("<MouseWheel>", self.on_wheel_win)
        self.canvas.bind("<Button-4>", self.on_wheel_linux)
        self.canvas.bind("<Button-5>", self.on_wheel_linux)
        self.canvas.bind("<Motion>", self.on_motion)
        self.bind("<Control-o>", lambda _e: self.open_image())
        self.bind("<Control-s>", lambda _e: self.save_to_db())
        self.bind("<Control-c>", lambda _e: self.copy_contours())
        self.bind("<Control-i>", lambda _e: self.import_verse_dialog())

    def open_image(self) -> None:
        init = self.start_dir if self.start_dir.exists() else Path.cwd()
        file_path = filedialog.askopenfilename(
            parent=self,
            initialdir=str(init),
            title="Open image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff"), ("All files", "*.*")],
        )
        if file_path:
            self.load_image(Path(file_path))

    def load_image(self, path: Path) -> None:
        self.image = Image.open(path).convert("RGB")
        self.image_path = path
        self.image_size = self.image.size
        self.image_cache_key = None
        self.start_dir = path.parent
        self.status.set(f"Loaded: {path.name}")
        self.after(40, self.fit_view)

    def fit_view(self) -> None:
        if self.image is None:
            self.redraw()
            return
        cw, ch = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        iw, ih = self.image_size
        if cw <= 1 or ch <= 1:
            self.after(30, self.fit_view)
            return
        self.zoom = max(self.min_zoom, min(self.max_zoom, min((cw - 30) / iw, (ch - 30) / ih)))
        self.pan_x = (cw - iw * self.zoom) / 2
        self.pan_y = (ch - ih * self.zoom) / 2
        self.redraw()

    def rel_to_canvas(self, point: Point) -> Point:
        iw, ih = self.image_size
        return (self.pan_x + point[0] * iw * self.zoom, self.pan_y + point[1] * ih * self.zoom)

    def canvas_to_rel(self, x: float, y: float) -> Point | None:
        if self.image is None:
            return None
        iw, ih = self.image_size
        ix = (x - self.pan_x) / self.zoom
        iy = (y - self.pan_y) / self.zoom
        if ix < 0 or iy < 0 or ix > iw or iy > ih:
            return None
        return (clamp01(ix / iw), clamp01(iy / ih))

    def nearest_point(self, x: float, y: float) -> tuple[int, int] | None:
        best: tuple[int, int] | None = None
        best_d2 = 12 * 12
        for ci, contour in enumerate(self.contours):
            for pi, point in enumerate(contour):
                px, py = self.rel_to_canvas(point)
                d2 = (px - x) ** 2 + (py - y) ** 2
                if d2 <= best_d2:
                    best, best_d2 = (ci, pi), d2
        return best

    def on_left_down(self, event: tk.Event[tk.Misc]) -> None:
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            return
        if self.wait_label_pick:
            self.wait_label_pick = False
            self.label_position = rel
            self._refresh_label_text()
            self.redraw()
            return
        mode = self.mode.get()
        if mode == "add":
            contour = self.contours[self.active_contour]
            if contour and self.snap_axis.get():
                px, py = contour[-1]
                dx, dy = abs(rel[0] - px), abs(rel[1] - py)
                rel = (px, rel[1]) if dx < dy else (rel[0], py)
            contour.append(rel)
            self._refresh_contour_info()
            self.redraw()
            return
        near = self.nearest_point(event.x, event.y)
        if near is None:
            return
        ci, pi = near
        if mode == "move":
            self.active_contour = ci
            self.drag_point = (ci, pi)
            self._refresh_contour_info()
        elif mode == "delete":
            self.contours[ci].pop(pi)
            self._refresh_contour_info()
            self.redraw()

    def on_left_drag(self, event: tk.Event[tk.Misc]) -> None:
        if self.drag_point is None:
            return
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            return
        ci, pi = self.drag_point
        self.contours[ci][pi] = rel
        self.redraw()

    def on_pan_start(self, event: tk.Event[tk.Misc]) -> None:
        self.panning = True
        self.pan_start = (event.x, event.y)
        self.pan_base = (self.pan_x, self.pan_y)

    def on_pan_drag(self, event: tk.Event[tk.Misc]) -> None:
        if not self.panning:
            return
        self.pan_x = self.pan_base[0] + (event.x - self.pan_start[0])
        self.pan_y = self.pan_base[1] + (event.y - self.pan_start[1])
        self.redraw()

    def on_wheel_win(self, event: tk.Event[tk.Misc]) -> None:
        self.zoom_at(event.x, event.y, 1.1 if event.delta > 0 else 1 / 1.1)

    def on_wheel_linux(self, event: tk.Event[tk.Misc]) -> None:
        self.zoom_at(event.x, event.y, 1.1 if event.num == 4 else 1 / 1.1)

    def zoom_at(self, x: float, y: float, factor: float) -> None:
        if self.image is None:
            return
        old_zoom = self.zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))
        if abs(self.zoom - old_zoom) < 1e-8:
            return
        self.pan_x = x - (x - self.pan_x) * (self.zoom / old_zoom)
        self.pan_y = y - (y - self.pan_y) * (self.zoom / old_zoom)
        self.redraw()

    def on_motion(self, event: tk.Event[tk.Misc]) -> None:
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            self.status.set(f"mode={self.mode.get()}  zoom={self.zoom:.2f}x  outside image")
            return
        self.status.set(f"mode={self.mode.get()}  zoom={self.zoom:.2f}x  rel=({rel[0]:.4f}, {rel[1]:.4f})")

    def new_contour(self) -> None:
        self.contours.append([])
        self.active_contour = len(self.contours) - 1
        self._refresh_contour_info()
        self.redraw()

    def clear_contour(self) -> None:
        self.contours[self.active_contour].clear()
        self._refresh_contour_info()
        self.redraw()

    def delete_contour(self) -> None:
        if len(self.contours) <= 1:
            self.contours[0].clear()
        else:
            self.contours.pop(self.active_contour)
            self.active_contour = max(0, self.active_contour - 1)
        self._refresh_contour_info()
        self.redraw()

    def pick_label(self) -> None:
        self.wait_label_pick = True
        self.status.set("Click image to place verse label.")

    def import_verse_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Import Verse(...)")
        dialog.geometry("900x560")
        dialog.minsize(700, 420)
        dialog.transient(self)
        dialog.grab_set()

        container = ttk.Frame(dialog, padding=8)
        container.pack(fill="both", expand=True)
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        ttk.Label(
            container,
            text=(
                "Paste Verse(...) block from the legacy primary sources snapshot.\n"
                "Expected fields: chapterNumber, verseNumber, labelPosition, wordIndexes, contours."
            ),
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        text = tk.Text(container, wrap="none")
        text.grid(row=1, column=0, sticky="nsew", pady=(8, 8))

        y_scroll = ttk.Scrollbar(container, orient="vertical", command=text.yview)
        y_scroll.grid(row=1, column=1, sticky="ns", pady=(8, 8))
        text.configure(yscrollcommand=y_scroll.set)

        try:
            clip = self.clipboard_get()
            if isinstance(clip, str) and "Verse(" in clip:
                text.insert("1.0", clip)
        except tk.TclError:
            pass

        buttons = ttk.Frame(container)
        buttons.grid(row=2, column=0, sticky="e")

        def do_import() -> None:
            raw = text.get("1.0", "end").strip()
            if not raw:
                messagebox.showwarning("Import Verse", "Paste Verse(...) first.", parent=dialog)
                return
            try:
                payload = parse_verse_snippet(raw)
                self.apply_imported_verse(payload)
            except Exception as exc:
                messagebox.showerror("Import Verse", f"Failed to parse snippet:\n{exc}", parent=dialog)
                return
            dialog.destroy()

        ttk.Button(buttons, text="Import", command=do_import).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).grid(row=0, column=1)

        text.focus_set()
        self.wait_window(dialog)

    def apply_imported_verse(self, payload: dict[str, object]) -> None:
        chapter = int(payload["chapter"])
        verse = int(payload["verse"])
        indexes = [int(v) for v in payload.get("word_indexes", [])]
        raw_contours = payload.get("contours", [])

        contours: list[list[Point]] = []
        for contour in raw_contours if isinstance(raw_contours, list) else []:
            points: list[Point] = []
            if isinstance(contour, list):
                for x, y in contour:
                    points.append((clamp01(float(x)), clamp01(float(y))))
            if points:
                contours.append(points)
        if not contours:
            raise ValueError("Imported verse has no contours.")

        self.chapter.set(chapter)
        self.verse.set(verse)
        self.word_indexes.set(format_indexes_for_ui(indexes))
        self.contours = contours
        self.active_contour = 0
        self.drag_point = None

        label = payload.get("label")
        if label is None:
            label = contours[0][0]
        self.label_position = (clamp01(float(label[0])), clamp01(float(label[1])))
        self._refresh_label_text()
        self._refresh_contour_info()
        self.redraw()
        self.status.set(f"Imported Verse {chapter}:{verse} with {len(contours)} contour(s).")

    def _refresh_label_text(self) -> None:
        if self.label_position is None:
            self.label_text.set("label: not set")
            return
        self.label_text.set(f"label: Offset({self.label_position[0]:.4f}, {self.label_position[1]:.4f})")

    def _refresh_contour_info(self) -> None:
        if not self.contours:
            self.contours = [[]]
            self.active_contour = 0
        summary = ", ".join(f"{index + 1}:{len(contour)}" for index, contour in enumerate(self.contours))
        self.status.set(f"Contours points count [{summary}] | active={self.active_contour + 1}")

    def redraw(self) -> None:
        self.canvas.delete("all")
        if self.image is None:
            self.canvas.create_text(
                self.canvas.winfo_width() / 2,
                self.canvas.winfo_height() / 2,
                text="Open image",
                fill="#ccc",
            )
            return
        iw, ih = self.image_size
        dw, dh = max(1, int(iw * self.zoom)), max(1, int(ih * self.zoom))
        cache_key = (str(self.image_path), dw, dh)
        if cache_key != self.image_cache_key:
            resampling = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
            self.tk_image = ImageTk.PhotoImage(self.image.resize((dw, dh), resampling))
            self.image_cache_key = cache_key
        self.canvas.create_image(self.pan_x, self.pan_y, image=self.tk_image, anchor="nw")
        for contour_index, contour in enumerate(self.contours):
            if len(contour) < 1:
                continue
            color = "#00a06f" if contour_index == self.active_contour else "#0b8561"
            pts = [self.rel_to_canvas(point) for point in contour]
            if len(pts) >= 2:
                flat = [xy for point in pts for xy in point]
                self.canvas.create_line(*flat, fill=color, width=3 if contour_index == self.active_contour else 2)
                if len(pts) >= 3 and contour[0] != contour[-1]:
                    self.canvas.create_line(*pts[-1], *pts[0], fill=color, width=2, dash=(4, 4))
            for point_index, (x, y) in enumerate(pts):
                radius = 4 if contour_index == self.active_contour else 3
                self.canvas.create_oval(
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                    fill="#0b5f47",
                    outline="",
                )
                if contour_index == self.active_contour:
                    self.canvas.create_text(
                        x + 8,
                        y - 8,
                        text=str(point_index),
                        fill="#0b5f47",
                        anchor="sw",
                        font=("Segoe UI", 8),
                    )
        if self.label_position:
            lx, ly = self.rel_to_canvas(self.label_position)
            self.canvas.create_rectangle(lx - 5, ly - 5, lx + 5, ly + 5, outline="#ffe066", width=2)
            self.canvas.create_text(
                lx + 9,
                ly,
                text=f"{self.chapter.get()}:{self.verse.get()}",
                fill="#ffe066",
                anchor="w",
                font=("Segoe UI", 11, "bold"),
            )

    def filtered_contours(self) -> list[list[Point]]:
        result: list[list[Point]] = []
        for contour in self.contours:
            points = contour[:-1] if len(contour) >= 2 and contour[0] == contour[-1] else contour
            if len(points) >= 3:
                result.append(points)
        return result

    def copy_contours(self) -> None:
        contours = self.filtered_contours()
        if not contours:
            messagebox.showwarning("Copy", "Need at least one contour with 3+ points.", parent=self)
            return
        lines = ["contours: const ["]
        for contour in contours:
            lines.append("  [")
            for x, y in contour:
                lines.append(f"    Offset({x:.4f}, {y:.4f}),")
            lines.append("  ],")
        lines.append("],")
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.status.set("Copied contours to clipboard.")

    def copy_verse(self) -> None:
        contours = self.filtered_contours()
        if not contours:
            messagebox.showwarning("Copy", "Need at least one contour with 3+ points.", parent=self)
            return
        try:
            indexes = parse_indexes(self.word_indexes.get())
        except Exception as exc:
            messagebox.showerror("Indexes", str(exc), parent=self)
            return
        label = self.label_position or contours[0][0]
        lines = [
            "Verse(",
            f"  chapterNumber: {self.chapter.get()},",
            f"  verseNumber: {self.verse.get()},",
            f"  labelPosition: Offset({label[0]:.4f}, {label[1]:.4f}),",
            "  wordIndexes: [",
        ]
        for index in indexes:
            lines.append(f"    {index},")
        lines.extend(["  ],", "  contours: const ["])
        for contour in contours:
            lines.append("    [")
            for x, y in contour:
                lines.append(f"      Offset({x:.4f}, {y:.4f}),")
            lines.append("    ],")
        lines.extend(["  ],", "),"])
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.status.set("Copied Verse(...) to clipboard.")

    def save_to_db(self) -> None:
        contours = self.filtered_contours()
        if not contours:
            messagebox.showwarning("Save", "Need at least one contour with 3+ points.", parent=self)
            return
        try:
            word_indexes = parse_indexes(self.word_indexes.get())
        except Exception as exc:
            messagebox.showerror("Indexes", str(exc), parent=self)
            return
        label = self.label_position or contours[0][0]
        payload = {
            "verse_index": str(int(self.verse_index_var.get())),
            "chapter_number": str(int(self.chapter.get())),
            "verse_number": str(int(self.verse.get())),
            "label_x": f"{label[0]:.4f}",
            "label_y": f"{label[1]:.4f}",
            "word_indexes_json": json.dumps(word_indexes, ensure_ascii=False),
            "contours_json": json.dumps(contours, ensure_ascii=False),
        }
        if self.on_save(payload, self.previous_verse_index):
            self.previous_verse_index = int(self.verse_index_var.get())
            self.status.set(
                f"Saved to DB: verse_index={self.previous_verse_index} for {self.source_id}/{self.page_name}"
            )


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
