# get_strongs_ru.py
import sqlite3
import urllib.request
import re

DB_PATH = r"C:\Users\karna\Downloads\Revelation\revelation_ru.sqlite"

print("Downloading page...")
with urllib.request.urlopen("https://www.bible.in.ua/underl/S/S/g00.htm") as resp:
    html_bytes = resp.read()
html = html_bytes.decode("windows-1251", errors="replace")
match = re.search(r'a\s*=\s*new\s*Array\s*\((.*)\);', html, re.DOTALL)
if not match:
    raise Exception("Array not found!")
array_src = match.group(1).strip()

def write_to_db(src: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    src = src.replace('\\r\\n', '\\n').replace('\r\n', '\n')
    elements = re.findall(r"'([^'\\]*(?:\\.[^'\\]*)*)'|\"([^\"\\]*(?:\\.[^\"\\]*)*)\"|(\d+)", src)
    index = 0
    count = 0
    gid = 1
    desc = ""
    gid_error = False
    for el in elements:
        if index % 5 == 0:
            try:
                gid = int(el[1] or el[0] or el[2])
                gid_error = False
            except ValueError:
                print(f"Skipping invalid ID at index {index}: '{el[1]}'")
                gid_error = True
        elif (index - 4) % 5 == 0 and not gid_error:
            raw_desc = el[1] or el[0] or el[2]
            s_index = raw_desc.find("</b\\>")
            if s_index != -1:
                desc = raw_desc[s_index + 6:]
            else:
                s_index = raw_desc.find("</font\\>")
                if s_index != -1:
                    desc = raw_desc[s_index + 9:]
                else:
                    desc = raw_desc
            desc = desc.replace("\\<", "<")
            desc = desc.replace("\\>", ">")
            if desc.endswith("<br>"):
                desc = desc[: -4]
            if desc.endswith("<br>"):
                desc = desc[: -4]
            if desc.endswith("<br>"):
                desc = desc[: -4]
            desc = desc.replace("<br> ", "\n>")
            desc = desc.replace("<br>", "\n>")
            desc = desc.replace("<i>", "*")
            desc = desc.replace("</i>", "*")
            desc = desc.replace("</b>", "**")
            desc = desc.replace("</b>", "**")
            # TODO replace tag a 
            # TODO remove tag font and word "син."
            try:
                cur.execute("INSERT OR REPLACE INTO greek_descs (id, desc) VALUES (?, ?)", (gid, desc))
                count += 1
            except Exception as e:
                print(f"Error inserting ID {gid}: {e}")
        index += 1
    conn.commit()
    conn.close()
    print(f"Success! Inserted/updated {count} complete records into 'greek_descs' table.")

write_to_db(array_src)