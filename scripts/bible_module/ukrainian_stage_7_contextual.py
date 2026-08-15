"""Fail-closed multilingual contextual candidates for Ukrainian stage 7.

This module implements one candidate feature channel.  It never accepts a
Strong alignment and it is deliberately not imported by the main stage-7
generator until the channel has been independently reviewed.  Production
inference requires an exact, local, digest-verified AWESOME-align model
snapshot; there is no network fallback and no substitute/mock inference.

The extraction follows the pinned model card: hidden layer 8, source-to-target
and target-to-source softmax, and their strict mutual intersection above
``1e-3``.  Word-level hyperedges are connected components of the resulting
subword links.  Token order supplies transformer sequence context only: no
position distance, nearest-neighbour tie-break, verse-bag transfer, frequency,
or translation bridge is used to create a link.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict, deque
import csv
from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import sys
import time
from typing import Any, Callable, Iterator, Mapping, Protocol, Sequence

from scripts.bible_module.ukrainian_stage_7_candidates import (
    CandidateContext,
    _attach_target_spans,
    _base_candidate,
    _relation,
    _strongs_for_originals,
    load_context,
    validate_candidate,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    stable_json,
)


CONTEXTUAL_CONTRACT_VERSION = "ukrainian-stage-7-contextual-candidate-v1"
CONTEXTUAL_GENERATOR_ID = "awesome-align-multilingual-contextual-v1"

MODEL_ID = "aneuraz/awesome-align-with-co"
MODEL_REVISION = "777756717e1fa9556e304d4d5db173ee386b9c16"
MODEL_LICENSE = "BSD-3-Clause"
MODEL_REPOSITORY_URL = "https://huggingface.co/aneuraz/awesome-align-with-co"
MODEL_REVISION_URL = f"{MODEL_REPOSITORY_URL}/tree/{MODEL_REVISION}"
MODEL_LICENSE_EVIDENCE_URL = (
    f"{MODEL_REPOSITORY_URL}/blob/{MODEL_REVISION}/README.md"
)
UPSTREAM_IMPLEMENTATION_URL = "https://github.com/neulab/awesome-align"
UPSTREAM_IMPLEMENTATION_LICENSE = "BSD-3-Clause"
UPSTREAM_PAPER_URL = "https://aclanthology.org/2021.eacl-main.181/"

ALIGN_LAYER = 8
MUTUAL_SOFTMAX_THRESHOLD = 0.001
MAX_MODEL_WORDPIECES = 510  # BERT's 512 positions minus [CLS] and [SEP].
EXPECTED_TARGET_REF_COUNT = 31_102

_SHA256_RE = re.compile(r"[0-9a-f]{64}")

# Exact Hugging Face repository snapshot metadata returned for MODEL_REVISION.
# ``pytorch_model.bin`` is an LFS object; its SHA is the LFS content SHA, not
# the Git pointer SHA.  Small-file SHA values were independently downloaded
# from the pinned ``resolve`` URLs and hashed as raw bytes.
MODEL_FILES: dict[str, dict[str, Any]] = {
    ".gitattributes": {
        "size": 1_173,
        "sha256": "983f034a5d3898b49e1c02cf4941beaf38849e8f01912ad6d8697e96270ee997",
    },
    "README.md": {
        "size": 3_170,
        "sha256": "bbb859a4fdcaf25accd623ca1d54f004d8a6ac9b9b0a9b385377fbdce20aa7f1",
    },
    "config.json": {
        "size": 1_190,
        "sha256": "3b691038d5c6691e45d7905e3f1ae25ef9bf6231410a222cb213c90d61f0f6aa",
    },
    "pytorch_model.bin": {
        "size": 1_086_292_375,
        "sha256": "9f9d19adbab07c9f5ec2d74fe5701a66c123919feb35d05fce29969b6a85adb9",
    },
    "special_tokens_map.json": {
        "size": 112,
        "sha256": "303df45a03609e4ead04bc3dc1536d0ab19b5358db685b6f3da123d05ec200e3",
    },
    "tokenizer_config.json": {
        "size": 40,
        "sha256": "ec70da9a619641c3b56e62cb949b8a07f2fdafdb8389b2c72649fb235a5580b3",
    },
    "vocab.txt": {
        "size": 995_526,
        "sha256": "fe0fda7c425b48c516fc8f160d594c8022a0808447475c1a7c6d6479763f310c",
    },
}

# Exact Windows/Python-3.12 runtime artifacts chosen for the owner's fixed
# machine.  Runtime inference additionally records the installed distribution
# RECORD digest, so a different wheel/build cannot be silently treated as the
# validated execution environment.
RUNTIME_PACKAGE_CONTRACTS: dict[str, dict[str, str]] = {
    "torch": {
        "version": "2.9.0",
        "license": "BSD-3-Clause",
        "artifact": "torch-2.9.0-cp312-cp312-win_amd64.whl",
        "artifact_sha256": "4582b162f541651f0cb184d3e291c05c2f556c7117c64a9873e2ee158d40062b",
        "artifact_url": (
            "https://files.pythonhosted.org/packages/66/11/"
            "c1c5ba6691cda6279087c35bd626536e4fd29521fe740abf5008377a9a02/"
            "torch-2.9.0-cp312-cp312-win_amd64.whl"
        ),
        "url": "https://pypi.org/project/torch/2.9.0/",
        "license_url": "https://github.com/pytorch/pytorch/blob/v2.9.0/LICENSE",
    },
    "transformers": {
        "version": "4.57.6",
        "license": "Apache-2.0",
        "artifact": "transformers-4.57.6-py3-none-any.whl",
        "artifact_sha256": "4c9e9de11333ddfe5114bc872c9f370509198acf0b87a832a0ab9458e2bd0550",
        "artifact_url": (
            "https://files.pythonhosted.org/packages/03/b8/"
            "e484ef633af3887baeeb4b6ad12743363af7cce68ae51e938e00aaa0529d/"
            "transformers-4.57.6-py3-none-any.whl"
        ),
        "url": "https://pypi.org/project/transformers/4.57.6/",
        "license_url": (
            "https://github.com/huggingface/transformers/blob/v4.57.6/LICENSE"
        ),
    },
    "huggingface-hub": {
        "version": "0.36.2",
        "license": "Apache-2.0",
        "artifact": "huggingface_hub-0.36.2-py3-none-any.whl",
        "artifact_sha256": "48f0c8eac16145dfce371e9d2d7772854a4f591bcb56c9cf548accf531d54270",
        "artifact_url": "https://files.pythonhosted.org/packages/a8/af/48ac8483240de756d2438c380746e7130d1c6f75802ef22f3c6d49982787/huggingface_hub-0.36.2-py3-none-any.whl",
        "url": "https://pypi.org/project/huggingface-hub/0.36.2/",
        "license_url": "https://github.com/huggingface/huggingface_hub/blob/v0.36.2/LICENSE",
    },
    "tokenizers": {
        "version": "0.22.2",
        "license": "Apache-2.0",
        "artifact": "tokenizers-0.22.2-cp39-abi3-win_amd64.whl",
        "artifact_sha256": "c9ea31edff2968b44a88f97d784c2f16dc0729b8b143ed004699ebca91f05c48",
        "artifact_url": "https://files.pythonhosted.org/packages/65/71/0670843133a43d43070abeb1949abfdef12a86d490bea9cd9e18e37c5ff7/tokenizers-0.22.2-cp39-abi3-win_amd64.whl",
        "url": "https://pypi.org/project/tokenizers/0.22.2/",
        "license_url": "https://github.com/huggingface/tokenizers/blob/v0.22.2/LICENSE",
    },
    "safetensors": {
        "version": "0.8.0",
        "license": "Apache-2.0",
        "artifact": "safetensors-0.8.0-cp310-abi3-win_amd64.whl",
        "artifact_sha256": "096ec1a98435df7beb08853bb5aa9081a84f23d0adc67ed1a0a10550f608373f",
        "artifact_url": "https://files.pythonhosted.org/packages/1b/6d/3fba214c1e5e0f69991677ec3bc17023f0421776975e1de0c682dca475e2/safetensors-0.8.0-cp310-abi3-win_amd64.whl",
        "url": "https://pypi.org/project/safetensors/0.8.0/",
        "license_url": "https://github.com/huggingface/safetensors/blob/v0.8.0/LICENSE",
    },
}

RUNTIME_INSTALL_REPORT_SHA256 = (
    "5c6047d4b9b8bceb779860bbbd0c3fe74f3539aeca492f68062c56740d6d5a2a"
)

# RECORD and METADATA digest locks cover the complete Python environment used
# by the local-only backend.  The four downloaded HF wheels are additionally
# pinned above by archive SHA and by the pip installation report.
RUNTIME_ENVIRONMENT_LOCKS: dict[str, dict[str, str]] = {
    "torch": {"version": "2.9.0", "record": "5d7235d13f807aa0340c631ee1de4d581d18ff7d205e9b43d367d7b0f7fa2996", "metadata": "977a43d37592986165d8ea2126b1c924d7195f863ec85b290c22785c96b6a683", "license": "BSD-3-Clause"},
    "transformers": {"version": "4.57.6", "record": "1cf8be5c43a4d9f40d27d682358333dbff249829a5332a66c6fdd25e3012999a", "metadata": "91601044a74fe02571a825356754dbbaa9e1d3e3dd3c2237254c15e903e421e3", "license": "Apache-2.0"},
    "huggingface-hub": {"version": "0.36.2", "record": "ad78cf5631b96f3eb3602a13469a5a79e1230e1f80ca877131f8905c157e179a", "metadata": "4dc2b0a3fb27bcba8b091f98bccff4b94369d269c9768aeaecd0b99d970665d9", "license": "Apache-2.0"},
    "tokenizers": {"version": "0.22.2", "record": "59cb1b72c40c376eb48ba3d2be7aed522b257bb1ab0d451c0e2dffad0a587d89", "metadata": "15a5ddaf489f592b77e0a934c0eeb46b51130a94064ca129232afdb0a3868efc", "license": "Apache-2.0"},
    "safetensors": {"version": "0.8.0", "record": "70546da2d572cbe73b36c91b30f6d3cf484362208e8b6a8323476364dbf2cea8", "metadata": "645be7b8d55e91534f991d144dc9e279581ea8dbea1a8c5b0be14e529d01e345", "license": "Apache-2.0"},
    "numpy": {"version": "2.0.2", "record": "49a8ac9a8f34a7197ed519fc1340d9b49ab200f80e1121f33369590414f8a3a4", "metadata": "0b1e601244cc69655bad407b02e8a160976ee7a1e3a2035836d3b3a6bbd0d5ce", "license": "BSD-3-Clause"},
    "packaging": {"version": "24.1", "record": "d46d8dc07d6ffaad0f1097c45b2178cd00397c7e10477400105119b19360448f", "metadata": "5f7a283b75a709fccd481aea42379f083d4f3801753365922e6b0732042515d9", "license": "Apache-2.0 OR BSD-2-Clause"},
    "PyYAML": {"version": "6.0.2", "record": "4ffd007a4dfde35a3865380892c2f838e1dd9ce6348c5d65aefc622898426272", "metadata": "f7ea1d141e6c7aee2918f704bfb13c8b2c4d179d7fb8a9da3468cb021cf696da", "license": "MIT"},
    "regex": {"version": "2024.9.11", "record": "60e4de7cfa5e338bf632986936f3c0acc2ab2d70397a6e7bf8c994fcae928263", "metadata": "14485598d4b18c63f8ec7c40c1eddd540a4d9ccb74f753f79bc3263ca76f49c7", "license": "Apache-2.0 AND CNRI-Python"},
    "requests": {"version": "2.32.3", "record": "357f7a5dd5ed60868f68a59f9a87fec0251a2ab57a67808aaefbd3d79e209ac4", "metadata": "658ee8454c1e2e76fb8c2127116f61156b3b22941b3559c00389dca70038581a", "license": "Apache-2.0"},
    "tqdm": {"version": "4.66.5", "record": "a7dbeac1fa529874b88f2100488dd7b45a1aa09e542a825ed1fe9378afaeecd4", "metadata": "39bc45fbe6ec7e76d009f93903e22c84eb186ec03ddc843a06468b99a4c93246", "license": "MPL-2.0 AND MIT"},
    "filelock": {"version": "3.25.0", "record": "48fe9ea902dd0daadce7ab72315ef78ac547110b57ae1609273175a1cc95b3b4", "metadata": "f74ce00f53d7adbf024d3a2b13f7d7b8459d9810764de210f738a4e740b8ba39", "license": "Unlicense"},
    "fsspec": {"version": "2025.12.0", "record": "80ef0e014bec839806547732e3f444019ee236b57a028f162cd363efbdf5417d", "metadata": "166d9b20c8a8d0d632d4474c7f1806ab8384da41399edd6a64368361b3ae0b43", "license": "BSD-3-Clause"},
    "typing-extensions": {"version": "4.15.0", "record": "5d2b9d87babf12084667cf9389051efe9b55ae913936601be7c9e05f08bfc09f", "metadata": "c138378fe8f18934ac99de060535c53ec6c13aeed65e94c32641da7ee3192a72", "license": "PSF-2.0"},
    "charset-normalizer": {"version": "3.4.0", "record": "dd774bfd5ad8b0664ca36472038dfdbcfc67bb0ac7d44c6b846bad983f024890", "metadata": "5866c45bd7a1876b29349c68d4ceac1061995a6b10fa88f60ec323576f73a26b", "license": "MIT"},
    "idna": {"version": "2.10", "record": "459b81beb04c9fa142c32671c25806f58739c870e36e5357c0c7e8f8953e97df", "metadata": "65609a4030637664afc79114ec2bfa3910bef4d510ea75e1d5e5f1dfcc927b8d", "license": "BSD-3-Clause"},
    "urllib3": {"version": "2.2.3", "record": "511615e61fd3eae07d9c662e1304f9d851875804e1e9a61ecc23049fc1bf24f3", "metadata": "369c8b318bbe42802640aea99a6828651baad073edfa57ff27dcc8b8218c44d6", "license": "MIT"},
    "certifi": {"version": "2024.8.30", "record": "805e572efa933535a0950c90461c6f77dbd3ac6485b1f8f4a029729e20911042", "metadata": "1a104745550de9ae19754804fcde709ae9097f2ba813e432225f18de27cd4013", "license": "MPL-2.0"},
    "colorama": {"version": "0.4.6", "record": "2de1747809a165c7c54a2fd115a569a061e6eedf56d5c6db3fe0dc8a2985562f", "metadata": "7baed29eb50c3b29bdb33ff84e3177bf1bc05784f7685ecdcaa4471c7dd810cc", "license": "BSD-3-Clause"},
}


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json(value: Any) -> str:
    return sha256(stable_json(value).encode("utf-8")).hexdigest()


MODEL_SNAPSHOT_CONTRACT_SHA256 = _sha256_json(
    {
        "model_id": MODEL_ID,
        "revision": MODEL_REVISION,
        "files": MODEL_FILES,
    }
)
_LOCKED_MODEL_SNAPSHOT_CONTRACT_SHA256 = (
    "1c6c17aca225480f6d04c1a838c814c03095a934b8f94612eefcbb0b34772df7"
)
if MODEL_SNAPSHOT_CONTRACT_SHA256 != _LOCKED_MODEL_SNAPSHOT_CONTRACT_SHA256:
    raise RuntimeError("Contextual model snapshot contract changed without review")


class ContextualRuntimeUnavailable(RuntimeError):
    """Raised when exact production inference prerequisites are unavailable."""


class ModelInputTooLong(ValueError):
    """Raised rather than truncating a verse and losing token evidence."""


@dataclass(frozen=True, slots=True)
class ContextualWordLink:
    """One model-observed mutual subword link mapped to two surface words."""

    original_word_index: int
    target_word_index: int
    original_subword_index: int
    target_subword_index: int
    original_subword: str
    target_subword: str
    source_to_target_probability: float
    target_to_source_probability: float
    dot_product: float


@dataclass(frozen=True, slots=True)
class ContextualObservation:
    """Complete token-level observation for one exact verse pair."""

    target_ref: str
    model_id: str
    model_revision: str
    model_snapshot_contract_sha256: str
    align_layer: int
    threshold: float
    original_wordpiece_count: int
    target_wordpiece_count: int
    original_sequence_sha256: str
    target_sequence_sha256: str
    links: tuple[ContextualWordLink, ...]


class ContextualEncoder(Protocol):
    """Small injectable boundary used by production and CC0 fixture encoders."""

    def align(
        self,
        *,
        target_ref: str,
        original_words: Sequence[str],
        target_words: Sequence[str],
    ) -> ContextualObservation:
        ...

    def runtime_registry(self) -> Mapping[str, Any]:
        ...


def validate_model_snapshot(
    snapshot_dir: Path,
    *,
    file_contract: Mapping[str, Mapping[str, Any]] = MODEL_FILES,
) -> dict[str, Any]:
    """Validate every required snapshot file; extra cache metadata is ignored."""

    errors: list[dict[str, Any]] = []
    checked: list[dict[str, Any]] = []
    for filename in sorted(file_contract):
        expected = file_contract[filename]
        path = snapshot_dir / filename
        if not path.is_file():
            errors.append({"file": filename, "error": "missing"})
            continue
        actual_size = path.stat().st_size
        actual_sha256 = _sha256_file(path)
        checked.append(
            {
                "file": filename,
                "size": actual_size,
                "sha256": actual_sha256,
            }
        )
        if actual_size != int(expected["size"]):
            errors.append(
                {
                    "file": filename,
                    "error": "size_mismatch",
                    "expected": int(expected["size"]),
                    "actual": actual_size,
                }
            )
        if actual_sha256 != str(expected["sha256"]):
            errors.append(
                {
                    "file": filename,
                    "error": "sha256_mismatch",
                    "expected": str(expected["sha256"]),
                    "actual": actual_sha256,
                }
            )
    if errors:
        raise ContextualRuntimeUnavailable(
            "Pinned contextual model snapshot is incomplete or changed: "
            + stable_json(errors)
        )
    return {
        "model_id": MODEL_ID,
        "revision": MODEL_REVISION,
        "snapshot_contract_sha256": MODEL_SNAPSHOT_CONTRACT_SHA256,
        "files": checked,
        "processed_count": len(checked),
        "skipped_count": 0,
        "error_count": 0,
    }


def _locate_distribution_record_file(
    distribution: metadata.Distribution, relative_path: str
) -> Path:
    """Resolve one installed RECORD member without weakening byte checks.

    ``pip install --target`` relocates Windows console launchers into the
    target directory's ``bin`` child, while the wheel RECORD retains an
    installation-scheme path such as ``../../bin/hf.exe``.  importlib resolves
    that path as though the target were a normal ``Lib/site-packages`` tree,
    which is not the layout of our pinned, project-local runtime.  Accept only
    this exact relocation shape as a fallback; the RECORD size and hash remain
    authoritative and are verified by the caller.
    """

    primary = Path(distribution.locate_file(relative_path))
    if primary.is_file():
        return primary
    parts = PurePosixPath(relative_path).parts
    if len(parts) == 4 and parts[:3] == ("..", "..", "bin"):
        target_root = Path(distribution.locate_file(""))
        relocated = target_root / "bin" / parts[3]
        if relocated.is_file():
            return relocated
    return primary


def _distribution_record(name: str) -> dict[str, Any]:
    try:
        distribution = metadata.distribution(name)
    except metadata.PackageNotFoundError as error:
        raise ContextualRuntimeUnavailable(
            f"Required contextual runtime package is not installed: {name}"
        ) from error
    lock = RUNTIME_ENVIRONMENT_LOCKS[name]
    if distribution.version != lock["version"]:
        raise ContextualRuntimeUnavailable(
            f"Contextual runtime version mismatch for {name}: "
            f"expected {lock['version']}, got {distribution.version}"
        )
    record = distribution.read_text("RECORD")
    metadata_text = distribution.read_text("METADATA")
    if record is None or metadata_text is None:
        raise ContextualRuntimeUnavailable(
            f"Installed distribution lacks digestable metadata: {name}"
        )
    record_sha256 = sha256(record.encode("utf-8")).hexdigest()
    metadata_sha256 = sha256(metadata_text.encode("utf-8")).hexdigest()
    if record_sha256 != lock["record"] or metadata_sha256 != lock["metadata"]:
        raise ContextualRuntimeUnavailable(
            f"Contextual runtime distribution content changed: {name}"
        )
    tree_digest = sha256()
    verified_files = 0
    unhashed_files = 0
    ignored_bytecode_caches = 0
    for row in csv.reader(record.splitlines()):
        if len(row) != 3 or not row[0]:
            raise ContextualRuntimeUnavailable(
                f"Contextual runtime RECORD is malformed: {name}"
            )
        relative_path, encoded_hash, raw_size = row
        path = _locate_distribution_record_file(distribution, relative_path)
        record_parts = PurePosixPath(relative_path).parts
        if (
            not encoded_hash
            and not raw_size
            and "__pycache__" in record_parts
            and relative_path.endswith(".pyc")
        ):
            try:
                source_path = Path(importlib.util.source_from_cache(str(path)))
            except ValueError as error:
                raise ContextualRuntimeUnavailable(
                    f"Contextual runtime RECORD bytecode path is invalid: {name}: {relative_path}"
                ) from error
            if not source_path.is_file():
                raise ContextualRuntimeUnavailable(
                    f"Contextual runtime RECORD bytecode source is missing: {name}: {relative_path}"
                )
            ignored_bytecode_caches += 1
            tree_digest.update(
                stable_json(
                    {
                        "path": relative_path,
                        "status": "ignored_unhashed_bytecode_cache",
                    }
                ).encode("utf-8")
                + b"\n"
            )
            continue
        if not path.is_file():
            raise ContextualRuntimeUnavailable(
                f"Contextual runtime RECORD file is missing: {name}: {relative_path}"
            )
        actual_size = path.stat().st_size
        if raw_size and actual_size != int(raw_size):
            raise ContextualRuntimeUnavailable(
                f"Contextual runtime RECORD size drift: {name}: {relative_path}"
            )
        actual_sha256 = _sha256_file(path)
        if encoded_hash:
            algorithm, separator, encoded = encoded_hash.partition("=")
            if separator != "=" or algorithm != "sha256":
                raise ContextualRuntimeUnavailable(
                    f"Unsupported contextual runtime RECORD hash: {name}: {relative_path}"
                )
            expected_bytes = base64.urlsafe_b64decode(
                encoded + "=" * (-len(encoded) % 4)
            )
            if bytes.fromhex(actual_sha256) != expected_bytes:
                raise ContextualRuntimeUnavailable(
                    f"Contextual runtime installed file drift: {name}: {relative_path}"
                )
            verified_files += 1
        else:
            unhashed_files += 1
        tree_digest.update(
            stable_json(
                {
                    "path": relative_path,
                    "sha256": actual_sha256,
                    "size": actual_size,
                }
            ).encode("utf-8")
            + b"\n"
        )
    return {
        **RUNTIME_PACKAGE_CONTRACTS.get(name, {}),
        "name": name,
        "version": lock["version"],
        "license": lock["license"],
        "url": RUNTIME_PACKAGE_CONTRACTS.get(name, {}).get(
            "url", f"https://pypi.org/project/{name}/{lock['version']}/"
        ),
        "installed_version": distribution.version,
        "installed_record_sha256": record_sha256,
        "installed_metadata_sha256": metadata_sha256,
        "installed_tree_sha256": tree_digest.hexdigest(),
        "installed_file_count": verified_files + unhashed_files,
        "record_hashed_file_count": verified_files,
        "record_unhashed_file_count": unhashed_files,
        "ignored_unhashed_bytecode_cache_count": ignored_bytecode_caches,
    }


def validate_runtime_install_report(path: Path) -> dict[str, Any]:
    if not path.is_file() or _sha256_file(path) != RUNTIME_INSTALL_REPORT_SHA256:
        raise ContextualRuntimeUnavailable(
            "Pinned contextual pip installation report is missing or changed"
        )
    value = json.loads(path.read_text(encoding="utf-8"))
    expected_names = set(RUNTIME_PACKAGE_CONTRACTS) - {"torch"}
    actual: dict[str, dict[str, Any]] = {}
    for row in value.get("install", ()):
        metadata_value = row.get("metadata", {})
        raw_name = str(metadata_value.get("name", ""))
        name = raw_name.replace("_", "-").casefold()
        if name not in expected_names or name in actual:
            raise ContextualRuntimeUnavailable(
                "Pinned contextual pip report contains an unexpected package"
            )
        contract = RUNTIME_PACKAGE_CONTRACTS[name]
        hashes = row.get("download_info", {}).get("archive_info", {}).get(
            "hashes", {}
        )
        if (
            str(metadata_value.get("version")) != contract["version"]
            or hashes.get("sha256") != contract["artifact_sha256"]
            or row.get("download_info", {}).get("url") != contract["artifact_url"]
        ):
            raise ContextualRuntimeUnavailable(
                f"Pinned contextual pip report drifted for {name}"
            )
        actual[name] = {
            "name": name,
            "version": contract["version"],
            "artifact_sha256": contract["artifact_sha256"],
            "artifact_url": contract["artifact_url"],
        }
    if set(actual) != expected_names:
        raise ContextualRuntimeUnavailable(
            "Pinned contextual pip report package set is incomplete"
        )
    return {
        "sha256": RUNTIME_INSTALL_REPORT_SHA256,
        "package_count": len(actual),
        "packages": [actual[name] for name in sorted(actual)],
    }


class AwesomeAlignLocalEncoder:
    """Exact local-only AWESOME-align inference backend.

    Construction is intentionally expensive and fail-closed.  It validates the
    complete model snapshot before importing/loading Transformers and never
    calls a network API or a model hub downloader.
    """

    def __init__(
        self,
        snapshot_dir: Path,
        runtime_install_report: Path,
        runtime_packages_dir: Path,
    ) -> None:
        self._snapshot = validate_model_snapshot(snapshot_dir)
        install_report = validate_runtime_install_report(runtime_install_report)
        if not runtime_packages_dir.is_dir():
            raise ContextualRuntimeUnavailable(
                "Pinned contextual runtime package directory is missing"
            )
        runtime_path = str(runtime_packages_dir.resolve())
        if runtime_path not in sys.path:
            sys.path.insert(0, runtime_path)
            importlib.invalidate_caches()
        runtime = {
            name: _distribution_record(name)
            for name in sorted(RUNTIME_ENVIRONMENT_LOCKS)
        }
        # These switches must precede the Transformers import.  Otherwise an
        # unrelated globally installed TensorFlow/Flax/image stack can be
        # detected and imported even though this channel is strictly PyTorch.
        os.environ["USE_TORCH"] = "1"
        os.environ["USE_TF"] = "0"
        os.environ["USE_FLAX"] = "0"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["OMP_NUM_THREADS"] = "1"
        os.environ["MKL_NUM_THREADS"] = "1"
        try:
            import torch  # type: ignore[import-not-found]
            import transformers  # type: ignore[import-not-found]
        except ImportError as error:
            raise ContextualRuntimeUnavailable(
                "Pinned torch/transformers runtime cannot be imported"
            ) from error
        torch.manual_seed(0)
        torch.set_num_threads(1)
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError as error:
            if torch.get_num_interop_threads() != 1:
                raise ContextualRuntimeUnavailable(
                    "PyTorch inter-op thread pool was initialized above one thread"
                ) from error
        torch.use_deterministic_algorithms(True)
        if hasattr(torch.backends, "mkldnn"):
            torch.backends.mkldnn.enabled = False

        tokenizer = transformers.AutoTokenizer.from_pretrained(
            str(snapshot_dir),
            local_files_only=True,
            trust_remote_code=False,
            use_fast=False,
        )
        model = transformers.AutoModel.from_pretrained(
            str(snapshot_dir),
            local_files_only=True,
            trust_remote_code=False,
            add_pooling_layer=False,
        )
        model.to(device="cpu", dtype=torch.float32)
        model.eval()
        self._torch = torch
        self._tokenizer = tokenizer
        self._model = model
        self._runtime = {
            "mode": "local_only_cpu_float32_single_thread",
            "network_access": False,
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_executable_sha256": _sha256_file(Path(sys.executable)),
            "platform": platform.platform(),
            "random_seed": 0,
            "torch_intraop_threads": torch.get_num_threads(),
            "torch_interop_threads": torch.get_num_interop_threads(),
            "torch_deterministic_algorithms": True,
            "mkldnn_enabled": False,
            "packages": runtime,
            "pip_install_report": install_report,
        }

    def runtime_registry(self) -> Mapping[str, Any]:
        return self._runtime

    def _prepare_words(
        self,
        words: Sequence[str],
    ) -> tuple[Any, list[int], list[str]]:
        wordpieces: list[str] = []
        subword_to_word: list[int] = []
        for word_index, word in enumerate(words):
            pieces = list(self._tokenizer.tokenize(word))
            if not pieces:
                raise ContextualRuntimeUnavailable(
                    "Pinned tokenizer produced an empty wordpiece sequence"
                )
            wordpieces.extend(pieces)
            subword_to_word.extend([word_index] * len(pieces))
        if len(wordpieces) > MAX_MODEL_WORDPIECES:
            raise ModelInputTooLong(
                f"Verse requires {len(wordpieces)} wordpieces; "
                f"maximum is {MAX_MODEL_WORDPIECES}; truncation is forbidden"
            )
        wordpiece_ids = self._tokenizer.convert_tokens_to_ids(wordpieces)
        prepared = self._tokenizer.prepare_for_model(
            wordpiece_ids,
            add_special_tokens=True,
            return_tensors="pt",
            truncation=False,
        )
        input_ids = prepared["input_ids"]
        if input_ids.ndim == 1:
            input_ids = input_ids.unsqueeze(0)
        if input_ids.ndim != 2 or input_ids.shape[0] != 1:
            raise ContextualRuntimeUnavailable(
                "Pinned tokenizer returned an unexpected input tensor shape"
            )
        return input_ids, subword_to_word, wordpieces

    def wordpiece_counts(
        self,
        *,
        original_words: Sequence[str],
        target_words: Sequence[str],
    ) -> tuple[int, int]:
        """Validate exact tokenization lengths without running the model."""

        _original_ids, _original_map, original_pieces = self._prepare_words(
            original_words
        )
        _target_ids, _target_map, target_pieces = self._prepare_words(target_words)
        return len(original_pieces), len(target_pieces)

    def align(
        self,
        *,
        target_ref: str,
        original_words: Sequence[str],
        target_words: Sequence[str],
    ) -> ContextualObservation:
        torch = self._torch
        original_ids, original_map, original_pieces = self._prepare_words(
            original_words
        )
        target_ids, target_map, target_pieces = self._prepare_words(target_words)
        with torch.inference_mode():
            original_output = self._model(
                original_ids,
                output_hidden_states=True,
                return_dict=True,
            )
            target_output = self._model(
                target_ids,
                output_hidden_states=True,
                return_dict=True,
            )
            original_hidden = original_output.hidden_states[ALIGN_LAYER][0, 1:-1]
            target_hidden = target_output.hidden_states[ALIGN_LAYER][0, 1:-1]
            dot_products = torch.matmul(original_hidden, target_hidden.transpose(0, 1))
            source_to_target = torch.softmax(dot_products, dim=-1)
            target_to_source = torch.softmax(dot_products, dim=-2)
            mutual = (source_to_target > MUTUAL_SOFTMAX_THRESHOLD) & (
                target_to_source > MUTUAL_SOFTMAX_THRESHOLD
            )
            coordinates = torch.nonzero(mutual, as_tuple=False).tolist()

        links: list[ContextualWordLink] = []
        for original_subword_index, target_subword_index in coordinates:
            original_piece = original_pieces[original_subword_index]
            target_piece = target_pieces[target_subword_index]
            if original_piece == "[UNK]" or target_piece == "[UNK]":
                continue
            links.append(
                ContextualWordLink(
                    original_word_index=original_map[original_subword_index],
                    target_word_index=target_map[target_subword_index],
                    original_subword_index=original_subword_index,
                    target_subword_index=target_subword_index,
                    original_subword=original_piece,
                    target_subword=target_piece,
                    source_to_target_probability=round(
                        float(source_to_target[
                            original_subword_index, target_subword_index
                        ].item()),
                        12,
                    ),
                    target_to_source_probability=round(
                        float(target_to_source[
                            original_subword_index, target_subword_index
                        ].item()),
                        12,
                    ),
                    dot_product=round(
                        float(dot_products[
                            original_subword_index, target_subword_index
                        ].item()),
                        12,
                    ),
                )
            )
        return ContextualObservation(
            target_ref=target_ref,
            model_id=MODEL_ID,
            model_revision=MODEL_REVISION,
            model_snapshot_contract_sha256=MODEL_SNAPSHOT_CONTRACT_SHA256,
            align_layer=ALIGN_LAYER,
            threshold=MUTUAL_SOFTMAX_THRESHOLD,
            original_wordpiece_count=len(original_pieces),
            target_wordpiece_count=len(target_pieces),
            original_sequence_sha256=_sha256_json(list(original_words)),
            target_sequence_sha256=_sha256_json(list(target_words)),
            links=tuple(
                sorted(
                    links,
                    key=lambda item: (
                        item.original_word_index,
                        item.target_word_index,
                        item.original_subword_index,
                        item.target_subword_index,
                    ),
                )
            ),
        )


def load_original_surfaces(
    original_universe_path: Path,
    *,
    context: CandidateContext,
    counters: Counter[str] | None = None,
) -> dict[str, str]:
    """Load exact original surfaces for current resolved-primary components."""

    accounting = counters if counters is not None else Counter()
    surfaces: dict[str, str] = {}
    with original_universe_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            accounting["original_rows_processed"] += 1
            row = json.loads(line)
            token_id = str(row["original_token_id"])
            token = context.originals_by_id.get(token_id)
            if token is None:
                raise ValueError(
                    f"Original surface row is absent from candidate context: {token_id}"
                )
            if not token.is_resolved_primary or token.target_ref is None:
                accounting["original_rows_skipped_not_resolved_primary"] += 1
                continue
            surface = str(row.get("surface_raw") or "")
            if not surface:
                accounting["original_rows_skipped_empty_surface"] += 1
                continue
            if token_id in surfaces:
                raise ValueError(
                    f"Duplicate original surface ID at line {line_number}: {token_id}"
                )
            surfaces[token_id] = surface
            accounting["original_surfaces_loaded"] += 1
    return surfaces


def _contextual_token_groups(
    *,
    context: CandidateContext,
    original_surfaces: Mapping[str, str],
    expected_target_ref_count: int | None = None,
) -> tuple[dict[str, list[Any]], dict[str, list[Any]], Counter[str]]:
    target_by_ref: dict[str, list[Any]] = defaultdict(list)
    original_by_ref: dict[str, list[Any]] = defaultdict(list)
    counters: Counter[str] = Counter()
    for token in context.target_by_id.values():
        if not token.comparison:
            counters["target_tokens_skipped_nonlexical"] += 1
            continue
        target_by_ref[token.target_ref].append(token)
        counters["target_tokens_loaded"] += 1
    for token_id, surface in original_surfaces.items():
        if not surface:
            raise ValueError("Contextual original surface inventory contains an empty value")
        token = context.originals_by_id[token_id]
        if not token.is_resolved_primary or token.target_ref is None:
            raise ValueError("Contextual original surface is not a resolved primary token")
        original_by_ref[token.target_ref].append(token)
        counters["original_tokens_loaded"] += 1
    target_refs = set(target_by_ref)
    original_refs = set(original_by_ref)
    missing_original = sorted(target_refs - original_refs)
    missing_target = sorted(original_refs - target_refs)
    if missing_original or missing_target:
        raise ValueError(
            "Contextual input ref grids differ: "
            f"missing_original={missing_original[:20]}, "
            f"missing_target={missing_target[:20]}"
        )
    if (
        expected_target_ref_count is not None
        and len(target_refs) != expected_target_ref_count
    ):
        raise ValueError(
            "Contextual input target-ref count drift: "
            f"{len(target_refs)} != {expected_target_ref_count}"
        )
    counters["validated_target_refs"] = len(target_refs)
    return target_by_ref, original_by_ref, counters


def preflight_contextual_sequences(
    *,
    context: CandidateContext,
    original_surfaces: Mapping[str, str],
    encoder: AwesomeAlignLocalEncoder,
    expected_target_ref_count: int = EXPECTED_TARGET_REF_COUNT,
    only_target_refs: set[str] | None = None,
) -> dict[str, int]:
    """Tokenize every requested exact sequence before expensive inference."""

    target_by_ref, original_by_ref, counters = _contextual_token_groups(
        context=context,
        original_surfaces=original_surfaces,
        expected_target_ref_count=expected_target_ref_count,
    )
    available = set(target_by_ref)
    requested = available if only_target_refs is None else set(only_target_refs)
    if not requested or not requested <= available:
        raise ValueError(
            "Contextual preflight requested missing or empty target-ref selection"
        )
    for target_ref in sorted(requested):
        originals = sorted(
            original_by_ref[target_ref], key=lambda item: (item.order, item.token_id)
        )
        targets = sorted(
            target_by_ref[target_ref], key=lambda item: (item.order, item.token_id)
        )
        original_count, target_count = encoder.wordpiece_counts(
            original_words=[original_surfaces[item.token_id] for item in originals],
            target_words=[item.surface for item in targets],
        )
        counters["preflight_verses"] += 1
        counters["preflight_original_wordpieces"] += original_count
        counters["preflight_target_wordpieces"] += target_count
        counters["preflight_max_original_wordpieces"] = max(
            counters["preflight_max_original_wordpieces"], original_count
        )
        counters["preflight_max_target_wordpieces"] = max(
            counters["preflight_max_target_wordpieces"], target_count
        )
    return dict(sorted(counters.items()))


def _validate_observation(
    observation: ContextualObservation,
    *,
    target_ref: str,
    original_words: Sequence[str],
    target_words: Sequence[str],
) -> tuple[ContextualWordLink, ...]:
    if (
        observation.target_ref != target_ref
        or observation.model_id != MODEL_ID
        or observation.model_revision != MODEL_REVISION
        or observation.model_snapshot_contract_sha256
        != MODEL_SNAPSHOT_CONTRACT_SHA256
        or observation.align_layer != ALIGN_LAYER
        or observation.threshold != MUTUAL_SOFTMAX_THRESHOLD
        or observation.original_sequence_sha256
        != _sha256_json(list(original_words))
        or observation.target_sequence_sha256 != _sha256_json(list(target_words))
    ):
        raise ValueError("Contextual observation violates the pinned model contract")
    original_count = len(original_words)
    target_count = len(target_words)
    identities: set[tuple[int, int, int, int]] = set()
    accepted: list[ContextualWordLink] = []
    for link in observation.links:
        if not 0 <= link.original_word_index < original_count:
            raise ValueError("Contextual observation has dangling original word index")
        if not 0 <= link.target_word_index < target_count:
            raise ValueError("Contextual observation has dangling target word index")
        identity = (
            link.original_word_index,
            link.target_word_index,
            link.original_subword_index,
            link.target_subword_index,
        )
        if identity in identities:
            raise ValueError("Contextual observation contains a duplicate subword link")
        identities.add(identity)
        if not 0.0 <= link.source_to_target_probability <= 1.0:
            raise ValueError("Invalid source-to-target contextual probability")
        if not 0.0 <= link.target_to_source_probability <= 1.0:
            raise ValueError("Invalid target-to-source contextual probability")
        if (
            link.source_to_target_probability > MUTUAL_SOFTMAX_THRESHOLD
            and link.target_to_source_probability > MUTUAL_SOFTMAX_THRESHOLD
            and link.original_subword != "[UNK]"
            and link.target_subword != "[UNK]"
        ):
            accepted.append(link)
    return tuple(accepted)


def _connected_components(
    links: Sequence[ContextualWordLink],
) -> list[tuple[tuple[int, ...], tuple[int, ...], tuple[ContextualWordLink, ...]]]:
    adjacency: dict[tuple[str, int], set[tuple[str, int]]] = defaultdict(set)
    links_by_nodes: dict[
        frozenset[tuple[str, int]], list[ContextualWordLink]
    ] = defaultdict(list)
    for link in links:
        original_node = ("original", link.original_word_index)
        target_node = ("target", link.target_word_index)
        adjacency[original_node].add(target_node)
        adjacency[target_node].add(original_node)
        links_by_nodes[frozenset((original_node, target_node))].append(link)

    seen: set[tuple[str, int]] = set()
    components: list[
        tuple[tuple[int, ...], tuple[int, ...], tuple[ContextualWordLink, ...]]
    ] = []
    for first in sorted(adjacency):
        if first in seen:
            continue
        queue = deque((first,))
        nodes: set[tuple[str, int]] = set()
        while queue:
            node = queue.popleft()
            if node in seen:
                continue
            seen.add(node)
            nodes.add(node)
            queue.extend(sorted(adjacency[node] - seen))
        original_indexes = tuple(
            sorted(index for kind, index in nodes if kind == "original")
        )
        target_indexes = tuple(
            sorted(index for kind, index in nodes if kind == "target")
        )
        component_links = tuple(
            sorted(
                (
                    link
                    for pair, pair_links in links_by_nodes.items()
                    if pair <= nodes
                    for link in pair_links
                ),
                key=lambda item: (
                    item.original_word_index,
                    item.target_word_index,
                    item.original_subword_index,
                    item.target_subword_index,
                ),
            )
        )
        components.append((original_indexes, target_indexes, component_links))
    return components


def validate_contextual_candidate(
    row: Mapping[str, Any],
    *,
    context: CandidateContext,
) -> None:
    validate_candidate(row, context=context)
    if row.get("generator_id") != CONTEXTUAL_GENERATOR_ID:
        raise ValueError("Wrong contextual generator ID")
    if row.get("resolver_eligible") is not False or row.get("auto_acceptance") is not False:
        raise ValueError("Contextual candidates must remain fail-closed")
    if row.get("position_features_used") is not False:
        raise ValueError("Contextual candidate claims a positional feature")
    if row.get("translation_bridge_used") is not False:
        raise ValueError("Contextual candidate claims a translation bridge")
    if row.get("verse_bag_transfer_used") is not False:
        raise ValueError("Contextual candidate claims verse-bag transfer")
    if row.get("single_translation_proof") is not False:
        raise ValueError("Contextual candidate claims single-translation proof")
    evidence = row.get("evidence")
    if not isinstance(evidence, list) or len(evidence) != 1:
        raise ValueError("Contextual candidate requires one complete model observation")
    links = evidence[0].get("subword_links")
    if not isinstance(links, list) or not links:
        raise ValueError("Contextual candidate has no token-level subword evidence")
    for link in links:
        if (
            float(link["source_to_target_probability"])
            <= MUTUAL_SOFTMAX_THRESHOLD
            or float(link["target_to_source_probability"])
            <= MUTUAL_SOFTMAX_THRESHOLD
        ):
            raise ValueError("Contextual candidate lacks mutual directional evidence")


def generate_contextual_candidates(
    *,
    context: CandidateContext,
    original_surfaces: Mapping[str, str],
    encoder: ContextualEncoder,
    only_target_refs: set[str] | None = None,
    expected_target_ref_count: int | None = None,
    fail_on_model_input_too_long: bool = False,
    progress_callback: Callable[[str, Mapping[str, int]], None] | None = None,
) -> tuple[Iterator[dict[str, Any]], Counter[str]]:
    """Generate uncalibrated verse-local contextual hyperedge candidates."""

    target_by_ref, original_by_ref, counters = _contextual_token_groups(
        context=context,
        original_surfaces=original_surfaces,
        expected_target_ref_count=expected_target_ref_count,
    )

    def iterate() -> Iterator[dict[str, Any]]:
        refs = sorted(set(target_by_ref) & set(original_by_ref))
        for target_ref in refs:
            if only_target_refs is not None and target_ref not in only_target_refs:
                counters["skipped_outside_requested_refs"] += 1
                continue
            originals = sorted(
                original_by_ref[target_ref], key=lambda item: (item.order, item.token_id)
            )
            targets = sorted(
                target_by_ref[target_ref], key=lambda item: (item.order, item.token_id)
            )
            counters["processed_verses"] += 1
            try:
                exact_original_words = [
                    original_surfaces[item.token_id] for item in originals
                ]
                exact_target_words = [item.surface for item in targets]
                observation = encoder.align(
                    target_ref=target_ref,
                    original_words=exact_original_words,
                    target_words=exact_target_words,
                )
            except ModelInputTooLong:
                counters["skipped_model_input_too_long"] += 1
                if progress_callback is not None:
                    progress_callback(target_ref, dict(counters))
                if fail_on_model_input_too_long:
                    raise
                continue
            accepted_links = _validate_observation(
                observation,
                target_ref=target_ref,
                original_words=exact_original_words,
                target_words=exact_target_words,
            )
            counters["observed_subword_links"] += len(observation.links)
            counters["mutual_non_unknown_subword_links"] += len(accepted_links)
            if not accepted_links:
                counters["verses_without_mutual_links"] += 1
                if progress_callback is not None:
                    progress_callback(target_ref, dict(counters))
                continue
            for original_indexes, target_indexes, component_links in _connected_components(
                accepted_links
            ):
                original_ids = tuple(originals[index].token_id for index in original_indexes)
                target_ids = tuple(targets[index].token_id for index in target_indexes)
                evidence_links = [
                    {
                        "original_token_id": originals[
                            link.original_word_index
                        ].token_id,
                        "target_token_id": targets[link.target_word_index].token_id,
                        "original_subword_index": link.original_subword_index,
                        "target_subword_index": link.target_subword_index,
                        "original_subword": link.original_subword,
                        "target_subword": link.target_subword,
                        "source_to_target_probability": round(
                            link.source_to_target_probability, 12
                        ),
                        "target_to_source_probability": round(
                            link.target_to_source_probability, 12
                        ),
                        "dot_product": round(link.dot_product, 12),
                    }
                    for link in component_links
                ]
                component_score = min(
                    min(
                        link.source_to_target_probability,
                        link.target_to_source_probability,
                    )
                    for link in component_links
                )
                evidence = {
                    "kind": "mutual_contextual_subword_softmax_component",
                    "model_id": MODEL_ID,
                    "model_revision": MODEL_REVISION,
                    "model_snapshot_contract_sha256": (
                        MODEL_SNAPSHOT_CONTRACT_SHA256
                    ),
                    "align_layer": ALIGN_LAYER,
                    "strict_mutual_threshold": MUTUAL_SOFTMAX_THRESHOLD,
                    "original_wordpiece_count": observation.original_wordpiece_count,
                    "target_wordpiece_count": observation.target_wordpiece_count,
                    "original_sequence_sha256": observation.original_sequence_sha256,
                    "target_sequence_sha256": observation.target_sequence_sha256,
                    "subword_links": evidence_links,
                    "sequence_order_use": "transformer_context_only",
                    "position_distance_or_tie_break": False,
                }
                evidence_sha256 = _sha256_json(evidence)
                row = _base_candidate(
                    generator_id=CONTEXTUAL_GENERATOR_ID,
                    target_ref=target_ref,
                    original_ids=original_ids,
                    target_ids=target_ids,
                    strongs=_strongs_for_originals(
                        original_ids, context.originals_by_id
                    ),
                    relation=_relation(len(original_ids), len(target_ids)),
                    evidence_channels=(
                        "multilingual_contextual_mutual_subword_softmax",
                    ),
                    evidence=(evidence,),
                    dependency_family_ids=(
                        "stage6_synthesized_text",
                        "original_token_universe_primary",
                        "awesome_align_with_co_model",
                    ),
                    identity_extra={
                        "contextual_contract_version": CONTEXTUAL_CONTRACT_VERSION,
                        "model_revision": MODEL_REVISION,
                        "evidence_sha256": evidence_sha256,
                    },
                    score={
                        "name": "minimum_mutual_subword_probability",
                        "value": round(component_score, 12),
                        "threshold": MUTUAL_SOFTMAX_THRESHOLD,
                        "calibrated": False,
                    },
                )
                _attach_target_spans(row, context=context)
                row.update(
                    {
                        "contextual_contract_version": CONTEXTUAL_CONTRACT_VERSION,
                        "evidence_sha256": evidence_sha256,
                        "position_features_used": False,
                        "translation_bridge_used": False,
                        "verse_bag_transfer_used": False,
                        "single_translation_proof": False,
                        "independent_vote": False,
                        "out_of_domain_for_model_card_languages": True,
                    }
                )
                row["proof_limitations"].extend(
                    [
                        "model-card alignment languages do not validate Ukrainian, Biblical Hebrew, or Koine Greek",
                        "contextual similarity is candidate evidence, not token-link proof",
                        "no resolver use is permitted before frozen-gold calibration",
                    ]
                )
                validate_contextual_candidate(row, context=context)
                counters["emitted_candidates"] += 1
                counters[f"relation.{row['relation']}"] += 1
                yield row
            if progress_callback is not None:
                progress_callback(target_ref, dict(counters))

    return iterate(), counters


def build_contextual_generator_registry(
    *,
    runtime_registry: Mapping[str, Any] | None,
) -> dict[str, Any]:
    module_path = Path(__file__)
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "contextual_contract_version": CONTEXTUAL_CONTRACT_VERSION,
        "artifact": "multilingual_contextual_candidate_generator_registry",
        "status": "candidate_only_no_auto_acceptance",
        "generator_id": CONTEXTUAL_GENERATOR_ID,
        "implementation": "scripts/bible_module/ukrainian_stage_7_contextual.py",
        "implementation_sha256": _sha256_file(module_path),
        "model": {
            "model_id": MODEL_ID,
            "revision": MODEL_REVISION,
            "repository_url": MODEL_REPOSITORY_URL,
            "revision_url": MODEL_REVISION_URL,
            "license": MODEL_LICENSE,
            "license_evidence_url": MODEL_LICENSE_EVIDENCE_URL,
            "snapshot_contract_sha256": MODEL_SNAPSHOT_CONTRACT_SHA256,
            "files": [
                {
                    "file": filename,
                    **MODEL_FILES[filename],
                    "url": (
                        f"{MODEL_REPOSITORY_URL}/resolve/{MODEL_REVISION}/{filename}"
                    ),
                }
                for filename in sorted(MODEL_FILES)
            ],
            "usage": "local feature extraction only; model weights are not committed",
        },
        "extraction": {
            "upstream_implementation_url": UPSTREAM_IMPLEMENTATION_URL,
            "upstream_license": UPSTREAM_IMPLEMENTATION_LICENSE,
            "paper_url": UPSTREAM_PAPER_URL,
            "align_layer": ALIGN_LAYER,
            "strict_mutual_threshold": MUTUAL_SOFTMAX_THRESHOLD,
            "hyperedge_rule": "bipartite connected components of mutual subword links",
            "positional_features": False,
            "nearest_neighbor_tie_break": False,
            "verse_bag_transfer": False,
            "translation_bridge": False,
        },
        "runtime_package_contracts": [
            {"package": name, **RUNTIME_PACKAGE_CONTRACTS[name]}
            for name in sorted(RUNTIME_PACKAGE_CONTRACTS)
        ],
        "runtime_environment_contracts": [
            {"package": name, **RUNTIME_ENVIRONMENT_LOCKS[name]}
            for name in sorted(RUNTIME_ENVIRONMENT_LOCKS)
        ],
        "runtime_install_report_sha256": RUNTIME_INSTALL_REPORT_SHA256,
        "runtime": runtime_registry,
        "calibrated": False,
        "auto_acceptance": False,
        "resolver_eligible": False,
        "processed_count": 1,
        "skipped_count": 0 if runtime_registry is not None else 1,
        "error_count": 0,
    }


def validate_contextual_generator_registry(registry: Mapping[str, Any]) -> None:
    if registry.get("contextual_contract_version") != CONTEXTUAL_CONTRACT_VERSION:
        raise ValueError("Wrong contextual registry contract")
    if registry.get("generator_id") != CONTEXTUAL_GENERATOR_ID:
        raise ValueError("Wrong contextual registry generator")
    if (
        registry.get("calibrated") is not False
        or registry.get("auto_acceptance") is not False
        or registry.get("resolver_eligible") is not False
    ):
        raise ValueError("Contextual registry enables uncalibrated decisions")
    model = registry.get("model")
    if not isinstance(model, Mapping):
        raise ValueError("Contextual registry lacks model contract")
    if (
        model.get("model_id") != MODEL_ID
        or model.get("revision") != MODEL_REVISION
        or model.get("license") != MODEL_LICENSE
        or model.get("snapshot_contract_sha256")
        != MODEL_SNAPSHOT_CONTRACT_SHA256
    ):
        raise ValueError("Contextual registry model provenance drift")
    for file_record in model.get("files", ()):
        if _SHA256_RE.fullmatch(str(file_record.get("sha256", ""))) is None:
            raise ValueError("Contextual registry has invalid model file digest")
    package_contracts = registry.get("runtime_package_contracts")
    if not isinstance(package_contracts, list) or len(package_contracts) != len(
        RUNTIME_PACKAGE_CONTRACTS
    ):
        raise ValueError("Contextual registry lacks exact runtime contracts")
    for package in package_contracts:
        if not package.get("version") or not package.get("license"):
            raise ValueError("Contextual registry runtime contract is incomplete")
        if _SHA256_RE.fullmatch(str(package.get("artifact_sha256", ""))) is None:
            raise ValueError("Contextual registry runtime artifact digest is invalid")
    environment_contracts = registry.get("runtime_environment_contracts")
    if not isinstance(environment_contracts, list) or len(
        environment_contracts
    ) != len(RUNTIME_ENVIRONMENT_LOCKS):
        raise ValueError("Contextual registry lacks the full runtime environment lock")
    runtime = registry.get("runtime")
    if runtime is not None:
        packages = runtime.get("packages")
        if not isinstance(packages, Mapping) or set(packages) != set(
            RUNTIME_ENVIRONMENT_LOCKS
        ):
            raise ValueError("Contextual runtime package inventory is incomplete")
        for name, lock in RUNTIME_ENVIRONMENT_LOCKS.items():
            package = packages[name]
            if (
                package.get("installed_version") != lock["version"]
                or package.get("installed_record_sha256") != lock["record"]
                or package.get("installed_metadata_sha256") != lock["metadata"]
            ):
                raise ValueError(f"Contextual runtime package lock drift: {name}")
            if (
                _SHA256_RE.fullmatch(
                    str(package.get("installed_tree_sha256", ""))
                )
                is None
                or int(package.get("installed_file_count", 0)) < 1
                or int(package.get("record_hashed_file_count", 0)) < 1
            ):
                raise ValueError(
                    f"Contextual runtime installed-file verification is incomplete: {name}"
                )
        if runtime.get("pip_install_report", {}).get("sha256") != (
            RUNTIME_INSTALL_REPORT_SHA256
        ):
            raise ValueError("Contextual runtime pip installation report drift")


def generate_contextual_artifacts(
    *,
    token_inventory_path: Path,
    original_universe_path: Path,
    source_registry_path: Path,
    model_snapshot_dir: Path,
    runtime_install_report_path: Path,
    runtime_packages_dir: Path,
    output_dir: Path,
    only_target_refs: set[str] | None = None,
    expected_target_ref_count: int = EXPECTED_TARGET_REF_COUNT,
    progress_path: Path | None = None,
) -> dict[str, Any]:
    """Run the exact production backend and serialize candidate-only artifacts."""

    if output_dir.exists():
        raise FileExistsError(
            f"Contextual output directory already exists: {output_dir}"
        )
    if not source_registry_path.is_file():
        raise FileNotFoundError(
            f"Contextual source registry is missing: {source_registry_path}"
        )
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    run_dir = output_dir.with_name(f".{output_dir.name}.tmp-{os.getpid()}")
    if run_dir.exists():
        raise FileExistsError(f"Contextual temporary output already exists: {run_dir}")

    context = load_context(token_inventory_path, original_universe_path)
    surface_counts: Counter[str] = Counter()
    original_surfaces = load_original_surfaces(
        original_universe_path,
        context=context,
        counters=surface_counts,
    )
    encoder = AwesomeAlignLocalEncoder(
        model_snapshot_dir,
        runtime_install_report_path,
        runtime_packages_dir,
    )
    preflight_counts = preflight_contextual_sequences(
        context=context,
        original_surfaces=original_surfaces,
        encoder=encoder,
        expected_target_ref_count=expected_target_ref_count,
        only_target_refs=only_target_refs,
    )
    expected_processed = (
        expected_target_ref_count
        if only_target_refs is None
        else len(only_target_refs)
    )
    started_unix = time.time()

    def write_progress(
        target_ref: str, current_counts: Mapping[str, int], *, force: bool = False
    ) -> None:
        if progress_path is None:
            return
        processed = int(current_counts.get("processed_verses", 0))
        if not force and processed % 100 != 0 and processed != expected_processed:
            return
        progress_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = progress_path.with_name(f".{progress_path.name}.tmp-{os.getpid()}")
        temporary.write_text(
            stable_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "contract_version": CONTRACT_VERSION,
                    "contextual_contract_version": CONTEXTUAL_CONTRACT_VERSION,
                    "artifact": "contextual_generation_progress",
                    "status": (
                        "complete"
                        if processed == expected_processed
                        else "inference_running"
                    ),
                    "pid": os.getpid(),
                    "started_unix": started_unix,
                    "updated_unix": time.time(),
                    "requested_target_refs": expected_processed,
                    "processed_target_refs": processed,
                    "last_target_ref": target_ref,
                    "emitted_candidates": int(
                        current_counts.get("emitted_candidates", 0)
                    ),
                    "error_count": 0,
                }
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(progress_path)

    write_progress("", {"processed_verses": 0}, force=True)
    iterator, counters = generate_contextual_candidates(
        context=context,
        original_surfaces=original_surfaces,
        encoder=encoder,
        only_target_refs=only_target_refs,
        expected_target_ref_count=expected_target_ref_count,
        fail_on_model_input_too_long=True,
        progress_callback=write_progress,
    )
    run_dir.mkdir()
    candidate_path = run_dir / "alignment_candidates.contextual.jsonl"
    digest = sha256()
    count = 0
    with candidate_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in iterator:
            line = stable_json(row) + "\n"
            handle.write(line)
            digest.update(line.encode("utf-8"))
            count += 1
    registry = build_contextual_generator_registry(
        runtime_registry=encoder.runtime_registry()
    )
    validate_contextual_generator_registry(registry)
    registry_path = run_dir / "contextual_generator_registry.json"
    registry_path.write_text(stable_json(registry) + "\n", encoding="utf-8", newline="\n")
    if counters["processed_verses"] != expected_processed:
        raise RuntimeError(
            "Contextual inference did not process every requested ref: "
            f"{counters['processed_verses']} != {expected_processed}"
        )
    if counters["skipped_model_input_too_long"]:
        raise RuntimeError("Contextual inference skipped an overlong verse")
    combined_counts = {
        **{
            f"surface.{key}": value
            for key, value in sorted(surface_counts.items())
        },
        **{
            f"preflight.{key}": value
            for key, value in sorted(preflight_counts.items())
        },
        **dict(sorted(counters.items())),
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "contextual_contract_version": CONTEXTUAL_CONTRACT_VERSION,
        "artifact": "multilingual_contextual_alignment_candidates",
        "status": "complete_candidate_only_no_auto_acceptance",
        "input_sha256": {
            "token_inventory": _sha256_file(token_inventory_path),
            "original_token_universe": _sha256_file(original_universe_path),
            "source_registry": _sha256_file(source_registry_path),
            "model_snapshot_contract": MODEL_SNAPSHOT_CONTRACT_SHA256,
            "runtime_install_report": _sha256_file(
                runtime_install_report_path
            ),
            "generator_registry": _sha256_file(registry_path),
        },
        "output": candidate_path.name,
        "output_sha256": digest.hexdigest(),
        "output_files": {
            candidate_path.name: digest.hexdigest(),
            registry_path.name: _sha256_file(registry_path),
        },
        "output_count": count,
        "processed_count": counters["processed_verses"],
        "skipped_count": sum(
            value for key, value in combined_counts.items() if "skipped_" in key
        ),
        "error_count": 0,
        "counts": combined_counts,
        "calibrated": False,
        "auto_acceptance": False,
        "resolver_eligible": False,
        "deterministic_serialization": "UTF-8 LF; stable_json; canonical candidate order",
    }
    manifest_path = run_dir / "alignment_candidates.contextual.manifest.json"
    manifest_path.write_text(stable_json(manifest) + "\n", encoding="utf-8", newline="\n")
    run_dir.replace(output_dir)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate fail-closed Ukrainian stage-7 contextual candidates"
    )
    parser.add_argument("--token-inventory", type=Path, required=True)
    parser.add_argument("--original-universe", type=Path, required=True)
    parser.add_argument("--source-registry", type=Path, required=True)
    parser.add_argument("--model-snapshot", type=Path, required=True)
    parser.add_argument("--runtime-install-report", type=Path, required=True)
    parser.add_argument("--runtime-packages", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--progress", type=Path)
    args = parser.parse_args(argv)
    manifest = generate_contextual_artifacts(
        token_inventory_path=args.token_inventory,
        original_universe_path=args.original_universe,
        source_registry_path=args.source_registry,
        model_snapshot_dir=args.model_snapshot,
        runtime_install_report_path=args.runtime_install_report,
        runtime_packages_dir=args.runtime_packages,
        output_dir=args.output,
        progress_path=args.progress,
    )
    print(stable_json(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
