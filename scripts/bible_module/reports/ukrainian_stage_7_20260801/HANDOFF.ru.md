# Этап 7 — текущий HANDOFF, пауза 2026-08-15

> **CURRENT PAUSE POINT.** Этот файл полностью заменяет предыдущий HANDOFF.
> Этап 7 остаётся в работе. Активных stage-7 Python-процессов и подагентов нет.
> Этап 8 и SQLite не начинались. Commit/push автоматически не выполнять.

## Неизменяемые входы

- edition/module/code: `ohienko_1988` / `ohienko_1988` / `OH1988`;
- canon/versification/mapping: `protestant_66` / `kjv_protestant` /
  `oh1988-kjv-protestant-v1`;
- target positions: `31 102`;
- stage-6 text: `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`;
- stage-6 manifest: `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af`;
- stage-6 comments: `5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4`;
- stage-6 footnote definitions: `4e69616e865d1e048391b6059eb622250570f1562b5a257a7a93c67edef2e5e7`;
- stage-6 footnote uses: `e86d3136a8760833b1910177c323896f02710ff9515391a6e4aae9b6d4798449`;
- stage-6 heading footnotes: `b06c705bf8c7ff5753dd4609cad73441de4cada296d5ccea2aff20ee3e31e92a`;
- rejected legacy snapshot: `d3a6371d2371a48c33fb7b756e0ef4e39f6815701f52bdd6c6eb714c010c6f4b`;
- fingerprint-selected original layer: 678 144 rows / SHA-256 `a2f8b017b702b8217ce4242e2578082f134b615be64968f190c066c0d4692c82`;
- Ukrainian token inventory SHA-256 `62caa29ff269c9ca8dad4b64c656728a645b3d09210034ddcc953c5363c567e1`;
- source registry SHA-256 `b1f7e2bc82929bdd40c5701f4d16ff00387da8645c5279cf311adc12973ffebd`;
- gold-selected original layer SHA-256
  `500482d4b1ce58f9749fe9e53b58bf8bce6be1558df926dacfbe0df29cf09ca4`;
- gold panel SHA-256
  `6f6ce4ce4eb8a941ae8fa4328798873141743889efb386cae15375db3fe0245c`;
- gold workbench SHA-256
  `d5d1aa78368520a152cd869aaa8c729a6008e86f5af359c2d9aac29138d934c2`.

## Завершённые candidate-only каналы

- Statistical OOF: два полных побайтно одинаковых bundle, 163 140 rows,
  JSONL SHA-256 `5be192bcddadec9699befa554654e0184886b38e1aeae8ef0903439ef0d663ad`.
- First-party canonical: 501 518 candidate-only rows, JSONL SHA-256
  `246f3d53af7a6d788cad5707d7fce7e9ccb0d38b2c1f1cd829449c7f3ef9687f`.
- Contextual: два изолированных полных прохода обработали `31 102/31 102`
  стихов, каждый дал 207 367 candidate-only hyperedges и 542 641 strict mutual
  links; 12 стихов без links, `error_count=0`.
- Оба contextual bundle побайтно совпали:
  - JSONL: 786 724 179 bytes / SHA-256
    `0e1e90dd1c2ffa2c907861a5eeba551bed00038015a0823ebc673446198a3881`;
  - registry SHA-256
    `8314af1538c87e3becb49d23a4859e1291ed76437283327b1a66366574283175`;
  - manifest SHA-256
    `9b79010cda937f909128ea753d64d90d6ae5c41f9730af61fb1f217d5a077372`.
- Оба каталога независимо прошли `_validate_contextual_candidate_bundle`.
- Автоматическая приёмка и resolver у всех candidate channels выключены;
  accepted links и Strong markers равны 0 до finalized gold/calibration.

## Авторские печатные сноски OH1988

- Реализован отдельный zero-vote канал
  `scripts/bible_module/ukrainian_stage_7_author_comments.py`, CC0 fixtures,
  tests и интеграция в основной stage-7 generator.
- Все 1 204 определения представлены 1 329 uses: 1 318 verse + 11 heading,
  1 222 target refs; exact comment/use/definition accounting и provenance
  проверяются fail-closed.
- Два gitignored work bundle побайтно совпали. Self-contained JSONL содержит
  exact note text, категории, scan page, stage-6 anchor и same-locus matches:
  2 665 842 bytes / SHA-256
  `0cc59c16c4b61e65ffc260c4401204d26b49a5ec28e90575421ed8f01f09dea3`;
  work manifest SHA-256
  `c7c3ca732a78e1ec2fb5dcc206a79d5f3c82dd7fdde052c78a4a16d46383c36c`.
- Найдены 267 exact original-form matches, 355 unmatched source-form mentions и
  7 textual-variant notes. Для будущего manual review подготовлены 7 high и
  329 medium records.
- `Gen.1.2`: `al pnej/pnei tehom` сопоставлены только с same-locus
  H5921/H6440/H8415; повторяющееся `al-pnei` оставлено many-candidate evidence,
  без позиционного выбора.
- Сноски не меняют `target_comment`, не голосуют автоматически и не доказывают
  украинский span сами по себе.
- Versioned `author_comment_evidence.manifest.json` и 336 manual-review rows ещё
  не выпущены; поэтому отдельный пункт 7.1 в roadmap остаётся открытым до
  integrated main generation.

## Gold state

- Answer-free panel: 2 171 verses, 45 831 original и 41 807 target decisions
  на каждый pass; по 66 exact book-shards.
- Оба независимых blind passes завершены только для `Gen–Deut`: 163 verses,
  3 987 original и 3 355 target decisions на pass. Disagreements сохранены.
- Остальные 61 книга не размечены; следующая — `Josh`.
- Finalized gold, adjudication, calibration, accepted links и markup отсутствуют.
- Primary agent не должен имитировать независимый blind review, имея доступ ко
  всему repo/candidates; следующие passes требуют отдельно разрешённых
  независимых reviewer agents.

## Проверки текущего сеанса

- author-comment focused tests: 8/8 PASS;
- combined pure stage-7 contracts: 95/95 PASS;
- selected gold/alignment/author tests: 24/24 PASS;
- artifact-inventory regression: 1/1 PASS;
- `py_compile`: PASS;
- оба full contextual bundle: fail-closed validation PASS и exact file-set/SHA
  equality PASS;
- `git diff --check`: PASS, кроме информационных Windows LF→CRLF warnings в
  двух русских документах;
- полные author/contextual/statistical corpora остаются gitignored.

## Точная следующая последовательность

1. Проверить `git status` и сохранить пользовательские изменения.
2. Запустить sequential integrated main generation на уже проверенных
   first-party/statistical/contextual bundle; не перезапускать дорогой inference.
3. Выполнить основной `--check`; проверить versioned author manifest, 336 новых
   manual-review rows и общий candidate/report inventory.
4. После успешного report manifest отметить отдельный checkbox анализа сносок
   7.1 и актуализировать report/validation log.
5. Выполнить integrated determinism и обязательные stage-3/4/5/6 checks.
6. Продолжить оба blind gold passes с book-shard `Josh`, затем остальные книги,
   merge/adjudication/finalize gold.
7. Только после finalized gold выполнить streaming evaluation, calibration
   A/B/C, constrained hypergraph, B/C review, overrides, полный accounting и
   отдельный Strong markup с exact 31 102 text/comment round-trip.
8. Не начинать этап 8, не создавать SQLite, не менять Flutter/content tool/DB.

## Незакоммиченный scope

Ожидаются два русских документа этапа 7, новый report-каталог, stage-7 Python
modules, tests и CC0 fixtures. Полные corpora/candidates/gold packets находятся
только в gitignored `scripts/bible_module/work/`. Пользовательские изменения не
удалять. Перед коммитом проверить полный `git status`; commit/push выполняет
только владелец.

## Короткая команда возобновления

`Продолжи этап 7 строго с текущей точки HANDOFF: scripts/bible_module/reports/ukrainian_stage_7_20260801/HANDOFF.ru.md`
