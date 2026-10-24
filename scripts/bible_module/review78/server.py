"""Loopback GET-only server for SHA-locked development packets."""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from scripts.bible_module.consensus76.io import canonical, read, sha, verify
from .build import PACKAGE, ROOT, SESSION, source_specs
from .contracts import GUARDS


class Store:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.manifest_path = self.directory / "manifest.json"
        self.manifest = read(self.manifest_path)
        self.manifest_sha256 = sha(self.manifest_path)
        for k, v in GUARDS.items():
            if self.manifest.get(k) != v:
                raise ValueError("Acceptance guard changed")
        protocol = self.manifest["protocol"]
        verify(protocol, ROOT)
        protocol_value = read(ROOT / protocol["path"])
        for key in ("source_runtime", "inputs"):
            verify(protocol_value[key], ROOT)
        source = read(ROOT / protocol_value["source_runtime"]["path"])
        inputs = read(ROOT / protocol_value["inputs"]["path"])
        for item in inputs["inputs"] + source["upstream_source"]:
            verify(item, ROOT)
        if source_specs() != source["source"]:
            raise ValueError("Viewer source no longer matches build lock")
        self.verify_local(self.manifest["index"])
        self.index = read(self.directory / "index.json")
        self.index["build_manifest_sha256"] = self.manifest_sha256
        self.by_ref = {p["target_ref"]: p for p in self.manifest["packets"]}
        if len(self.by_ref) != len(self.manifest["packets"]):
            raise ValueError("Duplicate packet reference")
        self.by_case = {c["case_id"]: c["target_ref"] for c in self.index["cases"]}

    def verify_local(self, item):
        path = (self.directory / item["path"]).resolve()
        if not path.is_relative_to(self.directory):
            raise ValueError("Packet path leaves workbench")
        verify({**item, "path": str(path)}, self.directory)
        return path

    def case(self, case_id):
        self.verify_snapshot()
        ref = self.by_case[case_id]
        item = self.by_ref[ref]
        packet = read(self.verify_local(item))
        if packet["target_ref"] != ref:
            raise ValueError("Packet reference mismatch")
        selected = next(c for c in packet["cases"] if c["case_id"] == case_id)
        return {"packet": packet, "case": selected, "packet_sha256": item["sha256"],
                "build_manifest_sha256": self.index["build_manifest_sha256"]}

    def verify_snapshot(self):
        if sha(self.manifest_path) != self.manifest_sha256:
            raise ValueError("Build manifest changed after viewer startup")
        self.verify_local(self.manifest["index"])


def handler(store):
    class Handler(BaseHTTPRequestHandler):
        def send(self, status, data, kind="application/json; charset=utf-8"):
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(data)

        def do_GET(self):
            try:
                url = urlsplit(self.path)
                assets = {"/": ("viewer.html", "text/html"), "/viewer.js": ("viewer.js", "text/javascript"), "/core.js": ("core.js", "text/javascript"), "/viewer.css": ("viewer.css", "text/css")}
                if url.path in assets:
                    file, mime = assets[url.path]
                    return self.send(200, (PACKAGE / file).read_bytes(), mime + "; charset=utf-8")
                if url.path == "/api/index":
                    store.verify_snapshot()
                    return self.send(200, canonical(store.index).encode("utf8"))
                if url.path == "/api/case":
                    query = parse_qs(url.query)
                    if set(query) != {"id"} or len(query["id"]) != 1:
                        raise KeyError("id")
                    return self.send(200, canonical(store.case(query["id"][0])).encode("utf8"))
                self.send(404, b'{"error":"not_found"}')
            except (KeyError, StopIteration):
                self.send(404, b'{"error":"unknown_case"}')
            except (ValueError, OSError) as error:
                self.send(409, canonical({"error": "stale_or_invalid_packet", "detail": str(error)}).encode("utf8"))

        do_HEAD = do_GET

        def do_POST(self):
            self.send(405, b'{"error":"read_only"}')

        do_PUT = do_DELETE = do_PATCH = do_POST

        def log_message(self, *_):
            pass

    return Handler


def serve(directory=SESSION / "build.v1", port=8878):
    store = Store(directory)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler(store))
    print("Review workbench: http://127.0.0.1:" + str(server.server_port), flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
