# Ukrainian stage 7 validation log

Date: `2026-09-05`
Schema-Version: `1`
Contract: `ukrainian-stage-7-evidence-alignment-v1`
Status: `blocked_before_gold_and_alignment_acceptance`
Processed: `31102` target positions
Skipped: `682836` original components (no production assignment)
Errors: `0` generator errors

## Generation invariants

- stage-6 text SHA-256: `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf` — PASS
- stage-6 manifest SHA-256: `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af` — PASS
- stage-6 comments SHA-256: `5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4` — PASS
- author footnote uses: `1329` total,
  `7` textual-variant notes,
  automatic vote `0` — PASS / MANUAL-REVIEW GATE
- exact target positions: `31102` — PASS
- exact scalar/byte token round-trip: `595077` tokens — PASS
- raw original parser errors: `0` — PASS
- raw OSHB/UXLC/UGNT controls: `751557` tokens — PASS
- original-control crosswalk unresolved/service: `118965` — EXPLICIT FAIL-CLOSED
- production Strong markers emitted: `0` — EXPECTED FAIL-CLOSED
- complete blind gold pass 1: `2171` verses / `45831` original /
  `41807` target decisions, 66 distinct shard reviewers, `error_count=0` — PASS
  AS NONFINAL INPUT
- frozen finalized gold accepted decisions: `0` — BLOCKER
- independent gold pass 2 and comparison: complete for `Gen–2Chr` (`459`
  verses / `12220` original / `10120` target); `Ezra–Rev` missing — BLOCKER
- post-blind comparison `1Sam–1Kgs`: `5274` stable decisions, `2793`
  alignment agreements, all `2481` substantive disagreements resolved by
  distinct adjudicators; exact overlay accounting and independent QC of `1128`
  unique rows passed with `error=0`, `uncertain=0` — PASS FOR THIS BATCH
- post-blind comparison `2Kgs–2Chr`: `4824` stable decisions, `3793`
  alignment agreements and `1031` substantive disagreements routed to
  distinct adjudication — PASS / MANUAL-ADJUDICATION GATE
- `Gen` third adjudication + full independent QC: `230/230` disagreements,
  `1507/1507` overlay decisions, `15/15` high, `4/4` new, `error=0`,
  `uncertain=0` — PASS FOR THIS BOOK
- `Exod` third adjudication structural validator: `130/130`, overlay
  `1382/1382` — STRUCTURAL PASS; full independent content-QC: `124` accepted,
  `6` error, `0` uncertain — BLOCKED pending explicit consensus correction
- `Lev` third adjudication structural validator: `216/216`, overlay
  `1395/1395` — STRUCTURAL PASS; independent content-QC checkpoint:
  `145/216` accepted, `71` remaining, status `partial_not_accepted` — PAUSED
- A_auto Wilson lower bound ≥99.5%: not calibrated — BLOCKER
- unresolved critical/high: `14` — BLOCKER
- stage 8 / SQLite: not run — PASS

## Repository-wide commands

- `python -m scripts.bible_module.ukrainian_stage_3_sources --check` — PASS,
  source lock/cache verified, `source_count=14`.
- `python -m scripts.bible_module.ukrainian_stage_4 --check` — PASS (exit 0).
- `python -m scripts.bible_module.ukrainian_stage_5 --check` — PASS,
  `{"stage":5,"status":"verified"}`.
- `python -m scripts.bible_module.ukrainian_stage_6 --check` — PASS,
  `{"stage":6,"status":"verified"}`.
- focused gold/compact/shard/external contract subset — PASS, `36` tests,
  включая metadata-only consensus, exact disagreement-set adjudication и
  запрет подмены согласованного решения.
- `python -m unittest discover -s scripts/bible_module/tests` — PASS, `395`
  tests.
- `python -m unittest discover -s scripts/content_tool/tests` — PASS, `30`
  tests; content tool was not changed.
- `dart format .` under current Dart `3.13.2` — command completed, but proposed
  formatter-only edits to four unrelated Flutter tests; all four were restored
  byte-equivalent to `HEAD` because Flutter is outside stage-7 scope.
- `flutter analyze` under current Flutter `3.47.2` — FAIL, `8` warnings in
  pre-existing Flutter files (`topic_screen.dart`, `sentry_app_runner.dart`,
  `database_version_loader.dart`). Its automatic `analysis_options.yaml` and
  `pubspec.lock` migrations were fully restored; stage 7 changed no Flutter
  source/config/dependency. A clean analyzer run remains required before final
  closure.
- `flutter test --no-pub` under current Flutter `3.47.2` — FAIL after a full
  completed run: `918` tests passed and `2` pre-existing Strong-dictionary widget
  tests failed because expected preview strings (`verse text`, `fourth verse`)
  were absent. A focused rerun of
  `test/features/strongs_dictionary/presentation/widgets/strong_dictionary_entry_view_test.dart`
  reproduced exactly the same `1` pass / `2` failures. Stage 7 changed no
  Flutter source or tests; a clean full run remains required before final closure.
- `dart run scripts/check_forbidden_patterns.dart` — PASS.
- `dart run scripts/check_docs_sync.dart` — PASS, all approved RU/EN pairs.
- double deterministic generation — PENDING after all current candidate and
  fingerprint artifacts are integrated.
- smoke integration — N/A: runtime, startup, routes and deep links were not changed.
- `git diff --check` — PASS at the 2026-09-05 pause checkpoint (only expected
  LF/CRLF conversion warnings); all six newly versioned batch manifests parse
  as JSON — PASS. Final secrets/binaries/full-corpus/gitignore audit remains
  pending for the final regression run; SQLite count created/modified by stage
  7 remains `0`.
