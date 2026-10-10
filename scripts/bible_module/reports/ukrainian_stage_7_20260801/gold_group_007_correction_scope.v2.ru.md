# Группа № 7: final correction scope v2

Дата: 2026-10-10. Actual actor: `/root/corrector_group007`. Supersedes [v1 report](gold_group_007_correction_scope.v1.ru.md) с сохранением всех его artifacts и semantic rows.

Итоговый correction scope — **10 baseline semantic rows**: consolidated1John v2 восемь rows в 2.22/4.13/4.20 и preserved2Pet v1 два classifier-only rows в 3.5/3.7. В этом follow-up выполнен **один** новый classifier row. Прежние семь полных correction payloads1John и оба2Pet payloads сохранены byte-identical в canonical rows; v1 correction/report/manifest/full-grid/input proofs не перезаписывались. Все3604 других baseline payloads группы и43 исторических blocking keys сохранены. Existing seal-correction/check-correction PASS, exit0; Strong assignments0.

## Новая строка 1John.4.20

Exact stable key: `original:gold7:original:557e036294ac465902177348e3aceb3f`.

Native o004 `ὅτι`, occurrence `tagnt:dd748faa55946494545ba24766a61df291eef81e41ceefcd292bd6a7b046f2a9:c01`, CONJ/G3754G, между `εἴπῃ` V-2AAS-3S и `ἀγαπῶ` V-PAI-1S. Exact OH1988: «Як хто скаже: „Я Бога люблю́“». Printed leaf1501/p1497 содержит двоеточие и quotation marks без отдельного conjunction в этом месте. Recitative ὅτι вводит прямую речь; independently inspected Burton §345 printed134 объясняет эту grammatical construction.

Меняется только `null_reason`: `translation_omission`→`grammatical_function_not_overt`. Original_omitted, singleton source group, empty target list и native ID сохранены. Ни source absence, ни new target/link/Strong не утверждаются. Before alignment SHA256 `3c8a4cf3d9662a3ce6776b45ae4f3aa7b6438e35c0a60fe81caf0610a610f518`; after `0dba4eba48d2dd34112abed3d2f5dc528103c1c990bef702130997cf6e5a4315`. Supersedes lock относится к ORIGINAL pre-overlay base, как и все восемь consolidated rows.

Две исторические error rows selected οὐ↔«як» в том же4.20 здесь не исправлялись: exact payloads и error verdicts сохранены для root closed deferral. Recitative o004 — иной stable key, отсутствующий в43 historical blocking keys. Не объявляется acceptance всего4.20.

## Сохранённые corrections и actual роли

1John2.22 сохраняет ἀρνούμενος→«відкидає» и native redundant οὐ NULL/grammatical_function_not_overt. 1John4.13 сохраняет jointἐντούτῳ→«тим» и resumptive italic«це» translation_addition. 2Pet3.5/3.7 сохраняет два non-overt article NULL classifiers, без direct article→case-word links. Current effective correction chains: [1John v2](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/1John.correction_chain_locks.v2.json) и [2Pet v1](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/2Pet.correction_chain_locks.v1.json).

Я — distinct correction author/scope inspector; новый own content scope — только exact4.20 recitative construction, дополнительно к четырём grids, inspected приv1. Reconstruction полного final grid является structural reproduction, не самостоятельным independent content QC. Primary grammar research и fresh independent original-base QC authored отдельно; fresh reviewer `/root/final_qc` выполнил собственное чтение97 grids. Я не автор research, независимого QC, registry или completion. Reading reviewed files is inspection, не authorship. [Own delta/role receipt](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/1John.scope_inspection.v2.json).

## Evidence closure и проверки

Fresh consolidated blockingQC v1 не использовался для correction: он связывал transient expanded authorv3 report/manifest/cases, а restored frozenv3 имел прежние bytes/digests. Этот stale evidence diagnostic сохранён без source flip, fabricated bridge или rewriteQC. Исправлена версия evidence closure через новую separately frozen QC, привязанную к READY author evidence. Это metadata repair того же bounded proof cycle; новая semantic задача не изобретена.

Перед payload execution проверены physical SHA/bytes всех fresh scope locks, frozen source/chain и preserved correctorv1 artifacts. [Exact input lock receipt](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/1John.consolidated_input_locks.v2.json). Existing seal/check проверяют8 rows отoriginalbase, complete reciprocal/NULL accounting и exact scope. Seven carried rows имеют те же complete payloads, v2 full final grid отличается отv1 ровно одним classifier. [Live receipts](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/1John.correction_livecheck_receipt.v2.json); [immutable43-key preservation proof](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/historical_scope_preservation.v1.json); [v2 manifest](gold_group_007_correction_scope.v2.manifest.json).

Change checklist применён: runtime/DB/source_selection/mapping/gold/folds/registry/dependencies/release/localization/approved RU-EN pairs и quality gates не менялись; Flutterformat/analyze/tests/smoke N/A для evidence-only correction. New validator не добавлен. Commit/push не выполнялись. Book completion, strict acceptance и export не объявлены; independent actual post-correction content QC остаётся fresh reviewer.
