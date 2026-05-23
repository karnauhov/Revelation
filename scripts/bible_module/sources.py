from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


STEPBIBLE_DATA_COMMIT = "b9dcc831a98e0fd6f3c7e122be9ff68377c310c0"
STEPBIBLE_LICENSE_NAME = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
STEPBIBLE_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
STEPBIBLE_REPOSITORY_URL = "https://github.com/STEPBible/STEPBible-Data"

CROSSWIRE_LXX_VERSION = "3.2 (2025-03-15)"
CROSSWIRE_LXX_LICENSE_NAME = "Copyrighted; Free non-commercial distribution"
CROSSWIRE_LXX_MODINFO_URL = "https://crosswire.org/sword/modules/ModInfo.jsp?modName=LXX"
CROSSWIRE_LXX_LICENSE_URL = (
    "https://www.crosswire.org/sword/copyright/ModInfoCopyright.jsp?modName=LXX"
)

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE_CACHE_DIR = PACKAGE_DIR / "source_cache"
DEFAULT_SOURCE_LOCK_PATH = PACKAGE_DIR / "source_manifest.lock.json"


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    title: str
    filename: str
    source_url: str
    source_page_url: str
    version: str
    source_commit: str | None
    license_name: str
    license_url: str
    notes: str


def _step_raw_url(path: str) -> str:
    return (
        f"https://raw.githubusercontent.com/STEPBible/STEPBible-Data/"
        f"{STEPBIBLE_DATA_COMMIT}/{quote(path)}"
    )


def _step_page_url(path: str) -> str:
    return (
        f"{STEPBIBLE_REPOSITORY_URL}/blob/"
        f"{STEPBIBLE_DATA_COMMIT}/{quote(path)}"
    )


def _step_source(
    *,
    source_id: str,
    title: str,
    filename: str,
    path: str,
    notes: str,
) -> SourceSpec:
    return SourceSpec(
        source_id=source_id,
        title=title,
        filename=filename,
        source_url=_step_raw_url(path),
        source_page_url=_step_page_url(path),
        version=f"STEPBible-Data commit {STEPBIBLE_DATA_COMMIT}",
        source_commit=STEPBIBLE_DATA_COMMIT,
        license_name=STEPBIBLE_LICENSE_NAME,
        license_url=STEPBIBLE_LICENSE_URL,
        notes=notes,
    )


SOURCE_SPECS: tuple[SourceSpec, ...] = (
    _step_source(
        source_id="step_tagnt_mat_jhn",
        title="TAGNT Mat-Jhn - Translators Amalgamated Greek NT",
        filename="step_tagnt_mat_jhn.txt",
        path=(
            "Translators Amalgamated OT+NT/"
            "TAGNT Mat-Jhn - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt"
        ),
        notes="NT source segment for Matthew through John.",
    ),
    _step_source(
        source_id="step_tagnt_act_rev",
        title="TAGNT Act-Rev - Translators Amalgamated Greek NT",
        filename="step_tagnt_act_rev.txt",
        path=(
            "Translators Amalgamated OT+NT/"
            "TAGNT Act-Rev - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt"
        ),
        notes="NT source segment for Acts through Revelation.",
    ),
    _step_source(
        source_id="step_tbesg",
        title="TBESG - Translators Brief lexicon of Extended Strongs for Greek",
        filename="step_tbesg.txt",
        path=(
            "Lexicons/"
            "TBESG - Translators Brief lexicon of Extended Strongs for Greek - "
            "STEPBible.org CC BY.txt"
        ),
        notes="Brief Greek lexicon source for dictionary build inputs.",
    ),
    _step_source(
        source_id="step_tflsj_0_5624",
        title="TFLSJ 0-5624 - Translators Formatted full LSJ Bible lexicon",
        filename="step_tflsj_0_5624.txt",
        path=(
            "Lexicons/"
            "TFLSJ  0-5624 - Translators Formatted full LSJ Bible lexicon - "
            "STEPBible.org CC BY.txt"
        ),
        notes="Formatted LSJ entries up to G5624.",
    ),
    _step_source(
        source_id="step_tflsj_extra",
        title="TFLSJ extra - Translators Formatted full LSJ Bible lexicon",
        filename="step_tflsj_extra.txt",
        path=(
            "Lexicons/"
            "TFLSJ extra - Translators Formatted full LSJ Bible lexicon - "
            "STEPBible.org CC BY.txt"
        ),
        notes="Additional formatted LSJ entries.",
    ),
    _step_source(
        source_id="step_tegmc",
        title="TEGMC - Translators Expansion of Greek Morphology Codes",
        filename="step_tegmc.txt",
        path=(
            "Morphology codes/"
            "TEGMC - Translators Expansion of Greek Morphhology Codes - "
            "STEPBible.org CC BY.txt"
        ),
        notes="Greek morphology code explanations.",
    ),
    SourceSpec(
        source_id="crosswire_lxx",
        title="CrossWire SWORD LXX - Septuagint, Morphologically Tagged Rahlfs'",
        filename="crosswire_lxx.zip",
        source_url="https://crosswire.org/ftpmirror/pub/sword/packages/rawzip/LXX.zip",
        source_page_url=CROSSWIRE_LXX_MODINFO_URL,
        version=CROSSWIRE_LXX_VERSION,
        source_commit=None,
        license_name=CROSSWIRE_LXX_LICENSE_NAME,
        license_url=CROSSWIRE_LXX_LICENSE_URL,
        notes=(
            "Owner-approved for this project under CrossWire's free non-commercial "
            "distribution terms."
        ),
    ),
)

SOURCE_SPECS_BY_ID = {source.source_id: source for source in SOURCE_SPECS}

