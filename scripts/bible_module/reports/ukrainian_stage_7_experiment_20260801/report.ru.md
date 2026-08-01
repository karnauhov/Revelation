# Этап 7 — добавление индексов Стронга в украинский текст

- `schema_version`: 1
- `contract_version`: `ukrainian-stage-7-strong-alignment-v1`
- mapping: `oh1988-kjv-protestant-v1` (не изменён)
- статус: **не завершён — требуется доказательное ручное Strong-выравнивание**

## Текст

Wikisource OH1988 назначен единственным базовым текстом; точный Commons/IA scan и независимые normalized источники этапа 4 использованы только как контроль. Синтезировано 31102 непустых target-позиций; учтены 31171 source spans и 595095 source word tokens без потери и дублирования. Merge использует U+0020 (72 вставок). Четыре split основаны на versioned scalar overrides и точном Commons DjVu; четыре разделительных U+0020 исключены только на доказанных печатных границах. `2Chr.14.14` сохранён отдельно как source-only range material.

## Strong

Кандидатная разметка построена непосредственно между украинскими surface tokens и OSHB/TAHOT/UXLC для OT, TAGNT/UGNT для NT; KJV, TR, RST и соседние стихи не использовались как источник Strong. Сохранено 440280 Strong occurrences: OT 299425, NT 140855. Покрыто 399645 из 595077 украинских surface tokens; 195432 tokens без прямого Strong сохранены отдельным полным списком. Invalid/dangling Strong: 0. Plain-text round-trip: 31102 / 31102.

Автоматическая corpus/position модель детерминирована и сохраняет raw Strong, normalization, control token и score evidence, но не является достаточным доказательством окончательной пословной связи. Её собственный low-margin шлюз выявил 180406 Strong occurrences в 30135 target-позициях (OT 128930, NT 51476). Ручная safety-выборка зафиксировала несовместимые surface bindings в `Isa.53.5`, `Mic.6.8`, `Luke.2.11` и `Acts.2.38`. Исправления не угадывались; весь агрегат оставлен unresolved high в `manual_review.jsonl` и `source_diff.csv`. Поэтому `strong_aligned_text.jsonl` является только незавершённым кандидатом и не разрешён для этапа 7.

## Сноски и comments

Разрешено 1318 target anchors через доказанные source→target интервалы. Все 1329 uses сохранены ровно по одному разу; 11 heading uses остались non-verse. Определений: 1204; named definitions: 99; uses не дедуплицированы. Пустой comment используется для стиха без сносок, blocks разделяются двумя LF.

Все 149 OCR-review текстов визуально сверены с точным Commons scan и оставлены без изменения. Exit criteria этапа 7 не выполнены из-за Strong-привязок; дорожная карта не закрыта. SQLite и этап 8 не выполнялись.
