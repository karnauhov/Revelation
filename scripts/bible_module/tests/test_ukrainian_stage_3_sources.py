from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.bible_module import ukrainian_stage_3_sources as stage3


class UkrainianStage3SourceLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lock = stage3.load_source_lock()

    def test_lock_structure_roles_and_unique_source_ids(self) -> None:
        self.assertEqual(stage3.validate_source_lock(self.lock), [])
        self.assertNotIn(b"\r", stage3.SOURCE_FILES_CSV_PATH.read_bytes())
        sources = self.lock["sources"]
        self.assertIsInstance(sources, list)
        self.assertEqual(len(sources), 14)
        source_ids = [source["source_id"] for source in sources]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(set(source_ids), stage3.EXPECTED_SOURCE_IDS)
        roles = {source["role_id"] for source in sources}
        self.assertTrue(stage3.REQUIRED_ROLES <= roles)
        for source in sources:
            with self.subTest(source_id=source["source_id"]):
                self.assertFalse(stage3.REQUIRED_ENTRY_FIELDS - set(source))
                self.assertRegex(source["sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(source["bytes"], 0)
                self.assertTrue(source["source_page_url"].startswith("https://"))
                self.assertTrue(source["download_url"].startswith("https://"))
                self.assertTrue(source["license_url"].startswith("https://"))
                self.assertFalse(Path(source["local_path"]).is_absolute())
                self.assertTrue(source["local_path"].startswith("../../source_cache/"))

    def test_exact_revisions_commits_tags_and_resolved_placeholders(self) -> None:
        by_id = {
            source["source_id"]: source for source in self.lock["sources"]
        }
        self.assertEqual(
            by_id["commons_ohienko_1988_scan"]["sha256"],
            stage3.COMMONS_SHA256,
        )
        self.assertEqual(
            by_id["openscriptures_oshb_v2_2"]["pin"],
            {
                "type": "git_tag_commit",
                "tag": stage3.OSHB_TAG,
                "value": stage3.OSHB_COMMIT,
            },
        )
        self.assertEqual(
            by_id["unfoldingword_ugnt_v0_34"]["pin"],
            {
                "type": "git_tag_commit",
                "tag": stage3.UGNT_TAG,
                "value": stage3.UGNT_COMMIT,
            },
        )
        self.assertEqual(
            by_id["internet_archive_ohienko_1988_scan"]["pin"],
            {
                "type": "internet_archive_file_sha1",
                "value": "baf96568afa4c964f692cbf6509f50d69fbf4289",
                "md5": "29ca8fc8bf1593a50511be9d526ed291",
            },
        )
        self.assertEqual(
            by_id["tanach_us_uxlc_2_5_27_6"]["pin"],
            {
                "type": "product_version_build_sha256",
                "version": "UXLC 2.5",
                "build": "27.6",
                "text_date": "2026-04-01",
            },
        )
        self.assertEqual(
            by_id["crosswire_kjv_3_1"]["pin"],
            {"type": "git_commit", "value": stage3.CROSSWIRE_KJV_COMMIT},
        )
        for source_id in (
            "step_tahot_gen_deu",
            "step_tahot_jos_est",
            "step_tahot_job_sng",
            "step_tahot_isa_mal",
            "step_tagnt_mat_jhn",
            "step_tagnt_act_rev",
            "step_tvtms",
        ):
            self.assertEqual(
                by_id[source_id]["pin"],
                {"type": "git_commit", "value": stage3.STEPBIBLE_COMMIT},
            )
        revisions = by_id["wikisource_ohienko_1988_revisions"]["revision_lock"]
        self.assertEqual(len(revisions), 1540)
        self.assertEqual(revisions[0]["revision_id"], 442425)
        self.assertEqual(revisions[1]["revision_id"], 960013)
        self.assertEqual(revisions[2]["revision_id"], 107971)
        self.assertEqual(revisions[-1]["revision_id"], 108567)
        self.assertEqual(
            by_id["wikisource_ohienko_1988_revisions"]["pin"][
                "revision_lock_sha256"
            ],
            stage3.WIKISOURCE_REVISION_LOCK_SHA256,
        )
        self.assertEqual(
            stage3._revision_lock_sha256(revisions),
            stage3.WIKISOURCE_REVISION_LOCK_SHA256,
        )
        self.assertEqual(
            by_id["wikisource_ohienko_1988_revisions"]["bytes"],
            stage3.WIKISOURCE_BUNDLE_BYTES,
        )
        self.assertEqual(
            by_id["wikisource_ohienko_1988_revisions"]["sha256"],
            stage3.WIKISOURCE_BUNDLE_SHA256,
        )
        placeholders = self.lock["resolved_placeholders"]
        self.assertEqual(placeholders["commons_scan_sha256"], stage3.COMMONS_SHA256)
        self.assertIn("1540 revisions", placeholders["wikisource_revision_lock"])

    def test_duplicate_source_id_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.lock)
        manifest["sources"][1]["source_id"] = manifest["sources"][0]["source_id"]
        errors = stage3.validate_source_lock(manifest)
        self.assertTrue(any("duplicate source_id" in error for error in errors))

    def test_unpinned_latest_and_branch_urls_are_rejected(self) -> None:
        for bad_url in (
            "https://example.test/releases/latest/source.zip",
            "https://example.test/repository/main/source.txt",
            "https://example.test/source.zip?ref=HEAD",
        ):
            with self.subTest(url=bad_url):
                manifest = copy.deepcopy(self.lock)
                manifest["sources"][0]["download_url"] = bad_url
                errors = stage3.validate_source_lock(manifest)
                self.assertTrue(
                    any("unpinned latest/branch URL" in error for error in errors)
                )

    def test_late_ubt_or_mixed_translation_source_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.lock)
        source = next(
            source
            for source in manifest["sources"]
            if source["role_id"] == "ukrainian_machine_transcription"
        )
        source["edition_year"] = 1991
        source["translation_id"] = "ubt_1991"
        errors = stage3.validate_source_lock(manifest)
        self.assertTrue(any("must be edition 1988" in error for error in errors))
        self.assertTrue(any("late/mixed UBT source" in error for error in errors))

    def test_manual_controls_cannot_masquerade_as_machine_inputs(self) -> None:
        manifest = copy.deepcopy(self.lock)
        manifest["manual_controls"][0]["sha256"] = "0" * 64
        errors = stage3.validate_source_lock(manifest)
        self.assertTrue(
            any("must not masquerade as a locked file" in error for error in errors)
        )

    def test_locked_exact_edition_sources_are_sufficient_for_future_footnotes(
        self,
    ) -> None:
        audit = json.loads(
            stage3.FOOTNOTE_SOURCE_AUDIT_PATH.read_text(encoding="utf-8")
        )
        by_id = {
            source["source_id"]: source for source in self.lock["sources"]
        }
        self.assertEqual(
            audit["status"],
            "sources_sufficient_for_future_footnote_extraction",
        )
        self.assertTrue(audit["source_lock_unchanged"])
        self.assertEqual(audit["machine_source_count"], 14)
        self.assertEqual(
            audit["source_lock_sha256"],
            stage3.sha256_file(stage3.SOURCE_LOCK_PATH),
        )

        scan = audit["print_reference"]
        locked_scan = by_id[scan["source_id"]]
        self.assertEqual(scan["edition_year"], 1988)
        self.assertEqual(scan["locked_pages"], 1538)
        self.assertEqual(scan["bytes"], locked_scan["bytes"])
        self.assertEqual(scan["sha256"], locked_scan["sha256"])

        transcription = audit["machine_transcription"]
        locked_transcription = by_id[transcription["source_id"]]
        self.assertEqual(transcription["revision_count"], 1540)
        self.assertEqual(transcription["proofread_page_revision_count"], 1538)
        self.assertEqual(
            transcription["revision_lock_sha256"],
            locked_transcription["pin"]["revision_lock_sha256"],
        )
        self.assertEqual(transcription["sha256"], locked_transcription["sha256"])
        self.assertTrue(transcription["all_revision_contents_present"])
        markers = transcription["marker_inventory"]
        self.assertEqual(
            markers["opening_ref"]["occurrences"],
            markers["closing_ref"]["occurrences"]
            + markers["self_closing_ref"]["occurrences"],
        )
        self.assertGreater(markers["reflist"]["occurrences"], 0)
        self.assertGreater(markers["anchor"]["occurrences"], 0)
        self.assertEqual(
            audit["sufficiency"],
            {
                "exact_print_pages_locked": True,
                "all_proofread_page_revisions_locked_with_content": True,
                "footnote_carriers_present": True,
                "additional_source_required": False,
            },
        )
        self.assertIn("no footnote was extracted", audit["scope_limit"])


class UkrainianStage3FailClosedFetchTests(unittest.TestCase):
    def _entry(self, payload: bytes) -> dict[str, object]:
        return {
            "source_id": "fixture",
            "download_url": "https://example.test/source.bin",
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "acquisition": {"kind": "https_file", "max_redirects": 5},
        }

    def test_wrong_size_and_sha256_fail_before_replacing_valid_cache(self) -> None:
        original = b"locked source\n"
        for corrupt in (b"short", b"corrupt source"):
            with self.subTest(corrupt=corrupt):
                with tempfile.TemporaryDirectory() as temp_dir:
                    target = Path(temp_dir) / "source.bin"
                    target.write_bytes(original)
                    entry = self._entry(original)

                    def fake_download(**kwargs: object) -> dict[str, object]:
                        Path(kwargs["target_path"]).write_bytes(corrupt)
                        return {"status": 200, "redirect_chain": []}

                    with mock.patch.object(stage3, "_download_once", fake_download):
                        with self.assertRaises(stage3.SourceLockError):
                            stage3._fetch_https_file(
                                entry,
                                target_path=target,
                                force=True,
                                offline=False,
                                max_attempts=1,
                                sleep=lambda _: None,
                            )
                    self.assertEqual(target.read_bytes(), original)

    def test_offline_valid_cache_hit_never_opens_network(self) -> None:
        payload = b"offline fixture\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "source.bin"
            target.write_bytes(payload)
            with mock.patch.object(
                stage3,
                "_download_once",
                side_effect=AssertionError("network must not be used"),
            ):
                result = stage3._fetch_https_file(
                    self._entry(payload),
                    target_path=target,
                    force=False,
                    offline=True,
                    max_attempts=1,
                    sleep=lambda _: None,
                )
            self.assertEqual(result["status"], "cache_hit")
            self.assertEqual(result["attempts"], [])

    def test_retry_is_bounded_and_uses_controlled_backoff(self) -> None:
        payload = b"retry fixture\n"
        sleeps: list[float] = []
        calls = 0

        def fake_download(**kwargs: object) -> dict[str, object]:
            nonlocal calls
            calls += 1
            if calls < 3:
                raise stage3._AttemptError(
                    "HTTP 429",
                    retryable=True,
                    details={"status": 429, "redirect_chain": []},
                )
            Path(kwargs["target_path"]).write_bytes(payload)
            return {"status": 200, "redirect_chain": []}

        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "source.bin"
            with mock.patch.object(stage3, "_download_once", fake_download):
                result = stage3._fetch_https_file(
                    self._entry(payload),
                    target_path=target,
                    force=False,
                    offline=False,
                    max_attempts=3,
                    sleep=sleeps.append,
                )
        self.assertEqual(calls, 3)
        self.assertEqual(sleeps, [2.0, 4.0])
        self.assertEqual(len(result["attempts"]), 3)

    def test_redirect_chain_is_recorded_and_https_only_is_enforced(self) -> None:
        payload = b"redirect fixture\n"

        def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            header_path = Path(command[command.index("--dump-header") + 1])
            target_path = Path(command[command.index("--output") + 1])
            header_path.write_text(
                "HTTP/1.1 302 Found\r\n"
                "Location: https://cdn.example.test/source.bin\r\n\r\n"
                "HTTP/1.1 200 OK\r\n"
                f"Content-Length: {len(payload)}\r\n\r\n",
                encoding="iso-8859-1",
            )
            target_path.write_bytes(payload)
            output = json.dumps(
                {
                    "url_effective": "https://cdn.example.test/source.bin",
                    "http_code": 200,
                    "num_redirects": 1,
                    "size_download": len(payload),
                    "ssl_verify_result": 0,
                    "curl_version": "libcurl/test Schannel",
                    "certs": "",
                    "remote_ip": "192.0.2.1",
                    "http_version": "1.1",
                    "time_total": 0.1,
                }
            )
            self.assertIn("--proto-redir", command)
            self.assertEqual(command[command.index("--proto-redir") + 1], "=https")
            self.assertEqual(command[command.index("--max-redirs") + 1], "2")
            return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "source.bin"
            with mock.patch.object(stage3.subprocess, "run", fake_run):
                metadata = stage3._curl_request_once(
                    url="https://example.test/source.bin",
                    target_path=target,
                    max_redirects=2,
                    expected_bytes=len(payload),
                )
            self.assertEqual(target.read_bytes(), payload)
        self.assertEqual(metadata["redirect_count"], 1)
        self.assertEqual(metadata["redirect_chain"][0]["status"], 302)
        with self.assertRaises(stage3._AttemptError):
            stage3._curl_request_once(
                url="http://example.test/source.bin",
                target_path=Path("unused"),
                max_redirects=2,
                expected_bytes=len(payload),
            )


if __name__ == "__main__":
    unittest.main()
