# Удалённый LLM-узел этапа 7: простая инструкция оператора

Doc-Version: `1.0.0`
Last-Updated: `2026-08-22`
Source-Commit: `working-tree`

## Что уже установлено

На компьютере Назара `COMP_NAZARA` установлен управляемый LLM-узел:

- адрес компьютера в домашней сети: `192.168.1.188`;
- OpenSSH слушает порт `22` и запускается вместе с Windows;
- LLM API использует порт `8080`, но только когда модель явно запущена;
- runtime, модели и удалённые журналы находятся в
  `D:\RevelationStage7LLM`;
- задания, ответы, manifests и прогресс находятся на ноутбуке владельца в
  `C:\Users\karna\Projects\Revelation\scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm`.

OpenSSH нужен только для управления. Сама LLM не имеет автозапуска: после
включения или перезагрузки компьютера задача `RevelationStage7LlamaServer`
остаётся в состоянии `Ready`, а модель не занимает VRAM/RAM. Брандмауэр допускает
SSH и LLM API только с ноутбука `192.168.1.251`.

Никакие задания и ответы не нужно переносить флешкой. Python-harness работает на
ноутбуке, посылает один verse-запрос по домашней сети и немедленно сохраняет
полученный ответ на ноутбуке. На компьютере Назара остаются только runtime,
GGUF-модели и технические логи `llama-server`.

## Где выполнять команды

Если явно не сказано обратное, все команды ниже выполняются **на ноутбуке
владельца**, в обычном PowerShell:

```powershell
Set-Location -LiteralPath C:\Users\karna\Projects\Revelation
```

Оба компьютера должны быть включены и находиться в одной домашней сети. Для
вычислительных запусков желательно подключить их к питанию и временно не запускать
игры на RTX 4070 SUPER.

## Безопасные проверки во время игры

Эти команды не загружают модель и почти не используют ресурсы компьютера Назара.

Проверить SSH-доступ:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action TestSsh
```

Нормальный ответ: `COMP_NAZARA`.

Проверить состояние LLM:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action Status
```

Безопасное остановленное состояние:

```text
status = stopped
scheduled_task_state = Ready
active_model_id = null
served_model_id = null
```

Проверить порты отдельно:

```powershell
Test-NetConnection 192.168.1.188 -Port 22
Test-NetConnection 192.168.1.188 -Port 8080
```

Порт `22` должен отвечать. Порт `8080` должен быть закрыт, пока LLM остановлена.

Показать зарегистрированные модели без их запуска:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action ListModels
```

## Модели и их роль

| Model ID | Что проверяем | Статус до пилота |
| --- | --- | --- |
| `qwen35_9b_q8_reasoning1024` | более точная 9B-квантизация, multilingual reasoning | основной кандидат |
| `ministral3_14b_reasoning_q4km` | независимая архитектура и более крупная reasoning-модель | независимый кандидат |
| `qwen35_27b_iq2xxs_reasoning1024` | более крупная модель с очень сильной квантизацией | экспериментальный контроль |

Ни одна модель заранее не считается пригодным gold-reviewer. Qwen 9B Q4 на CPU
дал `0 / 17` exact решений тестового стиха, а Ministral 8B Instruct Q4 после
безопасного исправления формальной JSON-оболочки дал `6 / 17` (`35,294%`). Оба
CPU-варианта отклонены для gold и остаются только candidate-only baselines.

## Полная последовательность работы

### Шаг 1. Дождаться свободного компьютера Назара

До запуска убедиться, что сын закончил играть. Проверить остановленное состояние:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action Status
```

### Шаг 2. Сравнить три GPU-модели

Запустить одну команду:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action BenchmarkAll
```

Контроллер последовательно:

1. запускает первую модель;
2. ждёт готовности API;
3. выполняет sealed benchmark на трёх заранее закреплённых стихах Ruth;
4. сохраняет запросы, ответы и метрики на ноутбуке;
5. останавливает модель;
6. повторяет то же для двух остальных моделей.

Одновременно работает только одна модель. Даже при ошибке конкретной модели
контроллер пытается остановить её и сохраняет уже полученные ответы.

Результат появляется на ноутбуке:

```text
scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm\remote_benchmarks\<UTC timestamp>\
```

Внутри каждой model-папки находятся:

- `benchmark.manifest.json` — итоговые метрики и SHA-256;
- `accepted_answers.jsonl` — принятые валидатором решения;
- `comparison.jsonl` — сравнение с sealed reference;
- `responses\` — полные ответы и usage/timing каждого запроса.

После завершения обязательно проверить, что модель остановлена:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action Status
```

### Шаг 3. Передать короткую команду Codex для приёмки пилота

Ничего не редактировать в benchmark-файлах. В следующем сеансе написать:

```text
Проверь последний remote GPU pilot в scripts/bible_module/work/ukrainian_stage_7_20260801/local_llm/remote_benchmarks, сравни три модели fail-closed и подготовь remote_pilot_verdict.json для допустимой модели.
```

Codex проверит schema, exact accounting, agreement, position signal, reasoning,
детерминизм и ошибки. Если ни одна модель не проходит — массовая очередь не
запускается. Пользователь не должен создавать или исправлять
`remote_pilot_verdict.json` вручную.

### Шаг 4. После разрешающего verdict запустить недельную очередь

Codex сообщит точный принятый `ModelId`. Пример для Qwen:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action RunWeekQueue -ModelId qwen35_9b_q8_reasoning1024
```

`RunWeekQueue` сначала выполняет более строгий полный пилот: два независимых
запуска всех 32 выбранных стихов Ruth. Production остаётся заблокированным, пока
автоматическая проверка не подтвердит одновременно:

- 100% валидный schema/exact original и target accounting;
- ноль invalid/dangling/cross-verse ID;
- 100% совпадение link/null semantics между двумя запусками;
- не менее 80% exact agreement с независимым Ruth reference;
- полный critical recall;
- отсутствие запрещённого position-collapse signal.

Только после этих ворот скрипт продолжает 28 подготовленных OT book-задач
`2Kgs–Mal`:

- 30 запусков вместе с двумя Ruth-пилотами;
- 1 018 verse-runs;
- 954 уникальных production-стиха;
- 21 779 original-token решений;
- 19 453 target-accounting решений.

Это blind pass 2/candidate work, а не final gold и не production Strong markup.
Каждая книга всё равно потребует независимого второго evidence-канала и
adjudication.

### Шаг 5. Смотреть прогресс с ноутбука

Основной PowerShell оставить работающим. Во втором окне PowerShell выполнить:

```powershell
Set-Location -LiteralPath C:\Users\karna\Projects\Revelation
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/show_stage7_local_progress.ps1
```

Сводка показывает число готовых книг, запусков и стихов, процент выполнения,
среднее время на стих и оценку оставшегося времени. Основные файлы прогресса:

```text
scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm\STATUS.ru.md
scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm\progress.json
scripts\bible_module\work\ukrainian_stage_7_20260801\local_llm\queue_manifest.json
```

После каждого принятого стиха также обновляется:

```text
local_llm\tasks\<task>\completed\<run_id>\STATUS.ru.md
local_llm\tasks\<task>\completed\<run_id>\progress.json
local_llm\tasks\<task>\completed\<run_id>\decisions\
local_llm\tasks\<task>\completed\<run_id>\responses\
```

Поэтому все результаты сразу доступны Codex на ноутбуке в следующем сеансе.
Копировать что-либо с компьютера Назара не требуется.

### Шаг 6. Пауза и продолжение

Для нормальной паузы нажать `Ctrl+C` в окне `RunWeekQueue`. Контроллер должен
выполнить `finally` и остановить удалённую модель. Затем проверить `Status`.

Если основное окно аварийно закрылось или сеть оборвалась, выполнить отдельно:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action Stop
```

Для продолжения повторить ту же команду `RunWeekQueue` с тем же принятым
`ModelId`. Валидные завершённые verse-решения проверяются и пропускаются; работа
продолжается со следующего незавершённого стиха.

### Шаг 7. Завершение недельной работы

Когда `STATUS.ru.md` показывает `1 018 / 1 018` verse-runs:

1. выполнить `Status` и убедиться в `stopped`;
2. не редактировать ответы вручную;
3. не переносить их в Git;
4. в следующем сеансе написать:

```text
Проверь завершённую remote LLM week queue в scripts/bible_module/work/ukrainian_stage_7_20260801/local_llm, выполни fail-closed импорт, сравнение и обнови этап 7.
```

## Ручные управляющие команды

Обычно `BenchmarkAll` и `RunWeekQueue` сами запускают и останавливают модели.
Команды ниже нужны только для диагностики.

Запустить конкретную модель:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action Start -ModelId qwen35_9b_q8_reasoning1024
```

Проверить API запущенной модели:

```powershell
Invoke-RestMethod http://192.168.1.188:8080/health
Invoke-RestMethod http://192.168.1.188:8080/v1/models
```

Остановить модель:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action Stop
```

Повторно проверить/докачать зарегистрированные модели без их запуска:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bible_module/manage_stage7_remote_llm.ps1 -Action InstallModels -ModelId all
```

`InstallModels` проверяет SHA-256 всех файлов и может заметно использовать сеть,
диск и CPU; без необходимости во время игры её не запускать.

## Что делать при ошибке

- `TestSsh` не отвечает: проверить, что компьютер включён, не спит и имеет адрес
  `192.168.1.188`.
- `Status` показывает `starting`: подождать до пяти минут и проверить снова.
- `RunWeekQueue` сообщает об отсутствии `remote_pilot_verdict.json`: это
  нормальная защита; сначала нужен шаг 2 и приёмка Codex.
- `pilot_verdict.json` сообщает failure: production не запускать; ответы пилота
  сохранены для анализа.
- API завис, но SSH отвечает: выполнить `Stop`, затем `Status`.
- Для удалённых runtime-логов использовать
  `D:\RevelationStage7LLM\logs`; task inputs и ответы искать только на ноутбуке.
- Если DHCP изменил адрес `192.168.1.188`, не ослаблять firewall и не менять
  registry догадкой: вернуть закреплённый адрес или обновить контракт отдельным
  проверенным изменением.

## Запреты

- Не запускать `BenchmarkAll`, `Start` или `RunWeekQueue` во время игры.
- Не открывать порты `22`/`8080` в Интернет и не менять `0.0.0.0`/firewall.
- Не копировать pass 1, candidates, legacy или completed gold в answer-free task.
- Не исправлять содержательные links/nulls модели догадками.
- Не считать локальную LLM источником Strong или final gold без всех ворот.
- Этот workflow не создаёт SQLite, не изменяет Flutter/content tool/DB и не
  начинает этап 8.
