# Журнал повторного закрытия этапа 2 украинского библейского модуля

Дата: `2026-08-01`

Исходное состояние: ветка `main`, рабочее дерево до задачи чистое.

Статус этапа: `Завершён`

## Объём и ограничения

Повторно проверены этап 1 и технический контракт этапа 2 после добавления
печатных сносок и `verses.comment`. Обновлены только нормативная модель,
генератор baseline, checked-in доказательства, contract-тесты и связанные
отчёты. Украинский корпус и итоговый `bible_ohienko_1988.sqlite` не создавались.
Парсинг сносок, UI редактора и Flutter runtime не реализовывались: это этапы
4, 9 и 10 соответственно.

Ни один файл не публиковался в Supabase, `Revelation.website` или другую
удалённую систему. Commit не создавался.

## Повторная проверка этапа 1

Страница точного 1538-страничного Commons DjVu применяет CC BY-SA 4.0 ко всему
файлу и подтверждает разрешение правообладателя VRT-билетом
`2013112610015211`. Сообщение Wikimedia Ukraine фиксирует разрешение УБТ на
тексты изданий Огиенко до 1991 года, производные работы и передачу точного
юбилейного издания 1988 года. Отдельного исключения для напечатанных в этом
файле стиховых сносок не найдено.

Поэтому в пределах этих доказательств сноски можно извлекать, преобразовывать,
хранить в `verses.comment`, воспроизводимо редактировать и распространять в
составе производного модуля при атрибуции, указании изменений и ShareAlike.
Вывод не распространяется на поздние редакции УБТ, внешние комментарии или
материал с отдельным уведомлением о правах. Результат сохранён в отчёте этапа
1 и `source_probe.json`.

## Разделённые schema profiles

Baseline больше не использует одно неоднозначное значение прикладной схемы:

- `legacy_v3` — фактическая общая схема существующих KJV/LXX_TR:
  `PRAGMA user_version = 3`, `db_metadata.schema_version = '3'`,
  `verses(verse_key, text)` без `comment`;
- `ukrainian_v4` — целевой контракт будущего украинского модуля:
  schema version `4`, `PRAGMA user_version = 4`,
  `db_metadata.schema_version = '4'` и точная таблица
  `verses(verse_key, text, comment)`, где
  `comment TEXT NOT NULL DEFAULT ''`.

Target schema fingerprint:
`b46dc7c39ddf8ec5d4ccbbf80d774dd94505baf7f43c33250869852ad0950954`.
Legacy schema fingerprint остался
`e14d4e2b2727122240f3765104cf4e2d63f789d5904be6aa3766cf761f5583b8`.

Генератор читает оба фактических legacy-файла, но только read-only, и
фиксирует их независимо от целевой украинской схемы. Contract-тесты
отрицательными мутациями подтверждают отказ при schema version 3 у
украинского профиля, schema version 4/`comment` у legacy-профиля, отсутствии
или изменении точного столбца `comment` и смешении профилей. Прежние ключи,
идентификаторы, metadata, info templates, целевая сетка и Strong-контракт
остаются зафиксированными.

## Неизменность legacy SQLite

До и после изменений попарно совпадают копии в `web/db` и
`%Documents%/revelation/db`:

| Файл | Размер | SHA-256 | Схема |
| --- | ---: | --- | ---: |
| `bible_kjv.sqlite` | 6 733 824 | `b105f174c37c6703b71831a99ff838fed3439b84132c743bd3b58b37a326c780` | 3 |
| `bible_lxx_tr.sqlite` | 12 840 960 | `443ab95f6fe54c3a803665e935a21bb862cdc97346ace6fa03d1d9c100bf3926` | 3 |

Файлы не пересобирались и не редактировались; столбца `comment` в них нет.

## Исправленная общая тестовая регрессия

Обязательный полный Python discovery первоначально воспроизвёл три старых
сбоя `test_apply_extended_strong_descriptions.py`: fixtures ожидали успешное
применение `G6000/G20833`, хотя актуальные content-tool ranges после удаления
extended Strong заканчиваются на `G5624`. Quality gate не был ослаблен и сбой
не был принят как допустимый. Три устаревших сценария переписаны под текущий
fail-closed контракт и теперь проверяют, что удалённые extended ranges
отклоняются до изменения локализованных БД. Runtime-код не менялся.

## Выполненные команды

| Команда | Результат |
| --- | --- |
| `python -m scripts.bible_module.generate_ukrainian_stage_2_baseline --check` | PASS; baseline и CSV точно воспроизводятся |
| `python -m unittest scripts.bible_module.tests.test_ukrainian_stage_2_contract` | PASS; 11 тестов |
| `python -m scripts.bible_module.ukrainian_stage_3_sources --check` | PASS; неизменённый lock, 14 cache-файлов и footnote-source evidence совпали |
| `python -m unittest scripts.bible_module.tests.test_sources scripts.bible_module.tests.test_ukrainian_stage_3_sources` | PASS; 14 тестов |
| `python -m unittest discover -s scripts/bible_module/tests` | PASS; 121 тест |
| `python -m unittest discover -s scripts/content_tool/tests` | PASS; 30 тестов |
| `python -m compileall -q ...` для изменённых Python-файлов | PASS |
| `dart format .` | PASS; 475 файлов, 0 изменений |
| `flutter analyze` | PASS; `No issues found`, 31,4 с |
| `flutter test` | PASS; 920 тестов |
| `dart run scripts/check_forbidden_patterns.dart` | PASS |
| `dart run scripts/check_docs_sync.dart` | PASS; все обязательные RU/EN пары синхронны |
| `git diff --check` | PASS |

Integration smoke и coverage не запускались: runtime, маршруты, deep links,
state management и пользовательские сценарии не менялись; roadmap прямо
оставляет реализацию/проверку комментариев в content tool и Flutter на этапы
9–10. Новая локализация, зависимости и acknowledgements не требовались.

## Выход

Точный schema contract версии 4, целевой baseline и контракт комментариев
зафиксированы и автоматически проверяются. Фактические legacy-модули версии 3
изолированы от целевого профиля и не изменены. Этап 2 повторно закрыт; после
read-only перепроверки уже закрытого этапа 3 следующим разрешён этап 4.
