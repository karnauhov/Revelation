#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_dots.py

Применение:
    python fix_dots.py
или
    python fix_dots.py --db "C:\\путь\\до\\revelation_ru.sqlite" --no-backup

Скрипт:
 - создаёт резервную копию БД (файл с суффиксом .bak) по умолчанию;
 - проходит по всем строкам таблицы greek_descs, колонке "desc";
 - если (после rstrip) строка не оканчивается на '.', выводит id и оригинальную строку;
 - если строка оканчивается на ';' — заменяет на '.', иначе добавляет '.' в конец;
 - записывает изменения в БД и выводит сводку.
"""

import argparse
import sqlite3
import shutil
import os
import sys

def make_backup(db_path):
    bak_path = db_path + ".bak"
    shutil.copy2(db_path, bak_path)
    return bak_path

def process_database(db_path, do_backup=True, verbose=True):
    db_path = os.path.abspath(db_path)
    if not os.path.exists(db_path):
        print(f"Ошибка: файл БД не найден: {db_path}", file=sys.stderr)
        return

    if do_backup:
        bak = make_backup(db_path)
        if verbose:
            print(f"Создан бэкап: {bak}")

    conn = sqlite3.connect(db_path)
    # Чтобы получать строки как dict (удобно), можно использовать row_factory:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Колонка называется desc — это зарезервированное слово, поэтому берём её в двойные кавычки
    select_sql = 'SELECT id, "desc" AS desc FROM greek_descs'
    update_sql = 'UPDATE greek_descs SET "desc" = ? WHERE id = ?'

    total_rows = 0
    changed = 0
    printed = 0

    try:
        cur.execute(select_sql)
        rows = cur.fetchall()
        total_rows = len(rows)
        if verbose:
            print(f"Найдено строк: {total_rows}")

        for row in rows:
            row_id = row["id"]
            original = row["desc"]  # может быть None

            # Пропускаем None
            if original is None:
                continue

            # Оставим оригинал для вывода, но будем работать с trimmed для принятия решения об окончании
            trimmed = original.rstrip()  # удаляем хвостовые пробельные символы
            if len(trimmed) == 0:
                # пустая строка (или только пробелы) — считаем, что не заканчивается точкой
                if verbose:
                    print(f"ID {row_id}: (пустая или только пробелы)")
                printed += 1
                # добавим точку
                new_trimmed = '.'
                cur.execute(update_sql, (new_trimmed, row_id))
                changed += 1
                continue

            last_char = trimmed[-1]

            if last_char == '.':
                # Всё в порядке — ничего не делаем
                continue

            # Если не заканчивается на точку — выводим id и оригинальную строку
            print(f"ID {row_id}: {original}")
            printed += 1

            # Готовим новое значение:
            if last_char == ';':
                # заменяем последний символ ';' на '.'
                new_trimmed = trimmed[:-1] + '.'
            else:
                # просто добавляем точку
                new_trimmed = trimmed + '.'

            # Записываем новое значение (без хвостовых пробелов)
            cur.execute(update_sql, (new_trimmed, row_id))
            changed += 1

        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Произошла ошибка при обработке базы:", e, file=sys.stderr)
    finally:
        conn.close()

    print("=== Сводка ===")
    print(f"Всего строк в выборке: {total_rows}")
    print(f"Выведено в консоль (не оканчиваются на точку): {printed}")
    print(f"Изменено записей: {changed}")
    if do_backup and verbose:
        print("Если что-то пошло не так — восстановите базу из .bak файла.")

def main():
    parser = argparse.ArgumentParser(description="Fix trailing punctuation in greek_descs.desc")
    parser.add_argument("--db", type=str,
                        default=r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_ru.sqlite",
                        help="Путь к SQLite файлу (по умолчанию ваш путь)")
    parser.add_argument("--no-backup", dest="no_backup", action="store_true",
                        help="Не создавать резервную копию .bak")
    parser.add_argument("--quiet", dest="quiet", action="store_true",
                        help="Минимум вывода")
    args = parser.parse_args()

    process_database(args.db, do_backup=not args.no_backup, verbose=not args.quiet)

if __name__ == "__main__":
    main()
