#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
remove_starred_refs.py

Ищет и удаляет в таблице `greek_descs` файла revelation_ru.sqlite все фрагменты,
начинающиеся со звёздочки и содержащие "см. евр." или "см. арам." —
т.е. шаблоны вида "*см. евр...." или "*см. арам...." до ближайшей точки ('.'),
точки с запятой (';') или конца строки.

Для каждой изменённой строки в консоль выводится:
ID <id> | REMOVED: <вырезанный_фрагмент>[ || <ещё фрагменты>] | NEW: <новое_значение_desc>

Изменения записываются обратно в базу revelation_ru.sqlite.

Внимание: перед изменением скрипт создаёт резервную копию файла БД с расширением .bak
(если уже есть .bak, создаётся с таймстампом).

Запуск:
    python remove_starred_refs.py
или
    python remove_starred_refs.py --db "C:\\путь\\to\\revelation_ru.sqlite"

"""

import argparse
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime


def make_backup(db_path: str):
    """Создаёт резервную копию файла БД. Возвращает путь к созданной копии."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Файл базы не найден: {db_path}")

    bak_path = db_path + ".bak"
    # Если bak уже существует — добавим таймстамп
    if os.path.exists(bak_path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_path = f"{db_path}.bak.{ts}"
    shutil.copy2(db_path, bak_path)
    return bak_path


# Регулярное выражение для поиска фрагментов.
# - начинается с '*' (возможно с пробелами после)
# - затем 'см.' (возможны пробелы), затем 'евр.' или 'арам.'
# - затем любой текст (включая переносы) минимально до первой '.' или ';' или конца строки
# Флаги: IGNORECASE и DOTALL (чтобы '.' в шаблоне захватывал новые строки)
PATTERN = re.compile(r"\*\s*см\.\s*(?:евр|арам)\..*?(?:[.;]|\Z)", re.IGNORECASE | re.DOTALL | re.UNICODE)


def clean_result(text: str) -> str:
    """Минимальная пост-обработка результата после удаления фрагментов:
    - убираем лишние пробелы (замена множественных пробелов на один)
    - удаляем пробелы перед переводом строки
    - обрезаем начальные/конечные пробельные символы
    Это сохраняет основную структуру текста, но убирает очевидные артефакты удаления.
    """
    # Замена последовательностей пробелов (>1) на один
    text = re.sub(r"[ ]{2,}", " ", text)
    # Удаляем пробелы в конце строки перед переводом строки
    text = re.sub(r"[ \t]+\n", "\n", text)
    # Убираем повторяющиеся пустые строки (более одной)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Обрезаем ведущие/концевые пробелы
    return text.strip()


def process_db(db_path: str, table: str = "greek_descs", col: str = "desc"):
    if not os.path.exists(db_path):
        print(f"Ошибка: файл базы не найден: {db_path}", file=sys.stderr)
        return 2

    # Создаём резервную копию
    try:
        bak = make_backup(db_path)
        print(f"Создана резервная копия базы: {bak}")
    except Exception as e:
        print(f"Не удалось создать резервную копию: {e}", file=sys.stderr)
        return 3

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Соберём статистику
    rows_scanned = 0
    rows_modified = 0
    total_removed_fragments = 0

    try:
        cur.execute(f"SELECT id, {col} FROM {table}")
    except sqlite3.Error as e:
        print(f"Ошибка при чтении таблицы {table}: {e}", file=sys.stderr)
        conn.close()
        return 4

    # Начинаем транзакцию
    try:
        for row in cur:
            rows_scanned += 1
            row_id, desc = row[0], row[1]
            if desc is None:
                continue
            text = str(desc)

            # Находим все вхождения
            matches = list(PATTERN.finditer(text))
            if not matches:
                continue

            # Сохраняем найденные фрагменты для отображения
            removed = [m.group(0) for m in matches]
            total_removed_fragments += len(removed)

            # Удаляем все вхождения
            new_text = PATTERN.sub('', text)
            # Небольшая чистка
            new_text = clean_result(new_text)

            # Вывод в консоль — перечисляем удалённые фрагменты и итоговый текст
            removed_display = ' || '.join(removed)
            print(f"ID {row_id} | REMOVED: {removed_display} | NEW: {new_text}")

            # Обновляем запись в БД
            try:
                cur_update = conn.cursor()
                cur_update.execute(f"UPDATE {table} SET {col} = ? WHERE id = ?", (new_text, row_id))
                rows_modified += 1
            except sqlite3.Error as e:
                print(f"Ошибка при обновлении id={row_id}: {e}", file=sys.stderr)
                conn.rollback()
                conn.close()
                return 5

        # фиксим изменения
        conn.commit()

    finally:
        conn.close()

    # Итоги
    print("\n--- Итоги ---")
    print(f"Просканировано строк: {rows_scanned}")
    print(f"Изменено строк: {rows_modified}")
    print(f"Всего удалённых фрагментов: {total_removed_fragments}")
    print("--------------")
    return 0


if __name__ == '__main__':
    default_db = r"C:\\Users\\karna\\OneDrive\\Documents\\revelation\\db\\revelation_ru.sqlite"

    parser = argparse.ArgumentParser(description="Удалить '*см. евр.' и '*см. арам.' фрагменты из revelation_ru.sqlite")
    parser.add_argument('--db', default=default_db, help='Путь к файлу revelation_ru.sqlite')
    parser.add_argument('--table', default='greek_descs', help='Имя таблицы (по умолчанию: greek_descs)')
    parser.add_argument('--col', default='desc', help='Имя колонки (по умолчанию: desc)')

    args = parser.parse_args()

    rc = process_db(args.db, table=args.table, col=args.col)
    sys.exit(rc)
