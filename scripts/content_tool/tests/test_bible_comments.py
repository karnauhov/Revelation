from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest

from scripts.content_tool.bible_map import BibleCatalog
from scripts.content_tool.mixins.bibles import BiblesMixin, bible_project_root
from scripts.content_tool.mixins.core_db import CoreDbMixin
from scripts.content_tool.web_db_manifest import read_web_db_manifest_entry


class Harness(BiblesMixin, CoreDbMixin, tk.Tk):
    def __init__(self, directory: Path):
        tk.Tk.__init__(self)
        self.withdraw()
        self.work_dir = directory
        self.bible_catalog = BibleCatalog.load(bible_project_root())
        self.bible_files = {}
        self.bible_connection = None
        self.current_bible_path = None
        self.bible_module_info = None
        self.bible_verse_rows = []
        self.bible_selected_verse_key = None
        self.bible_original_info_code = ""
        self.bible_pending_changes = False
        self.bible_comments_supported = False
        self._loading_bible_ui = False
        self._bible_controls = []
        self.manifest_dirty = []
        self.allow_switch = False
        self._build_bibles_tab(ttk.Frame(self))

    def _set_dirty(self, value): pass
    def _set_status(self, value): self.bible_status_var.set(value)
    def _update_section_db_labels(self): pass
    def _update_file_info(self): pass
    def _allow_switch_when_dirty(self): return self.allow_switch
    def _mark_local_db_manifest_dirty(self, path): self.manifest_dirty.append(path)


class BibleCommentsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.harness = Harness(self.directory)
        self.addCleanup(self.cleanup)

    def cleanup(self):
        self.harness._close_bible_connection()
        self.harness.destroy()
        self.temporary.cleanup()

    def make_db(self, name="bible_notes.sqlite", comments=True):
        path = self.directory / name
        with closing(sqlite3.connect(path)) as connection:
            connection.executescript('''
                CREATE TABLE info (code TEXT PRIMARY KEY, module_id TEXT, title TEXT,
                    description TEXT, language TEXT, canon TEXT, versification TEXT,
                    license TEXT, source_summary TEXT);
                INSERT INTO info VALUES ('TEST','test','Тест','Описание','uk','protestant_66',
                    'kjv_protestant','CC0-1.0','First-party synthetic test');
                CREATE TABLE db_metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL);
            ''')
            schema = 4 if comments else 3
            connection.execute(f"PRAGMA user_version={schema}")
            connection.executemany("INSERT INTO db_metadata VALUES (?,?)", [
                ("schema_version", str(schema)), ("data_version", "1"), ("date", "2026-10-01T00:00:00Z"),
            ])
            column = ", comment TEXT NOT NULL DEFAULT ''" if comments else ""
            connection.execute(f"CREATE TABLE verses (verse_key TEXT PRIMARY KEY,text TEXT NOT NULL{column})")
            if comments:
                connection.executemany("INSERT INTO verses VALUES (?,?,?)", [
                    ("001", "Світле слово", "Примітка з апострофом: об’єкт."), ("002", "Інший вірш", ""),
                ])
            else:
                connection.executemany("INSERT INTO verses VALUES (?,?)", [("001", "Word G1"), ("002", "Other")])
            connection.commit()
        return path

    def test_discovery_comment_filter_navigation_and_cancel_dirty_switch(self):
        self.make_db()
        h = self.harness
        h._refresh_bible_list(initial_select=True)
        self.assertIn("bible_notes.sqlite", h.bible_files)
        self.assertTrue(h.bible_comments_supported)
        self.assertEqual(h.bible_verse_comment.get("1.0", "end-1c"), "Примітка з апострофом: об’єкт.")
        h.bible_filter_var.set("ОБ’ЄКТ")
        self.assertEqual([r.verse_key for r in h.bible_verse_rows], ["001"])
        self.assertEqual(h.bible_verse_rows[0].text, "Світле слово")
        h.bible_pending_changes = True
        h._replace_text(h.bible_verse_comment, "Unsaved")
        h.bible_filter_var.set("absent")
        self.assertEqual(h.bible_verse_comment.get("1.0", "end-1c"), "Unsaved")
        self.assertEqual(h.bible_selected_verse_key, "001")

    def test_atomic_save_and_clear_comment_preserve_schema_bump_manifest(self):
        path = self.make_db()
        h = self.harness
        h._load_bible_db(path)
        h._replace_text(h.bible_verse_text, "Змінений вірш")
        h._replace_text(h.bible_verse_comment, "Нова сноска")
        self.assertTrue(h._save_bible_module(silent=True))
        row = h.bible_connection.execute("SELECT text,comment FROM verses WHERE verse_key='001'").fetchone()
        self.assertEqual(tuple(row), ("Змінений вірш", "Нова сноска"))
        entry = read_web_db_manifest_entry(path)
        self.assertEqual((entry["schemaVersion"], entry["dataVersion"]), (4, 2))
        self.assertNotEqual(entry["date"], "2026-10-01T00:00:00Z")
        self.assertIn(path, h.manifest_dirty)
        h._replace_text(h.bible_verse_comment, "")
        self.assertTrue(h._save_bible_module(silent=True))
        self.assertEqual(h.bible_verse_comment.get("1.0", "end-1c"), "")
        self.assertEqual(read_web_db_manifest_entry(path)["dataVersion"], 3)

    def test_failed_comment_update_rolls_back_text_info_and_metadata(self):
        path = self.make_db()
        h = self.harness
        h._load_bible_db(path)
        h.bible_connection.execute("""CREATE TRIGGER reject_note BEFORE UPDATE ON verses
            BEGIN SELECT RAISE(ABORT, 'test failure'); END""")
        h.bible_connection.commit()
        h.bible_info_vars["title"].set("Changed")
        h._replace_text(h.bible_verse_text, "Changed")
        h._replace_text(h.bible_verse_comment, "Changed")
        self.assertFalse(h._save_bible_module(silent=True))
        self.assertEqual(h.bible_connection.execute("SELECT title FROM info").fetchone()[0], "Тест")
        self.assertEqual(h.bible_connection.execute("SELECT text FROM verses WHERE verse_key='001'").fetchone()[0], "Світле слово")
        self.assertEqual(read_web_db_manifest_entry(path)["dataVersion"], 1)
        self.assertTrue(h.bible_pending_changes)

    def test_legacy_module_edit_does_not_add_comment_or_change_schema(self):
        path = self.make_db(comments=False)
        h = self.harness
        h._load_bible_db(path)
        self.assertFalse(h.bible_comments_supported)
        self.assertEqual(str(h.bible_verse_comment.cget("state")), "disabled")
        h._replace_text(h.bible_verse_text, "Changed G1")
        self.assertTrue(h._save_bible_module(silent=True))
        columns = [r[1] for r in h.bible_connection.execute("PRAGMA table_info(verses)")]
        self.assertEqual(columns, ["verse_key", "text"])
        self.assertEqual(read_web_db_manifest_entry(path)["schemaVersion"], 3)


if __name__ == "__main__":
    unittest.main()
