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

        self.topics: list[TopicRow] = []
        self.topic_texts: list[TopicTextRow] = []
        self.common_resources: list[ResourceRow] = []
        self.strong_rows: list[StrongRow] = []
        self.strong_filtered_indices: list[int] = []
        self.selected_topic_index: int | None = None
        self.selected_text_index: int | None = None
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
        self.future_local_db_var = tk.StringVar(value="-")
        self.future_common_db_var = tk.StringVar(value="-")

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

        self._build_ui()
        self._install_global_text_shortcuts()
        self.strong_filter_var.trace_add("write", self._on_strong_filter_changed)
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
        self._build_future_section(
            self.sources_section,
            "Раздел «Первоисточники» скоро будет доступен.",
        )
        self._build_future_section(
            self.bibles_section,
            "Раздел «Библии» скоро будет доступен.",
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

        self.article_sections = ttk.Notebook(parent)
        self.article_sections.grid(row=1, column=0, sticky="nsew")

        self.topics_tab = ttk.Frame(self.article_sections)
        self.texts_tab = ttk.Frame(self.article_sections)
        self.article_sections.add(self.topics_tab, text="Статьи главного окна")
        self.article_sections.add(self.texts_tab, text="Все статьи")

        self._build_topics_tab(self.topics_tab)
        self._build_texts_tab(self.texts_tab)

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

    def _build_future_section(self, parent: ttk.Frame, message: str) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        top = ttk.Frame(parent, padding=(8, 8, 8, 0))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)
        top.columnconfigure(3, weight=1)

        ttk.Label(top, text="Локализованная БД:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(top, textvariable=self.future_local_db_var, anchor="w").grid(row=0, column=1, sticky="ew")
        ttk.Label(top, text="Общая БД:").grid(row=0, column=2, sticky="w", padx=(16, 8))
        ttk.Label(top, textvariable=self.future_common_db_var, anchor="w").grid(row=0, column=3, sticky="ew")

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
        self.future_local_db_var.set(local_text)
        self.strong_local_db_var.set(local_text)

        common_text = "-"
        if self.common_db_path is not None:
            common_text = self.common_db_path.stem
        self.future_common_db_var.set(common_text)
        self.resources_db_var.set(common_text)
        self.strong_common_db_var.set(common_text)
        languages = [lang for lang, _ in self._localized_db_entries()]
        self.strong_languages_var.set(", ".join(languages) if languages else "-")

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

    def _new_split_pane(self, parent: tk.Misc) -> tk.PanedWindow:
        pane = tk.PanedWindow(
            parent,
            orient=tk.HORIZONTAL,
            sashwidth=8,
            sashrelief="raised",
            showhandle=True,
            relief="groove",
            bd=1,
            opaqueresize=True,
        )
        try:
            pane.configure(sashcursor="sb_h_double_arrow", handlesize=8, handlepad=2, sashpad=2)
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
    ) -> None:
        localized_widgets: list[tuple[tk.Widget, bool]] = [
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

    def _update_ui_availability(self) -> None:
        has_loaded_db = self.connection is not None and self.current_db_path is not None
        has_common_db = self.common_connection is not None and self.common_db_path is not None
        self.db_combo.configure(state="readonly" if self.db_files else "disabled")
        self.btn_publish.state(["!disabled"])
        self._set_editor_controls_enabled(
            localized_enabled=has_loaded_db,
            resources_enabled=has_common_db,
            strong_enabled=has_common_db,
        )

    def _build_topics_tab(self, parent: ttk.Frame) -> None:
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
            **self._button_kwargs("save", "Сохранить"),
            command=self._apply_topic_changes,
        )
        self.btn_apply_topic.pack(side="left")
        self.btn_cancel_topic = ttk.Button(
            topic_actions,
            **self._button_kwargs("cancel", "Отменить"),
            command=self._reload_selected_topic,
        )
        self.btn_cancel_topic.pack(side="left", padx=(8, 0))

    def _build_texts_tab(self, parent: ttk.Frame) -> None:
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
            **self._button_kwargs("save", "Сохранить"),
            command=self._apply_text_changes,
        )
        self.btn_apply_text.pack(side="left")
        self.btn_cancel_text = ttk.Button(
            text_actions,
            **self._button_kwargs("cancel", "Отменить"),
            command=self._reload_selected_text,
        )
        self.btn_cancel_text.pack(side="left", padx=(8, 0))

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
        self._load_strong_rows()
        self._refresh_topics_tree()
        self._refresh_texts_list()
        self._refresh_topic_route_options()
        self._refresh_topic_icon_options()
        self._clear_topic_editor()
        self._clear_text_editor()
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
        self._refresh_topic_icon_options()

    def _clear_local_views(self) -> None:
        self.topics.clear()
        self.topic_texts.clear()
        self._refresh_topics_tree()
        self._refresh_texts_list()
        self._clear_topic_editor()
        self._clear_text_editor()
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
        was_disabled = str(self.texts_list.cget("state")) == "disabled"
        if was_disabled:
            self.texts_list.configure(state="normal")
        self.texts_list.delete(0, tk.END)
        for row in self.topic_texts:
            self.texts_list.insert(tk.END, row.route)
        if was_disabled:
            self.texts_list.configure(state="disabled")

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

    def _ask_topic_route_for_new_topic(self) -> str | None:
        used_routes = {row.route for row in self.topics if row.route.strip()}
        available_routes = sorted(
            {
                row.route
                for row in self.topic_texts
                if row.route.strip() and row.route not in used_routes
            }
        )
        if not available_routes:
            messagebox.showinfo(
                "Нет доступных статей",
                "Нет свободных маршрутов. Сначала добавьте статью во вкладке 'Все статьи'.",
                parent=self,
            )
            return None

        dialog = tk.Toplevel(self)
        dialog.title("Выбор статьи")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        container = ttk.Frame(dialog, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        ttk.Label(container, text="Выберите статью из списка:").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 6),
        )
        route_var = tk.StringVar(value=available_routes[0])
        route_combo = ttk.Combobox(
            container,
            textvariable=route_var,
            values=available_routes,
            state="readonly",
        )
        route_combo.grid(row=1, column=0, sticky="ew")

        result: dict[str, str | None] = {"route": None}

        def apply_selection() -> None:
            value = route_var.get().strip()
            if not value:
                return
            result["route"] = value
            dialog.destroy()

        def cancel_selection() -> None:
            dialog.destroy()

        actions = ttk.Frame(container)
        actions.grid(row=2, column=0, sticky="e", pady=(10, 0))
        ttk.Button(actions, text="Выбрать", command=apply_selection).pack(side="left")
        ttk.Button(actions, text="Отмена", command=cancel_selection).pack(side="left", padx=(8, 0))

        self._fit_and_center_toplevel(
            dialog,
            min_width=420,
            max_width=620,
            min_height=150,
            max_height=240,
        )
        dialog.protocol("WM_DELETE_WINDOW", cancel_selection)
        dialog.bind("<Escape>", lambda _e: cancel_selection())
        dialog.bind("<Return>", lambda _e: apply_selection())
        route_combo.focus_set()
        self.wait_window(dialog)
        return result["route"]

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
        topic_route: str | None = None,
        text_route: str | None = None,
    ) -> bool:
        if self._save_all(status_text=success_status):
            return True
        self._restore_local_rows_after_save_error()
        if topic_route is not None:
            self._select_topic_by_route(topic_route)
        if text_route is not None:
            self._select_text_by_route(text_route)
        return False

    def _add_topic(self) -> None:
        route = self._ask_topic_route_for_new_topic()
        if route is None:
            return
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
        self._save_articles_immediately(
            success_status=(
                "Статья с маршрутом "
                f"'{self._display_route_value(route)}' добавлена в список главного окна."
            ),
            topic_route=route,
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
        self._save_articles_immediately(
            success_status=(
                "Статья с маршрутом "
                f"'{self._display_route_value(row.route)}' удалена из списка главного окна."
            )
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
        self._save_articles_immediately(
            success_status=(
                "Изменения для статьи с маршрутом "
                f"'{self._display_route_value(route)}' сохранены."
            ),
            topic_route=route,
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
        self._save_articles_immediately(
            success_status=f"Статья с маршрутом '{route}' добавлена в общий список статей.",
            text_route=route,
        )

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
        self._save_articles_immediately(
            success_status=f"Статья с маршрутом '{row.route}' удалена из общего списка статей."
        )

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
        self._save_articles_immediately(
            success_status=f"Изменения для статьи с маршрутом '{route}' сохранены.",
            text_route=route,
        )

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
            for topic in self.topics:
                if topic.id_icon == old_key:
                    topic.id_icon = key
                    affected_topics += 1
        topics_sync_failed = False
        if affected_topics > 0:
            if self.selected_topic_index is not None:
                self._reload_selected_topic()
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
        for topic in self.topics:
            if topic.id_icon == row.key:
                topic.id_icon = ""
                affected_topics += 1
        topics_sync_failed = False
        if affected_topics > 0:
            if self.selected_topic_index is not None:
                self._reload_selected_topic()
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

    def _save_all(self, *, status_text: str | None = None, silent: bool = False) -> bool:
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
                        FROM topics
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
