# Локальный выпуск Revelation

Doc-Version: 1.0.8
Last-Updated: 2026-10-31
Source-Commit: working-tree

[Общая панель сборок и автозапуск](build-service.ru.md) - http://127.0.0.1:8877.

Миграция выполняется в REV301. Наличие инструментов не означает завершённый переход.
Hosted `.github/workflows/flutter_build.yml` сохраняется до полного реального пробного выпуска, проверки GitHub assets и локального триггера.
Магазины, production-сайт и Supabase публикуются отдельной задачей версии после приёмки.

Дочерняя [REV302](https://ai11.link/cabinet/tasks?project=1&task=REV302) реализует общий локальный сервис всех проектов:
каталог версий/платформ/пакетов, текущие этапы и очередь, запуск/повтор/остановку, автозапуск и постоянный локальный URL.
Сервис читает те же файлы пакетов. Автобилды остальных проектов создаются в их собственных задачах
и подключаются к общему сервису через профили/очереди/каталоги этого координатора. Windows-сервис установлен;
реальный следующий login и Linux autostart проверяются отдельно, полный rollout REV301 ещё не завершён.

## Единственный каталог пакетов

Основной источник для развёртывания:

```text
.local-releases/
  releases/revelation/<version>+<build>/<full-Git-SHA>/
    packages/                 APK, AAB, EXE, MSIX, Web ZIP, Linux TAR.GZ, Snap
    job.json                  неизменные исходники, версии, состав и runtime
    manifest.json             относительные пути, размеры, SHA-256 и готовность
    source.bundle             исходный коммит для независимого checkout
    runtime/                  закреплённый координатор этого задания
    results/                  один актуальный результат и подтверждения по ОС
    logs/<os>/<step>.log       один журнал шага с историей повторов
    publication.json          внешние asset ID/URL и состояние зеркала
  w/<short-SHA>/<os-initial>/  временные изолированные рабочие деревья сборщиков
  github-index.json            индекс восстановленных исторических выпусков
  windows-config.json          локальные пути и настройки Windows
  REV301-report.md             один текущий отчёт миграции
```

Всё содержимое `.local-releases/` исключено из Git. Отдельной папки `jobs` и второй постоянной копии пакетов нет.
Пакеты после упаковки перемещаются в `packages/`; публикация читает эти же файлы.
Временные рабочие деревья и транспортные контейнеры не являются дополнительным архивом релизов.
`manifest.json` со статусом `incomplete` не подтверждает готовность; `archived` означает восстановление прежнего выпуска, а не повторение его проверок.
Отсутствующий пакет не заменяется другой версией или SHA. Повреждённый или конфликтующий файл не перезаписывается молча.

## Windows

Требуются Python 3.10+, Git, Flutter 3.47.2, Java 17, Android SDK, Visual Studio C++/Windows SDK и Inno Setup.
Секреты Android signing передаются через существующие `SIGNING_*` environment variables.
Рабочий keystore задаётся локальным `signing_store_file`; сборщик проверяет пароль приватного ключа и
`expected_signing_certificate_sha256`. Значения ключа и паролей не входят в переносимое задание.
Конфиг указывает `defines_file`, `sentry_properties`, `inno_setup`, при необходимости `environment`, `android_sdk`, `android_device`, `chromedriver_port` и `web_port`.
Для Windows integration включите `integration_targets: ["windows", "android", "web"]`.
Задайте отдельные `android_avd_name`, `android_device` вида `emulator-5584` и `adb_server_port` (например 5041, не 5037).
Координатор сам запускает этот AVD без окна с временными данными, ждёт загрузки и закрывает только свой процесс.
Уже работающий AVD используется только после проверки имени и не закрывается координатором.
`chromedriver_path`, его проверенный `chromedriver_sha256` и свободный `chromedriver_port` включают автоматический
запуск/закрытие ChromeDriver. Браузерные тесты используют отдельный headless profile, окна владельца не затрагиваются.
SQLite fixtures передаются бинарным `adb exec-in`: обычный Windows stdin может оборваться на DOS EOF.
После передачи координатор ждёт полного размера файла на устройстве и только потом сверяет SHA-256,
так как завершение `exec-in` опережает окончание удалённой записи. Готовые APK/AAB не пересобираются из-за fixture repair.
Android-файлы запускаются с `flutter test --no-uninstall`: стандартная очистка Flutter после первого файла
иначе удаляет приложение вместе с заранее установленными тестовыми базами. AVD остаётся отдельным временным окружением.
Web `flutter drive` требует IntegrationTest binding. Для smoke-файлов с обычным WidgetTest binding
координатор создаёт launcher в `.dart_tool/ai11_integration/`, подключает IntegrationTest binding и вызывает
исходный `main()` без изменения сценариев. Файлы с собственным IntegrationTest binding получают ту же диагностику.
Хеши launcher/исходного test сохраняются в `results/windows-web-driver-targets.json`.
Все Web-команды выполняются из физического checkout, без MSBuild SUBST. Иначе Flutter считает
пути C:/R: разными конфигурациями и может удалить свежие assets при очистке прежних outputs.
Recovery удаляет только Web/localization stamp с путями alias и Web `.last_build_id`, сохраняя native compile cache и пакеты;
evidence находится в `windows-web-cache-recovery.json`. Incognito предотвращает перенос service worker между тестами.
Release-диагностика сохраняет текст исключения и stack, даже если Flutter убирает описание ошибки.
Для точного исторического About smoke из build173 проверяемая test-only копия исправляет ожидания:
Web не показывает native-only обслуживание баз/папки, но показывает очистку кеша. Исходный checkout,
код приложения и пакеты не меняются; digest и причина адаптации записываются в тот же evidence.
Исторический retry smoke учитывает одну неудачную primary-попытку и ровно одну успешную загрузку на каждую
открытую панель, включая автоматический параллельный перевод. Число вызовов и панелей сохраняется в reportData.
Перед Android-командами координатор проверяет пути Flutter-плагинов и при необходимости пересоздаёт их через
`flutter pub get` из физического checkout. Временный SUBST применяется для Windows/MSBuild;
Android не должен зависеть от отключаемой буквы диска. Восстановление `android-cache-recovery` проверяет
`gradlew help --offline`, сохраняя готовые пакеты и прежнюю ошибку в доказательстве восстановления.
Секреты не должны попадать в Git, `job.json`, AI11 или handoff. Конфиг каждой ОС остаётся локальным.
Production-сборка задаёт `SENTRY_ENVIRONMENT=production`, сохраняя исходный dev-конфиг.

```powershell
python scripts/local_release/release.py prepare --repo . --profile scripts/local_release/revelation.json --root .local-releases --config .local-releases/windows-config.json
python scripts/local_release/release.py run --job <canonical-directory> --config .local-releases/windows-config.json --phase quality
python scripts/local_release/release.py run --job <canonical-directory> --config .local-releases/windows-config.json --phase integration
python scripts/local_release/release.py run --job <canonical-directory> --config .local-releases/windows-config.json --phase build
python scripts/local_release/release.py send-result --job <canonical-directory> --config .local-releases/windows-config.json
python scripts/local_release/release.py handoff --job <canonical-directory> --config .local-releases/windows-config.json
```

Можно выполнить `run` без `--phase` для всего этапа. Flutter-команды выполняются последовательно.
Проверки качества соответствуют исходному workflow, включая unit/widget/coverage, LCOV filter и 90% effective coverage.
Дополнительно обязательны локальные integration, docs sync и проверка упаковки/подписи.
Данные и настройки тестируемых устройств должны сохраняться; недоступное устройство не считается PASS.
Номер версии меняется штатным helper до выбора исходного SHA. Внутри задания его не повышают.

## Независимый Linux и обмен

Доступ к Windows-диску не требуется. Linux обновляет исходники и инструменты из Git, затем запускает:

```bash
bash scripts/local_release/run-linux.sh
```

Первичная доставка этих инструментов в Git должна быть отдельно выполнена в рамках разрешённого commit/push.
Скрипт получает подготовленное задание из принадлежащего ему draft GitHub Release, проверяет SHA/runtime/source bundle,
строит в собственном checkout и сохраняет результат в своём каноническом `.local-releases/`.
Его конфиг по умолчанию: `~/.config/ai11-local-release/revelation.json`.
У каждой ОС должны быть собственный GitHub-доступ (`GH_TOKEN`, защищённый token file, native Git credential helper или `gh auth`) и локальный Sentry token.
Секреты Windows не передаются Linux. Flutter/native/Snap tools должны быть реально доступны в Linux.
Автоматический Snap выполняет весь исходный `snapcraft_build.sh` из закреплённого source SHA в отдельном input checkout:
`rm -rf build`, `flutter clean`, `flutter pub get`, `flutter run -d linux --debug --dart-define-from-file=api-keys.json`,
`snapcraft clean`, `snapcraft pack` и сообщение `Build complete`. Git blob скрипта проверяется перед запуском;
порядок и команды не сокращаются. Сохраняются release override-build и pinned Flutter SDK из job.
Только ввод `q` автоматизирован через настоящий Linux PTY после команд Flutter, сообщения старта приложения
и пяти секунд работы. Этот debug-процесс использует отдельные XDG Documents/config/data/cache.
Snapcraft сохраняет исходное окружение. Доказательство полного запуска: `results/linux-snap-script.json`.
Ручной `./snapcraft_build.sh` сохраняет исходное поведение; автоматический многопроектный вход - `run-linux.sh`.
Встроенный `verify-linux` устанавливает именно проверенный по SHA-256 пакет, проверяет реальный запуск Flutter
и десять секунд работы, затем восстанавливает прежнюю revision, tracking и snapshot данных Snap.
Не закрывайте появившееся тестовое окно: терминал показывает обратный отсчёт, проверка сама его закроет.
Если окно нормально закрыто раньше, повторяется только запуск один раз без переустановки и пересборки.
Повторное раннее закрытие оставляет проверку незавершённой. Crash, fatal output и stop не повторяются автоматически.
Код выхода, startup marker и длительность каждой попытки сохраняются в `results/linux-snap-smoke.json`.
Перед тестом пользовательский каталог Snap временно переименовывается рядом с исходным местом;
после проверки возвращаются те же файлы с проверкой общего хеша, включая исключённые из snapshot caches.
Если приложения раньше не было, удаляется только временная установка с совпавшим хешем. Тест задаёт собственные
XDG config/data/cache/Documents внутри Snap; пользовательские базы и настройки не используются.
При ошибке или остановке восстановление всё равно выполняется. Журнал восстановления остаётся локально
в `.local-releases/w/<short-SHA>/snap-acceptance/restore.json` до успешного восстановления; после аварийного
выхода следующий запуск сначала завершит восстановление. Snapshot данных не передаётся на GitHub.
Установку выполняет `sudo -n snap`. Если права ещё не подтверждены, в графическом progress terminal
Ubuntu один раз запросит пароль через `sudo -v`; он не сохраняется и не попадает в журналы.
Успех аутентификации отдельно подтверждается перед проверкой пакета. Файлы установленных Snap в
`/var/lib/snapd/snaps/` могут быть недоступны обычному пользователю: их SHA-256 вычисляет
`sudo -n sha256sum`, включая проверку revision при восстановлении. Python не читает эти файлы напрямую,
права доступа не меняются. Отказ чтения после принятого пароля не считается ошибкой пароля.
Sudo-команды сохраняют controlling terminal; временное подтверждение продлевается только пока идёт
установка/проверка/восстановление, чтобы загрузка зависимостей не прервала последующее восстановление.
Постоянные passwordless/sudoers права не создаются. Без интерактивного терминала или доступного sudo gate
остаётся незавершённым с точной инструкцией. Собственный verifier по-прежнему можно явно закрепить через
`snap_verify_script` и `snap_verify_script_sha256`. Непройденная приёмка сохраняет draft;
бинарники возвращаются независимо от неё.
Ограниченный безопасный список найденных Snap-команд из `.bash_history` собирается как данные для анализа; автоматически история не исполняется.

Linux сам передаёт проверенные пакеты и актуальный статус, а при сбое - статус и очищенные журналы.
Ненулевой exit code сохраняется. При отсутствии сети/авторизации результат остаётся в локальном outbox до повторного запуска/`send-result`.
Такое состояние не подтверждает доставку отчёта на GitHub.

После возврата Windows:

```powershell
python scripts/local_release/release.py sync --job <canonical-directory> --config .local-releases/windows-config.json --cleanup
```

Команда получает пакеты, доказательства и журналы, проверяет идентичность запуска и хеши, сохраняет всё локально,
затем удаляет только известные ID временного обмена этого запуска. Пакеты, `SHA256SUMS` и итоговый release manifest остаются внешним резервом.
Полный публичный GitHub Release требует весь согласованный комплект и gates обеих ОС; один успешный Linux-этап не означает полный выпуск.

## Архив, очередь и восстановление

```powershell
python scripts/local_release/release.py archive --profile scripts/local_release/revelation.json --root .local-releases --config .local-releases/windows-config.json
python scripts/local_release/release.py verify-packages <canonical-directory>
python scripts/local_release/release.py status --job <canonical-directory>
python -m unittest discover -s tools/local_release/tests -v
python scripts/local_release/inventory.py --check
```

Архивирование получает все страницы GitHub Releases/assets, проверяет размер и доступный publisher SHA-256, сохраняет собственный SHA-256,
исходные URL/ID и tag SHA. Исторические версии не пересобираются. Существующие файлы сверяются, а не скачиваются повторно без причины.

Общий координатор - `tools/local_release/`, профиль - `scripts/local_release/revelation.json`;
[полная матрица 53 шагов](../../../scripts/local_release/workflow-inventory.json) привязана к исходному Git blob.
Другие проекты подключают свои профили к этому движку.

`init-queue` только фиксирует историческую границу. `install-trigger` требует завершённый опубликованный пробный выпуск;
до этого production-hooks и startup worker не включаются. Тестовые hooks проверяются только в изолированном репозитории.
Полный текст `[skip ci]` пропускает автоматический инкремент build и сборку/публикацию, а остальные новые локальные и полученные remote SHA сохраняются по одному,
без ограничений ветки/путей и без замены очереди последним коммитом. Существующие hooks выполняются и восстанавливаются при удалении триггера.
Задания с одинаковым version/build и разными SHA сохраняются раздельно; коллизия внешнего тега блокирует публикацию, не меняет исходники и не теряет пакет.
Сбой остаётся в очереди; `retry --queue <queue-file> --sha <full-SHA>` разрешает повтор только этого задания.
OS-backed locks освобождаются после завершения/аварии процесса; активный builder не вытесняется по таймеру.

Координатор перечисляет все `integration_test/**/*_test.dart`, включая smoke, и запускает каждый файл
отдельным процессом Flutter с собственным checkpoint. В Flutter 3.47.2 это также обходит закрытие
`DesktopLogReader` после первого desktop-приложения. Повтор сохраняет успешные файлы и выполняет оставшиеся;
общий integration gate проходит только после полного набора.

Подробный [протокол Windows/Linux](protocol.ru.md) задаёт структуру заданий, runtime repair, частичных пакетов, логов и receipts. Работа ведётся в main; отдельная ветка для обмена не нужна.
