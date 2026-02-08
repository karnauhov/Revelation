#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
update_greek_descs.py

Что делает:
- создаёт резервную копию базы данных (в той же папке, с добавлением timestamp);
- загружает JSON-файл;
- проходит по всем записям таблицы greek_descs (берёт id и desc);
- ищет в JSON ключ "G<id>", берёт из него поле "kjv_def";
- формирует новую строку: <desc_trimmed> + "; [in KJV: " + <kjv_def> + "]";
  (desc обрезается по краям — убираются пробельные символы в начале и конце)
- записывает эту строку в поле desc для данной id;
- печатает в консоль каждый обработанный id и прогресс;
- в конце выводит число обновлённых записей и список id, для которых нет объекта "G<id>" или нет поля "kjv_def".
"""

import sqlite3
import json
import shutil
import os
from datetime import datetime

# ====== Параметры (если нужно, поменяй пути) ======
DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation_en.sqlite"
JSON_PATH = r"C:\Users\karna\Downloads\Revelation\greek.json"
# ==================================================

def backup_db(db_path: str) -> str:
    """Создаёт копию БД рядом с оригиналом и возвращает путь к копии."""
    if not os.path.isfile(db_path):
        raise FileNotFoundError(f"DB file not found: {db_path}")
    dirname, fname = os.path.split(db_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{fname}.bak_{ts}"
    backup_path = os.path.join(dirname, backup_name)
    shutil.copy2(db_path, backup_path)
    return backup_path

def load_json(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("JSON root is not an object/dict.")
    return data

def main():
    print("Start update_greek_descs.py")
    print("DB:", DB_PATH)
    print("JSON:", JSON_PATH)
    try:
        backup_path = backup_db(DB_PATH)
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print("Не удалось создать резервную копию базы данных:", e)
        print("Прекращаю выполнение.")
        return

    try:
        json_data = load_json(JSON_PATH)
        print("JSON загружен, ключей в JSON:", len(json_data))
    except Exception as e:
        print("Ошибка при загрузке JSON:", e)
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute('SELECT COUNT(*) FROM greek_descs')
        total_rows = cur.fetchone()[0]
    except Exception as e:
        print("Ошибка при определении количества строк в таблице greek_descs:", e)
        conn.close()
        return

    try:
        cur.execute('SELECT id, desc FROM greek_descs')
        rows = cur.fetchall()
    except Exception as e:
        print("Ошибка при чтении данных из таблицы greek_descs:", e)
        conn.close()
        return

    updated_count = 0
    processed_count = 0
    missing_ids = []   # id для которых нет G<id> или нет поля kjv_def
    total_rows = len(rows)
    print(f"Найдено записей в таблице: {total_rows}. Начинаю обработку...")

    # Начинаем транзакцию
    try:
        for idx, (row_id, desc) in enumerate(rows, start=1):
            processed_count += 1
            key = f"G{row_id}"
            entry = json_data.get(key)
            if not entry or not isinstance(entry, dict):
                missing_ids.append(row_id)
                print(f"[{processed_count}/{total_rows}] ID {row_id}: нет объекта '{key}' в JSON — пропущено")
                continue

            kjv_def = entry.get("kjv_def")
            if kjv_def is None or (isinstance(kjv_def, str) and kjv_def.strip() == ""):
                missing_ids.append(row_id)
                print(f"[{processed_count}/{total_rows}] ID {row_id}: нет поля 'kjv_def' или оно пустое — пропущено")
                continue

            # Берём desc (если NULL — заменяем на пустую строку) и убираем пробелы по краям
            if desc is None:
                desc_val = ""
            else:
                # СТОРОННЕЕ замечание: здесь мы обрезаем пробелы по краям как просили раньше
                desc_val = str(desc).strip()

            # Формируем новую строку
            new_desc = f"{desc_val}; [in KJV: {kjv_def}]"

            # Обновляем запись; используем параметризованный запрос
            try:
                cur.execute('UPDATE greek_descs SET "desc" = ? WHERE id = ?', (new_desc, row_id))
                updated_count += 1
                # Можно коммитить периодически, но мы закоммитим в конце всей работы
                print(f"[{processed_count}/{total_rows}] ID {row_id}: обновлено ({updated_count} обновлено всего)")
            except Exception as e_upd:
                print(f"[{processed_count}/{total_rows}] ID {row_id}: ошибка при записи в БД: {e_upd}")
                # не добавляем в missing_ids — это другая причина; продолжаем

        # В конце — сохраняем изменения
        conn.commit()
    except Exception as e:
        print("Во время обновления произошла ошибка:", e)
        try:
            conn.rollback()
            print("Откат транзакции выполнен.")
        except:
            pass
    finally:
        conn.close()

    print("\nГотово.")
    print(f"Всего обработано записей: {processed_count}")
    print(f"Всего успешно обновлено: {updated_count}")
    print(f"Всего пропущено (нет G<id> или нет kjv_def): {len(missing_ids)}")
    if missing_ids:
        print("Список пропущенных id (первые 200):")
        print(missing_ids[:200])
        if len(missing_ids) > 200:
            print("...и ещё", len(missing_ids) - 200, "id")

    expected_total = 5523
    if updated_count == expected_total:
        print(f"Количество обновлённых записей совпадает с ожидаемым: {expected_total}")
    else:
        print(f"Ожидалось обновлено {expected_total}, фактически обновлено {updated_count} — проверь JSON / таблицу.")

if __name__ == "__main__":
    main()
