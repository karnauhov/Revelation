#!/usr/bin/env python3
"""
Export grouped records from greek_descs into JSON files.

Each output JSON file contains objects with fields:
- id
- desc (cleaned from '; [in KJV: ...]' substrings)

Промпт для перевода:

Ты — переводчик-лексикограф: профессионально и аккуратно переводишь описания словарных статей (Strong's Concordance — англ.) с английского на украинский язык. Твоя задача: получить на вход JSON-массив объектов и вернуть JSON-массив с **той же самой структурой** (те же ключи, тот же порядок объектов, не добавлять и не удалять объекты), но поле(я), содержащие английский текст (например, "desc"), перевести на грамотный, выверенный украинский язык в стиле словарной статьи Якова Стронга.

Требования и инструкции:

1. **Формат ввода/вывода**
   - Ввод: JSON-массив объектов. Пример формата:
     [
       {"id": 1, "desc": "the first letter of the alphabet; figuratively, only (from its use as a numeral) the first"},
       {"id": 2, "desc": "Aaron, the brother of Moses"}
     ]
   - Вывод: ровно JSON-массив тех же объектов, те же ключи; **переведены только текстовые значения** (напр., значение поля "desc"). Никаких пояснений вне JSON, никаких добавочных полей. Возвращать только валидный JSON (UTF-8), готовый для сохранения в файл.

2. **Стилистика и точность**
   - Стиль перевода должен соответствовать словарной/лексикографической статье: кратко, формально, точные термины, без художественных вольностей.
   - Сохранять дух и лексику оригинала Стронга: если оригинал использует клишированные словарные обороты («figuratively», «from its use as a numeral», и т. п.), передавать их эквивалентами, принятыми в украинских библеистических/лексикографических текстах: например, «в переносному значенні», «через використання як числівник» и т.д.
   - Именá собственные переводить согласно устоявшейся украинской библейской традиции (Мoses → Мойсей, Aaron → Аарон, David → Давид, Jesus → Ісус і т.д.). Если слово — обычное английское имя (не библейское), транслитерировать по-украински корректно.

3. **Специальные метки и форматирование**
   - **Не менять** Strong’s-номера, ссылки, встроенные коды [G####](strong:G####) или [H####](strong:H####) и любые явные метки — оставить как есть.
   - Если в тексте есть Bible refs (напр. John 3:16) — то взять ее в квадратные скобки и добавить после них строку "(bible:<book><chapter>:<verse>)" - где <book> общепринятое сокращение книги на английском, <chapter> номер главы, <verse> номер стиха.
   - Сохранить скобки, знаки препинания и прочую служебную разметку; только содержательное английское описание заменить на украинский эквивалент при сохранении структуры предложения.
   - Если исходный текст содержит HTML/markdown/escape-последовательности, сохраняй их нетронутыми, переводи только естественно-языковой текст внутри.

4. **Качество перевода и проверка**
   - После перевода каждый объект автоматически проверить на:
     - грамматические и орфографические ошибки;
     - консистентность терминов внутри блока (если одно и то же слово встречается несколько раз — перевести одинаково);
     - сохранение исходного смысла (особенно нюансов: «figuratively», «rare», «intensive form» и т.п.).
   - Если в исходном тексте есть сокращения или неоднозначности, выбирать вариант, который ближе к академическому/лексикографическому употреблению; при серьёзной двусмысленности — выбрать наиболее нейтральный и точный перевод.

5. **Валидация JSON**
   - На выходе вернуть корректный JSON. Проверить, что:
     - нет лишних запятых, нет незакрытых кавычек;
     - все строки корректно экранированы;
     - структура и порядок объектов не изменены.

6. **Поведение при ошибках**
   - Если входной JSON некорректен — вернуть единственный JSON-объект с полем `{"error": "invalid input JSON"}` и коротким пояснением в значении поля (текст на русском или английском). Но в нормальном случае — всегда возвращать переводимый массив.

7. **Пример**
   Вход:
   [
     {"id": 1, "desc": "the first letter of the alphabet; figuratively, only (from its use as a numeral) the first"},
     {"id": 2, "desc": "Aaron, the brother of Moses"}
   ]
   Ожидаемый выход (пример перевода):
   [
     {"id": 1, "desc": "перша літера алфавіту; в переносному значенні — лише (через використання як числівник) перша"},
     {"id": 2, "desc": "Аарон, брат Мойсея"}
   ]

8. **Дополнительные указания (опционально)**
   - Если поле с описанием называется не "desc", но содержит английский словарный текст — переводить его (т.е. ориентироваться на тип содержимого, а не строго на имя поля).
   - Если объект содержит несколько текстовых полей — перевести все текстовые поля.
   - Не менять числовые/логические/id-поля.

9. **Финальный шаг**
   - Выполни перевод блока и верни только JSON-массив с переводом. Никаких пояснений, комментариев или метаданных в ответе — только JSON.

Начни работу, пожалуйста, после того как я пришлю JSON-файл (или блок).

"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = (
    r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite"
)

# Precomputed contiguous ID ranges, each about 7000 symbols after cleaning.
GROUP_RANGES: list[tuple[int, int]] = [
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

KJV_PATTERN = re.compile(r"; \[in KJV:.*?\]", re.DOTALL)


def clean_desc(text: str | None) -> str:
    if not text:
        return ""
    return KJV_PATTERN.sub("", text)


def fetch_records(conn: sqlite3.Connection, start_id: int, end_id: int) -> list[dict]:
    query = """
        SELECT id, "desc"
        FROM greek_descs
        WHERE id BETWEEN ? AND ?
        ORDER BY id
    """
    rows = conn.execute(query, (start_id, end_id)).fetchall()
    return [{"id": row[0], "desc": clean_desc(row[1])} for row in rows]


def export_groups(db_path: Path, out_dir: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(str(db_path)) as conn:
        for index, (start_id, end_id) in enumerate(GROUP_RANGES, start=1):
            records = fetch_records(conn, start_id, end_id)
            file_name = f"group_{index:02d}_{start_id}-{end_id}.json"
            file_path = out_dir / file_name
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export greek_descs into 37 JSON files by predefined ID ranges, "
            "removing '; [in KJV: ...]' fragments from desc."
        )
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--out-dir",
        default="greek_descs_groups_json",
        help="Output directory for JSON files (default: greek_descs_groups_json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_groups(Path(args.db), Path(args.out_dir))


if __name__ == "__main__":
    main()
