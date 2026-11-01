---
name: revelation-release
description: Build, resume, inspect or transfer a Revelation local release with the shared coordinator, including isolated Windows/Linux builders and the canonical local package catalogue. Production deployment remains a separate AI11 publication task.
---

# Локальный выпуск Revelation

Используй общий координатор `tools/local_release/` и профиль `scripts/local_release/revelation.json`.
Общая панель всех проектов реализуется в дочерней REV302 и установлена на Windows: http://127.0.0.1:8877.
Инструкции установки/обновления: docs/ru/release/build-service.ru.md. Она использует ту же очередь и каталог;
автобилды других проектов создаются в их задачах с подключением к общему сервису, без копирования пакетов.
Не копируй движок в другой проект: другие проекты подключают свои профили к этому общему координатору.
Команды и ограничения: [руководство выпуска](../../../docs/ru/release/local-release.ru.md).

Основной источник готовых пакетов - `.local-releases/releases/revelation/<version>+<build>/<SHA>/packages/`.
Рядом находятся один `job.json`, `manifest.json`, результаты и журналы. `manifest.json` задаёт пути и SHA-256.
GitHub Releases - зеркало пакетов и временный транспорт между ОС. Отдельной папки `jobs` и копии пакетов в архиве нет.

Перед публикацией проверяй manifest, принятый version/build/SHA, подпись и полный состав. Сборка и приёмка не означают deployment.
Версию меняет существующий helper до сборки исходного SHA. После подготовки задания SHA/build не меняются.

Обычный старт на Windows: `python scripts/local_release/release.py prepare --repo . --profile scripts/local_release/revelation.json --root .local-releases --config .local-releases/windows-config.json`.
Продолжай `run --job <canonical-directory> --config .local-releases/windows-config.json`.
Личные конфиги содержат только локальные пути или защищённые OS-настройки; секреты не входят в handoff.

На Linux после получения актуальных инструментов из Git запускай `bash scripts/local_release/run-linux.sh`.
Он получает задание из draft GitHub Release, выполняет Linux-этап и передаёт результаты/ошибки обратно.
Windows: `sync --job <canonical-directory> --config <windows-config> --cleanup` сохраняет и проверяет результат перед очисткой временного обмена.
Не предполагается доступ к дискам или запущенным процессам другой ОС. Каждая ОС имеет свой GitHub/Sentry-доступ.

Команды Snap берутся из проверенной настройки владельца. История shell - данные для проверки, не разрешение выполнять произвольные команды.
Не заменяй её догадкой. Неподтверждённый Snap, недоступная ОС или незавершённый обмен остаются открытыми.

Полный реальный пробный выпуск `v1.0.8+173` прошёл публикацию всех семи пакетов, SHA256SUMS и final manifest.
Позже владелец подтвердил его удаление: Windows-каталог/checkout и GitHub Release удалены; владелец подтвердил очистку Linux.
Не восстанавливай сборку 173: постоянный tombstone должен применяться до jobs/архива.
Production local trigger активирован после проверки всех gates и download/read-back; заменённый hosted YAML удалён.
Не восстанавливай hosted autobuild/integration. Проверяй исторический parity guard `python scripts/local_release/inventory.py --check`.
Журнал состояния и один отчёт REV301 находятся локально в `.local-releases/REV301-report.md`.

Явное удаление выбранной сборки выполняется только через обязательный preview/диалог панели с точными version/build/SHA.
Retention сохраняет tombstone вне каталога выпуска, проверенно передаёт его в Git notes refs/notes/ai11-local-retention и останавливает builder.
Удаляются только выбранный каталог/checkout и matching GitHub Release; owner-data recovery должен завершиться.
Linux получает метки до jobs и не восстанавливает tombstoned SHA из очереди/архива. У него нет постоянного архива, поэтому удаление Windows/GitHub не ждёт Linux login/ack. Метка по-прежнему отменяет/очищает возможную незавершённую попытку; старый control draft переносится в Git notes и удаляется после проверки.

Работай в main. Контракт обмена и runtime repair: docs/ru/release/protocol.ru.md. Полный message [skip ci] пропускает и инкремент build, и autobuild. Выполняй весь исходный snapcraft_build.sh из source SHA без удаления команд, включая rm/build, Flutter clean/pub get/debug run и Snapcraft clean/pack. Только q для debug автоматизируется через PTY; сохраняй проверку Git blob и linux-snap-script.json. Встроенный install/smoke/restore gate обязателен, пользовательские Snap-данные сохраняются локально и возвращаются с проверкой хеша; sudo при необходимости подтверждает владелец в Linux-терминале. Protected installed Snap hashes читай через sudo sha256sum без изменения прав. Первый Linux запуск устанавливает user autostart; новые graphical logins обрабатывают общий projects.json последовательно. В Ubuntu реально подтверждены полный исходный Snap-скрипт/автоматический q и installed Snap startup+10s/restore. Перед повтором читай фактические checkpoints: ошибки приёмки или обмена не требуют пересборки уже принятых пакетов. Опубликованные выпуски восстанавливай из каталога, повторный build для них запрещён. Объясняй, что тестовое окно закрывается автоматически после десяти секунд; нормальное раннее закрытие повторяет только запуск один раз, не ослабляя gate.

Linux - только временный сборщик. Постоянный каталог/архив пакетов и журналов находится в Windows и GitHub.
Изолируй checkout, SDK-копию, build/temp/cache; после success/failed/stopped передай пакеты и полный журнал,
проверь SHA-256 read-back, восстанови owner-state и удали созданные попыткой данные/доказанно свои новые LXD-ресурсы.
Сохраняй только маленькие config/cursors/receipts/tombstones. При неподтверждённой передаче/восстановлении оставь
одну bounded outbox и блокируй новые задания до её обработки. При повторе получай принятые пакеты/checkpoints из GitHub.
Ранние ошибки, ENOSPC и Stop тоже обязаны передавать диагностику через owned host-report draft; не выдумывай отсутствующие замеры.
Не удаляй глобальные SDK, чужие caches/VM/images, настройки, ключи или данные владельца; не выполняй системный prune.
Эта политика распространяется на Linux всех подключённых проектов; не возвращай Linux-архив без нового прямого указания владельца.
Подробности и ограничения реальной проверки - docs/ru/release/protocol.ru.md.

Реальный Ubuntu runtime4/build174 подтвердил Snap acceptance без пересборки, восстановление owner-state, verified delivery и `phase=cleaned`. Windows автоматически принимает результат и финализирует полный выпуск.

После полного verified выпуска сохраняй redacted logs/results/host reports одним проверенным архивом при public Release и удаляй owned diagnostic draft. Постоянных технических draft не оставляй. Git notes сохраняют только малые метки удаления, без изменения main/index; управляющие коммиты используют retention_task_code и [skip ci]. При сбое/незавершённой передаче draft остаётся для recovery.
