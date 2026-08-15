# Этап 7 — текущий HANDOFF, пауза 2026-08-15 после `Judg`

> **CURRENT PAUSE POINT.** Этот файл полностью заменяет предыдущий HANDOFF.
> Этап 7 остаётся в работе. Активных stage-7 Python-процессов и работающих
> подагентов нет. Этап 8 и SQLite не начинались. Commit/push автоматически не
> выполнять.

## Состояние репозитория

- Сеанс начат с чистого коммита `e0acc66` (`Advance Ukrainian Strong stage 7
  evidence pipeline [skip ci]`).
- Текущие незакоммиченные изменения — regenerated stage-7 reports, roadmap,
  два новых versioned manifest и regression-правка stage-7 теста.
- Полные corpora/candidates/gold packets и completed reviewer submissions
  находятся только в gitignored `scripts/bible_module/work/`.
- Пользовательские изменения не удалять; commit/push выполняет только владелец.

## Неизменяемые входы

- edition/module/code: `ohienko_1988` / `ohienko_1988` / `OH1988`;
- canon/versification/mapping: `protestant_66` / `kjv_protestant` /
  `oh1988-kjv-protestant-v1`;
- target positions: `31 102`;
- stage-6 text: `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`;
- stage-6 manifest: `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af`;
- stage-6 comments: `5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4`;
- fingerprint-selected layer: 678 144 rows / SHA-256
  `a2f8b017b702b8217ce4242e2578082f134b615be64968f190c066c0d4692c82`;
- Ukrainian token inventory SHA-256
  `62caa29ff269c9ca8dad4b64c656728a645b3d09210034ddcc953c5363c567e1`;
- source registry SHA-256
  `b1f7e2bc82929bdd40c5701f4d16ff00387da8645c5279cf311adc12973ffebd`;
- gold-selected layer / panel / workbench SHA-256:
  `500482d4b1ce58f9749fe9e53b58bf8bce6be1558df926dacfbe0df29cf09ca4` /
  `6f6ce4ce4eb8a941ae8fa4328798873141743889efb386cae15375db3fe0245c` /
  `d5d1aa78368520a152cd869aaa8c729a6008e86f5af359c2d9aac29138d934c2`.

## Интегрированный candidate/report bundle

- Main generation и независимый `--check` завершены.
- Всего 872 025 candidate-only rows:
  - first-party: 501 518;
  - bidirectional statistical OOF: 163 140;
  - multilingual contextual: 207 367.
- `resolver_eligible=0`, automatic acceptance `0`, accepted links/Strong markers
  `0` до finalized gold/calibration.
- Двойная integrated generation совпала по 46 файлам; aggregate SHA-256
  `f874ad0bc1227220db0307e45e4f020188cc2c1a5efc0a095deff2adc6648aae`.
- Оба statistical и оба contextual full bundle ранее побайтно совпали;
  contextual JSONL SHA-256
  `0e1e90dd1c2ffa2c907861a5eeba551bed00038015a0823ebc673446198a3881`.
- Stage-3/4/5/6 `--check` после integrated generation прошли.

## Авторские сноски OH1988

- Пункт 7.1 закрыт как отдельный zero-vote evidence-канал: 1 204 определения,
  1 329 uses, 1 222 target refs, 267 exact same-locus matches, 355 unmatched
  original-form mentions и 7 textual-variant notes.
- Versioned `author_comment_evidence.manifest.json` включён в artifact inventory;
  work JSONL SHA-256
  `0cc59c16c4b61e65ffc260c4401204d26b49a5ec28e90575421ed8f01f09dea3`.
- Manual review получил 329 medium + 7 high records. Сноски не меняют
  `target_comment`, candidate selection или Strong автоматически.

## Gold 7.4

- Answer-free panel: 2 171 verses, 45 831 original и 41 807 target decisions на
  каждый pass; по 66 exact book-shards.
- Оба независимых blind passes завершены для первых семи книг `Gen–Judg`:
  228 стихов, 5 832 original и 4 825 target decisions exact-once на каждый pass.
- Все 14 compact expansions имеют разные reviewer IDs, `blind=true`, прошли
  merge-ready check с `error_count=0`; расхождения не сглажены.
- Последние завершённые shards:
  - `Josh` pass 1 raw SHA `17bfc8fe3b3c9b10bf2c71b314cb6b2f031b02b0cda1318929c9eaec9706d2f0`;
  - `Josh` pass 2 raw SHA `f12d0812d20e669f1dea89bf7b92d75d8fb110160b9b03bff5976b62e86d3480`;
  - `Judg` pass 1 raw SHA `653ea270cd27eeadffcb45fdb099ae6243d054356a4d81356b356c27bf6fe8b5`;
  - `Judg` pass 2 raw SHA `0048ca624619e9d17d2ef52e190a3a094c296456bb005848d117dd3fed319603`.
- Осталось 59 книг. Следующая — `Ruth`, shard `008` в обоих проходах.
- Finalized gold, merge/adjudication, evaluator metrics, calibration и production
  links отсутствуют; оба пункта 7.4 поэтому остаются открытыми.
- Владелец явно разрешил продолжать два независимых blind gold-прохода
  подагентами. При возобновлении создать два изолированных reviewer tasks для
  `Ruth`: pass 1 не читает pass 2, pass 2 не читает pass 1; обоим запрещены
  candidates, legacy, reports и completed answers других книг.
- Текущий versioned artifact inventory создан до completed `Josh/Judg`; это не
  повреждение input lock. Regenerate main reports после следующего разумного
  batch reviewer-книг, а не после каждого shard.

## Исправленный regression-контракт

- В `test_ukrainian_stage_7.py` добавлен отсутствовавший `WORK` для проверки
  ignored author evidence.
- Generated Acts.15.34 test теперь сверяет proven-omitted production token с
  закреплённым UGNT control ID из D05→UGNT crosswalk, а не ошибочно принимает
  внешний D05 locator за production token ID.

## Проверки текущего сеанса

- integrated main generation: PASS;
- main `--check`: PASS;
- integrated `--determinism`: PASS, 46 files / `f874ad0b…`;
- stage-3/4/5/6 `--check`: PASS;
- stage-7 discovery: 189/189 PASS после regression fix;
- полный `scripts/bible_module/tests`: 363/363 PASS;
- `scripts/content_tool/tests`: 30/30 PASS;
- `py_compile`: PASS;
- `git diff --check`: PASS, кроме информационных Windows LF→CRLF warnings;
- `Josh` и `Judg` pass 1/pass 2 independently rechecked: PASS, errors 0.

## Точная следующая последовательность

1. Проверить `git status` и сохранить текущие пользовательские изменения.
2. Запустить два независимых blind reviewer-подагента только для `Ruth` shard
   `008`, с отдельными reviewer IDs и запретом cross-pass/candidate leakage.
3. После завершения независимо выполнить оба `gold_compact check`, обновить
   cumulative counts в roadmap и перейти к `1Sam` shard `009`.
4. Продолжить книги по порядку до `Rev`; не считать заготовленные packets gold
   до фактических двух проходов.
5. После всех 66 книг выполнить deterministic merge каждого pass, сравнение,
   adjudication и finalize gold.
6. Затем запустить streaming evaluator для legacy и новых методов, calibration
   A/B/C, constrained hypergraph, B/C review, overrides, полный accounting и
   отдельный Strong markup с exact 31 102 text/comment round-trip.
7. Не начинать этап 8, не создавать SQLite, не менять Flutter/content tool/DB.

## Короткая команда возобновления

`Продолжи этап 7 строго с текущей точки HANDOFF: scripts/bible_module/reports/ukrainian_stage_7_20260801/HANDOFF.ru.md`
