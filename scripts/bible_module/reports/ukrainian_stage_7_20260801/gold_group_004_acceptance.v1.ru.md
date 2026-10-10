# Приёмка gold группы № 4 — Gal, Eph, Phil, Col

**Gold: завершено 51/66; строго принято 38/66; с отсрочками 13.**

Gal, Eph, Phil, Col зарегистрированы как `completed_with_registered_deferrals`. Незарегистрированного остатка группы нет. Проверены 129 полных сеток / 4097 labels; effective proven 4038; исключены 59 labels в 24 loci и 2 reciprocal edges. Current content uncertainties 59, errors 0, accepted dependency exclusions 0.

Разрешены 48 исторических stable keys; оставлены 48 исторических и 11 новых исключённых keys. Исходные QC verdicts сохранены. Запечатанная Eph.5.2 correction учтена и проверена отдельным post-correction content reviewer. Новые Strong/NULL/source omission не назначались ради закрытия.

Единственный Markdown registry обновлён на месте: 185 issue IDs, 155 active loci / 428 active keys. 145 записей других групп сохранены побайтно. Immutable completion snapshot является техническим доказательством, а не параллельным рабочим реестром.

Один bounded research cycle на трудный случай; дополнительный цикл deferred places для завершения не требуется. Остальные группы, OT research, global finalize, stage 8, SQLite, production Strong, Flutter/runtime, working/web DB, commit и push не выполнялись.

| Книга | Полная сетка | Proven | Deferred | Loci |
|---|---:|---:|---:|---:|
| Gal | 1055 | 1039 | 16 | 4 |
| Eph | 990 | 975 | 15 | 6 |
| Phil | 1035 | 1021 | 14 | 5 |
| Col | 1017 | 1003 | 14 | 9 |

Авторы исследований: `/root/gal_eph_research`, `/root/phil_col_research`; автор proof/overlay/docs: `/root`; независимый reviewer: `/root/independent_qc`, запущен без авторской истории. Preflight и final inventory выполняет отдельный mechanical writer `/root/preflight`. Чтение проверяемых файлов — inspection; reviewer не автор исследований, исправления Eph.5.2, ledger или validator. Frozen reviewer answers не регенерировались.

- [gold_group_004_Gal_Eph.source_resolution.v1.ru.md](gold_group_004_Gal_Eph.source_resolution.v1.ru.md)
- [gold_group_004_Phil_Col.source_resolution.v1.ru.md](gold_group_004_Phil_Col.source_resolution.v1.ru.md)
- [gold_group_004_independent_content_qc.v1.ru.md](gold_group_004_independent_content_qc.v1.ru.md)
- [gold_group_004_independent_content_qc.v2.ru.md](gold_group_004_independent_content_qc.v2.ru.md)
- [gold_group_004.deferral_evidence.v1.manifest.json](gold_group_004.deferral_evidence.v1.manifest.json)
- [gold_completion_registry.v13.manifest.json](gold_completion_registry.v13.manifest.json)
- [gold_group_004_completion_policy.v4.manifest.json](gold_group_004_completion_policy.v4.manifest.json)
- [gold_group_004_preserved_inputs.v1.manifest.json](gold_group_004_preserved_inputs.v1.manifest.json)
- [gold_group_004_Col_gar.source_resolution.v1.ru.md](gold_group_004_Col_gar.source_resolution.v1.ru.md)
- [gold_group_004_G6063.source_resolution.v1.ru.md](gold_group_004_G6063.source_resolution.v1.ru.md)
- [gold_group_004_Gal_Eph.source_resolution_addendum.v1.ru.md](gold_group_004_Gal_Eph.source_resolution_addendum.v1.ru.md)
- [gold_group_004_candidate_revision.v2.manifest.json](gold_group_004_candidate_revision.v2.manifest.json)
- [gold_group_004_G6063.source_resolution.v2.manifest.json](gold_group_004_G6063.source_resolution.v2.manifest.json)
- [Единый реестр OH1988](oh88_strongs_issue_inventory.ru.md#registry-records)
- [HANDOFF](HANDOFF.ru.md)

Проверки: stage 3 offline / 4–7 read-only до полных JSONL; physical SHA/byte baseline4260 PASS; 234 regression tests PASS; четыре live completion validators, independent full-grid/content, exact deferral overlay/registry и post-seal audits PASS. Финальные stage/SHA/inventory/docs/git результаты фиксируются в HANDOFF и validation log. Strict validators и strict aggregate сохранены; uncertainties не требуют ложного strict PASS.

Первый draft candidate отклонён live validator из-за двух повторных исторических Markdown entries; candidate v2 ограничивает новые строки текущей группой и проверен независимо. V1 draft сохранён как не принятый, mutable registry не менялся до approval. G6063 classic correspondence доказан по первичным источникам для четырёх occurrences / девяти labels; frozen classic[] и source selection сохранены. Три metadata-only snapshot различия документированы отдельным author bridge и независимым audit; QC использует полные actual payloads. Raw extended номера не являются экспортируемыми classic Strong, будущему назначению требуется exact source или проверенный source-resolution proof.

Change checklist: scope только stage7 evidence/docs; runtime/state/routes/DB/dependencies/localization/release не затронуты. Flutter format/analyze/test/coverage и smoke N/A по scope и прямой границе владельца. Approved RU/EN пары не менялись; docs sync и forbidden-pattern gates сохраняются. Все новые docs связаны из этого отчёта и checkpoint.
