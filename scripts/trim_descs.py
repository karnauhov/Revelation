#!/usr/bin/env python3
r"""
trim_descs.py

Пример использования:
  python trim_descs.py
  python trim_descs.py --db "C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite" --backup --dry-run

Сделает:
 - подключение к SQLite
 - пройдется по всем записям таблицы greek_descs
 - возьмет значение из колонки "desc", обрежет пробелы по краям (strip)
 - если значение изменилось, запишет trimmed значение обратно по rowid
 - выведет общее количество записей и количество изменённых (те, у которых были пробелы по краям)
"""
import argparse
import sqlite3
import shutil
import sys
from pathlib import Path

DEFAULT_DB = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite"

def main():
    parser = argparse.ArgumentParser(description="Trim leading/trailing whitespace in greek_descs.\"desc\"")
    parser.add_argument("--db", "-d", default=DEFAULT_DB, help="Path to sqlite db")
    parser.add_argument("--backup", "-b", action="store_true", help="Create a backup copy before modifying")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes, only report what would be changed")
    parser.add_argument("--limit", type=int, default=0, help="Optional: limit number of rows processed (0 = no limit)")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Ошибка: файл БД не найден: {db_path}", file=sys.stderr)
        sys.exit(2)

    if args.backup:
        backup_path = db_path.with_suffix(db_path.suffix + ".bak")
        print(f"Создаю бэкап: {backup_path}")
        shutil.copy2(db_path, backup_path)

    conn = sqlite3.connect(str(db_path))
    conn.text_factory = lambda b: b.decode(errors='surrogatepass')  # preserve bytes->str safely
    cur = conn.cursor()

    # Проверим, есть ли таблица и колонка (аккуратно, если схема другая — сообщение об ошибке)
    try:
        cur.execute("PRAGMA table_info(greek_descs);")
        cols = [r[1] for r in cur.fetchall()]
        if not cols:
            print("Таблица greek_descs не найдена или пуста.", file=sys.stderr)
            conn.close()
            sys.exit(3)
        if "desc" not in cols:
            # колонка может называться иначе (например Desc или description) — сообщим
            print('В таблице greek_descs нет колонки "desc". Существующие колонки:', cols, file=sys.stderr)
            conn.close()
            sys.exit(4)
    except sqlite3.Error as e:
        print("Ошибка при проверке схемы БД:", e, file=sys.stderr)
        conn.close()
        sys.exit(5)

    # Считаем общее количество записей (это для отчета)
    try:
        cur.execute("SELECT COUNT(*) FROM greek_descs;")
        total_rows = cur.fetchone()[0]
    except sqlite3.Error:
        total_rows = None

    print(f"Общее число строк в greek_descs: {total_rows if total_rows is not None else '(не удалось посчитать)'}")
    processed = 0
    modified = 0
    changed_rows = []

    # Итерация по всем строкам: используем rowid, это надёжный способ ссылаться на строку
    try:
        query = 'SELECT rowid, "desc" FROM greek_descs'
        if args.limit and args.limit > 0:
            query += f" LIMIT {int(args.limit)}"
        cur.execute(query)
    except sqlite3.Error as e:
        print("Ошибка при выборке строк:", e, file=sys.stderr)
        conn.close()
        sys.exit(6)

    # Начинаем транзакцию (если не dry-run)
    if not args.dry_run:
        conn.execute("BEGIN;")

    try:
        for row in cur:
            processed += 1
            rowid = row[0]
            value = row[1]

            # None остаётся None
            if value is None:
                continue

            # Приводим к str если bytes (редко)
            if isinstance(value, (bytes, bytearray)):
                try:
                    value = value.decode("utf-8")
                except Exception:
                    value = value.decode("utf-8", errors="surrogatepass")

            trimmed = value.strip()  # убирает только по краям любые пробельные символы

            if trimmed != value:
                modified += 1
                changed_rows.append((rowid, value, trimmed))
                if not args.dry_run:
                    # обновляем по rowid; закомментировать WHERE rowid=... если хочешь обновлять по другому PK
                    conn.execute('UPDATE greek_descs SET "desc" = ? WHERE rowid = ?', (trimmed, rowid))

        # Коммит если не dry-run
        if not args.dry_run:
            conn.commit()

    except sqlite3.Error as e:
        # при ошибке откатываем
        if not args.dry_run:
            conn.rollback()
        print("Ошибка во время обработки/обновления:", e, file=sys.stderr)
        conn.close()
        sys.exit(7)
    finally:
        conn.close()

    print()
    print("Результат:")
    print(f"  записей просмотрено: {processed}")
    print(f"  записей с пробелами по краям (и обновлёных при отсутствии --dry-run): {modified}")
    if args.dry_run:
        print("  (dry-run — изменения НЕ были записаны)")
    if modified:
        print()
        print("Первые 10 изменённых строк (rowid, original_preview -> trimmed_preview):")
        for r in changed_rows[:10]:
            rowid, orig, trimmed = r
            # показываем короткие превью (вырезаем новые строки для показа)
            orig_preview = orig.replace("\n", "\\n")
            trimmed_preview = trimmed.replace("\n", "\\n")
            if len(orig_preview) > 120:
                orig_preview = orig_preview[:117] + "..."
            if len(trimmed_preview) > 120:
                trimmed_preview = trimmed_preview[:117] + "..."
            print(f"  {rowid}: '{orig_preview}' -> '{trimmed_preview}'")

    print("\nГотово.")

if __name__ == "__main__":
    main()
