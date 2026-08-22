# Локальная языковая модель для этапа 7: установка и проверочный пилот

Doc-Version: `1.0.0`
Last-Updated: `2026-08-22`
Source-Commit: `working-tree`

> **Текущий operational workflow:** CPU-пилоты на ноутбуке не прошли gold-порог
> и не должны запускать недельную очередь. Удалённый RTX 4070 SUPER узел
> установлен, но его sealed GPU-пилот ещё не выполнен. Все пользовательские
> команды, порядок запуска и пути результатов приведены в отдельной
> [инструкции оператора](ukrainian-bible-strongs-stage-7-remote-llm-operator-guide.ru.md).

## Цель и граница доверия

Локальная модель может бесплатно по subscription-токенам выполнять слепой
review, готовить candidate evidence и сортировать ручные случаи. Она не получает
особого доверия только потому, что работает на компьютере владельца. До
сравнения с замороженным gold её результат не является gold, production link,
Strong-разметкой или override.

Главная задача остаётся прежней: связать конкретный еврейский/греческий original
token с конкретным украинским token/span. Локальной модели запрещено подбирать
Strong по похожему переводу, позиции, соседству, частоте или verse bag.

## Фактические ресурсы этого компьютера

Профиль проверен 22 августа 2026 года:

- ASUS Vivobook X1504ZA/F1504ZA;
- Intel Core i7-1255U, 10 ядер / 12 логических процессоров;
- 15,7 ГиБ RAM;
- NVIDIA GPU и `nvidia-smi` отсутствуют;
- на диске `C:` свободно около 318,6 ГиБ.

Поэтому практический предел — 8–9B модель в 4-битном GGUF на CPU. 27B/35B и
полноточные 8–9B модели для этого ноутбука не подходят. Ожидается медленная
генерация: пилот нужно запускать малыми verse-пакетами, при необходимости на
ночь, а не сразу на целой книге.

## Выбранная основная модель

Основной пилот: [Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B),
квантованный файл
[Unsloth Qwen3.5-9B GGUF Q4_K_M](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF).

Причины выбора:

- upstream и GGUF опубликованы под `Apache-2.0`;
- официальный [обзор Qwen3.5](https://qwen.ai/blog?id=qwen3.5) явно перечисляет
  украинский, греческий и иврит среди более чем 200 языков;
- `Q4_K_M` занимает около 5,68 ГБ и помещается в имеющуюся RAM вместе с
  ограниченным context/KV cache;
- модель поддерживается `llama.cpp` и имеет структурированный chat/JSON режим.

Контрольная модель после основного пилота:
[Ministral-3-8B-Instruct-2512-GGUF](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-GGUF),
также `Apache-2.0`. Она рассчитана на edge-устройства и имеет официальный GGUF,
но в опубликованном списке языков не заявлены одновременно украинский,
древнегреческий и библейский иврит. Поэтому она не заменяет Qwen, а проверяет,
не является ли результат зависимым от одной архитектуры.

Рейтинг Trending на Hugging Face использован только для поиска кандидатов, а не
как доказательство качества. Не использовать «abliterated», «uncensored»,
неофициальные merge и модели без точной upstream/quantization provenance.

## Специализированные модели

Их можно отдельно испытать только как candidate-каналы:

| Модель | Лицензия | Допустимая роль | Ограничение |
| --- | --- | --- | --- |
| [UGARIT/grc-alignment](https://huggingface.co/UGARIT/grc-alignment) | CC BY 4.0 | независимый NT word-alignment candidate | опубликованный AER для Greek→English около 19,73%; украинский не проверен, gold не заменяет |
| [open-greek/dragoman](https://huggingface.co/open-greek/dragoman) | CC BY 4.0 | дополнительный Greek alignment candidate | обучался в том числе на NT/OpenGNT; зависимость и overlap нужно учитывать, Ukrainian отсутствует |
| [Helsinki-NLP/opus-mt-he-uk](https://huggingface.co/Helsinki-NLP/opus-mt-he-uk) | Apache-2.0 | OT translation/candidate feature | современный Hebrew→Ukrainian MT, не библейско-еврейский token ground truth |
| [MiqraBERT](https://huggingface.co/davidmsmiley/MiqraBERT) | Apache-2.0 | поиск параллельных мест и negative/context evidence | verse similarity, а не word alignment |

Не использовать в этом запуске `CC BY-NC-SA` interlinear-модели, CC BY-SA
corpora и модели с неясной/custom лицензией. Gemma требует отдельного решения по
собственным terms и поэтому не выбрана для первого пилота.

## Простая установка на Windows

Установка выполняется вне репозитория и не меняет Flutter, content tool, DB или
SQLite.

1. Открыть обычный PowerShell.
2. Установить официальный runtime:

   ```powershell
   winget install llama.cpp
   ```

3. Закрыть и снова открыть PowerShell, проверить:

   ```powershell
   llama-server --version
   ```

4. Запустить локальный сервер. При первом запуске GGUF будет скачан с Hugging
   Face; это примерно 5,68 ГБ:

   ```powershell
   llama-server -hf unsloth/Qwen3.5-9B-GGUF:Q4_K_M --host 127.0.0.1 --port 8080 -t 10 -c 32768 -np 1 -dev none -ngl 0 --no-op-offload -mmdev none -rea off --reasoning-budget 0
   ```

5. Не закрывать это окно. В браузере открыть `http://127.0.0.1:8080` и выполнить
   короткую проверку на украинском. Сервер доступен только локально благодаря
   `127.0.0.1`.
6. Путь cache и SHA-256 фактически загруженного `.gguf` записать из startup log.
   Не переносить модель в Git; хранить её вне репозитория или в gitignored
   `scripts/bible_module/work/ukrainian_stage_7_20260801/local_llm/`.

Если 32K context не помещается в RAM, не уменьшать его так, чтобы обрезался
verse packet. Сначала остановить сервер, закрыть лишние программы и повторить.
Если проблема остаётся, пакет нужно дополнительно уменьшить; скрытая truncation
запрещена.

## Фактические локальные пути этого компьютера

Установка и загрузка уже выполнены. Полный список путей:

- runtime `llama-server.exe`:
  `C:\Users\karna\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe`;
- snapshot модели:
  `C:\Users\karna\.cache\huggingface\hub\models--unsloth--Qwen3.5-9B-GGUF\snapshots\3885219b6810b007914f3a7950a8d1b469d598a5\`;
- основной GGUF, 5 680 522 464 байта:
  `Qwen3.5-9B-Q4_K_M.gguf`, SHA-256
  `03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8`;
- projector, 921 705 024 байта: `mmproj-BF16.gguf`, SHA-256
  `853698ce7aa6c7ba732478bad280240969ddf7b0fcbf93900046f63903a83383`;
- реальные blob-файлы лежат в
  `C:\Users\karna\.cache\huggingface\hub\models--unsloth--Qwen3.5-9B-GGUF\blobs\`;
  файлы snapshot являются локальными символическими ссылками на эти blobs;
- versioned Python-harness:
  `scripts\bible_module\ukrainian_stage_7_local_llm.py`;
- пакетный оркестратор:
  `scripts\bible_module\ukrainian_stage_7_local_llm_batch.py`;
- sealed benchmark:
  `scripts\bible_module\ukrainian_stage_7_local_llm_benchmark.py`;
- единственный пользовательский запуск:
  `scripts\bible_module\run_stage7_local_llm.ps1`;
- отдельный просмотр прогресса:
  `scripts\bible_module\show_stage7_local_progress.ps1`;
- корень answer-free заданий, полных prompts и ответов:
  `scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm\`;
- подготовленные задания по книгам:
  `scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm\tasks\`;
- тестовые ответы разных моделей/параметров:
  `scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm\benchmarks\`;
- журнал скрытого локального сервера:
  `scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm\logs\`;
- общий план: `queue_manifest.json`; текущая машинная сводка: `progress.json`;
  удобная человеку сводка: `STATUS.ru.md`; решение пилотных ворот:
  `pilot_verdict.json`.

Модель, её cache, полные prompts и ответы находятся вне Git либо в gitignored `work/`.
Никакие SQLite-файлы, Flutter runtime или БД этим процессом не создаются и не изменяются.

## Как владелец будет выполнять подготовленное задание

Заранее подготовлена одна возобновляемая очередь: два sealed-запуска `Ruth`, затем 28
OT-книг `2Kgs–Mal`. Это 30 запусков, 1 018 стихов-запусков, 954 уникальных production
стиха, 21 779 original и 19 453 target decisions. Полные задания находятся в
`scripts/bible_module/work/ukrainian_stage_7_20260801/local_llm/tasks/`.

Порядок владельца:

1. Подключить ноутбук к питанию. Закрывать IDE или браузер необязательно, но это может
   немного замедлить CPU-инференс.
2. Открыть PowerShell в корне проекта.
3. Выполнить одну команду:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/bible_module/run_stage7_local_llm.ps1
   ```

   Скрипт сам проверяет SHA модели, поднимает скрытый CPU-only `llama-server`, сначала
   выполняет двухзапусковый sealed pilot, сравнивает его с закрытым reference и только
   после успешных ворот переходит к книгам. При нормальном завершении он сам выключает
   запущенный им сервер. Пока скрипт работает, он не даёт Windows автоматически усыпить
   компьютер, но экран может выключаться; закрытие крышки действует по системным
   настройкам ноутбука.
4. Окно PowerShell можно оставить работать на ночь. Если компьютер был выключен или
   процесс остановился, повторить ту же команду: уже принятые стихи валидируются и
   пропускаются, работа продолжается со следующего.
5. Ответы вручную не исправлять. Невалидный стих автоматически повторяется до трёх раз;
   после этого пакет останавливается с `failure.json`, сохраняя все готовые решения.

Параметры нужны только для подготовки/добавления диапазона книг. На этом компьютере уже
подготовлен весь допустимый OT-диапазон `12..39`, поэтому обычно параметры не нужны:

```powershell
# Эквивалентный явный запуск полной подготовленной очереди
powershell -ExecutionPolicy Bypass -File scripts/bible_module/run_stage7_local_llm.ps1 -FromOrdinal 12 -ToOrdinal 39
```

NT в этот запуск не добавляется: для него сначала потребуется отдельный Greek sealed
pilot. Значения вне `12..39` скрипт отвергает.

## Как смотреть прогресс

В другом PowerShell можно в любой момент выполнить:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/bible_module/show_stage7_local_progress.ps1
```

Либо использовать основной скрипт без запуска модели:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/bible_module/run_stage7_local_llm.ps1 -StatusOnly
```

Сводка показывает:

- книг готово / всего;
- запусков готово / всего;
- стихов-запусков готово / всего и процент;
- текущую книгу/запуск;
- среднее время на принятый стих и расчёт оставшихся часов;
- `complete`, `running`, `not_started` или `failed_resumable` для каждой строки.

После каждого принятого стиха обновляются как общий
`local_llm/STATUS.ru.md`, так и локальный
`tasks/<task>/completed/<run_id>/STATUS.ru.md`. Поэтому состояние видно даже во время
многодневного запуска.

До появления таких сгенерированных пакетов не вставлять полный book-shard в
Web UI вручную: на 16 ГиБ RAM слишком легко получить незаметную truncation.

## Замороженный пилот качества

Пилот выполняется до массовой работы и не настраивается после просмотра его
ответов:

1. `OT-Hebrew`: небольшая стратифицированная answer-free выборка из уже дважды
   независимо проверенных `Gen–Ruth`.
2. `NT-Greek`: отдельная выборка после появления независимых pass 1/pass 2 для
   NT.
3. Для каждой выборки — два запуска с одинаковыми `model digest`, prompt,
   `temperature=0`, seed, context и output limit.
4. Reference labels остаются sealed до завершения обоих запусков.
5. Сравниваются exact hyperedge/link/null semantics, а не похожесть rationale.

Минимальные ворота для роли blind reviewer:

- 100% schema и exact original/target accounting;
- invalid/dangling/cross-verse ID = 0;
- одинаковые link/null decisions в двух локальных запусках = 100%;
- overall exact agreement с независимо проверенным reference не ниже 80% и не
  хуже установленной внутренней baseline более чем на 3 процентных пункта;
- все reference `critical` найдены/совпали; все local/reference critical/high
  всё равно уходят в независимую ручную проверку;
- same-local-index signal ниже 50%, при этом сама позиция никогда не является
  evidence;
- отдельные метрики OT/NT, книги, omission/addition, reorder, merge/split,
  named entity, particle, compound и multiple Strong.

Если ворота не пройдены, модель всё ещё можно использовать для candidate-only
подсказок или сортировки B/C, но не как один из двух gold-проходов. Если пройдены,
каждая следующая книга всё равно проходит второй независимый reviewer и
adjudication; массовая автоматическая приёмка запрещена.

## Что фиксировать для каждого запуска

- точный Hugging Face repository и commit;
- upstream model commit, license URL и GGUF filename;
- SHA-256 файла модели и `llama.cpp --version`;
- hardware/OS, threads, context, seed, temperature, sampling и output limit;
- SHA-256 system prompt, request, input и output;
- processed/skipped/error/truncated counts;
- wall time, tokens/second и peak memory, если runtime их сообщает;
- запрет доступа к pass другого reviewer, candidates, legacy и готовому gold;
- deterministic comparison и итоговый verdict `gold-review-capable` либо
  `candidate-only`.

Полные prompts и ответы остаются в gitignored `work/`. В Git сохраняются только
код harness, CC0 fixtures, безопасный manifest с digest/метриками и этот документ.

## Связь с этапом 7

- 7.0: зарегистрировать модель/runtime/лицензию только после фактической загрузки.
- 7.4: локальная модель может стать независимым blind reviewer только после
  успешного sealed pilot.
- 7.5: специализированные модели и не прошедшая gold-порог LLM допустимы как
  раздельные zero-vote/candidate-only generators.
- 7.7: никакой local candidate не получает `A_auto` без общей lower-bound
  precision ≥ 99,5% на замороженном gold.
- 7.8: модель может сортировать B/C и формировать rationale, но override принимает
  независимый reviewer с current-digest gate.
- 7.9: локальная модель не формирует production markup напрямую.
