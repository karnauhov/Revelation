"""Search locally held study PDFs and keep their page locators. Requires pdftotext."""

import argparse
import hashlib
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_LIBRARY = Path.home() / "Downloads" / "Revelation"
INDEX = ROOT / ".build" / "revelation-study" / "pages.sqlite"


def default_books(library):
    commentary = library / "revelation-commentary-facebook"
    chapters = sorted(commentary.glob("Facebook-Comm-on-Rev-*.pdf"))
    present = {
        int(match[1]) for path in chapters
        if (match := re.search(r"Rev-(\d+)", path.stem))
    }
    missing = sorted(set(range(1, 23)) - present)
    if missing:
        print("Missing local chapter files:", ", ".join(map(str, missing)))
    return [
        *chapters,
        library / "Revelation-Outline.pdf",
        library / "Revelation-Translation.pdf",
    ]


def build_index(index, paths):
    paths = sorted({path.resolve(strict=True) for path in paths})
    index.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=index.parent) as temp_dir:
        temporary = Path(temp_dir) / "pages.sqlite"
        db = sqlite3.connect(temporary)
        try:
            db.execute("CREATE TABLE sources(id INTEGER PRIMARY KEY, path TEXT, sha256 TEXT, page_count INTEGER)")
            db.execute("CREATE VIRTUAL TABLE pages USING fts5(source_id UNINDEXED, page UNINDEXED, body)")
            for path in paths:
                with path.open("rb") as stream:
                    digest = hashlib.file_digest(stream, "sha256").hexdigest()
                extraction = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", str(path), "-"],
                    check=True, stdout=subprocess.PIPE,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                pages = extraction.stdout.decode("utf-8").removesuffix("\f").split("\f")
                if not any(page.strip() for page in pages):
                    raise ValueError(f"PDF needs a separate transcription: {path}")
                cursor = db.execute(
                    "INSERT INTO sources(path,sha256,page_count) VALUES (?,?,?)",
                    (str(path), digest, len(pages)),
                )
                db.executemany(
                    "INSERT INTO pages(source_id,page,body) VALUES (?,?,?)",
                    ((cursor.lastrowid, page, body) for page, body in enumerate(pages, 1)),
                )
            db.commit()
            print(f"{len(paths)} files, {db.execute('SELECT COUNT(*) FROM pages').fetchone()[0]} pages")
        finally:
            db.close()
        os.replace(temporary, index)


def search(index, phrase):
    # A literal phrase, including numeric components of verse references.
    expression = '"' + phrase.replace('"', '""') + '"'
    db = sqlite3.connect(index.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        rows = db.execute(
            """SELECT sources.path, pages.page, snippet(pages, 2, '[', ']', '...', 18)
               FROM pages JOIN sources ON sources.id = pages.source_id
               WHERE pages MATCH ? ORDER BY sources.path, pages.rowid""",
            (expression,),
        )
        for path, page, excerpt in rows:
            compact = " ".join(excerpt.split())
            print(f"{Path(path).name} | PDF p. {page} | {compact}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=INDEX)
    subcommands = parser.add_subparsers(dest="command", required=True)
    build = subcommands.add_parser("build")
    build.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    build.add_argument("--extra", type=Path, nargs="+", default=[])
    query = subcommands.add_parser("search")
    query.add_argument("phrase")
    args = parser.parse_args()
    if args.command == "build":
        downloads = sorted((INDEX.parent / "research-pdfs").glob("*.pdf"))
        build_index(args.index, default_books(args.library) + downloads + args.extra)
    else:
        search(args.index, args.phrase)


if __name__ == "__main__":
    main()
