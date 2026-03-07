from __future__ import annotations

import ast
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any

from .models import Point

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
