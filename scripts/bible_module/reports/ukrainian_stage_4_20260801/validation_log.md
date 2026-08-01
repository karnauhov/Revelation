# Validation log: Ukrainian Bible stage 4

Date: 2026-08-01

Scope: source-native parsers, normalization, footnote extraction/binding, deterministic work artifacts, safe reports and roadmap closure.

Runtime/Flutter changes: none. Stage 5 projection, Strong alignment, `target_comment`, SQLite and content tool changes: not performed.

## Locked-input gate

- `python -m scripts.bible_module.ukrainian_stage_3_sources --check` — PASS; all 14 locked cache files verified by expected byte size and SHA-256 before parsing.
- Stage-4 parsers call the same fail-closed verification independently before reading their format. Corrupt/unverified fixture and post-1990 UBT tests — PASS.
- No floating `latest`, `main`, `master` or `HEAD` input was used.

## Generation and deterministic replay

- `python -m scripts.bible_module.ukrainian_stage_4 --generate` — PASS twice on the final implementation.
- Each run parsed 14 sources and wrote 14 normalized JSONL files in `scripts/bible_module/work/ukrainian_stage_4_20260801/`.
- Final generator result: `normalized_count=14`, `diff_row_count=91569`, `warning_count=12`, `unresolved_footnote_count=11`.
- SHA-256/size comparison of all 37 generator-managed work/report artifacts after the two final runs — PASS: 37 compared, 0 differences. The separately maintained validation log is excluded from that generator-replay count.
- `python -m scripts.bible_module.ukrainian_stage_4 --check` — PASS after this log was created; every normalized file matches its checked-in manifest size and SHA-256.

## Full normalized-corpus invariants

Streaming audit of all 14 JSONL files:

- records: 177,629;
- footnote uses: 1,329;
- unique footnote definitions: 1,204;
- printed markers resolved from page-local carrier order: 1,329; without marker: 0;
- duplicate `use_id`: 0;
- conflicting text for one `footnote_id`: 0;
- invalid `anchor_start_scalar`/`anchor_end_scalar` range: 0;
- unstable/decreasing `source_order`: 0;
- missing provenance: 0;
- premature `verse_key`, target projection or comment/alignment fields: 0;
- every record has `projection_status=unprojected`.

Wikisource carrier inventory and resolved entities:

- `<ref...>` openings: 1,329;
- paired closings/definitions: 1,204;
- self-closing named uses: 125;
- `{{reflist...}}`: 735;
- `{{anchor...}}`: 2,201;
- unique definitions: 1,204;
- uses after named/self-closing resolution: 1,329;
- unambiguous source-verse bindings: 1,318;
- missing bindings: 11, all inside classified heading templates;
- ambiguous/unresolved bindings: 0/0;
- source verses with footnotes: 1,222; with multiple footnotes: 90.

Each marker is stored per use with its page-local `ref` ordinal and carrier provenance; self-closing named reuse keeps the definition identity but receives its own use marker. The 11 missing heading anchors are retained in `unresolved_footnotes.jsonl` without automatic nearest-verse attachment. OCR comparison against Commons found 641 exact normalized containments, 414 partial OCR evidences and 149 items requiring later visual print review. These 149 items retain full gitignored text plus page/revision/digest provenance and are not parser losses.

## Independent comparisons

- Commons vs dependent Internet Archive control: 1,538 pages compared, 0 hidden-OCR differences.
- TAHOT vs dependent OSHB control: 21,178 common source refs; all differences retained in the safe diff.
- OSHB vs independent UXLC surface control: 23,213 common source refs.
- TAGNT vs independent UGNT: 7,948 common source refs plus 10 source-native numbering/presence differences.
- TAGNT vs CrossWire KJV classic-Strong control: 7,948 common source refs plus 9 source-native presence differences.
- `source_diff.csv`: 91,569 rows — 89,366 informational, 2,203 medium, 0 high/critical. No discrepancy was silently corrected.

## Tests and project quality gates

- `python -m unittest scripts.bible_module.tests.test_ukrainian_stage_4` — PASS, 15 tests.
- `python -m unittest discover -s scripts/bible_module/tests` — PASS, 136 tests in 4.390 s (121 clean baseline tests plus 15 stage-4 tests).
- `python -m unittest discover -s scripts/content_tool/tests` — PASS, 30 tests in 2.914 s.
- `dart format .` — PASS, 475 files checked, 0 changed in 15.77 s.
- `flutter analyze` — PASS, no issues found in 152.7 s.
- `flutter test` — PASS, 920 tests in 2 min 11 s; matches the documented clean baseline.
- `dart run scripts/check_forbidden_patterns.dart` — PASS, all forbidden-pattern checks passed.
- `dart run scripts/check_docs_sync.dart` — PASS for all four approved RU/EN pairs.
- Smoke test — N/A: no runtime, startup, routing, deep-link, screen or user-flow code changed; only offline Python tooling, fixtures, reports and the Russian content roadmap changed.
- Coverage — N/A: no runtime code or high-risk state-management flow changed.
- `git diff --check` — PASS; only Git's existing Windows LF-to-CRLF notices were emitted.

## Repository, security and size audit

- Secret-pattern scan of every added/modified stage-4 file — PASS; no API key, auth token or private credential detected.
- Added-file audit — PASS; no source DjVu/ZIP/XML corpus, SQLite, executable or other source binary is tracked.
- Fixture audit — PASS; fixtures are short, synthetic and declared CC0-1.0.
- Safe-report audit — PASS; `source_diff.csv`, JSON reports and manifests contain identifiers, counters and digests, not the full Ukrainian text or full footnote corpus.
- `git check-ignore` — PASS for `scripts/bible_module/source_cache/*`, all full normalized JSONL files and the derived Commons logical DjVu container under `scripts/bible_module/work/*`.
- The only tracked entry under `scripts/bible_module/work/` is `.gitkeep`.

## Exit decision

PASS. Every mandatory machine source was parsed independently, every input line/member/revision/carrier is processed or explicitly classified, all footnotes are traceable and either source-verse-bound or listed as a non-verse heading anomaly, and unresolved critical/high defects equal zero. Stage 4 is complete. Stage 5 was not executed.
