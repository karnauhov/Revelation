# Ukrainian stage 7 validation log

Date: `2026-08-15`
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
- frozen gold accepted decisions: `0` — BLOCKER
- independent gold pass 2: missing — BLOCKER
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
