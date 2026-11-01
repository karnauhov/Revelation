# Обмен локальных сборщиков

Doc-Version: 2.2.1
Last-Updated: 2026-11-01
Source-Commit: working-tree

Git `main` хранит инструменты, профили и [перечень проектов](../../../scripts/local_release/projects.json).
Draft GitHub Releases передают задания, пакеты, результаты и очищенные логи. Секреты и бинарники в Git не попадают.
Регистрация другого проекта и его автобилд выполняются в задаче этого проекта; сейчас включён Revelation.

## Удаление и отсутствие повторного импорта

После обязательного UI confirmation один request сохраняется в `.local-releases/deletions/<project>/<SHA>.json`
и проверенно передаётся в Git notes `refs/notes/ai11-local-retention`. Request содержит project/repository,
version/build/SHA, release ID/tag и OS-роли без путей, команд или секретов. В notes также сохраняются
подтверждения постоянных архивных ОС; Linux ack не требуется. Main, index и изменения владельца не затрагиваются.

До удаления проверяются tag SHA/release ID. Активный процесс останавливается и возвращает owner data.
Рекурсивная очистка ограничена exact managed paths; чужие SHA/snapshots и recovery journals защищены.
Linux получает notes до jobs. Постоянная метка запрещает prepare/run, queue retry, handoff/publication,
receive/archive удалённого SHA. Сетевой отказ сохраняет recoverable state; повтор использует тот же request ID.
Удаляется GitHub Release, исходный Git-тег остаётся. Linux не хранит архив, поэтому его следующий login не задерживает
завершение удаления в Windows/GitHub. Legacy control draft принимается только с marker и доверенным uploader,
мигрирует в проверенные notes и удаляется. Новый постоянный технический Release для меток не создаётся.

## Время этапов

Result schema1 допускает stage `duration_seconds`, cumulative `total_duration_seconds`, `attempts`,
`parent_step`, `timing_exact` и `timing_partial`. Host-local `monotonic_started` используется только у
живого builder текущей ОС с совпадающим session_id. Завершённые durations переносимы между ОС;
чужой monotonic counter не сравнивается с локальным. `timing_totals` сохраняет потраченное время,
когда checkpoint приходится инвалидировать. Итог суммирует только корневые этапы, сохраняя вложенные
для детализации. Для старых данных используется явно обозначенная оценка, отсутствующие или обратные
времена не превращаются в выдуманные нули. Самостоятельные ожидания между запусками не суммируются.
После прерывания сохраняется уже измеренное время; незавершённый интервал прошлой session
отмечается неизвестным и не включает время перезагрузки.

## Идентичность задания

`run_id = <project>-<full-source-SHA>`, tag `v<version>+<build>`. `job.json` сохраняет исходный SHA,
версию/build, профиль, архитектуры, ожидаемые имена пакетов, SHA-256 source.bundle, digest production defines
и хеш каждого файла закреплённого Python runtime. У каждой ОС собственные credentials и пути.

Контейнеры JSON имеют `schema: 1`; версия протокола задаётся отдельным `protocol_version: 2`.
Совместимый приём старых сообщений версии 1 сохранён. Неизвестная новая версия отвергается.

## Пути и роли

Канонический каталог каждой ОС:
`.local-releases/releases/<project>/<version>+<build>/<SHA>/`.
В нём один `packages/`, `job.json`, `manifest.json`, source.bundle, runtime, `results/` и `logs/<host>/`.
Глобальный сервис индексирует эти каталоги, не копируя файлы.

| Данные | Размещение |
|---|---|
| Общий список проектов без credentials | `scripts/local_release/projects.json` в main координатора |
| Локальные пути профилей/репозиториев | `%LOCALAPPDATA%/AI11/LocalRelease/registry.json` или `~/.config/ai11-local-release/registry.json` |
| Windows credentials/настройки | `.local-releases/windows-config.json`, machine environment, защищённый keystore |
| Linux credentials/настройки | `~/.config/ai11-local-release/<project>.json` и private-файлы Linux checkout |
| Текущий этап и checkpoints | `results/<host>.json` |
| Результат приёма | `results/<host>-received.json`, `received.json`, runtime receipts |
| Неотправленный результат | `results/<host>-outbox.json` |
| План исправления Linux | `results/linux-remediation.json`, `results/linux-repair.sh` |

Windows готовит исходники и принимает Linux-результаты. Linux при graphical login обновляет main,
читает реестр и последовательно выполняет только зарегистрированные Linux-профили.
Новые подходящие коммиты сохраняются отдельными заданиями, `[skip ci]` пропускается.
Публичный релиз может финализировать сторона с полным набором подтверждённых результатов.

## Assets собственного draft

Префикс: `local-transfer-<run_id>-`. Принадлежность draft подтверждается маркером
`<!-- local-release:<run_id> -->`, source SHA и tag. Чужой draft не изменяется.

| Суффикс | Содержание |
|---|---|
| `job.tar.gz` | Неизменный исходный job, source.bundle, runtime, release notes |
| `runtime-v<N>.tar.gz` | Новая редакция координатора и job metadata без повторной передачи source.bundle |
| `<host>-status.json` | Идентичность, runtime revision, checkpoints, пакеты/asset IDs/digests, evidence и receipts |
| `<host>-logs.zip` | Очищенные журналы этапов данной ОС |
| `<host>-package-<SHA256>-<canonical-name>` | Неизменный временный пакет конкретного содержимого |

Скачивание проверяет размер/SHA-256; исходный bundle и runtime проверяются до исполнения.
Повторный запуск использует уже принятый bundle вместо повторного скачивания сотен мегабайт.
Пути контейнера обязаны оставаться внутри получателя; symlinks, directories и слишком большие runtime updates отвергаются.

## Частичный успех

Каждый успешно произведённый файл может попасть в собственный draft отдельно от остальных.
`built_unverified` означает сохранение для диагностики; `structure_verified` означает пройденные проверки состава.
Оба состояния отличаются от полного выпуска. Временное имя содержит хеш, поэтому исправление не перезаписывает прежний asset.
`manifest.json` хранит такие неподтверждённые файлы в `unverified_packages`, сохраняя один локальный экземпляр.

Отсутствующие Windows-пакеты не блокируют Linux. Неудачный Snap не блокирует TAR.GZ и наоборот.
Сбой сети оставляет локальные пакеты/outbox. Ошибки quality, integration, Sentry и install/smoke сохраняются;
они продолжают блокировать публичную финализацию, даже когда draft уже содержит бинарники.

Финализация требует всех обязательных gates обеих ОС, одинаковых compile inputs и полного комплекта пакетов.
Только затем публикуются канонические имена, SHA256SUMS и release-manifest.json.
Исторические опубликованные релизы не изменяются и не пересобираются.

## Обновление после ошибки

Windows выпускает проверенный runtime update с монотонным номером, предыдущим/new job digest и Git SHA инструментария.
Приём проверяет прежние source SHA/build/версии/архитектуры и сохранение всех обязательных gates.
Runtime меняется атомарно при отсутствии работающего builder; пакеты и подтверждённые checkpoints сохраняются.
Исправления Linux CMake/Snap packaging описываются точными `generated_source_overlays` digest, а не произвольным изменением исходников.
Опубликованный job таким способом обновлять нельзя.

Linux получает ремонт до следующего запуска, выполняет известные диагностические команды и повторяет нужные этапы.
Текст ошибок и история shell не исполняются как команды. Неизвестная ошибка возвращает новый лог.

`attempt_runtime_revision` фиксирует реально выполнявшуюся ревизию, `pending_runtime_revision` - доставленное
исправление до следующей попытки. Это позволяет Windows показать готовый repair отдельно от прежней ошибки.
`refresh-runtime --reason <описание>` сохраняет причину исправления в истории job.
Для проверенного изменения только приёмки можно дополнительно указать `--invalidate-step linux:verify-linux`.
Явный список повторяемых checkpoints записывается и в job audit, и в envelope; проверяется их совпадение,
а зависимые этапы сбрасываются транзитивно. Исходные gates остаются обязательными. При изменении source overlays
такое сохранение старых build checkpoints запрещено. По умолчанию сохраняется полная инвалидация Linux recipe.
Runtime15 использует `--invalidate-step linux:snap`: один раз повторяет весь исходный Snap-скрипт и его
inspection/install/smoke, сохраняя готовый TAR и пройденные integration tests. Заменяемый непубличный Snap
остаётся единственным локальным файлом; manifest переводит его в pending до пересборки и сохраняет ID
проверенной прежней копии в draft. Коллизия без подтверждённого remote backup по-прежнему блокирует замену.
Runtime16 сохраняет эти checkpoints и исправляет sudo TTY/временное подтверждение для установленной Snap-приёмки.
Runtime17 повторяет только `verify-linux`: protected Snap checksums читаются через подтверждённый sudo,
а новая успешно собранная Snap16, TAR и все пройденные build/test checkpoints сохраняются.
Runtime18 также повторяет только `verify-linux`: runtime17 успешно установил пакет, но владелец закрыл
тестовое окно до завершения десятисекундной проверки. Добавлены явная подсказка, обратный отсчёт,
один повтор только запуска после нормального раннего закрытия и exit/startup/timing evidence.
Требуемые десять секунд, готовые пакеты и пройденные build/test checkpoints сохраняются.

Snap-only инструменты проверяются в этапах Snap, сохраняя независимость portable TAR.
`unsquashfs -version` в squashfs-tools 4.6.1 печатает версию и возвращает 1 без входного image;
это принимается только для диагностики с распознанным version banner. Реальная проверка содержимого пакета
по-прежнему требует code0. Поведение подтверждается [исходником 4.6.1](https://github.com/plougher/squashfs-tools/blob/4.6.1/squashfs-tools/unsquashfs.c).

Receipts подтверждают точные asset IDs/digests. Base job/runtime repair сохраняются до полного завершения для recovery.
Очистка удаляет только собственные подтверждённые временные IDs; временные пакеты удаляются после проверенного
публичного зеркала. Канонические packages, SHA256SUMS и итоговый manifest остаются.
После полного успешного выпуска Windows проверяет все gates, локальные source/runtime/package hashes,
публичные package/checksum/manifest assets и сохраняет `results/exchange-closed.json` до первого удаления.
Этот финальный receipt закрывает весь завершённый обмен, включая старые runtime revisions и промежуточные
status/log/package assets с точным префиксом данного run. Удаляются только распознанные имена и сохранённые IDs;
чужие runs и неизвестные файлы сохраняются. Повтор очистки безопасен без нового входа в Linux.
После публикации manifest каталога ссылается на обычные публичные assets, а не удаляемые transport-копии.
Повтор handoff сначала проверяет уже отправленный base asset и не сжимает source.bundle заново.
Сохранённый receipt с точными identity/asset ID/hash и свежий GitHub digest позволяют повторно использовать
неизменённый base или пакет без повторного скачивания больших файлов. Первая отправка по-прежнему требует
полного download read-back; отсутствие receipt, новый ID или изменённый digest требуют повторной проверки.
При следующем Linux login уже опубликованный выпуск распознаётся по итоговому публичному manifest:
проверяются source/tag/build/defines, полный перечень gates, metadata всех пакетов и SHA256SUMS.
Локальный `publication-received.json` фиксирует подтверждение; старые локальные checkpoint records не подделываются.
Такой выпуск пропускается без сборки и без восстановления удалённых transport-файлов. После публикации карточка
может явно подтвердить завершение другой ОС по итоговому manifest, сохраняя историю её прошлых локальных попыток.
Для новых source snapshots, содержащих inventory script, `workflow-parity` обязателен на Windows и Linux.
Inventory фиксирует наличие hosted YAML; после cutover guard отвергает его повторное появление,
а parity исходных3jobs/53steps читается из immutable Git blob. Историческим snapshots без этого script
не добавляется невыполнимый gate и не сбрасываются их успешные проверки.

## Автонумерация и запуск

Новый локальный коммит без `[skip ci]` увеличивает build один раз через проектный helper и согласует четыре version-файла.
Git caches tree до commit-msg, поэтому контролируемый внутренний amend с выключенными hooks завершает один видимый коммит.
Наблюдатель получает итоговый SHA после согласования версии, промежуточный SHA не отправляется на сборку.
Retry после ошибки подписи повторно build не увеличивает. `[skip ci]` в заголовке/body пропускает и счётчик, и dispatch.
Получение существующих remote-коммитов не меняет их номера.

Первый запуск в Ubuntu: обновить main и выполнить `bash scripts/local_release/run-linux.sh`.
Он регистрирует профиль и устанавливает пользовательский XDG autostart без root. Следующие входы открывают терминал
с прогрессом и итогом всех подключённых проектов. Flutter закреплённой версии копируется/устанавливается только в временный каталог попытки; глобальный SDK не изменяется. Snapcraft выполняет весь исходный `snapcraft_build.sh`,
включая debug run; только его завершение через `q` автоматизировано в отдельном PTY. Release override-build сохраняется.

Реальная проверка нового graphical-login цикла и Snap install/smoke выполняется в Ubuntu; недоступный прогон не является PASS.

## Временное выполнение Linux и независимые отчёты

Linux отправляет собственный result, пакеты и полный logs.zip; не скачивает Windows APK/AAB/EXE/MSIX/Web и не публикует итоговый выпуск.
Перед большими пакетами отправляются logs.zip и provisional status с `delivery_complete=false`.
После read-back всех файлов отправляется status с `delivery_complete=true`. Неполная передача не является завершением выпуска.
Проверка upload выполняет полный потоковый SHA-256 read-back без второй дисковой копии пакета.
`linux-receipts/<project>/<SHA>.json` хранит небольшую квитанцию, preventing повторный download/build завершённого задания.
Новый runtime или явный `local-transfer-<run_id>-linux-resume.json` разрешают продолжение; сам immutable job.json не меняется от команды.
При повторе восстанавливаются только Linux-пакеты/evidence/checkpoints. Успешные Windows-этапы не сбрасываются.

Отдельный private control draft `ai11-local-reports-<project>` имеет marker `<!-- ai11-host-reports:<project>:1 -->`.
`latest-linux.json` - ограниченный текущий snapshot; `report-linux-<SHA|bootstrap>-<time>-<id>.json` - неизменяемая история завершений/ошибок.
Отчёт содержит schema/project/host/updated, phase/status, при наличии sha/result/timing/log_tails/error.
Его размер ограничен 512 KiB; секреты удаляются перед отправкой, временный JSON в Ubuntu создаётся в `/dev/shm`.
Bootstrap/Git-update/ENOSPC не требуют доступного job.json или места под второй пакет.
Windows проверяет marker/identity/digest, сохраняет отчёт и receipt; диагностический snapshot не объявляет gates пройденными.
Удаление версии также удаляет её диагностическую историю по точному SHA и запрещает её повторный импорт.

Очистка Linux разрешена после проверенной передачи и восстановления owner-state. При ошибке одна bounded outbox сохраняет попытку,
новые задания блокируются. В Linux остаются только небольшие управляющие записи, но не пакеты, логи, SDK-копии и build/cache-каталоги.
Новые LXD instances/images удаляются только при наблюдённой принадлежности процессной сессии сборки и отсутствии в baseline;
неизвестные или используемые другими проектами ресурсы сохраняются с явной ошибкой очистки. Системный prune запрещён.
Оригинальный snapcraft_build.sh выполняется целиком, без правок команд; ephemeral Snap использует LXD.

Linux получает и подготавливает задания по одному: следующий source bundle скачивается только после обработки предыдущей попытки. Исторический archive import в Linux запрещён движком.

## Повреждённый Python cache и обновление существующих заданий

После переполнения диска `.pyc` может остаться усечённым и вызвать `EOFError: marshal data too short` при следующем импорте.
Одного `-B` недостаточно: он запрещает запись, но не чтение существующего bytecode. Entry scripts загружают guard из исходника
до импорта координатора: включают dont_write_bytecode и уникальный пустой pycache_prefix. Новые cache-файлы не создаются,
глобальные/чужие Python-кэши не удаляются. Это проверено реальным усечённым `.pyc` на всех четырёх entrypoints.
Официальные источники: [CPython issue126606](https://github.com/python/cpython/issues/126606),
[параметры Python](https://docs.python.org/3.12/using/cmdline.html#envvar-PYTHONPYCACHEPREFIX).

Существующее job/outbox получает runtime repairs до recovery и запуска, а не только при получении новых заданий.
Ручной запуск и панель входят через актуальный CLI, затем выполняют проверенный frozen runtime задания.
Lifecycle lock не позволяет заменить runtime работающего builder. При незавершённых gates сначала передаётся прежний outbox,
после verified receipt та же попытка продолжается с принятыми пакетами. Полная пересборка/повторное скачивание им не требуются.
Импорт Snap acceptance находится внутри verify-linux, поэтому его ошибка не подписывается как успешный inspect-snap.
Очищенный traceback сохраняется в bounded result и отдельном stage-error.log, даже если внешний wrapper сообщает общую ошибку.

## Подтверждённый временный цикл и удаление

01.11.2026 Ubuntu runtime4/build174 завершил verify-linux за 28.388 с без повторной компиляции/упаковки.
Snap revision и пользовательские данные восстановлены; проверены передача и provider cleanup.
Итоговый независимый отчёт `phase=cleaned` подтверждает удаление managed build data (30.915 с вместе с доставкой).
Семь исходных пакетов сохранили SHA-256; Windows получает полные gates/logs/timings штатным receiver.
Linux - временный builder: Windows/GitHub deletion не ждёт Linux ack. Метки удаления остаются долговечными,
блокируют jobs/import и отменяют/очищают возможную bounded попытку до нового запуска. Старые control drafts
переносятся в проверенные Git notes и удаляются после миграции; новые не создаются. Старые Linux ack читаются для совместимости.

## Очистка технических draft после успеха

После публикации всех подготовленных jobs Windows сначала сохраняет полные redacted Windows/Linux logs, результаты
и историю host reports в одном `build-logs-<SHA256-prefix>.zip` при готовом public Release. Архив имеет отдельный
SHA-256/read-back receipt, не считается восьмым пакетом и не хранится второй ZIP-копией на диске Windows.
Только после durable receipt и повторной проверки неизменности списка assets удаляется owned diagnostic draft.
Неизвестные assets, новая отправка Linux, незавершённый job, bootstrap/Stop/transfer failure сохраняют draft для recovery.
Deletion control хранится в `refs/notes/ai11-local-retention`: только малые requests/acks, append/merge без force push,
проверка project/version/SHA и read-back; main/index/owner changes не меняются. Все control commits имеют реальный
`retention_task_code` из профиля и `[skip ci]`, поэтому autobuild не запускается и build не увеличивается.
Linux получает notes до любых jobs. Старые retention drafts мигрируют и удаляются, новые не создаются.
Основа формата: [Git notes](https://git-scm.com/docs/git-notes), [Git push](https://git-scm.com/docs/git-push).
