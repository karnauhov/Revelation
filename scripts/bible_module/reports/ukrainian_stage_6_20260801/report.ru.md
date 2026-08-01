# Этап 6 — синтез украинского текста

- `schema_version`: 1
- `contract_version`: `ukrainian-stage-6-text-synthesis-v1`
- mapping: `oh1988-kjv-protestant-v1` (не изменён)
- статус: **complete**

Wikisource OH1988 является единственным базовым текстом; точный Commons/IA scan и независимые normalized источники этапа 4 использованы только как контроль. Синтезировано 31102 непустых target-позиций; учтены 31171 source spans и 595095 source word tokens без потери и дублирования. Merge использует U+0020 (72 вставок). Четыре split основаны на versioned scalar overrides и точном Commons DjVu; четыре разделительных U+0020 исключены только на доказанных печатных границах. `2Chr.14.14` сохранён отдельно как source-only range material.

Разрешено 1318 target anchors через доказанные source→target интервалы. Все 1329 uses/markers сохранены ровно по одному разу; 11 heading uses остались non-verse. Определений: 1204; named definitions: 99; uses не дедуплицированы. Пустой comment используется для стиха без сносок, blocks разделяются двумя LF. Все 149 OCR-review текстов визуально сверены с точным Commons scan и оставлены без изменения.

Plain-text preservation: 31102 / 31102; lost/duplicated source word tokens: 0 / 0; unresolved critical/high: 0 / 0. Strong-разметка намеренно не входит в этот этап и перенесена в этап 7. SQLite и бывший этап 7 (теперь этап 8) не выполнялись.
