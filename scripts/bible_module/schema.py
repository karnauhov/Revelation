from __future__ import annotations

import datetime as dt
import sqlite3
from collections.abc import Iterable

from .canon import CANONICAL_BOOKS, CANON_NAME, canonical_verse_rows

BIBLE_MODULE_SCHEMA_VERSION = 1
BIBLE_MODULE_DATA_VERSION_INITIAL = 1

DB_METADATA_TABLE_NAME = "db_metadata"
DB_METADATA_SCHEMA_VERSION_KEY = "schema_version"
DB_METADATA_DATA_VERSION_KEY = "data_version"
DB_METADATA_DATE_KEY = "date"

CORE_TABLES = (
    "db_metadata",
    "bible_modules",
    "module_sources",
    "books",
    "canonical_verses",
    "source_texts",
    "module_verses",
    "module_verse_links",
    "import_warnings",
)
TOKEN_TABLES = ("tokens", "token_strongs")
FORBIDDEN_FORM_OCCURRENCE_TABLES = (
    "word_forms",
    "word_form_occurrences",
    "strong_forms",
    "strong_form_occurrences",
)

CORE_INDEXES = (
    "idx_canonical_verses_canonical_ref",
    "idx_canonical_verses_sort_key",
    "idx_module_verse_links_canonical_verse_id",
    "idx_module_verses_source_text_sort_key",
)
TOKEN_INDEXES = (
    "idx_tokens_module_verse_token_order",
    "idx_token_strongs_strong",
    "idx_token_strongs_token_id",
)


CORE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS db_metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bible_modules (
  module_id TEXT PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  language TEXT NOT NULL,
  module_kind TEXT NOT NULL,
  canon TEXT NOT NULL,
  versification TEXT NOT NULL,
  license TEXT NOT NULL,
  source_summary TEXT NOT NULL,
  schema_version INTEGER NOT NULL,
  data_version INTEGER NOT NULL,
  built_at TEXT NOT NULL,
  CHECK (length(trim(module_id)) > 0),
  CHECK (length(trim(code)) > 0),
  CHECK (length(trim(module_kind)) > 0),
  CHECK (schema_version > 0),
  CHECK (data_version > 0)
);

CREATE TABLE IF NOT EXISTS module_sources (
  source_id TEXT PRIMARY KEY,
  module_id TEXT NOT NULL,
  title TEXT NOT NULL,
  source_url TEXT NOT NULL,
  source_version TEXT,
  license TEXT NOT NULL,
  checksum_sha256 TEXT NOT NULL,
  import_notes TEXT NOT NULL,
  FOREIGN KEY (module_id) REFERENCES bible_modules(module_id) ON DELETE CASCADE,
  CHECK (length(trim(source_id)) > 0),
  CHECK (length(trim(checksum_sha256)) = 64)
);

CREATE TABLE IF NOT EXISTS books (
  book_id INTEGER PRIMARY KEY,
  canonical_code TEXT NOT NULL UNIQUE,
  osis_code TEXT NOT NULL,
  title TEXT NOT NULL,
  testament TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  is_canonical INTEGER NOT NULL,
  CHECK (book_id > 0),
  CHECK (testament IN ('OT', 'NT')),
  CHECK (sort_order > 0),
  CHECK (is_canonical IN (0, 1))
);

CREATE TABLE IF NOT EXISTS canonical_verses (
  canonical_verse_id INTEGER PRIMARY KEY,
  canonical_ref TEXT NOT NULL UNIQUE,
  osis_ref TEXT NOT NULL,
  book_id INTEGER NOT NULL,
  chapter INTEGER NOT NULL,
  verse INTEGER NOT NULL,
  subverse TEXT NOT NULL DEFAULT '',
  sort_key INTEGER NOT NULL,
  FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE RESTRICT,
  CHECK (canonical_verse_id > 0),
  CHECK (chapter > 0),
  CHECK (verse > 0),
  CHECK (sort_key > 0)
);

CREATE TABLE IF NOT EXISTS source_texts (
  source_text_id TEXT PRIMARY KEY,
  module_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  code TEXT NOT NULL,
  scope TEXT NOT NULL,
  language TEXT NOT NULL,
  priority INTEGER NOT NULL,
  FOREIGN KEY (module_id) REFERENCES bible_modules(module_id) ON DELETE CASCADE,
  FOREIGN KEY (source_id) REFERENCES module_sources(source_id) ON DELETE CASCADE,
  UNIQUE (module_id, code),
  CHECK (length(trim(source_text_id)) > 0),
  CHECK (length(trim(code)) > 0)
);

CREATE TABLE IF NOT EXISTS module_verses (
  module_verse_id INTEGER PRIMARY KEY,
  source_text_id TEXT NOT NULL,
  native_ref TEXT NOT NULL,
  book_id INTEGER NOT NULL,
  chapter INTEGER NOT NULL,
  verse INTEGER NOT NULL,
  subverse TEXT NOT NULL DEFAULT '',
  text_plain TEXT NOT NULL,
  text_display TEXT NOT NULL,
  tokens_count INTEGER NOT NULL,
  sort_key INTEGER NOT NULL,
  FOREIGN KEY (source_text_id) REFERENCES source_texts(source_text_id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE RESTRICT,
  UNIQUE (source_text_id, native_ref),
  CHECK (chapter > 0),
  CHECK (verse > 0),
  CHECK (tokens_count >= 0),
  CHECK (sort_key > 0)
);

CREATE TABLE IF NOT EXISTS module_verse_links (
  module_verse_id INTEGER NOT NULL,
  canonical_verse_id INTEGER NOT NULL,
  link_kind TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  PRIMARY KEY (module_verse_id, canonical_verse_id),
  FOREIGN KEY (module_verse_id) REFERENCES module_verses(module_verse_id) ON DELETE CASCADE,
  FOREIGN KEY (canonical_verse_id) REFERENCES canonical_verses(canonical_verse_id) ON DELETE RESTRICT,
  CHECK (length(trim(link_kind)) > 0)
);

CREATE TABLE IF NOT EXISTS import_warnings (
  warning_id INTEGER PRIMARY KEY,
  source_id TEXT NOT NULL,
  severity TEXT NOT NULL,
  code TEXT NOT NULL,
  source_ref TEXT NOT NULL,
  message TEXT NOT NULL,
  raw_json TEXT NOT NULL,
  FOREIGN KEY (source_id) REFERENCES module_sources(source_id) ON DELETE CASCADE,
  CHECK (length(trim(severity)) > 0),
  CHECK (length(trim(code)) > 0)
);
"""


TOKEN_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tokens (
  token_id INTEGER PRIMARY KEY,
  module_verse_id INTEGER NOT NULL,
  source_text_id TEXT NOT NULL,
  token_order INTEGER NOT NULL,
  source_ref TEXT NOT NULL,
  text_type TEXT NOT NULL,
  surface TEXT NOT NULL,
  surface_normalized TEXT NOT NULL,
  surface_search TEXT NOT NULL,
  transliteration TEXT NOT NULL,
  lemma TEXT NOT NULL,
  morphology TEXT NOT NULL,
  gloss TEXT NOT NULL,
  raw_json TEXT NOT NULL,
  FOREIGN KEY (module_verse_id) REFERENCES module_verses(module_verse_id) ON DELETE CASCADE,
  FOREIGN KEY (source_text_id) REFERENCES source_texts(source_text_id) ON DELETE CASCADE,
  UNIQUE (module_verse_id, token_order),
  CHECK (token_order > 0),
  CHECK (length(trim(text_type)) > 0)
);

CREATE TABLE IF NOT EXISTS token_strongs (
  token_strong_id INTEGER PRIMARY KEY,
  token_id INTEGER NOT NULL,
  strong TEXT NOT NULL,
  raw_strong TEXT NOT NULL,
  role TEXT NOT NULL,
  segment_order INTEGER NOT NULL,
  segment_surface TEXT NOT NULL,
  is_primary INTEGER NOT NULL,
  FOREIGN KEY (token_id) REFERENCES tokens(token_id) ON DELETE CASCADE,
  CHECK (length(trim(strong)) > 1),
  CHECK (strong NOT GLOB '[GH]0[0-9]*'),
  CHECK (segment_order >= 0),
  CHECK (is_primary IN (0, 1))
);
"""


CORE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_canonical_verses_canonical_ref
  ON canonical_verses(canonical_ref);
CREATE INDEX IF NOT EXISTS idx_canonical_verses_sort_key
  ON canonical_verses(sort_key);
CREATE INDEX IF NOT EXISTS idx_module_verse_links_canonical_verse_id
  ON module_verse_links(canonical_verse_id);
CREATE INDEX IF NOT EXISTS idx_module_verses_source_text_sort_key
  ON module_verses(source_text_id, sort_key);
"""


TOKEN_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_tokens_module_verse_token_order
  ON tokens(module_verse_id, token_order);
CREATE INDEX IF NOT EXISTS idx_token_strongs_strong
  ON token_strongs(strong);
CREATE INDEX IF NOT EXISTS idx_token_strongs_token_id
  ON token_strongs(token_id);
"""


def now_utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def create_bible_module_schema(
    connection: sqlite3.Connection,
    *,
    include_token_tables: bool = True,
    seed_canon: bool = True,
    data_version: int = BIBLE_MODULE_DATA_VERSION_INITIAL,
    date_iso: str | None = None,
) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA user_version = {BIBLE_MODULE_SCHEMA_VERSION}")
    connection.executescript(CORE_SCHEMA_SQL)
    connection.executescript(CORE_INDEX_SQL)
    if include_token_tables:
        connection.executescript(TOKEN_SCHEMA_SQL)
        connection.executescript(TOKEN_INDEX_SQL)
    set_db_metadata(
        connection,
        schema_version=BIBLE_MODULE_SCHEMA_VERSION,
        data_version=data_version,
        date_iso=date_iso or now_utc_iso(),
    )
    if seed_canon:
        seed_canonical_books_and_verses(connection)


def set_db_metadata(
    connection: sqlite3.Connection,
    *,
    schema_version: int,
    data_version: int,
    date_iso: str,
) -> None:
    connection.executemany(
        """
        INSERT INTO db_metadata(key, value)
        VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        [
            (DB_METADATA_SCHEMA_VERSION_KEY, str(schema_version)),
            (DB_METADATA_DATA_VERSION_KEY, str(data_version)),
            (DB_METADATA_DATE_KEY, date_iso),
        ],
    )


def seed_canonical_books_and_verses(connection: sqlite3.Connection) -> None:
    connection.executemany(
        """
        INSERT INTO books(
          book_id,
          canonical_code,
          osis_code,
          title,
          testament,
          sort_order,
          is_canonical
        )
        VALUES(?, ?, ?, ?, ?, ?, 1)
        ON CONFLICT(book_id) DO UPDATE SET
          canonical_code = excluded.canonical_code,
          osis_code = excluded.osis_code,
          title = excluded.title,
          testament = excluded.testament,
          sort_order = excluded.sort_order,
          is_canonical = excluded.is_canonical
        """,
        [
            (
                book.book_id,
                book.canonical_code,
                book.osis_code,
                book.title,
                book.testament,
                book.sort_order,
            )
            for book in CANONICAL_BOOKS
        ],
    )
    connection.executemany(
        """
        INSERT INTO canonical_verses(
          canonical_verse_id,
          canonical_ref,
          osis_ref,
          book_id,
          chapter,
          verse,
          subverse,
          sort_key
        )
        VALUES(
          :canonical_verse_id,
          :canonical_ref,
          :osis_ref,
          :book_id,
          :chapter,
          :verse,
          :subverse,
          :sort_key
        )
        ON CONFLICT(canonical_verse_id) DO UPDATE SET
          canonical_ref = excluded.canonical_ref,
          osis_ref = excluded.osis_ref,
          book_id = excluded.book_id,
          chapter = excluded.chapter,
          verse = excluded.verse,
          subverse = excluded.subverse,
          sort_key = excluded.sort_key
        """,
        canonical_verse_rows(),
    )


def table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    return {str(row[0]) for row in rows}


def index_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index'"
    ).fetchall()
    return {str(row[0]) for row in rows}


def expected_table_names(*, include_token_tables: bool = True) -> tuple[str, ...]:
    if include_token_tables:
        return (*CORE_TABLES, *TOKEN_TABLES)
    return CORE_TABLES


def expected_index_names(*, include_token_tables: bool = True) -> tuple[str, ...]:
    if include_token_tables:
        return (*CORE_INDEXES, *TOKEN_INDEXES)
    return CORE_INDEXES


def read_db_metadata(connection: sqlite3.Connection) -> dict[str, str]:
    rows = connection.execute(
        "SELECT key, value FROM db_metadata ORDER BY key"
    ).fetchall()
    return {str(row[0]): str(row[1]) for row in rows}


def assert_no_form_occurrence_tables(existing_table_names: Iterable[str]) -> None:
    forbidden = set(existing_table_names).intersection(FORBIDDEN_FORM_OCCURRENCE_TABLES)
    if forbidden:
        names = ", ".join(sorted(forbidden))
        raise ValueError(f"Bible module schema must not contain form tables: {names}")


def insert_minimal_module_fixture(
    connection: sqlite3.Connection,
    *,
    module_id: str = "fixture_module",
    code: str = "FIXTURE",
    module_kind: str = "translation",
    source_id: str = "fixture_source",
    source_text_id: str = "fixture_text",
) -> None:
    connection.execute(
        """
        INSERT INTO bible_modules(
          module_id,
          code,
          title,
          language,
          module_kind,
          canon,
          versification,
          license,
          source_summary,
          schema_version,
          data_version,
          built_at
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            module_id,
            code,
            "Fixture Bible Module",
            "en",
            module_kind,
            CANON_NAME,
            "protestant",
            "test-only",
            "Fixture source",
            BIBLE_MODULE_SCHEMA_VERSION,
            1,
            "2026-05-23T00:00:00Z",
        ),
    )
    connection.execute(
        """
        INSERT INTO module_sources(
          source_id,
          module_id,
          title,
          source_url,
          source_version,
          license,
          checksum_sha256,
          import_notes
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source_id,
            module_id,
            "Fixture Source",
            "https://example.com/fixture",
            "fixture",
            "test-only",
            "0" * 64,
            "Fixture notes",
        ),
    )
    connection.execute(
        """
        INSERT INTO source_texts(
          source_text_id,
          module_id,
          source_id,
          code,
          scope,
          language,
          priority
        )
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """,
        (source_text_id, module_id, source_id, code, "Gen.1.1", "en", 1),
    )

