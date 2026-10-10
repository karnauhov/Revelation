# Исправление синтаксической привязки 1Tim.1.13 — v1, 2026-10-10

Отдельный corrector `/root/corrector_1tim` выпустил immutable correction трёх решений по sealed independent blocking QC и bounded research packet `/root/tim_research`. Чтение исследований и прежних решений было инспекцией; corrector не является автором исследовательского пакета или независимым QC своих исправлений.

| Строка | До | После |
| --- | --- | --- |
| o001 τὸ, G3588, T-ASN | one_to_one → t002 що | original_omitted / grammatical_function_not_overt (no-target grammar) |
| o003 ὄντα, G1510, V-PAP-ASM | one_to_one → t004 був | one_to_many → t002 що + t004 був |
| t002 що | aligned ← o001 τὸ | aligned ← o003 ὄντα |
| t004 був | aligned ← o003 ὄντα | без изменения, reciprocal revalidation |

Выбранное τὸ πρότερον имеет адвербиальную функцию. Neuter τὸ не определяет masculine ὄντα и не является источником украинского относительного що. Существующая лексическая привязка πρότερον к давніше сохранена. Украинское що … був передаёт причастное выражение ὄντα как конечное относительное предложение. SBLGNT, locked UGNT и фактически просмотренный скан OH1988 (лист1462, печатная1458) подтверждают формы и текст «мене, що давніше був». Traditional τὸν не подменяет selected source.

Existing gold contract кодирует любое source-решение без target как relation=original_omitted с отдельным null_reason. Здесь grammatical_function_not_overt означает грамматическую функцию без отдельного выражения, без утверждения translation_omission или source_text_not_rendered. QC recommended label null не входит в allowed relations; corrector использовал действующий schema label без изменения семантического scope. Первый структурно отвергнутый builder/role сохранён отдельно; frozen QC не переписывался. Strong G3588/G1510 сохранены как существующие идентификаторы; новые Strong не назначались.

Перед полным чтением используемых JSONL проверены SHA-256 и bytes. Existing seal_consensus_correction_shard и validate_consensus_correction_shard, а также live CLI seal-correction/check-correction прошли. Воспроизведён full final grid1013; только3 alignments изменены,1 reciprocal target проверен без изменения,19 scalar/UTF-8 target spans этого стиха совпадают. Статус correction: complete_manual_consensus_correction_pending_independent_qc. Acceptance и completion утверждает отдельный reviewer/root после независимого QC.

[Correction manifest](gold_group_005_1Tim.correction.v1.manifest.json) фиксирует входные/выходные SHA-256 и bytes, роли, exact scope и live receipts. [Source research](gold_group_005_1Tim_2Tim.source_resolution.v1.ru.md) описывает законченный bounded cycle. Frozen passes/adjudication/QC, selected layer, stage6, mapping, gold selection/folds не менялись. Runtime/DB и commit/push не выполнялись.
