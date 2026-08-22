# Этап 7 — текущий HANDOFF, пауза 2026-08-22 после remote LLM pilot

> **CURRENT PAUSE POINT.** Этот файл полностью заменяет предыдущий HANDOFF.
> Этап 7 остаётся в работе. Активных stage-7 Python-процессов, локальных или
> удалённых LLM и работающих подагентов нет. Этап 8 и SQLite не начинались.
> Commit/push автоматически не выполнять.

## Состояние репозитория

- Последний коммит владельца: `ace68d4` (`Add stage 7 external gold and local
  LLM workflows [skip ci]`).
- После него изменены только remote/local LLM controller/harness/tests и
  документация/checkpoint текущего пилота. Production candidates, gold labels,
  Strong links, markup, stage-6 text/comment и mapping не менялись.
- Полные ответы моделей находятся только в gitignored
  `scripts/bible_module/work/ukrainian_stage_7_20260801/local_llm/`.
- Пользовательские изменения не удалять; commit/push выполняет только владелец.

## Неизменяемые входы и основной stage-7 контракт

- edition/module/code: `ohienko_1988` / `ohienko_1988` / `OH1988`;
- canon/versification/mapping: `protestant_66` / `kjv_protestant` /
  `oh1988-kjv-protestant-v1`;
- target positions: `31 102`;
- stage-6 text SHA-256:
  `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`;
- stage-6 manifest SHA-256:
  `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af`;
- stage-6 comments SHA-256:
  `5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4`;
- production assignment/Strong markers остаются `0` до finalized gold и
  calibration; `resolver_eligible=0`.

## Основной прогресс этапа 7

- Source/license registry, исторический и 53-locus textual fingerprint,
  токенизация 31 102 текстов, original-token universe, RUSSYN/YLT bridges,
  author-comment evidence и candidate generators уже реализованы.
- Общий regenerated bundle: 872 025 candidate-only rows; оба statistical OOF и
  оба contextual прогона детерминированы. Aggregate integrated SHA-256:
  `f874ad0bc1227220db0307e45e4f020188cc2c1a5efc0a095deff2adc6648aae`.
- Gold panel: 2 171 стих, 45 831 original и 41 807 target-accounting requests на
  каждый pass. Оба blind passes завершены для `Gen–Ruth`.
- Внешний pass 1 для 40 книг `1Sam–Gal` локально нормализован, развёрнут и
  принят только как merge-ready submission: 1 380 стихов, 29 962 original и
  27 192 target-accounting решений. Aggregate SHA-256:
  `a59ea192278f15feebcb8e9b9f02c0d67dbd7242e45dbdf91e1ee2f27c95ac2b`.
  Для этих книг всё ещё обязательны независимый blind pass 2 и adjudication.
- Оставшиеся внешние pass-1 пакеты: ordinals 49–66. Их наличие не заменяет
  pass 2, локальный audit или finalize gold.
- Основные пункты 7.4, 7.6–7.9 и критерий выхода этапа остаются открытыми.

## Remote LLM pilot 2026-08-22

Узел: `COMP_NAZARA`, `192.168.1.188`, RTX 4070 SUPER 12 282 MiB, pinned
`llama.cpp b10545 (a30273376)`. Все модели и runtime находятся на
`D:\RevelationStage7LLM`; LLM не имеет автозапуска. Sealed sample:
`Ruth.4.18,Ruth.3.5,Ruth.4.8`, одинаковые prompt/reference, seed 7,
temperature 0 и exact evaluator.

1. `qwen35_9b_q8_reasoning1024` завершил все 3 стиха:
   - exact link/null agreement `12 / 67` = `17,910%`;
   - по стихам: `7/17`, `5/24`, `0/26`;
   - same-local-index ratio `2/3` = `66,667%`;
   - 5 responses, 19 161 prompt tokens, 14 533 completion tokens,
     generation wall time 348,242 s;
   - провалены ворота agreement `>=80%` и position signal `<50%`;
   - manifest SHA-256
     `02328e6ff18643d347e51d5664c71d37e501ca8f7fc60b772842e1d27ad43771`;
     accepted answers SHA-256
     `6753edafcd04b861293d7229d6861341cd7ab0e7e7144aa209d5f4e7e0188e1f`.
2. `ministral3_14b_reasoning_q4km` трижды ответил на `Ruth.4.18`, но каждый
   ответ повторно использовал target local index в нескольких группах. Exact
   accounting нарушен, догадочная коррекция запрещена; 0 принятых стихов.
3. `qwen35_27b_iq2xxs_reasoning1024` в каждой из трёх повторных попыток
   исчерпал контекст, зациклился на рассуждении и не завершил JSON; 0 принятых
   стихов. Первый технический прогон отдельно сохранён, затем исправлена потеря
   последнего непустого retry-контекста и выполнен чистый повтор, подтвердивший
   модельный fail.

Итог: все три модели `candidate-only`. Разрешающий gitignored
`remote_pilot_verdict.json` не создан, `RunWeekQueue` остаётся заблокирован,
полные Ruth-проходы и недельная очередь не запускались. Safe checkpoint:
`scripts/bible_module/reports/ukrainian_stage_7_20260801/local_llm_remote_pilot_checkpoint.manifest.json`.

Полные gitignored пути результатов:

- `work/.../local_llm/remote_benchmarks/20260822T121634Z/` — основная матрица;
- `work/.../local_llm/remote_benchmarks/20260822T125710Z_qwen27_retry_fix1/` —
  Qwen 27B после исправления retry harness.

## Исправления, сделанные во время пилота

- PowerShell 5.1-compatible `SetThreadExecutionState` теперь получает явные
  `[uint32]2147483649` / `[uint32]2147483648`, а не отрицательно
  интерпретируемые hex literals.
- Startup health timeout увеличен с 5 до 15 минут, потому что SHA-256 больших
  GGUF и загрузка на этом узле штатно занимают более пяти минут.
- Benchmark retry сохраняет последний непустой completion, если следующий
  truncated ответ содержит только reasoning и пустой text body.
- Добавлены regression tests и versioned safe checkpoint; quality gates,
  evaluator и sealed reference не ослаблялись.

## Состояние компьютера сына на паузе

Последняя двойная проверка после `Stop`:

- `status=stopped`;
- `scheduled_task_state=Ready`;
- `served_model_id=null`;
- GPU memory used: 1 221 MiB, utilization 3%;
- updated at UTC: `2026-08-22T13:01:42.3732757Z`.

Не запускать `Start`, `BenchmarkAll` или `RunWeekQueue`, пока владелец снова
явно не подтвердит, что компьютер свободен.

## Проверки текущего изменения

- До remote pilot полный репозиторный набор прошёл: `bible_module` 390/390,
  `content_tool` 30/30, `flutter analyze`, 920 Flutter tests, docs sync,
  forbidden patterns, secret/binary audit и `git diff --check`.
- После retry regression fix targeted local/remote LLM tests прошли 21/21.
- После добавления checkpoint необходимо при возобновлении сначала повторить
  targeted tests и `git diff --check`; удалённый узел для этого не нужен.

## Точная следующая последовательность

1. Проверить `git status`, сохранить пользовательские изменения и прочитать
   safe checkpoint вместе с gitignored response summaries.
2. Не перезапускать три уже отклонённые конфигурации. Локально перепроверить
   checkpoint schema/hashes, targeted tests и документацию; при необходимости
   выпустить отдельный versioned v2 pilot только для действительно нового
   model/parameter contract и только когда владелец освободит GPU-узел.
3. Не создавать `remote_pilot_verdict.json` для текущих результатов и не
   запускать недельную очередь.
4. Вернуться к основному gold 7.4: выполнить независимые blind pass 2 для
   `1Sam–Gal`, импортировать оставшиеся внешние pass 1 ordinals 49–66 после их
   появления, затем comparison/adjudication/finalize без cross-pass leakage.
5. После finalized gold выполнить evaluator legacy/new methods, calibration
   A/B/C, constrained hypergraph, B/C review, overrides и только затем Strong
   markup с exact 31 102 text/comment round-trip.
6. Не начинать этап 8, не создавать SQLite и не менять Flutter/content tool/DB.

## Короткая команда возобновления

`Продолжи этап 7 строго с текущей точки HANDOFF: scripts/bible_module/reports/ukrainian_stage_7_20260801/HANDOFF.ru.md`
