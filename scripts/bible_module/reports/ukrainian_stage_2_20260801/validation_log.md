# Журнал проверок этапа 2 украинского библейского модуля

Дата: `2026-08-01`

Рабочий commit до изменений: `d7f6b9a` (`Qualify Ukrainian translation sources`)

Статус этапа: `Завершён`

## Объём

Проверена и зафиксирована только техническая спецификация этапа 2. Украинские
исходные файлы не загружались, source lock этапа 3 не создавался, украинский
SQLite-модуль не собирался и существующие SQLite-файлы не изменялись.

## Нормативный baseline

- `bible_kjv.sqlite` SHA-256:
  `b105f174c37c6703b71831a99ff838fed3439b84132c743bd3b58b37a326c780`;
- schema fingerprint:
  `e14d4e2b2727122240f3765104cf4e2d63f789d5904be6aa3766cf761f5583b8`;
- SHA-256 последовательности 31 102 `verse_key`:
  `43324c450e6158f77ea92eedbc9d6dc0df60184dee43ce14eac27baa0dae6e60`;
- количество книг/глав/целевых стихов/ключей:
  `66 / 1 189 / 31 102 / 31 102`;
- первый/последний ключ: `001 / NZY`;
- полный упорядоченный список ключей, metadata, `PRAGMA user_version`, строка
  `info` и SQL-схема находятся в `baseline_manifest.json`.

## Выполненные команды

| Команда | Результат |
| --- | --- |
| `python -m scripts.bible_module.generate_ukrainian_stage_2_baseline --check` | PASS; артефакты совпали с воспроизводимой генерацией |
| `python -m unittest scripts.bible_module.tests.test_ukrainian_stage_2_contract` | PASS; 9 тестов |
| `python -m unittest discover -s scripts/content_tool/tests` | PASS; 30 тестов |
| `python -m compileall -q scripts/bible_module/generate_ukrainian_stage_2_baseline.py scripts/bible_module/ukrainian_stage_2_contract.py scripts/bible_module/ukrainian_strong.py scripts/bible_module/tests/test_ukrainian_stage_2_contract.py` | PASS |
| `python -m unittest discover -s scripts/bible_module/tests` | KNOWN PRE-EXISTING FAILURE; 108 тестов, 1 failure и 2 errors в неизменённом `test_apply_extended_strong_descriptions.py` |
| `dart format .` | PASS; 475 файлов, 0 изменений |
| `flutter analyze` | PASS; `No issues found`, 80,5 с |
| `flutter test` | PASS; 920 тестов |
| `dart run scripts/check_forbidden_patterns.dart` | PASS |
| `dart run scripts/check_docs_sync.dart` | PASS |
| `flutter test integration_test/smoke -d windows` | PARTIAL; первый файл и 3 теста прошли, следующие runners не стартовали повторно (`log reader stopped unexpectedly`) |
| изолированные Windows smoke-файлы | 8 PASS, 1 предсуществующий FAIL; подробности ниже |
| `git diff --check` | PASS |

Первый объединённый запуск `flutter analyze` вместе с двумя Dart-проверками
превысил лимит 240 секунд без результата. Оставшийся процесс конкретного
запуска был завершён по его PID; все три команды затем выполнены отдельно и
прошли. Это не считается результатом проверки и сохранено здесь только для
воспроизводимости журнала.

## Предсуществующие отклонения

### Python discovery

Полная discovery падает только в старых сценариях
`test_apply_extended_strong_descriptions.py`: fixture использует `G6000` и
`G20833`, а `GREEK_DESC_GROUP_RANGES` после commit `6981496`
(`Removed extended Strong Numbers`) заканчивается на `G5624`. Те же 1 failure
и 2 errors уже зафиксированы до этапа 2 в
`scripts/bible_module/reports/evidence_audit_20260725/checkpoint.json`.

Ни `scripts/content_tool/helpers.py`, ни
`scripts/bible_module/apply_extended_strong_descriptions.py`, ни его старый
тест в этом change set не изменялись. Ремонт удалённого extended-слоя не
входит в этап 2. Новые правила украинского модуля проверяются отдельными
fail-closed contract-тестами и проходят.

### Windows smoke

После неуспешного пакетного перезапуска каждый smoke-файл запускался отдельно:

- `about_download_navigation_smoke_test.dart`: PASS, 3 теста;
- `app_startup_smoke_test.dart`: PASS, 1 тест;
- `planned_features_navigation_smoke_test.dart`: PASS, 1 тест;
- `primary_sources_navigation_smoke_test.dart`: PASS, 1 тест;
- `settings_topics_language_sync_smoke_test.dart`: PASS, 1 тест;
- `strongs_dictionary_navigation_smoke_test.dart`: PASS, 1 тест;
- `bible_navigation_smoke_test.dart`: FAIL, 1 тест; существующий finder
  ожидал один `bible_module_dropdown`, текущий неизменённый runtime отрисовал
  два.

Этап 2 не меняет runtime, маршруты, UI или smoke coverage. Этот старый
UI/smoke-конфликт не ослабляет автоматические контракты целевой сетки, схемы,
порядка ключей, идентификаторов и Strong, но должен исправляться отдельным
change set, а не внутри технической спецификации.

## Проверяемые контракты этапа

Новые тесты аварийно завершаются при изменении:

- SHA-256 KJV-эталона, `PRAGMA user_version`, metadata, строки `info` или
  SQL-схемы;
- канона, количества книг/глав/стихов, JSON-карты или любого места и порядка
  31 102 ключей;
- `bible_ohienko_1988.sqlite`, `OH1988`, `ohienko_1988`, языка, названия,
  канона, версификации или шаблонов `info`;
- диапазонов classic Strong, удаления ведущих нулей, утверждённой таблицы
  extended→classic, обработки альтернативных/составных значений или попытки
  молча отбросить неизвестный extended Strong;
- подтверждения закрытого этапа 1 или запрета начинать этап 3 в рамках этого
  change set.

## Выход

Все решения этапа 2 однозначны, baseline воспроизводим, контрактные проверки
проходят. Фактическая сохраняющая проекция полного корпуса должна быть доказана
на этапе 5; её невозможность является `critical`, блокирует сборку и повторно
открывает этап 2 для отдельного архитектурного согласования.
