"""Compile LXX/TR verse and Strong posting lists for Revelation's allusion search."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sqlite3
import struct
import sys
import zlib
from array import array
from contextlib import closing
from pathlib import Path

if __package__:
    from .allusion_weight_policy import read_policy
else:  # The documented direct script entrypoint.
    from allusion_weight_policy import read_policy

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets/data"
INDEX_KEY = "allusion_index_v1"
TOKEN = re.compile(r"(?<!\S)[Gg]([0-9]+)(?!\S)")


def _bytes(typecode: str, values) -> bytes:
    items = array(typecode, values)
    if sys.byteorder != "little":
        items.byteswap()
    return items.tobytes()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compile_index(connection: sqlite3.Connection) -> bytes:
    """Read a consistent snapshot after metadata and corpus updates in its transaction."""
    canon = json.loads((ASSETS / "bible_verse_map.json").read_text(encoding="utf-8"))
    policy_version, weights = read_policy()
    count = canon["verses_count"]
    if max(count, len(weights) - 1) > 65535:
        raise ValueError("Corpus exceeds allusion index v1 capacity")
    rows = [[] for _ in range(count + 1)]
    terms = [[] for _ in weights]
    corpus_hash = hashlib.sha256()
    nonempty = 0
    seen = set()
    for key, text in connection.execute(
        "SELECT verse_key, text FROM verses WHERE trim(text) <> '' ORDER BY verse_key"
    ):
        if not isinstance(key, str) or not re.fullmatch("[0-9A-Za-z]{3}", key):
            raise ValueError(f"Invalid verse key {key}")
        ordinal = int(key, 36)
        if not 1 <= ordinal <= count or ordinal in seen:
            raise ValueError(f"Unknown or duplicate verse key {key}")
        seen.add(ordinal)
        corpus_hash.update((key + "\0" + text + "\n").encode("utf-8"))
        nonempty += 1
        for term in dict.fromkeys(map(int, TOKEN.findall(text))):
            if not 1 <= term < len(weights):
                raise ValueError(f"Unclassified Strong number G{term}")
            if weights[term] > 0:
                rows[ordinal].append(term)
                terms[term].append(ordinal)

    def offsets(groups):
        value = 0
        yield value
        for group in groups:
            value += len(group)
            yield value

    weight_bytes = _bytes("d", weights)
    payload = b"".join((
        weight_bytes, _bytes("I", offsets(rows)), _bytes("I", offsets(terms)),
        _bytes("H", (n for group in rows for n in group)),
        _bytes("H", (n for group in terms for n in group)),
    ))
    meta = dict(connection.execute(
        "SELECT key, value FROM db_metadata WHERE key IN ('schema_version','data_version','date')"
    ))
    canon_contract = json.dumps([[b["id"], b["chapters"]] for b in canon["books"]], separators=(",", ":"))
    header = json.dumps({
        "module": "lxx_tr", "schema": int(meta["schema_version"]),
        "revision": int(meta["data_version"]), "date": meta["date"],
        "corpus_sha256": corpus_hash.hexdigest(),
        "canon_sha256": _sha(canon_contract.encode()), "canon": canon_contract,
        "weights_sha256": _sha(weight_bytes), "policy": policy_version,
        "verses": count, "documents": nonempty, "terms": len(weights) - 1,
        "pairs": sum(map(len, rows)), "checksum": zlib.adler32(payload),
    }, separators=(",", ":"), sort_keys=True).encode()
    header += b" " * (-len(header) % 8)
    return b"ALX1" + struct.pack("<I", len(header)) + header + payload


def embed_index(connection: sqlite3.Connection) -> None:
    """Transport the derived bytes inside a text metadata entry, in the same release."""
    data = compile_index(connection)
    length, = struct.unpack_from("<I", data, 4)
    corpus_hash = json.loads(data[8:8 + length])["corpus_sha256"]
    connection.executemany("INSERT OR REPLACE INTO db_metadata(key,value) VALUES(?,?)", [
        (INDEX_KEY, base64.b64encode(data).decode("ascii")),
        ("allusion_corpus_sha256", corpus_hash),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / "web/db/bible_lxx_tr.sqlite")
    parser.add_argument("--output", type=Path, default=ASSETS / "allusion_index.bin")
    args = parser.parse_args()
    with closing(sqlite3.connect(args.db.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("BEGIN")
        data = compile_index(db)
    args.output.write_bytes(data)
    print(f"{args.output}: {len(data)} bytes")


if __name__ == "__main__":
    main()
