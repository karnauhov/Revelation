# Этап 7 — текущий HANDOFF, рабочая точка 2026-09-05

> **CURRENT WORK POINT.** Этот файл полностью заменяет предыдущий HANDOFF.
> Этап 7 остаётся в работе. Этап 8 и SQLite не начинались. Удалённый LLM-сервис
> на `COMP_NAZARA` по прямому указанию владельца остаётся остановленным и не
> должен запускаться или опрашиваться. Commit/push автоматически не выполнять.

## Состояние репозитория

- Последний commit владельца: `62e1050` (`Seal stage 7 remote LLM pilot results
  [skip ci]`).
- В начале текущего сеанса worktree был чистым. Текущие незакоммиченные
  изменения относятся только к stage-7 gold workflow, тестам, manifests и
  документации; пользовательские изменения сохранять.
- Полные corpus/review/comparison/adjudication JSONL находятся только в
  gitignored `scripts/bible_module/work/ukrainian_stage_7_20260801/`.

## Неизменяемые входы

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
- production Strong assignments/markers и `resolver_eligible` остаются `0` до
  finalized gold и calibration.

## Текущий результат gold 7.4

1. Все внешние pass-1 результаты `1Sam–Rev` (58 книг) локально
   canonicalized/expanded/checked без исправления смысловых решений догадками:
   1 911 стихов, 39 148 original и 36 248 target-accounting decisions.
2. Вместе с `Gen–Ruth` полный pass 1 объединён и принят workflow:
   2 171 стих, 45 831 original, 41 807 target, 66 reviewer IDs,
   `error_count=0`.
   - merged SHA-256:
     `40a644da0193fc705dd9af9ff5cc63901d2e2e9f3394ac83cc586b21ef37eaee`;
   - validated SHA-256:
     `681dc4fb5265146518aab2dd9b6cd806436a41be655786337e95f18f19becb7b`.
3. Pass 2 и post-blind comparison завершены для `Gen–2Chr` (первые 14 книг):
   459 стихов, 12 220 original и 10 120 target decisions. Новые `2Kgs`, `1Chr`,
   `2Chr` независимо повторно прошли `gold_compact check`, `error_count=0`;
   среди 4 824 stable decisions совпали 3 793, а 1 031 расхождение ожидает
   distinct adjudication.
4. Реализован новый deterministic post-blind
   `ukrainian_stage_7_gold_compare.py`:
   - реальные link/null расхождения отделяются от разной терминологии
     `severity/phenomena`;
   - совпавший alignment сохраняет union phenomena и максимальную severity;
   - adjudication может содержать только exact substantive disagreement set и
     после overlay повторно проходит полное verse-local accounting.
5. Сравнение `1Sam–1Kgs`: 5 274 stable decisions, 2 793 alignment agreements,
   2 481 substantive disagreements, 2 413 metadata-only differences. Все 2 481
   расхождение разрешены distinct third adjudication; повторный validator
   подтвердил exact overlay accounting 5 274/5 274. Независимый QC проверил
   1 128 уникальных строк, включая все critical/high и новые/pass-2 решения:
   `error=0`, `uncertain=0`.
6. Для накопленной очереди `Gen–Lev` distinct third adjudication структурно
   завершена и повторно провалидирована: `Gen` 230/230 и overlay 1 507,
   `Exod` 130/130 и overlay 1 382, `Lev` 216/216 и overlay 1 395.
   Content-QC разделяет их так:
   - `Gen` полностью принят: 230/230, включая 15 high и 4 new,
     `error=0`, `uncertain=0`;
   - `Exod` не принят: QC 130/130 дал 124 accepted / 6 error / 0 uncertain.
     Ошибки — три reciprocal пары в `Exod.27.1`, `32.19`, `32.35`, где
     `той/те` ошибочно связано с noun, а согласованный article `הַ/הָ`
     (HTd/H9009) оставлен null. Нужен отдельный fail-closed consensus-correction:
     `article→той/те`, `noun→noun`, затем полный повторный QC;
   - `Lev` не принят: QC checkpoint `145/216` accepted, `error=0`,
     `uncertain=0`, остаётся exact 71 решений.
7. Остальные сравнения `Num–Ruth` содержат 2 017 substantive disagreements и
   ещё не прошли adjudication.

Versioned доказательства текущей точки:

- `external_gold_pass1_batch_049_066.manifest.json`;
- `external_gold_pass1_batch_009_066.manifest.json`;
- `gold_alignment.pass1.manifest.json`;
- `gold_review_batch_009_011.manifest.json`;
- `gold_adjudication_batch_009_011.manifest.json`;
- `gold_review_batch_012_014.manifest.json`.

## Активная работа на момент записи

Активных agents, OS-команд или remote-LLM процессов нет. Работа остановлена по
просьбе владельца на безопасной границе. Adjudication/QC `1Sam–1Kgs` и `Gen`
приняты; `Exod` и `Lev` явно не приняты.

Полные выходы находятся только в gitignored
`work/.../gold_review_adjudication/<Book>/`, имеют distinct identities и exact
pass/comparison SHA locks. Повторная structural-проверка выполняется командой:

```powershell
python -m scripts.bible_module.ukrainian_stage_7_gold_compare check-adjudication `
  --pass1 <pass1> --pass2 <pass2> --comparison <comparison> `
  --adjudication <completed-adjudication>
```

Точные pause-артефакты:

- `Gen/qc/qc.adjudication.Gen.shard_001.codex-independent-20260905.jsonl`,
  SHA-256 `44d7ab93e80c00fd449a03d96e20ba5267c0218f8940be0efd6d50ecf7725b95`;
- его manifest SHA-256
  `f15febd45ef2ac7fccae4447d1a51f0a18b88e11304e2447c1e59bbd2369d9d7`;
- `Exod/qc/qc.adjudication.Exod.shard_002.codex-independent-20260905.jsonl`,
  SHA-256 `ad2f377aebf8c5510e2cd70dfb1b62210aa90418eef3d050c821ed1a00f39cca`;
- его manifest SHA-256
  `582947981f4fd29d4a4ef3fc456df5337159432d18abab1c8d4d506a7ce523f6`;
- `Lev/qc/qc.checkpoint.adjudication.shard_003.codex-independent-20260905.json`,
  SHA-256 `2c0e98a4dbaf70dbcef57c932731ba84ff8160109fa6f8d11c8b7a88d2ab2fae`;
- его manifest SHA-256
  `fafe80b9c03968253aba51356f66e0d6ee4b9eb1aa105e9d49dff13c60dde8cd`.

## Проверки текущего сеанса

- обязательные stage 3/4/5/6 `--check` — PASS;
- `python -m unittest` для gold/compact/shards/external — PASS, 36 tests;
- `python -m unittest discover -s scripts/bible_module/tests` — PASS,
  395 tests;
- `python -m unittest discover -s scripts/content_tool/tests` — PASS, 30 tests;
- forbidden-pattern and docs-sync checks — PASS;
- current Flutter `3.47.2` / Dart `3.13.2`: `dart format .` attempted to change
  four out-of-scope tests and `flutter analyze` reported 8 pre-existing
  warnings after automatic dependency/config migration; all unintended tracked
  edits were restored. Analyzer remains a final blocker, not a stage-7 code
  regression;
- `flutter test --no-pub` completed the full repository suite: `918` tests
  passed and `2` pre-existing Strong-dictionary widget tests failed because the
  expected preview strings were absent; a focused rerun reproduced `1` pass / `2`
  failures. Stage 7 changed no Flutter source/test/dependency;
- `python -m py_compile` для изменённых gold modules — PASS;
- локальный `gold_compact check` для `1Sam`, `2Sam`, `1Kgs` — PASS;
- локальный `gold_compact check` для `2Kgs`, `1Chr`, `2Chr` — PASS;
- `check-adjudication` для `Gen`, `Exod`, `Lev` — PASS structural; content-QC
  verdicts различаются и перечислены выше;
- полный Flutter-набор повторён, но остаётся красным по двум указанным
  out-of-scope тестам; после стабилизации окружения/исходного Flutter baseline
  он должен быть чисто повторён перед закрытием этапа.

## Точная следующая последовательность

1. Возобновить `Lev` QC строго из checkpoint: проверить только exact 71 remaining
   IDs, затем собрать полный deterministic QC 216/216. До этого `Lev` не
   принимать.
2. По `Exod` сначала прочитать полный QC manifest и реализовать/проверить
   отдельный SHA-locked consensus-correction contract, потому что правильное
   исправление переоткрывает три ранее согласованных article-null решения.
   Distinct correction reviewer должен заменить только exact article/noun/
   demonstrative rows, пройти полный verse-local accounting и новый независимый
   QC. Не ослаблять существующий disagreement-only adjudication молча.
3. После принятия `Exod` и `Lev` создать versioned aggregate adjudication manifest
   для `Gen–Lev` и поставить отдельную выполненную галочку только фактически
   принятым книгам.
4. Продолжить distinct adjudication очереди `Num`, `Josh`, `Judg`, затем `Ruth`;
   каждый shard принимать только после independent content-QC.
5. После освобождения reviewer slots продолжить blind pass 2 с `Ezra` (015),
   `Neh` (016), `Esth` (017), не открывая pass 1/candidates/legacy до окончания.
6. После каждого pass 2 выполнить локальный `gold_compact check`, post-blind
   compare, distinct adjudication и QC. Повторять book batches до `Rev`.
7. После всех 66 книг объединить pass 2, проверить reviewer independence,
   выполнить `ingest-pass2`, global comparison, собрать exact global
   adjudication и только затем `finalize/check-final`.
8. После finalized gold оценить legacy и новые методы, выполнить calibration
   A/B/C, B/C review, overrides и лишь затем Strong markup с exact 31 102
   text/comment round-trip.
9. Не начинать этап 8, не создавать SQLite, не менять Flutter/content tool/DB.

## Remote LLM

Remote pilot остаётся candidate-only и запечатан в
`local_llm_remote_pilot_checkpoint.manifest.json`; разрешающего verdict нет.
Не запускать `Start`, `BenchmarkAll` или `RunWeekQueue`, пока владелец снова
явно не сообщит, что компьютер доступен.

## Короткая команда возобновления

`Продолжи этап 7 строго с текущей точки HANDOFF: scripts/bible_module/reports/ukrainian_stage_7_20260801/HANDOFF.ru.md`
