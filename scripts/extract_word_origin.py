import os
import re
import sqlite3

# Directory with HTML files
BASE_DIR = r"C:\Users\karna\Downloads\Revelation\html_files"

# Marker to search for. The marker includes the opening square bracket '[' at the end.
MARKER = "Word Origin: </span>["

START = 1
END = 5624  # inclusive

# Path to SQLite database where results will be written
DB_PATH = r"C:\Users\karna\OneDrive\Documents\revelation\db\revelation.sqlite"
DB_TABLE = "greek_words"
DB_COLUMN = "origin"  # column to write the resulting codes string into

# Regex to find G<number> and H<number> tokens.
# This will capture sequences like G575, H2584 etc.
CODE_RE = re.compile(r'\b([GH]\d+)\b')

def try_decode(raw_bytes):
    """Try to decode bytes with several encodings commonly used on Windows.
    Return decoded string or None if all attempts fail.
    """
    for enc in ("utf-8", "latin-1"):
        try:
            return raw_bytes.decode(enc)
        except Exception:
            continue
    return None

def extract_codes(origin_text):
    """Given the extracted origin substring, find all G/H codes preserving
    first-occurrence order and removing duplicates.
    Returns a comma-separated string like 'G575,G3737' or empty string if none found.
    """
    seen = set()
    ordered = []
    for m in CODE_RE.finditer(origin_text):
        code = m.group(1)
        if code not in seen:
            seen.add(code)
            ordered.append(code)
    return ",".join(ordered)

def open_db(path):
    """Open sqlite DB and return connection. Create connection inside the script.
    Caller is responsible for closing the connection."""
    conn = sqlite3.connect(path)
    return conn

def upsert_origin(conn, table, column, row_id, value):
    """Insert or update the origin column for given id.
    Uses SQLite UPSERT (INSERT ... ON CONFLICT DO UPDATE) assuming 'id' is constrained UNIQUE/PRIMARY KEY.
    If UPSERT fails (e.g. because 'id' isn't unique or table schema unexpected), fallback to trying UPDATE,
    and if UPDATE affects 0 rows, attempt INSERT (may fail if other NOT NULL columns exist).
    Returns True if write was successful, False otherwise.
    """
    cur = conn.cursor()
    try:
        # Try UPSERT first (works if id is UNIQUE or PRIMARY KEY)
        sql_upsert = f"""
            INSERT INTO {table} (id, {column})
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET {column}=excluded.{column}
        """
        cur.execute(sql_upsert, (row_id, value))
        return True
    except sqlite3.OperationalError:
        # UPSERT syntax might not be supported or table schema different.
        # Try UPDATE then INSERT fallback.
        try:
            sql_update = f"UPDATE {table} SET {column} = ? WHERE id = ?"
            cur.execute(sql_update, (value, row_id))
            if cur.rowcount > 0:
                return True
            else:
                # Try simple INSERT (may fail if table has other NOT NULL columns)
                sql_insert = f"INSERT INTO {table} (id, {column}) VALUES (?, ?)"
                cur.execute(sql_insert, (row_id, value))
                return True
        except Exception as e:
            # Write failed
            return False
    except Exception as e:
        return False

def main():
    # Counters
    processed = 0
    files_missing_marker = 0
    files_decode_fail = 0
    files_file_not_found = 0
    files_marker_no_closing = 0
    files_empty_origin = 0

    origins_extracted = 0  # number of files where we extracted the origin substring
    codes_found_count = 0  # number of files where we found at least one G/H code
    codes_not_found_count = 0  # number of files where no codes were found

    db_written_count = 0
    db_failed_count = 0

    # Open DB connection once
    try:
        conn = open_db(DB_PATH)
    except Exception as e:
        print(f"ERROR: Could not open DB at {DB_PATH}: {e}")
        return

    for i in range(START, END + 1):
        filename = os.path.join(BASE_DIR, f"{i}.html")
        processed += 1

        try:
            with open(filename, "rb") as f:
                raw = f.read()
        except FileNotFoundError:
            print(f"{i}.html: File not found.")
            files_file_not_found += 1
            continue
        except Exception as e:
            print(f"{i}.html: Error opening file: {e}")
            files_file_not_found += 1
            continue

        text = try_decode(raw)
        if text is None:
            print(f"{i}.html: Could not decode file with tried encodings (utf-8, cp1251, latin-1).")
            files_decode_fail += 1
            continue

        idx = text.find(MARKER)
        if idx == -1:
            # Marker not found at all
            print(f"{i}.html: Word Origin not found.")
            files_missing_marker += 1
            continue

        start_pos = idx + len(MARKER)
        end_pos = text.find("]", start_pos)
        if end_pos == -1:
            print(f"{i}.html: Word Origin opening found but closing ']' not found.")
            files_marker_no_closing += 1
            continue

        # extract and trim result
        word_origin = text[start_pos:end_pos].strip()
        if not word_origin:
            print(f"{i}.html: Word Origin brackets found but content is empty.")
            files_empty_origin += 1
            continue

        # We have an origin substring
        origins_extracted += 1

        # Find G/H codes
        codes_str = extract_codes(word_origin)
        if codes_str:
            codes_found_count += 1
            print(f"{i}.html: ORIGINAL ORIGIN: {word_origin}")
            print(f"{i}.html: EXTRACTED CODES: {codes_str}")
        else:
            codes_not_found_count += 1
            print(f"{i}.html: ORIGINAL ORIGIN: {word_origin}")
            print(f"{i}.html: No G#/H# codes found in this origin substring.")

        # Write the resulting codes_str (could be empty string) into DB column origin for id = i
        try:
            success = upsert_origin(conn, DB_TABLE, DB_COLUMN, i, codes_str)
            if success:
                db_written_count += 1
            else:
                db_failed_count += 1
                print(f"{i}.html: Failed to write to DB for id={i}.")
        except Exception as e:
            db_failed_count += 1
            print(f"{i}.html: Exception writing to DB for id={i}: {e}")

    # Commit and close DB
    try:
        conn.commit()
        conn.close()
    except:
        pass

    # Summary
    print()
    print("=== Summary ===")
    print(f"Processed files (attempted): {processed}")
    print(f"Files not found (missing file): {files_file_not_found}")
    print(f"Files decode failure: {files_decode_fail}")
    print(f"Files without marker 'Word Origin': {files_missing_marker}")
    print(f"Files with marker but missing closing ']': {files_marker_no_closing}")
    print(f"Files with empty origin content: {files_empty_origin}")
    print()
    print(f"Origin substrings extracted: {origins_extracted}")
    print(f"Files where G/H codes found: {codes_found_count}")
    print(f"Files where no G/H codes found: {codes_not_found_count}")
    print()
    print(f"DB writes successful: {db_written_count}")
    print(f"DB writes failed: {db_failed_count}")

if __name__ == "__main__":
    main()
