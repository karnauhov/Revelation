# Ukrainian stage 7 validation log

Date: `2026-09-12`
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

## Checkpoint 2026-09-12: Isaiah third adjudication

- Stage 3/4/5/6 `--check` — PASS before reading full work JSONL.
- `Isa` component panel: 144 verse-local components / 252 substantive
  disagreements; 105 singleton source-only punctuation/grammatical cases and
  39 multirow or target-involving components individually inspected.
- Manual third adjudication: 252/252 keys (183 original, 69 target), 34/34
  verses, 1 113 agreements preserved, full reciprocal grid 1 365/1 365;
  `new=6`, `pass_1=6`, `pass_2=132` at component level.
- Frozen stage-6 text/comments and original/target input SHA locks — PASS.
  `Isa.7.14`/`Isa.53.5` primary-MT fingerprint gate — PASS.
- Two separate deterministic generations: adjudication SHA-256
  `bb79e3daa4ec2bb32e6000690fbdf463a9a7507482853cda8b7c6285bebda47c`,
  sidecar SHA-256
  `0690822875dcc68dd55005e5d31c6f32e5662ab75d5668e9cb087574517d49e4`
  in both runs — PASS.
- `python -m scripts.bible_module.ukrainian_stage_7_gold_compare
  check-adjudication` for exact `Isa` chain — PASS,
  `processed_count=252`, `error_count=0`, `skipped_count=0`.
- Separate independent content-QC — completed, BLOCKING: 252/252 adjudicated
  rows and 1 113/1 113 agreed rows in all 34 verses examined; 250 adjudicated
  and 1 112 agreed accepted, three semantic errors at `Isa.66.15/C0141`,
  `uncertain=0`. Blocking QC/sidecar SHA-256
  `f4890fdb6afa16b0755ac3d0c764bbac80249e443a334b2901eb59ed43664b18` /
  `0031caca33fe30d2979cd8b998b12ed9e6b20ea7f7ce4362f73a5ac39779f701`;
  two generations byte-identical. `check-adjudication-qc` exit 1 is the
  required refusal of a blocking QC, not permission to accept the book.
  Separate scoped correction — PASS structural: exactly 3 semantic changes
  (1 original, 2 target), one unchanged reciprocal row revalidated, final
  grid 1 365/1 365; two byte-identical generations, `seal-correction` and
  independent root `check-correction` with `error_count=0`. Correction/sidecar
  SHA-256 `929320462dc00f8fbada2c407e91708d19e9e16ac2dc9d63106806e075aa57ba` /
  `000b4591d7177712c203e3d4b3216ebec50fcca792c12711618f329d3a3264f3`.
  A new distinct post-correction content QC is still required.
- `Jer` blind pass 2 and canonical comparison — PASS: 32 verses, 946 original
  + 773 target; double `gold_compact check` with `error_count=0`, 1 315
  agreements and 404 substantive disagreements. Root physical SHA checks of
  expanded JSONL/sidecar and comparison JSONL/sidecar match all four entries
  in `gold_review_batch_024.manifest.json`.
- `Lam` blind pass 2 and canonical comparison — PASS: 32 verses, 538 original
  + 515 target; double `gold_compact check` with `error_count=0`, 873
  agreements and 180 substantive disagreements. Root physical SHA checks of
  expanded JSONL/sidecar and comparison JSONL/sidecar match all four entries
  in `gold_review_batch_025.manifest.json`.
- Targeted gold/external Python tests — PASS, 25/25; full bible-module tests —
  PASS, 399/399; content-tool tests — PASS, 30/30. Forbidden-pattern and
  docs-sync checks — PASS. The two pre-existing stale document locks in
  `artifact_inventory.manifest.json` were refreshed mechanically for
  `report.ru.md` and `validation_log.md` only; the other 303 entries matched
  their physical files and were preserved. Stage-7 aggregate `--check` — PASS
  after this correction, with `error_count=0`, `accepted_links=0`.
- `Isa`, `Jer` and `Lam` remain outside the owner's strict accepted-book count
  (`22/66`); finalized gold and Strong assignment remain blocked.
- `Jer` third adjudication — PASS structural: 404/404 disagreements, 261
  components, 32 verses, 1 315 agreements retained, full overlay 1 719/1 719;
  double deterministic generation and separate root `check-adjudication`
  (`error_count=0`). Adjudication/sidecar SHA-256 `da312d83…` / `d93dc611…`;
  independent QC still required.
- `Lam` third adjudication — PASS structural: 180/180 disagreements, 116
  components, 32 verses, 873 agreements retained, full overlay 1 053/1 053;
  double deterministic generation and separate root `check-adjudication`
  (`error_count=0`). Adjudication/sidecar SHA-256 `84fba5b1…` / `0194bf68…`;
  independent QC still required.
- `Ezek` blind pass 2/comparison — PASS: 32 verses, 845 original + 717 target,
  1 329 agreements / 233 substantive disagreements. Two expand/check runs
  and byte-identical canonical comparison returned `error_count=0`; root
  compact check and four physical SHA locks in `gold_review_batch_026.manifest.json`
  passed. Distinct adjudication and independent QC are pending.
- `Ezek` distinct third adjudication — PASS structural: 233/233 disagreements,
  184 components, 32 verses, 1 329 agreements preserved, full overlay
  1 562/1 562; double deterministic generation and separate root
  `check-adjudication` returned `error_count=0`. Adjudication/sidecar SHA-256
  `a161a533…` / `ddbef116…`; independent QC remains required.
- `Isa` independent post-correction QC — PASS content/structure: 252
  adjudicated + 3 corrected + 1 revalidate-only = 256 observations (254
  unique stable IDs), plus all 1 113 originally agreed rows; all 34 verses,
  full grid 1 365/1 365, `error=0`, `uncertain=0`. Two deterministic runs and
  separate root `check-correction-qc` passed. QC/sidecar SHA-256
  `31879520…` / `e4c292e9…`; full corrected grid SHA-256 `467a44de…` includes
  the originally agreed t005 correction. Book-level acceptance still awaits
  fail-closed correction-aware global merge.
- `Lam` independent QC — PASS content/structure: 180/180 adjudicated rows,
  116/116 components, all 873 agreed rows and all 32 verses, full grid
  1 053/1 053; `error=0`, `uncertain=0`. Two byte-identical runs and root
  `check-adjudication-qc` passed. QC/sidecar SHA-256 `c15a7107…` / `81d4132a…`;
  the owner's strict accepted-book count increased to `23/66`.
- `Dan` independent blind pass 2/comparison — PASS: 32 verses, 844 original +
  721 target = 1 565 decisions; 1 090 agreements / 475 substantive
  disagreements. Post-freeze double expand/check, root compact check and
  four physical SHA locks in `gold_review_batch_027.manifest.json` passed.
  Distinct adjudication and independent QC remain required.
- `Ezek` independent QC — PASS: 233/233 adjudicated, 184/184 components,
  1 329/1 329 agreed and all 32 verses; full grid 1 562/1 562, 4 critical and
  40 high, `error=0`, `uncertain=0`. Double deterministic generation and
  separate root `check-adjudication-qc` passed; QC/sidecar physical SHA-256
  `f37208a2…` / `30c6ce09…` match the accepted versioned
  `gold_adjudication_batch_026.manifest.json`. Strict count `24/66`.
- `Hos` blind pass 2/comparison — PASS: 32 verses, 615 original + 588 target,
  943 agreements / 260 substantive disagreements. Two post-freeze expansions
  were byte-identical, separate root shard-mode `gold_compact check` returned
  `error_count=0`; comparison JSONL/sidecar physical SHA-256 `f6b419c8…` /
  `e8175ed6…` and pass2 JSONL/sidecar `2470f5f4…` / `abed56f4…` match
  `gold_review_batch_028.manifest.json`. Hos remains unaccepted.
- `Dan` distinct third adjudication — PASS structural: 475/475 disagreements
  across 228 verse-local components and 32 verses, preserving 1 090
  agreements and exact overlay grid 1 565/1 565. Three deterministic
  generations and separate root `check-adjudication` returned `error_count=0`;
  adjudication/sidecar physical SHA-256 `1138d1a2…` / `3977bf82…` match
  `gold_adjudication_batch_027.manifest.json`. Independent content-QC remains
  mandatory before book-level acceptance.
- Correction-aware finalizer CC0 tests — PASS, 17/17 targeted after requiring
  production accepted-manifest path under the versioned report directory;
  full bible-module 400/400 also passed before that final path guard. A new
  full suite run is required after the guard. Real 66-book finalization remains
  blocked by missing accepted book packages; no production links emitted.
- Correction-aware finalizer after versioned-report path guard — PASS,
  targeted 17/17 and full bible-module 400/400. Real-input one-book `Isa`
  production-contract probe (temporary one-book roster, not global finalize)
  revalidated seven SHA-locked artifacts, accepted book manifest SHA
  `9241e931…`, registry SHA `d31525f2…`, and semantic equality of all
  1 365/1 365 corrected grid rows, including one originally agreed target
  correction. Versioned proof: `gold_correction_registry_isa_probe.manifest.json`.
  Book-level Isa accepted; actual 66-book registry/global finalize remains
  blocked.
- `Jer` independent QC — PASS: 404/404 adjudicated, 261 components, all
  1 315 agreed and all 32 verses, full grid 1 719/1 719; 2 critical and 80
  high, `error=0`, `uncertain=0`. Double byte-identical generation, separate
  root `check-adjudication-qc` and physical QC/sidecar SHA `d9467f06…` /
  `f37c0770…` passed; `gold_adjudication_batch_024.manifest.json` accepted.
  Strict count with Isa `26/66`.
- `Hos` distinct third adjudication — PASS structural: 260/260 substantive
  disagreements in 135 verse-local components, preserving 943 agreements and
  overlay 1 203/1 203. Double generation, separate root `check-adjudication`,
  physical adjudication/sidecar SHA `09ea7233…` / `0f40b416…` passed;
  `gold_adjudication_batch_028.manifest.json` records pending independent QC.
- `Joel` blind pass 2/comparison — PASS: 32 verses, 745 original + 644 target,
  857 agreements / 532 substantive disagreements. Root physical pass2/sidecar
  SHA `7bab8fc0…` / `593df4eb…` and comparison/sidecar `2cbb07ee…` /
  `58bde254…` match versioned `gold_review_batch_029.manifest.json`; separate
  shard-mode `gold_compact check` returned `error_count=0`. Joel pending
  distinct adjudication/QC.
- `Hos` independent QC — PASS: 260/260 adjudicated, 943/943 agreed, 32 verses,
  grid 1 203/1 203, `error=0`, `uncertain=0`; two byte-identical generations,
  root `check-adjudication-qc` and physical SHA `b1529877…` / `afe7d5e2…`
  passed. `gold_adjudication_batch_028.manifest.json` accepted; strict count
  reached `27/66` at this checkpoint.
- `Dan` independent QC — correctly BLOCKED: all 475 adjudicated and 1 090
  agreed rows, 32 verses, grid 1 565 checked; five originally agreed IDs in
  `Dan.7.15` falsely linked locative Aramaic `בְּ ג֣וֹא נִדְנֶ֑ה` to causal
  OH1988 «через це». QC/sidecar SHA `383c1b10…` / `f63c1879…`; acceptance
  validator rejected it. Frozen pass/adjudication outputs were preserved.
- `Dan` scoped correction — PASS: five exact stable IDs (three original
  omissions, two target translation additions) with stage-6 text/comment
  unchanged. Double deterministic generation and `seal-correction` verified
  grid 1 565/1 565; correction/sidecar SHA `0f8dbcdf…` / `c5a9e82e…`.
  New correction validator regression accepts the agreed-QC error format and
  rejects missing/duplicate/cross-verse scope; targeted gold tests 18/18 PASS.
- `Dan` distinct post-correction QC — PASS: 475 adjudication + 5 correction
  + 23 unchanged revalidation = 503 observations / 499 unique IDs, all
  1 090 agreements and 32 verses, grid 1 565/1 565, `error=0`,
  `uncertain=0`. Three byte-identical generations, root `check-correction-qc`,
  physical SHA `f0fd4393…` / `ceb8b61f…` passed. Real-input one-book registry
  probe validated the seven-artifact chain and all five originally agreed
  corrections, probe SHA `322a08dc…`. `gold_adjudication_batch_027.manifest.json`
  and `gold_correction_registry_dan_probe.manifest.json` accept book-level Dan;
  strict count reached `28/66`, global 66-book finalize remains blocked.
- `Amos` blind pass 2/comparison — PASS: 32 verses, 779 original + 690
  target, 1 097 agreements / 372 disagreements; byte-identical comparison,
  physical SHA `7e0b0f6b…` / `0cc48dce…`. Distinct adjudication 372/372 in
  202 components, grid 1 469/1 469; root `check-adjudication`, SHA
  `6382f81b…` / `0950f35f…` passed. Independent QC checked all 372
  adjudicated and 1 097 agreed rows, `error=0`, `uncertain=0`; root
  `check-adjudication-qc`, two byte-identical generations and SHA
  `492db6a8…` / `9f9988e3…` passed. Amos accepted; strict count `29/66`.
- `Joel` distinct adjudication — PASS structural: 532/532 disagreements in
  239 components, 857 agreements preserved, grid 1 389/1 389, root
  `check-adjudication`, SHA `29844bc0…` / `ffbcbeca…`; independent QC is
  investigating Joel.2.27 and has not accepted the book.
- `Obad` blind pass 2/comparison — PASS: 21 verses, 498 original + 478
  target, 759 agreements / 217 disagreements; comparison SHA
  `cbe7a7dd…` / `5378d325…`. Distinct adjudication 217/217 in 109
  components, grid 976/976, root `check-adjudication`, SHA `2c60f544…` /
  `0daa3bd5…` passed; independent QC remains required.
- `Obad` independent content-QC — PASS: 217 adjudicated + 759 agreed,
  all 109 components and grid 976/976 in 21 verses; 24 high reviewed,
  `error=0`, `uncertain=0`. Double byte-identical generation, root physical
  SHA `91f81897…` / `b090c5e4…` and `check-adjudication-qc` PASS. Book-level
  accepted in `gold_adjudication_batch_031.manifest.json`; strict count `30/66`.
- `Joel` blocking QC — correctly REJECTED: two adjudicated stable IDs in
  Joel.2.27 wrongly treated «іншого» as addition; original H5750 phrase link
  needed t016+t017. SHA QC/sidecar `e7760a22…` / `226b4f5d…`; scoped two-row
  correction SHA `bfac6d3f…` / `a89fb175…` passed `seal-correction` and
  double deterministic generation without mutating frozen pass/adjudication.
- `Joel` distinct post-correction QC — PASS: 532 adjudication + two corrected
  + one unchanged reciprocal = 535 observations, all 857 agreements,
  grid 1 389/1 389, `error=0`, `uncertain=0`; double byte-identical runs,
  root physical SHA `cc2e3390…` / `31b707cb…` and `check-correction-qc`
  PASS. Real-input one-book correction registry twice confirmed two corrected
  IDs, 1 387 unchanged semantics, final semantics SHA `7b6deb9a…`; probe SHA
  `283087ca…`, versioned evidence `gold_correction_registry_joel_probe.manifest.json`.
  Book-level accepted; strict count `31/66`, global finalize blocked.
- `Jonah` blind pass 2/comparison — PASS: 32 verses, 831 original + 696
  target, 1 075 agreements / 452 disagreements, SHA `c42dec07…` /
  `6de20fc8…`; distinct adjudication/QC pending.
- `Mic` blind pass 2/comparison — PASS: 32 verses, 761 original + 725
  target, 1 155 agreements / 331 disagreements, SHA `cdcfb19c…` /
  `17a839ec…`; root physical SHA and two deterministic runs matched.
  Distinct adjudication/QC pending.
- `python -m unittest discover -s scripts/bible_module/tests` — PASS,
  402/402 tests after Joel correction parser regression.
- `Jonah` distinct third adjudication — PASS structural: 452/452 substantive
  disagreements in 226 components, 1 075 agreements and full reciprocal
  grid 1 527/1 527; Jonah.1.11 C0057 required a seven-row new phrase/null
  decomposition and Jonah.3.4 retained primary-MT 40 days. Double byte-identical
  generation, root physical SHA `0eac81db…` / `a13544c1…` and
  `check-adjudication` PASS; independent content-QC pending.
- `Nah` blind pass 2/comparison — PASS: 32 verses, 604 original + 593 target,
  1 022 agreements / 175 disagreements, comparison/sidecar SHA
  `af5d948c…` / `d00dd38f…`; root physical SHA matched, distinct
  adjudication/QC pending.
- `python -m unittest discover -s scripts/content_tool/tests` — PASS, 30/30.
- `python -m scripts.bible_module.ukrainian_stage_3_sources --check` — PASS;
  `python -m scripts.bible_module.ukrainian_stage_4 --check` — PASS;
  `python -m scripts.bible_module.ukrainian_stage_5 --check` — PASS;
  `python -m scripts.bible_module.ukrainian_stage_6 --check` — PASS.
- `python -m scripts.bible_module.ukrainian_stage_7 --check` — PASS as
  fail-closed in-progress contract: 31 102 target positions,
  `candidate_count=872025`, `accepted_links=0`, `error_count=0`, status
  `blocked_before_gold_and_alignment_acceptance`; 66-book gold,
  calibration and production links remain intentionally absent.
- `git diff --check` — PASS (Windows LF→CRLF notices only).
- `Mic` distinct third adjudication — PASS structural: 331/331
  disagreements, 1 155 agreements, 161 components and grid 1 486/1 486,
  including Mic.6.8 primary-MT control; double byte-identical generation,
  root physical SHA `339b1d47…` / `fa5b3ba8…` and `check-adjudication`
  PASS. Subsequent independent content-QC found three errors at `Mic.2.8`;
  book blocked pending correction/re-QC.
- `Hab` blind pass 2/comparison — PASS: 32 verses, 707 original + 703
  target, 1 060 agreements / 350 disagreements; comparison/sidecar SHA
  `2ae9e92b…` / `2c35f156…`. Root physical SHA matched; distinct
  adjudication subsequently completed, independent QC pending.
- `Nah` distinct third adjudication — PASS structural: 175/175
  disagreements in 107 components, 1 022 agreements and grid 1 197/1 197;
  five critical Nah.1.8 IDs preserved as source-omitted and target-null
  instead of inventing an alternative Strong. Double byte-identical runs,
  root physical SHA `4ef2b08e…` / `b1a27ce4…` and `check-adjudication`
  PASS; subsequent independent content-QC found five critical uncertainties
  at `Nah.1.8`, so book-level acceptance remains blocked.
- `Jonah` independent content-QC — PASS: 452 adjudicated and 1 075 agreed,
  all 32 verses, grid 1 527/1 527, high 10, `error=0`, `uncertain=0`.
  Three byte-identical generations, root physical SHA `685de4bf…` /
  `975ed8b9…` and `check-adjudication-qc` PASS. Book-level accepted in
  `gold_adjudication_batch_032.manifest.json`; strict count `32/66`.
- `Mic` and `Nah` independent full-grid QC — EXPECTED FAIL-CLOSED:
  `Mic` 331 adjudicated + 1 155 agreed = 1 486 checked, `error=3` at
  `Mic.2.8`; `Nah` 175 adjudicated + 1 022 agreed = 1 197 checked,
  `uncertain=5` at `Nah.1.8`. Physical QC/sidecar SHA match; double
  generations byte-identical; root `check-adjudication-qc` exit 1 for both
  at the blocking status gate. No book acceptance. SHA records in
  `gold_qc_blocking_batch_033_034.manifest.json`.
- `Mic.2.8` three-row correction — PASS/PENDING RE-QC: independent blocker
  scope exactly 3 changed stable IDs + 2 reciprocal revalidations; primary
  MT H7725G has no token-level return span in OH1988 «як здо́бич».
  Three generated JSONL files and sidecars are pairwise byte-identical;
  correction/sidecar SHA `5a7afded…` / `902744e3…`; root
  `seal-correction` exit 0, grid 1 486/1 486. Separate reviewer and
  correction-aware one-book probe remain mandatory.
- `Nah.1.8` textual diagnostic — BLOCKED: exact scan leaf 1156 (printed
  page 1152) shows the frozen OH phrase, no verse note; source TAHOT MT
  H4725+H9024 means place/its; read-only local LXX control contains
  `τοὺς ἐπεγειρομένους`, resembling «заколотниками». Local DB physical
  SHA `443ab95f…` equals registry. Neither exact OH Vorlage nor stable
  alternative Hebrew token is proved. Addendum is research-only and
  authorizes no Strong or book acceptance.
- `Hab` distinct third adjudication — PASS structural: 350/350
  disagreements, 1 060 agreements, 162 components, reciprocal grid
  1 410/1 410; two byte-identical runs, root SHA `e5e162c7…` /
  `ab73e3fb…`, root `check-adjudication` exit 0. Person mismatch
  `Hab.3.16` remains explicit null/negative evidence for independent QC.
- `Zeph` distinct third adjudication — PASS structural: 251/251
  disagreements, 1 228 agreements, 183 components, reciprocal grid
  1 479/1 479; two byte-identical runs, root SHA `138c90e0…` /
  `0f2f8cd3…`, root `check-adjudication` exit 0; independent QC pending.
- `Hag` and `Zech` blind pass 2/comparison — PASS: 1 595/1 606 stable
  decisions, 522/278 substantive disagreements, comparison/sidecar SHA
  `c80267d8…` / `9f368a8c…` and `f09db0e6…` / `38262fde…`;
  root physical SHA and double byte-identical comparison checked.
- `Mal` blind pass 2/comparison — PASS: 32 verses, 855 original + 758
  target = 1 613 stable decisions, 1 173 agreements / 440 substantive
  disagreements. Pass-2 SHA frozen before post-blind unsealing, both
  deterministic comparisons byte-identical; root physical comparison/sidecar
  SHA `c9b40811…` / `641bff4f…`. Adjudication and QC not yet done.
- `Mic` post-correction independent full-grid QC — PASS: 331 adjudicated +
  3 corrected + 2 unchanged revalidations = 336 observations, all 1 155
  pass-agreed decisions and reciprocal grid 1 486/1 486 checked; `error=0`,
  `uncertain=0`, two byte-identical generations, physical QC/sidecar SHA
  `f861d76f…` / `a5c230eb…`, root `check-correction-qc` exit 0.
  One-book real-input correction registry probe twice verified exact
  1 486/1 486 semantics and only three corrected IDs; registry/proof SHA
  `d5d2e87e…` / `4f00c9d2…`. `Mic` accepted book-level; global gold pending.
- `Hab` independent full-grid content-QC — PASS: 350 adjudicated + 1 060
  agreed = 1 410/1 410 stable decisions, 32 verses and 162 components;
  `error=0`, `uncertain=0`, double byte-identical generation, physical
  QC/sidecar SHA `6c82495c…` / `8edf2e61…`, root
  `check-adjudication-qc` exit 0. `Hab` accepted book-level.
- `Zeph` independent full-grid content-QC — EXPECTED FAIL-CLOSED: 251
  adjudicated + 1 228 agreed = 1 479/1 479, `error=0`, `uncertain=4`
  high textual cases at 2.14/3.17. Double byte-identical generation,
  physical QC/sidecar SHA `1e9acf7e…` / `75275ace…`; root
  `check-adjudication-qc` exit 1 at blocking status. Exact OH1988 scan
  leaves 1165/1166 have no explanatory note for these loci; MT/LXX
  similarity alone cannot prove the source reading. Book not accepted.
- `Hag` distinct third adjudication — PASS structural: 522/522 substantive
  disagreements in 300 components, 1 073 agreements and reciprocal grid
  1 595/1 595; double byte-identical generation, physical adjudication/
  sidecar SHA `292fde29…` / `fc7eb3ad…`, root `check-adjudication` exit 0.
  Independent full-grid content-QC pending.
- `Zech` distinct third adjudication — PASS structural: 278/278 substantive
  disagreements in 197 components, 1 328 agreements and reciprocal grid
  1 606/1 606; double byte-identical generation, physical adjudication/
  sidecar SHA `eec20654…` / `9cf08b19…`, root `check-adjudication` exit 0.
  Seven high/critical textual IDs at 11.7/14.6 remain unresolved;
  independent QC and source fingerprint pending, book not accepted.
- `Hag` root independent content-QC audit — PASS: physical QC/sidecar SHA
  `45b7f26c…` / `96f38086…` and `check-adjudication-qc` exit 0 on the
  frozen pass-2 answer-free template and all 1 595 decisions. One deliberate
  wrong-template invocation failed with stale-template SHA before the
  correct frozen pass-2 template was supplied; no data were changed.
  `Hag` accepted book-level; strict count `35/66`.
- `Mal` distinct third adjudication — PASS structural: 440/440 substantive
  disagreements in 219 components, 1 173 agreements and reciprocal grid
  1 613/1 613; double byte-identical generation, physical adjudication/
  sidecar SHA `cc7a3201…` / `5433ce1d…`, root `check-adjudication` exit 0.
  Independent content-QC pending, no book-level acceptance.
- `Zech.11.7`/`14.6` primary diagnostic — RESEARCH-ONLY: root visually
  inspected OH1988 scan leaves 1177/1180 and confirmed the target wording,
  printed pages 1173/1176 and no locus-specific footnotes. Frozen TAHOT/MT
  and read-only LXX controls differ at the seven high/critical IDs; Greek
  similarity and scholarly retroversion do not establish exact OH1988
  Vorlage. Evidence note/sidecar physical SHA `0b13a996…` / `68eceea7…`;
  `textual_fingerprint_zech_11_7_14_6.manifest.json` records source SHA.
  No Strong promotion or Zech book acceptance.
- `Zech` independent full-grid QC — EXPECTED FAIL-CLOSED: 278 adjudicated
  (271 accepted, seven high/critical uncertain) + 1 328 agreed = 1 606/1 606
  decisions, 32 verses and 197 components. Three byte-identical generations,
  root physical QC/sidecar SHA `b4cc4e50…` / `bc4d8585…`; root
  `check-adjudication-qc` exit 1 at blocking status. Book not accepted.
- Frozen prior-stage checks repeated: stage-3 source/cache lock — PASS;
  stage 4 — `source_count=14`, verified; stage 5 — verified; stage 6 —
  verified. No mapping or stage-6 text/comment mutation.
- Documentation sync and forbidden-pattern Dart checks — PASS (all configured
  checks). No Flutter/runtime/db/content-tool changes were made.
- `Mal` independent full-grid content-QC — EXPECTED FAIL-CLOSED: 440
  adjudicated + 1 173 agreed = 1 613/1 613 decisions, `error=2`,
  `uncertain=0` at two reciprocal `Mal.3.11` stable IDs; H9003 was
  incorrectly linked to Ukrainian «все». Original v1 QC/sidecar SHA
  `f36a1065…` / `18bf0e32…`; contract-complete v2 kept all 440 verdict
  rows byte-identical, added exact proposal-only correction scope and used
  required blocked status; v2 SHA `dd452cbf…` / `b41900a9…`.
  Root physical SHA and expected `check-adjudication-qc` exit 1 confirmed.
- `Mal.3.11` scoped correction — PASS/PENDING DISTINCT RE-QC: exact two
  changed stable IDs plus unchanged t007 reciprocal revalidation. H9003
  remains linked only to «те», «все» becomes unnumbered translation
  addition; full grid 1 613/1 613. Three generated JSONL/sidecars
  byte-identical, correction/sidecar SHA `368eed86…` / `1e6dc228…`,
  root `seal-correction` exit 0. Frozen blind passes/adjudication and
  stage-6 text/comment unchanged. Book not accepted until distinct
  post-correction QC and real-input one-book registry proof.
- Focused Stage-7 gold/evaluation tests — PASS: `25/25`. Full bible-module
  Python suite — PASS: `402/402`; content-tool suite — PASS: `30/30`.
  `python -m scripts.bible_module.ukrainian_stage_7 --check` — PASS in
  fail-closed state: 31 102 target positions, 872 025 candidate-only rows,
  `accepted_links=0`, `error_count=0`, status
  `blocked_before_gold_and_alignment_acceptance`. Canonical serialization
  audit: 67 gold review/adjudication/blocking/registry manifests, zero
  noncanonical files. `git diff --check` exit 0 (Windows CRLF notices only).
- `Mat` shard 040 blind pass 2 — PASS, not book acceptance: 39 verses,
  691 original + 667 target = 1 358 exact decisions. Completed raw/sidecar
  physical SHA `682f925f…` / `54a5fe42…` matched independent reviewer
  freeze; two expanded raw emissions and `gold_compact check` matched.
  Two post-blind comparisons were byte-identical, with 1 072 agreements,
  286 substantive disagreements (186 original + 100 target), 706
  metadata-only differences and `error=0`; comparison/sidecar SHA
  `f109bf7c…` / `b25451cf…` are pinned in
  `gold_review_batch_040.manifest.json`. Distinct adjudication and full-grid
  independent QC remain pending; Mat.21.30 is textual fail-closed.
- `Mal` distinct post-correction independent QC — PASS: 443/443 observations
  (440 adjudication, 2 correction, 1 unchanged reciprocal revalidation),
  full grid 1 613/1 613, `error=0`, `uncertain=0`. Three QC emissions were
  byte-identical; root physical QC/sidecar SHA `9dfbfbd9…` / `2ade4358…`
  matched and `check-correction-qc` returned accepted. Real one-book
  correction-aware registry probe ran twice with byte-identical registry
  SHA `5a0edee2…`, probe SHA `087c824f…`, corrected-semantics SHA
  `1e896aec…`; all 1 613 stable IDs retained, exact two-row correction,
  no originally-agreed override. `Mal` accepted at book level only, strict
  count 36/66; no global finalize/Strong production.
- `Nah.1.8` / `Zeph.2.14` / `Zeph.3.17` primary-source diagnostic —
  COMPLETE BUT BLOCKING: exact OH1988 scan pages and author 1963 primary
  testimony visually checked; root independently inspected page images.
  The author confirms a Hebrew OT base and occasional LXX consultation,
  but no dated locus-specific source reading. Nine high/critical QC IDs
  remain unresolved, no Greek-to-Hebrew Strong transfer. Note physical SHA
  `c90b2741…`, source/page digests in
  `textual_fingerprint_nah_zeph_primary_audit.manifest.json`.
- `Mat` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  286/286 substantive disagreements in 138 verse-local components,
  1 072 agreements preserved, full grid 1 358/1 358 in 39 verses. Two
  JSONL/sidecar emissions byte-identical, root physical SHA
  `02240391…` / `5e9afa62…`, `check-adjudication` exit 0. Selected
  TAGNT versus OH1988 `Mat.21.30` remains one critical source-reading
  uncertainty; no production Strong assigned. Distinct full-grid QC and
  source resolution pending, `gold_adjudication_batch_040.manifest.json`.
- Independent `Mat.21.30` textual-source audit — DIAGNOSTIC PASS,
  RESOLUTION BLOCKED: exact OH1988 printed `21.29–31`, empty locus comments,
  pinned TAGNT/UGNT and separately licensed TR/Byzantine/SBLGNT controls
  checked. Official SBLGNT edition apparatus supports a Westcott–Hort
  son-order analogue, but not Ohiienko's exact Greek Vorlage. Note physical
  SHA `67b7ce6c…`, input digests in
  `textual_fingerprint_mat_21_30.manifest.json`; one critical source-reading
  uncertainty remains. No Strong transfer or source-map mutation.
- `Mark` shard 041 blind pass 2 — PASS, not book acceptance: 40 verses,
  681 original + 647 target = 1 328 decisions. Independent pass2/sidecar
  physical SHA `a4615e79…` / `965b9608…`; double expansion and root
  `gold_compact check` PASS. Two byte-identical post-blind comparisons:
  1 039 agreements, 289 substantive disagreements (201 original + 88
  target), 656 metadata-only differences, `error=0`; comparison/sidecar
  SHA `55ca5a79…` / `5d3792a7…` in
  `gold_review_batch_041.manifest.json`. Distinct adjudication/QC pending;
  source-apparatus endings of chapter 16 remain fail-closed.
- `Luke` shard 042 blind pass 2 — PASS, not book acceptance: 39 verses,
  606 original + 604 target = 1 210 decisions. Independent pass2/sidecar
  physical SHA `e84bcd28…` / `38c2fbd0…`; double expansion and root
  `gold_compact check` PASS. Two byte-identical post-blind comparisons:
  960 agreements, 250 substantive disagreements (160 original + 90 target),
  665 metadata-only differences, `error=0`; comparison/sidecar SHA
  `ba0a7788…` / `a5893392…` in
  `gold_review_batch_042.manifest.json`. Distinct adjudication/QC pending;
  `Luke.2.11` and textual variants remain fail-closed.
- `Mat` independent full-grid QC — EXPECTED BLOCK, no book acceptance:
  distinct reviewer audited 286 adjudicated + 1 072 pass-agreed =
  1 358/1 358 stable decisions in 39 verses. 1 343 accepted, 15 critical
  source-uncertain at `Mat.21.30` (7 adjudicated, 8 pass-agreed), content
  errors 0. Three byte-identical QC/sidecar emissions; root physical SHA
  `793f54aa…` / `f8116493…`. Root `check-adjudication-qc` exit 1,
  `Independent adjudication QC status or reviewer independence differs`,
  is expected for blocking status; `gold_adjudication_batch_040.manifest.json`
  records the full grid and hashes. Source resolution/re-QC required.
- `Mark` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  289/289 substantive disagreements in 171 verse-local components,
  1 039 agreements preserved, full grid 1 328/1 328. Three byte-identical
  JSONL/sidecar emissions, root physical SHA `76d2f827…` / `ee29b8e4…`,
  `check-adjudication` exit 0. Three critical textual-choice loci remain
  unresolved (`1.2`, `16.8`, `16.9`); the 34 Short Ending source atoms
  `16.8` are `source_text_not_rendered`, not proven translation omissions.
  Independent full-grid QC and source resolution pending; manifest
  `gold_adjudication_batch_041.manifest.json`.
- `John` shard 043 blind pass 2 — PASS, not book acceptance: 36 verses,
  593 original + 577 target = 1 170 decisions. Independent pass2/sidecar
  physical SHA `751084b6…` / `afa6ca96…`; root `gold_compact check` PASS.
  Two byte-identical post-blind comparisons: 1 039 agreements, 131
  substantive disagreements (108 original + 23 target), 719 metadata-only
  differences, `error=0`; comparison/sidecar SHA `a18fa1f0…` /
  `210c5edc…` in `gold_review_batch_043.manifest.json`. Distinct
  adjudication/QC pending; textual variants remain fail-closed.
- `Acts` shard 044 blind pass 2 — PASS, not book acceptance: 39 verses,
  720 original + 716 target = 1 436 decisions. Independent pass2/sidecar
  physical SHA `859d3211…` / `0647c0a5…`; root `gold_compact check` PASS.
  Two byte-identical post-blind comparisons: 1 175 agreements, 261
  substantive disagreements (182 original + 79 target), 962 metadata-only
  differences, `error=0`; comparison/sidecar SHA `17ea9ca5…` /
  `3526ce28…` in `gold_review_batch_044.manifest.json`. Source-qualified
  adjudication/QC pending; corrected renderer emits no foreign `Mat` prefix.
- `Mark` independent full-grid QC — EXPECTED BLOCK: distinct reviewer
  audited 289 adjudicated + 1 039 agreed = 1 328/1 328 decisions in 40
  verses. 1 324 accepted, 4 critical source-choice uncertain at `1.2`/
  `16.9`, content errors 0. Three byte-identical QC/sidecar emissions;
  root physical SHA `753de840…` / `416193d2…`; root
  `check-adjudication-qc` exit 1 is expected for blocking status. `16.8`
  Short Ending, `9.38`, `10.7`, `15.28` checked. Old pass2 Mat-label
  provenance requires downstream SHA rebase; manifest
  `gold_adjudication_batch_041.manifest.json`, no book acceptance.
- `Luke` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  250/250 substantive disagreements in 105 verse-local components,
  960 agreements preserved, grid 1 210/1 210. Two byte-identical
  JSONL/sidecar emissions; root physical SHA `7f4e8a7d…` / `889ccdfb…`,
  `check-adjudication` exit 0. `Luke.10.15` source μὴ/G3361 positive OH
  reading remains critical; `Luke.2.11` agreed legacy counterexample
  handed to distinct full-grid QC. Old pass2 Mat-label provenance needs
  downstream SHA rebase; `gold_adjudication_batch_042.manifest.json`.
- `Mark`/`Luke`/`John` frozen pass2 metadata provenance repair — PASS
  METADATA-ONLY, not book acceptance: SHA-locked first-party repair changed
  exactly 1 893 copied Mat rationale/evidence labels, 0 semantic decisions
  across 3 708/3 708 stable IDs. Two byte-identical compact repairs,
  expanded raw+sidecars and comparison+sidecars per book; three root
  `gold_compact check` PASS. Rebased comparison disagreement counts stayed
  289/250/131. Five targeted regression tests PASS; hashes and limits in
  `gold_pass2_provenance_repair.manifest.json`. Frozen originals unchanged;
  adjudication/QC downstream rebase remains mandatory.
- `Rom` blind pass 2/comparison — PASS, not book acceptance: 33 selected
  verses, 520 original + 536 target = 1 056 decisions; two expanded
  outputs and `gold_compact check` PASS, physical pass2 SHA `a4a520dc…`.
  Two canonical-v2 comparison/sidecar emissions byte-identical: 866
  agreements, 190 substantive disagreements (127 original + 63 target),
  535 metadata-only differences; physical SHA `5c927827…` / `254b4e2c…`.
  `gold_review_batch_045.manifest.json`; distinct adjudication/QC pending.
- `Mark`/`Luke` explicit adjudication SHA-rebase — PASS STRUCTURALLY,
  BOOKS BLOCKED: 539/539 decision rows unchanged, 0 disagreement keys
  changed. Two byte-identical rebased adjudication/sidecar emissions per
  book, root physical SHA `Mark` `19cc5703…`/`3e08abfd…`, `Luke`
  `6060591b…`/`1d34d91e…`; root `check-adjudication` exit 0 on both
  repaired chains. Three focused rebase tests PASS. The original blind
  artifacts remain frozen; downstream QC and textual source resolution
  are pending. See `gold_adjudication_provenance_rebase.manifest.json`.
- `John` distinct third adjudication — PASS STRUCTURALLY, BOOK NOT YET
  ACCEPTED: on repaired pass2/comparison, 131/131 disagreements in 98
  components, 1 039 agreed unchanged, full grid 1 170/1 170. Two
  byte-identical emissions; root physical adjudication/sidecar SHA
  `139ffd0f…` / `5410146d…`; root `check-adjudication` exit 0.
  Independent full-grid QC and exact textual source scrutiny pending;
  `gold_adjudication_batch_043.manifest.json`.
- `Luke` independent full-grid QC — EXPECTED BLOCK: distinct reviewer
  audited 250 adjudicated + 960 agreed = 1 210/1 210 decisions in 39
  verses. 1 196 accepted, 14 source-choice uncertain at `1.76`, `10.15`,
  `10.42`, `13.7`, `16.21`, `20.34`, content errors 0. Three byte-identical
  QC/sidecar emissions; root physical SHA `9c34b5a2…` / `c5df3e4b…`;
  root `check-adjudication-qc` exit 1 is expected for blocking status.
  `Luke.2.11` legacy negative control passed. Old QC SHA needs explicit
  downstream rebase after pass2 provenance repair; source choices remain
  unresolved. `gold_adjudication_batch_042.manifest.json`, no acceptance.
- `1Cor` blind pass 2/comparison — PASS, not book acceptance: 33 verses,
  471 original + 481 target = 952 decisions; two expanded outputs and
  root `gold_compact check` PASS, physical pass2 SHA `012203d3…`.
  Two comparison/sidecar emissions byte-identical: 777 agreements, 175
  substantive disagreements (116 original + 59 target), 571 metadata-only
  differences; physical SHA `acaf2e6d…` / `85f3c618…`. `8.2`, `10.28`,
  `11.31`, `14.34` retain source-qualified gates. Distinct adjudication/QC
  pending; `gold_review_batch_046.manifest.json`.
- `Mark`/`Luke` explicit blocked-QC SHA-rebase — PASS METADATA-ONLY,
  BOOKS BLOCKED: 539/539 QC adjudication-result rows and full agreed-row
  audit unchanged; 2 538/2 538 full-grid decisions, 4/14 source-choice
  uncertain and 0 content errors preserved. Two byte-identical emissions
  per book; physical rebased QC/sidecar SHA `Mark` `b40721a7…`/
  `2e54d0ce…`, `Luke` `aa6ce85b…`/`b4906325…`. Rebased acceptance
  validator reaches and rejects only the expected blocking-status gate;
  four focused tests PASS. Source resolution and new independent re-QC
  remain mandatory; `gold_qc_provenance_rebase.manifest.json`.
- `2Cor` blind pass 2/comparison — PASS, not book acceptance: 34 verses,
  540 original + 543 target = 1 083 decisions; two expanded outputs
  and root `gold_compact check` PASS, physical pass2 SHA `ab7bfa3c…`.
  Two comparison/sidecar emissions byte-identical: 916 agreements, 167
  substantive disagreements (117 original + 50 target), 706 metadata-only
  differences; physical SHA `4b6388b0…` / `e0e8f481…`.
  `gold_review_batch_047.manifest.json`; distinct adjudication/QC pending.
- `Acts` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  261/261 substantive disagreements in 145 verse-local components,
  1 175 agreements preserved, grid 1 436/1 436. Two byte-identical
  emissions; root physical SHA `69315757…` / `c5adb14b…`, root
  `check-adjudication` exit 0. Four critical/high source/semantic cases
  remain unresolved (`2.38`, `13.26`, `15.34`, `27.12`); agreed `13.29`
  t009 handed to distinct full-grid QC. `gold_adjudication_batch_044.manifest.json`.
- `John` independent full-grid QC — EXPECTED BLOCK: distinct reviewer
  audited 131 adjudicated + 1 039 agreed = 1 170/1 170 decisions in
  36 verses on repaired pass2/comparison chain. 1 160 accepted, 10
  source-choice uncertain at `1.18`, `1.28`, `8.11`, `14.15`, content
  errors 0. Three byte-identical QC/sidecar emissions; root physical SHA
  `67233ff0…` / `08c0a235…`; root `check-adjudication-qc` exit 1 only
  for blocking status. `5.4` invented G2962 rejected; `19.34` author
  note checked. `gold_adjudication_batch_043.manifest.json` updated;
  source resolution/re-QC mandatory, no book acceptance.
- `python -m scripts.bible_module.ukrainian_stage_7 --check` — PASS,
  exit 0 after refreshing two existing report-document SHA locks in the
  305-entry artifact inventory; 31 102 target positions, 872 025
  candidate-only rows, accepted production links 0, stage-6 text SHA
  `e55156cd…` unchanged. Later documentation additions require one final
  existing-lock refresh before another `--check`.
- `python -m unittest discover -s scripts/bible_module/tests` — PASS,
  414/414 tests, 13.709 s; includes the new provenance/adjudication/QC
  rebase regressions and existing stage-7 invariants.
- `python -m unittest discover -s scripts/content_tool/tests` — PASS,
  30/30 tests, 3.042 s; content tool was not modified.
- `Rom` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  190/190 substantive disagreements in 94 verse-local components,
  866 agreements preserved, grid 1 056/1 056. Two byte-identical
  emissions; root physical SHA `42483a9c…` / `43375656…`, root
  `check-adjudication` exit 0. Four critical source/segmentation cases
  (`3.22`, `6.1`, `6.11`, `13.11`) remain unresolved; no G2248 transfer
  to «нам» without exact textual proof. Distinct QC pending;
  `gold_adjudication_batch_045.manifest.json`.
- `Gal` blind pass 2/comparison — PASS FOR SHARD ONLY: 32 verses,
  499 original + 556 target = 1 055 stable decisions; root shard-mode
  `gold_compact check` exit 0 with `error_count=0`. Two byte-identical
  comparison/sidecar emissions: 853 agreements, 202 disagreements
  (120 original + 82 target), 635 metadata-only differences; physical
  comparison/sidecar SHA `97f5f748…` / `5eb58abf…`.
  `gold_review_batch_048.manifest.json`; adjudication/QC pending.
- `Acts` independent full-grid QC — EXPECTED BLOCK: 261 adjudicated +
  1 175 agreed = 1 436/1 436 decisions; 1 399 accepted, two
  reciprocal content errors in `13.29` (one adjudicated original, one
  originally agreed target), 35 source/semantic uncertain across five
  loci. Three byte-identical emissions; root physical QC/sidecar SHA
  `a77ef5dd…` / `0fae5c28…`. Root
  `check-adjudication-qc` exit 1 at blocking-status gate as expected.
  Exact mixed correction and distinct re-QC are recorded separately below;
  `gold_adjudication_batch_044.manifest.json`.
- `1Cor` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  all 175/175 disagreements in 96 components, 777 agreements
  preserved, grid 952/952. Two byte-identical adjudication/sidecar
  emissions and root physical SHA `d6c5cd7a…` / `8ea22cf7…`;
  root `check-adjudication` exit 0. Four source-choice loci remain
  unresolved; distinct full-grid QC pending;
  `gold_adjudication_batch_046.manifest.json`.
- `Acts.13.29` exact mixed consensus correction — PASS STRUCTURALLY,
  BOOK STILL BLOCKED: one adjudicated original and one originally
  agreed target ID changed; two unchanged reciprocal target IDs
  revalidated, all 1 436/1 436 final decisions remain reciprocal.
  Three byte-identical corrections/sidecars; root `seal-correction`
  exit 0, physical SHA `c1ee34fe…` / `7c30e54b…`. Distinct
  post-correction QC recorded separately below; 35 source-uncertain
  decisions still block acceptance.
- `Rom` independent full-grid QC — EXPECTED BLOCK: 190 adjudicated +
  866 agreed = 1 056/1 056 decisions; 1 037 accepted, error 0,
  uncertain 19 across nine loci. Three byte-identical QC emissions;
  physical QC/sidecar SHA `778c7318…` / `670ea20f…`; root
  `check-adjudication-qc` exit 1 only at blocking-status gate.
  `gold_adjudication_batch_045.manifest.json`.
- `Eph` blind pass 2/comparison — PASS FOR SHARD ONLY: 32 verses,
  530 original + 460 target = 990 decisions; root compact check
  `error_count=0`. Two byte-identical comparison/sidecar emissions:
  762 agreements, 228 disagreements (171 original + 57 target),
  480 metadata-only differences; physical SHA `c94804e9…` /
  `2e5aa6d5…`. `Eph.5.30` seven target tokens without selected
  Greek clause remain null; `gold_review_batch_049.manifest.json`.
- `2Cor` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  167/167 disagreements in 103 components, 916 agreements untouched,
  grid 1 083/1 083. Two byte-identical adjudication/sidecar emissions;
  physical SHA `0ba52794…` / `78d71c65…`, root
  `check-adjudication` exit 0. Seven source/verse-boundary watchpoints
  remain fail-closed, including agreed-only `5.18`/`10.4`.
  Independent QC pending; `gold_adjudication_batch_047.manifest.json`.
- `gold_review_batch_048.manifest.json` and
  `gold_review_batch_049.manifest.json` input digest audit — corrected
  copied prior-book `complete_pass_1` anchor to the physically verified
  Gal/Eph pass-1 SHA; comparison/decision artifacts unchanged.
- `python -m unittest scripts.bible_module.tests.test_ukrainian_stage_7_gold`
  — PASS, 20/20 after the mixed agreed/adjudicated correction-scope
  regression. Full bible-module suite should be repeated after final
  code/doc changes.
- `Phil` blind pass 2/comparison — PASS FOR SHARD ONLY: 32 verses,
  499 original + 536 target = 1 035 decisions; root compact check
  `error_count=0`. Two byte-identical comparison/sidecar emissions:
  821 agreements, 214 disagreements (127 original + 87 target), 621
  metadata-only differences; physical SHA `e37fd2c8…` / `8f6b9354…`.
  `gold_review_batch_050.manifest.json`; adjudication/QC pending.
- `Acts` distinct post-correction full-grid QC — EXPECTED SOURCE BLOCK:
  261 adjudicated + 1 175 agreed, 2 changed + 2 unchanged reciprocal
  correction rows reviewed; final grid 1 436/1 436 = 1 401 accepted,
  0 content errors, 35 source/semantic uncertain across five loci.
  Three byte-identical QC/sidecar emissions; physical SHA
  `1520e928…` / `256a3a70…`; root `check-correction-qc` exit 1 only
  at blocking source-choice status. `gold_adjudication_batch_044.manifest.json`;
  book remains unaccepted pending source resolution and new re-QC.
- `Col` blind pass 2/comparison — PASS FOR SHARD ONLY: 33 verses,
  526 original + 491 target = 1 017 decisions; root compact check
  `error_count=0`. Two byte-identical comparison emissions: 803
  agreements, 214 disagreements (151 original + 63 target), 544
  metadata-only differences; physical SHA `14adfa41…` / `194f4724…`.
  Critical source-choice loci `1.12`, `3.4`, `3.15`, `3.16`, `3.22`
  remain fail-closed; `gold_review_batch_051.manifest.json`.
- `Gal` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  202/202 disagreements in 91 components, 853 agreements untouched,
  grid 1 055/1 055. Two byte-identical adjudication/sidecar emissions;
  physical SHA `628bf95b…` / `847542aa…`, root
  `check-adjudication` exit 0. Source/semantic blockers `2.2`, `3.1`,
  `4.7`, `4.14` remain fail-closed; agreed additions `3.1`/`4.7`
  must be checked in independent full-grid QC.
  `gold_adjudication_batch_048.manifest.json`.
- `1Cor` independent full-grid QC — EXPECTED SOURCE BLOCK: 175
  adjudicated + 777 agreed = 952/952 decisions; 932 accepted,
  error 0, source-choice uncertain 20 (9 adjudicated + 11 agreed)
  across `8.2`, `10.28`, `11.26`, `11.31`, `14.34`. Three
  byte-identical QC/sidecar emissions; physical SHA `6df87695…` /
  `c8fa94f4…`; root `check-adjudication-qc` exit 1 only at
  blocking-status gate. `gold_adjudication_batch_046.manifest.json`;
  source resolution/re-QC required before book acceptance.
- `1Thess` blind pass 2/comparison — PASS FOR SHARD ONLY: 32 verses,
  531 original + 506 target = 1 037 decisions; root compact check
  `error_count=0`. Two byte-identical comparison emissions: 874
  agreements, 163 disagreements (117 original + 46 target), 608
  metadata-only differences; physical SHA `df4c25e6…` / `aeec643c…`.
  `2.6`, `2.11`, `3.2`, `3.5` remain source-qualified;
  `gold_review_batch_052.manifest.json`.
- `Eph` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  228/228 disagreements in 152 components, 762 agreements untouched,
  grid 990/990. Two byte-identical adjudication/sidecar emissions;
  physical SHA `b58d2938…` / `9708ea53…`, root
  `check-adjudication` exit 0. Source/semantic blockers `3.9`, `4.8`,
  `5.30` remain; seven agreed target additions `5.30` did not inherit
  TR/Byz-only Strong. `gold_adjudication_batch_049.manifest.json`.
- `2Thess` blind pass 2/comparison — PASS FOR SHARD ONLY: 32 verses,
  603 original + 597 target = 1 200 decisions; root compact check
  `error_count=0`. Two byte-identical comparison emissions: 948
  agreements, 252 disagreements (163 original + 89 target), 570
  metadata-only differences; physical SHA `ec99f04a…` / `1ed413e7…`.
  `gold_review_batch_053.manifest.json`; adjudication/QC pending.
- `2Cor` independent full-grid QC — EXPECTED SOURCE BLOCK: 167
  adjudicated + 916 agreed = 1 083/1 083 decisions; 1 052 accepted,
  error 0, 31 source/verse-boundary uncertain (8 adjudicated +
  23 agreed) across ten loci. Three byte-identical QC/sidecar emissions;
  physical SHA `8a30d2a8…` / `9fb4091d…`; root
  `check-adjudication-qc` exit 1 only at blocking-status gate.
  `7.12` apparatus pronoun variant and TAGNT bracketed `8.13`/`10.4`
  locators remain fail-closed; `gold_adjudication_batch_047.manifest.json`.
- `Phil` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  214/214 disagreements in 84 components, 821 agreements untouched,
  grid 1 035/1 035. Two byte-identical adjudication/sidecar emissions;
  physical SHA `2539e53a…` / `a3cc7e28…`, root
  `check-adjudication` exit 0. Source/verse-boundary blockers `2.7`,
  `2.26`, `4.13`, `4.23` remain; no alternate/cross-verse Strong.
  `gold_adjudication_batch_050.manifest.json`.
- `1Tim` blind pass 2/comparison — PASS FOR SHARD ONLY: 33 verses,
  483 original + 530 target = 1 013 decisions; root compact check
  `error_count=0`. Two byte-identical comparison emissions: 814
  agreements, 199 disagreements (113 original + 86 target), 563
  metadata-only differences; physical SHA `34dea918…` / `b13c4dd7…`.
  Exact fused stage-6 surface `2.2` preserved; other source/lexical
  watchpoints remain. `gold_review_batch_054.manifest.json`.
- `python -m scripts.bible_module.ukrainian_stage_3_sources --check`,
  `python -m scripts.bible_module.ukrainian_stage_4 --check`,
  `python -m scripts.bible_module.ukrainian_stage_5 --check`,
  `python -m scripts.bible_module.ukrainian_stage_6 --check` — all PASS;
  physical stage-6 text/comment SHA remain
  `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`
  / `5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4`.
- `dart run scripts/check_forbidden_patterns.dart` — PASS.
- `dart run scripts/check_docs_sync.dart` — PASS.
- `2Tim` blind pass 2/comparison — PASS FOR SHARD ONLY: 32 verses,
  513 original + 507 target = 1 020 decisions; root compact check
  `error_count=0`. Two byte-identical comparison emissions: 848
  agreements, 172 disagreements (118 original + 54 target), 587
  metadata-only differences; physical SHA `96dfda02…` / `49a084fc…`.
  Fused stage-6 surface `3.15` preserved;
  `gold_review_batch_055.manifest.json`.
- `Gal` independent full-grid QC — EXPECTED SOURCE BLOCK: 202
  adjudicated + 853 agreed = 1 055/1 055 decisions; 1 037 accepted,
  error 0, 18 source-choice uncertain (9 adjudicated + 9 agreed)
  across six loci. Three byte-identical QC/sidecar emissions;
  physical SHA `4308527f…` / `738fcb27…`; root
  `check-adjudication-qc` exit 1 only at blocking-status gate.
  `2.2` is source-omitted/target-addition, not a Strong transfer;
  `gold_adjudication_batch_048.manifest.json`.
- `Col` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  214/214 disagreements in 127 components, 803 agreements untouched,
  grid 1 017/1 017. Two byte-identical adjudication/sidecar emissions;
  physical SHA `023c7533…` / `d12d2920…`, root
  `check-adjudication` exit 0. Five selected-source/OH mismatch loci
  remain critical; reciprocal reordering `1.16` preserved.
  `gold_adjudication_batch_051.manifest.json`.
- `Titus` blind pass 2/comparison — PASS FOR SHARD ONLY: 32 verses,
  460 original + 473 target = 933 decisions; root compact check
  `error_count=0`. Two byte-identical comparison emissions: 789
  agreements, 144 disagreements (92 original + 52 target), 443
  metadata-only differences; physical SHA `01633d4a…` / `0fa88340…`.
  Source/lexical watchpoints remain; `gold_review_batch_056.manifest.json`.
- `flutter analyze` — exit 1, four pre-existing out-of-scope warnings
  in untouched runtime files: `topic_screen.dart:400`
  (`unawaited_return_in_try_block`), `sentry_app_runner.dart:33,41`
  (`experimental_member_use`), `database_version_loader.dart:59`
  (`unawaited_return_in_try_block`); no Stage-7/Dart runtime edits.
- `flutter test` — exit 1, 918 passed and 2 failed in untouched
  `strong_dictionary_entry_view_test.dart`: usage-reference dialog
  from ellipsis and usage Bible links with preview copy. These are
  existing out-of-scope Flutter failures; no runtime/widget files
  changed by this Stage-7 continuation.
- `Phlm` blind pass 2/comparison — PASS FOR SHARD ONLY: 25 verses,
  338 original + 358 target = 696 decisions; root compact check
  `error_count=0`. Two byte-identical comparison emissions: 567
  agreements, 129 disagreements (79 original + 50 target), 429
  metadata-only differences; physical SHA `72865f9d…` / `7044fb2f…`.
  `gold_review_batch_057.manifest.json`; adjudication/QC pending.
- `1Thess` distinct third adjudication — PASS STRUCTURALLY, BOOK BLOCKED:
  163/163 disagreements in 108 components, 874 agreements untouched,
  grid 1 037/1 037. Two byte-identical adjudication/sidecar emissions;
  physical SHA `8d913a35…` / `b2e8ea43…`, root
  `check-adjudication` exit 0. Three source/segmentation loci remain;
  `gold_adjudication_batch_052.manifest.json`.
- `Eph` independent full-grid QC — EXPECTED CONTENT/SOURCE BLOCK: 228
  adjudicated + 762 agreed = 990/990; 970 accepted, 2 reciprocal
  originally-agreed content errors at `5.2`, 18 source-choice uncertain.
  Three byte-identical QC/sidecar emissions, physical SHA
  `27b7ffec…` / `6c0091df…`; root `check-adjudication-qc` exit 1
  at blocking-status gate. Exact two-row correction and distinct
  post-correction QC remain; `gold_adjudication_batch_049.manifest.json`.
- `python -m unittest discover -s scripts/bible_module/tests` — PASS,
  415/415 in 31.423s after mixed-error correction-scope changes and
  new 7.4 batch evidence.
- `python -m unittest discover -s scripts/content_tool/tests` — PASS,
  30/30 in 9.150s; content tool remains untouched.

## Пауза владельца — 2026-09-12

- Все три агента завершили текущие ограниченные задания; новых заданий
  не запускалось. Ранее запущенные Flutter-команды завершились.
- Точная граница: pass 1 `66/66`, blind pass 2/comparison `57/66`,
  строгая book-level приёмка `36/66`; production Strong links `0`.
- `Phlm` pass 2, `1Thess` adjudication и `Eph` blocking QC зафиксированы
  выше; дальнейшее принятие этих книг требует отдельных проверок.
- Stage 8, SQLite, commit и push не выполнялись. Новая точка и очередь
  записаны в `HANDOFF.ru.md`.
