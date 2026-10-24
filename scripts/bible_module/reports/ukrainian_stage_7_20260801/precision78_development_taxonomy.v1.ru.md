# 7.8 — development error taxonomy

Doc-Version: `1.0.0`
Last-Updated: `2026-10-17`
Source-Commit: `working-tree`

Только eligible development folds0–2; это inspection finalized labels, не новая
разметка или независимая оценка policy. Главный вывод и все 342 строки доступны в
[feasibility report](precision78.v1.ru.md). Training/new annotation остановлены NO_GO.

Единица — полная semantic hyperedge (verse, relation, все original IDs, все target IDs,
null reason). Для каждого selected false edge найдены overlapping gold groups;
расстояние — сумма symmetric differences endpoint sets по обеим сторонам.
Сохраняются **все** ties ближайшей группы, их IDs и digests. Multi-label категории
могут пересекаться, их нельзя складывать как непересекающиеся причины ошибок.
Необработанная семантическая неоднозначность не превращается в определённую причину.

Проверено 5782 selected false edges. Структурная taxonomy воспроизводима; для causal/philological taxonomy требуется отдельный development review, который здесь не выдаётся за выполненный.

| Категория | Правило и предел интерпретации |
|---|---|
| wrong_endpoints | Есть и пропуск, и лишний endpoint относительно ближайшей gold group; либо нет overlap. Это точное расхождение IDs, не доказанная lexical причина. |
| incomplete_group | В ближайшей полной gold hyperedge есть original/target участник, отсутствующий у prediction. Общая группа не разбивается на pairs. |
| extra_participant | Prediction содержит original/target участника вне ближайшей gold group. Может одновременно иметь incomplete/wrong endpoints. |
| relation_null_semantics | Endpoints полностью совпадают, relation или null_reason различается. Отсутствующий candidate не превращается в NULL. |
| repetition | Verse-level hint: повтор original Strong-list либо OH comparison form. Может не касаться именно ошибочного endpoint; не causal label. |
| morphology_polysemy | Hints отдельно: morphology отсутствует/heuristic candidate содержит unresolved; либо frozen prior.polysemous. Реальная morphology incompatibility/смысл не доказаны автоматически. |
| textual_conflict | Frozen relation textual_alternative, nonprimary/unresolved original reading либо explicit provenance conflict. Это evidence hint; source choice не изменяется. |
| decomposition_selection | Ошибочное selected edge конфликтует с exact-gold candidate, не выбранным top-1; сохранены IDs и alternative n-best ranks. Замена в полном bundle и суммарный выигрыш не доказаны. |

Структурные сигнатуры:

| Структурное расхождение | Edges (multi-label) |
|---|---:|
| wrong_endpoints | 2126 |
| incomplete_group | 3024 |
| extra_participant | 4884 |
| relation_null_semantics | 0 |

Evidence hints, не доказанные причины:

| Evidence hint | Edges |
|---|---:|
| repetition | 5273 |
| morphology_unresolved | 4517 |
| polysemy | 0 |
| textual_conflict | 0 |

Decomposition opportunity: 946 false edges конфликтуют с доступной правильной альтернативой; это не число совместимых исправлений и не измеренный прирост precision.

Отдельные endpoints/ties не являются gold decomposition. Shared target declarations
и multiplicity остаются intact. Original/target IDs из разных gold groups не сливаются
в новый label. Unknown/uncovered не становится NULL. Причины retrieval failure не
выводятся из отсутствия candidate.

Три раздельных показателя: (1) precision будущего selected subclass — **не измерена**;
(2) улучшение выбора внутри saved graph — **не измерено**, сейчас только opportunity
signatures; (3) retrieval coverage — исторические 7401/27462 из7.6, не новая оценка.
Разница 7401−6479=922 не является достижимой гарантией; 20061 gold edges вне union
останется вне возможностей reranker. Это обосновывает отдельное обсуждение generators
после development review, сохраняя frozen graph7.6.

Для B_review первыми полезно показывать полные конфликтующие groups и source
provenance, выявлять неполноту/лишних участников; не повышать score простым повтором
того же источника. Prior ambiguity и morphology здесь используются как подсказки
для inspection, без новых Strong decisions и без переоткрытия deferrals.

[Summary/definitions](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/taxonomy.v1.json), [все stable cases с полными semantic IDs, graph-row и gold-row digests](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/development_error_taxonomy.v1.jsonl).
