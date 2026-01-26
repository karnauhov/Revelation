#!/usr/bin/env python3
r"""
compare_json_sqlite.py

Сравнивает поле `lemma` из JSON-файла с колонкой `word` в SQLite таблице `greek_words`.
Дополнительно сравнивает `derivation` (JSON) и `origin` (DB) — извлекает все подстроки вида G<число> или H<число>
и сравнивает последовательность (порядок важен). Если в JSON есть токены, которых нет в колонке `origin`,
скрипт добавляет отсутствующие токены в конец колонки, через запятую. По умолчанию скрипт **только симулирует** изменения.
Чтобы действительно изменить БД, запусти с флагом `--update-db`.

По-умолчанию использует пути:
JSON: C:/Users/karna/Downloads/Revelation/greek.json
SQLite: C:/Users/karna/OneDrive/Documents/revelation/db/revelation.sqlite

Пример запуска (только просмотр изменений):
    python compare_json_sqlite.py

Пример запуска (внести изменения в БД, рекомендую предварительно сделать backup):
    python compare_json_sqlite.py --update-db --backup-db

Опции:
  --json PATH       путь к JSON файлу
  --db PATH         путь к SQLite файлу
  --csv PATH        (опционально) сохранить список несовпадений lemma в CSV
  --no-normalize    не применять Unicode-normalization и .strip() перед сравнением
  --ignore-case     сравнивать без учёта регистра (после нормализации)
  --update-db       реально применять изменения к DB (по умолчанию -- dry-run)
  --backup-db       если указан вместе с --update-db, создаст копию БД перед изменениями

Вывод в консоль:
 - для каждой несовпадающей пары lemma vs word выводится строка с ID и обоими значениями
 - для каждой несовпадающей пары derivation vs origin выводится строка с ID и обоими списками токенов
 - если включено --update-db, для каждой записи, в которой добавлены токены, выводится:
     ID <id>: origin before='...' -> after='...' (added: ...)

В конце печатается подробная сводка по всем проверкам и по произведённым/планируемым изменениям.
"""

import argparse
import json
import sqlite3
import unicodedata
import csv
import sys
import re
import shutil
from pathlib import Path

DEFAULT_JSON = "C:/Users/karna/Downloads/Revelation/greek.json"
DEFAULT_DB = "C:/Users/karna/OneDrive/Documents/revelation/db/revelation.sqlite"

# Регекс для поиска токенов вида G123 или H456
DERIV_TOKEN_RE = re.compile(r'[GH][0-9]+', flags=re.IGNORECASE)


def normalize_text(s: str, do_normalize: bool, ignore_case: bool) -> str:
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    if do_normalize:
        s = unicodedata.normalize('NFC', s)
        s = s.strip()
    if ignore_case:
        s = s.casefold()
    return s


def extract_derivation_tokens(s: str):
    """Возвращает список токенов вида 'G123' или 'H456' в том порядке, как они встречаются.
    Для токенов 'H' убираются ведущие нули в числовой части: 'H08559' -> 'H8559'.
    """
    if not s:
        return []
    found = DERIV_TOKEN_RE.findall(s)
    tokens = []
    for t in found:
        if not t:
            continue
        t_up = t.upper()
        prefix = t_up[0]
        num = t_up[1:]
        if prefix == 'H':
            # убрать ведущие нули в числовой части
            num = num.lstrip('0')
            if num == '':
                num = '0'
        tokens.append(f"{prefix}{num}")
    return tokens


def parse_origin_column(origin_raw: str):
    """Разбирает содержимое колонки origin и возвращает список токенов в нормализованном виде.
    Использует ту же нормализацию, что и extract_derivation_tokens(), поэтому H08559 -> H8559.
    """
    return extract_derivation_tokens(origin_raw)


def main():
    parser = argparse.ArgumentParser(description='Compare JSON "lemma" with SQLite "word" and derivation/origin; optionally update DB')
    parser.add_argument('--json', default=DEFAULT_JSON, help='Path to JSON file')
    parser.add_argument('--db', default=DEFAULT_DB, help='Path to SQLite DB')
    parser.add_argument('--csv', default=None, help='Optional: path to CSV file to save lemma mismatches')
    parser.add_argument('--no-normalize', dest='normalize', action='store_false', help='Do not apply Unicode normalize+strip')
    parser.add_argument('--ignore-case', action='store_true', help='Compare case-insensitive')
    parser.add_argument('--update-db', action='store_true', help='If set, actually apply origin updates to DB (default: dry-run)')
    parser.add_argument('--backup-db', action='store_true', help='Create a copy of the DB file before applying updates (use with --update-db)')
    args = parser.parse_args()

    json_path = Path(args.json)
    db_path = Path(args.db)

    if not json_path.exists():
        print(f"JSON file not found: {json_path}")
        sys.exit(2)
    if not db_path.exists():
        print(f"SQLite DB not found: {db_path}")
        sys.exit(2)

    # Load JSON
    try:
        with json_path.open('r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(3)

    # Optionally backup DB
    if args.update_db and args.backup_db:
        backup_path = db_path.with_suffix(db_path.suffix + '.backup')
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")

    # Connect to DB
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
    except Exception as e:
        print(f"Error opening SQLite DB: {e}")
        sys.exit(4)

    total = 0
    matched = 0
    mismatched = 0
    missing_in_db = 0
    missing_lemma = 0
    mismatches_list = []  # for CSV: lemma mismatches

    # For derivation/origin comparisons and updates
    derivation_total = 0
    derivation_matched = 0
    derivation_mismatched = 0
    derivation_missing_json = 0
    derivation_missing_db = 0
    derivation_mismatches_list = []

    # Update counters
    rows_modified = 0
    tokens_added_total = 0

    for key, obj in data.items():
        if not isinstance(key, str):
            continue
        if not (key.startswith('G') or key.startswith('g')):
            continue
        num_part = key[1:]
        if not num_part.isdigit():
            continue
        id_num = int(num_part)
        total += 1

        # --- lemma vs word check ---
        lemma = obj.get('lemma', '')
        if lemma is None or lemma == '':
            missing_lemma += 1

        cur.execute('SELECT word, origin FROM greek_words WHERE id = ?', (id_num,))
        row = cur.fetchone()
        if row is None:
            missing_in_db += 1
            db_word_raw = ''
            db_origin_raw = ''
            mismatched += 1
            print(f"ID {id_num}: MISSING in DB. JSON lemma='{lemma}'")
            mismatches_list.append((id_num, lemma, ''))
            # cannot update origin for missing DB row
            continue
        else:
            db_word_raw = row[0] if row[0] is not None else ''
            db_origin_raw = row[1] if len(row) > 1 and row[1] is not None else ''

        json_val = normalize_text(lemma, args.normalize, args.ignore_case)
        db_val = normalize_text(db_word_raw, args.normalize, args.ignore_case)

        if json_val == db_val:
            matched += 1
        else:
            mismatched += 1
            print(f"ID {id_num}: JSON lemma='{lemma}'  <-->  DB word='{db_word_raw}'")
            mismatches_list.append((id_num, lemma, db_word_raw))

        # --- derivation vs origin check & potential update ---
        derivation_total += 1
        derivation_raw = obj.get('derivation', '')
        deriv_tokens = extract_derivation_tokens(derivation_raw)

        origin_raw = db_origin_raw
        origin_tokens = parse_origin_column(origin_raw)

        if not derivation_raw:
            derivation_missing_json += 1
        if not origin_raw:
            derivation_missing_db += 1

        if deriv_tokens == origin_tokens:
            derivation_matched += 1
        else:
            derivation_mismatched += 1
            print(f"ID {id_num}: derivation tokens={deriv_tokens}  <-->  origin tokens={origin_tokens}")
            derivation_mismatches_list.append((id_num, derivation_raw, origin_raw, deriv_tokens, origin_tokens))

            # Determine which tokens from deriv_tokens are missing in origin_tokens
            origin_set = set(origin_tokens)
            to_add = [t for t in deriv_tokens if t not in origin_set]
            if to_add:
                new_origin_tokens = origin_tokens + to_add
                new_origin_str = ','.join(new_origin_tokens)
                print(f"ID {id_num}: origin before='{origin_raw}' -> after='{new_origin_str}' (added: {to_add})")
                tokens_added_total += len(to_add)
                rows_modified += 1
                if args.update_db:
                    try:
                        cur.execute('UPDATE greek_words SET origin = ? WHERE id = ?', (new_origin_str, id_num))
                        conn.commit()
                    except Exception as e:
                        print(f"Error updating DB for ID {id_num}: {e}")
                        conn.rollback()
                else:
                    print(f"(dry-run) Not applying update to DB for ID {id_num}. Use --update-db to apply changes.")

    # Summary
    print('=== SUMMARY ===')
    print(f'Total JSON entries processed: {total}')
    print(f'Lemma checks: Matched: {matched}  |  Mismatched: {mismatched}  |  Missing in DB: {missing_in_db}  |  Missing lemma in JSON: {missing_lemma}')

    print('Derivation/Origin checks:')
    print(f'Total checks: {derivation_total}')
    print(f'Matched: {derivation_matched}')
    print(f'Mismatched: {derivation_mismatched}')
    print(f'Missing derivation in JSON: {derivation_missing_json}')
    print(f'Missing origin in DB: {derivation_missing_db}')

    print(f'DB modifications (planned/applied): rows_modified={rows_modified}, tokens_added_total={tokens_added_total}')

    # Save CSV if requested (only lemma mismatches to keep CSV simple)
    if args.csv:
        try:
            with open(args.csv, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['id', 'json_lemma', 'db_word'])
                for row in mismatches_list:
                    writer.writerow(row)
            print(f'Mismatches saved to CSV: {args.csv}')
        except Exception as e:
            print(f'Error saving CSV: {e}')

    conn.close()


if __name__ == '__main__':
    main()
