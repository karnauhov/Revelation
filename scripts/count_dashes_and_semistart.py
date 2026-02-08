#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
count_dashes_and_semistart.py

Для каждой записи в таблице greek_descs (колонка desc):
 - считает количество (перекрывающихся) вхождений '--';
 - проверяет, начинается ли строка с ';' после удаления ведущих пробелов;
 - печатает прогресс и в конце выводит сводную статистику и списки id.
"""

import sqlite3
import re
import os
import sys

DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite"

# Регекс для подсчёта перекрывающихся вхождений '--'
RE_DASHES = re.compile(r'(?=--)')

def analyze_desc(desc_text: str):
    """Возвращает tuple (num_dashes, starts_with_semicolon)
    - num_dashes: количество (перекрывающихся) вхождений '--'
    - starts_with_semicolon: True если строка (после lstrip) начинается с ';'
    """
    if desc_text is None:
        s = ""
    else:
        s = str(desc_text)

    # подсчёт перекрывающихся вхождений '--'
    num_dashes = len(RE_DASHES.findall(s))

    # проверка начала строки игнорируя ведущие пробельные символы
    starts_with_semicolon = s.lstrip().startswith(';')

    return num_dashes, starts_with_semicolon

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
    total_rows = len(rows)
    print(f"Найдено записей: {total_rows}. Начинаю обработку...")

    # Агрегация результатов
    total_dashes = 0                     # общее количество найденных последовательностей "--" во всей базе
    rows_with_dashes_count = 0           # количество строк, где найдено >=1 '--'
    rows_with_dashes_ids = []            # список id где найдено >=1 '--'
    rows_starting_semicolon_count = 0    # количество строк, которые начинаются с ';' (после lstrip)
    rows_starting_semicolon_ids = []     # список id таких строк

    for idx, (row_id, desc) in enumerate(rows, start=1):
        num_dashes, starts_with_semicolon = analyze_desc(desc)

        # агрегация
        if num_dashes > 0:
            total_dashes += num_dashes
            rows_with_dashes_count += 1
            rows_with_dashes_ids.append({'id': row_id, 'count': num_dashes})

        if starts_with_semicolon:
            rows_starting_semicolon_count += 1
            rows_starting_semicolon_ids.append(row_id)

        # печатаем прогресс
        dash_part = f"-- count={num_dashes}"
        sem_part = f"starts_with_;={'YES' if starts_with_semicolon else 'no'}"
        print(f"[{idx}/{total_rows}] ID {row_id}: {dash_part}; {sem_part}")

    # итоговый вывод
    print("\n--- Итоги ---")
    print(f"Всего записей проверено: {total_rows}")
    print(f"Общее количество последовательностей '--' во всех строках: {total_dashes}")
    print(f"Количество строк, где найдено хотя бы одно '--': {rows_with_dashes_count}")
    if rows_with_dashes_ids:
        print("Примеры (первые 500) id с количеством '--':")
        # печатаем в читаемом виде (id:count)
        print([f"{item['id']}:{item['count']}" for item in rows_with_dashes_ids[:500]])
        if len(rows_with_dashes_ids) > 500:
            print("...и ещё", len(rows_with_dashes_ids) - 500, "записей")

    print(f"\nКоличество строк, которые (после удаления ведущих пробелов) начинаются с ';': {rows_starting_semicolon_count}")
    if rows_starting_semicolon_ids:
        print("Примеры (первые 500) id таких строк:")
        print(rows_starting_semicolon_ids[:500])
        if len(rows_starting_semicolon_ids) > 500:
            print("...и ещё", len(rows_starting_semicolon_ids) - 500, "id")

    conn.close()

    # Возвращаем данные (удобно если импортировать модуль)
    return {
        'total_rows': total_rows,
        'total_dashes': total_dashes,
        'rows_with_dashes_count': rows_with_dashes_count,
        'rows_with_dashes_ids': rows_with_dashes_ids,
        'rows_starting_semicolon_count': rows_starting_semicolon_count,
        'rows_starting_semicolon_ids': rows_starting_semicolon_ids
    }

if __name__ == '__main__':
    main()
