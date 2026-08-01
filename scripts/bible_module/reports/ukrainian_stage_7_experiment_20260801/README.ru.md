# Снимок отклонённого Strong-эксперимента

Этот каталог сохраняет незавершённую попытку Strong-выравнивания как воспроизводимый baseline и источник кандидатов. Он не является каталогом доказательств выполненного этапа 7.

Структурный результат эксперимента:

- 31 102 target-позиций;
- 595 077 украинских surface tokens;
- 440 280 Strong occurrences;
- 399 645 tokens получили хотя бы один экспериментальный binding;
- 195 432 tokens остались unaligned;
- 180 406 Strong occurrences в 30 135 targets имеют low-margin status;
- `Isa.53.5`, `Mic.6.8`, `Luke.2.11` и `Acts.2.38` вручную подтверждают ошибочность части bindings;
- unresolved critical/high: 0/1.

Разрешено переиспользовать парсеры controls, raw Strong normalization, renderer/stripper, exact round-trip, coverage scaffolding, восемь control-reference overrides, CC0 fixtures и контрпримеры. Все surface bindings и confidence labels являются только `legacy_baseline` evidence и должны быть переоценены с нуля.

Эксперимент повторно синтезировал украинский текст из stage 5. Будущая реализация этапа 7 обязана вместо этого прочитать точный stage-6 `synthesized_text.jsonl` и проверить опубликованный SHA-256.

Внутренние manifests и отчёты сохранены побайтно, поэтому их исходный contract name и названия artifact paths не переписаны после переноса каталога. Полный производный corpus перемещён в gitignored `scripts/bible_module/work/ukrainian_stage_7_experiment_20260801/`.

Актуальный план новой реализации: [`ukrainian-bible-strongs-stage-7-alignment-plan.ru.md`](../../../../docs/ru/content/ukrainian-bible-strongs-stage-7-alignment-plan.ru.md).

