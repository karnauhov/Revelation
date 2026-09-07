# Ukrainian stage 7 validation log

Date: `2026-09-08`
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
- independent gold pass 2 and comparison: complete for `Gen–Isa` (`814`
  verses / `19207` original / `16692` target); `Jer–Rev` missing — BLOCKER
- repeated post-blind comparison `Deut`: `1562` stable decisions, `1363`
  alignment agreements and `199` substantive disagreements; two independent
  outputs and manifests are byte-identical, all four physical SHA locks match
  `gold_review_batch_005.manifest.json`; distinct third adjudication resolved
  `199/199`, preserved grid `1562/1562`, all `91` high and frozen `Deut.32.8`
  primary-MT fingerprint, unresolved/error `0`; deterministic reproduction
  passed; distinct QC audited `199/199`, all high/new, 33/33 template verses and
  grid `1562/1562`, `error=0`, `uncertain=0`; root generic/canonical/SHA audit
  passed — PASS FOR THIS BOOK
- post-blind comparison `1Sam–1Kgs`: `5274` stable decisions, `2793`
  alignment agreements, all `2481` substantive disagreements resolved by
  distinct adjudicators; exact overlay accounting and independent QC of `1128`
  unique rows passed with `error=0`, `uncertain=0` — PASS FOR THIS BATCH
- post-blind comparison `2Kgs–2Chr`: `4824` stable decisions, `3793`
  alignment agreements and `1031` substantive disagreements routed to
  distinct adjudication; subsequent separate adjudication and QC are recorded
  below — PASS FOR COMPARISON CHECKPOINT
- post-blind comparison `Ezra`: `1601` stable decisions, `1110` alignment
  agreements and `491` substantive disagreements routed to distinct
  adjudication; subsequent separate adjudication and QC are recorded below —
  PASS FOR COMPARISON CHECKPOINT
- `Ezra` distinct third adjudication: `491/491` disagreements in `259`
  components, `1110` preserved agreements, full overlay `1601/1601`, all `27`
  critical and `268` high resolved, unresolved critical/high `0`; distinct full
  QC audited `491/491`, exact grid `1601/1601`, stage-6 text/comments and all
  SHA locks, `error=0`, `uncertain=0`; generic validator plus root
  canonical/unique/SHA audit passed — PASS FOR THIS BOOK
- post-blind comparison `Neh`: `1106` stable decisions, `868` alignment
  agreements and `238` substantive disagreements; distinct third adjudication
  resolved `238/238`, preserved grid `1106/1106`, all `3` critical and `18`
  high, unresolved/error `0`; initial QC found exactly `7` high errors in
  `Neh.6.7`/`Neh.12.47`; seven-row correction plus post-correction QC accepted
  `247/247` observations / `240` unique IDs and grid `1106/1106`, while critical
  `Neh.13.27` remains fail-closed, `error=0`, `uncertain=0`; root
  correction-QC/canonical/SHA audit passed — PASS FOR THIS BOOK
- post-blind comparison `Esth`: `1938` stable decisions, `461` alignment
  agreements and `1477` substantive disagreements; distinct third adjudication
  resolved `1477/1477` in `382` components, full grid `1938/1938`, all `401`
  high, unresolved/error `0`; distinct QC audited every row/component/high/new,
  grid `1938/1938`, `error=0`, `uncertain=0`; root generic/canonical/SHA audit
  passed — PASS FOR THIS BOOK
- post-blind comparison `Job`: `870` stable decisions, `627` alignment
  agreements and `243` substantive disagreements; distinct adjudication
  resolved `243/243` in `105` components, preserved grid `870/870`, resolved
  all `4` critical and `122` high, including primary-MT `Job.39.18`, with
  unresolved/error `0`; distinct QC accepted `243/243`, all `122` high, `4`
  critical and `5` new components, exact grid `870/870`, `error=0`,
  `uncertain=0`; generic validator and double canonical regeneration passed —
  PASS FOR THIS BOOK
- post-blind comparison `Ps`: `3261` stable decisions, `1589` alignment
  agreements and `1672` substantive disagreements; distinct adjudication
  resolved `1672/1672` in `632` components and preserved grid `3261/3261`.
  Distinct fail-closed QC checked all `1672` rows, `632` components, `930` high,
  `64` new, `97` verses and grid `3261/3261`: `1659` accepted, `13` error,
  `0` uncertain. All errors are confined to `Ps.61.1`, `Ps.70.1`, `Ps.80.1`,
  where H9012 must link separately to `же/ж`; blocking QC/sidecar SHA-256 are
  `6b3acd2e…` / `6ed953cc…`, deterministic regeneration passed —
  PASS FOR BLOCKING QC. Exact correction changed only the scoped `13` high
  rows (`6` original + `7` target), preserved the other `1659` adjudication
  rows and grid `3261/3261`; double `check-correction` passed, correction and
  corrected-adjudication SHA pairs are `57c57e7d…` / `7c68870a…` and
  `2e1d6495…` / `1bcc754d…`. Distinct post-correction QC accepted `1688/1688`
  observations over `1672` unique IDs, all `632` components, `930` high, `97`
  verses and grid `3261/3261`; `error=0`, `uncertain=0`. Double validator and
  root `16/16` SHA audit passed; QC/sidecar `f5858df0…` / `67e699c4…` —
  PASS FOR THIS BOOK
- post-blind comparison `Prov`: `813` stable decisions, `649` alignment
  agreements and `164` substantive disagreements; distinct adjudication and
  QC accepted all `164`, including `5` critical, `93` high and `11` new rows,
  with grid `813/813`, `error=0`, `uncertain=0`; generic validator passed twice
  and all `10/10` physical SHA locks matched — PASS FOR THIS BOOK
- post-blind comparison `Eccl`: `1405` stable decisions, `970` alignment
  agreements and `435` substantive disagreements (`307` original + `128`
  target); distinct adjudication resolved `435/435` in `229` components,
  preserved grid `1405/1405`, resolved all `2` critical and `186` high with
  unresolved `0`; distinct QC audited `435/435`, all critical/high/new and grid
  `1405/1405`, while preserving the explicit `Eccl.2.25` person divergence and
  excluding unresolved `Eccl.9.2`; double validator and 10/10 SHA audit passed,
  `error=0`, `uncertain=0` — PASS FOR THIS BOOK
- post-blind comparison `Song`: `1200` stable decisions, `591` alignment
  agreements and `609` substantive disagreements (`346` original + `263`
  target); distinct adjudication resolved `609/609` in `207` components,
  preserved grid `1200/1200`, selected `385` pass-1, `115` pass-2 and `109`
  declared-new rows, and resolved all `21` critical and `142` high with no
  unresolved critical/high; distinct QC audited `609/609`, all 207 components,
  all critical/high/new and grid `1200/1200`; double validator and 10/10 SHA
  audit passed, `error=0`, `uncertain=0` — PASS FOR THIS BOOK
- post-blind comparison `Isa`: `1365` stable decisions, `1113` alignment
  agreements and `252` substantive disagreements (`183` original + `69`
  target); blind pass 2 exact-once/compact checks passed twice, `Isa.7.14` and
  `Isa.53.5` remained fail-closed, root comparison is byte-identical and all
  `4/4` SHA locks match `gold_review_batch_023.manifest.json` —
  PASS / MANUAL-ADJUDICATION GATE
- `2Kgs` distinct third adjudication + full independent QC: `402/402`
  disagreements, `1316` preserved agreements, full overlay `1718/1718`, all
  `114/114` high, exact stage-6 text/comments `32/32`, `error=0`, `uncertain=0`,
  unresolved critical/high `0` — PASS FOR THIS BOOK
- `1Chr` distinct third adjudication + full independent QC: `273/273`
  disagreements, `991` preserved agreements, full overlay `1264/1264`, all
  `126/126` high, exact stage-6 text/comments `32/32`, `error=0`, `uncertain=0`,
  unresolved critical/high `0` — PASS FOR THIS BOOK
- `2Chr` distinct third adjudication + full independent QC: `356/356`
  disagreements, `1486` preserved agreements, full overlay `1842/1842`, all
  `96/96` high, exact stage-6 text/comments `34/34`, `error=0`, `uncertain=0`,
  unresolved critical/high `0` — PASS FOR THIS BOOK
- `Num` distinct third adjudication + full independent QC: `310/310`
  disagreements, `1186` preserved agreements, full overlay `1496/1496`, all
  `56/56` high and `22/22` new checked, exact stage-6 text/comments `33/33`,
  `error=0`, `uncertain=0`, unresolved critical/high `0` — PASS FOR THIS BOOK
- `Josh` distinct third adjudication + full independent QC: `464/464`
  disagreements, `1102` preserved agreements, full overlay `1566/1566`, all
  `33/33` high and `59/59` new checked, exact stage-6 text/comments `32/32`,
  `error=0`, `uncertain=0`, unresolved critical/high `0` — PASS FOR THIS BOOK
- universal `check-adjudication-qc`: real `Lev` 216/1395, `Num` 310/1496,
  `Josh` 464/1566, `Judg` 562/1749, `Ruth` 252/1585, `2Kgs` 402/1718,
  `1Chr` 273/1264 and `2Chr` 356/1842 plus 16 focused
  positive/negative tests, including explicit alignment/semantic selection
  basis and fail-closed mixed-category rejection — PASS
- `Judg` distinct third adjudication + full independent QC: `562/562`
  disagreements, `1187` preserved agreements, full overlay `1749/1749`, all
  `40/40` high, exact stage-6 text/comments `33/33`, `error=0`, `uncertain=0`,
  unresolved critical/high `0` — PASS FOR THIS BOOK
- `Ruth` distinct third adjudication + full independent QC on accepted
  external pass 1 v3 and independent pass 2 v2 only: `252/252` disagreements,
  `1333` preserved agreements, full overlay `1585/1585`, all `56/56` high,
  exact stage-6 text/comments `32/32`, rejected over-grouped pass 2 excluded,
  `error=0`, `uncertain=0`, unresolved critical/high `0` — PASS FOR THIS BOOK
- `Gen` third adjudication + full independent QC: `230/230` disagreements,
  `1507/1507` overlay decisions, `15/15` high, `4/4` new, `error=0`,
  `uncertain=0` — PASS FOR THIS BOOK
- `Exod` third adjudication structural validator: `130/130`, overlay
  `1382/1382` — STRUCTURAL PASS; full independent content-QC: `124` accepted,
  `6` error, `0` uncertain. Separate SHA-locked correction contains exact `9`
  allowed changes in `3` verses and preserves the full `1382/1382` grid.
  Distinct post-correction QC checked `130 + 9 + 3 = 142` observations / `136`
  unique stable IDs, all `42/42` high and `22/22` affected verses,
  `error=0`, `uncertain=0` — PASS FOR THIS BOOK
- `Lev` third adjudication structural validator: `216/216`, overlay
  `1395/1395` — STRUCTURAL PASS; resumed independent content-QC completed
  `216/216`, including `152/152` high and `10/10` new decisions,
  `error=0`, `uncertain=0` — PASS FOR THIS BOOK
- strict completed-book counter (`pass 1 + pass 2 + full adjudication +
  independent QC without error/uncertain`): `22/66` (`Gen`, `Exod`, `Lev`,
  `Num`, `Deut`, `Josh`, `Judg`, `Ruth`, `1Sam`, `2Sam`, `1Kgs`, `2Kgs`,
  `1Chr`, `2Chr`, `Ezra`, `Neh`, `Esth`, `Job`, `Ps`, `Prov`, `Eccl`, `Song`) — PARTIAL GOLD PROGRESS
- all 18 tracked accepted book/batch manifests through shard `022`:
  deterministic compact serialization and all `225/225` physical output SHA
  locks independently rechecked — PASS
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
- focused gold correction contract suite
  (`python -m unittest scripts.bible_module.tests.test_ukrainian_stage_7_gold`)
  — PASS, `16` tests, including exact QC-scoped correction, stale/tamper,
  reciprocal accounting, deterministic reseal and final-QC semantic/reviewer
  tamper regressions.
- production `check-correction-qc` for `Exod` — PASS: exact `142`
  observations / `136` unique IDs, final grid `1382/1382`, 18 current input
  SHA locks, `error=0`, `uncertain=0`.
- previous focused gold/compact/shard/external contract subset — PASS, `36` tests,
  включая metadata-only consensus, exact disagreement-set adjudication и
  запрет подмены согласованного решения.
- `python -m unittest discover -s scripts/bible_module/tests` — PASS, `399`
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
