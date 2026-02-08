#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
find_punct_and_brackets.py

Ищет в столбце `desc` последовательности "знак;" (символ, который не является буквой/цифрой/пробелом/кавычкой/закрывающей скобкой, затем ';')
и проверяет баланс скобок для (), {} и [].
Печатает прогресс и в конце выводит:
 - список id с найденной последовательностью "знак;"
 - список id с несбалансированными скобками и соответствующие подсчёты
"""

import sqlite3
import re
import os
import sys

DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite"

# Регекс для "знак;" — находим символ ';', перед которым НЕ стоит:
#   \w (буквы/цифры/_), \s (пробельные символы), одинарная/двойная кавычка, или закрывающая скобка: ) ] }
# Используем негативный lookbehind (?<![...]) — фиксированная ширина 1 символ.
PATTERN = re.compile(r"(?<![\w\s'\"\)\]\}]);", flags=re.UNICODE)

def analyze_desc(desc_text: str):
    """Возвращает (has_punct_semicolon, bracket_counts_dict).
    bracket_counts_dict = {
       '()': (count_open, count_close),
       '{}': (count_open, count_close),
       '[]': (count_open, count_close)
    }
    """
    if desc_text is None:
        desc_text = ""
    s = str(desc_text)

    has_pattern = bool(PATTERN.search(s))

    counts = {
        '()': (s.count('('), s.count(')')),
        '{}': (s.count('{'), s.count('}')),
        '[]': (s.count('['), s.count(']')),
    }

    return has_pattern, counts

def main():
    if not os.path.isfile(DB_PATH):
        print(f"DB not found: {DB_PATH}", file=sys.stderr)
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, desc FROM greek_descs")
    except Exception as e:
        print("Ошибка запроса к таблице greek_descs:", e, file=sys.stderr)
        conn.close()
        return

    rows = cur.fetchall()
    total = len(rows)
    print(f"Найдено записей: {total}. Начинаю проверку...")

    punct_ids = []         # id где найден "знак;"
    mismatched = []        # список словарей { 'id': id, 'counts': {...} } где есть несбалансированные скобки

    for idx, (row_id, desc) in enumerate(rows, start=1):
        has_pattern, counts = analyze_desc(desc)

        # проверка несбаланса
        unbalanced = {}
        for br, (open_cnt, close_cnt) in counts.items():
            if open_cnt != close_cnt:
                unbalanced[br] = {'open': open_cnt, 'close': close_cnt}

        # собираем результаты
        if has_pattern:
            punct_ids.append(row_id)

        if unbalanced:
            mismatched.append({
                'id': row_id,
                'unbalanced': unbalanced
            })

        # печатаем прогресс по каждой записи
        status_parts = []
        status_parts.append(f"pattern={'YES' if has_pattern else 'no'}")
        if unbalanced:
            ub_br = ",".join([f"{br}({v['open']}!={v['close']})" for br, v in unbalanced.items()])
            status_parts.append(f"unbalanced={ub_br}")
        else:
            status_parts.append("balanced")

        print(f"[{idx}/{total}] ID {row_id}: " + "; ".join(status_parts))

    # итог
    print("\n--- Итоги ---")
    print(f"Всего проверено: {total}")
    print(f"Найдено id с последовательностью 'знак;': {len(punct_ids)}")
    if punct_ids:
        print("Список id (первые 500):")
        print(punct_ids[:500])
        if len(punct_ids) > 500:
            print("...и ещё", len(punct_ids) - 500, "id")

    print(f"\nНайдено id с несбалансированными скобками: {len(mismatched)}")
    if mismatched:
        print("Примеры (первые 200):")
        for item in mismatched[:200]:
            rid = item['id']
            unb = item['unbalanced']
            details = "; ".join([f"{br}: open={v['open']}, close={v['close']}" for br, v in unb.items()])
            print(f"  ID {rid}: {details}")
        if len(mismatched) > 200:
            print("...и ещё", len(mismatched) - 200, "id")

    conn.close()

    return {
        'total': total,
        'punct_ids': punct_ids,
        'mismatched': mismatched
    }

if __name__ == '__main__':
    main()
