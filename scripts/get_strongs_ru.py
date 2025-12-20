# get_strongs_ru.py
import sqlite3
import urllib.request
import urllib.error
from bs4 import BeautifulSoup, NavigableString
import re
import os
import time

DB_PATH = r"C:\Users\karna\Downloads\Revelation\revelation_ru.sqlite"
BASE_URL = "https://www.bible.in.ua/underl/S/S/g{num:02d}.htm"
STRONG_BASE_RE = re.compile(r'^[hgHG]\d{2}\.htm$')
FONT_PATTERN = re.compile(r'\(<font\b[^>]*>.*?</font>\)', flags=re.IGNORECASE | re.DOTALL)

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
                print(f"Skipping invalid ID at index {index}: '{el[1] or el[0] or el[2]}'")
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
            desc = desc.replace("<br> ", "\r\n")
            desc = desc.replace("<br>", "\r\n")
            desc = desc.replace("<i>", "*")
            desc = desc.replace("</i>", "*")
            desc = desc.replace("</b>", "**")
            desc = desc.replace("</b>", "**")
            desc = desc.replace("\\""", "")
            desc = html_links_to_md(desc)
            desc = remove_font_parentheses(desc)
            desc = desc.replace(" ;", ";")
            desc = desc.replace(" ,", ",")
            desc = desc.replace(" .", ".")
            desc = desc.replace("    ", " ")
            desc = desc.replace("   ", " ")
            desc = desc.replace("  ", " ")
            #print(f"Q{gid}: {desc}")
            try:
                cur.execute("INSERT OR REPLACE INTO greek_descs (id, desc) VALUES (?, ?)", (gid, desc))
                count += 1
            except Exception as e:
                print(f"Error inserting ID {gid}: {e}")
        index += 1
    conn.commit()
    conn.close()
    print(f"Success! Inserted/updated {count} complete records into 'greek_descs' table.")

def html_links_to_md(html: str, *, convert_non_htm=False, text_only=False) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for a in list(soup.find_all('a', href=True)):
        href = a['href']
        href_no_query = href.split('?', 1)[0]

        if '#' in href_no_query:
            href_path, frag = href_no_query.split('#', 1)
        else:
            href_path, frag = href_no_query, None

        base = os.path.basename(href_path)
        new_md = None

        if base.lower().endswith('.htm') and STRONG_BASE_RE.match(base) and frag:
            m = re.match(r'\s*0*([0-9]+)', frag)
            if m:
                num = str(int(m.group(1)))
                letter = base[0].upper()
                scheme = f'strong:{letter}{num}'
                text = f'{letter}{num}'
                new_md = f'[{text}]({scheme})'

        elif base.lower().endswith('.htm'):
            name = os.path.splitext(base)[0]
            if name:
                visible = a.get_text(strip=True) or name

                next_node = a.next_sibling
                if isinstance(next_node, NavigableString):
                    m = re.match(r'^(\s+)(\d+):(\d+)', str(next_node))
                    if m:
                        leading_spaces = m.group(1) 
                        chap = m.group(2)
                        verse = m.group(3)
                        visible_with_ref = f'{visible} {chap}:{verse}'
                        scheme = f'bible:{name}:{verse}'
                        new_md = f'[{visible_with_ref}]({scheme})'
                        rest = str(next_node)[m.end():]
                        new_next = leading_spaces + rest
                        if new_next == '':
                            next_node.extract()
                        else:
                            next_node.replace_with(NavigableString(new_next))
                    else:
                        scheme = f'bible:{name}'
                        text = visible
                        new_md = f'[{text}]({scheme})'
                else:
                    scheme = f'bible:{name}'
                    text = visible
                    new_md = f'[{text}]({scheme})'

        else:
            if convert_non_htm:
                text = a.get_text(strip=True) or href
                new_md = f'[{text}]({href})'

        if new_md is not None:
            a.replace_with(NavigableString(new_md))

    if text_only:
        return soup.get_text()
    else:
        return str(soup)

def remove_font_parentheses(text: str) -> str:
    return FONT_PATTERN.sub('', text)

if __name__ == "__main__":
    for i in range(0, 57):
        url = BASE_URL.format(num=i)
        print(f"Downloading page {i:02d} -> {url} ...")
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                html_bytes = resp.read()
        except urllib.error.HTTPError as e:
            print(f"HTTP error for {url}: {e.code} {e.reason} — skip")
            continue
        except urllib.error.URLError as e:
            print(f"URL error for {url}: {e.reason} — skip")
            continue
        except Exception as e:
            print(f"Other error downloading {url}: {e} — skip")
            continue

        try:
            html = html_bytes.decode("windows-1251", errors="replace")
        except Exception as e:
            print(f"Decoding error {url}: {e} — skip")
            continue

        match = re.search(r'a\s*=\s*new\s*Array\s*\((.*)\);', html, re.DOTALL)
        if not match:
            print(f"Array not found on page {url} — skip")
            continue

        array_src = match.group(1).strip()
        if not array_src:
            print(f"Empty array on page {url} — skip")
            continue

        try:
            print(f"Parsing and writing data from page {i:02d} ...")
            write_to_db(array_src)
        except Exception as e:
            print(f"Error processing data with {url}: {e}")

        time.sleep(1)

    print("All done.")
