# OH1988 — независимый final content/completion QC группы №3, v1

Дата: 2026-10-10. Reviewer: `subagent:/root/independent_qc:group003:20261010`.

**Candidate approval: PASS.** Самостоятельно прочитаны все 139 окончательных
verse grids Acts/Rom/1Cor/2Cor и проверены 4527 stable keys. Приняты 4467 labels,
60 остаются `uncertain`, definite errors 0. Completion overlay исключает ровно
60 labels / 12 reciprocal edges в 24 loci. Accepted dependencies вне этих
uncertainties не исключаются. Это отдельная проверка текущих решений после
существующей Acts.13.29 correction; исторические blind passes, adjudication и
initial QC не повторялись.

| Книга | Полные сетки | Reviewed labels | Effective proven labels | Deferred labels | Loci | Edges |
|---|---:|---:|---:|---:|---:|---:|
| Acts | 39 | 1436 | 1419 | 17 | 5 | 5 |
| Rom | 33 | 1056 | 1040 | 16 | 8 | 3 |
| 1Cor | 33 | 952 | 946 | 6 | 3 | 1 |
| 2Cor | 34 | 1083 | 1062 | 21 | 8 | 3 |
| Всего | 139 | 4527 | 4467 | 60 | 24 | 12 |

Счётчики относятся к reviewed alignment/accounting labels. Они не являются
числом опубликованных Strong links. Global gold/production acceptance и экспорт
этим reviewer не выполнялись. Книги ещё требуют отдельно sealed completion и
post-seal physical review; candidate approval не подменяет эти действия.

## Фактическая независимость и выполненная работа

Reviewer получил свежий `fork:none` контекст с репозиторными инструкциями и
самостоятельным поручением QC, без авторской истории root. Фактическая роль —
`independent_content_and_completion_reviewer`. Проверяемые авторы:
`/root`, `/root/acts_rom_research`, `/root/corinthians_research`.
Reviewer не писал проверяемые research/corrections, ledger либо completion
validator. Чтение этих файлов — инспекция, не авторство. Один reviewer ID сам по
себе не является доказательством независимости; её подтверждают отдельные
действия и receipts ниже.

Сначала reviewer восстановил и прочитал current grids, написал 139 собственных
verse-specific обоснований, затем сопоставил отдельные авторские research
packets с actual occurrence evidence. Визуально прочитаны 26 точных scan leaves:
13 Acts/Rom и 13 Corinthians. Проверены source display/lemma/Strong identities,
sameverse lexical concordance, primary SBL text/apparatus, specific VarApp
readings и доступные авторские grammatical/commentary explanations. Недоступные
автору документы не выдавались за прочитанные manuscript evidence.

Все 4527 per-key observations содержат точный `final_decision`, точные
`source_evidence` / `target_evidence` из answer-free template, собственное
обоснование, actual reviewer ID и `reciprocal_accounting_checked: true`.
Повторные source/target occurrences не сопоставлялись по одному порядку или
общему verse bag. Обе стороны каждой hyperedge, полный node roster, scalar и
UTF-8 spans проверены. Для closure построена отдельная source-incidence graph,
не копия результата автора `reciprocal_components`.

## Содержательные выводы

Из 105 исторических uncertain keys 48 приняты относительно actual selected
reference occurrences; 57 остаются без доказанного назначения. Direct lexical
и grammatical links проверены в своих clauses: например, каже и второе ваших
в Acts.2.38, Judas/travel tail Acts.15.34, названия ветров Acts.27.12, три knowing
occurrences 1Cor.8.2, repeat-relative particle 1Cor.11.26, permission group
1Cor.14.34, light predicate 2Cor.4.6 и имеет силу 2Cor.9.8. Историческая
translator Vorlage этими выводами не устанавливается. Alternate lemma/Strong
не переносится в selected source.

Существующая correction Acts.13.29 содержательно подтверждена: καθελόντες/G2507
сохраняет «зняли Його», а «то» является украинским корелятом «Коли» и не получает
G2507. Обе correction rows находятся в полной final grid; новые corrections не
понадобились.

Самостоятельная полная проверка выявила два дополнительных loci вне прежнего
списка. Старый accepted QC verdict сохранён как history; новая uncertainty не
переименована в definite error:

- 1Cor.2.13: target «Святого» виден в OH1988 и в alternate ἁγίου, но selected
  layer не содержит Holy original ID. Addition classifier не доказан.
- 2Cor.8.19: selected σύν и target «для» имеют неподтверждённый source-NULL /
  target-addition accounting. Два exact nodes отложены без новой связи.

Отдельные три source-only nodes καὶ προθυμίαν ἡμῶν в 2Cor.8.19 сохраняют только
фактический `source_text_not_rendered`: reference содержит phrase, printed
target её не содержит. Это не утверждение translator omission либо Vorlage и
не target Strong assignment.

Случаи verse-boundary/source-projection divergence (Rom.6.1, 2Cor.8.13,
2Cor.10.4), обратные possessive roles 2Cor.7.12, preposition/source-choice cases,
extended G9995/G20447 и отсутствующие selected name/title nodes зарегистрированы
с exact identities и missing proof. Повторный цикл исследования для book
completion не требуется.

## Completion tool и candidate overlay

Независимо прочитан correction-aware
[completion v2](../../ukrainian_stage_7_completion_v2.py) и
[его tests](../../tests/test_ukrainian_stage_7_completion_v2.py).
Обнаруженная reviewer ошибка поля correction metadata author исправлена автором:
guard учитывает `correction_reviewer_id` header и `reviewer_id` decision rows.
Reviewer самостоятельно запустил 8 focused tests: PASS. Live v2 final grids
побъектно совпали с independently reconstructed corrected grids.

Live completion validation четырёх candidate configs/projections: PASS;
проекции побайтно совпадают с live outputs. Все accepted effective decisions
сохраняют exact frozen payload. Deferred identity nodes имеют empty edges,
`assigned_strongs: []`, `strong_assignment: null` и выключены из training,
scoring и Strong export; overlay не утверждает omission/addition classifiers.
Closed exclusions точно равны 60 uncertainties, без принятых collateral nodes.

Единственный editable human registry —
[oh88_strongs_issue_inventory.ru.md](oh88_strongs_issue_inventory.ru.md).
Candidate snapshot содержит 181 unique issue IDs: 179 прежних и 2 новых.
Все 150 unrelated Markdown index rows и все 150 unrelated technical proof rows
побайтно сохранены. Для 29 прежних current-group issues сохранены exact
исторические affected keys, decisions и QC status; три новых uncertain keys
сохраняют исходный accepted history. Technical JSONL — immutable proof приёмки,
не второй editable registry.

## Exact review artifacts

- [Actual-role attestation](../../work/ukrainian_stage_7_20260801/session_group3_20261010_independent_qc_01/actual_role_attestation.v1.json).
- [139 собственных verse rationales](../../work/ukrainian_stage_7_20260801/session_group3_20261010_independent_qc_01/verse_grid_rationales.v1.txt).
- [4527 per-key observations](../../work/ukrainian_stage_7_20260801/session_group3_20261010_independent_qc_01/independent_full_grid_observations.v1.jsonl).
- [Content/accounting receipt](../../work/ukrainian_stage_7_20260801/session_group3_20261010_independent_qc_01/independent_content_accounting.v1.json).
- [Research physical/occurrence receipt](../../work/ukrainian_stage_7_20260801/session_group3_20261010_independent_qc_01/research_physical_and_occurrence_review.v1.json): 222 references / 180 unique physical files, errors 0, skipped 0.
- [Independent v2 grid crosscheck](../../work/ukrainian_stage_7_20260801/session_group3_20261010_independent_qc_01/v2_grid_crosscheck.v1.json).
- [Exact locked candidate approval](../../work/ukrainian_stage_7_20260801/session_group3_20261010_independent_qc_01/independent_completion_review.v1.json): 12225 bytes, SHA256 `ca3464cda704b24524038bab8734bbabc36139b8463f2abd43ecc44e545db4fa`.

Review scope: только группа003. Sealed history не менялась; другие группы,
global finalize, stage8, SQLite/working/web DB, runtime, production markup,
commit и push не выполнялись. Flutter checks N/A для reviewer evidence scope;
targeted physical, content, span, reciprocal и completion checks выполнены.
