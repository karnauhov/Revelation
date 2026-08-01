# Validation log: Ukrainian stage 5

- Date: 2026-08-01
- Mapping contract: `oh1988-kjv-protestant-v1`
- Generation status: PASS
- Source records: 31160 / 31160
- Target positions: 31102 / 31102
- Footnote uses: 1329 / 1329
- Footnote markers: 1329 / 1329
- Duplicate target keys: 0
- Forward/reverse consistent: PASS
- Nearest-verse fallback: NOT USED
- Target comment: NOT CREATED
- Strong alignment: NOT PERFORMED
- SQLite/content tool/Flutter: NOT CHANGED
- Smoke: N/A; runtime, startup, routes and deep links were not changed.

## Final command results

- `python -m scripts.bible_module.ukrainian_stage_3_sources --check`: PASS; 14 locked sources verified.
- `python -m scripts.bible_module.ukrainian_stage_4 --check`: PASS; 14 normalized source manifests verified.
- `python -m scripts.bible_module.ukrainian_stage_5 --check`: PASS.
- Targeted stage-5 tests: PASS; 22 tests.
- Double deterministic generation: PASS; all 19 artifacts matched byte-for-byte.
- `python -m unittest discover -s scripts/bible_module/tests`: PASS; 158 tests.
- `python -m unittest discover -s scripts/content_tool/tests`: PASS; 30 tests.
- `dart format .`: PASS; 475 files, 0 changed.
- `flutter analyze`: PASS; no issues found.
- `flutter test`: PASS; 920 tests.
- `dart run scripts/check_forbidden_patterns.dart`: PASS; all checks.
- `dart run scripts/check_docs_sync.dart`: PASS; all four RU/EN pairs.
- `git diff --check`: PASS.
- Secret/binary/full-corpus/gitignore audit: PASS; reports contain no canonical verse corpus or tokens, only safe identifiers/digests and 11 required heading-footnote records; all full maps remain ignored under `scripts/bible_module/work/`.
- Smoke: N/A; this stage changed only offline Python mapping tooling, tests, reports, fixtures, and roadmap documentation.
