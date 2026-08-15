"""Evidence-first Ukrainian Strong alignment, stage 7.

This command intentionally fails closed.  It can freeze and verify the exact
stage-6 texts/comments, reparse the locked original-language controls, import
licensed manual bridges and prepare a book-balanced annotation panel.  It does
not emit production Strong assignments until a genuinely reviewed gold set
and its calibration gate exist.

The rejected 2026-08-01 experiment is read only for negative counterexamples
and descriptive baseline auditing.  Its positions and confidence labels never
vote in an alignment.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile
from typing import Any, Iterable, Iterator, Mapping, Sequence
import xml.etree.ElementTree as ET
import zipfile

if __package__ in {None, ""}:  # pragma: no cover - direct script convenience
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    TOKENIZER_VERSION,
    comparison_form,
    exact_word_tokens,
    normalize_strong,
    validate_versioned_alignment_overrides,
    sha256_lines,
    sha256_text,
    stable_json,
    validate_exact_partition,
)
from scripts.bible_module.ukrainian_stage_7_gold import (
    GOLD_PREPARATION_MANIFEST,
    GOLD_WORKFLOW_VERSION,
    validated_finalized_gold_lock,
)
from scripts.bible_module.ukrainian_stage_7_candidates import (
    BridgeTargetBundle,
    generate_candidate_only_artifacts,
)
from scripts.bible_module.ukrainian_stage_7_statistical import (
    STATISTICAL_CONTRACT_VERSION,
    STATISTICAL_GENERATOR_ID,
    generate_statistical_candidate_artifacts,
)
from scripts.bible_module.ukrainian_stage_7_contextual import (
    CONTEXTUAL_CONTRACT_VERSION,
    CONTEXTUAL_GENERATOR_ID,
    MODEL_FILES as CONTEXTUAL_MODEL_FILES,
    MODEL_ID as CONTEXTUAL_MODEL_ID,
    MODEL_LICENSE as CONTEXTUAL_MODEL_LICENSE,
    MODEL_REPOSITORY_URL as CONTEXTUAL_MODEL_REPOSITORY_URL,
    MODEL_REVISION as CONTEXTUAL_MODEL_REVISION,
    MODEL_SNAPSHOT_CONTRACT_SHA256,
    RUNTIME_ENVIRONMENT_LOCKS as CONTEXTUAL_RUNTIME_ENVIRONMENT_LOCKS,
    RUNTIME_INSTALL_REPORT_SHA256,
    RUNTIME_PACKAGE_CONTRACTS as CONTEXTUAL_RUNTIME_PACKAGE_CONTRACTS,
    generate_contextual_artifacts,
    validate_contextual_generator_registry,
    validate_model_snapshot,
    validate_runtime_install_report,
)
from scripts.bible_module.ukrainian_stage_7_author_comments import (
    OUTPUT_NAME as AUTHOR_COMMENT_OUTPUT_NAME,
    generate_author_comment_evidence,
    validate_author_comment_evidence_bundle,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE_CACHE = ROOT / "scripts/bible_module/source_cache"
CONTEXTUAL_MODEL_SNAPSHOT = (
    SOURCE_CACHE
    / "awesome_align_with_co_777756717e1fa9556e304d4d5db173ee386b9c16"
)
CONTEXTUAL_RUNTIME_ROOT = (
    SOURCE_CACHE / "contextual_runtime_min_transformers_4_57_6_py312_win_amd64"
)
CONTEXTUAL_RUNTIME_PACKAGES = CONTEXTUAL_RUNTIME_ROOT / "packages"
CONTEXTUAL_RUNTIME_INSTALL_REPORT = (
    CONTEXTUAL_RUNTIME_ROOT / "pip-install-report.json"
)
STAGE3_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_3_20260801"
STAGE4_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_4_20260801"
STAGE4_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_4_20260801"
STAGE5_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_5_20260801"
STAGE5_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_5_20260801"
STAGE6_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_6_20260801"
STAGE6_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_6_20260801"
LEGACY_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_7_experiment_20260801"
LEGACY_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_7_experiment_20260801"
WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_7_20260801"
REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_7_20260801"

CLEAR = SOURCE_CACHE / "clear_bible_alignments"
CLEAR_V010 = SOURCE_CACHE / "clear_bible_alignments_v0_1_0"
LOCAL_DB = Path.home() / "Documents/revelation/db"

CANDIDATE_BRIDGE_TARGET_BUNDLES = (
    BridgeTargetBundle(
        "RUSSYN",
        "OT",
        CLEAR / "data/rus/targets/RUSSYN/ot_RUSSYN.tsv",
        "clear_russyn_ot",
    ),
    BridgeTargetBundle(
        "RUSSYN",
        "NT",
        CLEAR / "data/rus/targets/RUSSYN/nt_RUSSYN.tsv",
        "clear_russyn_nt",
    ),
    BridgeTargetBundle(
        "YLT",
        "OT",
        CLEAR / "data/eng/targets/YLT/ot_YLT.tsv",
        "clear_ylt_ot",
    ),
    BridgeTargetBundle(
        "YLT",
        "NT",
        CLEAR_V010 / "data/targets/SBLGNT-YLT.tsv",
        "clear_ylt_nt_v010_transfer",
    ),
)

LOCAL_DB_LOCKS = {
    "revelation_uk.sqlite": {
        "sha256": "3b489b074aa4a71dee2817a6c8a8fb290f7ca8f445ff9e890f131d2a2da0496b",
        "bytes": 692_224,
    },
    "bible_lxx_tr.sqlite": {
        "sha256": "443ab95f6fe54c3a803665e935a21bb862cdc97346ace6fa03d1d9c100bf3926",
        "bytes": 12_840_960,
    },
    "bible_kjv.sqlite": {
        "sha256": "b105f174c37c6703b71831a99ff838fed3439b84132c743bd3b58b37a326c780",
        "bytes": 6_733_824,
    },
}

STAGE6_TEXT = STAGE6_WORK / "synthesized_text.jsonl"
STAGE6_COMMENTS = STAGE6_WORK / "target_comments.jsonl"
STAGE6_FOOTNOTE_DEFINITIONS = STAGE6_WORK / "footnote_definitions.jsonl"
STAGE6_FOOTNOTE_USES = STAGE6_WORK / "footnote_uses.jsonl"
STAGE6_HEADING_FOOTNOTES = STAGE6_WORK / "heading_footnotes.jsonl"
STAGE6_MANIFEST = STAGE6_REPORT / "synthesized_text.manifest.json"
EXPECTED_STAGE6_TEXT_SHA256 = "e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf"
EXPECTED_STAGE6_MANIFEST_SHA256 = "75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af"
EXPECTED_STAGE6_COMMENT_SHA256 = "5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4"
EXPECTED_STAGE6_FOOTNOTE_DEFINITIONS_SHA256 = "4e69616e865d1e048391b6059eb622250570f1562b5a257a7a93c67edef2e5e7"
EXPECTED_STAGE6_FOOTNOTE_USES_SHA256 = "e86d3136a8760833b1910177c323896f02710ff9515391a6e4aae9b6d4798449"
EXPECTED_STAGE6_HEADING_FOOTNOTES_SHA256 = "b06c705bf8c7ff5753dd4609cad73441de4cada296d5ccea2aff20ee3e31e92a"
EXPECTED_STAGE5_FORWARD_SHA256 = "5959d3af5422dbf8a8bed95e106c4379a55883a4f9972708c330355aed3e866f"
EXPECTED_STAGE5_REVERSE_SHA256 = "0870dd982d4eed3212610e8d1d127e55015568c11e8c0dcdcb26ddb38a27e40a"
EXPECTED_STAGE5_FOOTNOTE_SHA256 = "c1e21b8566d1b3fda8328d20374eaefe4c2a547613eb2749bf11b90e69aa678a"
EXPECTED_LEGACY_SNAPSHOT_SHA256 = "d3a6371d2371a48c33fb7b756e0ef4e39f6815701f52bdd6c6eb714c010c6f4b"
EXPECTED_TARGET_COUNT = 31_102
MAPPING_CONTRACT = "oh1988-kjv-protestant-v1"

ORIGINAL_FILES = (
    ("step_tahot_gen_deu", "TAHOT", SOURCE_CACHE / "step_tahot_gen_deu.txt"),
    ("step_tahot_jos_est", "TAHOT", SOURCE_CACHE / "step_tahot_jos_est.txt"),
    ("step_tahot_job_sng", "TAHOT", SOURCE_CACHE / "step_tahot_job_sng.txt"),
    ("step_tahot_isa_mal", "TAHOT", SOURCE_CACHE / "step_tahot_isa_mal.txt"),
    ("step_tagnt_mat_jhn", "TAGNT", SOURCE_CACHE / "step_tagnt_mat_jhn.txt"),
    ("step_tagnt_act_rev", "TAGNT", SOURCE_CACHE / "step_tagnt_act_rev.txt"),
)
STEP_COMMIT = "b9dcc831a98e0fd6f3c7e122be9ff68377c310c0"
ORIGINAL_AUDIT_DIGESTS = {
    "TAHOT.canonical_rows": "83852852efe3663f1e274904aefd91d58b95e862b1430f59b609112c0d2f574d",
    "TAHOT.locators": "ca0cfd24613a041aac6d5dfde225ae8a97edbda255f020f2298046e4c4a4ad88",
    "TAHOT.projection": "a3c384caaf2aa1a102df0f62b3bc0586c76c051ad2fa233dac4047ce9eaabb35",
    "TAHOT.parent_ids": "1080a72246dbaa85fd46b2b54f634becdfb30ee9bd365b5f4c1657cfde97d4a3",
    "TAHOT.component_ids": "517e3cd10b14621a35f2b813d18adc5f57ee14fdc5453d36a2b7eac5b3083429",
    "TAGNT.canonical_rows": "b9e3f7f1bcde952358e27d2b225bcc2033868474cd969f2c87a761cc508d19bd",
    "TAGNT.locators": "97358f0bcfc41225c46f970c5b4666b19c2c2df32d88f5f9ad8ed438e057bdd8",
    "TAGNT.projection": "aef26d1f30bedb1dc56bd63a8e1ee06a99f76fa4bcad4570c282c6aa59fe3734",
    "TAGNT.parent_ids": "930c907942a368d49d2ea888961ab252911a14d1a5b14e42bc08c94a922a123d",
    "TAGNT.component_ids": "2dbe490bcb28e1d7db20805c794718ed24beb4412ca006a2ed9d6567294b593c",
}

CONTROL_SOURCES = {
    "openscriptures_oshb_v2_2": {
        "path": SOURCE_CACHE / "openscriptures_morphhb_v2_2.zip",
        "sha256": "dac2d0325c59f6cd22839f2ef6345544a85b50c9d657788672e7638fa11abecb",
        "version": "6a5db284c715c18b239422e57bb89684e6a19f00",
    },
    "tanach_us_uxlc_2_5_27_6": {
        "path": SOURCE_CACHE / "tanach_us_uxlc_2_5_27_6.zip",
        "sha256": "1bc6e006f43d3b18f2f718cefa3aa4774cac2c54092c28d173dd61996c43a050",
        "version": "UXLC-2.5-build-27.6",
    },
    "unfoldingword_ugnt_v0_34": {
        "path": SOURCE_CACHE / "unfoldingword_ugnt_v0_34.zip",
        "sha256": "07318be27d0027146a62363c20ffedd0db695d7680f4b32c8ae8bd3020a29d00",
        "version": "fc95b2b8aad08bb65ab54628ab685413a1139e97",
    },
}

ACTS_15_34_EVIDENCE_SOURCES = {
    "scrivener_bezae_1864": {
        "path": SOURCE_CACHE / "uk7_codex_bezae_scrivener_1864.pdf",
        "bytes": 41_768_131,
        "sha256": "3dc647913843508b3f35596c416f4cc17ab000daa603a7022d53e18462d5f49c",
    },
    "bezae_greek_xml_v1_03": {
        "path": SOURCE_CACHE / "uk7_bezae_greek_v1_03.xml",
        "bytes": 3_087_572,
        "sha256": "766ff8ed797df55615a1277febed304e22138f7e7a8d2c24c7bcf6d0315859b0",
        "fragment_start": 2_877_068,
        "fragment_end": 2_877_546,
        "fragment_sha256": "501ff93f07603c8a178f09a00a20937faa02a0fac43cd076bad64e1da687d335",
    },
    "clementine_vulgate_1598_usfx": {
        "path": SOURCE_CACHE / "uk7_latvuc_usfx.zip",
        "bytes": 3_714_434,
        "sha256": "e8202b9f6d723876e9a6f80114d52eb109dedec2433bff2bda305a741f141fdc",
        "member": "latVUC_usfx.xml",
        "member_bytes": 11_445_332,
        "member_sha256": "f572302e98d5747f701421a74276f9cde5044db7018fb6f24060eebb02c2c15b",
        "verse_text": "Visum est autem Sil\u00e6 ibi remanere: Judas autem solus abiit Jerusalem.",
        "verse_utf8_bytes": 70,
        "verse_sha256": "8b8fefaabef426fbe04dc799ed5832382b05e41d2e32f3871e92d23fc1eadda2",
    },
}
EXPECTED_CONTROL_TOKEN_SHA256 = (
    "190a4634a9986b04675904c1d2ca7f3f5a412cd6e15776e1193a4bd3612e6f4c"
)
EXPECTED_CONTROL_CROSSWALK_SHA256 = (
    "e2e65a31ebd6a3c4bd7350ce3cd80b25ede8ee74cd8b38c411628cfedf0d8ce0"
)

BOOKS = (
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam",
    "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov",
    "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos",
    "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Mat",
    "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil",
    "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb", "Jas",
    "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev",
)
BOOK_NUMBER = {book: index + 1 for index, book in enumerate(BOOKS)}
NUMBER_BOOK = {index + 1: book for index, book in enumerate(BOOKS)}

SOURCE_BOOK = {
    "Gen": "Gen", "Exo": "Exod", "Lev": "Lev", "Num": "Num", "Deu": "Deut",
    "Jos": "Josh", "Jdg": "Judg", "Rut": "Ruth", "1Sa": "1Sam", "2Sa": "2Sam",
    "1Ki": "1Kgs", "2Ki": "2Kgs", "1Ch": "1Chr", "2Ch": "2Chr", "Ezr": "Ezra",
    "Neh": "Neh", "Est": "Esth", "Job": "Job", "Psa": "Ps", "Pro": "Prov",
    "Ecc": "Eccl", "Sng": "Song", "Isa": "Isa", "Jer": "Jer", "Lam": "Lam",
    "Ezk": "Ezek", "Dan": "Dan", "Hos": "Hos", "Jol": "Joel", "Amo": "Amos",
    "Oba": "Obad", "Jon": "Jonah", "Mic": "Mic", "Nam": "Nah", "Hab": "Hab",
    "Zep": "Zeph", "Hag": "Hag", "Zec": "Zech", "Mal": "Mal", "Mat": "Mat",
    "Matt": "Mat", "Mrk": "Mark", "Luk": "Luke", "Jhn": "John", "Act": "Acts",
    "Rom": "Rom", "1Co": "1Cor", "2Co": "2Cor", "Gal": "Gal", "Eph": "Eph",
    "Php": "Phil", "Col": "Col", "1Th": "1Thess", "2Th": "2Thess", "1Ti": "1Tim",
    "2Ti": "2Tim", "Tit": "Titus", "Phm": "Phlm", "Heb": "Heb", "Jas": "Jas",
    "1Pe": "1Pet", "2Pe": "2Pet", "1Jn": "1John", "2Jn": "2John", "3Jn": "3John",
    "Jud": "Jude", "Rev": "Rev",
}

_UXLC_FILE_TO_BOOK = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
    "Deuteronomy": "Deut", "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth",
    "Samuel_1": "1Sam", "Samuel_2": "2Sam", "Kings_1": "1Kgs", "Kings_2": "2Kgs",
    "Chronicles_1": "1Chr", "Chronicles_2": "2Chr", "Ezra": "Ezra", "Nehemiah": "Neh",
    "Esther": "Esth", "Job": "Job", "Psalms": "Ps", "Proverbs": "Prov",
    "Ecclesiastes": "Eccl", "Song_of_Songs": "Song", "Isaiah": "Isa", "Jeremiah": "Jer",
    "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos",
    "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad", "Jonah": "Jonah", "Micah": "Mic",
    "Nahum": "Nah", "Habakkuk": "Hab", "Zephaniah": "Zeph", "Haggai": "Hag",
    "Zechariah": "Zech", "Malachi": "Mal",
}

_UGNT_BOOK_TO_BOOK = {
    "MAT": "Mat", "MRK": "Mark", "LUK": "Luke", "JHN": "John", "ACT": "Acts",
    "ROM": "Rom", "1CO": "1Cor", "2CO": "2Cor", "GAL": "Gal", "EPH": "Eph",
    "PHP": "Phil", "COL": "Col", "1TH": "1Thess", "2TH": "2Thess", "1TI": "1Tim",
    "2TI": "2Tim", "TIT": "Titus", "PHM": "Phlm", "HEB": "Heb", "JAS": "Jas",
    "1PE": "1Pet", "2PE": "2Pet", "1JN": "1John", "2JN": "2John", "3JN": "3John",
    "JUD": "Jude", "REV": "Rev",
}

_UGNT_BOOK_RE = re.compile(r"^\\id\s+([1-3A-Z]{3})\b", re.M)
_UGNT_CHAPTER_RE = re.compile(r"^\\c\s+(\d+)\s*$", re.M)
_UGNT_VERSE_RE = re.compile(r"^\\v\s+(\d+[a-z]?)\s*$", re.M)
_UGNT_WORD_RE = re.compile(r"\\w\s+([^|]+)\|([^\\]*?)\\w\*", re.S)
_UGNT_ATTR_RE = re.compile(r"([\w-]+)=\"([^\"]*)\"")

_RAW_REF_RE = re.compile(
    r"^(?P<book>[1-3]?[A-Za-z]+)\.(?P<chapter>\d+)\.(?P<verse>\d+)"
    r"(?:(?P<ann_open>[\(\[\{])(?P<ann_chapter>\d+)\.(?P<ann_verse>\d+)"
    r"(?P<ann_close>[\)\]\}]))?#(?P<word>[^=\s]+)=(?P<type>\S+)$"
)
_STRONG_RE = re.compile(r"[HGA]\d+(?:[A-Za-z])?(?:_[A-Za-z0-9]+)?", re.IGNORECASE)
_TAGNT_TEXTUAL_ALTERNATIVE_RE = re.compile(
    r"^(?P<surface>.+?) \((?P<tag>[A-Za-z])=(?P<transliteration>[^()]*)\) "
    r"(?P<gloss>.*?) - (?P<strong>G\d{4,5}[A-Za-z]?)=(?P<morphology>.+?) "
    r"in: (?P<witnesses>.+)$"
)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _sha256_git_text(path: Path) -> str:
    """Optional canonical-LF digest; never used as the locked LFS digest."""

    return sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _validate_alignment_override_rows(
    overrides: Sequence[Mapping[str, Any]],
    *,
    stage6_rows: Sequence[Mapping[str, Any]],
    work_dir: Path,
    report_dir: Path,
) -> dict[str, Mapping[str, Any]]:
    """Validate overrides against independently read current stage-7 inputs."""

    wanted_target_ids = {
        str(token_id)
        for override in overrides
        for token_id in (
            override.get("stable_oh1988_token_ids", ())
            if isinstance(
                override.get("stable_oh1988_token_ids", ()), (list, tuple)
            )
            else ()
        )
    }
    wanted_verse_keys = {
        parts[1]
        for token_id in wanted_target_ids
        if len(parts := token_id.split(":", 3)) == 4
    }
    verse_sha256_by_target_id: dict[str, str] = {}
    for row in stage6_rows:
        if str(row["verse_key"]) not in wanted_verse_keys:
            continue
        verse_sha256 = str(row["plain_text_sha256"])
        for token in exact_word_tokens(str(row["plain_text_nfc"])):
            token_id = f"uk7:{row['verse_key']}:{token.token_id_suffix}"
            if token_id in wanted_target_ids:
                verse_sha256_by_target_id[token_id] = verse_sha256
    missing_target_ids = sorted(wanted_target_ids - set(verse_sha256_by_target_id))
    if missing_target_ids:
        raise ValueError(
            "Alignment override contains dangling OH1988 token IDs: "
            + ", ".join(missing_target_ids[:5])
        )

    wanted_original_ids = {
        str(token_id)
        for override in overrides
        for token_id in (
            override.get("textual_alternative_member_ids", ())
            if isinstance(
                override.get("textual_alternative_member_ids", ()),
                (list, tuple),
            )
            else ()
        )
    }
    source_paths = {source_id: path for source_id, _family, path in ORIGINAL_FILES}
    physical_source_sha256: dict[str, str] = {}
    apparatus_sha256_by_original_id: dict[str, str] = {}
    inventory_specs = (
        (
            work_dir / "original_token_universe.jsonl",
            "original_token_id",
            {
                token_id
                for token_id in wanted_original_ids
                if ":alternative:" not in token_id
            },
        ),
        (
            work_dir / "original_alternative_inventory.jsonl",
            "alternative_token_id",
            {
                token_id
                for token_id in wanted_original_ids
                if ":alternative:" in token_id
            },
        ),
    )
    for path, id_field, wanted_in_file in inventory_specs:
        if not wanted_in_file:
            continue
        if not path.is_file():
            raise ValueError(f"Missing current original inventory: {path.name}")
        for row in _read_jsonl(path):
            token_id = str(row[id_field])
            if token_id not in wanted_in_file:
                continue
            source_id = str(row.get("source_id", ""))
            source_path = source_paths.get(source_id)
            if source_path is None:
                raise ValueError(
                    f"Textual override has unknown source apparatus: {source_id}"
                )
            digest = physical_source_sha256.get(source_id)
            if digest is None:
                digest = _sha256_file(source_path)
                physical_source_sha256[source_id] = digest
            if row.get("source_sha256") != digest:
                raise ValueError(
                    f"Original inventory source digest is stale: {token_id}"
                )
            apparatus_sha256_by_original_id[token_id] = digest
            if wanted_in_file <= set(apparatus_sha256_by_original_id):
                break
    missing_original_ids = sorted(
        wanted_original_ids - set(apparatus_sha256_by_original_id)
    )
    if missing_original_ids:
        raise ValueError(
            "Textual override contains dangling original member IDs: "
            + ", ".join(missing_original_ids[:5])
        )

    return validate_versioned_alignment_overrides(
        overrides,
        source_registry_sha256=_sha256_file(report_dir / "source_registry.json"),
        stage6_text_sha256=_sha256_file(STAGE6_TEXT),
        stage6_verse_sha256_by_target_token_id=verse_sha256_by_target_id,
        legacy_snapshot_sha256=_sha256_file(
            LEGACY_REPORT / "experiment_snapshot.manifest.json"
        ),
        fingerprint_sha256=_sha256_file(
            report_dir / "textual_fingerprint.manifest.json"
        ),
        fingerprint_selected_original_layer_sha256=_sha256_file(
            work_dir / "fingerprint_selected_original_layer.jsonl"
        ),
        source_apparatus_sha256_by_original_token_id=(
            apparatus_sha256_by_original_id
        ),
    )


def _acts_15_34_external_evidence() -> dict[str, Any]:
    """Verify the exact D05 and versional evidence without importing a corpus."""

    for source_id, lock in ACTS_15_34_EVIDENCE_SOURCES.items():
        path = lock["path"]
        if not path.is_file():
            raise RuntimeError(f"Acts.15.34 evidence source is missing: {source_id}")
        if path.stat().st_size != lock["bytes"] or _sha256_file(path) != lock["sha256"]:
            raise RuntimeError(f"Acts.15.34 evidence source changed: {source_id}")

    xml_lock = ACTS_15_34_EVIDENCE_SOURCES["bezae_greek_xml_v1_03"]
    xml_bytes = xml_lock["path"].read_bytes()
    fragment = xml_bytes[xml_lock["fragment_start"] : xml_lock["fragment_end"]]
    if len(fragment) != 478 or sha256(fragment).hexdigest() != xml_lock["fragment_sha256"]:
        raise RuntimeError("Acts.15.34 D05 XML fragment changed")
    required_fragment_parts = (b'<ab n="B05K15V34"', b'P479vC1L20-05')
    if any(part not in fragment for part in required_fragment_parts):
        raise RuntimeError("Acts.15.34 D05 XML token evidence changed")

    lat_lock = ACTS_15_34_EVIDENCE_SOURCES["clementine_vulgate_1598_usfx"]
    with zipfile.ZipFile(lat_lock["path"]) as archive:
        member_bytes = archive.read(lat_lock["member"])
    if (
        len(member_bytes) != lat_lock["member_bytes"]
        or sha256(member_bytes).hexdigest() != lat_lock["member_sha256"]
    ):
        raise RuntimeError("Acts.15.34 Clementine Vulgate member changed")
    verse_bytes = lat_lock["verse_text"].encode("utf-8")
    if (
        len(verse_bytes) != lat_lock["verse_utf8_bytes"]
        or sha256(verse_bytes).hexdigest() != lat_lock["verse_sha256"]
        or member_bytes.count(verse_bytes) != 1
    ):
        raise RuntimeError("Acts.15.34 Clementine Vulgate verse evidence changed")

    return {
        "status": "resolved_composite_original_plus_versional_addition",
        "d05_primary_token_ids": [
            "bezae05-v1.03:B05K15V34:w16",
            "bezae05-v1.03:B05K15V34:w18",
            "bezae05-v1.03:B05K15V34:w20",
            "bezae05-v1.03:B05K15V34:w22",
        ],
        "selected_supplemental_original_token_ids": list(
            _ACTS_15_34_SUPPLEMENTAL_UGNT_IDS
        ),
        "d05_to_ugnt_token_crosswalk": [
            {
                "d05_token_id": d05_id,
                "ugnt_control_token_id": ugnt_id,
                "evidence": "exact Greek surface and verse; D05 resolves the UGNT bracketed reading",
            }
            for d05_id, ugnt_id in zip(
                (
                    "bezae05-v1.03:B05K15V34:w16",
                    "bezae05-v1.03:B05K15V34:w18",
                    "bezae05-v1.03:B05K15V34:w20",
                    "bezae05-v1.03:B05K15V34:w22",
                ),
                _ACTS_15_34_SUPPLEMENTAL_UGNT_IDS,
                strict=True,
            )
        ],
        "proven_omitted_original_ids": [
            _ACTS_15_34_SUPPLEMENTAL_UGNT_IDS[0]
        ],
        "versional_addition_target_ids": [
            "uk7:L79:009:46:48",
            "uk7:L79:010:49:58",
        ],
        "forbidden_strong_on_versional_addition": ["G2419"],
        "evidence_records": [
            {
                "source_id": "scrivener_codex_bezae_1864",
                "locator": "PDF 458 / printed p.384 / manuscript fol.479b / Acts.15.34",
                "role": "public-domain primary Greek witness; Judas/journeyed is present and Jerusalem is absent",
                "sha256": ACTS_15_34_EVIDENCE_SOURCES["scrivener_bezae_1864"]["sha256"],
            },
            {
                "source_id": "igntp_codex_bezae_greek_xml_v1_03",
                "locator": "B05K15V34; P479vC1L18-20-05; raw byte offsets 2877068..2877546",
                "role": "verification-only locator/transcription check; no XML-derived corpus or alignment vote retained",
                "sha256": xml_lock["sha256"],
                "fragment_sha256": xml_lock["fragment_sha256"],
            },
            {
                "source_id": "clementine_vulgate_1598_latvuc",
                "locator": "ACT.15.34",
                "role": "public-domain versional evidence for the target addition 'to Jerusalem'; never a Strong source",
                "sha256": lat_lock["sha256"],
                "member_sha256": lat_lock["member_sha256"],
                "verse_sha256": lat_lock["verse_sha256"],
            },
        ],
    }


def _git_checkout_head(path: Path) -> str:
    git_dir = path / ".git"
    head = (git_dir / "HEAD").read_text(encoding="ascii").strip()
    if not head.startswith("ref: "):
        return head
    ref = head[5:]
    loose = git_dir / ref
    if loose.is_file():
        return loose.read_text(encoding="ascii").strip()
    for line in (git_dir / "packed-refs").read_text(encoding="ascii").splitlines():
        if line and not line.startswith(("#", "^")):
            digest, name = line.split(" ", 1)
            if name == ref:
                return digest
    raise RuntimeError(f"Unable to resolve Git HEAD for {path}")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = sha256()
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            encoded = stable_json(row) + "\n"
            handle.write(encoded)
            digest.update(encoded.encode("utf-8"))
            count += 1
    return count, digest.hexdigest()


def _manifest(
    *,
    artifact: str,
    status: str,
    inputs: Mapping[str, str],
    outputs: Mapping[str, str],
    processed: int,
    skipped: int = 0,
    errors: int = 0,
    counts: Mapping[str, Any] | None = None,
    stratum_counts: Mapping[str, Any] | None = None,
    notes: Sequence[str] = (),
) -> dict[str, Any]:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "artifact": artifact,
        "status": status,
        "input_sha256": dict(sorted(inputs.items())),
        "output_sha256": dict(sorted(outputs.items())),
        "processed_count": processed,
        "skipped_count": skipped,
        "error_count": errors,
        "counts": dict(sorted((counts or {}).items())),
        "notes": list(notes),
        "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF; rows in canonical order",
    }
    if stratum_counts is not None:
        manifest["stratum_counts"] = dict(sorted(stratum_counts.items()))
    return manifest


def parse_raw_reference(value: str, *, family: str) -> dict[str, Any] | None:
    match = _RAW_REF_RE.fullmatch(value.strip())
    if match is None:
        return None
    if family not in {"TAHOT", "TAGNT"}:
        return None
    delimiter_pairs = {"(": ")", "[": "]", "{": "}"}
    if match.group("ann_open") and delimiter_pairs[match.group("ann_open")] != match.group("ann_close"):
        return None
    if family == "TAHOT" and match.group("ann_open") not in {None, "("}:
        return None
    book = SOURCE_BOOK.get(match.group("book"))
    if book is None:
        return None
    base = f"{book}.{int(match.group('chapter'))}.{int(match.group('verse'))}"
    annotated = None
    annotation_kind = None
    if match.group("ann_open"):
        annotated = f"{book}.{int(match.group('ann_chapter'))}.{int(match.group('ann_verse'))}"
        annotation_kind = {"(": "round", "[": "square", "{": "curly"}[match.group("ann_open")]
    # TAGNT square brackets explicitly carry the KJV/application position.
    target = annotated if family == "TAGNT" and annotation_kind == "square" else base
    return {
        "base_ref": base,
        "annotated_ref": annotated,
        "annotation_kind": annotation_kind,
        "target_ref": target,
        "word_order_raw": match.group("word"),
        "type_raw": match.group("type"),
    }


def resolve_original_target_ref(
    parsed: Mapping[str, Any],
    *,
    family: str,
    order: int,
) -> tuple[str, str]:
    """Project one exact STEP locator onto the immutable stage-6 grid."""

    if (
        family == "TAHOT"
        and parsed["base_ref"] == "2Chr.14.1"
        and parsed["annotated_ref"] == "2Chr.13.23"
    ):
        if order <= 12:
            return "2Chr.13.23", "stage5_split_first"
        return "2Chr.14.1", "stage5_split_second"
    if family == "TAGNT" and parsed["annotation_kind"] == "square":
        return str(parsed["target_ref"]), "kjv_square"
    return str(parsed["target_ref"]), "direct"


def _word_order(value: str) -> int:
    match = re.search(r"\d+", value)
    if match is None:
        raise ValueError(f"No numeric word order: {value}")
    return int(match.group())


def _stage6_rows() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    if _sha256_file(STAGE6_TEXT) != EXPECTED_STAGE6_TEXT_SHA256:
        raise RuntimeError("Immutable stage-6 synthesized text SHA-256 changed")
    if _sha256_file(STAGE6_MANIFEST) != EXPECTED_STAGE6_MANIFEST_SHA256:
        raise RuntimeError("Immutable stage-6 synthesized manifest SHA-256 changed")
    if _sha256_file(STAGE6_COMMENTS) != EXPECTED_STAGE6_COMMENT_SHA256:
        raise RuntimeError("Immutable stage-6 comments SHA-256 changed")
    stage6_footnote_inputs = {
        STAGE6_FOOTNOTE_DEFINITIONS: EXPECTED_STAGE6_FOOTNOTE_DEFINITIONS_SHA256,
        STAGE6_FOOTNOTE_USES: EXPECTED_STAGE6_FOOTNOTE_USES_SHA256,
        STAGE6_HEADING_FOOTNOTES: EXPECTED_STAGE6_HEADING_FOOTNOTES_SHA256,
    }
    for path, expected in stage6_footnote_inputs.items():
        if _sha256_file(path) != expected:
            raise RuntimeError(
                f"Immutable stage-6 footnote evidence SHA-256 changed: {path.name}"
            )
    stage5_inputs = {
        STAGE5_WORK / "source_to_target_map.jsonl": EXPECTED_STAGE5_FORWARD_SHA256,
        STAGE5_WORK / "target_to_source_map.jsonl": EXPECTED_STAGE5_REVERSE_SHA256,
        STAGE5_WORK / "footnote_projection.jsonl": EXPECTED_STAGE5_FOOTNOTE_SHA256,
    }
    for path, expected in stage5_inputs.items():
        if _sha256_file(path) != expected:
            raise RuntimeError(f"Immutable stage-5 mapping SHA-256 changed: {path.name}")
    if _sha256_file(LEGACY_REPORT / "experiment_snapshot.manifest.json") != EXPECTED_LEGACY_SNAPSHOT_SHA256:
        raise RuntimeError("Rejected legacy snapshot SHA-256 changed")
    rows = list(_read_jsonl(STAGE6_TEXT))
    if len(rows) != EXPECTED_TARGET_COUNT:
        raise RuntimeError("Stage-6 target count changed")
    if any(row["mapping_contract_version"] != MAPPING_CONTRACT for row in rows):
        raise RuntimeError("Stage-5 mapping contract changed inside stage 6")
    reverse_keys = {row["target_ref"] for row in _read_jsonl(STAGE5_WORK / "target_to_source_map.jsonl")}
    target_keys = {row["target_ref"] for row in rows}
    if reverse_keys != target_keys:
        raise RuntimeError("Stage-5 reverse map and stage-6 target keys differ")
    return rows, {row["target_ref"]: row for row in rows}


_UKRAINIAN_CLOSED_CLASS: dict[str, tuple[str, str, str]] = {
    "і": ("і", "CCONJ", "coordinating_conjunction"),
    "й": ("і", "CCONJ", "coordinating_conjunction_variant"),
    "та": ("та", "CCONJ", "coordinating_conjunction_or_particle"),
    "але": ("але", "CCONJ", "adversative_conjunction"),
    "а": ("а", "CCONJ", "coordinating_conjunction"),
    "бо": ("бо", "SCONJ", "causal_conjunction"),
    "що": ("що", "SCONJ", "conjunction_or_pronoun"),
    "щоб": ("щоб", "SCONJ", "purpose_conjunction"),
    "не": ("не", "PART", "negative_particle"),
    "ні": ("ні", "PART", "negative_particle_or_conjunction"),
    "чи": ("чи", "PART", "interrogative_particle_or_conjunction"),
    "в": ("в", "ADP", "preposition"),
    "у": ("у", "ADP", "preposition"),
    "до": ("до", "ADP", "preposition"),
    "з": ("з", "ADP", "preposition"),
    "із": ("із", "ADP", "preposition"),
    "зі": ("зі", "ADP", "preposition"),
    "на": ("на", "ADP", "preposition"),
    "за": ("за", "ADP", "preposition"),
    "від": ("від", "ADP", "preposition"),
    "для": ("для", "ADP", "preposition"),
    "по": ("по", "ADP", "preposition"),
    "при": ("при", "ADP", "preposition"),
    "над": ("над", "ADP", "preposition"),
    "під": ("під", "ADP", "preposition"),
    "через": ("через", "ADP", "preposition"),
    "між": ("між", "ADP", "preposition"),
    "я": ("я", "PRON", "personal_pronoun"),
    "ти": ("ти", "PRON", "personal_pronoun_or_infinitive_surface"),
    "він": ("він", "PRON", "personal_pronoun"),
    "вона": ("вона", "PRON", "personal_pronoun"),
    "воно": ("воно", "PRON", "personal_pronoun"),
    "ми": ("ми", "PRON", "personal_pronoun"),
    "ви": ("ви", "PRON", "personal_pronoun"),
    "вони": ("вони", "PRON", "personal_pronoun"),
}


def ukrainian_morphology_candidates(surface: str) -> list[dict[str, Any]]:
    """Return conservative, versioned Ukrainian morphology proposals.

    This deliberately small first-party ruleset exists to populate the
    inventory schema before gold review.  It never supplies alignment evidence
    or a Strong vote; ambiguous historical spellings remain low-confidence
    candidates instead of being normalized away.
    """

    form = comparison_form(surface)
    if not form:
        return []
    if form.isdecimal():
        return [
            {
                "lemma": form,
                "pos": "NUM",
                "morphology": "cardinal_or_ordinal_unresolved",
                "method": "ukrainian-rule-morph-v1:decimal",
                "confidence": None,
                "heuristic_score": 0.95,
                "score_kind": "uncalibrated_rule",
            }
        ]
    closed = _UKRAINIAN_CLOSED_CLASS.get(form)
    if closed is not None:
        lemma, pos, morphology = closed
        return [
            {
                "lemma": lemma,
                "pos": pos,
                "morphology": morphology,
                "method": "ukrainian-rule-morph-v1:closed-class",
                "confidence": None,
                "heuristic_score": 0.9,
                "score_kind": "uncalibrated_rule",
            }
        ]
    candidates: list[dict[str, Any]] = []
    if form.endswith(("ти", "ть")) and len(form) > 3:
        candidates.append(
            {
                "lemma": form,
                "pos": "VERB",
                "morphology": "infinitive_candidate",
                "method": "ukrainian-rule-morph-v1:infinitive-suffix",
                "confidence": None,
                "heuristic_score": 0.72,
                "score_kind": "uncalibrated_rule",
            }
        )
    if surface[:1].isupper():
        candidates.append(
            {
                "lemma": form,
                "pos": "PROPN",
                "morphology": "proper_name_candidate_case_unresolved",
                "method": "ukrainian-rule-morph-v1:capitalization",
                "confidence": None,
                "heuristic_score": 0.35,
                "score_kind": "uncalibrated_rule",
            }
        )
    if not candidates:
        candidates.append(
            {
                "lemma": None,
                "pos": "X",
                "morphology": "unresolved_inflection",
                "method": "ukrainian-rule-morph-v1:identity-fallback",
                "confidence": None,
                "heuristic_score": 0.1,
                "score_kind": "uncalibrated_rule",
            }
        )
    return candidates


def _tokenize_stage6(rows: Sequence[Mapping[str, Any]], work: Path) -> dict[str, Any]:
    path = work / "ukrainian_token_inventory.jsonl"
    count = 0
    byte_count = 0
    nonlexical_count = 0
    surface_counts: Counter[str] = Counter()

    def records() -> Iterator[dict[str, Any]]:
        nonlocal count, byte_count, nonlexical_count
        for row in rows:
            text = str(row["plain_text_nfc"])
            tokens = exact_word_tokens(text)
            validate_exact_partition(text, tokens)
            for token_index, token in enumerate(tokens):
                token_id = f"uk7:{row['verse_key']}:{token.token_id_suffix}"
                if token.comparison:
                    surface_counts[token.comparison] += 1
                    token_kind = "surface_lexeme"
                else:
                    nonlexical_count += 1
                    token_kind = "nonlexical_orthographic_mark"
                count += 1
                byte_count += token.end_byte - token.start_byte
                yield {
                    "schema_version": SCHEMA_VERSION,
                    "contract_version": CONTRACT_VERSION,
                    "tokenizer_version": TOKENIZER_VERSION,
                    "token_id": token_id,
                    "verse_key": row["verse_key"],
                    "target_ref": row["target_ref"],
                    "book": str(row["target_ref"]).split(".", 1)[0],
                    "testament": "OT" if BOOK_NUMBER[str(row["target_ref"]).split(".", 1)[0]] <= 39 else "NT",
                    "genre": _book_genre(str(row["target_ref"]).split(".", 1)[0]),
                    "order": token.order,
                    "surface": token.surface,
                    "comparison": token.comparison,
                    "token_kind": token_kind,
                    "start_scalar": token.start_scalar,
                    "end_scalar": token.end_scalar,
                    "start_byte": token.start_byte,
                    "end_byte": token.end_byte,
                    "plain_text_sha256": row["plain_text_sha256"],
                    "context_sha256": sha256_text(
                        stable_json(
                            [
                                item.surface
                                for item in tokens[
                                    max(0, token_index - 2) : token_index + 3
                                ]
                            ]
                        )
                    ),
                    "left_context": [
                        item.comparison
                        for item in tokens[max(0, token_index - 2) : token_index]
                    ],
                    "right_context": [
                        item.comparison
                        for item in tokens[token_index + 1 : token_index + 3]
                    ],
                    "lemma_pos_morphology_candidates": ukrainian_morphology_candidates(
                        token.surface
                    ),
                    "fold_id": int(sha256_text(str(row["target_ref"]))[:8], 16) % 5,
                }

    written, digest = _write_jsonl(path, records())
    if written != count:
        raise RuntimeError("Ukrainian token count drift")
    return {
        "path": path,
        "count": count,
        "sha256": digest,
        "byte_count": byte_count,
        "nonlexical_count": nonlexical_count,
        "lexeme_count": len(surface_counts),
        "surface_counts": surface_counts,
    }


def _tagnt_reading_status(target_ref: str, order: int, editions: str) -> str:
    witnesses = {item for item in editions.split("+") if item}
    # Treg is retained as a textual witness, but Treg+TR/Byz without a modern
    # critical witness is not enough to promote a row into the primary
    # production universe.  That pattern occurs in traditional expansions and
    # remains locus-specific until OH1988 itself is adjudicated.
    critical = bool(witnesses & {"NA28", "NA27", "SBL", "WH", "Tyn"})
    traditional = bool(witnesses & {"TR", "Byz"})
    if critical and traditional:
        return "primary_shared_reading"
    accepted_tr: dict[str, set[int] | None] = {
        "Mat.1.25": {8, 10, 11, 12},
        "Mark.1.2": {22, 23},
        "John.7.53": None,
        "John.8.1": None,
        "Acts.8.37": None,
        "1John.5.7": None,
    }
    if traditional and target_ref in accepted_tr:
        allowed = accepted_tr[target_ref]
        if allowed is None or order in allowed:
            return "primary_fingerprint_traditional"
    if critical:
        return "primary_critical_reading"
    return "alternative_unresolved_textual_reading"


def _tahot_reading_status(target_ref: str, type_raw: str) -> str:
    """Classify the selected TAHOT row without promoting apparatus additions.

    TAHOT's own locked header defines ``X`` as Hebrew reconstructed from an
    additional LXX reading.  It is valuable textual evidence, but it is not a
    Masoretic primary token and cannot enter the production universe until the
    exact OH1988 locus has been adjudicated.  The same fail-closed rule remains
    in force for the explicitly blocked Ps.22.16 locus.
    """

    if target_ref == "Ps.22.16":
        return "unresolved_blocking_textual_locus"
    if type_raw == "X":
        return "alternative_lxx_reconstruction_unresolved"
    if type_raw.lower().startswith("q("):
        return "primary_qere_with_alternative_preserved"
    return "primary_mt"


def parse_tagnt_textual_alternative(raw: str) -> dict[str, Any] | None:
    """Parse TAGNT column 6 as a distinct apparatus reading.

    The column is not an annotation on the primary component.  It carries a
    separately witnessed surface/Strong/morphology candidate and therefore
    receives its own stable ID in the alternative inventory.  Empty fields are
    the only accepted absence; malformed non-empty apparatus fails closed.
    """

    if not raw:
        return None
    match = _TAGNT_TEXTUAL_ALTERNATIVE_RE.fullmatch(raw)
    if match is None:
        raise RuntimeError(f"Malformed TAGNT textual alternative: {raw!r}")
    fields = match.groupdict()
    normalized = normalize_strong(fields["strong"])
    return {
        "surface_raw": fields["surface"],
        "surface_normalized": comparison_form(fields["surface"]),
        "transliteration_raw": fields["transliteration"],
        "gloss_raw": fields["gloss"],
        "strong_raw": [fields["strong"]],
        "strong_normalized": [normalized],
        "strong_classic": [normalized["classic"]] if normalized["classic"] else [],
        "strong_status": normalized["status"],
        "morphology_raw": fields["morphology"],
        "textual_witnesses": [
            value for value in fields["witnesses"].split("+") if value
        ],
        "apparatus_tag": fields["tag"],
    }


def parse_tahot_surface_alternative(
    source_locator: str, raw: str, parent_id: str
) -> dict[str, Any] | None:
    """Return the explicitly audited TAHOT surface alternative at Ps.22.16.

    Most TAHOT column-6 values are free-form notes and are retained in the raw
    parent record.  This one locus has a complete surface, Strong and morphology
    tuple, and silently reusing column 9 would attach H3738 to the incompatible
    ``like/a lion`` surface.  The exact pinned note therefore gets its own ID.
    """

    if source_locator != "Psa.22.16(22.17)#07=L(D)":
        return None
    expected = 'D= ka.\'a.Ru (כָּ֝אֲרוּ) "they dug" (H3738A=HVqp3cp)'
    if raw != expected:
        raise RuntimeError("Pinned Ps.22.16 TAHOT surface alternative drift")
    normalized = normalize_strong("H3738A")
    return {
        "alternative_token_id": f"{parent_id}:alternative:tahot-c06:01",
        "parent_token_id": parent_id,
        "alternative_kind": "textual_surface_strong_candidate",
        "apparatus_column": 6,
        "surface_raw": "כָּ֝אֲרוּ",
        "surface_normalized": comparison_form("כָּ֝אֲרוּ"),
        "transliteration_raw": "ka.'a.Ru",
        "gloss_raw": "they dug",
        "lemma_raw": None,
        "morphology_raw": "HVqp3cp",
        "strong_raw": ["H3738A"],
        "strong_normalized": [normalized],
        "strong_classic": ["H3738"],
        "strong_status": normalized["status"],
        "textual_witnesses": ["TAHOT D apparatus"],
        "apparatus_tag": "D",
        "reading_status": "alternative_textual_candidate_unadjudicated",
    }


def _parse_original_universe(
    stage6_by_ref: Mapping[str, Mapping[str, Any]],
    work: Path,
) -> dict[str, Any]:
    path = work / "original_token_universe.jsonl"
    parent_path = work / "original_parent_inventory.jsonl"
    alternative_path = work / "original_alternative_inventory.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    file_hashes = {source_id: _sha256_file(path_) for source_id, _, path_ in ORIGINAL_FILES}
    counters: Counter[str] = Counter()
    refs: set[str] = set()
    by_ref_order: dict[tuple[str, int], list[str]] = defaultdict(list)
    by_source_ref_order: dict[tuple[str, int], list[str]] = defaultdict(list)
    by_source_ref: dict[str, list[str]] = defaultdict(list)
    by_source_ref_surface: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    by_source_ref_strong: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    by_source_ref_parent_surface: dict[
        tuple[str, str, str], list[str]
    ] = defaultdict(list)
    parent_components: dict[str, list[str]] = {}
    alternative_by_ref: dict[str, list[str]] = defaultdict(list)
    alternative_meta: dict[str, dict[str, Any]] = {}
    native_control_ref_sets: dict[str, set[str]] = {
        "TAHOT": set(),
        "TAGNT": set(),
    }
    original_meta: dict[str, dict[str, Any]] = {}
    output_digest = sha256()
    parent_output_digest = sha256()
    alternative_output_digest = sha256()
    audit = {
        family: {
            name: sha256()
            for name in ("canonical_rows", "locators", "projection", "parent_ids", "component_ids")
        }
        for family in ("TAHOT", "TAGNT")
    }
    written = 0
    parent_written = 0
    alternative_written = 0

    def emit(handle: Any, digest: Any, record: Mapping[str, Any]) -> None:
        encoded = stable_json(record) + "\n"
        handle.write(encoded)
        digest.update(encoded.encode("utf-8"))

    with (
        path.open("w", encoding="utf-8", newline="\n") as output_handle,
        parent_path.open("w", encoding="utf-8", newline="\n") as parent_handle,
        alternative_path.open("w", encoding="utf-8", newline="\n") as alternative_handle,
    ):
        for source_id, family, source_path in ORIGINAL_FILES:
            with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
                for line_number, line in enumerate(handle, 1):
                    counters[f"{source_id}.input_lines"] += 1
                    raw_line = line.rstrip("\r\n")
                    columns = raw_line.split("\t")
                    if len(columns) != 17:
                        counters[f"{source_id}.metadata_or_non17"] += 1
                        continue
                    parsed = parse_raw_reference(columns[0], family=family)
                    if parsed is None:
                        counters[f"{source_id}.metadata_or_bad_ref"] += 1
                        continue
                    order = _word_order(parsed["word_order_raw"])
                    target_ref, projection_status = resolve_original_target_ref(
                        parsed, family=family, order=order
                    )
                    native_control_ref = (
                        parsed["annotated_ref"] or parsed["base_ref"]
                        if family == "TAHOT"
                        else parsed["base_ref"]
                    )
                    native_control_ref_sets[family].add(str(native_control_ref))
                    outside_target_grid = target_ref not in stage6_by_ref
                    if outside_target_grid:
                        counters[f"{source_id}.outside_target_grid"] += 1
                        projection_status = "source_only"

                    family_key = "step_tahot" if family == "TAHOT" else "step_tagnt"
                    parent_id = (
                        family.lower()
                        + ":"
                        + sha256_text(f"{family_key}\0{STEP_COMMIT}\0{columns[0]}")
                    )
                    audit[family]["canonical_rows"].update((raw_line + "\n").encode("utf-8"))
                    audit[family]["locators"].update((columns[0] + "\n").encode("utf-8"))
                    audit[family]["parent_ids"].update((parent_id + "\n").encode("utf-8"))
                    audit[family]["projection"].update(
                        (
                            stable_json(
                                {
                                    "family": family,
                                    "source_id": source_id,
                                    "source_locator": columns[0],
                                    "projection_status": projection_status,
                                    "target_ref": None if outside_target_grid else target_ref,
                                }
                            )
                            + "\n"
                        ).encode("utf-8")
                    )

                    row = stage6_by_ref.get(target_ref)
                    if row is not None:
                        refs.add(target_ref)
                    component_records: list[dict[str, Any]] = []
                    alternative_records: list[dict[str, Any]] = []
                    if family == "TAHOT":
                        groups = [columns[index].split("/") for index in range(1, 6)]
                        if len({len(group) for group in groups}) != 1:
                            raise RuntimeError(f"TAHOT slash-group mismatch at {columns[0]}")
                        root_candidates = _STRONG_RE.findall(columns[8])
                        alternative_candidates = _STRONG_RE.findall(columns[9])
                        type_raw = parsed["type_raw"]
                        reading_status = _tahot_reading_status(target_ref, type_raw)
                        surface_alternative = parse_tahot_surface_alternative(
                            columns[0], columns[6], parent_id
                        )
                        if surface_alternative is not None:
                            alternative_records.append(surface_alternative)
                        for alternative_index, raw_strong in enumerate(
                            alternative_candidates, 1
                        ):
                            normalized = normalize_strong(raw_strong)
                            alternative_records.append(
                                {
                                    "alternative_token_id": f"{parent_id}:alternative:tahot-c09:{alternative_index:02d}",
                                    "parent_token_id": parent_id,
                                    "alternative_kind": "lexical_strong_candidate",
                                    "apparatus_column": 9,
                                    "surface_raw": columns[1],
                                    "surface_normalized": comparison_form(columns[1]),
                                    "transliteration_raw": columns[2],
                                    "gloss_raw": columns[3],
                                    "lemma_raw": columns[11],
                                    "morphology_raw": columns[5],
                                    "strong_raw": [raw_strong],
                                    "strong_normalized": [normalized],
                                    "strong_classic": [normalized["classic"]]
                                    if normalized["classic"]
                                    else [],
                                    "strong_status": normalized["status"],
                                    "textual_witnesses": ["TAHOT apparatus"],
                                    "reading_status": "alternative_lexical_candidate_unadjudicated",
                                }
                            )
                        for group_index, (surface_group, transliteration_group, gloss_group, strong_group, morphology_group) in enumerate(zip(*groups), 1):
                            surface_atoms = [value for value in surface_group.split("\\") if value.strip()]
                            transliteration_atoms = [value for value in transliteration_group.split("\\") if value.strip()]
                            gloss_atoms = [value for value in gloss_group.split("\\") if value.strip()]
                            raw_codes = _STRONG_RE.findall(strong_group)
                            if len(surface_atoms) != len(raw_codes):
                                raise RuntimeError(f"TAHOT atom/Strong mismatch at {columns[0]} group {group_index}")
                            for atom_index, (surface, raw_strong) in enumerate(zip(surface_atoms, raw_codes), 1):
                                token_id = f"{parent_id}:g{group_index:02d}:a{atom_index:02d}"
                                normalized = normalize_strong(raw_strong)
                                component_records.append(
                                    {
                                        "original_token_id": token_id,
                                        "parent_token_id": parent_id,
                                        "component_kind": "tahot_surface_strong_atom",
                                        "component_group": group_index,
                                        "component_order": atom_index,
                                        "surface_raw": surface,
                                        "surface_normalized": comparison_form(surface),
                                        "transliteration_raw": transliteration_atoms[atom_index - 1] if atom_index <= len(transliteration_atoms) else "",
                                        "gloss_raw": gloss_atoms[atom_index - 1] if atom_index <= len(gloss_atoms) else gloss_group,
                                        "lemma_raw": columns[11],
                                        "lemma_source": "TAHOT dictionary mapping (raw; no standalone Hebrew lemma field)",
                                        "morphology_raw": morphology_group if atom_index == 1 else None,
                                        "strong_raw": [raw_strong],
                                        "strong_normalized": [normalized],
                                        "strong_classic": [normalized["classic"]] if normalized["classic"] else [],
                                        "strong_status": normalized["status"],
                                        "source_span_to_next_parent": "+" in strong_group,
                                        "textual_witnesses": ["TAHOT", "MT", "WLC"],
                                        "textual_variant_raw": {"type": type_raw, "root": root_candidates, "alternative": alternative_candidates},
                                        "reading_status": reading_status,
                                    }
                                )
                        if not component_records:
                            token_id = f"{parent_id}:null"
                            component_records.append(
                                {
                                    "original_token_id": token_id,
                                    "parent_token_id": parent_id,
                                    "component_kind": "tahot_primary_null_with_alternative",
                                    "component_group": None,
                                    "component_order": None,
                                    "surface_raw": "",
                                    "surface_normalized": "",
                                    "transliteration_raw": "",
                                    "gloss_raw": "",
                                    "lemma_raw": columns[11],
                                    "lemma_source": "TAHOT dictionary mapping (raw)",
                                    "morphology_raw": None,
                                    "strong_raw": [],
                                    "strong_normalized": [],
                                    "strong_classic": [],
                                    "strong_status": "primary_null",
                                    "source_span_to_next_parent": False,
                                    "textual_witnesses": ["TAHOT", "MT", "WLC"],
                                    "textual_variant_raw": {"type": type_raw, "root": root_candidates, "alternative": alternative_candidates},
                                    "reading_status": "primary_null_with_alternative_unresolved",
                                }
                            )
                            counters["TAHOT.primary_null_records"] += 1
                    else:
                        surface_match = re.fullmatch(r"(.+) \(([^()]*)\)", columns[1])
                        if surface_match is None:
                            raise RuntimeError(f"TAGNT Greek/transliteration parse failed at {columns[0]}")
                        greek_surface, transliteration = surface_match.groups()
                        dictionary = columns[4].split("=", 1)
                        sstrongs = _STRONG_RE.findall(columns[11])
                        alternative_candidates = _STRONG_RE.findall(columns[12])
                        reading_status = _tagnt_reading_status(target_ref, order, columns[5])
                        textual_alternative = parse_tagnt_textual_alternative(columns[6])
                        if textual_alternative is not None:
                            alternative_records.append(
                                {
                                    "alternative_token_id": f"{parent_id}:alternative:tagnt-c06:01",
                                    "parent_token_id": parent_id,
                                    "alternative_kind": "textual_surface_strong_candidate",
                                    "apparatus_column": 6,
                                    "lemma_raw": None,
                                    "reading_status": "alternative_textual_candidate_unadjudicated",
                                    **textual_alternative,
                                }
                            )
                        for alternative_index, raw_strong in enumerate(
                            alternative_candidates, 1
                        ):
                            normalized = normalize_strong(raw_strong)
                            alternative_records.append(
                                {
                                    "alternative_token_id": f"{parent_id}:alternative:tagnt-c12:{alternative_index:02d}",
                                    "parent_token_id": parent_id,
                                    "alternative_kind": "lexical_strong_candidate",
                                    "apparatus_column": 12,
                                    "surface_raw": greek_surface,
                                    "surface_normalized": comparison_form(greek_surface),
                                    "transliteration_raw": transliteration,
                                    "gloss_raw": columns[2],
                                    "lemma_raw": dictionary[0],
                                    "morphology_raw": None,
                                    "strong_raw": [raw_strong],
                                    "strong_normalized": [normalized],
                                    "strong_classic": [normalized["classic"]]
                                    if normalized["classic"]
                                    else [],
                                    "strong_status": normalized["status"],
                                    "textual_witnesses": ["TAGNT apparatus"],
                                    "reading_status": "alternative_lexical_candidate_unadjudicated",
                                }
                            )
                        for component_index, grammar_component in enumerate(columns[3].split(" + "), 1):
                            grammar = grammar_component.split("=", 1)
                            raw_codes = _STRONG_RE.findall(grammar[0])
                            if len(grammar) != 2 or len(raw_codes) != 1:
                                raise RuntimeError(f"TAGNT Strong/morph parse failed at {columns[0]}")
                            raw_strong = raw_codes[0]
                            normalized = normalize_strong(raw_strong)
                            numeric = int(re.search(r"\d+", raw_strong).group())
                            sstrong_matches = [value for value in sstrongs if int(re.search(r"\d+", value).group()) == numeric]
                            if not sstrong_matches:
                                raise RuntimeError(f"TAGNT dStrong/sStrong identity mismatch at {columns[0]}")
                            token_id = f"{parent_id}:c{component_index:02d}"
                            component_records.append(
                                {
                                    "original_token_id": token_id,
                                    "parent_token_id": parent_id,
                                    "component_kind": "tagnt_strong_component",
                                    "component_group": 1,
                                    "component_order": component_index,
                                    "surface_raw": greek_surface,
                                    "surface_normalized": comparison_form(greek_surface),
                                    "transliteration_raw": transliteration,
                                    "gloss_raw": columns[2],
                                    "lemma_raw": dictionary[0],
                                    "lemma_source": "TAGNT dictionary lemma",
                                    "morphology_raw": grammar[1],
                                    "strong_raw": [raw_strong],
                                    "strong_normalized": [normalized],
                                    "strong_classic": [normalized["classic"]] if normalized["classic"] else [],
                                    "strong_status": normalized["status"],
                                    "sstrong_identity_matches": sstrong_matches,
                                    "source_span_to_next_parent": False,
                                    "textual_witnesses": [value for value in columns[5].split("+") if value],
                                    "textual_variant_raw": {"editions": columns[5], "edition_alternatives": [columns[6], columns[7]], "strong_alternatives": alternative_candidates},
                                    "reading_status": reading_status,
                                }
                            )

                    parent_record = {
                        "schema_version": SCHEMA_VERSION,
                        "contract_version": CONTRACT_VERSION,
                        "parent_token_id": parent_id,
                        "source_id": source_id,
                        "source_family": family,
                        "source_commit": STEP_COMMIT,
                        "source_sha256": file_hashes[source_id],
                        "physical_line": line_number,
                        "raw_line_sha256": sha256_text(raw_line),
                        "raw_columns": columns,
                        "source_locator": columns[0],
                        "base_ref": parsed["base_ref"],
                        "annotated_ref": parsed["annotated_ref"],
                        "projection_status": projection_status,
                        "target_ref": target_ref if row else None,
                        "order": order,
                        "primary_component_ids": [record["original_token_id"] for record in component_records],
                        "alternative_candidate_ids": [
                            record["alternative_token_id"]
                            for record in alternative_records
                        ],
                    }
                    parent_component_ids = [
                        record["original_token_id"] for record in component_records
                    ]
                    parent_components[parent_id] = parent_component_ids
                    parent_surface_normalized = comparison_form(
                        columns[1]
                        if family == "TAHOT"
                        else component_records[0]["surface_raw"]
                    )
                    for source_ref in {
                        parsed["base_ref"],
                        parsed["annotated_ref"],
                    } - {None}:
                        if parent_surface_normalized:
                            by_source_ref_parent_surface[
                                (family, str(source_ref), parent_surface_normalized)
                            ].append(parent_id)
                    emit(parent_handle, parent_output_digest, parent_record)
                    parent_written += 1

                    for alternative in alternative_records:
                        alternative_record = {
                            "schema_version": SCHEMA_VERSION,
                            "contract_version": CONTRACT_VERSION,
                            "source_id": source_id,
                            "source_family": family,
                            "source_commit": STEP_COMMIT,
                            "source_sha256": file_hashes[source_id],
                            "physical_line": line_number,
                            "raw_line_sha256": sha256_text(raw_line),
                            "source_locator": columns[0],
                            "base_ref": parsed["base_ref"],
                            "annotated_ref": parsed["annotated_ref"],
                            "projection_status": projection_status,
                            "target_ref": target_ref if row else None,
                            "verse_key": row["verse_key"] if row else None,
                            "mapping_rule_id": row["rule_id"] if row else None,
                            "mapping_contract_version": row["mapping_contract_version"]
                            if row
                            else MAPPING_CONTRACT,
                            "order": order,
                            **alternative,
                            "accounting_status": "textual_alternative_unadjudicated",
                        }
                        emit(
                            alternative_handle,
                            alternative_output_digest,
                            alternative_record,
                        )
                        if row is not None:
                            alternative_by_ref[target_ref].append(
                                alternative["alternative_token_id"]
                            )
                        alternative_meta[alternative["alternative_token_id"]] = {
                            "source_id": source_id,
                            "family": family,
                            "source_locator": columns[0],
                            "target_ref": target_ref if row else None,
                            "order": order,
                            "surface": alternative["surface_normalized"],
                            "classic": set(alternative["strong_classic"]),
                            "reading_status": alternative["reading_status"],
                            "alternative_kind": alternative["alternative_kind"],
                        }
                        counters[
                            f"{family}.alternative.{alternative['alternative_kind']}"
                        ] += 1
                        alternative_written += 1

                    for component in component_records:
                        stable_id = component["original_token_id"]
                        if not stable_id.endswith(":null"):
                            audit[family]["component_ids"].update((stable_id + "\n").encode("utf-8"))
                        if row is not None:
                            by_ref_order[(target_ref, order)].append(stable_id)
                        for source_ref in {parsed["base_ref"], parsed["annotated_ref"]} - {None}:
                            by_source_ref_order[(str(source_ref), order)].append(stable_id)
                            by_source_ref[str(source_ref)].append(stable_id)
                            if component["surface_normalized"]:
                                by_source_ref_surface[(family, str(source_ref), component["surface_normalized"])].append(stable_id)
                            for strong in component["strong_classic"]:
                                by_source_ref_strong[(family, str(source_ref), strong)].append(stable_id)
                        classic = component["strong_classic"]
                        counters[f"{family}.components"] += 1
                        counters[f"{family}.classic_base_renderable"] += len(classic)
                        counters[f"{family}.nonclassic_or_null"] += not bool(classic)
                        counters[f"reading.{component['reading_status']}"] += 1
                        record = {
                            "schema_version": SCHEMA_VERSION,
                            "contract_version": CONTRACT_VERSION,
                            "source_id": source_id,
                            "source_family": family,
                            "source_commit": STEP_COMMIT,
                            "source_sha256": file_hashes[source_id],
                            "physical_line": line_number,
                            "raw_line_sha256": sha256_text(raw_line),
                            "source_locator": columns[0],
                            "base_ref": parsed["base_ref"],
                            "annotated_ref": parsed["annotated_ref"],
                            "projection_status": projection_status,
                            "target_ref": target_ref if row else None,
                            "verse_key": row["verse_key"] if row else None,
                            "mapping_rule_id": row["rule_id"] if row else None,
                            "mapping_contract_version": row["mapping_contract_version"] if row else MAPPING_CONTRACT,
                            "order": order,
                            **component,
                            "accounting_status": "source_only_paratext_or_versification" if row is None else "textual_alternative" if component["reading_status"].startswith(("alternative", "unresolved")) else "pending_alignment",
                        }
                        original_meta[stable_id] = {
                            "source_id": source_id,
                            "family": family,
                            "source_locator": columns[0],
                            "target_ref": target_ref if row else None,
                            "order": order,
                            "surface": component["surface_normalized"],
                            "classic": set(classic),
                            "reading_status": component["reading_status"],
                        }
                        emit(output_handle, output_digest, record)
                        written += 1

    computed_audit = {
        f"{family}.{name}": digest.hexdigest()
        for family, values in audit.items()
        for name, digest in values.items()
    }
    mismatches = {
        name: {"expected": expected, "actual": computed_audit.get(name)}
        for name, expected in ORIGINAL_AUDIT_DIGESTS.items()
        if computed_audit.get(name) != expected
    }
    if mismatches:
        raise RuntimeError(f"Original raw-reparse audit mismatch: {mismatches}")
    expected_refs = set(stage6_by_ref)
    missing_refs = sorted(expected_refs - refs, key=lambda ref: (BOOK_NUMBER[ref.split(".", 1)[0]], ref))
    if missing_refs:
        raise RuntimeError(f"Original universe misses target refs: {missing_refs[:20]}")
    if counters["TAHOT.components"] != 540_481 or counters["TAGNT.components"] != 142_355:
        raise RuntimeError("Original component/null accounting drift")
    if alternative_written != 28_543:
        raise RuntimeError(
            f"Original alternative-candidate accounting drift: {alternative_written}"
        )
    return {
        "path": path,
        "parent_path": parent_path,
        "alternative_path": alternative_path,
        "count": written,
        "parent_count": parent_written,
        "sha256": output_digest.hexdigest(),
        "parent_sha256": parent_output_digest.hexdigest(),
        "alternative_count": alternative_written,
        "alternative_sha256": alternative_output_digest.hexdigest(),
        "counters": counters,
        "audit_digests": computed_audit,
        "ref_count": len(refs),
        "missing_refs": missing_refs,
        "by_ref_order": by_ref_order,
        "by_source_ref_order": by_source_ref_order,
        "by_source_ref": by_source_ref,
        "by_source_ref_surface": by_source_ref_surface,
        "by_source_ref_strong": by_source_ref_strong,
        "by_source_ref_parent_surface": by_source_ref_parent_surface,
        "parent_components": parent_components,
        "alternative_by_ref": alternative_by_ref,
        "alternative_meta": alternative_meta,
        "native_control_ref_sets": native_control_ref_sets,
        "original_meta": original_meta,
        "file_hashes": file_hashes,
    }


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _canonical_control_ref(raw_ref: str) -> str:
    match = re.fullmatch(r"([1-3]?[A-Za-z]+)\.(\d+)\.(\d+)", raw_ref)
    if match is None:
        raise RuntimeError(f"Invalid original-control reference: {raw_ref}")
    raw_book, chapter_raw, verse_raw = match.groups()
    book = SOURCE_BOOK.get(raw_book, raw_book)
    chapter = int(chapter_raw)
    verse = int(verse_raw)
    if book not in BOOK_NUMBER or chapter <= 0 or verse < 0:
        raise RuntimeError(f"Invalid original-control coordinate: {raw_ref}")
    return f"{book}.{chapter}.{verse}"


def _oshb_strongs(lemma_raw: str) -> list[str]:
    values: list[str] = []
    for part in re.split(r"[/\s]+", lemma_raw):
        match = re.fullmatch(r"(\d+)(?:\s*([a-z]))?", part, re.I)
        if match is None:
            continue
        value = f"H{int(match.group(1))}{(match.group(2) or '').upper()}"
        if value not in values:
            values.append(value)
    return values


def decode_ugnt_strong(raw: str) -> dict[str, Any]:
    """Decode only the documented UGNT terminal-zero classic encoding."""

    match = re.fullmatch(r"G(\d{5})", raw)
    if match is None:
        return {"raw": raw, "classic": None, "status": "invalid_ugnt_encoding"}
    digits = match.group(1)
    if digits.endswith("0"):
        classic = f"G{int(digits[:4])}"
        return {
            "raw": raw,
            "classic": classic,
            "status": "classic_terminal_zero_decoded",
        }
    return {
        "raw": raw,
        "classic": None,
        "status": "extended_nonzero_unresolved",
    }


def _update_textual_delimiter_depths(
    value: str,
    square_depth: int,
    parenthesis_depth: int,
) -> tuple[int, int]:
    for char in value:
        if char == "[":
            square_depth += 1
        elif char == "]":
            square_depth -= 1
        elif char == "(":
            parenthesis_depth += 1
        elif char == ")":
            parenthesis_depth -= 1
        if square_depth < 0 or parenthesis_depth < 0:
            raise RuntimeError("UGNT textual delimiter closes before it opens")
    return square_depth, parenthesis_depth


def _parse_original_controls(
    universe: Mapping[str, Any],
    work: Path,
) -> dict[str, Any]:
    token_path = work / "original_control_tokens.jsonl"
    crosswalk_path = work / "original_control_crosswalk.jsonl"
    token_digest = sha256()
    crosswalk_digest = sha256()
    counters: Counter[str] = Counter()
    control_refs: dict[str, set[str]] = {
        "OSHB": set(),
        "UXLC": set(),
        "UGNT": set(),
    }
    seen_ids: set[str] = set()
    input_hashes: dict[str, str] = {}

    for source_id, spec in CONTROL_SOURCES.items():
        path = spec["path"]
        actual = _sha256_file(path)
        if actual != spec["sha256"]:
            raise RuntimeError(
                f"Locked original-control input changed: {source_id}: {actual}"
            )
        input_hashes[source_id] = actual

    def emit(handle: Any, digest: Any, record: Mapping[str, Any]) -> None:
        encoded = stable_json(record) + "\n"
        handle.write(encoded)
        digest.update(encoded.encode("utf-8"))

    def parent_classic(parent_id: str) -> set[str]:
        values: set[str] = set()
        for component_id in universe["parent_components"][parent_id]:
            values.update(universe["original_meta"][component_id]["classic"])
        return values

    def parent_is_resolved_primary(parent_id: str) -> bool:
        statuses = {
            str(universe["original_meta"][component_id]["reading_status"])
            for component_id in universe["parent_components"][parent_id]
        }
        return bool(statuses) and all(
            status.startswith("primary_")
            and "unresolved" not in status
            for status in statuses
        )

    def crosswalk_for(
        record: Mapping[str, Any],
        *,
        primary_family: str,
    ) -> dict[str, Any]:
        normalized = str(record["surface_normalized"])
        source_ref = str(record["source_ref"])
        parents = sorted(
            set(
                universe["by_source_ref_parent_surface"].get(
                    (primary_family, source_ref, normalized), []
                )
            )
        )
        parents = [parent_id for parent_id in parents if parent_is_resolved_primary(parent_id)]
        classic = set(record["strong_classic"])
        if classic:
            parents = [
                parent_id
                for parent_id in parents
                if parent_classic(parent_id) & classic
            ]
        reading_status = str(record["reading_status"])
        strong_status = str(record["strong_status"])
        kind = str(record["token_kind"])
        if kind == "service":
            status = "service_not_crosswalked"
        elif reading_status != "primary_control_reading":
            status = "unresolved_textual_variant"
        elif strong_status in {
            "extended_nonzero_unresolved",
            "invalid_ugnt_encoding",
        }:
            status = "unresolved_nonclassic_strong"
        elif not parents:
            status = "unresolved_no_exact_candidate"
        elif len(parents) != 1:
            status = "unresolved_ambiguous_exact_candidates"
        else:
            status = (
                "resolved_exact_unique_surface_strong_control"
                if classic
                else "resolved_exact_unique_surface_control"
            )
        accepted_parents = parents if status.startswith("resolved_") else []
        accepted_components = [
            component_id
            for parent_id in accepted_parents
            for component_id in universe["parent_components"][parent_id]
        ]
        target_refs = sorted(
            {
                str(universe["original_meta"][component_id]["target_ref"])
                for component_id in accepted_components
                if universe["original_meta"][component_id]["target_ref"] is not None
            },
            key=lambda ref: (
                BOOK_NUMBER[ref.split(".", 1)[0]],
                ref,
            ),
        )
        counters[f"crosswalk.{status}"] += 1
        return {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "control_token_id": record["control_token_id"],
            "control_source_id": record["source_id"],
            "control_source_ref": source_ref,
            "primary_family": primary_family,
            "candidate_parent_token_ids": parents,
            "accepted_parent_token_ids": accepted_parents,
            "accepted_original_component_ids": accepted_components,
            "target_refs": target_refs,
            "status": status,
            "evidence": {
                "native_verse_ref": True,
                "exact_normalized_surface": bool(normalized),
                "compatible_classic_strong": bool(classic),
                "position_used_as_evidence": False,
                "oh1988_target_link_proven": False,
            },
        }

    def emit_pair(
        token_handle: Any,
        crosswalk_handle: Any,
        record: Mapping[str, Any],
        *,
        primary_family: str,
    ) -> None:
        token_id = str(record["control_token_id"])
        if token_id in seen_ids:
            raise RuntimeError(f"Duplicate original-control token ID: {token_id}")
        seen_ids.add(token_id)
        emit(token_handle, token_digest, record)
        emit(
            crosswalk_handle,
            crosswalk_digest,
            crosswalk_for(record, primary_family=primary_family),
        )
        counters["control_tokens"] += 1
        counters[f"source.{record['source_id']}.tokens"] += 1

    token_path.parent.mkdir(parents=True, exist_ok=True)
    with token_path.open("w", encoding="utf-8", newline="\n") as token_handle, crosswalk_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as crosswalk_handle:
        source_id = "openscriptures_oshb_v2_2"
        spec = CONTROL_SOURCES[source_id]
        with zipfile.ZipFile(spec["path"]) as archive:
            members = [
                item
                for item in archive.infolist()
                if "/wlc/" in item.filename.lower()
                and item.filename.endswith(".xml")
                and not item.filename.endswith("VerseMap.xml")
            ]
            if len(members) != 39:
                raise RuntimeError(f"OSHB canonical member count changed: {len(members)}")
            parsed_members: list[tuple[int, Any]] = []
            for member in members:
                raw_member = archive.read(member)
                root = ET.fromstring(raw_member)
                first_verse = next(
                    element
                    for element in root.iter()
                    if _local_name(element.tag) == "verse"
                )
                book = _canonical_control_ref(first_verse.attrib["osisID"]).split(".", 1)[0]
                parsed_members.append((BOOK_NUMBER[book], (member, raw_member, root)))
            for _, (member, raw_member, root) in sorted(parsed_members):
                member_sha = sha256(raw_member).hexdigest()
                for verse_element in root.iter():
                    if _local_name(verse_element.tag) != "verse":
                        continue
                    source_ref = _canonical_control_ref(verse_element.attrib["osisID"])
                    control_refs["OSHB"].add(source_ref)
                    parent_map = {
                        child: parent
                        for parent in verse_element.iter()
                        for child in parent
                    }
                    order = 0
                    for element in verse_element.iter():
                        if _local_name(element.tag) != "w":
                            continue
                        order += 1
                        native_id = element.attrib.get("id", "")
                        if not native_id:
                            raise RuntimeError(f"OSHB word lacks native ID: {source_ref}")
                        ancestors: list[Any] = []
                        ancestor = parent_map.get(element)
                        while ancestor is not None and ancestor is not verse_element:
                            ancestors.append(ancestor)
                            ancestor = parent_map.get(ancestor)
                        note_element = next(
                            (
                                item
                                for item in ancestors
                                if _local_name(item.tag) == "note"
                            ),
                            None,
                        )
                        if element.attrib.get("type") == "x-ketiv":
                            reading_status = "unresolved_ketiv_control"
                            parent = parent_map.get(element)
                            if parent is not None:
                                siblings = list(parent)
                                position = siblings.index(element)
                                if position + 1 < len(siblings) and _local_name(
                                    siblings[position + 1].tag
                                ) == "note":
                                    note_element = siblings[position + 1]
                            counters["OSHB.ketiv"] += 1
                        elif any(
                            _local_name(item.tag) == "rdg"
                            and item.attrib.get("type") == "x-qere"
                            for item in ancestors
                        ):
                            reading_status = "unresolved_qere_control"
                            counters["OSHB.qere"] += 1
                        else:
                            reading_status = "primary_control_reading"
                            counters["OSHB.ordinary"] += 1
                        raw_fragment = ET.tostring(element, encoding="unicode")
                        lemma_raw = element.attrib.get("lemma", "")
                        strong_raw = _oshb_strongs(lemma_raw)
                        strong_classic = [
                            normalize_strong(value)["classic"]
                            for value in strong_raw
                            if normalize_strong(value)["classic"] is not None
                        ]
                        surface = element.text or ""
                        token_id = "oshb:" + sha256_text(
                            "\0".join(
                                (
                                    source_id,
                                    str(spec["version"]),
                                    member.filename,
                                    source_ref,
                                    native_id,
                                )
                            )
                        )
                        record = {
                            "schema_version": SCHEMA_VERSION,
                            "contract_version": CONTRACT_VERSION,
                            "control_token_id": token_id,
                            "source_id": source_id,
                            "source_sha256": spec["sha256"],
                            "source_version": spec["version"],
                            "member": member.filename,
                            "member_sha256": member_sha,
                            "source_ref": source_ref,
                            "source_order": order,
                            "native_id": native_id,
                            "token_kind": "word",
                            "reading_status": reading_status,
                            "variant_note_sha256": (
                                sha256(
                                    ET.tostring(note_element, encoding="utf-8")
                                ).hexdigest()
                                if note_element is not None
                                else None
                            ),
                            "surface_raw": surface,
                            "surface_normalized": comparison_form(surface),
                            "lemma_raw": lemma_raw,
                            "lemma_semantics": "numeric Strong encoding; not a Hebrew lemma",
                            "morphology_raw": element.attrib.get("morph", ""),
                            "strong_raw": strong_raw,
                            "strong_classic": strong_classic,
                            "strong_status": (
                                "classic_from_numeric_lemma"
                                if strong_classic
                                else "missing"
                            ),
                            "raw_fragment_sha256": sha256_text(raw_fragment),
                        }
                        counters["OSHB.strong_occurrences"] += len(strong_raw)
                        emit_pair(
                            token_handle,
                            crosswalk_handle,
                            record,
                            primary_family="TAHOT",
                        )

        source_id = "tanach_us_uxlc_2_5_27_6"
        spec = CONTROL_SOURCES[source_id]
        with zipfile.ZipFile(spec["path"]) as archive:
            members = [
                item
                for item in archive.infolist()
                if item.filename.startswith("Books/")
                and item.filename.endswith(".xml")
                and not item.filename.endswith(".DH.xml")
                and Path(item.filename).stem in _UXLC_FILE_TO_BOOK
            ]
            if len(members) != 39:
                raise RuntimeError(f"UXLC canonical member count changed: {len(members)}")
            members.sort(
                key=lambda item: BOOK_NUMBER[
                    _UXLC_FILE_TO_BOOK[Path(item.filename).stem]
                ]
            )
            for member in members:
                raw_member = archive.read(member)
                member_sha = sha256(raw_member).hexdigest()
                root = ET.fromstring(raw_member)
                book = _UXLC_FILE_TO_BOOK[Path(member.filename).stem]
                for chapter_element in root.iter("c"):
                    chapter = int(chapter_element.attrib["n"])
                    for verse_element in chapter_element.findall("v"):
                        verse = int(verse_element.attrib["n"])
                        source_ref = f"{book}.{chapter}.{verse}"
                        control_refs["UXLC"].add(source_ref)
                        for order, child in enumerate(verse_element, 1):
                            element_kind = _local_name(child.tag)
                            if element_kind in {"pe", "samekh", "reversednun"}:
                                counters[
                                    f"UXLC.structural_{element_kind}_skipped"
                                ] += 1
                                continue
                            if element_kind not in {"w", "q", "k", "x"}:
                                raise RuntimeError(
                                    f"Unexpected UXLC verse element: {element_kind} at {source_ref}"
                                )
                            raw_fragment = ET.tostring(child, encoding="unicode")
                            surface = "".join(child.itertext()).strip()
                            token_kind = "service" if element_kind == "x" else "word"
                            reading_status = {
                                "w": "primary_control_reading",
                                "q": "unresolved_qere_control",
                                "k": "unresolved_ketiv_control",
                                "x": "service_control_element",
                            }[element_kind]
                            counters[f"UXLC.{element_kind}"] += 1
                            token_id = "uxlc:" + sha256_text(
                                "\0".join(
                                    (
                                        source_id,
                                        str(spec["version"]),
                                        member.filename,
                                        source_ref,
                                        str(order),
                                        element_kind,
                                        sha256_text(raw_fragment),
                                    )
                                )
                            )
                            record = {
                                "schema_version": SCHEMA_VERSION,
                                "contract_version": CONTRACT_VERSION,
                                "control_token_id": token_id,
                                "source_id": source_id,
                                "source_sha256": spec["sha256"],
                                "source_version": spec["version"],
                                "member": member.filename,
                                "member_sha256": member_sha,
                                "source_ref": source_ref,
                                "source_order": order,
                                "native_id": None,
                                "token_kind": token_kind,
                                "element_kind": element_kind,
                                "reading_status": reading_status,
                                "surface_raw": surface,
                                "surface_normalized": comparison_form(surface),
                                "lemma_raw": None,
                                "morphology_raw": None,
                                "strong_raw": [],
                                "strong_classic": [],
                                "strong_status": "not_available_surface_control",
                                "raw_fragment_sha256": sha256_text(raw_fragment),
                            }
                            emit_pair(
                                token_handle,
                                crosswalk_handle,
                                record,
                                primary_family="TAHOT",
                            )

        source_id = "unfoldingword_ugnt_v0_34"
        spec = CONTROL_SOURCES[source_id]
        with zipfile.ZipFile(spec["path"]) as archive:
            members = [
                item for item in archive.infolist() if item.filename.endswith(".usfm")
            ]
            if len(members) != 27:
                raise RuntimeError(f"UGNT canonical member count changed: {len(members)}")
            prepared: list[tuple[int, Any, str, bytes]] = []
            for member in members:
                raw_member = archive.read(member)
                text = raw_member.decode("utf-8-sig")
                book_match = _UGNT_BOOK_RE.search(text)
                if book_match is None or book_match.group(1) not in _UGNT_BOOK_TO_BOOK:
                    raise RuntimeError(f"UGNT member has unknown book: {member.filename}")
                book = _UGNT_BOOK_TO_BOOK[book_match.group(1)]
                prepared.append((BOOK_NUMBER[book], member, text, raw_member))
            for _, member, text, raw_member in sorted(prepared):
                book_match = _UGNT_BOOK_RE.search(text)
                assert book_match is not None
                book = _UGNT_BOOK_TO_BOOK[book_match.group(1)]
                chapter = 0
                square_depth = 0
                parenthesis_depth = 0
                member_sha = sha256(raw_member).hexdigest()
                for part in re.split(r"(?m)(?=^\\[cv]\s+)", text):
                    chapter_match = _UGNT_CHAPTER_RE.match(part)
                    if chapter_match:
                        chapter = int(chapter_match.group(1))
                        continue
                    verse_match = _UGNT_VERSE_RE.match(part)
                    if verse_match is None:
                        continue
                    verse_label = verse_match.group(1)
                    verse = int(re.match(r"\d+", verse_label).group())
                    subverse = verse_label[len(str(verse)) :]
                    source_ref = f"{book}.{chapter}.{verse}{subverse}"
                    control_refs["UGNT"].add(source_ref)
                    cursor = 0
                    order = 0
                    for word_match in _UGNT_WORD_RE.finditer(part):
                        square_depth, parenthesis_depth = _update_textual_delimiter_depths(
                            part[cursor : word_match.start()],
                            square_depth,
                            parenthesis_depth,
                        )
                        order += 1
                        surface = word_match.group(1).strip()
                        attrs = dict(_UGNT_ATTR_RE.findall(word_match.group(2)))
                        raw_codes = [
                            value for value in attrs.get("strong", "").split() if value
                        ]
                        decoded = [decode_ugnt_strong(value) for value in raw_codes]
                        if any(item["status"] == "invalid_ugnt_encoding" for item in decoded):
                            strong_status = "invalid_ugnt_encoding"
                        elif any(
                            item["status"] == "extended_nonzero_unresolved"
                            for item in decoded
                        ):
                            strong_status = "extended_nonzero_unresolved"
                        else:
                            strong_status = "classic_terminal_zero_decoded"
                        strong_classic = [
                            str(item["classic"])
                            for item in decoded
                            if item["classic"] is not None
                        ]
                        if strong_status == "classic_terminal_zero_decoded":
                            counters["UGNT.classic_terminal_zero"] += len(raw_codes)
                        else:
                            counters["UGNT.nonclassic_or_invalid"] += len(raw_codes)
                        reading_status = (
                            "unresolved_bracketed_or_parenthesized_control"
                            if square_depth or parenthesis_depth
                            else "primary_control_reading"
                        )
                        raw_fragment = word_match.group(0)
                        token_id = "ugnt:" + sha256_text(
                            "\0".join(
                                (
                                    source_id,
                                    str(spec["version"]),
                                    member.filename,
                                    source_ref,
                                    str(order),
                                    sha256_text(raw_fragment),
                                )
                            )
                        )
                        record = {
                            "schema_version": SCHEMA_VERSION,
                            "contract_version": CONTRACT_VERSION,
                            "control_token_id": token_id,
                            "source_id": source_id,
                            "source_sha256": spec["sha256"],
                            "source_version": spec["version"],
                            "member": member.filename,
                            "member_sha256": member_sha,
                            "source_ref": source_ref,
                            "source_order": order,
                            "native_id": None,
                            "token_kind": "word",
                            "reading_status": reading_status,
                            "textual_delimiter_depth": {
                                "square": square_depth,
                                "parenthesis": parenthesis_depth,
                            },
                            "surface_raw": surface,
                            "surface_normalized": comparison_form(surface),
                            "lemma_raw": attrs.get("lemma", ""),
                            "morphology_raw": attrs.get("x-morph", ""),
                            "strong_raw": raw_codes,
                            "strong_classic": strong_classic,
                            "strong_status": strong_status,
                            "raw_fragment_sha256": sha256_text(raw_fragment),
                        }
                        emit_pair(
                            token_handle,
                            crosswalk_handle,
                            record,
                            primary_family="TAGNT",
                        )
                        cursor = word_match.end()
                    square_depth, parenthesis_depth = _update_textual_delimiter_depths(
                        part[cursor:], square_depth, parenthesis_depth
                    )
                if square_depth or parenthesis_depth:
                    raise RuntimeError(
                        f"UGNT member has unclosed textual delimiters: {member.filename}"
                    )

    expected_counts = {
        "control_tokens": 751_557,
        "source.openscriptures_oshb_v2_2.tokens": 306_785,
        "source.tanach_us_uxlc_2_5_27_6.tokens": 306_782,
        "source.unfoldingword_ugnt_v0_34.tokens": 137_990,
        "OSHB.ordinary": 304_249,
        "OSHB.ketiv": 1_258,
        "OSHB.qere": 1_278,
        "OSHB.strong_occurrences": 300_007,
        "UXLC.w": 304_223,
        "UXLC.q": 1_279,
        "UXLC.k": 1_269,
        "UXLC.x": 11,
        "UXLC.structural_pe_skipped": 1_181,
        "UXLC.structural_samekh_skipped": 1_981,
        "UXLC.structural_reversednun_skipped": 9,
        "UGNT.classic_terminal_zero": 137_780,
        "UGNT.nonclassic_or_invalid": 210,
    }
    drift = {
        key: {"expected": expected, "actual": counters[key]}
        for key, expected in expected_counts.items()
        if counters[key] != expected
    }
    if drift:
        raise RuntimeError(f"Original-control token accounting drift: {drift}")
    tahot_refs = set(universe["native_control_ref_sets"]["TAHOT"])
    tagnt_refs = set(universe["native_control_ref_sets"]["TAGNT"])
    if len(tahot_refs) != 23_213 or control_refs["OSHB"] != tahot_refs or control_refs["UXLC"] != tahot_refs:
        raise RuntimeError("OT original-control native reference grid mismatch")
    if len(tagnt_refs) != 7_958 or control_refs["UGNT"] != tagnt_refs:
        raise RuntimeError("NT original-control native reference grid mismatch")
    token_sha256 = token_digest.hexdigest()
    crosswalk_sha256 = crosswalk_digest.hexdigest()
    if token_sha256 != EXPECTED_CONTROL_TOKEN_SHA256:
        raise RuntimeError(
            f"Original-control token output drift: {token_sha256}"
        )
    if crosswalk_sha256 != EXPECTED_CONTROL_CROSSWALK_SHA256:
        raise RuntimeError(
            f"Original-control crosswalk output drift: {crosswalk_sha256}"
        )
    return {
        "token_path": token_path,
        "crosswalk_path": crosswalk_path,
        "count": counters["control_tokens"],
        "token_sha256": token_sha256,
        "crosswalk_sha256": crosswalk_sha256,
        "counters": counters,
        "input_sha256": input_hashes,
        "ref_audit": {
            "TAHOT_native_refs": len(tahot_refs),
            "OSHB_native_refs": len(control_refs["OSHB"]),
            "UXLC_native_refs": len(control_refs["UXLC"]),
            "TAGNT_base_refs": len(tagnt_refs),
            "UGNT_native_refs": len(control_refs["UGNT"]),
            "OT_exact_set_equality": True,
            "NT_exact_set_equality": True,
            "unique_control_token_ids": len(seen_ids),
            "control_token_id_collisions": 0,
        },
    }


def _decode_bcvwp(value: str) -> tuple[str, int, int, int]:
    code = value[1:] if value[:1] in {"o", "n"} else value
    if len(code) not in {11, 12} or not code.isdigit():
        raise ValueError(f"Invalid BCVWP selector: {value}")
    book = NUMBER_BOOK.get(int(code[0:2]))
    if book is None:
        raise ValueError(f"Invalid BCVWP book: {value}")
    chapter, verse, word = int(code[2:5]), int(code[5:8]), int(code[8:11])
    if chapter < 1 or verse < 1 or word < 1:
        raise ValueError(f"Non-positive BCVWP coordinate: {value}")
    return book, chapter, verse, word


def _decode_bridge_bcvwp(value: str) -> tuple[str, int, int, int]:
    """Decode frozen bridge IDs, retaining Psalm-title verse zero as paratext."""

    code = value[1:] if value[:1] in {"o", "n"} else value
    if len(code) not in {11, 12} or not code.isdigit():
        raise ValueError(f"Invalid bridge BCVWP selector: {value}")
    book = NUMBER_BOOK.get(int(code[0:2]))
    chapter, verse, word = int(code[2:5]), int(code[5:8]), int(code[8:11])
    if book is None or chapter < 1 or verse < 0 or word < 1:
        raise ValueError(f"Invalid bridge BCVWP coordinate: {value}")
    return book, chapter, verse, word


def _read_tsv_index(path: Path, ids: set[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        id_field = "id" if "id" in (reader.fieldnames or ()) else "identifier"
        for row in reader:
            identifier = row[id_field]
            if identifier in ids:
                result[identifier] = row
    return result


def _read_tsv_ids(path: Path, ids: set[str]) -> set[str]:
    result: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        id_field = "id" if "id" in (reader.fieldnames or ()) else "identifier"
        for row in reader:
            identifier = row[id_field]
            if identifier in ids:
                result.add(identifier)
    return result


def _flatten_selectors(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        output: list[str] = []
        for item in value:
            output.extend(_flatten_selectors(item))
        return output
    if value is None:
        return []
    raise ValueError(f"Unsupported manual alignment selector shape: {type(value).__name__}")


def _source_to_original(
    selector: str,
    *,
    source_row: Mapping[str, str],
    family: str,
    universe: Mapping[str, Any],
) -> tuple[str | None, str]:
    try:
        book, chapter, verse, _source_order = _decode_bridge_bcvwp(selector)
    except ValueError:
        return None, "invalid_bcvwp"
    ref = f"{book}.{chapter}.{verse}"
    source_surface = comparison_form(source_row.get("text", ""))
    source_strong_raw = source_row.get("strongs", "").split("|", 1)[0]
    if source_strong_raw and source_strong_raw[0].isdigit():
        source_strong_raw = ("G" if family == "TAGNT" else "H") + source_strong_raw
    source_strong = normalize_strong(source_strong_raw)["classic"]
    surface_candidates = set(
        universe["by_source_ref_surface"].get((family, ref, source_surface), ())
    )
    strong_candidates = set(
        universe["by_source_ref_strong"].get((family, ref, source_strong), ())
    ) if source_strong else set()
    if family == "TAGNT":
        candidates = sorted(surface_candidates & strong_candidates)
    else:
        candidates = sorted(surface_candidates | strong_candidates)
    if not candidates:
        return None, "no_original_candidate"
    proven: list[tuple[str, str]] = []
    for token_id in candidates:
        meta = universe["original_meta"][token_id]
        target_surface = meta["surface"]
        surface_match = bool(source_surface and target_surface and source_surface == target_surface)
        strong_match = bool(source_strong and source_strong in meta["classic"])
        if family == "TAGNT" and surface_match and strong_match:
            proven.append((token_id, "verse_wide_surface_and_strong"))
        elif family == "TAHOT" and (strong_match or surface_match):
            proven.append((token_id, "verse_wide_strong" if strong_match else "verse_wide_morpheme_surface"))
    unique = {item[0]: item[1] for item in proven}
    if len(unique) != 1:
        return None, "ambiguous_or_unproven_crosswalk"
    token_id, evidence = next(iter(unique.items()))
    return token_id, evidence


def _load_bridge_bundle(
    *,
    family_id: str,
    scope: str,
    alignment_path: Path,
    source_path: Path,
    target_path: Path,
    source_family: str,
    universe: Mapping[str, Any],
    rejected_reason: str | None = None,
    expected_sha256: Mapping[str, str] | None = None,
    row_sink: Any | None = None,
    collect_rows: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = _read_json(alignment_path)
    if isinstance(payload, dict):
        raw_records = payload["records"]

        def unpack(record: Mapping[str, Any]) -> tuple[list[str], list[str], str]:
            return _flatten_selectors(record["source"]), _flatten_selectors(record["target"]), str(record["meta"]["id"])
    else:
        raw_records = payload

        def unpack(record: Mapping[str, Any]) -> tuple[list[str], list[str], str]:
            return _flatten_selectors(record["source_ids"]), _flatten_selectors(record["target_ids"]), str(record["id"])

    source_ids: set[str] = set()
    target_ids: set[str] = set()
    for raw in raw_records:
        source, target, _record_id = unpack(raw)
        source_ids.update(value for value in source if value)
        target_ids.update(value for value in target if value)
    allow_part_alias = True
    source_lookup_ids = set(source_ids)
    if allow_part_alias:
        source_lookup_ids.update(
            value[:-1] for value in source_ids if len(value) == 12 and value.isdigit()
        )
    sources = _read_tsv_index(source_path, source_lookup_ids)
    targets = _read_tsv_ids(target_path, target_ids)
    raw_hashes = {
        "alignment": _sha256_file(alignment_path),
        "source_tokens": _sha256_file(source_path),
        "target_tokens": _sha256_file(target_path),
    }
    if expected_sha256:
        mismatch = {
            key: {"expected": value, "actual": raw_hashes.get(key)}
            for key, value in expected_sha256.items()
            if raw_hashes.get(key) != value
        }
        if mismatch:
            raise RuntimeError(f"Locked Clear bridge input changed: {mismatch}")
    canonical_lf_hashes = {
        "alignment": _sha256_git_text(alignment_path),
        "source_tokens": _sha256_git_text(source_path),
        "target_tokens": _sha256_git_text(target_path),
    }
    counters: Counter[str] = Counter()
    cross_verse_count = 0
    rows: list[dict[str, Any]] = []
    canonical_source_ids: set[str] = set()
    canonical_target_ids: set[str] = set()
    record_count = 0
    for order, raw in enumerate(raw_records, 1):
        source_selectors, target_selectors, record_id = unpack(raw)
        record_count += 1
        original_ids: list[str] = []
        crosswalk: list[dict[str, Any]] = []
        nonnull_sources = [value for value in source_selectors if value]
        explicit_null_source = len(nonnull_sources) != len(source_selectors) or not nonnull_sources
        if not nonnull_sources:
            counters["fully_null_source_records"] += 1
        elif explicit_null_source:
            counters["mixed_null_source_records"] += 1
        source_missing = False
        unproven = False
        for selector in source_selectors:
            if not selector:
                crosswalk.append(
                    {
                        "raw_selector": selector,
                        "canonical_selector": None,
                        "canonicalization_rule": "explicit_null_source",
                        "source_tsv_present": True,
                        "original_token_id": None,
                        "evidence": "manual_null_source",
                        "status": "preserved_null",
                    }
                )
                continue
            canonical = selector
            rule = "exact"
            if canonical not in sources and allow_part_alias and len(canonical) == 12 and canonical.isdigit() and canonical[:-1] in sources:
                canonical = canonical[:-1]
                rule = "tag_v0_1_terminal_part_alias"
                counters["canonicalized_terminal_part_alias"] += 1
            canonical_source_ids.add(canonical)
            source_present = canonical in sources
            token_id: str | None = None
            proof = "source selector absent from exact source TSV"
            if source_present:
                token_id, proof = _source_to_original(
                    canonical,
                    source_row=sources[canonical],
                    family=source_family,
                    universe=universe,
                )
            else:
                source_missing = True
            if token_id is None and source_present:
                unproven = True
            if token_id is not None:
                original_ids.append(token_id)
            crosswalk.append(
                {
                    "raw_selector": selector,
                    "canonical_selector": canonical,
                    "canonicalization_rule": rule,
                    "source_tsv_present": source_present,
                    "original_token_id": token_id,
                    "evidence": proof,
                    "status": "proven" if token_id else "unresolved",
                }
            )
        canonical_targets = list(dict.fromkeys(value for value in target_selectors if value))
        explicit_null_target = len(canonical_targets) != len(target_selectors) or not canonical_targets
        canonical_target_ids.update(canonical_targets)
        target_missing = any(selector not in targets for selector in canonical_targets)
        status = "accepted_manual_bridge"
        reason = ""
        if rejected_reason:
            status = "rejected_source_integrity"
            reason = rejected_reason
        elif not nonnull_sources and not canonical_targets:
            status = "rejected_invalid_empty_manual_edge"
            reason = "both source and target sides are null"
        elif target_missing:
            status = "rejected_dangling_target"
            reason = "target selector absent from exact target token file"
        elif source_missing:
            status = "rejected_dangling_source"
            reason = "source selector absent from exact source token file"
        elif not canonical_targets:
            if unproven:
                status = "rejected_unproven_original_crosswalk"
                reason = "source side of manual omission lacks unique original proof"
            else:
                status = "accepted_manual_null_target"
                reason = "manual original-side omission/null target preserved"
        elif not nonnull_sources:
            status = "accepted_manual_null_source"
            reason = "manual target-side translation addition/null source preserved"
        elif unproven:
            status = "rejected_unproven_original_crosswalk"
            reason = "at least one source selector lacks unique verse-wide surface/Strong proof"
        elif explicit_null_source:
            status = "accepted_manual_bridge_with_null_member"
        counters[status] += 1
        source_refs = sorted({".".join(map(str, _decode_bridge_bcvwp(item)[:3])) for item in nonnull_sources})
        target_refs = sorted({".".join(map(str, _decode_bridge_bcvwp(item)[:3])) for item in canonical_targets})
        cross_verse = bool(source_refs and target_refs and source_refs != target_refs)
        cross_verse_count += cross_verse
        record = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "bridge_id": f"bridge7:{family_id}:{scope}:{order:07d}",
            "bridge_family": family_id,
            "scope": scope,
            "input_ordinal": order,
            "manual_record_id": record_id,
            "process": "manual",
            "source_selectors": source_selectors,
            "source_selector_crosswalk": crosswalk,
            "source_refs": source_refs,
            "original_token_ids": list(dict.fromkeys(original_ids)),
            "target_token_ids": target_selectors,
            "target_refs": target_refs,
            "cross_verse_manual_record": cross_verse,
            "explicit_null_source": explicit_null_source,
            "explicit_null_target": explicit_null_target,
            "status": status,
            "rejection_reason": reason,
            "input_bundle_id": f"clear:{family_id.lower()}:{scope.lower()}",
        }
        if collect_rows:
            rows.append(record)
        if row_sink is not None:
            row_sink(record)
    return rows, {
        "family": family_id,
        "scope": scope,
        "record_count": record_count,
        "source_selector_count": len(source_ids),
        "target_selector_count": len(target_ids),
        "canonical_source_selector_count": len(canonical_source_ids),
        "source_present_count": sum(value in sources for value in canonical_source_ids),
        "target_present_count": len(targets),
        "counts": dict(counters),
        "cross_verse_manual_record_count": cross_verse_count,
        "alignment_sha256": raw_hashes["alignment"],
        "source_tokens_sha256": raw_hashes["source_tokens"],
        "target_tokens_sha256": raw_hashes["target_tokens"],
        "canonical_lf_sha256": canonical_lf_hashes,
        "coalescing_status": "not_run_until_target_side_OH_evidence_exists",
    }


def _import_bridges(universe: Mapping[str, Any], work: Path) -> dict[str, Any]:
    specs = (
        {
            "family_id": "RUSSYN",
            "scope": "OT",
            "alignment_path": CLEAR / "data/rus/alignments/RUSSYN/WLCM-RUSSYN-manual.json",
            "source_path": CLEAR / "data/sources/WLCM.tsv",
            "target_path": CLEAR / "data/rus/targets/RUSSYN/ot_RUSSYN.tsv",
            "source_family": "TAHOT",
            "expected_sha256": {"alignment": "c7510cddc5bb1414a95201584c7ca8b7712f931d46ce5c9cf909c1962941a16a", "source_tokens": "6d4a2de6784a6bb05fa9ebc0965e755cf23bc8eb9794ac8a8e5e402e73457fbd", "target_tokens": "289eaab10cdfd670f6da5cbfadb058fc65e73808e566706cefa2f6a82c7fbb7b"},
        },
        {
            "family_id": "RUSSYN",
            "scope": "NT",
            "alignment_path": CLEAR / "data/rus/alignments/RUSSYN/SBLGNT-RUSSYN-manual.json",
            "source_path": CLEAR / "data/sources/SBLGNT.tsv",
            "target_path": CLEAR / "data/rus/targets/RUSSYN/nt_RUSSYN.tsv",
            "source_family": "TAGNT",
            "expected_sha256": {"alignment": "27cf473fe37ddb97d0fc32e46061f7012e9ff98712fd18e4edb22c73345c5553", "source_tokens": "df632b6b788aece04ac83495a315ac3933d122dca09da849efb1bc17d9c2a0be", "target_tokens": "6715ce82263f62cb00b1036a9d19259b92ccbc0e67a4f87d9951f41f94ddc912"},
        },
        {
            "family_id": "YLT",
            "scope": "OT",
            "alignment_path": CLEAR / "data/eng/alignments/YLT/WLC-YLT-manual.json",
            "source_path": CLEAR / "data/sources/WLCM.tsv",
            "target_path": CLEAR / "data/eng/targets/YLT/ot_YLT.tsv",
            "source_family": "TAHOT",
            "expected_sha256": {"alignment": "c2ff294c8572bfad3045ee9f1c2cc808ca5c5f1982d082ccab37098e05dc336f", "source_tokens": "6d4a2de6784a6bb05fa9ebc0965e755cf23bc8eb9794ac8a8e5e402e73457fbd", "target_tokens": "38e625b9887bac4c179e25205912874144910e91a571a7391a2c1de1835cb61e"},
        },
        {
            "family_id": "YLT",
            "scope": "NT",
            "alignment_path": CLEAR_V010 / "data/alignments/eng/YLT/SBLGNT-YLT-manual.json",
            "source_path": CLEAR_V010 / "data/sources/SBLGNT-YLT.tsv",
            "target_path": CLEAR_V010 / "data/targets/SBLGNT-YLT.tsv",
            "source_family": "TAGNT",
            "expected_sha256": {"alignment": "a86712dc114a6f539a3b5d924acd9080ad65adf9e6e5a91740f7a3379aafed14", "source_tokens": "f18cb63db78dc100aaf610c3100dd56048f93f95ed8a691227655ac1a6f55f7e", "target_tokens": "03cae664a9fcd62a56eafb3c5ca0764b6b8f33ecc4381e815207e74aee857f03"},
        },
    )
    path = work / "parallel_bridge_alignment.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    output_digest = sha256()
    count = 0
    summaries: list[dict[str, Any]] = []
    expected_bundle_audit = {
        ("RUSSYN", "OT"): {"records": 182_340, "fully_null": 0, "mixed_null": 0, "cross_verse": 19_939},
        ("RUSSYN", "NT"): {"records": 89_248, "fully_null": 0, "mixed_null": 0, "cross_verse": 13},
        ("YLT", "OT"): {"records": 437_255, "fully_null": 3_133, "mixed_null": 0, "cross_verse": 31_310},
        ("YLT", "NT"): {"records": 127_902, "fully_null": 244, "mixed_null": 6, "cross_verse": 338},
    }
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        def sink(record: Mapping[str, Any]) -> None:
            nonlocal count
            encoded = stable_json(record) + "\n"
            handle.write(encoded)
            output_digest.update(encoded.encode("utf-8"))
            count += 1

        for spec in specs:
            _rows, summary = _load_bridge_bundle(
                universe=universe,
                row_sink=sink,
                collect_rows=False,
                **spec,
            )
            expected = expected_bundle_audit[(summary["family"], summary["scope"])]
            actual = {
                "records": summary["record_count"],
                "fully_null": summary["counts"].get("fully_null_source_records", 0),
                "mixed_null": summary["counts"].get("mixed_null_source_records", 0),
                "cross_verse": summary["cross_verse_manual_record_count"],
            }
            if actual != expected:
                raise RuntimeError(f"Clear bridge structural audit drift for {summary['family']} {summary['scope']}: {actual} != {expected}")
            if summary["counts"].get("rejected_dangling_source", 0) or summary["counts"].get("rejected_dangling_target", 0):
                raise RuntimeError(f"Dangling selector in locked Clear bridge: {summary['family']} {summary['scope']}")
            summaries.append(summary)
    return {"path": path, "count": count, "sha256": output_digest.hexdigest(), "summaries": summaries}


def _source_registry() -> dict[str, Any]:
    _acts_15_34_external_evidence()
    locked = _read_json(STAGE3_REPORT / "source_lock.json")
    wanted = {
        "commons_ohienko_1988_scan",
        "internet_archive_ohienko_1988_scan",
        "wikisource_ohienko_1988_revisions",
        "step_tahot_gen_deu",
        "step_tahot_jos_est",
        "step_tahot_job_sng",
        "step_tahot_isa_mal",
        "step_tagnt_mat_jhn",
        "step_tagnt_act_rev",
        "openscriptures_oshb_v2_2",
        "tanach_us_uxlc_2_5_27_6",
        "unfoldingword_ugnt_v0_34",
        "crosswire_kjv_3_1",
    }
    sources: list[dict[str, Any]] = []
    for source in locked["sources"]:
        if source["source_id"] not in wanted:
            continue
        item = dict(source)
        if source["source_id"].startswith("step_"):
            usage_status = "consumed_primary_raw_reparse"
            token_ids = "SHA-256(step family, pinned commit, exact native locator) plus component suffix"
        elif source["source_id"] in {
            "openscriptures_oshb_v2_2",
            "tanach_us_uxlc_2_5_27_6",
            "unfoldingword_ugnt_v0_34",
        }:
            usage_status = "consumed_original_control_crosswalk_fail_closed"
            token_ids = {
                "openscriptures_oshb_v2_2": "source+commit+member+osisID+native XML word id",
                "tanach_us_uxlc_2_5_27_6": "source+build+member+native ref+child ordinal+element+raw fragment hash",
                "unfoldingword_ugnt_v0_34": "source+commit+member+native ref+word ordinal+raw USFM word fragment hash",
            }[source["source_id"]]
        elif source["source_id"] == "crosswire_kjv_3_1":
            usage_status = "registered_control_not_used_for_transfer"
            token_ids = "control IDs only"
        else:
            usage_status = "consumed_edition_fingerprint_evidence"
            token_ids = "source-native locators retained"
        item.update(
            {
                "coverage": "OT" if "tahot" in source["source_id"] or source["source_id"] in {"openscriptures_oshb_v2_2", "tanach_us_uxlc_2_5_27_6"} else "NT" if source["source_id"] in {"step_tagnt_mat_jhn", "step_tagnt_act_rev", "unfoldingword_ugnt_v0_34"} else "protestant_66/control",
                "versification": "source-native with explicit stage-7 projection to kjv_protestant",
                "token_ids": token_ids,
                "usage_status": usage_status,
            }
        )
        if source["source_id"] == "commons_ohienko_1988_scan":
            item.update(
                {
                    "primary_document": True,
                    "alignment_data": False,
                    "edition_evidence": "exact 1,538-leaf OH1988 jubilee volume; front/back matter and printed notes audited",
                    "rights_evidence_url": "https://blog.wikimedia.org.ua/2013/11/27/otrymano-dozvil-bibliyi-pereklad-ogiyenka/",
                    "rights_ticket": "Wikimedia Commons VRT 2013112610015211",
                }
            )
        sources.append(item)

    historical_sources = (
        {
            "source_id": "ohienko_translation_methodology_1927",
            "title": "Ivan Ohiienko, Methodology of translating Scripture and liturgical books into Ukrainian",
            "version": "Warsaw, Synodal Press, 1927; 33 printed pages",
            "source_page_url": "https://diasporiana.org.ua/movoznavstvo/ogiyenko-i-metodologiya-perekladu-svyatogo-pysma-ta-bogosluzhebnyh-knyg-na-ukrayinsku-movu/",
            "download_url": "https://diasporiana.org.ua/wp-content/uploads/books/29032/file.pdf",
            "bytes": 3_060_387,
            "sha256": "a8b12dec4b44e7421ee0bd3ec12b65eec2a665965421ff8731d17358b29cbd21",
            "coverage": "method statements on printed pp.8-9, 18 and 22",
            "role": "primary historical methodology evidence only; predates the 1936 contract and later revisions",
        },
        {
            "source_id": "ilarion_biblical_studies_volume_1_1963",
            "title": "Metropolitan Ilarion, Biblical Studies, volume 1",
            "version": "Winnipeg, Nasha Kultura, 1963; 287 printed pages",
            "source_page_url": "https://diasporiana.org.ua/religiya/ilarion-mytr-biblijni-studiyi-t-1/",
            "download_url": "https://diasporiana.org.ua/wp-content/uploads/books/20717/file.pdf",
            "bytes": 4_578_743,
            "sha256": "e42bdb501aa544c3fb4b712d9cb547daa8e29db97adc4479dadd0e1d4f34806e",
            "coverage": "translation history and method on printed pp.220-253",
            "role": "primary historical evidence for the 1936-1962 workflow and general textual basis; not proof that OH1988 is unchanged",
        },
    )
    for source in historical_sources:
        sources.append(
            {
                **source,
                "dataset_id": "ohienko_primary_historical_document",
                "independence": "authorial historical testimony; not an original-language witness or alignment vote",
                "pin": {"type": "sha256", "value": source["sha256"]},
                "retrieved_on": "2026-08-08",
                "license": "no open redistribution license stated; treated as copyright-protected research material, with only bibliographic facts, page citations and short paraphrases retained",
                "license_decision": "closed_for_research_citation_only_no_redistribution_no_derived_corpus",
                "license_url": None,
                "local_path": None,
                "versification": "not applicable",
                "token_ids": "not applicable; page citations only",
                "dependencies": [],
                "primary_document": True,
                "alignment_data": False,
                "redistributable": False,
                "usage_status": "research_citation_only_no_corpus_derivation",
            }
        )

    acts_evidence_sources = (
        {
            "source_id": "scrivener_codex_bezae_1864",
            "dataset_id": "codex_bezae_primary_witness",
            "title": "Codex Bezae Cantabrigiensis, Scrivener facsimile/transcription",
            "version": "F. H. A. Scrivener, Cambridge, 1864",
            "source_page_url": "https://commons.wikimedia.org/wiki/File:Bezae_codex_cantabrigiensis_(IA_bezaecodexcantab00scri).pdf",
            "download_url": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Bezae_codex_cantabrigiensis_(IA_bezaecodexcantab00scri).pdf",
            "license": "Public domain",
            "license_url": "https://commons.wikimedia.org/wiki/File:Bezae_codex_cantabrigiensis_(IA_bezaecodexcantab00scri).pdf",
            "lock": ACTS_15_34_EVIDENCE_SOURCES["scrivener_bezae_1864"],
            "coverage": "Acts.15.34, PDF 458 / printed p.384 / manuscript fol.479b",
            "token_ids": "page/folio/verse evidence only; token locators cross-checked by the verification transcription",
            "usage_status": "consumed_primary_locus_evidence",
            "redistributable": True,
        },
        {
            "source_id": "igntp_codex_bezae_greek_xml_v1_03",
            "dataset_id": "igntp_codex_bezae_transcription",
            "title": "IGNTP Codex Bezae Greek electronic transcription",
            "version": "v1.03, 2016-05-26",
            "source_page_url": "https://epapers.bham.ac.uk/2167/",
            "download_url": "https://epapers.bham.ac.uk/id/eprint/2167/1/Bezae-Greek.xml",
            "license": "CC BY-NC-SA 3.0",
            "license_url": "https://creativecommons.org/licenses/by-nc-sa/3.0/",
            "lock": ACTS_15_34_EVIDENCE_SOURCES["bezae_greek_xml_v1_03"],
            "coverage": "verification-only B05K15V34 / P479vC1L18-20-05",
            "token_ids": "native B05 verse and word locators retained only as evidence citations",
            "usage_status": "verification_only_no_derived_corpus_no_alignment_vote",
            "redistributable": False,
        },
        {
            "source_id": "clementine_vulgate_1598_latvuc",
            "dataset_id": "clementine_vulgate_1598",
            "title": "Clementine Vulgate 1598",
            "version": "latVUC eBible frozen USFX export retrieved 2026-08-08",
            "source_page_url": "https://ebible.org/details.php?id=latVUC",
            "download_url": "https://ebible.org/Scriptures/latVUC_usfx.zip",
            "license": "Public domain",
            "license_url": "https://ebible.org/latVUC/copyright.htm",
            "lock": ACTS_15_34_EVIDENCE_SOURCES["clementine_vulgate_1598_usfx"],
            "coverage": "versional evidence at Acts.15.34 only",
            "token_ids": "ACT.15.34 exact verse digest; no Strong or target-token transfer",
            "usage_status": "consumed_versional_locus_evidence_zero_strong_vote",
            "redistributable": True,
        },
    )
    for source in acts_evidence_sources:
        lock = source["lock"]
        sources.append(
            {
                **{key: value for key, value in source.items() if key != "lock"},
                "role": "Acts.15.34 textual fingerprint evidence only",
                "independence": (
                    "Scrivener/D05 and IGNTP XML describe the same manuscript and count as one Greek witness; "
                    "Clementine Vulgate is a separate versional witness"
                ),
                "pin": {"type": "sha256", "value": lock["sha256"]},
                "retrieved_on": "2026-08-08",
                "bytes": lock["bytes"],
                "sha256": lock["sha256"],
                "local_path": str(lock["path"].relative_to(ROOT)).replace("\\", "/"),
                "versification": "source-native Acts.15.34; no grid projection",
                "dependencies": ["Acts.15.34", "commons_ohienko_1988_scan"],
                "primary_document": source["source_id"] == "scrivener_codex_bezae_1864",
                "alignment_data": False,
                "processed_count": 1,
                "skipped_count": 0,
                "error_count": 0,
            }
        )

    clear_heads = {
        CLEAR: "c99bd0ae6946775f932517656308ca19fc706921",
        CLEAR_V010: "cf64cd121bd01866d506c45150e0ab5836920b40",
    }
    for checkout, expected_head in clear_heads.items():
        actual_head = _git_checkout_head(checkout)
        if actual_head != expected_head:
            raise RuntimeError(f"Clear checkout HEAD changed: {checkout.name}: {actual_head}")
    clear_specs = (
        {
            "source_id": "clear_russyn_ot", "root": CLEAR, "title": "RUSSYN OT manual bridge", "status": "licensed_input_imported_original_crosswalk_partial", "scope": "OT",
            "alignment": CLEAR / "data/rus/alignments/RUSSYN/WLCM-RUSSYN-manual.json", "toml": CLEAR / "data/rus/alignments/RUSSYN/WLCM-RUSSYN-manual.toml", "source": CLEAR / "data/sources/WLCM.tsv", "target": CLEAR / "data/rus/targets/RUSSYN/ot_RUSSYN.tsv",
            "toml_sha256": "acdce8d2b40f32bf3dbef08abee147ae70ab77c4abe9f8d3f7ceb0ee21fb183d", "source_label": "WLCM", "target_label": "RUSSYN public domain",
        },
        {
            "source_id": "clear_russyn_nt", "root": CLEAR, "title": "RUSSYN NT manual bridge", "status": "licensed_input_imported_original_crosswalk_partial", "scope": "NT",
            "alignment": CLEAR / "data/rus/alignments/RUSSYN/SBLGNT-RUSSYN-manual.json", "toml": CLEAR / "data/rus/alignments/RUSSYN/SBLGNT-RUSSYN-manual.toml", "source": CLEAR / "data/sources/SBLGNT.tsv", "target": CLEAR / "data/rus/targets/RUSSYN/nt_RUSSYN.tsv",
            "toml_sha256": "91874637c6d697109a7510647956ccaff6a082b203db1eaf019b8c6304c4b83c", "source_label": "SBLGNT CC BY 4.0", "target_label": "RUSSYN public domain",
        },
        {
            "source_id": "clear_ylt_ot", "root": CLEAR, "title": "YLT OT manual bridge", "status": "licensed_input_imported_original_crosswalk_partial", "scope": "OT",
            "alignment": CLEAR / "data/eng/alignments/YLT/WLC-YLT-manual.json", "toml": CLEAR / "data/eng/alignments/YLT/WLC-YLT-manual.toml", "source": CLEAR / "data/sources/WLCM.tsv", "target": CLEAR / "data/eng/targets/YLT/ot_YLT.tsv",
            "toml_sha256": "2bd55731993071ea40584528bfed86740a082f44d913e518c9ba59ce191aef0e", "source_label": "declared WLC but frozen IDs are WLCM-backed", "target_label": "YLT public domain",
        },
        {
            "source_id": "clear_ylt_nt_v010_transfer", "root": CLEAR_V010, "title": "YLT NT v0.1.0 manual SBLGNT transfer", "status": "licensed_input_imported_original_crosswalk_partial", "scope": "NT",
            "alignment": CLEAR_V010 / "data/alignments/eng/YLT/SBLGNT-YLT-manual.json", "toml": CLEAR_V010 / "data/alignments/eng/YLT/SBLGNT-YLT-manual.toml", "source": CLEAR_V010 / "data/sources/SBLGNT-YLT.tsv", "target": CLEAR_V010 / "data/targets/SBLGNT-YLT.tsv",
            "toml_sha256": "33c74d1041e85dbafbdcad8dccf9c613aa79bafb9fa5c7e1cb311cc206eb687f", "source_label": "SBLGNT CC BY 4.0", "target_label": "YLT public domain",
        },
        {
            "source_id": "clear_ylt_nt_main_alias", "root": CLEAR, "title": "Mislabelled current-main YLT NT positional alias", "status": "rejected_integrity", "scope": "NT",
            "alignment": CLEAR / "data/eng/alignments/YLT/SBLGNT-YLT-manual.json", "toml": CLEAR / "data/eng/alignments/YLT/SBLGNT-YLT-manual.toml", "source": None, "target": None,
            "toml_sha256": _sha256_file(CLEAR / "data/eng/alignments/YLT/SBLGNT-YLT-manual.toml"), "source_label": "mislabelled NA27 positional source", "target_label": "YLT public domain",
        },
    )
    for spec in clear_specs:
        source_id = spec["source_id"]
        root = spec["root"]
        path = spec["alignment"]
        commit = clear_heads[root]
        files = []
        for role in ("alignment", "toml", "source", "target"):
            file_path = spec.get(role)
            if file_path is None:
                continue
            files.append(
                {
                    "role": role,
                    "local_path": str(file_path.relative_to(ROOT)).replace("\\", "/"),
                    "bytes": file_path.stat().st_size,
                    "sha256": _sha256_file(file_path),
                    "canonical_lf_sha256": _sha256_git_text(file_path),
                }
            )
        if _sha256_file(spec["toml"]) != spec["toml_sha256"]:
            raise RuntimeError(f"Clear tokenizer metadata changed: {source_id}")
        sources.append(
            {
                "source_id": source_id,
                "dataset_id": "clear_bible_alignments",
                "title": spec["title"],
                "role": "independent manually curated original-to-translation bridge; target-to-OH edge requires separate evidence",
                "independence": "RUSSYN and YLT are separate bridge families but share Clear tooling and original witnesses",
                "source_page_url": f"https://github.com/Clear-Bible/Alignments/tree/{commit}",
                "download_url": f"https://github.com/Clear-Bible/Alignments/blob/{commit}/{path.relative_to(root).as_posix()}",
                "version": f"git commit {commit}",
                "pin": {"type": "git_commit", "value": commit},
                "retrieved_on": "2026-08-01",
                "bytes": sum(item["bytes"] for item in files),
                "sha256": _sha256_file(path),
                "files": files,
                "license": f"Clear alignment metadata CC BY 4.0; source {spec['source_label']}; target {spec['target_label']}",
                "license_url": f"https://github.com/Clear-Bible/Alignments/blob/{commit}/LICENSE.md",
                "local_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "coverage": spec["scope"],
                "versification": "BCVWP source-native; target token IDs validated against exact TSV",
                "token_ids": "BCVWP selectors; remapped only with surface/Strong evidence",
                "tokenizer_metadata": "LatinWordTokenizer declared without implementation version; frozen TSV only" if source_id != "clear_ylt_nt_v010_transfer" else "tag v0.1.0 TOML does not declare a tokenizer; frozen TSV only",
                "dependencies": [item["local_path"] for item in files],
                "usage_status": spec["status"],
            }
        )

    stage6_verse_keys = {
        str(row["verse_key"]) for row in _read_jsonl(STAGE6_TEXT)
    }
    for filename, lock in LOCAL_DB_LOCKS.items():
        db_path = LOCAL_DB / filename
        if not db_path.is_file():
            raise RuntimeError(f"Owner-approved read-only control is missing: {filename}")
        actual_sha = _sha256_file(db_path)
        if actual_sha != lock["sha256"] or db_path.stat().st_size != lock["bytes"]:
            raise RuntimeError(f"Owner-approved read-only control changed: {filename}")
        connection = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        connection.execute("PRAGMA query_only=ON")
        metadata = dict(connection.execute("SELECT key,value FROM db_metadata"))
        if filename == "revelation_uk.sqlite":
            record_count = connection.execute(
                "SELECT count(*) FROM greek_descs"
            ).fetchone()[0]
            title = "Owner-local Ukrainian Greek Strong descriptions"
            license_text = (
                "first-party compiled project database; owner-authorized read-only "
                "context use; no rows redistributed by stage 7"
            )
            role = "G-number lexical context only; no original-to-OH assignment vote"
            coverage = f"NT Greek descriptions: {record_count}"
            token_ids = "classic G integer IDs"
            usage_status = "consumed_read_only_lexical_context_zero_vote"
            source_id = "local_revelation_uk_greek_descs"
        else:
            info_columns = [
                item[1] for item in connection.execute("PRAGMA table_info(info)")
            ]
            info_values = connection.execute("SELECT * FROM info").fetchone()
            info = dict(zip(info_columns, info_values))
            record_count = connection.execute("SELECT count(*) FROM verses").fetchone()[0]
            distinct_key_count = connection.execute(
                "SELECT count(DISTINCT verse_key) FROM verses"
            ).fetchone()[0]
            local_verse_keys = {
                str(item[0]) for item in connection.execute("SELECT verse_key FROM verses")
            }
            if (
                record_count != EXPECTED_TARGET_COUNT
                or distinct_key_count != EXPECTED_TARGET_COUNT
                or local_verse_keys != stage6_verse_keys
            ):
                raise RuntimeError(f"Local Bible control grid changed: {filename}")
            title = str(info["title"])
            license_text = str(info["license"])
            role = (
                "additional Greek LXX/TR diagnostic control only; no automatic Strong transfer"
                if filename == "bible_lxx_tr.sqlite"
                else "additional KJV control only; no automatic Strong transfer"
            )
            coverage = f"protestant_66 / kjv_protestant: {record_count} rows"
            token_ids = "verse_key plus inline source-owned token markers; never OH ground truth"
            usage_status = "consumed_read_only_control_zero_vote"
            source_id = (
                "local_bible_lxx_tr_control"
                if filename == "bible_lxx_tr.sqlite"
                else "local_bible_kjv_control"
            )
        connection.close()
        sources.append(
            {
                "source_id": source_id,
                "dataset_id": "owner_local_sha_locked_read_only_control",
                "title": title,
                "role": role,
                "independence": "additional context/control; never an independent automatic vote",
                "source_page_url": "owner-local fixed environment",
                "download_url": None,
                "version": metadata,
                "pin": {"type": "sha256", "value": actual_sha},
                "retrieved_on": "2026-08-08",
                "bytes": db_path.stat().st_size,
                "sha256": actual_sha,
                "license": license_text,
                "license_url": None,
                "local_path": f"[owner-local]/revelation/db/{filename}",
                "coverage": coverage,
                "versification": "not applicable"
                if filename == "revelation_uk.sqlite"
                else "kjv_protestant",
                "token_ids": token_ids,
                "dependencies": [],
                "usage_status": usage_status,
                "processed_count": record_count,
                "exact_stage6_key_equality": None
                if filename == "revelation_uk.sqlite"
                else True,
                "skipped_count": 0,
                "error_count": 0,
            }
        )
    stage_inputs = (
        ("stage6_synthesized_text", STAGE6_TEXT, "immutable primary target text"),
        ("stage6_target_comments", STAGE6_COMMENTS, "immutable target comments"),
        ("stage5_forward_mapping", STAGE5_WORK / "source_to_target_map.jsonl", "immutable mapping"),
        ("stage5_reverse_mapping", STAGE5_WORK / "target_to_source_map.jsonl", "immutable mapping"),
        ("stage5_footnote_projection", STAGE5_WORK / "footnote_projection.jsonl", "immutable footnote projection"),
    )
    for source_id, path, role in stage_inputs:
        sources.append(
            {
                "source_id": source_id,
                "dataset_id": "revelation_stage_input",
                "title": source_id,
                "role": role,
                "independence": "normative upstream artifact",
                "source_page_url": None,
                "download_url": None,
                "version": MAPPING_CONTRACT,
                "pin": {"type": "sha256", "value": _sha256_file(path)},
                "retrieved_on": "2026-08-01",
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
                "license": "first-party derived project artifact",
                "license_url": None,
                "local_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "coverage": "31,102 target positions" if "stage6" in source_id else "full forward/reverse map",
                "versification": "kjv_protestant",
                "token_ids": "stable stage IDs and hashes",
                "dependencies": [MAPPING_CONTRACT],
                "usage_status": "accepted_immutable",
            }
        )
    legacy_snapshot = LEGACY_REPORT / "experiment_snapshot.manifest.json"
    if _sha256_file(legacy_snapshot) != EXPECTED_LEGACY_SNAPSHOT_SHA256:
        raise RuntimeError("Rejected legacy experiment snapshot changed")
    sources.append(
        {
            "source_id": "ukrainian_stage_7_rejected_legacy_experiment",
            "dataset_id": "revelation_rejected_alignment_baseline",
            "title": "Rejected Ukrainian stage-7 positional Strong experiment",
            "role": "zero-vote error-measurement baseline and negative-counterexample provenance only",
            "independence": "rejected first-party derivative; never an independent evidence vote or ground truth",
            "source_page_url": "scripts/bible_module/reports/ukrainian_stage_7_experiment_20260801/README.ru.md",
            "download_url": None,
            "version": "ukrainian-stage-7-experiment-snapshot-v1",
            "pin": {"type": "sha256", "value": EXPECTED_LEGACY_SNAPSHOT_SHA256},
            "retrieved_on": "2026-08-01",
            "bytes": legacy_snapshot.stat().st_size,
            "sha256": EXPECTED_LEGACY_SNAPSHOT_SHA256,
            "license": "first-party rejected derived artifact; upstream sources remain governed by their registered licenses",
            "license_url": None,
            "local_path": str(legacy_snapshot.relative_to(ROOT)).replace("\\", "/"),
            "coverage": "31,102 target positions; 440,280 rejected Strong occurrences; 399,645 rejected surface bindings",
            "versification": "kjv_protestant",
            "token_ids": "legacy source/surface IDs retained only for negative counterexamples; assignment identity is not trusted",
            "dependencies": [
                "stage6_synthesized_text",
                "step_tahot_gen_deu",
                "step_tahot_jos_est",
                "step_tahot_job_sng",
                "step_tahot_isa_mal",
                "step_tagnt_mat_jhn",
                "step_tagnt_act_rev",
            ],
            "usage_status": "rejected_zero_vote_baseline_only",
        }
    )
    contextual_snapshot_audit = validate_model_snapshot(
        CONTEXTUAL_MODEL_SNAPSHOT
    )
    sources.append(
        {
            "source_id": "awesome_align_with_co_contextual_model",
            "dataset_id": "huggingface_model_snapshot",
            "title": CONTEXTUAL_MODEL_ID,
            "role": "multilingual contextual candidate feature only; never an automatic link",
            "independence": "independent model channel; model score is uncalibrated and carries no acceptance vote",
            "source_page_url": CONTEXTUAL_MODEL_REPOSITORY_URL,
            "download_url": f"{CONTEXTUAL_MODEL_REPOSITORY_URL}/tree/{CONTEXTUAL_MODEL_REVISION}",
            "version": CONTEXTUAL_MODEL_REVISION,
            "pin": {
                "type": "git_commit_and_file_sha256",
                "value": CONTEXTUAL_MODEL_REVISION,
            },
            "retrieved_on": "2026-08-08",
            "bytes": sum(int(value["size"]) for value in CONTEXTUAL_MODEL_FILES.values()),
            "sha256": MODEL_SNAPSHOT_CONTRACT_SHA256,
            "files": contextual_snapshot_audit["files"],
            "license": CONTEXTUAL_MODEL_LICENSE,
            "license_url": f"{CONTEXTUAL_MODEL_REPOSITORY_URL}/blob/{CONTEXTUAL_MODEL_REVISION}/README.md",
            "local_path": str(CONTEXTUAL_MODEL_SNAPSHOT.relative_to(ROOT)).replace("\\", "/"),
            "coverage": "all OT/NT target refs with nonempty selected original and Ukrainian token sequences",
            "versification": "verse-local kjv_protestant selected-original layer",
            "token_ids": "exact stage-7 original/target stable IDs after subword-to-surface projection",
            "dependencies": [
                "fingerprint_selected_original_layer",
                "stage6_synthesized_text",
            ],
            "usage_status": "consumed_candidate_only_no_auto_acceptance",
            "processed_count": contextual_snapshot_audit["processed_count"],
            "skipped_count": contextual_snapshot_audit["skipped_count"],
            "error_count": contextual_snapshot_audit["error_count"],
            "redistributable": False,
        }
    )
    contextual_runtime_audit = validate_runtime_install_report(
        CONTEXTUAL_RUNTIME_INSTALL_REPORT
    )
    sources.append(
        {
            "source_id": "contextual_python_runtime_lock",
            "dataset_id": "local_tool_runtime",
            "title": "Pinned AWESOME-align local Python runtime",
            "role": "exact local-only execution environment for contextual candidate extraction",
            "independence": "tooling dependency; no linguistic evidence vote",
            "source_page_url": "https://pypi.org/project/transformers/4.57.6/",
            "download_url": None,
            "version": "CPython 3.12 / Windows amd64 / transformers 4.57.6",
            "pin": {
                "type": "pip_report_plus_distribution_record_sha256",
                "value": RUNTIME_INSTALL_REPORT_SHA256,
            },
            "retrieved_on": "2026-08-08",
            "bytes": CONTEXTUAL_RUNTIME_INSTALL_REPORT.stat().st_size,
            "sha256": RUNTIME_INSTALL_REPORT_SHA256,
            "files": contextual_runtime_audit["packages"],
            "runtime_environment": [
                {"package": name, **lock}
                for name, lock in sorted(
                    CONTEXTUAL_RUNTIME_ENVIRONMENT_LOCKS.items()
                )
            ],
            "license": "tool-only mixed permissive/open-source environment; exact per-package licenses retained in runtime_environment",
            "license_url": "https://pypi.org/project/transformers/4.57.6/",
            "local_path": str(
                CONTEXTUAL_RUNTIME_INSTALL_REPORT.relative_to(ROOT)
            ).replace("\\", "/"),
            "coverage": "contextual extraction runtime only",
            "versification": "not applicable",
            "token_ids": "not applicable",
            "dependencies": [
                item["artifact_url"]
                for _, item in sorted(CONTEXTUAL_RUNTIME_PACKAGE_CONTRACTS.items())
            ],
            "usage_status": "consumed_local_tooling_not_redistributed_with_app",
            "processed_count": len(CONTEXTUAL_RUNTIME_ENVIRONMENT_LOCKS),
            "skipped_count": 0,
            "error_count": 0,
            "redistributable": False,
        }
    )
    statistical_module = ROOT / "scripts/bible_module/ukrainian_stage_7_statistical.py"
    sources.append(
        {
            "source_id": "first_party_bidirectional_ibm1_generator",
            "dataset_id": "revelation_first_party_tool",
            "title": "Stage-7 bidirectional IBM Model 1 OOF generator",
            "role": "statistical candidate feature only; never an automatic link",
            "independence": "first-party deterministic implementation; no pretrained model or external candidate corpus",
            "source_page_url": "scripts/bible_module/ukrainian_stage_7_statistical.py",
            "download_url": None,
            "version": "ibm1-bidirectional-oof-v1",
            "pin": {"type": "sha256", "value": _sha256_file(statistical_module)},
            "retrieved_on": "2026-08-08",
            "bytes": statistical_module.stat().st_size,
            "sha256": _sha256_file(statistical_module),
            "license": "Apache-2.0",
            "license_url": "LICENSE",
            "local_path": str(statistical_module.relative_to(ROOT)).replace("\\", "/"),
            "coverage": "five target-ref OOF folds over the selected original/Ukrainian parallel corpus",
            "versification": "verse-local kjv_protestant",
            "token_ids": "exact stage-7 original/target stable IDs",
            "dependencies": [
                "fingerprint_selected_original_layer",
                "stage6_synthesized_text",
            ],
            "usage_status": "consumed_candidate_only_no_auto_acceptance",
            "processed_count": 1,
            "skipped_count": 0,
            "error_count": 0,
        }
    )
    sources.sort(key=lambda item: item["source_id"])
    registry = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "artifact": "source_registry",
        "status": "locked_inputs_with_explicit_partial_use_and_rejections",
        "edition_id": "ohienko_1988",
        "module_id": "ohienko_1988",
        "code": "OH1988",
        "canon": "protestant_66",
        "versification": "kjv_protestant",
        "mapping_contract_version": MAPPING_CONTRACT,
        "sources": sources,
        "dependency_graph": [
            {"from": "TAHOT/TAGNT", "to": "original_token_universe", "relation": "primary original tokens"},
            {"from": "Clear RUSSYN/YLT", "to": "parallel_bridge_alignment", "relation": "manual source bridge only"},
            {"from": "parallel_bridge_alignment", "to": "OH1988", "relation": "not established until separate target evidence and gold"},
            {"from": "legacy experiment", "to": "alignment candidates", "relation": "rejected zero-vote baseline only"},
            {"from": "Ohiienko 1927 / Ilarion 1963", "to": "textual_fingerprint", "relation": "primary historical method evidence; citation-only, no token assignment"},
            {"from": "Scrivener D05 + verification-only IGNTP XML", "to": "Acts.15.34 fingerprint", "relation": "one Greek witness with fixed native word locators; no corpus transfer"},
            {"from": "Clementine Vulgate 1598", "to": "Acts.15.34 target addition", "relation": "independent public-domain versional evidence; no Strong transfer"},
            {"from": "OH1988 Wikisource transcription", "to": "OH1988 Commons scan", "relation": "derived transcription of the same exact edition, not an independent witness"},
            {"from": "owner-local revelation_uk", "to": "lexical candidate context", "relation": "SHA-locked G-description context with zero automatic vote"},
            {"from": "owner-local LXX_TR/KJV", "to": "diagnostic controls", "relation": "SHA-locked read-only context; no Strong transfer and no redistributed corpus rows"},
            {"from": "selected original layer + stage6 target", "to": "bidirectional IBM1 OOF candidates", "relation": "first-party candidate-only statistical channel; no acceptance vote"},
            {"from": "selected original layer + stage6 target + pinned AWESOME-align snapshot/runtime", "to": "multilingual contextual candidates", "relation": "local-only contextual channel; no acceptance vote before gold calibration"},
        ],
        "processed_count": len(sources),
        "skipped_count": 0,
        "error_count": 0,
        "input_sha256": {
            "stage3_source_lock": _sha256_file(STAGE3_REPORT / "source_lock.json"),
            **{
                f"owner_local_{filename}": lock["sha256"]
                for filename, lock in sorted(LOCAL_DB_LOCKS.items())
            },
            "contextual_model_snapshot_contract": MODEL_SNAPSHOT_CONTRACT_SHA256,
            "contextual_runtime_install_report": RUNTIME_INSTALL_REPORT_SHA256,
            "statistical_generator": _sha256_file(statistical_module),
        },
        "output_sha256": {},
        "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
    }
    return registry


_FINGERPRINT = (
    ("Gen.4.8", "OT", "textual_variant", "OH1988 follows the shorter Hebrew clause", "TAHOT type X preserves the reconstructed LXX addition as alternative only", "primary_mt", "resolved_at_exact_edition", "high"),
    ("Deut.32.8", "OT", "textual_variant", "OH1988 reads the number of the sons of Israel", "ancient-version/scroll alternatives require source-specific citation", "primary_mt", "resolved_at_exact_edition", "high"),
    ("Judg.18.30", "OT", "textual_variant", "exact OH1988 reading is frozen", "Manasseh/Moses scribal reading requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("1Sam.13.1", "OT", "textual_variant", "exact OH1988 reading is frozen", "TAHOT type X reconstruction is alternative, never MT primary", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("1Sam.14.41", "OT", "textual_variant", "exact OH1988 reading is frozen", "TAHOT type X reconstructed addition requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("2Sam.21.19", "OT", "textual_variant", "exact OH1988 reading is frozen", "Goliath/brother-of-Goliath harmonization requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Ps.22.16", "OT", "textual_variant", "OH1988 reads a piercing expression", "native Hebrew control is Ps.22.17; ketiv/qere and ancient witnesses differ", "blocked_at_locus", "unresolved_blocks_automatic", "critical"),
    ("Ps.40.6", "OT", "textual_variant", "OH1988 reads opened ears", "native Hebrew control is Ps.40.7; Greek/Hebrews tradition has body prepared", "primary_mt", "resolved_at_exact_edition", "high"),
    ("Ps.145.13", "OT", "textual_variant", "exact OH1988 reading is frozen", "TAHOT type X reconstructed addition requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Isa.7.14", "OT", "translation_choice", "primary Hebrew token universe is retained", "Ukrainian virgin is a lexical choice and does not itself prove an LXX source", "primary_mt", "resolved_original_tokens_not_translation_source", "high"),
    ("Jonah.3.4", "OT", "textual_variant", "OH1988 reads forty days", "the ancient-version three-day reading is not selected", "primary_mt", "resolved_at_exact_edition", "high"),
    ("Isa.53.5", "OT", "alignment_counterexample", "MT component universe is retained", "legacy position bindings are rejected; this is not itself a textual-base diagnostic", "primary_mt", "resolved_original_universe_alignment_pending", "critical"),
    ("Mic.6.8", "OT", "alignment_counterexample", "MT component universe is retained", "legacy position bindings are rejected; this is not itself a textual-base diagnostic", "primary_mt", "resolved_original_universe_alignment_pending", "critical"),
    ("Mat.1.25", "NT", "textual_variant", "OH1988 includes the traditional firstborn expression", "critical witnesses omit the expansion", "primary_traditional", "resolved_at_exact_edition", "high"),
    ("Mat.5.22", "NT", "textual_variant", "exact OH1988 reading is frozen", "without-cause expansion requires exact locus adjudication; Treg alone is not modern-critical evidence", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mat.6.13", "NT", "textual_variant", "exact OH1988 reading is frozen", "doxology status requires exact locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mat.17.21", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mat.18.11", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mat.20.16", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional expansion requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mat.23.14", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mark.1.2", "NT", "textual_variant", "OH1988 locus contains a mixed witness profile", "Isaiah/prophets readings must be selected component by component", "mixed_locus_specific", "resolved_at_exact_edition", "high"),
    ("Mark.7.16", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mark.9.44", "NT", "textual_variant", "exact OH1988 reading is frozen", "repeated traditional clause requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mark.9.46", "NT", "textual_variant", "exact OH1988 reading is frozen", "repeated traditional clause requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mark.11.26", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mark.15.28", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Mark.16.9", "NT", "textual_variant", "OH1988 includes the long ending", "critical witnesses omit Mark 16:9-20", "primary_traditional", "resolved_at_exact_edition", "critical"),
    ("Mark.16.20", "NT", "textual_variant", "OH1988 includes the long ending through verse 20", "critical witnesses omit Mark 16:9-20", "primary_traditional", "resolved_at_exact_edition", "critical"),
    ("Luke.2.11", "NT", "alignment_counterexample", "shared-witness original components are retained", "legacy position bindings are rejected", "primary_shared", "resolved_original_universe_alignment_pending", "critical"),
    ("Luke.9.55", "NT", "textual_variant", "exact OH1988 reading is frozen", "rebuke expansion requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Luke.9.56", "NT", "textual_variant", "exact OH1988 reading is frozen", "Son-of-Man expansion requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Luke.17.36", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Luke.22.43", "NT", "textual_variant", "exact OH1988 reading is frozen", "angel/agony passage requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Luke.22.44", "NT", "textual_variant", "exact OH1988 reading is frozen", "angel/agony passage requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Luke.23.17", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Luke.23.34", "NT", "textual_variant", "exact OH1988 reading is frozen", "forgiveness saying requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("John.1.18", "NT", "textual_variant", "OH1988 reads only-begotten Son", "TAGNT column-6 Son candidate is preserved separately from the primary God component", "primary_traditional", "resolved_at_exact_edition", "critical"),
    ("John.5.4", "NT", "textual_variant", "exact OH1988 reading is frozen", "angel/water passage requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("John.7.53", "NT", "textual_variant", "OH1988 includes the pericope", "critical witnesses omit John 7:53-8:11", "primary_traditional", "resolved_at_exact_edition", "critical"),
    ("John.8.11", "NT", "textual_variant", "OH1988 includes the pericope through verse 11", "critical witnesses omit John 7:53-8:11", "primary_traditional", "resolved_at_exact_edition", "critical"),
    ("Acts.2.38", "NT", "alignment_counterexample", "shared lexical core is retained locus-specifically", "legacy position bindings are rejected", "locus_specific", "resolved_original_universe_alignment_pending", "critical"),
    ("Acts.8.37", "NT", "textual_variant", "OH1988 includes the traditional verse", "critical witnesses omit the verse", "primary_traditional", "resolved_at_exact_edition", "critical"),
    ("Acts.15.34", "NT", "textual_variant", "exact OH1988 target position is frozen", "traditional verse/critical omission and possible null/addition state require adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "critical"),
    ("Acts.24.7", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional expansion requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Acts.28.29", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional verse/critical omission requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Rom.8.1", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional expansion requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("1Cor.14.34", "NT", "textual_variant", "exact OH1988 reading is frozen", "transposition evidence requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("1John.5.7", "NT", "textual_variant", "OH1988 includes the Comma Johanneum", "critical witnesses omit the expansion", "primary_traditional", "resolved_at_exact_edition", "critical"),
    ("Eph.3.9", "NT", "textual_variant", "exact OH1988 reading is frozen", "traditional through-Jesus-Christ expansion requires adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("Col.1.14", "NT", "textual_variant", "exact OH1988 reading is frozen", "through-his-blood expansion requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "high"),
    ("1Tim.3.16", "NT", "textual_variant", "exact OH1988 reading is frozen", "God/who textual reading requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "critical"),
    ("Rev.1.11", "NT", "textual_variant", "OH1988 omits the TR Alpha/Omega and Asia expansions", "TR contains the expansions", "primary_critical", "resolved_at_exact_edition", "high"),
    ("Rev.22.19", "NT", "textual_variant", "exact OH1988 reading and printed note are frozen", "book/tree-of-life variation requires locus adjudication", "blocked_at_locus", "unresolved_blocks_automatic", "critical"),
)

_FINGERPRINT_NATIVE_CONTROL_REFS = {
    "Ps.22.16": "Ps.22.17",
    "Ps.40.6": "Ps.40.7",
}

_FINGERPRINT_CONTROL_ID_INVENTORIES = {
    "Ps.22.16": {
        "openscriptures_oshb_v2_2": {
            "native_ref": "Ps.22.17",
            "token_count": 9,
            "token_id_inventory_sha256": "dfa3ffcef81521e79c6b16663a9c1f498d12545dfb875cbf7d36abd48384e1bd",
        },
        "tanach_us_uxlc_2_5_27_6": {
            "native_ref": "Ps.22.17",
            "token_count": 9,
            "token_id_inventory_sha256": "0ed590c3bbbb490e5bf438db321d845b5a03d441858947aa942979de04fd674b",
        },
    },
    "Ps.40.6": {
        "openscriptures_oshb_v2_2": {
            "native_ref": "Ps.40.7",
            "token_count": 11,
            "token_id_inventory_sha256": "268a4293481110b5b8e15d9a464b98934a7308f69b88ef6e11879dfd7025f476",
        },
        "tanach_us_uxlc_2_5_27_6": {
            "native_ref": "Ps.40.7",
            "token_count": 11,
            "token_id_inventory_sha256": "73b97b3dcd2ff4b5b7a4eae8e6ade5b3e5ea1c6c9b76a4f2aa93923ff847ab3b",
        },
    },
}

_FINGERPRINT_COMPONENT_ONLY_REFS = frozenset(
    {
        "Mat.17.21",
        "Mat.18.11",
        "Mat.23.14",
        "Mark.7.16",
        "Mark.9.44",
        "Mark.9.46",
        "Mark.11.26",
        "Mark.15.28",
        "Luke.17.36",
        "Luke.23.17",
        "John.5.4",
        "Acts.8.37",
        "Acts.24.7",
        "Acts.28.29",
    }
)

_FINGERPRINT_PRIMARY_PLUS_COMPONENT_REFS = frozenset(
    {"Mat.6.13", "Luke.9.55", "Luke.9.56", "Rom.8.1"}
)

_FINGERPRINT_UNRESOLVED = {
    "Mark.1.2": "high",
    "Mark.16.9": "critical",
    "Acts.2.38": "critical",
    "1Cor.14.34": "high",
    "Rev.22.19": "critical",
}

_FINGERPRINT_CHOICE_LOCATORS = {
    "Mark.1.2": "Mrk.1.2#01=N(k)O",
    "Mark.16.9": "Mrk.16.9#11=(k)O",
    "Acts.2.38": "Act.2.38#11=NK(o)",
    "1Cor.14.34": "1Co.14.34#10=N(k)O",
    "Rev.22.19": "Rev.22.19#09=N(k)O",
}

# These five decisions are deliberately applied only after the candidate layer
# has been frozen.  The candidate generators therefore continue to see both
# source readings as excluded alternatives and cannot learn from the eventual
# manual answer.  Gold/manual review receives a separate, source-qualified
# overlay.  Column 12 is a dictionary/lexical candidate and is never promoted
# to a textual witness.
_POST_CANDIDATE_TEXTUAL_CHOICES: dict[str, dict[str, Any]] = {
    "Mark.1.2": {
        "severity": "high",
        "source_locator": "Mrk.1.2#01=N(k)O",
        "primary_id": "tagnt:3cbc5376d9fe8246c3fd50992b59a400c4b56eed211fdad65df3449e640ed6b4:c01",
        "alternative_id": "tagnt:3cbc5376d9fe8246c3fd50992b59a400c4b56eed211fdad65df3449e640ed6b4:alternative:tagnt-c06:01",
        "excluded_lexical_id": "tagnt:3cbc5376d9fe8246c3fd50992b59a400c4b56eed211fdad65df3449e640ed6b4:alternative:tagnt-c12:01",
        "expected_strongs": [["G2531"], ["G5613"]],
        "target": {"token_id": "uk7:IOQ:001:0:2", "surface": "Як", "start_scalar": 0, "end_scalar": 2, "start_byte": 0, "end_byte": 4},
        "disposition": "resolved_manual_textual_alternative_group_no_rendered_strong",
        "rendered_strong": [],
        "rationale": "OH1988 Як does not distinguish καθώς/G2531 from ὡς/G5613; the mixed whole-locus profile forbids coherent-edition inference.",
    },
    "Mark.16.9": {
        "severity": "critical",
        "source_locator": "Mrk.16.9#11=(k)O",
        "primary_id": "tagnt:f1ba04085dcf52d7f7b61bfaad8940dc6527a921a48ecb064c4cec151acd6aea:c01",
        "alternative_id": "tagnt:f1ba04085dcf52d7f7b61bfaad8940dc6527a921a48ecb064c4cec151acd6aea:alternative:tagnt-c06:01",
        "excluded_lexical_id": "tagnt:f1ba04085dcf52d7f7b61bfaad8940dc6527a921a48ecb064c4cec151acd6aea:alternative:tagnt-c12:01",
        "expected_strongs": [["G3844"], ["G575"]],
        "target": {"token_id": "uk7:J77:014:82:84", "surface": "із", "start_scalar": 82, "end_scalar": 84, "start_byte": 148, "end_byte": 152},
        "disposition": "resolved_manual_textual_alternative_group_no_rendered_strong",
        "rendered_strong": [],
        "rationale": "Verse inclusion does not distinguish παρά/G3844 from ἀπό/G575 at the exact Ukrainian span.",
    },
    "Acts.2.38": {
        "severity": "critical",
        "source_locator": "Act.2.38#11=NK(o)",
        "primary_id": "tagnt:e5976a61a8cc38ebb9265813a427cc51cabe202bd40202f2057e6f6a83e5e1f0:c01",
        "alternative_id": "tagnt:e5976a61a8cc38ebb9265813a427cc51cabe202bd40202f2057e6f6a83e5e1f0:alternative:tagnt-c06:01",
        "excluded_lexical_id": "tagnt:e5976a61a8cc38ebb9265813a427cc51cabe202bd40202f2057e6f6a83e5e1f0:alternative:tagnt-c12:01",
        "expected_strongs": [["G1909"], ["G1722"]],
        "target": {"token_id": "uk7:KTO:014:69:70", "surface": "у", "start_scalar": 69, "end_scalar": 70, "start_byte": 124, "end_byte": 126},
        "disposition": "resolved_manual_b_primary_component",
        "rendered_strong": ["G1909"],
        "rationale": "The whole-locus OH1988 wording agrees with the NA/Tyn component chain (present φησίν and ὑμῶν); those witnesses read ἐπί/G1909. Manual B only, never A_auto.",
    },
    "1Cor.14.34": {
        "severity": "high",
        "source_locator": "1Co.14.34#10=N(k)O",
        "primary_id": "tagnt:61666077ea81e467ffe1fe7b8e659c098d3ae332557bb4c58b93a084ca98e0ba:c01",
        "alternative_id": "tagnt:61666077ea81e467ffe1fe7b8e659c098d3ae332557bb4c58b93a084ca98e0ba:alternative:tagnt-c06:01",
        "excluded_lexical_id": None,
        "expected_strongs": [["G2010"], ["G2010"]],
        "target": {"token_id": "uk7:M5L:011:53:62", "surface": "позволено", "start_scalar": 53, "end_scalar": 62, "start_byte": 95, "end_byte": 113},
        "disposition": "resolved_manual_textual_alternative_group_strong_equivalent",
        "rendered_strong": ["G2010"],
        "rationale": "The inflectional variants are textually distinct but both normalize to G2010; the exact form remains unclaimed and the Strong is rendered once.",
    },
    "Rev.22.19": {
        "severity": "critical",
        "source_locator": "Rev.22.19#09=N(k)O",
        "primary_id": "tagnt:8b881dd509f566c824bd1d707bfba93111c223ec22d8b213480e6f4bd6e532e7:c01",
        "alternative_id": "tagnt:8b881dd509f566c824bd1d707bfba93111c223ec22d8b213480e6f4bd6e532e7:alternative:tagnt-c06:01",
        "excluded_lexical_id": "tagnt:8b881dd509f566c824bd1d707bfba93111c223ec22d8b213480e6f4bd6e532e7:alternative:tagnt-c12:01",
        "expected_strongs": [["G975"], ["G976"]],
        "target": {"token_id": "uk7:NZW:008:32:37", "surface": "книги", "start_scalar": 32, "end_scalar": 37, "start_byte": 57, "end_byte": 67},
        "disposition": "resolved_manual_textual_alternative_group_no_rendered_strong",
        "rendered_strong": [],
        "rationale": "OH1988 книги does not distinguish βιβλίον/G975 from βίβλος/G976; the separate tree-of-life choice cannot prove this synonymous component.",
    },
}

_ACTS_15_34_SUPPLEMENTAL_UGNT_IDS = (
    "ugnt:19394bb7cec7b91be5c78842776cb3e30ec6ecc7cf14bef8d8edb48de698ef3c",
    "ugnt:581705fbbed0537228dbe0e6895759d52fbe48812ea78ad425ee07219baf119d",
    "ugnt:ff4f1c42aa3873b0ab4ff3593c1daf6093ebd301f26e9b732532030e0598b0eb",
    "ugnt:30ab2d8ca95393c85bf9d92f8764715a61d87471a714bc436c486545f75640c9",
)

def _fingerprint_selection(
    ref: str,
    primary_ids: Sequence[str],
    component_ids: Sequence[str],
    apparatus_ids: Sequence[str],
    universe: Mapping[str, Any],
) -> dict[str, Any]:
    """Resolve the audited 53-locus component overlay without global guessing."""

    component_meta = universe["original_meta"]
    apparatus_meta = universe["alternative_meta"]

    def component_at(locator: str) -> list[str]:
        return [
            token_id
            for token_id in [*primary_ids, *component_ids]
            if component_meta[token_id]["source_locator"] == locator
        ]

    def c06_at(locator: str) -> str:
        matches = [
            token_id
            for token_id in apparatus_ids
            if apparatus_meta[token_id]["source_locator"] == locator
            and ":alternative:" in token_id
            and "-c06:" in token_id
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected one column-6 alternative at {ref} {locator}, got {matches}"
            )
        return matches[0]

    fixed: list[str]
    choice_groups: list[dict[str, Any]] = []
    supplemental: list[str] = []
    supplemental_witnesses: list[str] = []
    supplemental_crosswalk: list[dict[str, Any]] = []
    proven_omitted: list[str] = []
    versional_addition_targets: list[str] = []
    forbidden_versional_strong: list[str] = []
    evidence_records: list[dict[str, Any]] = []
    unresolved_reason: str | None = None
    if ref in _FINGERPRINT_COMPONENT_ONLY_REFS:
        # Most traditional-only rows are classified as alternative components,
        # but exact witness typing can already mark a row as
        # primary_fingerprint_traditional (notably Acts.8.37).  The audited
        # whole-verse selection must retain both buckets; it never chooses an
        # apparatus column-6/9 candidate here.
        fixed = [*primary_ids, *component_ids]
        rule = "selected_traditional_complete_component_layer"
    elif ref in _FINGERPRINT_PRIMARY_PLUS_COMPONENT_REFS:
        fixed = [*primary_ids, *component_ids]
        rule = "selected_primary_plus_traditional_expansion"
    elif ref == "Ps.22.16":
        locator = "Psa.22.16(22.17)#07=L(D)"
        fixed = [
            token_id
            for token_id in component_ids
            if component_meta[token_id]["source_locator"] != locator
        ]
        fixed.append(c06_at(locator))
        rule = "selected_tahot_column6_pierced_surface_alternative"
    elif ref == "Luke.23.34":
        locator = "Luk.23.34#19=NK(o)"
        fixed = [
            token_id
            for token_id in primary_ids
            if component_meta[token_id]["source_locator"] != locator
        ]
        fixed.append(c06_at(locator))
        rule = "selected_singular_lot_surface_alternative"
    elif ref == "John.1.18":
        locator = "Jhn.1.18#07=N(K)O"
        fixed = [
            token_id
            for token_id in primary_ids
            if component_meta[token_id]["source_locator"] != locator
        ]
        fixed.append(c06_at(locator))
        rule = "selected_only_begotten_son_surface_alternative"
    elif ref == "Acts.15.34":
        external = _acts_15_34_external_evidence()
        fixed = list(component_ids)
        supplemental = list(external["selected_supplemental_original_token_ids"])
        supplemental_witnesses = list(external["d05_primary_token_ids"])
        supplemental_crosswalk = list(external["d05_to_ugnt_token_crosswalk"])
        proven_omitted = list(external["proven_omitted_original_ids"])
        versional_addition_targets = list(external["versional_addition_target_ids"])
        forbidden_versional_strong = list(
            external["forbidden_strong_on_versional_addition"]
        )
        evidence_records = list(external["evidence_records"])
        rule = "selected_tagnt_silas_clause_plus_d05_long_clause_and_versional_addition"
    elif ref in _FINGERPRINT_CHOICE_LOCATORS:
        locator = _FINGERPRINT_CHOICE_LOCATORS[ref]
        choice_components = component_at(locator)
        choice_alternative = c06_at(locator)
        fixed = [
            token_id
            for token_id in [*primary_ids, *component_ids]
            if component_meta[token_id]["source_locator"] != locator
        ]
        if ref == "1Cor.14.34":
            selected_locator = "1Co.14.34#14=N(k)O"
            fixed = [
                token_id
                for token_id in fixed
                if component_meta[token_id]["source_locator"] != selected_locator
            ]
            fixed.append(c06_at(selected_locator))
        choice_groups.append(
            {
                "choice_id": f"{ref}:component-choice",
                "source_locator": locator,
                "candidate_original_token_ids": [
                    *choice_components,
                    choice_alternative,
                ],
                "status": "unresolved_blocks_automatic_assignment",
            }
        )
        unresolved_reason = (
            "exact OH1988 wording does not distinguish the source-apparatus alternatives"
        )
        rule = "component_specific_unresolved_choice"
    else:
        fixed = list(primary_ids)
        rule = "selected_primary_component_layer"

    candidate_ids = {
        token_id
        for group in choice_groups
        for token_id in group["candidate_original_token_ids"]
    }
    selected = list(dict.fromkeys(fixed))
    excluded = [
        token_id
        for token_id in [*primary_ids, *component_ids, *apparatus_ids]
        if token_id not in set(selected) | candidate_ids
    ]
    return {
        "selection_rule": rule,
        "selected_original_token_ids": selected,
        "selected_original_token_count": len(selected),
        "unresolved_choice_groups": choice_groups,
        "unresolved_choice_candidate_count": len(candidate_ids),
        "supplemental_control_candidate_ids": supplemental,
        "supplemental_witness_token_ids": supplemental_witnesses,
        "supplemental_original_crosswalk": supplemental_crosswalk,
        "proven_omitted_original_ids": proven_omitted,
        "versional_addition_target_ids": versional_addition_targets,
        "forbidden_strong_on_versional_addition": forbidden_versional_strong,
        "evidence_records": evidence_records,
        "excluded_original_candidate_ids": excluded,
        "excluded_original_candidate_count": len(excluded),
        "unresolved_reason": unresolved_reason,
    }


def _post_candidate_textual_choice_resolutions(
    stage6_by_ref: Mapping[str, Mapping[str, Any]],
    universe: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Build the five reviewed post-candidate textual-choice overlays.

    Candidate generation remains bound to the pre-resolution selected layer.
    These records exist for gold/manual accounting only and therefore cannot
    influence a candidate score or the statistical OOF corpus.
    """

    wanted_primary = {
        str(spec["primary_id"]) for spec in _POST_CANDIDATE_TEXTUAL_CHOICES.values()
    }
    wanted_alternatives = {
        str(spec[key])
        for spec in _POST_CANDIDATE_TEXTUAL_CHOICES.values()
        for key in ("alternative_id", "excluded_lexical_id")
        if spec[key] is not None
    }
    full_primary: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(Path(universe["path"])):
        token_id = str(row["original_token_id"])
        if token_id in wanted_primary:
            full_primary[token_id] = row
            if set(full_primary) == wanted_primary:
                break
    full_alternatives: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(Path(universe["alternative_path"])):
        token_id = str(row["alternative_token_id"])
        if token_id in wanted_alternatives:
            full_alternatives[token_id] = row
            if set(full_alternatives) == wanted_alternatives:
                break
    if set(full_primary) != wanted_primary or set(full_alternatives) != wanted_alternatives:
        raise RuntimeError("Reviewed textual full-record inventory is incomplete")

    resolutions: dict[str, dict[str, Any]] = {}
    for ref, spec in _POST_CANDIDATE_TEXTUAL_CHOICES.items():
        primary_id = str(spec["primary_id"])
        alternative_id = str(spec["alternative_id"])
        excluded_lexical_id = (
            str(spec["excluded_lexical_id"])
            if spec["excluded_lexical_id"] is not None
            else None
        )
        if primary_id not in universe["original_meta"]:
            raise RuntimeError(f"Missing reviewed primary textual candidate: {primary_id}")
        if alternative_id not in universe["alternative_meta"]:
            raise RuntimeError(
                f"Missing reviewed column-6 textual candidate: {alternative_id}"
            )
        if (
            excluded_lexical_id is not None
            and excluded_lexical_id not in universe["alternative_meta"]
        ):
            raise RuntimeError(
                f"Missing excluded column-12 lexical candidate: {excluded_lexical_id}"
            )
        primary = full_primary[primary_id]
        alternative = full_alternatives[alternative_id]
        lexical = (
            full_alternatives[excluded_lexical_id]
            if excluded_lexical_id is not None
            else None
        )
        expected_strongs = [list(value) for value in spec["expected_strongs"]]
        if [
            list(primary["strong_classic"]),
            list(alternative["strong_classic"]),
        ] != expected_strongs:
            raise RuntimeError(f"Reviewed textual Strong inventory drift at {ref}")
        if any(
            str(meta["target_ref"]) != ref
            or str(meta["source_locator"]) != str(spec["source_locator"])
            for meta in (primary, alternative, *([lexical] if lexical else []))
        ):
            raise RuntimeError(f"Reviewed textual source locator drift at {ref}")
        if (
            excluded_lexical_id is not None
            and "-c12:" not in excluded_lexical_id
        ) or "-c06:" not in alternative_id:
            raise RuntimeError(f"Reviewed textual apparatus-column contract drift at {ref}")

        stage6 = stage6_by_ref[ref]
        target = dict(spec["target"])
        target_tokens = exact_word_tokens(str(stage6["plain_text_nfc"]))
        target_matches = [
            token
            for token in target_tokens
            if f"uk7:{stage6['verse_key']}:{token.token_id_suffix}"
            == target["token_id"]
        ]
        if len(target_matches) != 1:
            raise RuntimeError(f"Reviewed textual target token ID drift at {ref}")
        target_token = target_matches[0]
        observed_target = {
            "token_id": target["token_id"],
            "surface": target_token.surface,
            "start_scalar": target_token.start_scalar,
            "end_scalar": target_token.end_scalar,
            "start_byte": target_token.start_byte,
            "end_byte": target_token.end_byte,
        }
        if observed_target != target:
            raise RuntimeError(f"Reviewed textual target span drift at {ref}")

        rendered_strong = list(spec["rendered_strong"])
        use_primary_component = str(spec["disposition"]) == (
            "resolved_manual_b_primary_component"
        )
        member_ids = [primary_id, alternative_id]
        if use_primary_component:
            overlay_id = primary_id
            overlay = {
                **primary,
                "original_token_id": primary_id,
                "reading_status": "primary_manual_textual_choice_b",
                "source_reading_status": primary["reading_status"],
                "accounting_status": "pending_gold_manual_span_review",
                "strong_classic": rendered_strong,
                "manual_textual_member_ids": member_ids,
                "excluded_textual_member_ids": [alternative_id],
                "excluded_lexical_candidate_ids": (
                    [excluded_lexical_id] if excluded_lexical_id else []
                ),
            }
        else:
            group_material = "\0".join(
                [CONTRACT_VERSION, ref, *member_ids, *rendered_strong]
            )
            overlay_id = "gold7:textual-choice:" + sha256_text(group_material)
            strong_normalized = (
                list(primary.get("strong_normalized", [])) if rendered_strong else []
            )
            overlay = {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "original_token_id": overlay_id,
                "parent_token_id": primary.get("parent_token_id"),
                "target_ref": ref,
                "verse_key": stage6["verse_key"],
                "order": primary["order"],
                "component_order": 1,
                "component_group": 1,
                "component_kind": "manual_textual_alternative_group",
                "surface_raw": " | ".join(
                    [str(primary["surface_raw"]), str(alternative["surface_raw"])]
                ),
                "surface_normalized": " | ".join(
                    [
                        str(
                            primary.get("surface_normalized", primary["surface_raw"])
                        ),
                        str(
                            alternative.get(
                                "surface_normalized", alternative["surface_raw"]
                            )
                        ),
                    ]
                ),
                "transliteration_raw": " | ".join(
                    filter(
                        None,
                        [
                            str(primary.get("transliteration_raw") or ""),
                            str(alternative.get("transliteration_raw") or ""),
                        ],
                    )
                ),
                "gloss_raw": " | ".join(
                    filter(
                        None,
                        [
                            str(primary.get("gloss_raw") or ""),
                            str(alternative.get("gloss_raw") or ""),
                        ],
                    )
                ),
                "lemma_raw": None,
                "lemma_source": "manual textual alternative group; exact form intentionally unselected",
                "morphology_raw": None,
                "strong_raw": rendered_strong,
                "strong_normalized": strong_normalized,
                "strong_classic": rendered_strong,
                "strong_status": (
                    "classic_textual_group_equivalent"
                    if rendered_strong
                    else "textual_group_no_render"
                ),
                "reading_status": "primary_manual_textual_choice_group",
                "source_reading_status": "manual_textual_alternative_group",
                "accounting_status": "pending_gold_manual_span_review",
                "source_family": primary["source_family"],
                "source_id": primary["source_id"],
                "source_locator": primary["source_locator"],
                "source_sha256": primary.get("source_sha256"),
                "mapping_rule_id": primary.get("mapping_rule_id"),
                "mapping_contract_version": primary.get(
                    "mapping_contract_version", MAPPING_CONTRACT
                ),
                "projection_status": primary.get("projection_status"),
                "textual_witnesses": sorted(
                    set(primary.get("textual_witnesses", []))
                    | set(alternative.get("textual_witnesses", []))
                ),
                "textual_variant_raw": {
                    "member_original_token_ids": member_ids,
                    "member_surface_raw": [
                        primary["surface_raw"],
                        alternative["surface_raw"],
                    ],
                    "member_strong_classic": expected_strongs,
                    "exact_form_selected": False,
                },
                "manual_textual_member_ids": member_ids,
                "excluded_lexical_candidate_ids": (
                    [excluded_lexical_id] if excluded_lexical_id else []
                ),
            }
        overlay["manual_textual_disposition"] = spec["disposition"]
        overlay["rendered_strong"] = rendered_strong
        overlay["reviewed_target_span"] = observed_target

        resolutions[ref] = {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "decision_id": "uk7-textual-" + ref.lower().replace(".", "-"),
            "locus": ref,
            "severity": spec["severity"],
            "status": spec["disposition"],
            "candidate_layer_status": "frozen_pre_resolution_choices_excluded",
            "candidate_original_token_ids": member_ids,
            "selected_original_token_ids": [overlay_id],
            "excluded_lexical_candidate_ids": (
                [excluded_lexical_id] if excluded_lexical_id else []
            ),
            "rendered_strong": rendered_strong,
            "target_span": observed_target,
            "rationale": spec["rationale"],
            "review": {
                "pass_1": "independent_textual_locus_audit",
                "pass_2": "primary_agent_contract_review",
                "adjudication": "accepted_fail_closed_post_candidate_disposition",
            },
            "input_sha256": {
                "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
                "stage6_verse": stage6["plain_text_sha256"],
                "source_apparatus": primary.get("source_sha256"),
            },
            "gold_overlay_original_token": overlay,
        }
    return resolutions


def _textual_fingerprint(
    stage6_by_ref: Mapping[str, Mapping[str, Any]],
    universe: Mapping[str, Any],
) -> dict[str, Any]:
    title_page = next(
        row
        for row in _read_jsonl(STAGE4_WORK / "normalized_commons_ohienko_1988_scan.jsonl")
        if row["source_locator"]["page"] == 5
    )
    manual_resolutions = _post_candidate_textual_choice_resolutions(
        stage6_by_ref, universe
    )
    unresolved_after_manual = set(_FINGERPRINT_UNRESOLVED) - set(
        manual_resolutions
    )
    loci: list[dict[str, Any]] = []
    for (
        ref,
        testament,
        category,
        primary,
        alternative,
        selection,
        status,
        severity,
    ) in _FINGERPRINT:
        row = stage6_by_ref[ref]
        pages = sorted({part["provenance"]["page_start"] for part in row["source_parts"]})
        all_original_ids = [
            token_id
            for (target_ref, _order), token_ids in sorted(
                universe["by_ref_order"].items(), key=lambda item: (item[0][0], item[0][1])
            )
            if target_ref == ref
            for token_id in token_ids
        ]
        primary_ids = [
            token_id
            for token_id in all_original_ids
            if str(universe["original_meta"][token_id]["reading_status"]).startswith(
                "primary_"
            )
            and "unresolved"
            not in str(universe["original_meta"][token_id]["reading_status"])
        ]
        alternative_component_ids = [
            token_id for token_id in all_original_ids if token_id not in primary_ids
        ]
        apparatus_alternative_ids = list(universe["alternative_by_ref"].get(ref, []))
        decision = _fingerprint_selection(
            ref,
            primary_ids,
            alternative_component_ids,
            apparatus_alternative_ids,
            universe,
        )
        target_token_ids = {
            f"uk7:{row['verse_key']}:{token.token_id_suffix}"
            for token in exact_word_tokens(str(row["plain_text_nfc"]))
        }
        if not set(decision["versional_addition_target_ids"]) <= target_token_ids:
            raise RuntimeError(
                f"Fingerprint versional-addition target ID drift at {ref}"
            )
        manual_resolution = manual_resolutions.get(ref)
        second_pass_status = (
            str(manual_resolution["status"])
            if manual_resolution is not None
            else "unresolved_blocks_automatic"
            if ref in unresolved_after_manual
            else "resolved_original_component_universe"
        )
        original_source_ids = sorted(
            {
                universe["original_meta"][token_id]["source_id"]
                for token_id in all_original_ids
            }
        )
        loci.append(
            {
                "locus": ref,
                "testament": testament,
                "category": category,
                "severity": severity,
                "primary_reading_evidence": primary,
                "alternative_reading_evidence": alternative,
                "initial_hypothesis_selection": selection,
                "initial_hypothesis_status": status,
                "selected_original_status": decision["selection_rule"],
                "status": second_pass_status,
                "oh1988_plain_text_sha256": row["plain_text_sha256"],
                "scan_pages": pages,
                "scan_sha256": "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34",
                "mapping_rule_id": row["rule_id"],
                "native_original_control_ref": _FINGERPRINT_NATIVE_CONTROL_REFS.get(
                    ref, ref
                ),
                "native_control_token_inventories": _FINGERPRINT_CONTROL_ID_INVENTORIES.get(
                    ref, {}
                ),
                "primary_original_token_count": len(primary_ids),
                "primary_original_token_ids": primary_ids,
                "alternative_component_ids": alternative_component_ids,
                "apparatus_alternative_token_ids": apparatus_alternative_ids,
                "all_original_candidate_id_inventory_sha256": sha256_text(
                    "\n".join(
                        primary_ids
                        + alternative_component_ids
                        + apparatus_alternative_ids
                    )
                    + "\n"
                ),
                **decision,
                "manual_textual_resolution": manual_resolution,
                "automation_allowed": False,
                "automation_block_reason": (
                    decision["unresolved_reason"]
                    if second_pass_status.startswith("unresolved")
                    else "the source-component disposition is resolved, but OH1988 span review and gold calibration remain separate contracts"
                ),
                "evidence": [
                    {
                        "kind": "exact_oh1988_scan",
                        "source_id": "commons_ohienko_1988_scan",
                        "source_sha256": "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34",
                        "scan_pages": pages,
                        "plain_text_sha256": row["plain_text_sha256"],
                    },
                    {
                        "kind": "source_qualified_original_apparatus",
                        "source_ids": original_source_ids,
                        "source_sha256": {
                            source_id: universe["file_hashes"][source_id]
                            for source_id in original_source_ids
                        },
                        "stable_primary_ids": primary_ids,
                        "stable_alternative_component_ids": alternative_component_ids,
                        "stable_apparatus_alternative_ids": apparatus_alternative_ids,
                    },
                    {
                        "kind": "primary_historical_method",
                        "source_ids": [
                            "ohienko_translation_methodology_1927",
                            "ilarion_biblical_studies_volume_1_1963",
                        ],
                        "role": "general textual-basis context only; never a token assignment",
                    },
                    {
                        "kind": "owner_local_read_only_diagnostic_control",
                        "source_id": "local_bible_lxx_tr_control",
                        "source_sha256": LOCAL_DB_LOCKS["bible_lxx_tr.sqlite"][
                            "sha256"
                        ],
                        "target_ref": ref,
                        "role": "LXX for OT or TR for NT; zero-vote diagnostic only",
                        "versioned_text_retained": False,
                    },
                ],
            }
        )
    global_unresolved_refs = sorted(
        {
            str(meta["target_ref"])
            for meta in universe["original_meta"].values()
            if meta["target_ref"]
            and str(meta["reading_status"]).startswith(("alternative", "unresolved"))
        },
        key=lambda ref: stage6_by_ref[ref]["order"],
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "artifact": "textual_fingerprint",
        "status": "historical_and_53_locus_diagnostic_fingerprint_complete_with_five_post_candidate_manual_dispositions",
        "edition_fingerprint": {
            "exact_scan": {
                "sha256": "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34",
                "bytes": 83637482,
                "leaves": 1538,
                "license": "CC BY-SA 4.0 (Wikimedia Commons VRT 2013112610015211)",
            },
            "title_page": 5,
            "title_page_statement": "translated anew from ancient Hebrew and Greek; jubilee edition 1988",
            "title_page_fragment_sha256": title_page["source_fragment_sha256"],
            "front_and_back_matter_audit": {
                "front_leaves": "1-10; title on leaf 5, contents on 7-8, OT divider on 9",
                "last_scripture_leaf": 1527,
                "maps": "1529-1532",
                "result": "no preface, colophon, publisher/imprint, ISBN, revision statement, or exact source-edition statement is present in this volume",
            },
            "primary_historical_documents": [
                {
                    "source_id": "ohienko_translation_methodology_1927",
                    "sha256": "a8b12dec4b44e7421ee0bd3ec12b65eec2a665965421ff8731d17358b29cbd21",
                    "page_evidence": "printed pp.8-9, 18, 22",
                    "result": "documents the 1925 translation-method intention, not the final 1962/1988 textual readings",
                    "usage": "research citation and short paraphrase only; redistribution license unresolved",
                },
                {
                    "source_id": "ilarion_biblical_studies_volume_1_1963",
                    "sha256": "e42bdb501aa544c3fb4b712d9cb547daa8e29db97adc4479dadd0e1d4f34806e",
                    "page_evidence": "printed pp.220-253, especially 230, 232, 234, 244-247 and 253",
                    "result": "documents Hebrew as the general OT base, Greek as the general NT base, occasional LXX control, the 1936-1962 workflow, and an author-reported post-approval editorial intervention",
                    "usage": "research citation and short paraphrase only; redistribution license unresolved",
                },
            ],
            "ot_result": "Hebrew is the documented general base; LXX was used occasionally and in notes, never as an automatic source substitution",
            "nt_result": "Greek is the documented general base, but no exact edition is named; exact loci show a mixed critical/traditional profile",
            "revision_result": "the 1962 ancestor is documented, but unchanged 1962-to-1988 identity is not proven; edition-level scan collation remains mandatory",
            "historical_document_status": "primary historical-document and exact-volume front/back-matter audit complete; exact Hebrew/Greek editions and the 1962-to-1988 revision relation remain unresolved",
        },
        "loci": loci,
        "post_candidate_manual_textual_resolution_count": len(manual_resolutions),
        "post_candidate_manual_textual_resolution_refs": sorted(
            manual_resolutions,
            key=lambda ref: stage6_by_ref[ref]["order"],
        ),
        "unresolved_textual_locus_count": len(unresolved_after_manual),
        "unresolved_textual_loci": sorted(
            unresolved_after_manual,
            key=lambda ref: stage6_by_ref[ref]["order"],
        ),
        "global_unresolved_source_apparatus_ref_count": len(global_unresolved_refs),
        "global_unresolved_source_apparatus_refs": global_unresolved_refs,
        "unresolved_textual_component_count": sum(
            value
            for key, value in universe["counters"].items()
            if key.startswith("reading.alternative_")
            or key.startswith("reading.unresolved_")
        ),
        "automation_allowed_locus_count": 0,
        "blockers": [
            "exact Hebrew/Greek editions and an unchanged 1962-to-1988 relation are not documented; therefore each locus is controlled independently",
            "the five previously unresolved diagnostic component choices have fail-closed post-candidate manual dispositions; three intentionally render no Strong",
            "traditional-only and other source-apparatus readings outside the 53-locus diagnostic panel remain globally fail-closed",
        ],
        "processed_count": len(loci),
        "skipped_count": 0,
        "error_count": 0,
        "unresolved_critical_count": sum(
            item["locus"] in unresolved_after_manual
            and item["severity"] == "critical"
            for item in loci
        ),
        "unresolved_high_count": sum(
            item["locus"] in unresolved_after_manual
            and item["severity"] == "high"
            for item in loci
        ),
        "automation_blocked_critical_count": sum(
            not item["automation_allowed"] and item["severity"] == "critical"
            for item in loci
        ),
        "automation_blocked_high_count": sum(
            not item["automation_allowed"] and item["severity"] == "high"
            for item in loci
        ),
        "alignment_challenge_count": sum(
            item["category"] == "alignment_counterexample" for item in loci
        ),
        "input_sha256": {
            "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
            "commons_scan": "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34",
            "wikisource_revision_bundle": "c7bc09ffdb232ded0abae6b631e382d896396750e3d3931ba5ee07e22c3e0702",
            "ohienko_methodology_1927": "a8b12dec4b44e7421ee0bd3ec12b65eec2a665965421ff8731d17358b29cbd21",
            "ilarion_biblical_studies_1963": "e42bdb501aa544c3fb4b712d9cb547daa8e29db97adc4479dadd0e1d4f34806e",
            "scrivener_codex_bezae_1864": ACTS_15_34_EVIDENCE_SOURCES[
                "scrivener_bezae_1864"
            ]["sha256"],
            "igntp_codex_bezae_greek_xml_v1_03": ACTS_15_34_EVIDENCE_SOURCES[
                "bezae_greek_xml_v1_03"
            ]["sha256"],
            "clementine_vulgate_1598_latvuc": ACTS_15_34_EVIDENCE_SOURCES[
                "clementine_vulgate_1598_usfx"
            ]["sha256"],
            "owner_local_lxx_tr_control": LOCAL_DB_LOCKS[
                "bible_lxx_tr.sqlite"
            ]["sha256"],
        },
        "output_sha256": {},
        "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
    }


def _build_fingerprint_selected_original_layer(
    *,
    stage6_by_ref: Mapping[str, Mapping[str, Any]],
    universe: Mapping[str, Any],
    controls: Mapping[str, Any],
    fingerprint: Mapping[str, Any],
    work: Path,
) -> dict[str, Any]:
    """Serialize the exact original layer permitted for alignment candidates.

    The raw STEP universe deliberately preserves primary, alternative and
    unresolved readings without silently choosing among them.  Candidate
    generators need a different view: resolved raw primary components outside
    the audited loci, the explicit component selections inside the fingerprint,
    and the four source-qualified UGNT controls selected for Acts.15.34.  The
    five local choice groups and every unselected apparatus candidate remain
    absent and therefore cannot acquire an automatic Strong link.
    """

    output_path = work / "fingerprint_selected_original_layer.jsonl"
    fingerprint_refs = {str(row["locus"]) for row in fingerprint["loci"]}
    selected_main_to_ref: dict[str, str] = {}
    supplemental_to_ref: dict[str, str] = {}
    selection_rule_by_ref: dict[str, str] = {}
    choice_ids: set[str] = set()
    for locus in fingerprint["loci"]:
        ref = str(locus["locus"])
        selection_rule_by_ref[ref] = str(locus["selection_rule"])
        for token_id in locus["selected_original_token_ids"]:
            token_id = str(token_id)
            if token_id in selected_main_to_ref:
                raise RuntimeError(
                    f"Fingerprint original ID selected by multiple loci: {token_id}"
                )
            selected_main_to_ref[token_id] = ref
        for token_id in locus["supplemental_control_candidate_ids"]:
            token_id = str(token_id)
            if token_id in supplemental_to_ref:
                raise RuntimeError(
                    f"Fingerprint control ID selected by multiple loci: {token_id}"
                )
            supplemental_to_ref[token_id] = ref
        for group in locus["unresolved_choice_groups"]:
            choice_ids.update(str(value) for value in group["candidate_original_token_ids"])
    if choice_ids & (set(selected_main_to_ref) | set(supplemental_to_ref)):
        raise RuntimeError("Unresolved fingerprint choice entered the selected layer")

    counters: Counter[str] = Counter()
    emitted_ids: set[str] = set()
    emitted_refs: set[str] = set()

    def selected_record(
        row: Mapping[str, Any],
        *,
        token_id: str,
        ref: str,
        selection_kind: str,
    ) -> dict[str, Any]:
        if token_id in emitted_ids:
            raise RuntimeError(f"Duplicate selected original ID: {token_id}")
        if ref not in stage6_by_ref:
            raise RuntimeError(f"Selected original is outside stage-6 grid: {token_id}")
        emitted_ids.add(token_id)
        emitted_refs.add(ref)
        source_reading_status = str(row.get("reading_status") or "")
        result = dict(row)
        result.update(
            {
                "original_token_id": token_id,
                "target_ref": ref,
                "verse_key": stage6_by_ref[ref]["verse_key"],
                "mapping_rule_id": stage6_by_ref[ref]["rule_id"],
                "mapping_contract_version": stage6_by_ref[ref][
                    "mapping_contract_version"
                ],
                "source_reading_status": source_reading_status,
                "reading_status": (
                    "primary_fingerprint_selected_controlled"
                    if ref in fingerprint_refs
                    else source_reading_status
                ),
                "selection_kind": selection_kind,
                "selection_rule": selection_rule_by_ref.get(
                    ref, "resolved_primary_original_layer"
                ),
                "accounting_status": "pending_alignment",
            }
        )
        return result

    def records() -> Iterator[dict[str, Any]]:
        for row in _read_jsonl(universe["path"]):
            token_id = str(row["original_token_id"])
            ref_value = row.get("target_ref")
            if ref_value is None:
                counters["skipped_source_only"] += 1
                continue
            ref = str(ref_value)
            status = str(row["reading_status"])
            if ref in fingerprint_refs:
                if selected_main_to_ref.get(token_id) != ref:
                    counters["skipped_fingerprint_unselected_raw"] += 1
                    continue
                kind = "fingerprint_selected_raw_component"
            else:
                if not status.startswith("primary_") or "unresolved" in status:
                    counters["skipped_unresolved_or_alternative_raw"] += 1
                    continue
                kind = "resolved_primary_raw_component"
            counters[kind] += 1
            yield selected_record(
                row,
                token_id=token_id,
                ref=ref,
                selection_kind=kind,
            )

        for row in _read_jsonl(universe["alternative_path"]):
            token_id = str(row["alternative_token_id"])
            ref = selected_main_to_ref.get(token_id)
            if ref is None:
                counters["skipped_unselected_apparatus_candidate"] += 1
                continue
            normalized = dict(row)
            normalized["component_kind"] = (
                "fingerprint_selected_" + str(row["alternative_kind"])
            )
            counters["fingerprint_selected_apparatus_candidate"] += 1
            yield selected_record(
                normalized,
                token_id=token_id,
                ref=ref,
                selection_kind="fingerprint_selected_apparatus_candidate",
            )

        for row in _read_jsonl(controls["token_path"]):
            token_id = str(row["control_token_id"])
            ref = supplemental_to_ref.get(token_id)
            if ref is None:
                continue
            normalized = dict(row)
            normalized.update(
                {
                    "source_family": str(row["source_id"]),
                    "source_locator": str(row.get("native_id") or token_id),
                    "order": int(row["source_order"]),
                    "transliteration_raw": str(
                        row.get("transliteration_raw") or ""
                    ),
                    "component_kind": "fingerprint_selected_original_control",
                }
            )
            counters["fingerprint_selected_original_control"] += 1
            yield selected_record(
                normalized,
                token_id=token_id,
                ref=ref,
                selection_kind="fingerprint_selected_original_control",
            )

    count, digest = _write_jsonl(output_path, records())
    expected_selected = set(selected_main_to_ref) | set(supplemental_to_ref)
    missing_selected = sorted(expected_selected - emitted_ids)
    if missing_selected:
        raise RuntimeError(
            "Fingerprint-selected original IDs are missing from serialized layers: "
            + ", ".join(missing_selected[:10])
        )
    if emitted_ids & choice_ids:
        raise RuntimeError("Unresolved fingerprint choice was serialized")
    missing_refs = sorted(
        set(stage6_by_ref) - emitted_refs,
        key=lambda ref: int(stage6_by_ref[ref]["order"]),
    )
    if missing_refs:
        raise RuntimeError(
            "Selected original layer misses stage-6 target refs: "
            + ", ".join(missing_refs[:10])
        )
    return {
        "path": output_path,
        "count": count,
        "sha256": digest,
        "ref_count": len(emitted_refs),
        "choice_candidate_count": len(choice_ids),
        "selected_fingerprint_main_count": len(selected_main_to_ref),
        "selected_supplemental_control_count": len(supplemental_to_ref),
        "counters": counters,
    }


_NEGATIVE_COUNTEREXAMPLES = (
    ("Isa.53.5", "H2490", "f09c1950ee19c4c4f8b175f5", 0, 1, "verb/participle was attached to a conjunction"),
    ("Isa.53.5", "H2250", "3f66fbeaa4ebc3f0d880063a", 121, 133, "wound/stripe noun was attached to a healing verb"),
    ("Isa.53.5", "H7495", "db22f25fe94afec1c1de51dd", 109, 116, "healing verb was attached to a wounds noun"),
    ("Mic.6.8", "H120", "98e3cd6418b2b7de5b1af124", 59, 62, "human noun was attached to a preposition"),
    ("Mic.6.8", "H6213", "040cfd8cf567e0bed5a5c81f", 119, 120, "do infinitive was attached to a conjunction"),
    ("Mic.6.8", "H430", "903cacc1b301fa8e5b65ba75", 140, 141, "God noun was attached to a conjunction"),
    ("Luke.2.11", "G5088", "df2b7a75e24c7f23fbea6c5a", 14, 23, "birth verb was attached to a Davidic adjective"),
    ("Luke.2.11", "G4771", "49df7ad07212655226775e35", 30, 39, "second-person pronoun was attached to a birth verb"),
    ("Luke.2.11", "G3739", "b9dbd37143162cb8c0456bec", 44, 47, "relative pronoun was attached to a second-person pronoun despite legacy high confidence"),
    ("Acts.2.38", "G846", "5018e0c548cd14b4a9b0734d", 15, 19, "pronoun was attached to a speech verb"),
    ("Acts.2.38", "G5346", "200b55f4e66f9f6a3d384e85", 11, 14, "speech verb was attached to a pronoun"),
    ("Acts.2.38", "G1519", "a7735a3056eb65242900a9d3", 65, 68, "preposition was attached to a pronoun"),
)


def _book_genre(book: str) -> str:
    if book in {"Gen", "Exod", "Lev", "Num", "Deut"}:
        return "torah_prose_law"
    if book in {"Josh", "Judg", "Ruth", "1Sam", "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth"}:
        return "historical_prose"
    if book in {"Job", "Ps", "Prov", "Eccl", "Song"}:
        return "poetry_wisdom"
    if book in {"Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal"}:
        return "prophetic"
    if book in {"Mat", "Mark", "Luke", "John"}:
        return "gospel_narrative"
    if book == "Acts":
        return "acts_narrative"
    if book == "Rev":
        return "apocalyptic"
    return "epistle"


def _gold_preparation(
    rows: Sequence[Mapping[str, Any]],
    universe: Mapping[str, Any],
    fingerprint: Mapping[str, Any],
    control_token_path: Path,
    selected_original_layer_path: Path,
    work: Path,
    report: Path,
    *,
    write_placeholder_annotations: bool = True,
) -> dict[str, Any]:
    by_book: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_ref = {str(row["target_ref"]): row for row in rows}
    comments_by_ref = {str(row["target_ref"]): row for row in _read_jsonl(STAGE6_COMMENTS)}
    original_by_ref: dict[str, list[str]] = defaultdict(list)
    for (target_ref, _order), token_ids in universe["by_ref_order"].items():
        original_by_ref[target_ref].extend(token_ids)
    for row in rows:
        by_book[str(row["target_ref"]).split(".", 1)[0]].append(row)
    fingerprint_by_ref = {
        str(row["locus"]): row for row in fingerprint["loci"]
    }
    manual_overlay_by_ref: dict[str, dict[str, Any]] = {}
    manual_overlay_by_id: dict[str, dict[str, Any]] = {}
    for locus in fingerprint["loci"]:
        resolution = locus.get("manual_textual_resolution")
        if not resolution:
            continue
        overlay = dict(resolution["gold_overlay_original_token"])
        overlay_id = str(overlay["original_token_id"])
        ref = str(locus["locus"])
        if ref in manual_overlay_by_ref or overlay_id in manual_overlay_by_id:
            raise RuntimeError("Duplicate post-candidate textual gold overlay")
        manual_overlay_by_ref[ref] = overlay
        manual_overlay_by_id[overlay_id] = overlay
    supplemental_ids = {
        str(token_id)
        for row in fingerprint["loci"]
        for token_id in row["supplemental_control_candidate_ids"]
    }
    supplemental_meta = {
        str(row["control_token_id"]): row
        for row in _read_jsonl(control_token_path)
        if str(row["control_token_id"]) in supplemental_ids
    }
    if set(supplemental_meta) != supplemental_ids:
        raise RuntimeError("Fingerprint-selected supplemental original controls are missing")

    def selected_meta(token_id: str) -> Mapping[str, Any]:
        if token_id in manual_overlay_by_id:
            meta = manual_overlay_by_id[token_id]
            return {
                "source_id": meta["source_id"],
                "order": meta["order"],
                "surface": meta.get("surface_normalized", ""),
                "classic": set(meta.get("strong_classic", [])),
                "reading_status": meta["reading_status"],
            }
        if token_id in supplemental_meta:
            meta = supplemental_meta[token_id]
            return {
                "source_id": meta["source_id"],
                "order": meta["source_order"],
                "surface": meta["surface_normalized"],
                "classic": set(meta["strong_classic"]),
                "reading_status": meta["reading_status"],
            }
        if token_id in universe["original_meta"]:
            return universe["original_meta"][token_id]
        if token_id in universe["alternative_meta"]:
            return universe["alternative_meta"][token_id]
        raise RuntimeError(f"Gold-selected original token is unknown: {token_id}")

    def ordered_original_ids(token_ids: Iterable[str]) -> list[str]:
        return sorted(
            dict.fromkeys(token_ids),
            key=lambda token_id: (int(selected_meta(token_id)["order"]), token_id),
        )

    selected_original_by_ref: dict[str, list[str]] = {}
    selection_rule_by_ref: dict[str, str] = {}
    for ref in by_ref:
        if ref in fingerprint_by_ref:
            locus = fingerprint_by_ref[ref]
            selected_original_by_ref[ref] = ordered_original_ids(
                [
                    *locus["selected_original_token_ids"],
                    *locus["supplemental_control_candidate_ids"],
                ]
            )
            selection_rule_by_ref[ref] = str(locus["selection_rule"])
        else:
            selected_original_by_ref[ref] = ordered_original_ids(
                token_id
                for token_id in original_by_ref[ref]
                if str(universe["original_meta"][token_id]["reading_status"]).startswith(
                    "primary_"
                )
                and "unresolved"
                not in str(universe["original_meta"][token_id]["reading_status"])
            )
            selection_rule_by_ref[ref] = "resolved_primary_original_layer"
    serialized_selected_by_ref: dict[str, list[str]] = defaultdict(list)
    for selected_row in _read_jsonl(selected_original_layer_path):
        selected_id = str(selected_row["original_token_id"])
        serialized_selected_by_ref[str(selected_row["target_ref"])].append(selected_id)
    selected_layer_mismatches = [
        ref
        for ref in by_ref
        if ordered_original_ids(serialized_selected_by_ref.get(ref, []))
        != selected_original_by_ref[ref]
    ]
    if selected_layer_mismatches:
        raise RuntimeError(
            "Gold/fingerprint-selected original layer mismatch: "
            + ", ".join(selected_layer_mismatches[:10])
        )
    gold_selected_original_by_ref = {
        ref: list(token_ids) for ref, token_ids in selected_original_by_ref.items()
    }
    for ref, overlay in manual_overlay_by_ref.items():
        gold_selected_original_by_ref[ref] = ordered_original_ids(
            [
                *gold_selected_original_by_ref[ref],
                str(overlay["original_token_id"]),
            ]
        )
        selection_rule_by_ref[ref] += "+post_candidate_manual_textual_overlay"

    gold_selected_layer_path = work / "gold_selected_original_layer.jsonl"

    def gold_selected_layer_rows() -> Iterator[dict[str, Any]]:
        seen: set[str] = set()
        for row in _read_jsonl(selected_original_layer_path):
            token_id = str(row["original_token_id"])
            if token_id in seen:
                raise RuntimeError(
                    f"Candidate selected layer repeats an original ID: {token_id}"
                )
            seen.add(token_id)
            yield row
        for ref in sorted(
            manual_overlay_by_ref,
            key=lambda item: int(by_ref[item]["order"]),
        ):
            overlay = manual_overlay_by_ref[ref]
            token_id = str(overlay["original_token_id"])
            if token_id in seen:
                raise RuntimeError(
                    f"Post-candidate textual overlay repeats an original ID: {token_id}"
                )
            seen.add(token_id)
            yield overlay

    gold_selected_layer_count, gold_selected_layer_sha = _write_jsonl(
        gold_selected_layer_path, gold_selected_layer_rows()
    )
    candidate_selected_layer_count = sum(
        len(token_ids) for token_ids in serialized_selected_by_ref.values()
    )
    if gold_selected_layer_count != (
        candidate_selected_layer_count + len(manual_overlay_by_id)
    ):
        raise RuntimeError("Gold-selected original layer accounting drifted")
    fingerprint_refs = {item[0] for item in _FINGERPRINT}
    mapping_anomaly_refs = {
        str(row["target_ref"])
        for row in rows
        if str(row["operation"]) in {"merge", "split"}
    }
    mandatory = fingerprint_refs | mapping_anomaly_refs
    selected: set[str] = set()
    for book in BOOKS:
        candidates = sorted(
            by_book[book],
            key=lambda row: (sha256_text("gold-panel-v1:" + str(row["target_ref"])), row["target_ref"]),
        )
        selected.update(str(row["target_ref"]) for row in candidates[: min(32, len(candidates))])
    # Keep the pre-candidate 32/book quota and add every immutable mapping
    # anomaly plus each declared textual-fingerprint locus.  The additions are
    # not replaced by easier verses: all merge/split cases must remain visible.
    selected.update(mandatory)
    strong_frequencies: Counter[str] = Counter()
    for meta in universe["original_meta"].values():
        reading_status = str(meta["reading_status"])
        if reading_status.startswith("primary_") and "unresolved" not in reading_status:
            strong_frequencies.update(meta["classic"])
    panel_rows: list[dict[str, Any]] = []
    projected_decisions = 0
    stratum_counts: Counter[str] = Counter()
    for ref in sorted(selected, key=lambda item: (BOOK_NUMBER[item.split(".", 1)[0]], by_ref[item]["order"])):
        original_ids = gold_selected_original_by_ref[ref]
        projected_decisions += len(original_ids)
        row = by_ref[ref]
        book = ref.split(".", 1)[0]
        verse_strongs = {
            strong
            for token_id in original_ids
            for strong in selected_meta(token_id)["classic"]
        }
        frequency_bands = sorted(
            {
                "rare_1_to_5" if strong_frequencies[strong] <= 5 else
                "frequent_1000_plus" if strong_frequencies[strong] >= 1_000 else
                "mid_frequency"
                for strong in verse_strongs
            }
        )
        strata = {
            "testament": "OT" if BOOK_NUMBER[book] <= 39 else "NT",
            "genre": _book_genre(book),
            "mapping_operation": str(row["operation"]),
            "textual_fingerprint_locus": ref in fingerprint_refs,
            "original_frequency_bands": frequency_bands,
            "original_selection_rule": selection_rule_by_ref[ref],
        }
        stratum_counts[f"testament:{strata['testament']}"] += 1
        stratum_counts[f"genre:{strata['genre']}"] += 1
        stratum_counts[f"mapping:{strata['mapping_operation']}"] += 1
        if strata["textual_fingerprint_locus"]:
            stratum_counts["textual_fingerprint_locus"] += 1
        for band in frequency_bands:
            stratum_counts[f"original_frequency:{band}"] += 1
        fold_id = int(sha256_text(ref)[:8], 16) % 5
        fold_role = (
            "calibration"
            if fold_id <= 2
            else "validation"
            if fold_id == 3
            else "sealed_evaluation"
        )
        panel_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "selection_id": f"gold7:{row['verse_key']}",
                "target_ref": ref,
                "verse_key": row["verse_key"],
                "book": book,
                "testament": strata["testament"],
                "plain_text_sha256": row["plain_text_sha256"],
                "comment_sha256": comments_by_ref[ref]["comment_sha256"],
                "original_token_ids": ordered_original_ids(original_ids),
                "projected_decision_count": len(original_ids),
                "fold_id": fold_id,
                "fold_role": fold_role,
                "strata": strata,
                "annotation_status": "unannotated_requires_independent_passes",
                "stratification_status": "immutable_book_testament_genre_mapping_frequency_and_fingerprint_strata_selected_semantic_link_strata_pending",
            }
        )
    panel_path = work / "gold_selection_panel.jsonl"
    panel_count, panel_sha = _write_jsonl(panel_path, panel_rows)
    panel_refs = {str(panel["target_ref"]) for panel in panel_rows}
    expected_panel_original_ids = {
        str(token_id)
        for panel in panel_rows
        for token_id in panel["original_token_ids"]
    }
    selected_layer_by_id: dict[str, dict[str, Any]] = {}
    for selected_row in _read_jsonl(selected_original_layer_path):
        if str(selected_row["target_ref"]) not in panel_refs:
            continue
        selected_id = str(selected_row["original_token_id"])
        if selected_id in selected_layer_by_id:
            raise RuntimeError(
                f"Gold-selected original layer repeats an ID: {selected_id}"
            )
        selected_layer_by_id[selected_id] = selected_row
    for overlay_id, overlay in manual_overlay_by_id.items():
        if str(overlay["target_ref"]) not in panel_refs:
            continue
        if overlay_id in selected_layer_by_id:
            raise RuntimeError(
                f"Gold textual overlay repeats a selected-layer ID: {overlay_id}"
            )
        selected_layer_by_id[overlay_id] = overlay
    if set(selected_layer_by_id) != expected_panel_original_ids:
        raise RuntimeError(
            "Gold workbench original context differs from its selected stable-ID panel"
        )
    workbench_path = work / "gold_annotation_workbench.jsonl"
    workbench_rows = []
    for panel in panel_rows:
        ref = panel["target_ref"]
        row = by_ref[ref]
        target_tokens = exact_word_tokens(str(row["plain_text_nfc"]))
        validate_exact_partition(str(row["plain_text_nfc"]), target_tokens)
        workbench_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "selection_id": panel["selection_id"],
                "target_ref": ref,
                "fold_id": panel["fold_id"],
                "fold_role": panel["fold_role"],
                "plain_text_nfc": row["plain_text_nfc"],
                "target_comment": comments_by_ref[ref]["target_comment"],
                "target_tokens": [
                    {
                        "token_id": f"uk7:{row['verse_key']}:{token.token_id_suffix}",
                        "order": token.order,
                        "surface": token.surface,
                        "comparison": token.comparison,
                        "start_scalar": token.start_scalar,
                        "end_scalar": token.end_scalar,
                        "start_byte": token.start_byte,
                        "end_byte": token.end_byte,
                    }
                    for token in target_tokens
                ],
                "original_tokens": [
                    {
                        "original_token_id": token_id,
                        "order": selected_layer_by_id[token_id]["order"],
                        "component_order": selected_layer_by_id[token_id].get(
                            "component_order"
                        ),
                        "component_group": selected_layer_by_id[token_id].get(
                            "component_group"
                        ),
                        "component_kind": selected_layer_by_id[token_id].get(
                            "component_kind"
                        ),
                        "surface_raw": selected_layer_by_id[token_id].get(
                            "surface_raw", ""
                        ),
                        "surface_normalized": selected_layer_by_id[token_id].get(
                            "surface_normalized", ""
                        ),
                        "transliteration_raw": selected_layer_by_id[token_id].get(
                            "transliteration_raw"
                        ),
                        "gloss_raw": selected_layer_by_id[token_id].get("gloss_raw"),
                        "lemma_raw": selected_layer_by_id[token_id].get("lemma_raw"),
                        "lemma_source": selected_layer_by_id[token_id].get(
                            "lemma_source"
                        ),
                        "morphology_raw": selected_layer_by_id[token_id].get(
                            "morphology_raw"
                        ),
                        "strong_raw": selected_layer_by_id[token_id].get(
                            "strong_raw", []
                        ),
                        "strong_normalized": selected_layer_by_id[token_id].get(
                            "strong_normalized", []
                        ),
                        "strong_classic": selected_layer_by_id[token_id].get(
                            "strong_classic", []
                        ),
                        "strong_status": selected_layer_by_id[token_id].get(
                            "strong_status"
                        ),
                        "reading_status": (
                            selected_layer_by_id[token_id]["reading_status"]
                            if str(
                                selected_layer_by_id[token_id]["reading_status"]
                            ).startswith("primary_")
                            and "unresolved"
                            not in str(
                                selected_layer_by_id[token_id]["reading_status"]
                            )
                            else "primary_fingerprint_selected_controlled"
                        ),
                        "source_reading_status": selected_layer_by_id[token_id].get(
                            "source_reading_status",
                            selected_layer_by_id[token_id]["reading_status"],
                        ),
                        "textual_witnesses": selected_layer_by_id[token_id].get(
                            "textual_witnesses", []
                        ),
                        "textual_variant_raw": selected_layer_by_id[token_id].get(
                            "textual_variant_raw"
                        ),
                        "source_family": selected_layer_by_id[token_id].get(
                            "source_family"
                        ),
                        "source_id": selected_layer_by_id[token_id]["source_id"],
                        "source_locator": selected_layer_by_id[token_id].get(
                            "source_locator"
                        ),
                        "mapping_rule_id": selected_layer_by_id[token_id].get(
                            "mapping_rule_id"
                        ),
                        "projection_status": selected_layer_by_id[token_id].get(
                            "projection_status"
                        ),
                        "gold_selection_provenance": selection_rule_by_ref[ref],
                    }
                    for token_id in gold_selected_original_by_ref[ref]
                ],
                "annotation_template": {"links_or_null": [], "review_pass_1": None, "review_pass_2": None, "adjudication": None},
                "strata": panel["strata"],
            }
        )
    workbench_count, workbench_sha = _write_jsonl(workbench_path, workbench_rows)

    annotations: list[dict[str, Any]] = []
    for order, (ref, strong, legacy_source_id, start, end, reason) in enumerate(_NEGATIVE_COUNTEREXAMPLES, 1):
        row = by_ref[ref]
        tokens = exact_word_tokens(str(row["plain_text_nfc"]))
        token = next((item for item in tokens if item.start_scalar == start and item.end_scalar == end), None)
        if token is None:
            raise RuntimeError(f"Counterexample span no longer matches stage 6: {ref} {start}:{end}")
        annotations.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "record_type": "negative_edge",
                "annotation_id": f"gold7-negative-{order:03d}",
                "selection_panel": "legacy-counterexamples-v1",
                "fold_id": int(sha256_text(ref)[:8], 16) % 5,
                "strata": ["legacy_error", "known_counterexample", "OT" if BOOK_NUMBER[ref.split('.', 1)[0]] <= 39 else "NT"],
                "target": {
                    "target_ref": ref,
                    "verse_key": row["verse_key"],
                    "stage6_plain_sha256": row["plain_text_sha256"],
                    "tokenization_contract_version": TOKENIZER_VERSION,
                    "token_ids": [f"uk7:{row['verse_key']}:{token.token_id_suffix}"],
                    "scalar_intervals": [{"start": start, "end": end}],
                    "byte_intervals": [{"start": token.start_byte, "end": token.end_byte}],
                    "surface_sha256": [sha256_text(token.surface)],
                },
                "original": {
                    "universe_token_ids": [],
                    "legacy_source_token_id": legacy_source_id,
                    "strong_raw": [strong],
                    "strong_classic": [strong],
                    "witness": "rejected_legacy_primary_control",
                    "reading_status": "not_adjudicated_by_this_negative_edge",
                },
                "label": {"decision": "reject_link", "relation": "1:1"},
                "evidence": [{"kind": "semantic_type_mismatch", "rationale": reason}],
                "severity": "high",
                "review": {"required_passes": 2, "pass_1": "gold_audit_agent", "pass_2": None, "agreement": None, "adjudication": None},
                "input_sha256": {"stage6_text": EXPECTED_STAGE6_TEXT_SHA256, "verse": row["plain_text_sha256"], "legacy_snapshot": EXPECTED_LEGACY_SNAPSHOT_SHA256},
                "status": "review_pass_2_required",
                "supersedes": None,
            }
        )
    annotations_path = report / "gold_alignment.annotations.jsonl"
    if write_placeholder_annotations:
        annotation_count, annotation_sha = _write_jsonl(annotations_path, annotations)
    else:
        if not annotations_path.is_file():
            raise RuntimeError("Finalized gold lock exists but annotations are missing")
        annotation_count = sum(1 for _ in _read_jsonl(annotations_path))
        annotation_sha = _sha256_file(annotations_path)
    return {
        "panel_path": panel_path,
        "panel_count": panel_count,
        "panel_sha256": panel_sha,
        "workbench_path": workbench_path,
        "workbench_count": workbench_count,
        "workbench_sha256": workbench_sha,
        "gold_selected_original_layer_path": gold_selected_layer_path,
        "gold_selected_original_layer_count": gold_selected_layer_count,
        "gold_selected_original_layer_sha256": gold_selected_layer_sha,
        "post_candidate_manual_overlay_count": len(manual_overlay_by_id),
        "projected_decisions": projected_decisions,
        "mapping_anomaly_ref_count": len(mapping_anomaly_refs),
        "fingerprint_ref_count": len(fingerprint_refs),
        "stratum_counts": dict(sorted(stratum_counts.items())),
        "annotations_path": annotations_path,
        "annotation_count": annotation_count,
        "annotation_sha256": annotation_sha,
        "legacy_negative_annotations": annotations,
        "legacy_negative_annotation_count": len(annotations),
    }


def _lexeme_inventory(token_inventory: Mapping[str, Any], work: Path) -> dict[str, Any]:
    aggregated: dict[str, dict[str, Any]] = {}
    nonlexical_skipped = 0
    for row in _read_jsonl(token_inventory["path"]):
        key = row["comparison"]
        if not key or row.get("token_kind") == "nonlexical_orthographic_mark":
            nonlexical_skipped += 1
            continue
        item = aggregated.setdefault(
            key,
            {
                "surface_forms": Counter(),
                "books": Counter(),
                "testaments": Counter(),
                "genres": Counter(),
                "folds": Counter(),
                "left_context": Counter(),
                "right_context": Counter(),
                "morphology_candidates": Counter(),
                "examples": [],
                "count": 0,
            },
        )
        item["surface_forms"][row["surface"]] += 1
        item["books"][row["book"]] += 1
        item["testaments"][row["testament"]] += 1
        item["genres"][row["genre"]] += 1
        item["folds"][str(row["fold_id"])] += 1
        if row["left_context"]:
            item["left_context"][row["left_context"][-1]] += 1
        if row["right_context"]:
            item["right_context"][row["right_context"][0]] += 1
        for candidate in row["lemma_pos_morphology_candidates"]:
            item["morphology_candidates"][stable_json(candidate)] += 1
        item["count"] += 1
        if len(item["examples"]) < 3:
            item["examples"].append(
                {
                    "token_id": row["token_id"],
                    "target_ref": row["target_ref"],
                    "genre": row["genre"],
                    "context_sha256": row["context_sha256"],
                    "surface_sha256": sha256_text(row["surface"]),
                }
            )
    rows: list[dict[str, Any]] = []
    for key in sorted(aggregated):
        item = aggregated[key]
        folds = dict(sorted(item["folds"].items()))
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "lexeme_id": f"uklex7:{sha256_text(key)[:20]}",
                "normalized_form": key,
                "surface_forms": dict(sorted(item["surface_forms"].items(), key=lambda pair: (-pair[1], pair[0]))),
                "occurrence_count": item["count"],
                "books": dict(sorted(item["books"].items(), key=lambda pair: BOOK_NUMBER[pair[0]])),
                "testaments": dict(sorted(item["testaments"].items())),
                "genres": dict(sorted(item["genres"].items())),
                "fold_occurrences": folds,
                "out_of_fold_training_occurrences": {fold: item["count"] - count for fold, count in folds.items()},
                "lemma_pos_morphology_candidates": [
                    {
                        **json.loads(candidate),
                        "occurrence_count": count,
                    }
                    for candidate, count in sorted(
                        item["morphology_candidates"].items(),
                        key=lambda pair: (-pair[1], pair[0]),
                    )
                ],
                "left_context_distribution": dict(
                    item["left_context"].most_common(20)
                ),
                "right_context_distribution": dict(
                    item["right_context"].most_common(20)
                ),
                "candidate_strong_evidence": {
                    "direct_original": {},
                    "RUSSYN": {},
                    "YLT": {},
                    "contextual_gloss": {},
                    "manual": {},
                },
                "strong_distribution": {},
                "entropy": None,
                "polysemy_status": "unavailable_until_gold_acceptance",
                "accepted_examples": [],
                "rejected_examples": [],
                "unresolved_examples": item["examples"],
                "compound_relations": [],
                "negative_evidence": ["legacy global-corpus distribution excluded because it leaks the evaluated verse"],
                "status": "occurrence_and_morphology_candidate_inventory_complete_strong_distribution_blocked_before_gold",
            }
        )
    path = work / "ukrainian_lexeme_strong_ledger.jsonl"
    count, digest = _write_jsonl(path, rows)
    return {
        "path": path,
        "count": count,
        "sha256": digest,
        "nonlexical_skipped": nonlexical_skipped,
    }


def _plain_preservation(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    comments = list(_read_jsonl(STAGE6_COMMENTS))
    text_keys = [(row["order"], row["verse_key"], row["target_ref"], row["plain_text_sha256"]) for row in rows]
    comment_keys = [(row["order"], row["verse_key"], row["target_ref"], row["comment_sha256"]) for row in comments]
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "artifact": "plain_text_preservation",
        "status": "pass_upstream_frozen_no_markup_emitted",
        "stage6_text_sha256": _sha256_file(STAGE6_TEXT),
        "stage6_manifest_sha256": _sha256_file(STAGE6_MANIFEST),
        "stage6_comment_sha256": _sha256_file(STAGE6_COMMENTS),
        "expected_stage6_text_sha256": EXPECTED_STAGE6_TEXT_SHA256,
        "expected_stage6_manifest_sha256": EXPECTED_STAGE6_MANIFEST_SHA256,
        "expected_stage6_comment_sha256": EXPECTED_STAGE6_COMMENT_SHA256,
        "text_key_count": len(text_keys),
        "comment_key_count": len(comment_keys),
        "exact_key_equality": len(text_keys) == len(comment_keys) == EXPECTED_TARGET_COUNT and [item[:3] for item in text_keys] == [item[:3] for item in comment_keys],
        "plain_text_mismatch_count": 0,
        "comment_mismatch_count": 0,
        "markup_round_trip_count": 0,
        "markup_round_trip_status": "not_applicable_until_links_accepted",
        "processed_count": EXPECTED_TARGET_COUNT,
        "skipped_count": 0,
        "error_count": 0,
        "input_sha256": {"stage6_text": EXPECTED_STAGE6_TEXT_SHA256, "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256},
        "output_sha256": {},
        "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
    }


def _seal_payload(value: dict[str, Any]) -> dict[str, Any]:
    existing = dict(value.get("output_sha256", {}))
    existing["canonical_payload_before_output_digest"] = sha256_text(stable_json(value))
    value["output_sha256"] = dict(sorted(existing.items()))
    return value


def _write_source_diff(path: Path, rows: Sequence[Mapping[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "schema_version", "contract_version", "artifact", "diff_id", "scope", "baseline", "stage7", "status", "severity", "evidence"
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "artifact": "source_diff", **row})
    return _sha256_file(path)


def _report_ru(summary: Mapping[str, Any]) -> str:
    bridge_counts = summary["bridge_counts"]
    return f"""# Этап 7: evidence-first Strong alignment OH1988

Doc-Version: `1.0.0`
Last-Updated: `2026-08-15`
Source-Commit: `working-tree`
Schema-Version: `{SCHEMA_VERSION}`
Contract-Version: `{CONTRACT_VERSION}`
Input-SHA-256: `{EXPECTED_STAGE6_TEXT_SHA256}`
Processed/Skipped/Errors: `{summary['target_count']} / {summary['original_token_count']} / 0`

## Статус

Этап **не закрыт**. Доказаны immutable input freeze, точная украинская
токенизация, raw primary/alternative component reparse, native-token control
layer, source/license registry и аудит первичных исторических документов.
Исторический и 53-locus textual fingerprint завершён; пять прежних локальных
choices получили двухпроходные post-candidate manual dispositions, причём три
неразличимых места намеренно не выводят Strong. Target-side bridge proof и gold
остаются частичными и fail-closed. Нормативный gold-набор содержит
`0 / 25 000` принятых assignment/null решений и ни одно решение не прошло два
независимых слепых прохода. Поэтому candidate tuning, A/B/C calibration и
production Strong markup намеренно не выполнялись.

## Зафиксированные результаты

- exact stage-6 texts/comments: {summary['target_count']:,} позиций;
- украинские surface tokens: {summary['ukrainian_token_count']:,};
- raw original components (включая 14 primary-null) после повторного чтения TAHOT/TAGNT: {summary['original_token_count']:,};
- отдельно адресуемые TAHOT/TAGNT apparatus alternatives: {summary['alternative_candidate_count']:,};
- raw OSHB/UXLC/UGNT control tokens: {summary['original_control_token_count']:,};
- exact unique control→TAHOT/TAGNT crosswalks: {summary['original_control_resolved_count']:,}; unresolved/service: {summary['original_control_unresolved_count']:,};
- покрытие original refs application grid: {summary['original_ref_count']:,} / 31 102;
- RUSSYN/YLT manual bridge records audited: {summary['bridge_record_count']:,};
- украинские comparison lexemes: {summary['lexeme_count']:,};
- авторские сноски exact OH1988: {summary['author_comment_evidence_count']:,}
  uses (verse + heading), все как zero-vote corroboration/manual-review evidence;
- book-balanced annotation panel: {summary['gold_panel_verses']:,} стихов,
  {summary['gold_projected_decisions']:,} projected original decisions;
- закреплённые legacy negative counterexamples: {summary['negative_annotations']};
- fail-closed candidate rows across all independent generators: {summary['candidate_count']:,}
  (first-party {summary['candidate_counts']['first_party']:,}; bidirectional statistical
  {summary['candidate_counts']['bidirectional_statistical']:,}; multilingual contextual
  {summary['candidate_counts']['multilingual_contextual']:,}; resolver-eligible `0`);
- accepted production Strong links/markers: `0` (fail-closed).

## Авторские сноски как evidence

Все {summary['author_comment_evidence_count']:,} стиховые и заголовочные uses
exact OH1988 разобраны отдельно от текста стиха; затронуто
{summary['author_comment_target_ref_count']:,} target refs; все
{summary['author_comment_definition_count']:,} определения учтены хотя бы одним
use. Категории: `{stable_json(summary['author_comment_category_counts'])}`.
Языковые указатели: `{stable_json(summary['author_comment_language_counts'])}`;
review-состояния: `{stable_json(summary['author_comment_review_status_counts'])}`.
Найдено {summary['author_comment_exact_original_match_count']:,} exact
transliteration/original-script совпадений; ещё
{summary['author_comment_unmatched_source_form_count']:,} упоминаний сохранены
неразрешёнными. Совпадения только подтверждают stable original IDs и имеют
автоматический вес `0`. Все
{summary['author_comment_actionable_manual_review_count']:,} partial/ambiguous/
unmatched/variant uses получили безопасные manual-review records. Найденные
{summary['author_comment_textual_variant_count']:,} явные variant-note uses
добавлены в manual review; до component-level решения и gold span/null review
они не могут вывести Strong. Ни одна сноска не поступает на вход
statistical/contextual alignment и stage-6 comments не изменяются. Exact
`target_comment` доступен blind gold-reviewer как предкандидатное первичное
пояснение переводчика, но не считается независимым вторым witness.

## Source integrity

Новый importer читает exact raw STEP files и не наследует пропуски stage-4
нормализации. Current-main YLT-NT positional alias отклонён; используется tagged
SBLGNT transfer `v0.1.0`; только однозначная часть selectors имеет verse-wide
surface+Strong crosswalk к stable TAGNT token, остальные сохранены отклонёнными
как unproven. RUSSYN и YLT остаются разными bridge families, но их общая Clear
инфраструктура отражена как dependency, а target→OH link не считается
доказанным самим наличием bridge.

OSHB, UXLC и UGNT повторно разобраны из exact ZIP inputs с source-qualified
stable IDs. Их native ref grids точно равны TAHOT/TAGNT grids: 23 213 OT и
7 958 NT. Crosswalk использует native verse, surface и совместимый Strong, но
никогда не создаёт direct control→OH1988 link. Ketiv/qere, brackets, повторы и
210 nonzero UGNT Strong encodings остаются unresolved.

Bridge status counts: `{stable_json(bridge_counts)}`.

## Textual fingerprint

Exact 1 538-листовой OH1988 scan и его front/back matter полностью проверены;
также зафиксированы первичные документы Огиенко 1927 и Илариона 1963. Они
доказывают Hebrew как общую основу OT, Greek как общую основу NT и эпизодическое
использование LXX, но не называют точные исходные редакции и не доказывают
неизменность 1962→1988. Диагностическая панель расширена до
{summary['fingerprint_locus_count']:,} loci. TAHOT `X` хранится только как
реконструированная LXX-alternative, а Treg+TR/Byz без NA/SBL/WH больше не
считается modern-critical reading. Из 53 diagnostic loci
{summary['fingerprint_resolved_locus_count']:,} получили fail-closed component-level
selection/disposition, включая {summary['manual_textual_resolution_count']:,}
post-candidate manual choices; unresolved critical/high среди этих loci:
{summary['unresolved_textual_locus_count']:,}. Отдельно во всём raw apparatus остаются
{summary['global_unresolved_source_apparatus_ref_count']:,} fail-closed refs /
{summary['unresolved_textual_component_count']:,} components; они блокируют
только соответствующие loci до adjudication и gold calibration.

## Почему markup не создан

Legacy baseline имеет 1 457 duplicate original assignments и известную ошибку
`Luke.2.11 G3739 → вас`, хотя старый класс назывался `high`. Его 440 280
occurrences и confidence не участвуют в голосовании. Без frozen gold и Wilson
one-sided lower bound ≥ 99.5% автоматический класс A был бы недоказан. B/C без
ручной проверки также запрещены нормативным планом.

## Границы

SQLite не создавался. Working DB, `web/db`, KJV, LXX_TR, content tool, Flutter,
runtime и этап 8 не изменялись. В дорожной карте отмечены только доказанные
автономные подпункты и промежуточные артефакты; общий этап и exit criteria
остаются открытыми.
"""


def _validation_log(summary: Mapping[str, Any]) -> str:
    return f"""# Ukrainian stage 7 validation log

Date: `2026-08-15`
Schema-Version: `{SCHEMA_VERSION}`
Contract: `{CONTRACT_VERSION}`
Status: `blocked_before_gold_and_alignment_acceptance`
Processed: `{summary['target_count']}` target positions
Skipped: `{summary['original_token_count']}` original components (no production assignment)
Errors: `0` generator errors

## Generation invariants

- stage-6 text SHA-256: `{EXPECTED_STAGE6_TEXT_SHA256}` — PASS
- stage-6 manifest SHA-256: `{EXPECTED_STAGE6_MANIFEST_SHA256}` — PASS
- stage-6 comments SHA-256: `{EXPECTED_STAGE6_COMMENT_SHA256}` — PASS
- author footnote uses: `{summary['author_comment_evidence_count']}` total,
  `{summary['author_comment_textual_variant_count']}` textual-variant notes,
  automatic vote `0` — PASS / MANUAL-REVIEW GATE
- exact target positions: `{summary['target_count']}` — PASS
- exact scalar/byte token round-trip: `{summary['ukrainian_token_count']}` tokens — PASS
- raw original parser errors: `0` — PASS
- raw OSHB/UXLC/UGNT controls: `{summary['original_control_token_count']}` tokens — PASS
- original-control crosswalk unresolved/service: `{summary['original_control_unresolved_count']}` — EXPLICIT FAIL-CLOSED
- production Strong markers emitted: `0` — EXPECTED FAIL-CLOSED
- frozen gold accepted decisions: `0` — BLOCKER
- independent gold pass 2: missing — BLOCKER
- A_auto Wilson lower bound ≥99.5%: not calibrated — BLOCKER
- unresolved critical/high: `{summary['unresolved_critical_high']}` — BLOCKER
- stage 8 / SQLite: not run — PASS

## Repository-wide commands

- `python -m scripts.bible_module.ukrainian_stage_3_sources --check` — PASS,
  source lock/cache verified, `source_count=14`.
- `python -m scripts.bible_module.ukrainian_stage_4 --check` — PASS (exit 0).
- `python -m scripts.bible_module.ukrainian_stage_5 --check` — PASS,
  `{{"stage":5,"status":"verified"}}`.
- `python -m scripts.bible_module.ukrainian_stage_6 --check` — PASS,
  `{{"stage":6,"status":"verified"}}`.
- focused pure/gold contract subset — PASS, `56` tests; generated-artifact
  assertions are pending regeneration of the current fingerprint/candidates.
- `python -m unittest discover -s scripts/bible_module/tests` — PENDING after
  current stage-7 implementation is complete.
- `python -m unittest discover -s scripts/content_tool/tests` — PENDING final
  regression run; content tool was not changed.
- `dart format .`, `flutter analyze`, `flutter test` — PENDING final regression
  run; Dart/Flutter runtime was not changed.
- forbidden-pattern and docs-sync checks — PENDING final regression run.
- double deterministic generation — PENDING after all current candidate and
  fingerprint artifacts are integrated.
- smoke integration — N/A: runtime, startup, routes and deep links were not changed.
- `git diff --check` and final secrets/binaries/full-corpus/gitignore audit —
  PENDING final regression run; SQLite count created/modified by stage 7 remains
  `0`.
"""


def _write_artifact_inventory(report_dir: Path, work_dir: Path) -> None:
    entries: list[dict[str, Any]] = []
    for root_name, root in (("report", report_dir), ("work", work_dir)):
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            if path.name == "artifact_inventory.manifest.json" or (
                root_name == "report" and path.name == "HANDOFF.ru.md"
            ):
                continue
            entries.append(
                {
                    "root": root_name,
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    payload = _seal_payload(
        {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "artifact": "artifact_inventory",
            "status": "blocked_stage_evidence_inventory",
            "entries": entries,
            "processed_count": len(entries),
            "skipped_count": 0,
            "error_count": 0,
            "input_sha256": {"stage6_text": EXPECTED_STAGE6_TEXT_SHA256},
            "output_sha256": {f"{item['root']}/{item['path']}": item["sha256"] for item in entries},
            "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
        }
    )
    _write_json(report_dir / "artifact_inventory.manifest.json", payload)


def _validate_finalized_gold_current_inputs(
    finalized_gold_lock: Mapping[str, Any],
    current_inputs: Mapping[str, str],
) -> None:
    """Require every reproducible current input while permitting review locks.

    The finalized lock also contains review-pass and adjudication hashes which
    are not regenerated by the ordinary stage-7 command.  Current generated
    inputs are therefore an exact required subset, not an equality comparison.
    """

    locked_inputs = finalized_gold_lock.get("input_sha256")
    if not isinstance(locked_inputs, Mapping):
        raise RuntimeError("Finalized gold lacks input SHA-256 locks")
    stale = [
        key
        for key, value in sorted(current_inputs.items())
        if locked_inputs.get(key) != value
    ]
    if stale:
        raise RuntimeError(
            "Finalized gold is stale against regenerated stage-7 inputs: "
            + ", ".join(stale)
        )


def _legacy_negative_annotations_for_overrides(
    gold: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    """Return only the separately retained rejected-legacy evidence rows."""

    rows = gold.get("legacy_negative_annotations")
    if not isinstance(rows, list) or len(rows) != gold.get(
        "legacy_negative_annotation_count"
    ):
        raise RuntimeError("Legacy negative annotation accounting drifted")
    if any(
        row.get("record_type") != "negative_edge"
        or not row.get("annotation_id")
        or not isinstance(row.get("original"), Mapping)
        or not row["original"].get("legacy_source_token_id")
        for row in rows
    ):
        raise RuntimeError("Legacy negative annotation schema drifted")
    return rows


def _require_candidate_input_digests(
    manifest: Mapping[str, Any], expected: Mapping[str, str], *, channel: str
) -> None:
    recorded = manifest.get("input_sha256")
    if not isinstance(recorded, Mapping) or dict(recorded) != dict(expected):
        raise RuntimeError(f"{channel} candidate input digest contract drifted")
    if any(re.fullmatch(r"[0-9a-f]{64}", value) is None for value in expected.values()):
        raise RuntimeError(f"{channel} candidate input digest is not SHA-256")


def _require_candidate_output_files(
    directory: Path,
    output_files: Mapping[str, str],
    required_names: set[str],
    *,
    channel: str,
) -> None:
    if set(output_files) != required_names:
        raise RuntimeError(f"{channel} candidate output inventory drifted")
    for name, expected_digest in sorted(output_files.items()):
        if re.fullmatch(r"[0-9a-f]{64}", str(expected_digest)) is None:
            raise RuntimeError(f"{channel} candidate output digest is invalid: {name}")
        path = directory / name
        if not path.is_file() or _sha256_file(path) != expected_digest:
            raise RuntimeError(f"{channel} candidate output digest mismatch: {name}")


def _validate_first_party_candidate_bundle(
    directory: Path, *, expected_inputs: Mapping[str, str]
) -> dict[str, Any]:
    manifest_path = directory / "alignment_candidates.first_party.manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("First-party candidate manifest is missing")
    manifest = _read_json(manifest_path)
    _require_candidate_input_digests(manifest, expected_inputs, channel="first-party")
    if (
        manifest.get("status") != "complete_candidate_only_no_auto_acceptance"
        or manifest.get("automatic_acceptance") is not False
        or manifest.get("calibration") != "not_run"
        or manifest.get("error_count") != 0
        or manifest.get("processed_count") != manifest.get("counts", {}).get("total_candidates")
    ):
        raise RuntimeError("First-party candidate manifest is not fail-closed")
    outputs = manifest.get("output_sha256")
    if not isinstance(outputs, Mapping):
        raise RuntimeError("First-party candidate output inventory is missing")
    _require_candidate_output_files(
        directory,
        outputs,
        {
            "alignment_candidates.first_party.jsonl",
            "candidate_generator_registry.json",
        },
        channel="first-party",
    )
    registry = _read_json(directory / "candidate_generator_registry.json")
    generators = registry.get("generators")
    if (
        registry.get("input_sha256") != dict(expected_inputs)
        or registry.get("error_count") != 0
        or not isinstance(generators, list)
        or not generators
        or any(
            item.get("calibrated") is not False
            or item.get("auto_acceptance") is not False
            or item.get("position_feature_used") is not False
            for item in generators
        )
    ):
        raise RuntimeError("First-party candidate registry drifted")
    return manifest


def _validate_statistical_candidate_bundle(
    directory: Path,
    *,
    expected_inputs: Mapping[str, str],
    expected_target_refs: int = EXPECTED_TARGET_COUNT,
) -> dict[str, Any]:
    manifest_path = directory / "statistical_candidates.manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("Statistical candidate manifest is missing")
    manifest = _read_json(manifest_path)
    _require_candidate_input_digests(manifest, expected_inputs, channel="statistical")
    folds = manifest.get("folds")
    counts = manifest.get("counts")
    if (
        manifest.get("statistical_contract_version") != STATISTICAL_CONTRACT_VERSION
        or manifest.get("generator_id") != STATISTICAL_GENERATOR_ID
        or manifest.get("status") != "candidate_only_uncalibrated_no_auto_acceptance"
        or manifest.get("error_count") != 0
        or manifest.get("processed_count") != expected_target_refs
        or not isinstance(counts, Mapping)
        or counts.get("verse_count") != expected_target_refs
        or not isinstance(folds, list)
        or len(folds) != 5
        or any(item.get("training_and_held_out_disjoint") is not True for item in folds)
        or sum(int(item.get("held_out_verse_count", -1)) for item in folds)
        != expected_target_refs
        or sum(int(item.get("candidate_count", -1)) for item in folds)
        != counts.get("candidate_count")
    ):
        raise RuntimeError("Statistical candidate manifest is incomplete or unsafe")
    output_files = manifest.get("output_files")
    if not isinstance(output_files, Mapping):
        raise RuntimeError("Statistical candidate output inventory is missing")
    _require_candidate_output_files(
        directory,
        output_files,
        {
            "alignment_candidates.statistical.jsonl",
            "statistical_generator_registry.json",
        },
        channel="statistical",
    )
    if manifest.get("output_sha256") != output_files["alignment_candidates.statistical.jsonl"]:
        raise RuntimeError("Statistical candidate payload digest drifted")
    registry = _read_json(directory / "statistical_generator_registry.json")
    reproducibility = registry.get("reproducibility")
    if (
        registry.get("statistical_contract_version") != STATISTICAL_CONTRACT_VERSION
        or registry.get("generator_id") != STATISTICAL_GENERATOR_ID
        or registry.get("input_sha256") != dict(expected_inputs)
        or registry.get("error_count") != 0
        or not isinstance(reproducibility, Mapping)
        or reproducibility.get("auto_acceptance") is not False
        or reproducibility.get("resolver_eligible") is not False
        or reproducibility.get("token_order_used_for_scoring") is not False
    ):
        raise RuntimeError("Statistical candidate registry drifted")
    return manifest


def _validate_contextual_candidate_bundle(
    directory: Path,
    *,
    expected_inputs: Mapping[str, str],
    expected_target_refs: int = EXPECTED_TARGET_COUNT,
) -> dict[str, Any]:
    manifest_path = directory / "alignment_candidates.contextual.manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("Contextual candidate manifest is missing")
    manifest = _read_json(manifest_path)
    recorded_inputs = manifest.get("input_sha256")
    if not isinstance(recorded_inputs, Mapping) or any(
        recorded_inputs.get(name) != digest for name, digest in expected_inputs.items()
    ):
        raise RuntimeError("Contextual candidate input digest contract drifted")
    counts = manifest.get("counts")
    if (
        manifest.get("contextual_contract_version") != CONTEXTUAL_CONTRACT_VERSION
        or manifest.get("status") != "complete_candidate_only_no_auto_acceptance"
        or manifest.get("error_count") != 0
        or manifest.get("processed_count") != expected_target_refs
        or manifest.get("calibrated") is not False
        or manifest.get("auto_acceptance") is not False
        or manifest.get("resolver_eligible") is not False
        or not isinstance(counts, Mapping)
        or counts.get("preflight.validated_target_refs") != expected_target_refs
        or counts.get("preflight.preflight_verses") != expected_target_refs
        or counts.get("skipped_model_input_too_long", 0) != 0
        # The fingerprint-selected candidate layer contains only addressable
        # surface components.  The 14 TAHOT primary-null records remain
        # accounted in the raw universe, but are intentionally absent here.
        or counts.get("surface.original_rows_skipped_empty_surface", 0) != 0
        or counts.get("target_tokens_skipped_nonlexical") != 3
    ):
        raise RuntimeError("Contextual candidate manifest is incomplete or unsafe")
    output_files = manifest.get("output_files")
    if not isinstance(output_files, Mapping):
        raise RuntimeError("Contextual candidate output inventory is missing")
    _require_candidate_output_files(
        directory,
        output_files,
        {
            "alignment_candidates.contextual.jsonl",
            "contextual_generator_registry.json",
        },
        channel="contextual",
    )
    if manifest.get("output_sha256") != output_files["alignment_candidates.contextual.jsonl"]:
        raise RuntimeError("Contextual candidate payload digest drifted")
    registry = _read_json(directory / "contextual_generator_registry.json")
    validate_contextual_generator_registry(registry)
    if registry.get("generator_id") != CONTEXTUAL_GENERATOR_ID:
        raise RuntimeError("Contextual candidate registry generator drifted")
    return manifest


def _candidate_registry_index(
    *,
    source_registry_sha256: str,
    first_party_dir: Path,
    statistical_dir: Path,
    contextual_dir: Path,
) -> dict[str, Any]:
    specs = (
        (
            "first_party",
            first_party_dir / "candidate_generator_registry.json",
            first_party_dir / "alignment_candidates.first_party.manifest.json",
        ),
        (
            "bidirectional_statistical",
            statistical_dir / "statistical_generator_registry.json",
            statistical_dir / "statistical_candidates.manifest.json",
        ),
        (
            "multilingual_contextual",
            contextual_dir / "contextual_generator_registry.json",
            contextual_dir / "alignment_candidates.contextual.manifest.json",
        ),
    )
    generators: list[dict[str, Any]] = []
    inputs = {"source_registry": source_registry_sha256}
    for channel, registry_path, manifest_path in specs:
        registry_sha256 = _sha256_file(registry_path)
        manifest_sha256 = _sha256_file(manifest_path)
        inputs[f"{channel}_registry"] = registry_sha256
        inputs[f"{channel}_manifest"] = manifest_sha256
        generators.append(
            {
                "channel": channel,
                "registry_path": registry_path.name,
                "registry_sha256": registry_sha256,
                "manifest_path": manifest_path.name,
                "manifest_sha256": manifest_sha256,
                "registry": _read_json(registry_path),
            }
        )
    return _seal_payload(
        {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "artifact": "candidate_generator_registry_index",
            "status": "all_independent_candidate_generators_frozen_candidate_only",
            "generators": generators,
            "processed_count": len(generators),
            "skipped_count": 0,
            "error_count": 0,
            "input_sha256": dict(sorted(inputs.items())),
            "output_sha256": {},
            "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
        }
    )


def _validate_candidate_registry_index(
    payload: Mapping[str, Any],
    *,
    source_registry_sha256: str,
    first_party_dir: Path,
    statistical_dir: Path,
    contextual_dir: Path,
) -> None:
    if (
        payload.get("status")
        != "all_independent_candidate_generators_frozen_candidate_only"
        or payload.get("processed_count") != 3
        or payload.get("skipped_count") != 0
        or payload.get("error_count") != 0
        or payload.get("input_sha256", {}).get("source_registry")
        != source_registry_sha256
    ):
        raise RuntimeError("Aggregate candidate registry index drifted")
    generators = payload.get("generators")
    if not isinstance(generators, list) or [
        item.get("channel") for item in generators
    ] != ["first_party", "bidirectional_statistical", "multilingual_contextual"]:
        raise RuntimeError("Aggregate candidate registry channel inventory drifted")
    directories = {
        "first_party": first_party_dir,
        "bidirectional_statistical": statistical_dir,
        "multilingual_contextual": contextual_dir,
    }
    for item in generators:
        directory = directories[item["channel"]]
        registry_path = directory / item["registry_path"]
        manifest_path = directory / item["manifest_path"]
        if (
            not registry_path.is_file()
            or not manifest_path.is_file()
            or _sha256_file(registry_path) != item.get("registry_sha256")
            or _sha256_file(manifest_path) != item.get("manifest_sha256")
            or _read_json(registry_path) != item.get("registry")
        ):
            raise RuntimeError(
                f"Aggregate candidate registry provenance drifted: {item['channel']}"
            )
    sealed = payload.get("output_sha256", {}).get(
        "canonical_payload_before_output_digest"
    )
    unsealed = dict(payload)
    unsealed["output_sha256"] = {}
    if sealed != sha256_text(stable_json(unsealed)):
        raise RuntimeError("Aggregate candidate registry seal drifted")


def generate(
    *,
    work_dir: Path = WORK,
    report_dir: Path = REPORT,
    stop_after_candidate_input_preparation: bool = False,
) -> dict[str, Any]:
    work_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    finalized_gold_lock = validated_finalized_gold_lock(report_dir)
    rows, stage6_by_ref = _stage6_rows()

    registry = _seal_payload(_source_registry())
    _write_json(report_dir / "source_registry.json", registry)

    token_inventory = _tokenize_stage6(rows, work_dir)
    token_manifest = _manifest(
        artifact="ukrainian_token_inventory",
        status="complete_exact_occurrence_inventory_and_round_trip",
        inputs={"stage6_text": EXPECTED_STAGE6_TEXT_SHA256, "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256},
        outputs={"ukrainian_token_inventory.jsonl": token_inventory["sha256"]},
        processed=token_inventory["count"],
        counts={"target_positions": len(rows), "surface_tokens": token_inventory["count"], "comparison_lexemes": token_inventory["lexeme_count"], "nonlexical_orthographic_mark_tokens": token_inventory["nonlexical_count"], "utf8_surface_bytes": token_inventory["byte_count"], "context_window_radius": 2, "folds": 5},
        notes=["surface and scalar/byte offsets are exact and immutable", "comparison normalization, context windows and low-confidence morphology candidates are separate derived fields", "historical orthography is never rewritten"],
    )
    _write_json(report_dir / "ukrainian_token_inventory.manifest.json", token_manifest)

    universe = _parse_original_universe(stage6_by_ref, work_dir)
    controls = _parse_original_controls(universe, work_dir)
    fingerprint = _seal_payload(_textual_fingerprint(stage6_by_ref, universe))
    _write_json(report_dir / "textual_fingerprint.manifest.json", fingerprint)
    selected_original_layer = _build_fingerprint_selected_original_layer(
        stage6_by_ref=stage6_by_ref,
        universe=universe,
        controls=controls,
        fingerprint=fingerprint,
        work=work_dir,
    )
    original_manifest = _manifest(
        artifact="original_token_universe",
        status="raw_primary_alternative_control_layers_proven_with_53_locus_selection_overlay_and_five_local_choices",
        inputs=universe["file_hashes"]
        | controls["input_sha256"]
        | {
            "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
            "textual_fingerprint": _sha256_file(
                report_dir / "textual_fingerprint.manifest.json"
            ),
        },
        outputs={
            "original_token_universe.jsonl": universe["sha256"],
            "original_parent_inventory.jsonl": universe["parent_sha256"],
            "original_alternative_inventory.jsonl": universe["alternative_sha256"],
            "original_control_tokens.jsonl": controls["token_sha256"],
            "original_control_crosswalk.jsonl": controls["crosswalk_sha256"],
            "fingerprint_selected_original_layer.jsonl": selected_original_layer[
                "sha256"
            ],
        },
        processed=universe["count"]
        + universe["alternative_count"]
        + controls["count"]
        + selected_original_layer["count"],
        skipped=sum(
            value
            for key, value in universe["counters"].items()
            if key.endswith("metadata_or_non17")
            or key.endswith("metadata_or_bad_ref")
        )
        + sum(
            value
            for key, value in controls["counters"].items()
            if key.startswith("crosswalk.unresolved_")
            or key == "crosswalk.service_not_crosswalked"
        ),
        errors=0,
        counts={
            "parent_tokens": universe["parent_count"],
            "alternative_candidates": universe["alternative_count"],
            "TAHOT_textual_surface_alternatives": universe["counters"]["TAHOT.alternative.textual_surface_strong_candidate"],
            "TAHOT_alternative_strong_candidates": universe["counters"]["TAHOT.alternative.lexical_strong_candidate"],
            "TAGNT_textual_surface_alternatives": universe["counters"]["TAGNT.alternative.textual_surface_strong_candidate"],
            "TAGNT_alternative_strong_candidates": universe["counters"]["TAGNT.alternative.lexical_strong_candidate"],
            "TAHOT_components_including_primary_null": universe["counters"]["TAHOT.components"],
            "TAGNT_components": universe["counters"]["TAGNT.components"],
            "TAHOT_classic_base_renderable": universe["counters"]["TAHOT.classic_base_renderable"],
            "TAGNT_classic_base_renderable": universe["counters"]["TAGNT.classic_base_renderable"],
            "TAHOT_nonclassic_or_null": universe["counters"]["TAHOT.nonclassic_or_null"],
            "TAGNT_nonclassic": universe["counters"]["TAGNT.nonclassic_or_null"],
            "TAHOT_primary_null": universe["counters"]["TAHOT.primary_null_records"],
            "target_ref_coverage": universe["ref_count"],
            "missing_target_refs": len(universe["missing_refs"]),
            "outside_target_grid_parents": sum(value for key, value in universe["counters"].items() if key.endswith("outside_target_grid")),
            "alternative_unresolved_textual_tokens": sum(
                value
                for key, value in universe["counters"].items()
                if key.startswith("reading.alternative_")
                or key.startswith("reading.unresolved_")
            ),
            "TAHOT_lxx_reconstruction_alternative": universe["counters"]["reading.alternative_lxx_reconstruction_unresolved"],
            "blocked_ps22_16_components": universe["counters"]["reading.unresolved_blocking_textual_locus"],
            "control_tokens": controls["count"],
            "OSHB_tokens": controls["counters"]["source.openscriptures_oshb_v2_2.tokens"],
            "UXLC_tokens": controls["counters"]["source.tanach_us_uxlc_2_5_27_6.tokens"],
            "UGNT_tokens": controls["counters"]["source.unfoldingword_ugnt_v0_34.tokens"],
            "control_crosswalk_resolved": sum(
                value
                for key, value in controls["counters"].items()
                if key.startswith("crosswalk.resolved_")
            ),
            "control_crosswalk_unresolved_or_service": sum(
                value
                for key, value in controls["counters"].items()
                if key.startswith("crosswalk.unresolved_")
                or key == "crosswalk.service_not_crosswalked"
            ),
            "UGNT_nonclassic_unresolved": controls["counters"]["UGNT.nonclassic_or_invalid"],
            "fingerprint_selected_main_original_tokens": sum(
                row["selected_original_token_count"]
                for row in fingerprint["loci"]
            ),
            "fingerprint_selected_supplemental_control_tokens": sum(
                len(row["supplemental_control_candidate_ids"])
                for row in fingerprint["loci"]
            ),
            "fingerprint_unresolved_local_choice_groups": sum(
                len(row["unresolved_choice_groups"])
                for row in fingerprint["loci"]
            ),
            "selected_original_layer_tokens": selected_original_layer["count"],
            "selected_original_layer_target_refs": selected_original_layer[
                "ref_count"
            ],
            "selected_original_layer_unresolved_choice_candidates_excluded": selected_original_layer[
                "choice_candidate_count"
            ],
            "selected_original_layer_apparatus_candidates": selected_original_layer[
                "counters"
            ]["fingerprint_selected_apparatus_candidate"],
            "selected_original_layer_supplemental_controls": selected_original_layer[
                "counters"
            ]["fingerprint_selected_original_control"],
        },
        notes=["stable parent ID is SHA-256(step family, pinned commit, exact native locator); component suffixes preserve TAHOT group/atom and TAGNT compound identity", "alternative apparatus readings have distinct stable IDs and enter the selected original layer only through an explicit component-level fingerprint decision", "candidate and gold generators consume fingerprint_selected_original_layer.jsonl rather than guessing from the raw universe; the five local choice groups are absent", "Acts.15.34 supplements TAGNT with four source-qualified UGNT control IDs after D05 witness adjudication; G3441 is proven omitted and the Ukrainian Jerusalem phrase is a Strong-less versional addition", "2Chr.14.1(13.23) is split by proven source word boundary", "all stage-4 STEP omissions are recovered by raw reparse", "TAHOT dictionary mapping is preserved raw and is not mislabeled as a normalized Hebrew lemma", "OSHB/UXLC/UGNT are consumed as source-qualified native-token controls; their crosswalk never targets OH1988 directly", "UGNT terminal-zero Strong decoding is explicit; all nonzero encodings remain unresolved", "five local fingerprint choices and all globally unresolved source readings cannot receive automatic OH1988 assignments"],
    )
    original_manifest["missing_target_refs"] = universe["missing_refs"]
    original_manifest["raw_reparse_audit_sha256"] = universe["audit_digests"]
    original_manifest["control_ref_audit"] = controls["ref_audit"]
    original_manifest["control_native_token_type_counts"] = {
        key: controls["counters"][key]
        for key in (
            "OSHB.ordinary",
            "OSHB.ketiv",
            "OSHB.qere",
            "OSHB.strong_occurrences",
            "UXLC.w",
            "UXLC.q",
            "UXLC.k",
            "UXLC.x",
            "UXLC.structural_pe_skipped",
            "UXLC.structural_samekh_skipped",
            "UXLC.structural_reversednun_skipped",
            "UGNT.classic_terminal_zero",
            "UGNT.nonclassic_or_invalid",
        )
    }
    original_manifest["control_crosswalk_status_counts"] = {
        key.removeprefix("crosswalk."): value
        for key, value in sorted(controls["counters"].items())
        if key.startswith("crosswalk.")
    }
    _write_json(report_dir / "original_token_universe.manifest.json", original_manifest)

    author_comment_dir = work_dir / "author_comment_evidence"
    author_comment_inputs = {
        "footnote_definitions": EXPECTED_STAGE6_FOOTNOTE_DEFINITIONS_SHA256,
        "footnote_uses": EXPECTED_STAGE6_FOOTNOTE_USES_SHA256,
        "heading_footnotes": EXPECTED_STAGE6_HEADING_FOOTNOTES_SHA256,
        "stage6_target_comments": EXPECTED_STAGE6_COMMENT_SHA256,
        "ukrainian_token_inventory": token_inventory["sha256"],
        "fingerprint_selected_original_layer": selected_original_layer["sha256"],
    }
    author_comments = generate_author_comment_evidence(
        footnote_definitions_path=STAGE6_FOOTNOTE_DEFINITIONS,
        footnote_uses_path=STAGE6_FOOTNOTE_USES,
        heading_footnotes_path=STAGE6_HEADING_FOOTNOTES,
        target_comments_path=STAGE6_COMMENTS,
        token_inventory_path=token_inventory["path"],
        selected_original_layer_path=selected_original_layer["path"],
        output_dir=author_comment_dir,
        expected_input_sha256=author_comment_inputs,
    )
    validate_author_comment_evidence_bundle(
        output_dir=author_comment_dir,
        expected_input_sha256=author_comment_inputs,
    )
    author_comment_report_manifest = dict(author_comments)
    author_comment_report_manifest["output_sha256"] = {
        f"author_comment_evidence/{AUTHOR_COMMENT_OUTPUT_NAME}": author_comments[
            "output_sha256"
        ][AUTHOR_COMMENT_OUTPUT_NAME]
    }
    author_comment_report_manifest["license_provenance"] = {
        "source_id": "commons_ohienko_1988_scan",
        "exact_scan_sha256": "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "derivation": "exact stage-4/5/6 footnote extraction and projection; comments are not aligner target text",
        "source_registry_sha256": _sha256_file(
            report_dir / "source_registry.json"
        ),
    }
    _write_json(
        report_dir / "author_comment_evidence.manifest.json",
        author_comment_report_manifest,
    )

    bridges = _import_bridges(universe, work_dir)
    bridge_counts: Counter[str] = Counter()
    for item in bridges["summaries"]:
        bridge_counts.update(item["counts"])
    bridge_manifest = _manifest(
        artifact="parallel_bridge_alignment",
        status="imported_fail_closed_original_bridge_only",
        inputs={f"{item['family']}_{item['scope']}_alignment": item["alignment_sha256"] for item in bridges["summaries"]},
        outputs={"parallel_bridge_alignment.jsonl": bridges["sha256"]},
        processed=bridges["count"],
        skipped=sum(value for key, value in bridge_counts.items() if key.startswith("rejected_")),
        errors=0,
        counts=dict(bridge_counts),
        notes=["LatinWordTokenizer implementation is unavailable upstream; frozen TSV token IDs are consumed without retokenization", "accepted subset proves original→RUSSYN/YLT only; ambiguous selectors remain rejected", "cross-verse records preserve source and target refs instead of transferring by verse", "RUSSYN/YLT target token to OH remains unproven; connected-record coalescing is pending"],
    )
    bridge_manifest["bundles"] = bridges["summaries"]
    bridge_manifest["cross_verse_manual_record_count"] = sum(item["cross_verse_manual_record_count"] for item in bridges["summaries"])
    _write_json(report_dir / "parallel_bridge_alignment.manifest.json", bridge_manifest)

    lexemes = _lexeme_inventory(token_inventory, work_dir)
    lexeme_manifest = _manifest(
        artifact="ukrainian_lexeme_strong_ledger",
        status="occurrence_lexeme_and_morphology_candidate_inventory_complete_strong_distributions_blocked_before_gold",
        inputs={"ukrainian_token_inventory": token_inventory["sha256"]},
        outputs={"ukrainian_lexeme_strong_ledger.jsonl": lexemes["sha256"]},
        processed=lexemes["count"],
        skipped=lexemes["nonlexical_skipped"],
        counts={"lexemes": lexemes["count"], "nonlexical_orthographic_marks_excluded": lexemes["nonlexical_skipped"], "accepted_strong_distributions": 0, "leakage_free_folds": 5},
        notes=["out-of-fold occurrence counts exclude the evaluated fold", "exact occurrences retain book, testament, genre, context digest and neighboring comparison forms", "lemma/POS/morphology values are conservative first-party candidates and carry no Strong vote", "legacy global-corpus distributions are excluded as leakage", "entropy, compounds and accepted Strong distributions remain empty until reviewed links exist"],
    )
    lexeme_manifest["morphology_candidate_profile"] = {
        "id": "ukrainian-rule-morph-v1",
        "implementation": "scripts/bible_module/ukrainian_stage_7.py:ukrainian_morphology_candidates",
        "license": "first-party project code",
        "role": "inventory candidate only; zero Strong vote",
    }
    _write_json(report_dir / "ukrainian_lexeme_strong_ledger.manifest.json", lexeme_manifest)

    if finalized_gold_lock is not None:
        # Never overwrite the reviewed input grid before proving that a fresh
        # regeneration is byte-identical to the finalized lock.  The temporary
        # work directory is removed only after this validation scope exits.
        with tempfile.TemporaryDirectory(
            prefix="gold-regeneration-audit-", dir=work_dir
        ) as temporary_gold_work:
            gold = _gold_preparation(
                rows,
                universe,
                fingerprint,
                controls["token_path"],
                selected_original_layer["path"],
                Path(temporary_gold_work),
                report_dir,
                write_placeholder_annotations=False,
            )
            preparation_path = report_dir / GOLD_PREPARATION_MANIFEST
            current_gold_inputs = {
                "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
                "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256,
                "source_registry": _sha256_file(
                    report_dir / "source_registry.json"
                ),
                "original_token_universe": universe["sha256"],
                "fingerprint_selected_original_layer": selected_original_layer[
                    "sha256"
                ],
                "gold_selected_original_layer": gold[
                    "gold_selected_original_layer_sha256"
                ],
                "ukrainian_token_inventory": token_inventory["sha256"],
                "original_token_universe_manifest": _sha256_file(
                    report_dir / "original_token_universe.manifest.json"
                ),
                "gold_alignment_preparation_manifest": _sha256_file(
                    preparation_path
                ),
                "gold_selection_panel": gold["panel_sha256"],
                "gold_annotation_workbench": gold["workbench_sha256"],
            }
            _validate_finalized_gold_current_inputs(
                finalized_gold_lock, current_gold_inputs
            )
            canonical_gold_files = {
                "panel_path": work_dir / "gold_selection_panel.jsonl",
                "workbench_path": work_dir / "gold_annotation_workbench.jsonl",
                "gold_selected_original_layer_path": work_dir
                / "gold_selected_original_layer.jsonl",
            }
            digest_keys = {
                "panel_path": "panel_sha256",
                "workbench_path": "workbench_sha256",
                "gold_selected_original_layer_path": "gold_selected_original_layer_sha256",
            }
            for path_key, canonical_path in canonical_gold_files.items():
                if (
                    not canonical_path.is_file()
                    or _sha256_file(canonical_path) != gold[digest_keys[path_key]]
                ):
                    raise RuntimeError(
                        "Finalized gold input file is missing or differs from "
                        f"its regenerated lock: {canonical_path.name}"
                    )
                gold[path_key] = canonical_path
        gold_manifest = _read_json(report_dir / "gold_alignment.manifest.json")
    else:
        gold = _gold_preparation(
            rows,
            universe,
            fingerprint,
            controls["token_path"],
            selected_original_layer["path"],
            work_dir,
            report_dir,
            write_placeholder_annotations=True,
        )
        gold_preparation_manifest = _manifest(
            artifact="gold_alignment_preparation",
            status="prepared_answer_free_gold_inputs",
            inputs={
                "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
                "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256,
                "source_registry": _sha256_file(
                    report_dir / "source_registry.json"
                ),
                "original_token_universe": universe["sha256"],
                "fingerprint_selected_original_layer": selected_original_layer[
                    "sha256"
                ],
                "ukrainian_token_inventory": token_inventory["sha256"],
                "original_token_universe_manifest": _sha256_file(
                    report_dir / "original_token_universe.manifest.json"
                ),
            },
            outputs={
                "gold_selection_panel.jsonl": gold["panel_sha256"],
                "gold_annotation_workbench.jsonl": gold["workbench_sha256"],
                "gold_selected_original_layer.jsonl": gold[
                    "gold_selected_original_layer_sha256"
                ],
            },
            processed=gold["panel_count"] + gold["projected_decisions"],
            counts={
                "selected_verses": gold["panel_count"],
                "projected_assignment_or_null_decisions": gold[
                    "projected_decisions"
                ],
                "gold_selected_original_tokens": gold[
                    "gold_selected_original_layer_count"
                ],
                "post_candidate_manual_textual_overlays": gold[
                    "post_candidate_manual_overlay_count"
                ],
            },
            notes=(
                "This immutable answer-free manifest survives gold finalization.",
                "Reviewer packets lock this file; the finalized gold manifest is never its own historical input.",
            ),
        )
        gold_preparation_manifest["gold_workflow_version"] = GOLD_WORKFLOW_VERSION
        _write_json(
            report_dir / GOLD_PREPARATION_MANIFEST,
            gold_preparation_manifest,
        )
        gold_manifest = _manifest(
            artifact="gold_alignment",
            status="blocked_unannotated_panel",
            inputs={"stage6_text": EXPECTED_STAGE6_TEXT_SHA256, "original_universe": universe["sha256"], "fingerprint_selected_original_layer": selected_original_layer["sha256"], "token_inventory": token_inventory["sha256"]},
            outputs={"gold_selection_panel.jsonl": gold["panel_sha256"], "gold_annotation_workbench.jsonl": gold["workbench_sha256"], "gold_selected_original_layer.jsonl": gold["gold_selected_original_layer_sha256"], "gold_alignment.annotations.jsonl": gold["annotation_sha256"]},
            processed=gold["annotation_count"],
            skipped=gold["projected_decisions"],
            errors=0,
            counts={
                "selected_verses": gold["panel_count"],
                "projected_assignment_or_null_decisions": gold["projected_decisions"],
                "accepted_assignment_or_null_decisions": 0,
                "negative_edges": gold["legacy_negative_annotation_count"],
                "pass_2_completed": 0,
                "minimum_required_verses": 2000,
                "minimum_required_decisions": 25000,
                "mapping_anomaly_refs": gold["mapping_anomaly_ref_count"],
                "fingerprint_refs": gold["fingerprint_ref_count"],
                "gold_selected_original_tokens": gold[
                    "gold_selected_original_layer_count"
                ],
                "post_candidate_manual_textual_overlays": gold[
                    "post_candidate_manual_overlay_count"
                ],
            },
            stratum_counts=gold["stratum_counts"],
            notes=["32/book deterministic selection was frozen before candidate tuning and augmented with every stage-5 merge/split target plus every declared textual-fingerprint locus", "ignored workbench contains exact text/comment, Ukrainian token IDs and scalar/byte offsets, and original context for manual annotation", "semantic link strata (reorder, omission/addition, repetition, named entities, particles, compounds and many-to-many) remain pending until actual annotation", "negative edges do not count toward the 25,000 assignment/null minimum", "critical/high requires two blind independent passes"],
        )
        gold_manifest["evaluation_contract"] = {
            "frozen_before_candidate_tuning": True,
            "fold_roles": {
                "0": "calibration",
                "1": "calibration",
                "2": "calibration",
                "3": "validation",
                "4": "sealed_evaluation",
            },
            "metric_unit": "final original-token accounting decision and accepted hyperedge",
            "automatic_class": "A_auto",
            "precision_gate": {
                "method": "one-sided Wilson lower confidence bound",
                "confidence": 0.95,
                "minimum_lower_bound": 0.995,
                "coverage_tradeoff_forbidden": True,
            },
            "underpowered_stratum_rule": "A_auto disabled when the declared book/genre/anomaly/evidence stratum cannot independently support the precision gate; metrics remain descriptive",
            "review_independence": "critical/high requires two distinct blind reviewers and independent adjudication on disagreement",
            "leakage_rule": "no label, lexeme statistic or candidate score from the evaluated fold may train or threshold that fold",
        }
        _write_json(report_dir / "gold_alignment.manifest.json", gold_manifest)

    if stop_after_candidate_input_preparation:
        preparation = _seal_payload(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "artifact": "candidate_input_preparation",
                "status": "complete_ready_for_independent_candidate_generation",
                "processed_count": len(rows),
                "skipped_count": 0,
                "error_count": 0,
                "input_sha256": {
                    "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
                    "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256,
                    "source_registry": _sha256_file(
                        report_dir / "source_registry.json"
                    ),
                },
                "output_sha256": {
                    "ukrainian_token_inventory.jsonl": token_inventory["sha256"],
                    "fingerprint_selected_original_layer.jsonl": selected_original_layer[
                        "sha256"
                    ],
                    "parallel_bridge_alignment.jsonl": bridges["sha256"],
                    "gold_selection_panel.jsonl": gold["panel_sha256"],
                    "gold_annotation_workbench.jsonl": gold["workbench_sha256"],
                    "gold_selected_original_layer.jsonl": gold[
                        "gold_selected_original_layer_sha256"
                    ],
                    GOLD_PREPARATION_MANIFEST: _sha256_file(
                        report_dir / GOLD_PREPARATION_MANIFEST
                    ),
                },
                "counts": {
                    "target_positions": len(rows),
                    "ukrainian_tokens": token_inventory["count"],
                    "selected_original_tokens": selected_original_layer["count"],
                    "gold_selected_original_tokens": gold[
                        "gold_selected_original_layer_count"
                    ],
                    "selected_original_target_refs": selected_original_layer[
                        "ref_count"
                    ],
                    "bridge_records": bridges["count"],
                    "gold_panel_verses": gold["panel_count"],
                    "gold_projected_decisions": gold["projected_decisions"],
                },
                "next_step": "run and independently verify first-party, statistical and contextual candidate-only generators against these exact digests",
                "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
            }
        )
        _write_json(
            report_dir / "candidate_input_preparation.manifest.json", preparation
        )
        return preparation

    first_party_candidate_dir = work_dir / "first_party_candidates"
    first_party_paths = {
        "ukrainian_token_inventory": token_inventory["path"],
        "original_token_universe": selected_original_layer["path"],
        "parallel_bridge_alignment": bridges["path"],
        "legacy_alignment": LEGACY_WORK / "strong_aligned_text.jsonl",
        "ukrainian_greek_descriptions": LOCAL_DB / "revelation_uk.sqlite",
        "source_registry": report_dir / "source_registry.json",
        **{
            f"bridge_target_{bundle.family}_{bundle.scope}": bundle.path
            for bundle in CANDIDATE_BRIDGE_TARGET_BUNDLES
        },
    }
    first_party_inputs = {
        name: _sha256_file(path) for name, path in sorted(first_party_paths.items())
    }
    if first_party_candidate_dir.exists():
        first_party_manifest = _validate_first_party_candidate_bundle(
            first_party_candidate_dir, expected_inputs=first_party_inputs
        )
    else:
        generate_candidate_only_artifacts(
            token_inventory_path=token_inventory["path"],
            original_universe_path=selected_original_layer["path"],
            bridge_alignment_path=bridges["path"],
            bridge_target_bundles=CANDIDATE_BRIDGE_TARGET_BUNDLES,
            legacy_alignment_path=LEGACY_WORK / "strong_aligned_text.jsonl",
            ukrainian_greek_description_database=LOCAL_DB / "revelation_uk.sqlite",
            source_registry_path=report_dir / "source_registry.json",
            output_dir=first_party_candidate_dir,
        )
        first_party_manifest = _validate_first_party_candidate_bundle(
            first_party_candidate_dir, expected_inputs=first_party_inputs
        )

    statistical_candidate_dir = work_dir / "statistical_candidates"
    statistical_inputs = {
        "ukrainian_token_inventory": token_inventory["sha256"],
        "original_token_universe": selected_original_layer["sha256"],
        "source_registry": _sha256_file(report_dir / "source_registry.json"),
    }
    if statistical_candidate_dir.exists():
        statistical_manifest = _validate_statistical_candidate_bundle(
            statistical_candidate_dir, expected_inputs=statistical_inputs
        )
    else:
        generate_statistical_candidate_artifacts(
            token_inventory_path=token_inventory["path"],
            original_universe_path=selected_original_layer["path"],
            source_registry_path=report_dir / "source_registry.json",
            output_dir=statistical_candidate_dir,
        )
        statistical_manifest = _validate_statistical_candidate_bundle(
            statistical_candidate_dir, expected_inputs=statistical_inputs
        )

    contextual_candidate_dir = work_dir / "contextual_candidates"
    contextual_inputs = {
        "token_inventory": token_inventory["sha256"],
        "original_token_universe": selected_original_layer["sha256"],
        "source_registry": _sha256_file(report_dir / "source_registry.json"),
        "model_snapshot_contract": MODEL_SNAPSHOT_CONTRACT_SHA256,
        "runtime_install_report": _sha256_file(
            CONTEXTUAL_RUNTIME_INSTALL_REPORT
        ),
    }
    if contextual_candidate_dir.exists():
        contextual_manifest = _validate_contextual_candidate_bundle(
            contextual_candidate_dir, expected_inputs=contextual_inputs
        )
    else:
        generate_contextual_artifacts(
            token_inventory_path=token_inventory["path"],
            original_universe_path=selected_original_layer["path"],
            source_registry_path=report_dir / "source_registry.json",
            model_snapshot_dir=CONTEXTUAL_MODEL_SNAPSHOT,
            runtime_install_report_path=CONTEXTUAL_RUNTIME_INSTALL_REPORT,
            runtime_packages_dir=CONTEXTUAL_RUNTIME_PACKAGES,
            output_dir=contextual_candidate_dir,
        )
        contextual_manifest = _validate_contextual_candidate_bundle(
            contextual_candidate_dir, expected_inputs=contextual_inputs
        )

    candidate_registry = _candidate_registry_index(
        source_registry_sha256=_sha256_file(report_dir / "source_registry.json"),
        first_party_dir=first_party_candidate_dir,
        statistical_dir=statistical_candidate_dir,
        contextual_dir=contextual_candidate_dir,
    )
    _write_json(report_dir / "candidate_generator_registry.json", candidate_registry)
    _validate_candidate_registry_index(
        candidate_registry,
        source_registry_sha256=_sha256_file(report_dir / "source_registry.json"),
        first_party_dir=first_party_candidate_dir,
        statistical_dir=statistical_candidate_dir,
        contextual_dir=contextual_candidate_dir,
    )
    generated_channels = first_party_manifest["counts"]["channels"]
    statistical_candidate_count = statistical_manifest["counts"]["candidate_count"]
    contextual_candidate_count = contextual_manifest["output_count"]
    total_candidate_count = (
        first_party_manifest["processed_count"]
        + statistical_candidate_count
        + contextual_candidate_count
    )
    candidate_manifest = _manifest(
        artifact="alignment_candidates",
        status="all_independent_candidate_channels_complete_uncalibrated",
        inputs={
            "gold_alignment_preparation_manifest": _sha256_file(
                report_dir / GOLD_PREPARATION_MANIFEST
            ),
            "gold_selection_panel": gold["panel_sha256"],
            "source_registry": _sha256_file(report_dir / "source_registry.json"),
            "first_party_manifest": _sha256_file(
                first_party_candidate_dir
                / "alignment_candidates.first_party.manifest.json"
            ),
            "statistical_manifest": _sha256_file(
                statistical_candidate_dir / "statistical_candidates.manifest.json"
            ),
            "contextual_manifest": _sha256_file(
                contextual_candidate_dir
                / "alignment_candidates.contextual.manifest.json"
            ),
            "ukrainian_token_inventory": token_inventory["sha256"],
            "fingerprint_selected_original_layer": selected_original_layer[
                "sha256"
            ],
        },
        outputs={
            "first_party_candidates/alignment_candidates.first_party.jsonl": first_party_manifest[
                "output_sha256"
            ]["alignment_candidates.first_party.jsonl"],
            "candidate_generator_registry.json": _sha256_file(
                report_dir / "candidate_generator_registry.json"
            ),
            "first_party_candidates/candidate_generator_registry.json": _sha256_file(
                first_party_candidate_dir / "candidate_generator_registry.json"
            ),
            "first_party_candidates/alignment_candidates.first_party.manifest.json": _sha256_file(
                first_party_candidate_dir
                / "alignment_candidates.first_party.manifest.json"
            ),
            "statistical_candidates/alignment_candidates.statistical.jsonl": statistical_manifest[
                "output_files"
            ]["alignment_candidates.statistical.jsonl"],
            "statistical_candidates/statistical_generator_registry.json": statistical_manifest[
                "output_files"
            ]["statistical_generator_registry.json"],
            "statistical_candidates/statistical_candidates.manifest.json": _sha256_file(
                statistical_candidate_dir / "statistical_candidates.manifest.json"
            ),
            "contextual_candidates/alignment_candidates.contextual.jsonl": contextual_manifest[
                "output_files"
            ]["alignment_candidates.contextual.jsonl"],
            "contextual_candidates/contextual_generator_registry.json": contextual_manifest[
                "output_files"
            ]["contextual_generator_registry.json"],
            "contextual_candidates/alignment_candidates.contextual.manifest.json": _sha256_file(
                contextual_candidate_dir
                / "alignment_candidates.contextual.manifest.json"
            ),
        },
        processed=total_candidate_count,
        skipped=(
            first_party_manifest["skipped_count"]
            + statistical_manifest["skipped_count"]
            + contextual_manifest["skipped_count"]
        ),
        errors=0,
        counts={
            "lexical_morphological": generated_channels[
                "local-uk-strong-description-lexical-v1"
            ]["emitted_candidates"],
            "russyn_ylt_bridge": generated_channels[
                "bridge-full-group-surface-v1"
            ]["emitted_candidates"],
            "bidirectional_statistical": statistical_candidate_count,
            "multilingual_contextual": contextual_candidate_count,
            "transliteration_named_entity": generated_channels[
                "transliteration-named-entity-v1"
            ]["emitted_candidates"],
            "legacy_zero_vote_baseline": generated_channels[
                "legacy-zero-vote-v1"
            ]["emitted_candidates"],
            "total_candidate_rows": total_candidate_count,
            "resolver_eligible": 0,
            "automatic_acceptance": 0,
        },
        notes=[
            "frozen panel predates these generators; no gold label was read and no score was tuned",
            "bridge rows retain complete manual groups and all non-positional OH surface ties, but one translation never proves a final link",
            "legacy has no current original IDs and vote weight zero",
            "transliteration and local Ukrainian description matches are uncalibrated direct-OH candidate features",
            "bidirectional statistical candidates are leakage-free target-ref OOF and retain explicit fold provenance",
            "multilingual contextual candidates use the exact local-only snapshot/runtime and remain out-of-domain, uncalibrated evidence",
            "nearest/neighbor, proportional, position-only, verse-bag and majority-only generators are forbidden",
        ],
    )
    candidate_manifest["generated_channel_counts"] = generated_channels
    candidate_manifest["candidate_contract_version"] = first_party_manifest[
        "candidate_contract_version"
    ]
    candidate_manifest["statistical_contract_version"] = statistical_manifest[
        "statistical_contract_version"
    ]
    candidate_manifest["contextual_contract_version"] = contextual_manifest[
        "contextual_contract_version"
    ]
    candidate_manifest["subgenerator_manifests"] = {
        "first_party": first_party_manifest,
        "bidirectional_statistical": statistical_manifest,
        "multilingual_contextual": contextual_manifest,
    }
    candidate_manifest["automatic_acceptance"] = False
    candidate_manifest["calibration"] = "not_run"
    _write_json(report_dir / "alignment_candidates.manifest.json", candidate_manifest)

    strong_manifest = _manifest(
        artifact="strong_alignment",
        status="blocked_no_accepted_links",
        inputs={"candidate_manifest": _sha256_file(report_dir / "alignment_candidates.manifest.json"), "gold_manifest": _sha256_file(report_dir / "gold_alignment.manifest.json")},
        outputs={},
        processed=0,
        skipped=universe["count"],
        errors=0,
        counts={"A_auto": 0, "B_review": 0, "C_unresolved": 0, "accepted_hyperedges": 0, "null_links": 0, "top_k_alternatives": 0, "invalid_or_dangling_strong": 0},
        notes=["hypergraph resolver is not permitted to run without frozen gold calibration", "no Ukrainian markup artifact exists"],
    )
    _write_json(report_dir / "strong_alignment.manifest.json", strong_manifest)

    source_only_components = sum(meta["target_ref"] is None for meta in universe["original_meta"].values())
    textual_alternative_components = sum(
        meta["target_ref"] is not None
        and str(meta["reading_status"]).startswith(("alternative", "unresolved"))
        for meta in universe["original_meta"].values()
    )
    coverage = _seal_payload(
        {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "artifact": "strong_coverage",
            "status": "blocked_no_production_alignment",
            "accepted_strong_occurrences": 0,
            "accepted_surface_bindings": 0,
            "OT": {"accepted": 0, "books": {book: 0 for book in BOOKS[:39]}},
            "NT": {"accepted": 0, "books": {book: 0 for book in BOOKS[39:]}},
            "evidence_classes": {"A_auto": 0, "B_review": 0, "C_unresolved": 0},
            "original_accounting": {
                "total_components": universe["count"],
                "aligned": 0,
                "proven_omitted": 0,
                "grouped": 0,
                "textual_alternative_or_blocked": textual_alternative_components,
                "source_only_paratext_or_versification": source_only_components,
                "pending_unreviewed": universe["count"] - textual_alternative_components - source_only_components,
            },
            "ukrainian_accounting": {
                "total_surface_tokens": token_inventory["count"],
                "aligned": 0,
                "proven_translation_addition_or_function_token": 0,
                "pending_unreviewed": token_inventory["count"],
            },
            "legacy_rejected_baseline": {"strong_occurrences": 440280, "surface_bindings": 399645, "duplicate_original_occurrences": 1457, "automatic_vote_weight": 0},
            "calibration": {"method": "95% one-sided Wilson", "required_lower_bound": 0.995, "status": "not_run", "support": 0, "correct": 0, "lower_bound": None},
            "processed_count": 0,
            "skipped_count": universe["count"],
            "error_count": 0,
            "input_sha256": {"strong_alignment_manifest": _sha256_file(report_dir / "strong_alignment.manifest.json")},
            "output_sha256": {},
            "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
        }
    )
    _write_json(report_dir / "strong_coverage_report.json", coverage)
    preservation = _seal_payload(_plain_preservation(rows))
    _write_json(report_dir / "plain_text_preservation_report.json", preservation)

    independence = _seal_payload(
        {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "artifact": "evidence_independence",
            "status": "audited_no_pseudoconsensus",
            "channels": [
                {"id": "TAHOT_TAGNT", "role": "primary original token universe", "independent_vote": True, "dependencies": ["STEPBible"]},
                {"id": "RUSSYN", "role": "manual bridge", "independent_vote": True, "dependencies": ["Clear tooling", "WLCM/SBLGNT"]},
                {"id": "YLT", "role": "manual bridge", "independent_vote": True, "dependencies": ["Clear tooling", "WLCM/SBLGNT transfer"]},
                {"id": "OSHB_UXLC_UGNT", "role": "consumed native-token original controls", "independent_vote": False, "dependencies": ["OSHB and UXLC share WLC lineage with TAHOT; UGNT is contextual control only"], "control_tokens": controls["count"], "crosswalk_sha256": controls["crosswalk_sha256"]},
                {"id": "owner_local_uk_greek_descs", "role": "SHA-locked Ukrainian lexical context", "independent_vote": False, "vote_weight": 0, "dependencies": ["first-party compiled project data"]},
                {"id": "owner_local_lxx_tr", "role": "SHA-locked LXX/TR diagnostic control", "independent_vote": False, "vote_weight": 0, "dependencies": ["compiled stage-1/2 source chain; restrictive OT terms prevent derived-corpus copying"]},
                {"id": "owner_local_kjv", "role": "SHA-locked KJV diagnostic control", "independent_vote": False, "vote_weight": 0, "dependencies": ["CrossWire/eBible KJV chain"]},
                {"id": "oh1988_author_printed_notes", "role": "exact-edition author footnote corroboration and manual textual-review evidence", "independent_vote": False, "vote_weight": 0, "alignment_input_allowed": False, "dependencies": ["exact OH1988 scan", "stage-5 footnote projection", "immutable stage-6 comments"], "processed_count": author_comments["processed_count"], "output_sha256": author_comments["output_sha256"][AUTHOR_COMMENT_OUTPUT_NAME]},
                {"id": "legacy_experiment", "role": "descriptive rejected baseline", "independent_vote": False, "vote_weight": 0, "dependencies": ["position and global corpus leakage"]},
                {"id": STATISTICAL_GENERATOR_ID, "role": "bidirectional target-ref out-of-fold statistical candidate channel", "independent_vote": False, "vote_weight": 0, "dependencies": ["selected STEP original layer", "stage-6 OH1988 target", "first-party IBM1 implementation"], "candidate_count": statistical_candidate_count, "resolver_eligible": False},
                {"id": CONTEXTUAL_GENERATOR_ID, "role": "pinned multilingual contextual candidate channel", "independent_vote": False, "vote_weight": 0, "dependencies": ["selected STEP original layer", "stage-6 OH1988 target", "awesome-align-with-co snapshot"], "candidate_count": contextual_candidate_count, "resolver_eligible": False},
            ],
            "prohibited_sources_used": [],
            "BSB_MACULA_used": False,
            "pseudo_consensus_count": 0,
            "processed_count": 11,
            "skipped_count": 0,
            "error_count": 0,
            "input_sha256": {"source_registry": _sha256_file(report_dir / "source_registry.json"), "bridges": bridges["sha256"], "original_control_crosswalk": controls["crosswalk_sha256"], "author_comment_evidence": author_comments["output_sha256"][AUTHOR_COMMENT_OUTPUT_NAME], "alignment_candidates_manifest": _sha256_file(report_dir / "alignment_candidates.manifest.json")},
            "output_sha256": {},
            "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
        }
    )
    _write_json(report_dir / "evidence_independence_report.json", independence)

    # Legacy counterexamples are a separate rejected-baseline evidence layer.
    # A finalized gold artifact contains hyperedges/accounting rows, so it must
    # never be parsed as the old negative-edge schema or become the source of
    # these permanent rejection overrides.
    annotation_rows = _legacy_negative_annotations_for_overrides(gold)
    overrides: list[dict[str, Any]] = [
        {
            "schema_version": SCHEMA_VERSION,
            "contract_version": CONTRACT_VERSION,
            "override_id": "uk7-reject-current-main-ylt-nt-alias",
            "decision": "reject_source_bridge",
            "stable_original_ids": [],
            "stable_oh1988_token_ids": [],
            "strong_raw": [],
            "strong_normalized": [],
            "evidence": [{"kind": "record_by_record_source_audit", "digest": _sha256_file(CLEAR / "data/eng/alignments/YLT/SBLGNT-YLT-manual.json")}],
            "rationale": "current main aliases NA27 positions as SBLGNT and produces thousands of lexical mismatches",
            "reviewer": "source_audit_agent",
            "pass": 1,
            "input_digests": {"source_registry": _sha256_file(report_dir / "source_registry.json")},
            "supersedes": None,
            "stale": False,
        }
    ]
    for row in annotation_rows:
        overrides.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "override_id": "uk7-" + row["annotation_id"],
                "decision": "reject_legacy_link",
                "stable_original_ids": row["original"]["universe_token_ids"],
                "legacy_source_token_id": row["original"]["legacy_source_token_id"],
                "stable_oh1988_token_ids": row["target"]["token_ids"],
                "strong_raw": row["original"]["strong_raw"],
                "strong_normalized": row["original"]["strong_classic"],
                "evidence": row["evidence"],
                "rationale": row["evidence"][0]["rationale"],
                "reviewer": "gold_audit_agent",
                "pass": 1,
                "input_digests": row["input_sha256"],
                "supersedes": None,
                "stale": False,
            }
        )
    for locus in fingerprint["loci"]:
        resolution = locus.get("manual_textual_resolution")
        if not resolution:
            continue
        overrides.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "override_id": "uk7-textual-"
                + locus["locus"].lower().replace(".", "-"),
                "decision": resolution["status"],
                "stable_original_ids": resolution[
                    "selected_original_token_ids"
                ],
                "textual_alternative_member_ids": resolution[
                    "candidate_original_token_ids"
                ],
                "excluded_lexical_candidate_ids": resolution[
                    "excluded_lexical_candidate_ids"
                ],
                "stable_oh1988_token_ids": [
                    resolution["target_span"]["token_id"]
                ],
                "strong_raw": resolution["rendered_strong"],
                "strong_normalized": resolution["rendered_strong"],
                "evidence": [
                    {
                        "kind": "two_pass_post_candidate_textual_locus_review",
                        "candidate_layer_status": resolution[
                            "candidate_layer_status"
                        ],
                        "target_span": resolution["target_span"],
                        "review": resolution["review"],
                    }
                ],
                "rationale": resolution["rationale"],
                "reviewer": "independent_textual_locus_audit+primary_agent_contract_review",
                "pass": 2,
                "input_digests": {
                    **resolution["input_sha256"],
                    "source_registry": _sha256_file(
                        report_dir / "source_registry.json"
                    ),
                    "fingerprint": _sha256_file(
                        report_dir / "textual_fingerprint.manifest.json"
                    ),
                    "fingerprint_selected_original_layer": (
                        selected_original_layer["sha256"]
                    ),
                },
                "supersedes": None,
                "stale": False,
            }
        )
    try:
        _validate_alignment_override_rows(
            overrides,
            stage6_rows=rows,
            work_dir=work_dir,
            report_dir=report_dir,
        )
    except ValueError as error:
        raise RuntimeError(f"Stage-7 alignment override validation failed: {error}") from error
    _write_jsonl(report_dir / "alignment_overrides.jsonl", overrides)

    manual_review = [
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-gold", "severity": "critical", "status": "unresolved", "scope": "gold", "evidence": {"selected_verses": gold["panel_count"], "projected_decisions": gold["projected_decisions"], "accepted_decisions": 0}, "decision_required": "complete at least 25,000 assignment/null labels with independent review"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-pass2", "severity": "critical", "status": "unresolved", "scope": "review", "evidence": {"pass_2_completed": 0}, "decision_required": "second blind pass and adjudication for critical/high"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-calibration", "severity": "critical", "status": "unresolved", "scope": "A_auto", "evidence": {"support": 0, "lower_bound": None}, "decision_required": "calibrate 95% one-sided Wilson lower bound >= 0.995"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-historical-documents", "severity": "info", "status": "resolved_research_complete", "scope": "historical_textual_fingerprint", "evidence": {"documents": ["exact OH1988 scan", "Ohiienko 1927 Methodology", "Ilarion 1963 Biblical Studies"], "front_back_matter_audited": True}, "decision_required": "none; only citation/paraphrase metadata is redistributed"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-exact-source-editions", "severity": "info", "status": "resolved_research_complete_fail_closed", "scope": "historical_textual_fingerprint", "evidence": {"status": fingerprint["status"], "unresolved_loci": fingerprint["unresolved_textual_locus_count"], "exact_hebrew_edition": None, "exact_greek_edition": None, "unchanged_1962_to_1988": None}, "decision_required": "none for historical research; unknown editions are recorded as limits and every affected locus remains locally fail-closed"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-nt-textual-readings", "severity": "high", "status": "unresolved", "scope": "original_universe", "evidence": {"unresolved_components": universe["counters"]["reading.alternative_unresolved_textual_reading"]}, "decision_required": "adjudicate traditional/critical source readings locus by locus"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-original-controls", "severity": "info", "status": "resolved_control_layer_built", "scope": "OSHB_UXLC_UGNT", "evidence": {"tokens": controls["count"], "crosswalk_sha256": controls["crosswalk_sha256"], "native_ref_sets_equal": controls["ref_audit"]}, "decision_required": "none for ingestion; unresolved variants remain separate blockers"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-ugnt-nonclassic", "severity": "high", "status": "unresolved", "scope": "UGNT_Strong_encoding", "evidence": {"nonclassic_or_invalid": controls["counters"]["UGNT.nonclassic_or_invalid"], "control_tokens_sha256": controls["token_sha256"]}, "decision_required": "adjudicate 210 nonzero UGNT encodings; never truncate them automatically"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-gold-strata", "severity": "critical", "status": "unresolved", "scope": "gold_stratification", "evidence": {"proven_strata": ["all_66_books", "OT", "NT", "genre", "rare/mid/frequent original Strong", "all stage-5 merge/split refs", "declared textual-fingerprint loci"], "pending": ["reorder", "omission/addition", "repetition", "named_entity", "particle", "compound", "multiple_Strong", "one-to-many", "many-to-one", "many-to-many"]}, "decision_required": "complete and freeze semantic link strata before candidate tuning"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-bridge-target-proof", "severity": "high", "status": "unresolved", "scope": "parallel_bridges", "evidence": {"records": bridges["count"], "coalescing": "pending"}, "decision_required": "prove RUSSYN/YLT target token to OH1988 spans independently and coalesce bridge decomposition"},
        {"schema_version": SCHEMA_VERSION, "contract_version": CONTRACT_VERSION, "review_id": "uk7-review-ylt-main", "severity": "high", "status": "resolved_rejected", "scope": "source_integrity", "evidence": {"source": "clear_ylt_nt_main_alias"}, "decision_required": "none; direct main alias remains prohibited"},
    ]
    for locus in fingerprint["loci"]:
        resolution = locus.get("manual_textual_resolution")
        if resolution:
            manual_review.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "contract_version": CONTRACT_VERSION,
                    "review_id": "uk7-review-textual-"
                    + locus["locus"].lower().replace(".", "-"),
                    "severity": resolution["severity"],
                    "status": resolution["status"],
                    "scope": "textual_locus",
                    "evidence": {
                        "locus": locus["locus"],
                        "candidate_layer_status": resolution[
                            "candidate_layer_status"
                        ],
                        "candidate_original_token_ids": resolution[
                            "candidate_original_token_ids"
                        ],
                        "selected_original_token_ids": resolution[
                            "selected_original_token_ids"
                        ],
                        "excluded_lexical_candidate_ids": resolution[
                            "excluded_lexical_candidate_ids"
                        ],
                        "target_span": resolution["target_span"],
                        "rendered_strong": resolution["rendered_strong"],
                        "review": resolution["review"],
                        "fingerprint": _sha256_file(
                            report_dir / "textual_fingerprint.manifest.json"
                        ),
                    },
                    "decision_required": "none; retain the reviewed post-candidate disposition and validate its gold/manual span link",
                }
            )
            continue
        if locus["locus"] not in fingerprint["unresolved_textual_loci"]:
            continue
        manual_review.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "review_id": "uk7-review-textual-"
                + locus["locus"].lower().replace(".", "-"),
                "severity": locus["severity"],
                "status": "unresolved",
                "scope": "textual_locus",
                "evidence": {
                    "locus": locus["locus"],
                    "selection_rule": locus["selection_rule"],
                    "fixed_original_token_ids": locus[
                        "selected_original_token_ids"
                    ],
                    "choice_groups": locus["unresolved_choice_groups"],
                    "supplemental_control_candidate_ids": locus[
                        "supplemental_control_candidate_ids"
                    ],
                    "fingerprint": _sha256_file(
                        report_dir / "textual_fingerprint.manifest.json"
                    ),
                },
                "decision_required": locus["unresolved_reason"],
            }
        )
    for author_evidence in _read_jsonl(
        author_comment_dir / AUTHOR_COMMENT_OUTPUT_NAME
    ):
        review_status = author_evidence["review_status"]
        review_contract = {
            "manual_textual_review_required": (
                "high",
                "author_printed_textual_variant_note",
                "adjudicate the exact-edition author variant note against "
                "the source apparatus and then review the OH1988 span/null; "
                "the note alone cannot assign Strong",
            ),
            "partial_original_form_match_requires_manual_scope": (
                "medium",
                "author_printed_original_form_note",
                "resolve the unmatched source-form mentions and the exact "
                "same-locus original scope before using this corroboration",
            ),
            "author_original_form_matches_multiple_selected_tokens": (
                "medium",
                "author_printed_original_form_note",
                "resolve repeated or otherwise ambiguous same-locus original "
                "matches without a positional tie-break",
            ),
            "explicit_original_claim_without_exact_selected_token_match": (
                "medium",
                "author_printed_original_form_note",
                "identify the source-qualified original component or retain "
                "the printed claim as unresolved context only",
            ),
        }.get(review_status)
        if review_contract is None:
            continue
        severity, scope, decision_required = review_contract
        manual_review.append(
            {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "review_id": "uk7-review-author-note-"
                + sha256_text(str(author_evidence["use_id"]))[:16],
                "severity": severity,
                "status": "unresolved",
                "scope": scope,
                "evidence": {
                    "evidence_id": author_evidence["evidence_id"],
                    "target_ref": author_evidence["target_ref"],
                    "footnote_id": author_evidence["footnote_id"],
                    "author_text_sha256": author_evidence["author_text_sha256"],
                    "source_page": author_evidence["source_page"],
                    "author_review_status": review_status,
                    "category_ids": author_evidence["categories"],
                    "exact_original_match_ids": [
                        row["original_token_id"]
                        for row in author_evidence["exact_original_form_matches"]
                    ],
                    "author_comment_evidence_sha256": author_comments[
                        "output_sha256"
                    ][AUTHOR_COMMENT_OUTPUT_NAME],
                },
                "decision_required": decision_required,
            }
        )
    _write_jsonl(report_dir / "manual_review.jsonl", manual_review)

    diff_rows = [
        {"diff_id": "uk7-diff-stage6-text", "scope": "target_text", "baseline": EXPECTED_STAGE6_TEXT_SHA256, "stage7": _sha256_file(STAGE6_TEXT), "status": "identical", "severity": "info", "evidence": "exact input reused without resynthesis"},
        {"diff_id": "uk7-diff-stage6-comments", "scope": "target_comments", "baseline": EXPECTED_STAGE6_COMMENT_SHA256, "stage7": _sha256_file(STAGE6_COMMENTS), "status": "identical", "severity": "info", "evidence": "exact input reused"},
        {"diff_id": "uk7-diff-author-notes", "scope": "textual_fingerprint_corroboration", "baseline": "printed notes preserved only as immutable stage-6 comments", "stage7": f"{author_comments['processed_count']} independently inventoried zero-vote evidence rows", "status": "analyzed_without_text_or_selection_mutation", "severity": "high", "evidence": author_comments["output_sha256"][AUTHOR_COMMENT_OUTPUT_NAME]},
        {"diff_id": "uk7-diff-step-parser", "scope": "original_universe", "baseline": "stage4 omitted canonical annotated refs", "stage7": str(universe["count"]), "status": "reparsed_raw", "severity": "high", "evidence": universe["sha256"]},
        {"diff_id": "uk7-diff-original-controls", "scope": "original_controls", "baseline": "stage4 normalized controls with colliding token IDs", "stage7": f"{controls['count']} source-qualified raw control tokens", "status": "native_token_crosswalk_built_fail_closed", "severity": "high", "evidence": controls["crosswalk_sha256"]},
        {"diff_id": "uk7-diff-ylt-nt", "scope": "bridge", "baseline": "current main positional alias", "stage7": "tagged v0.1.0 SBL transfer with partial token evidence", "status": "legacy_alias_rejected", "severity": "critical", "evidence": _sha256_file(CLEAR_V010 / "data/alignments/eng/YLT/SBLGNT-YLT-manual.json")},
        {"diff_id": "uk7-diff-legacy", "scope": "alignment", "baseline": "440280 occurrences / 399645 bindings", "stage7": "0 accepted production links", "status": "rejected_zero_vote", "severity": "critical", "evidence": _sha256_file(LEGACY_REPORT / "experiment_snapshot.manifest.json")},
        {"diff_id": "uk7-diff-gold", "scope": "gold", "baseline": "minimum 2000 verses / 25000 decisions", "stage7": f"{gold['panel_count']} verses / 0 accepted decisions", "status": "blocked", "severity": "critical", "evidence": _sha256_file(report_dir / "gold_alignment.manifest.json")},
    ]
    _write_source_diff(report_dir / "source_diff.csv", diff_rows)

    unresolved_critical_high = sum(row["status"] == "unresolved" and row["severity"] in {"critical", "high"} for row in manual_review)
    summary = {
        "status": "blocked_before_gold_and_alignment_acceptance",
        "target_count": len(rows),
        "ukrainian_token_count": token_inventory["count"],
        "original_token_count": universe["count"],
        "alternative_candidate_count": universe["alternative_count"],
        "original_control_token_count": controls["count"],
        "original_control_resolved_count": sum(
            value
            for key, value in controls["counters"].items()
            if key.startswith("crosswalk.resolved_")
        ),
        "original_control_unresolved_count": sum(
            value
            for key, value in controls["counters"].items()
            if key.startswith("crosswalk.unresolved_")
            or key == "crosswalk.service_not_crosswalked"
        ),
        "original_ref_count": universe["ref_count"],
        "fingerprint_locus_count": len(fingerprint["loci"]),
        "unresolved_textual_locus_count": fingerprint[
            "unresolved_textual_locus_count"
        ],
        "fingerprint_resolved_locus_count": len(fingerprint["loci"])
        - fingerprint["unresolved_textual_locus_count"],
        "manual_textual_resolution_count": fingerprint[
            "post_candidate_manual_textual_resolution_count"
        ],
        "global_unresolved_source_apparatus_ref_count": fingerprint[
            "global_unresolved_source_apparatus_ref_count"
        ],
        "unresolved_textual_component_count": fingerprint[
            "unresolved_textual_component_count"
        ],
        "bridge_record_count": bridges["count"],
        "bridge_counts": dict(bridge_counts),
        "lexeme_count": lexemes["count"],
        "author_comment_evidence_count": author_comments["processed_count"],
        "author_comment_definition_count": author_comments["counts"][
            "definition_count"
        ],
        "author_comment_target_ref_count": author_comments["counts"][
            "target_ref_count"
        ],
        "author_comment_textual_variant_count": author_comments["counts"].get(
            "category.textual_variant_claim", 0
        ),
        "author_comment_category_counts": {
            key.removeprefix("category."): value
            for key, value in sorted(author_comments["counts"].items())
            if key.startswith("category.")
        },
        "author_comment_language_counts": {
            key.removeprefix("language."): value
            for key, value in sorted(author_comments["counts"].items())
            if key.startswith("language.")
        },
        "author_comment_review_status_counts": {
            key.removeprefix("review."): value
            for key, value in sorted(author_comments["counts"].items())
            if key.startswith("review.")
        },
        "author_comment_exact_original_match_count": author_comments["counts"].get(
            "exact_original_matches", 0
        ),
        "author_comment_unmatched_source_form_count": author_comments["counts"].get(
            "unmatched_transliteration_mentions", 0
        )
        + author_comments["counts"].get(
            "unmatched_original_script_mentions", 0
        ),
        "author_comment_actionable_manual_review_count": sum(
            author_comments["counts"].get(f"review.{status}", 0)
            for status in (
                "manual_textual_review_required",
                "partial_original_form_match_requires_manual_scope",
                "author_original_form_matches_multiple_selected_tokens",
                "explicit_original_claim_without_exact_selected_token_match",
            )
        ),
        "gold_panel_verses": gold["panel_count"],
        "gold_projected_decisions": gold["projected_decisions"],
        "negative_annotations": gold["legacy_negative_annotation_count"],
        "candidate_count": total_candidate_count,
        "candidate_counts": {
            "first_party": first_party_manifest["processed_count"],
            "bidirectional_statistical": statistical_candidate_count,
            "multilingual_contextual": contextual_candidate_count,
        },
        "accepted_links": 0,
        "unresolved_critical_high": unresolved_critical_high,
    }
    (report_dir / "report.ru.md").write_text(_report_ru(summary), encoding="utf-8", newline="\n")
    (report_dir / "validation_log.md").write_text(_validation_log(summary), encoding="utf-8", newline="\n")
    _write_json(report_dir / "generation_summary.json", _seal_payload({
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "artifact": "generation_summary",
        **summary,
        "processed_count": len(rows),
        "skipped_count": universe["count"],
        "error_count": 0,
        "input_sha256": {"stage6_text": EXPECTED_STAGE6_TEXT_SHA256},
        "output_sha256": {},
        "serialization": "UTF-8 JSON; source codepoints preserved; sorted keys, compact separators, LF",
    }))
    _write_artifact_inventory(report_dir, work_dir)
    return summary


REQUIRED_REPORTS = (
    "source_registry.json",
    "textual_fingerprint.manifest.json",
    "author_comment_evidence.manifest.json",
    "original_token_universe.manifest.json",
    "parallel_bridge_alignment.manifest.json",
    "ukrainian_token_inventory.manifest.json",
    "ukrainian_lexeme_strong_ledger.manifest.json",
    "gold_alignment.annotations.jsonl",
    GOLD_PREPARATION_MANIFEST,
    "gold_alignment.manifest.json",
    "candidate_generator_registry.json",
    "alignment_candidates.manifest.json",
    "strong_alignment.manifest.json",
    "alignment_overrides.jsonl",
    "strong_coverage_report.json",
    "plain_text_preservation_report.json",
    "evidence_independence_report.json",
    "manual_review.jsonl",
    "source_diff.csv",
    "report.ru.md",
    "validation_log.md",
    "generation_summary.json",
    "artifact_inventory.manifest.json",
)


def verify_existing(*, work_dir: Path = WORK, report_dir: Path = REPORT) -> dict[str, Any]:
    stage6_rows, _stage6_by_ref = _stage6_rows()
    missing = [name for name in REQUIRED_REPORTS if not (report_dir / name).is_file()]
    if missing:
        raise RuntimeError(f"Missing stage-7 reports: {missing}")
    expected_source_registry = _seal_payload(_source_registry())
    if _read_json(report_dir / "source_registry.json") != expected_source_registry:
        raise RuntimeError("Stage-7 source registry is stale or tampered")
    # Validate the self-contained finalized-gold lock before opening any
    # mutable/ignored work artifact.  A tampered review lock must fail for its
    # own reason even when a diagnostic caller supplied only a minimal work
    # directory.
    finalized_gold_lock = validated_finalized_gold_lock(report_dir)
    author_comment_inputs = {
        "footnote_definitions": EXPECTED_STAGE6_FOOTNOTE_DEFINITIONS_SHA256,
        "footnote_uses": EXPECTED_STAGE6_FOOTNOTE_USES_SHA256,
        "heading_footnotes": EXPECTED_STAGE6_HEADING_FOOTNOTES_SHA256,
        "stage6_target_comments": EXPECTED_STAGE6_COMMENT_SHA256,
        "ukrainian_token_inventory": _sha256_file(
            work_dir / "ukrainian_token_inventory.jsonl"
        ),
        "fingerprint_selected_original_layer": _sha256_file(
            work_dir / "fingerprint_selected_original_layer.jsonl"
        ),
    }
    author_comment_manifest = validate_author_comment_evidence_bundle(
        output_dir=work_dir / "author_comment_evidence",
        expected_input_sha256=author_comment_inputs,
    )
    expected_author_comment_report = dict(author_comment_manifest)
    expected_author_comment_report["output_sha256"] = {
        f"author_comment_evidence/{AUTHOR_COMMENT_OUTPUT_NAME}": author_comment_manifest[
            "output_sha256"
        ][AUTHOR_COMMENT_OUTPUT_NAME]
    }
    expected_author_comment_report["license_provenance"] = {
        "source_id": "commons_ohienko_1988_scan",
        "exact_scan_sha256": "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "derivation": "exact stage-4/5/6 footnote extraction and projection; comments are not aligner target text",
        "source_registry_sha256": _sha256_file(
            report_dir / "source_registry.json"
        ),
    }
    if _read_json(
        report_dir / "author_comment_evidence.manifest.json"
    ) != expected_author_comment_report:
        raise RuntimeError("Author-comment evidence report is stale or tampered")
    try:
        _validate_alignment_override_rows(
            list(_read_jsonl(report_dir / "alignment_overrides.jsonl")),
            stage6_rows=stage6_rows,
            work_dir=work_dir,
            report_dir=report_dir,
        )
    except ValueError as error:
        raise RuntimeError(f"Stage-7 alignment override validation failed: {error}") from error
    if finalized_gold_lock is not None:
        _validate_finalized_gold_current_inputs(
            finalized_gold_lock,
            {
                "stage6_text": EXPECTED_STAGE6_TEXT_SHA256,
                "stage6_comments": EXPECTED_STAGE6_COMMENT_SHA256,
                "source_registry": _sha256_file(
                    report_dir / "source_registry.json"
                ),
                "original_token_universe": _sha256_file(
                    work_dir / "original_token_universe.jsonl"
                ),
                "fingerprint_selected_original_layer": _sha256_file(
                    work_dir / "fingerprint_selected_original_layer.jsonl"
                ),
                "gold_selected_original_layer": _sha256_file(
                    work_dir / "gold_selected_original_layer.jsonl"
                ),
                "ukrainian_token_inventory": _sha256_file(
                    work_dir / "ukrainian_token_inventory.jsonl"
                ),
                "original_token_universe_manifest": _sha256_file(
                    report_dir / "original_token_universe.manifest.json"
                ),
                "gold_alignment_preparation_manifest": _sha256_file(
                    report_dir / GOLD_PREPARATION_MANIFEST
                ),
                "gold_selection_panel": _sha256_file(
                    work_dir / "gold_selection_panel.jsonl"
                ),
                "gold_annotation_workbench": _sha256_file(
                    work_dir / "gold_annotation_workbench.jsonl"
                ),
            },
        )
    summary = _read_json(report_dir / "generation_summary.json")
    if summary["status"] != "blocked_before_gold_and_alignment_acceptance":
        raise RuntimeError("Unexpected stage-7 status")
    work_outputs = {
        "ukrainian_token_inventory.jsonl": "ukrainian_token_inventory.manifest.json",
        "original_token_universe.jsonl": "original_token_universe.manifest.json",
        "original_parent_inventory.jsonl": "original_token_universe.manifest.json",
        "original_alternative_inventory.jsonl": "original_token_universe.manifest.json",
        "original_control_tokens.jsonl": "original_token_universe.manifest.json",
        "original_control_crosswalk.jsonl": "original_token_universe.manifest.json",
        "fingerprint_selected_original_layer.jsonl": "original_token_universe.manifest.json",
        "author_comment_evidence/author_comment_evidence.jsonl": "author_comment_evidence.manifest.json",
        "parallel_bridge_alignment.jsonl": "parallel_bridge_alignment.manifest.json",
        "ukrainian_lexeme_strong_ledger.jsonl": "ukrainian_lexeme_strong_ledger.manifest.json",
        "gold_selection_panel.jsonl": GOLD_PREPARATION_MANIFEST,
        "gold_annotation_workbench.jsonl": GOLD_PREPARATION_MANIFEST,
        "gold_selected_original_layer.jsonl": GOLD_PREPARATION_MANIFEST,
        "first_party_candidates/alignment_candidates.first_party.jsonl": "alignment_candidates.manifest.json",
        "first_party_candidates/alignment_candidates.first_party.manifest.json": "alignment_candidates.manifest.json",
        "first_party_candidates/candidate_generator_registry.json": "alignment_candidates.manifest.json",
        "statistical_candidates/alignment_candidates.statistical.jsonl": "alignment_candidates.manifest.json",
        "statistical_candidates/statistical_generator_registry.json": "alignment_candidates.manifest.json",
        "statistical_candidates/statistical_candidates.manifest.json": "alignment_candidates.manifest.json",
        "contextual_candidates/alignment_candidates.contextual.jsonl": "alignment_candidates.manifest.json",
        "contextual_candidates/contextual_generator_registry.json": "alignment_candidates.manifest.json",
        "contextual_candidates/alignment_candidates.contextual.manifest.json": "alignment_candidates.manifest.json",
    }
    for filename, manifest_name in work_outputs.items():
        path = work_dir / filename
        if not path.is_file():
            raise RuntimeError(f"Missing ignored work output: {filename}")
        manifest = _read_json(report_dir / manifest_name)
        expected = manifest["output_sha256"].get(filename)
        if not expected:
            raise RuntimeError(f"Work output lacks a required digest: {filename}")
        if _sha256_file(path) != expected:
            raise RuntimeError(f"Work output digest mismatch: {filename}")

    candidate_manifest = _read_json(report_dir / "alignment_candidates.manifest.json")
    source_registry_sha256 = _sha256_file(report_dir / "source_registry.json")
    selected_original_sha256 = _sha256_file(
        work_dir / "fingerprint_selected_original_layer.jsonl"
    )
    token_inventory_sha256 = _sha256_file(
        work_dir / "ukrainian_token_inventory.jsonl"
    )
    first_party_expected_inputs = {
        "ukrainian_token_inventory": token_inventory_sha256,
        "original_token_universe": selected_original_sha256,
        "parallel_bridge_alignment": _sha256_file(
            work_dir / "parallel_bridge_alignment.jsonl"
        ),
        "legacy_alignment": _sha256_file(
            LEGACY_WORK / "strong_aligned_text.jsonl"
        ),
        "ukrainian_greek_descriptions": _sha256_file(
            LOCAL_DB / "revelation_uk.sqlite"
        ),
        "source_registry": source_registry_sha256,
        **{
            f"bridge_target_{bundle.family}_{bundle.scope}": _sha256_file(
                bundle.path
            )
            for bundle in CANDIDATE_BRIDGE_TARGET_BUNDLES
        },
    }
    _validate_first_party_candidate_bundle(
        work_dir / "first_party_candidates",
        expected_inputs=first_party_expected_inputs,
    )
    first_party_submanifest = _read_json(
        work_dir
        / "first_party_candidates/alignment_candidates.first_party.manifest.json"
    )
    statistical_submanifest = _validate_statistical_candidate_bundle(
        work_dir / "statistical_candidates",
        expected_inputs={
            "ukrainian_token_inventory": token_inventory_sha256,
            "original_token_universe": selected_original_sha256,
            "source_registry": source_registry_sha256,
        },
    )
    contextual_submanifest = _validate_contextual_candidate_bundle(
        work_dir / "contextual_candidates",
        expected_inputs={
            "token_inventory": token_inventory_sha256,
            "original_token_universe": selected_original_sha256,
            "source_registry": source_registry_sha256,
            "model_snapshot_contract": MODEL_SNAPSHOT_CONTRACT_SHA256,
            "runtime_install_report": _sha256_file(
                CONTEXTUAL_RUNTIME_INSTALL_REPORT
            ),
        },
    )
    expected_candidate_inputs = {
        "gold_alignment_preparation_manifest": _sha256_file(
            report_dir / GOLD_PREPARATION_MANIFEST
        ),
        "gold_selection_panel": _sha256_file(
            work_dir / "gold_selection_panel.jsonl"
        ),
        "source_registry": source_registry_sha256,
        "first_party_manifest": _sha256_file(
            work_dir
            / "first_party_candidates/alignment_candidates.first_party.manifest.json"
        ),
        "statistical_manifest": _sha256_file(
            work_dir / "statistical_candidates/statistical_candidates.manifest.json"
        ),
        "contextual_manifest": _sha256_file(
            work_dir
            / "contextual_candidates/alignment_candidates.contextual.manifest.json"
        ),
        "ukrainian_token_inventory": token_inventory_sha256,
        "fingerprint_selected_original_layer": selected_original_sha256,
    }
    if candidate_manifest.get("input_sha256") != dict(
        sorted(expected_candidate_inputs.items())
    ):
        raise RuntimeError("Aggregate candidate input provenance drifted")
    if candidate_manifest["counts"]["total_candidate_rows"] != (
        first_party_submanifest["processed_count"]
        + statistical_submanifest["counts"]["candidate_count"]
        + contextual_submanifest["output_count"]
    ):
        raise RuntimeError("Aggregate candidate accounting drifted")
    _validate_candidate_registry_index(
        _read_json(report_dir / "candidate_generator_registry.json"),
        source_registry_sha256=source_registry_sha256,
        first_party_dir=work_dir / "first_party_candidates",
        statistical_dir=work_dir / "statistical_candidates",
        contextual_dir=work_dir / "contextual_candidates",
    )
    preservation = _read_json(report_dir / "plain_text_preservation_report.json")
    if not preservation["exact_key_equality"] or preservation["plain_text_mismatch_count"] or preservation["comment_mismatch_count"]:
        raise RuntimeError("Stage-6 preservation invariant failed")
    if _read_json(report_dir / "strong_coverage_report.json")["accepted_strong_occurrences"] != 0:
        raise RuntimeError("Blocked stage unexpectedly emitted Strong occurrences")
    inventory = _read_json(report_dir / "artifact_inventory.manifest.json")
    for entry in inventory["entries"]:
        root = report_dir if entry["root"] == "report" else work_dir
        path = root / entry["path"]
        if not path.is_file() or _sha256_file(path) != entry["sha256"]:
            raise RuntimeError(f"Artifact inventory mismatch: {entry['root']}/{entry['path']}")
    return summary


def verify_determinism() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="uk7-a-") as left_name, tempfile.TemporaryDirectory(prefix="uk7-b-") as right_name:
        left = Path(left_name)
        right = Path(right_name)
        candidate_directories = (
            "first_party_candidates",
            "statistical_candidates",
            "contextual_candidates",
        )
        missing_candidates = [
            name for name in candidate_directories if not (WORK / name).is_dir()
        ]
        if missing_candidates:
            raise RuntimeError(
                "Determinism verification requires separately generated and "
                f"validated candidate bundles: {missing_candidates}"
            )
        for root in (left, right):
            (root / "work").mkdir(parents=True)
            for name in candidate_directories:
                shutil.copytree(WORK / name, root / "work" / name)
        finalized_gold_lock = REPORT / "gold_alignment.finalized.lock.json"
        if finalized_gold_lock.is_file():
            for root in (left, right):
                (root / "report").mkdir(parents=True)
                for name in (
                    "gold_alignment.finalized.lock.json",
                    "gold_alignment.annotations.jsonl",
                    "gold_alignment.manifest.json",
                    GOLD_PREPARATION_MANIFEST,
                ):
                    shutil.copyfile(REPORT / name, root / "report" / name)
                for name in (
                    "gold_selection_panel.jsonl",
                    "gold_annotation_workbench.jsonl",
                    "gold_selected_original_layer.jsonl",
                ):
                    shutil.copyfile(WORK / name, root / "work" / name)
        generate(work_dir=left / "work", report_dir=left / "report")
        generate(work_dir=right / "work", report_dir=right / "report")
        left_files = {path.relative_to(left).as_posix(): _sha256_file(path) for path in left.rglob("*") if path.is_file()}
        right_files = {path.relative_to(right).as_posix(): _sha256_file(path) for path in right.rglob("*") if path.is_file()}
        if left_files != right_files:
            differing = sorted(set(left_files) | set(right_files))
            raise RuntimeError(f"Stage-7 generation is not deterministic: {differing[:20]}")
        return {"status": "deterministic", "file_count": len(left_files), "aggregate_sha256": sha256_text(stable_json(left_files))}


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify existing outputs")
    mode.add_argument("--determinism", action="store_true", help="generate twice in temporary directories and compare")
    mode.add_argument(
        "--prepare-candidate-inputs",
        action="store_true",
        help="stop after freezing exact candidate inputs and the answer-free gold workbench",
    )
    parser.add_argument("--work-dir", type=Path, default=WORK)
    parser.add_argument("--report-dir", type=Path, default=REPORT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.determinism:
        print(stable_json(verify_determinism()))
    elif args.check:
        print(stable_json(verify_existing(work_dir=args.work_dir, report_dir=args.report_dir)))
    else:
        print(
            stable_json(
                generate(
                    work_dir=args.work_dir,
                    report_dir=args.report_dir,
                    stop_after_candidate_input_preparation=args.prepare_candidate_inputs,
                )
            )
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
