# Обмен локальных сборщиков

Doc-Version: 2.0.1
Last-Updated: 2026-10-31
Source-Commit: working-tree

Git `main` хранит инструменты, профили и [перечень проектов](../../../scripts/local_release/projects.json).
Draft GitHub Releases передают задания, пакеты, результаты и очищенные логи. Секреты и бинарники в Git не попадают.
Регистрация другого проекта и его автобилд выполняются в задаче этого проекта; сейчас включён Revelation.

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

Snap-only инструменты проверяются в этапах Snap, сохраняя независимость portable TAR.
`unsquashfs -version` в squashfs-tools 4.6.1 печатает версию и возвращает 1 без входного image;
это принимается только для диагностики с распознанным version banner. Реальная проверка содержимого пакета
по-прежнему требует code0. Поведение подтверждается [исходником 4.6.1](https://github.com/plougher/squashfs-tools/blob/4.6.1/squashfs-tools/unsquashfs.c).

Receipts подтверждают точные asset IDs/digests. Base job/runtime repair сохраняются до полного завершения для recovery.
Очистка удаляет только собственные подтверждённые временные IDs; временные пакеты удаляются после проверенного
публичного зеркала. Канонические packages, SHA256SUMS и итоговый manifest остаются.

## Автонумерация и запуск

Новый локальный коммит без `[skip ci]` увеличивает build один раз через проектный helper и согласует четыре version-файла.
Git caches tree до commit-msg, поэтому контролируемый внутренний amend с выключенными hooks завершает один видимый коммит.
Наблюдатель получает итоговый SHA после согласования версии, промежуточный SHA не отправляется на сборку.
Retry после ошибки подписи повторно build не увеличивает. `[skip ci]` в заголовке/body пропускает и счётчик, и dispatch.
Получение существующих remote-коммитов не меняет их номера.

Первый запуск в Ubuntu: обновить main и выполнить `bash scripts/local_release/run-linux.sh`.
Он регистрирует профиль и устанавливает пользовательский XDG autostart без root. Следующие входы открывают терминал
с прогрессом и итогом всех подключённых проектов. Flutter при необходимости устанавливается отдельно в user cache
строго указанной версии; глобальный SDK не заменяется. Snapcraft использует подтверждённую последовательность clean/pack
и release override-build без интерактивного flutter run.

Реальная проверка нового graphical-login цикла и Snap install/smoke выполняется в Ubuntu; недоступный прогон не является PASS.
