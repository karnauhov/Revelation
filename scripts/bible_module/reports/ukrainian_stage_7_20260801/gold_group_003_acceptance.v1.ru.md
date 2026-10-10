# OH1988 — группа № 3 завершена, 2026-10-10

**Gold: завершено 47/66; строго принято 38/66; с отсрочками 9.**
Acts, Rom, 1Cor, 2Cor зарегистрированы как `completed_with_registered_deferrals`.
Незарегистрированного остатка текущей группы нет. OT не переоткрывался;
остальные группы и global finalize не запускались. Accepted production links — 0;
полнота завершения книги отличается от доказанного покрытия Strong.

| Книга | Полные сетки | Проверено labels | Effective proven | Deferred labels | Deferred loci |
|---|---:|---:|---:|---:|---:|
| Acts | 39 | 1436 | 1419 | 17 | 5 |
| Rom | 33 | 1056 | 1040 | 16 | 8 |
| 1Cor | 33 | 952 | 946 | 6 | 3 |
| 2Cor | 34 | 1083 | 1062 | 21 | 8 |
| Всего | 139 | 4527 | 4467 | 60 | 24 |

Независимый content QC: accepted 4467, uncertain 60, error 0. Замкнутые
exclusions содержат ровно 60 keys и 12 reciprocal edges; accepted dependency
exclusions — 0. Identity deferred nodes сохранена, edges пусты, Strong не назначен,
training/scoring/Strong export запрещены для этих nodes. Недоказанные NULL/addition
classifiers отсутствуют в effective deferred payloads. Overlay требуется live
проверять перед будущим использованием; текущая работа экспорта не разрешает.

## Решения и исправления

Из 105 прежних uncertain keys 48 разрешены по evidence конкретного occurrence,
57 зарегистрированы как отсрочки. Acts.2.38 — speech и possessive pairs;
Acts.15.34 — conjunction/name/travel pairs; Acts.27.12 — wind names/conjunction;
Rom.6.1 — существующий verb pair; Rom.12.5 — article function accounting.
1Cor.8.2 — knowing occurrences и разрывное отрицание; 1Cor.11.26 — modal function;
1Cor.14.34 — controlled possessive/permission/submission;
2Cor.3.1 — вопрос; 2Cor.4.6 — первый shining occurrence;
2Cor.9.8 — ability group; 2Cor.11.28 — pronoun span; 2Cor.12.3 — without span.
Историческая Vorlage не реконструирована; альтернативный номер из другого
reading или стиха не назначен. Exact historical edition не добавлена как gate
для уже доказанных source-reference links.

Новых semantic corrections нет; отдельный corrector для новых corrections — N/A.
Запечатанное двухстрочное исправление Acts.13.29 сохранено и включено в final grid:
G2507 связан со «зняли Його», коррелят «то» не включён в lexical edge.
Versioned [completion v2](../../ukrainian_stage_7_completion_v2.py) учитывает эту
цепочку через неизменённый strict correction validator и повторное accounting.
V1, strict validators и исходные review artifacts не переписаны.

Независимый final-grid review обнаружил дополнительно 1Cor.2.13 «Святого» и
2Cor.8.19 source συν / target «для»: три новых uncertain keys. Их прежний accepted
QC сохранён как история; новые observations имеют uncertain, без definite error.
Три source-only tail nodes 2Cor.8.19 приняты лишь как фактическое
`source_text_not_rendered` относительно reference/print, без вывода о translator
omission или Vorlage и без target Strong.

## Отложенные места

- Acts: 2.38, 5.34, 13.26, 15.34, 27.12.
- Rom: 3.22, 6.1, 6.11, 9.31, 11.25, 13.11, 15.8, 15.15.
- 1Cor: 2.13, 10.28, 11.31.
- 2Cor: 4.6, 5.3, 5.18, 7.12, 8.13, 8.19, 10.4, 11.28.

Каждое место прошло один bounded cycle с exact OH1988 scans, локальными
original occurrence/lemma/Strong controls и доступными apparatus/scholarly sources.
Missing proof, попытки, findings, exact source/target IDs и scalar/UTF8 spans,
input digests и optional follow-up находятся в единственном
[реестре OH1988](oh88_strongs_issue_inventory.ru.md#registry-records).
Повторное исследование не является условием завершения.
Реестр содержит 181 issue ID: 167 active loci / 465 active keys и 14 history records.
Обновлены 29 прежних записей группы, добавлены две; остальные 150 сохранены побайтно.
Все прежние sealed JSONL и manifests остаются технической историей.
Новый locked snapshot — неизменяемое доказательство completion, не второй
редактируемый реестр; указатель — [deferral evidence](gold_group_003.deferral_evidence.v1.manifest.json).

## Реальные роли и доказательства

`/root/acts_rom_research` и `/root/corinthians_research` — отдельные авторы
bounded research. `/root` — автор completion v2, tests, registry/proof preparation
и приёмочных записей. `/root/independent_qc` — reviewer с `fork_turns=none`,
не автор исследуемых research/corrections/ledger/validator. Он сначала самостоятельно
восстановил и прочитал 139 grids, написал собственные 139 verse rationales,
проверил 26 scan leaves, per-key content/span/accounting и затем author packets.
Независимость подтверждена фактическими ролями и собственными receipts;
чтение проверяемых файлов — inspection, не authorship. `/root/inventory_writer`
обновляет artifact inventory отдельным helper-only действием.

- [Acts/Rom research](gold_group_003_Acts_Rom.source_resolution.v1.ru.md),
  [v1 seal](gold_group_003_Acts_Rom.source_resolution.v1.manifest.json),
  [v2 exact publication/input bridge](gold_group_003_Acts_Rom.source_resolution.v2.manifest.json).
- [1Cor/2Cor research и supplemental cases](gold_group_003_1Cor_2Cor.source_resolution.v1.ru.md),
  [v1 seal](gold_group_003_1Cor_2Cor.source_resolution.v1.manifest.json).
- [Независимый content/overlay QC](gold_group_003_independent_content_qc.v1.ru.md),
  [v1 seal](gold_group_003_independent_content_qc.v1.manifest.json),
  [post-seal v2](gold_group_003_independent_content_qc.v2.ru.md),
  [formatting bridge v3](gold_group_003_independent_content_qc.v3.ru.md).
- [Acts completion](gold_group_003_Acts.completed_with_deferrals.v1.manifest.json),
  [Rom](gold_group_003_Rom.completed_with_deferrals.v1.manifest.json),
  [1Cor](gold_group_003_1Cor.completed_with_deferrals.v1.manifest.json),
  [2Cor](gold_group_003_2Cor.completed_with_deferrals.v1.manifest.json),
  [completion registry v9](gold_completion_registry.v9.manifest.json).
- [Owner policy v3](gold_group_003_completion_policy.v3.manifest.json),
  [точные preserved input locators](gold_group_003_preserved_inputs.v1.manifest.json),
  [EOF formatting receipt](gold_group_003_registry_formatting_bridge.v1.manifest.json),
  [v2 regression tests](../../tests/test_ukrainian_stage_7_completion_v2.py),
  [validation log](validation_log.md), [актуальный HANDOFF](HANDOFF.ru.md).

## Проверки и границы

До full work reads stage 3–7 preflight прошёл, физически проверены 4046 inventory
entries и входные SHA/byte locks. Исходный git status чистый; девять baseline
snapshots сохранены. 234 stage-7 regression tests прошли, включая восемь новых
v2 tests с negative subcases. Независимые content/tool/overlay checks и четыре
live completion validators прошли; candidate/sealed projections побайтно равны.
Strict QC по исходным uncertainties ожидаемо отклонён правильным status gate,
структурный или stale отказ не выдаётся за успешную completion-проверку.

Финальные stage, regression, SHA/inventory, post-seal, docs и git diff результаты
фиксируются в validation log и последнем HANDOFF после их фактического выполнения.
Checklist scope: Python evidence/completion tools/tests и docs; runtime/routes/
state/l10n/dependencies/release не менялись. Flutter format/analyze/test/coverage
и integration smoke для этого scope N/A; релевантные Python/live checks выполнены.
Approved RU/EN architecture/testing pairs не менялись; docs-sync проверяется.
Immutable stage-6 text/comment, mapping, original selection, gold selection/folds
и frozen review answers сохранены. Stage 8, SQLite/working/web DB, production
markup, Flutter/runtime, commit и push не выполнялись.
