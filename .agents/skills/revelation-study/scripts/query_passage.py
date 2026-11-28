"""Read a shipped verse or run the project's allusion search on its bundled index."""

import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.content_tool.bible_map import BibleCatalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verse = commands.add_parser("verse", help="read one verse with its stored Strong tags")
    verse.add_argument("reference", help='e.g. "Rev 22:6"')
    verse.add_argument("--module", choices=("lxx_tr", "kjv", "ohienko_1988"), default="lxx_tr")
    search = commands.add_parser("allusions", help="run the Flutter engine without opening the app")
    search.add_argument("reference", help='first verse, e.g. "Rev 1:1"')
    search.add_argument("--length", type=int, default=1)
    search.add_argument("--scope", choices=("oldTestament", "newTestament", "wholeBible"), default="oldTestament")
    search.add_argument("--level", choices=("verse", "chapter", "book"), default="verse")
    search.add_argument("--limit", type=int, default=5, help="maximum results to print")
    args = parser.parse_args()

    catalog = BibleCatalog.load(ROOT)
    reference = catalog.parse_reference(args.reference)
    if reference is None:
        parser.error(f"Unknown reference: {args.reference}")
    book, chapter, number = reference
    try:
        key = catalog.key_for(book_id=book.id, chapter=chapter, verse=number)
    except ValueError as error:
        parser.error(str(error))

    module = args.module if args.command == "verse" else "lxx_tr"
    path = ROOT / "web" / "db" / f"bible_{module}.sqlite"
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        metadata = dict(db.execute(
            "SELECT key, value FROM db_metadata "
            "WHERE key IN ('schema_version', 'data_version', 'date', 'allusion_corpus_sha256')"
        ))
        if args.command == "verse":
            row = db.execute("SELECT text FROM verses WHERE verse_key = ?", (key,)).fetchone()
            if row is None or not row[0].strip():
                parser.exit(1, f"No verse text for {key} in {path.name}\n")
            print(f"{book.code} {chapter}:{number} | {key} | {path.name} v{metadata['data_version']}")
            print(row[0])
            return 0

    if args.limit < 1:
        parser.error("--limit must be positive")
    if not 1 <= args.length <= 77:
        parser.error("--length must be between 1 and 77 verses")
    flutter = shutil.which("flutter")
    if flutter is None:
        parser.error("flutter is required for allusions")
    query = dict(key=key, length=args.length, scope=args.scope, level=args.level,
                 limit=args.limit, metadata=metadata)
    runner = Path(__file__).with_name("allusions_test.dart")
    run = subprocess.run(
        [flutter, "test", "--no-pub", "--reporter", "expanded", str(runner)],
        cwd=ROOT,
        env={**os.environ, "REVELATION_STUDY_QUERY": json.dumps(query)},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    sys.stdout.buffer.write(run.stdout)
    return run.returncode


if __name__ == "__main__":
    sys.exit(main())
