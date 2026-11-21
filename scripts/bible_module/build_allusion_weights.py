"""Reproduce semantic weights and bounded ranking evaluation for Greek Strong IDs.

No legacy text or dictionary definitions are copied. Optional legacy input reads
only the owner's numeric decisions, for the comparison column in the audit.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3

if __package__:
    from .allusion_weight_policy import POLICY_FILE, compact_policy, read_policy
else:
    from allusion_weight_policy import POLICY_FILE, compact_policy, read_policy

ROOT = Path(__file__).resolve().parents[2]
GREEK_TOKEN = re.compile(r"(?<!\S)[Gg](\d+)(?!\S)")
QUANTIFIERS = {243, 537, 1543, 2087, 3745, 3956, 5108, 5118}
COPULAS = {1510, 1511, 2070, 2071, 2258}
DISCOURSE = {2400}  # ἰδού (behold), a frequent attention marker


def semantic_weight(number: int, word: str, category: str,
                    weak_numbers: set[int]) -> tuple[float, str]:
    if not word.strip():
        return 0.0, "unused_dictionary_slot"
    if number in weak_numbers:
        return 0.0, "weak_grammatical_word"
    if "Neg" in category:
        return 0.35, "negation"
    if "@pron" in category:
        return 0.15, "pronoun"
    if number in COPULAS:
        return 0.25, "copula"
    if number in QUANTIFIERS:
        return 0.35, "quantifier"
    if "@particle" in category or "@conj" in category:
        return 0.2, "grammatical_connector"
    if number in DISCOURSE or any(
        tag in category for tag in ("@advInt", "@advCor", "@interj", "@prefix")
    ):
        return 0.25, "discourse_or_deictic_word"
    if not category.strip():
        raise ValueError(f"G{number} has a lemma but no category")
    return 1.0, "lexical_word"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs():
    lexicon_path = ROOT / "web/db/revelation.sqlite"
    corpus_path = ROOT / "web/db/bible_lxx_tr.sqlite"
    weak_path = ROOT / "assets/data/greek_weak_strong_numbers.json"
    with closing(sqlite3.connect(lexicon_path.as_uri() + "?mode=ro", uri=True)) as db:
        lexicon = db.execute("SELECT id, word, category FROM greek_words ORDER BY id").fetchall()
    with closing(sqlite3.connect(corpus_path.as_uri() + "?mode=ro", uri=True)) as db:
        corpus = {int(key, 36): {int(n) for n in GREEK_TOKEN.findall(text)}
                  for key, text in db.execute("SELECT verse_key, text FROM verses WHERE trim(text) <> ''")}
        revision = dict(db.execute("SELECT key, value FROM db_metadata "
                                   "WHERE key IN ('schema_version','data_version','date')"))
    verse_map = json.loads((ROOT / "assets/data/bible_verse_map.json").read_text(encoding="utf-8"))
    references = [None] + [(book["id"], chapter, verse)
                           for book in verse_map["books"]
                           for chapter, count in enumerate(book["chapters"], 1)
                           for verse in range(1, count + 1)]
    weak_json = json.loads(weak_path.read_text(encoding="utf-8"))
    weak = {int(code[1:]) for group in weak_json["excluded_strong_numbers_by_category"].values()
            for code in group}
    if [row[0] for row in lexicon] != list(range(1, 5625)):
        raise ValueError("Expected all 5,624 Greek dictionary positions")
    unknown = {number for numbers in corpus.values() for number in numbers} - {
        row[0] for row in lexicon
    }
    if unknown:
        raise ValueError(f"Unclassified corpus numbers: {sorted(unknown)}")
    return lexicon, corpus, references, weak, revision, {
        "lexicon_sha256": digest(lexicon_path),
        "corpus_sha256": digest(corpus_path),
        "weak_list_sha256": digest(weak_path),
    }


def evaluate(corpus, references, entries, legacy):
    """Diagnostic pairs, not an exhaustive gold standard for allusions."""
    ordinals = {reference: ordinal for ordinal, reference in enumerate(references) if reference}
    cases = [((40, 4, 4), (5, 8, 3)), ((40, 4, 7), (5, 6, 16)),
             ((40, 4, 10), (5, 6, 13)), ((40, 22, 37), (5, 6, 5)),
             ((40, 22, 39), (3, 19, 18)), ((58, 1, 5), (19, 2, 7)),
             ((58, 1, 7), (19, 104, 4)), ((66, 2, 27), (19, 2, 9)),
             ((66, 21, 4), (23, 25, 8)), ((66, 1, 7), (27, 7, 13)),
             ((58, 1, 5), (1, 31, 43)), ((66, 21, 4), (1, 13, 10)),
             ((40, 4, 7), (6, 24, 26))]
    df = Counter(number for numbers in corpus.values() for number in numbers)
    size = len(corpus)
    weights = {n: entry["weight"] * min(4.0, 1 + math.log((size + 1) / (df[n] + 1)))
               for n, entry in entries.items()}
    totals = {ordinal: sum(weights[n] for n in numbers) for ordinal, numbers in corpus.items()}
    old = {n: entry["legacy_weight"] for n, entry in entries.items()}
    observed = []
    for source, target in cases:
        source_numbers = corpus[ordinals[source]]
        ranked = {}
        counts = {}
        for mode, terms in (("legacy", old), ("weighted", weights)):
            rows = []
            for ordinal, numbers in corpus.items():
                if references[ordinal][0] > 39:
                    continue
                common = source_numbers & numbers
                meaningful = sum((terms[n] > 0 if mode == "legacy" else entries[n]["weight"] >= 0.5)
                                 for n in common)
                if meaningful < 3:
                    continue
                score = sum(terms[n] for n in common)
                if mode == "weighted":
                    score = 2 * score / (totals[ordinal] + totals[ordinals[source]])
                rows.append((-score, ordinal))
            rows.sort()
            ordered = [ordinal for _, ordinal in rows]
            target_ordinal = ordinals[target]
            ranked[mode] = ordered.index(target_ordinal) + 1 if target_ordinal in ordered else None
            counts[mode] = len(rows)
        observed.append({"source": source, "target": target, "rank": ranked, "candidates": counts})
    return observed


def read_legacy(path: Path) -> dict[int, float]:
    raw = path.read_text(encoding="utf-8-sig")
    body = re.sub(r",\s*([}\]])", r"\1", raw[raw.index("{"):raw.rindex("}") + 1])
    prior = json.loads(body)
    if "words" in prior:
        return {int(row["id"][1:]): row["weight"] for row in prior["words"]}
    return {int(code[1:]): entry["legacy_weight"] for code, entry in prior["entries"].items()}


def build(legacy_path: Path | None):
    lexicon, corpus, references, weak, revision, hashes = load_inputs()
    version, weights = read_policy()
    if len(weights) != len(lexicon) + 1:
        raise ValueError("Greek weight policy and lexicon cover different Strong ranges")
    hashes["policy_sha256"] = digest(POLICY_FILE)
    legacy = None
    if legacy_path is not None:
        legacy = read_legacy(legacy_path)
        if any(row[0] not in legacy for row in lexicon):
            raise ValueError("Legacy comparison must cover every Greek Strong number")
        hashes["legacy_weights_sha256"] = digest(legacy_path)
    ot_df, nt_df = Counter(), Counter()
    for ordinal, numbers in corpus.items():
        (ot_df if references[ordinal][0] <= 39 else nt_df).update(numbers)
    entries = {}
    for number, word, category in lexicon:
        suggested, reason = semantic_weight(number, word, category, weak)
        weight = weights[number]
        entries[number] = {"weight": weight, "reason": reason,
                           "verses_ot": ot_df[number], "verses_nt": nt_df[number]}
        if weight != suggested:
            entries[number].update(reason="reviewed_override", suggested_weight=suggested,
                                   suggested_reason=reason)
        if legacy is not None:
            entries[number]["legacy_weight"] = legacy[number]
    payload = {"schema_version": 1, "policy_version": version,
               "provenance": {**hashes, "module": "lxx_tr", "revision": revision},
               "frequency_policy": "runtime IDF = min(4, 1 + ln((N+1)/(df+1))); unique Greek IDs per verse",
               "entries": {f"G{n}": entry for n, entry in entries.items()}}
    evaluation = evaluate(corpus, references, entries, legacy) if legacy is not None else []
    return payload, evaluation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy", type=Path,
                        help="BibleAllusions numeric table or an earlier full audit containing legacy_weight")
    parser.add_argument("--audit", "--output", type=Path, dest="audit",
                        help="Write full per-number audit JSON (counts, reasons, optional legacy decisions)")
    parser.add_argument("--report", type=Path, help="Write the human-readable audit report")
    parser.add_argument("--propose-policy", type=Path,
                        help="Export the category-based proposal for comparison with the reviewed policy")
    args = parser.parse_args()
    payload, evaluation = build(args.legacy)
    if args.audit:
        args.audit.parent.mkdir(parents=True, exist_ok=True)
        args.audit.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.propose_policy:
        entries = {key: {"weight": value.get("suggested_weight", value["weight"])}
                   for key, value in payload["entries"].items()}
        proposal = compact_policy(entries, payload["policy_version"])
        args.propose_policy.parent.mkdir(parents=True, exist_ok=True)
        args.propose_policy.write_bytes((json.dumps(proposal, indent=2) + "\n").encode())
    classes = Counter(entry["reason"] for entry in payload["entries"].values())
    lines = ["# REV319 Greek Strong weights", "", "## Policy", "",
             "Semantic weights are retrieval heuristics. The table covers G1-G5624.",
             "All 77 weak grammatical numbers remain zero. Pronouns get 0.15, negation 0.35,",
             "copulas 0.25, quantifiers 0.35, remaining connectors 0.2, deictic/discourse words",
             "0.25 and lexical words 1.0. Empty dictionary slots get zero.",
             "Frequency is recomputed from the current corpus. IDF is capped at 4.",
             "Verse ranking uses weighted Dice, 2*shared/(source+target), to limit long-verse noise.",
             "Chapter/book groups use weighted unique source coverage, preserving group-level semantics.",
             "Verse candidates require three distinct lexical words (semantic weight >= 0.5).",
             "Low-weight words affect ordering only after that admission rule is met.", "",
             "Each number has a reason, separate OT/NT verse counts and optional legacy weight.",
             "Corpus, lexicon and policy input SHA-256 values are in the table.", "", "## Coverage", "",
             *(f"- {reason}: {count}" for reason, count in sorted(classes.items())), "",
             "## Diagnostic references", "",
             "The first ten pairs are diagnostic references, including difficult Revelation echoes.",
             "The final three compare incidental word overlap in different contexts.",
             "Null rank means that the lexical admission rule excluded the target.",
             "Candidate counts measure search volume, not the number of false positives.",
             "No overall precision or scholarly confirmation of an allusion is claimed.", "",
             "| Source | Target | Legacy rank | Weighted rank | Legacy candidates | Weighted candidates |",
             "| --- | --- | --- | --- | --- | --- |"]
    for row in evaluation:
        lines.append(f"| {row['source']} | {row['target']} | {row['rank']['legacy']} | "
                     f"{row['rank']['weighted']} | {row['candidates']['legacy']} | {row['candidates']['weighted']} |")
    lines += ["", "## Storage and maintenance", "",
              "Edit scripts/bible_module/data/greek_strong_weights.json to maintain the shared policy. "
              "It stores the default weight and exceptions. Use --audit to export the per-number evidence.",
              "The module builder and content publisher embed revision-specific posting lists. "
              "After editing this policy, rebuild the bundled index with python -m scripts.bible_module.build_allusion_index. "
              "IDF is computed from the postings for the active corpus.",
              "Re-run this script with the current DBs after data changes and inspect category/coverage drift.",
              "The numeric lexical policy is independent of UI language and translation selection.", "",
              "## Sources", "",
              "- Current project Greek lexicon and LXX/TR, identified by the table digests.",
              "- Owner-authored BibleAllusions numeric weights, when --legacy is supplied.",
              "- Manning et al., Introduction to Information Retrieval, inverse document frequency:",
              "  https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html",
              "- de la Selle and Mellerin, 2026, Detection and Typology of Psalmic Text Reuses:",
              "  https://www.mdpi.com/2077-1444/17/1/88", "",
              "The coefficient values and admission rule are project decisions. The sources motivate",
              "frequency discrimination and retaining grammatical context, not these exact coefficients.",
              "", "## Limits", "",
              "Classification covers every number using the current lexicon's POS tags and explicit overrides.",
              "It is not an independent manual philological review of each lemma in every context.",
              "Strong identity misses synonyms and conceptual echoes. Verse boundaries, missing tags and",
              "translation variants affect ranks. Source boilerplate can dilute a short quoted phrase.",
              "This small diagnostic set helped select normalization and is not held-out evaluation.",
              "Do not equate its results or lexical scores with proof of a biblical allusion."]
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"positions": len(payload["entries"]), "classes": classes,
                      "diagnostic_pairs": evaluation}, ensure_ascii=False))


if __name__ == "__main__":
    main()
