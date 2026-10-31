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

До успешного полного реального пробного выпуска и проверки триггера сохраняй hosted workflow и не активируй автоматические локальные сборки.
Сейчас идёт REV301; журнал состояния и один отчёт находятся локально в `.local-releases/REV301-report.md`.

Работай в main. Контракт обмена и runtime repair: docs/ru/release/protocol.ru.md. Полный message [skip ci] пропускает и инкремент build, и autobuild. Выполняй весь исходный snapcraft_build.sh из source SHA без удаления команд, включая rm/build, Flutter clean/pub get/debug run и Snapcraft clean/pack. Только q для debug автоматизируется через PTY; сохраняй проверку Git blob и linux-snap-script.json. Встроенный install/smoke/restore gate обязателен, пользовательские Snap-данные сохраняются локально и возвращаются с проверкой хеша; sudo при необходимости подтверждает владелец в Linux-терминале. Protected installed Snap hashes читай через sudo sha256sum без изменения прав. Первый Linux запуск устанавливает user autostart; новые graphical logins обрабатывают общий projects.json последовательно. В runtime16 реально пройдены полный исходный Snap-скрипт и автоматический q; runtime18 повторяет только installed Snap приёмку, сохраняя готовые пакеты и тесты. Объясняй, что тестовое окно закрывается автоматически после десяти секунд; нормальное раннее закрытие повторяет только запуск один раз, не ослабляя gate.
