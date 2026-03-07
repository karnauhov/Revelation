# Миграция Primary Sources в БД

Последнее обновление: 2026-03-07
Статус: Фаза 5 завершена

## Цель

Перенести данные, которые сейчас захардкожены в
`lib/repositories/primary_sources_repository.dart`, в существующую схему БД:

- общая БД: `revelation.sqlite`
- локализованные БД: `revelation_<lang>.sqlite`

Миграция должна сохранить текущее поведение приложения, добавить полную CRUD-
поддержку первоисточников в `scripts/content_tool.py` и хранить прогресс работ
в одном месте, чтобы миграцию можно было безопасно продолжить в следующем
сеансе или из другого чата.

## Зафиксированные решения

- Добавить `primary_source_link_texts` в каждую локализованную БД.
- Общие UI-строки оставить в ARB-файлах.
- Preview-картинки перенести в DB resources, чтобы новый первоисточник можно
  было добавить без выпуска новой версии приложения.
- Полные page images не хранить в SQLite; в БД хранить только пути к ним и
  сохранить текущую схему скачивания/кеширования для полноразмерных изображений.
- Встроить workflow contour editor в `scripts/content_tool.py`.
- Переделать contour editor так, чтобы он читал и записывал данные напрямую в
  таблицы БД.
- Добавить в `content_tool.py` кнопки скачивания page images в ту же локальную
  папку, которую ожидает приложение.
- Для ссылок использовать стабильный `link_id`, а не `sort_order`, чтобы можно
  было безопасно менять порядок ссылок без поломки локализованных заголовков.
- Для строк атрибуции использовать стабильный `attribution_id`, чтобы можно
  было безопасно менять порядок и редактировать записи в UI.

## Инварианты путей

Текущая логика приложения рассчитывает, что все лежит внутри:

- `%Documents%/revelation/db`
- `%Documents%/revelation/primary_sources`

На текущей машине это ожидается как:

- `C:\Users\karna\OneDrive\Documents\revelation\db`
- `C:\Users\karna\OneDrive\Documents\revelation\primary_sources`

Важно:

- файлы БД лежат в `db`
- локально скачанные/закешированные page images лежат в соседней папке
  `primary_sources`
- действия скачивания картинок в `content_tool.py` должны использовать ту же
  логику путей, что и Flutter-приложение:
  `getApplicationDocumentsDirectory()/revelation/...`

## Текущий контракт данных, который нужно сохранить

Текущий источник истины до миграции:

- всего 19 первоисточников
- 3 полных (`full`)
- 4 значительных (`significant`)
- 12 фрагментарных (`fragment`)
- всего 232 страницы
- всего 156 слов
- всего 172 прямоугольника
- всего 8 verse-overlay записей
- 13 источников с `permissionsReceived = true`
- 6 источников с `permissionsReceived = false`
- 2 источника вообще без страниц: `U025`, `U052`
- только 3 источника сейчас содержат разметку слов/стихов: `U001`, `U002`,
  `U004`

Эти числа нужно повторно проверить после импорта и после перевода приложения на
DB-backed репозиторий.

## Что остается вне БД

Оставить в ARB:

- `primary_sources_screen`
- `primary_sources_header`
- `full_primary_sources`
- `significant_primary_sources`
- `fragments_primary_sources`
- `show_more`
- `hide`
- `verses`
- `wikipedia`
- `intf`
- `image_source`

Оставить вне SQLite:

- полноразмерные page images

Перенести в БД:

- preview images через `common_resources`
- весь source-specific локализованный контент, который сейчас привязан к
  первоисточникам

## Целевая схема

### Общая БД: `revelation.sqlite`

#### `primary_sources`

- `id TEXT PRIMARY KEY`
- `family TEXT NOT NULL`
- `number INTEGER NOT NULL`
- `group_kind TEXT NOT NULL`
- `sort_order INTEGER NOT NULL`
- `verses_count INTEGER NOT NULL`
- `preview_resource_key TEXT NOT NULL`
- `default_max_scale REAL NOT NULL`
- `can_show_images INTEGER NOT NULL`
- `images_are_monochrome INTEGER NOT NULL`
- `notes TEXT NOT NULL DEFAULT ''`

Примечания:

- `id` это стабильный код рукописи, например `U001`, `P115`
- `group_kind` заменяет текущее деление на три метода репозитория
- `preview_resource_key` указывает на `common_resources`
- `can_show_images` это будущий DB-аналог `permissionsReceived`

#### `primary_source_links`

- `source_id TEXT NOT NULL`
- `link_id TEXT NOT NULL`
- `sort_order INTEGER NOT NULL`
- `link_role TEXT NOT NULL`
- `url TEXT NOT NULL`
- primary key: `(source_id, link_id)`

Примечания:

- `link_id` это стабильный идентификатор строки ссылки внутри источника,
  например `wiki`, `intf`, `image`, `link_1`
- `sort_order` отвечает только за порядок отображения
- `link_role` ожидается одним из: `wikipedia`, `intf`, `image_source`,
  `external`
- общие заголовки ссылок берутся из ARB, если нет явного override в
  локализованной БД

#### `primary_source_attributions`

- `source_id TEXT NOT NULL`
- `attribution_id TEXT NOT NULL`
- `sort_order INTEGER NOT NULL`
- `text TEXT NOT NULL`
- `url TEXT NOT NULL`
- primary key: `(source_id, attribution_id)`

Примечания:

- `attribution_id` это стабильный идентификатор строки атрибуции внутри
  источника
- `sort_order` отвечает только за порядок отображения

#### `primary_source_pages`

- `source_id TEXT NOT NULL`
- `page_name TEXT NOT NULL`
- `sort_order INTEGER NOT NULL`
- `content_ref TEXT NOT NULL`
- `image_path TEXT NOT NULL`
- `mobile_image_path TEXT`
- primary key: `(source_id, page_name)`

Примечания:

- `image_path` остается каноническим storage path, который использует приложение
- `mobile_image_path` позволяет явно задать mobile override вместо того, чтобы
  полагаться только на соглашение с суффиксом `_mb`

#### `primary_source_words`

- `source_id TEXT NOT NULL`
- `page_name TEXT NOT NULL`
- `word_index INTEGER NOT NULL`
- `text TEXT NOT NULL`
- `strong_number INTEGER`
- `strong_pronounce INTEGER NOT NULL`
- `strong_x_shift REAL NOT NULL`
- `missing_char_indexes_json TEXT NOT NULL`
- `rectangles_json TEXT NOT NULL`
- primary key: `(source_id, page_name, word_index)`

Примечания:

- `missing_char_indexes_json` хранит текущий массив `notExist`
- `rectangles_json` хранит текущий список значений `PageRect(...)`

#### `primary_source_verses`

- `source_id TEXT NOT NULL`
- `page_name TEXT NOT NULL`
- `verse_index INTEGER NOT NULL`
- `chapter_number INTEGER NOT NULL`
- `verse_number INTEGER NOT NULL`
- `label_x REAL NOT NULL`
- `label_y REAL NOT NULL`
- `word_indexes_json TEXT NOT NULL`
- `contours_json TEXT NOT NULL`
- primary key: `(source_id, page_name, verse_index)`

Примечания:

- `word_indexes_json` хранит текущий `wordIndexes`
- `contours_json` хранит текущие polygon contours

### Локализованные БД: `revelation_<lang>.sqlite`

#### `primary_source_texts`

- `source_id TEXT PRIMARY KEY`
- `title_markup TEXT NOT NULL`
- `date_label TEXT NOT NULL`
- `content_label TEXT NOT NULL`
- `material_text TEXT NOT NULL`
- `text_style_text TEXT NOT NULL`
- `found_text TEXT NOT NULL`
- `classification_text TEXT NOT NULL`
- `current_location_text TEXT NOT NULL`

Примечания:

- `title_markup` должен сохранять текущую разметку `<sup>`

#### `primary_source_link_texts`

- `source_id TEXT NOT NULL`
- `link_id TEXT NOT NULL`
- `title TEXT NOT NULL`
- primary key: `(source_id, link_id)`

Примечания:

- эта таблица обязательна по принятому решению
- для текущего датасета она может оставаться пустой для стандартных ролей и
  использоваться как override-таблица там, где это понадобится

## Точный SQL DDL Фазы 1

### `revelation.sqlite`

```sql
CREATE TABLE IF NOT EXISTS primary_sources (
  id TEXT NOT NULL PRIMARY KEY,
  family TEXT NOT NULL,
  number INTEGER NOT NULL,
  group_kind TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  verses_count INTEGER NOT NULL DEFAULT 0,
  preview_resource_key TEXT NOT NULL,
  default_max_scale REAL NOT NULL DEFAULT 3.0,
  can_show_images INTEGER NOT NULL DEFAULT 1,
  images_are_monochrome INTEGER NOT NULL DEFAULT 0,
  notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS primary_source_links (
  source_id TEXT NOT NULL,
  link_id TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  link_role TEXT NOT NULL,
  url TEXT NOT NULL,
  PRIMARY KEY (source_id, link_id)
);

CREATE TABLE IF NOT EXISTS primary_source_attributions (
  source_id TEXT NOT NULL,
  attribution_id TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  text TEXT NOT NULL,
  url TEXT NOT NULL,
  PRIMARY KEY (source_id, attribution_id)
);

CREATE TABLE IF NOT EXISTS primary_source_pages (
  source_id TEXT NOT NULL,
  page_name TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  content_ref TEXT NOT NULL,
  image_path TEXT NOT NULL,
  mobile_image_path TEXT,
  PRIMARY KEY (source_id, page_name)
);

CREATE TABLE IF NOT EXISTS primary_source_words (
  source_id TEXT NOT NULL,
  page_name TEXT NOT NULL,
  word_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  strong_number INTEGER,
  strong_pronounce INTEGER NOT NULL DEFAULT 0,
  strong_x_shift REAL NOT NULL DEFAULT 0.0,
  missing_char_indexes_json TEXT NOT NULL DEFAULT '[]',
  rectangles_json TEXT NOT NULL DEFAULT '[]',
  PRIMARY KEY (source_id, page_name, word_index)
);

CREATE TABLE IF NOT EXISTS primary_source_verses (
  source_id TEXT NOT NULL,
  page_name TEXT NOT NULL,
  verse_index INTEGER NOT NULL,
  chapter_number INTEGER NOT NULL,
  verse_number INTEGER NOT NULL,
  label_x REAL NOT NULL,
  label_y REAL NOT NULL,
  word_indexes_json TEXT NOT NULL DEFAULT '[]',
  contours_json TEXT NOT NULL DEFAULT '[]',
  PRIMARY KEY (source_id, page_name, verse_index)
);
```

### `revelation_<lang>.sqlite`

```sql
CREATE TABLE IF NOT EXISTS primary_source_texts (
  source_id TEXT NOT NULL PRIMARY KEY,
  title_markup TEXT NOT NULL,
  date_label TEXT NOT NULL,
  content_label TEXT NOT NULL,
  material_text TEXT NOT NULL,
  text_style_text TEXT NOT NULL,
  found_text TEXT NOT NULL,
  classification_text TEXT NOT NULL,
  current_location_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS primary_source_link_texts (
  source_id TEXT NOT NULL,
  link_id TEXT NOT NULL,
  title TEXT NOT NULL,
  PRIMARY KEY (source_id, link_id)
);
```

## План работ по фазам

### Фаза 0. Runbook и baseline

- [x] Согласовать направление схемы и ограничения миграции
- [x] Добавить отдельный migration ledger
- [x] Зафиксировать точные baseline counts отдельным скриптом и отразить их в
      этом файле
- [x] Добавить в конец файла секцию session log для продолжения работ

### Фаза 1. Схема БД

- [x] Добавить новые common tables в `lib/db/db_common.dart`
- [x] Добавить новые localized tables в `lib/db/db_localized.dart`
- [x] Поднять версии схем
- [x] Добавить Drift migrations для существующих файлов БД
- [x] Расширить DDL-хелперы в `content_tool.py` для common и localized БД
- [x] Записать финальный SQL DDL в этот файл для справки

### Фаза 2. Одноразовый импортёр

- [x] Создать отдельный скрипт миграции/импорта
- [x] Добавить dry-run/apply режимы и backup целевых БД перед записью
- [x] Распарсить `primary_sources_repository.dart`
- [x] Распарсить `app_en.arb`, `app_es.arb`, `app_uk.arb`, `app_ru.arb`
- [x] Импортировать common rows в `revelation.sqlite`
- [x] Импортировать localized rows во все `revelation_<lang>.sqlite`
- [x] Импортировать preview images в `common_resources`
- [x] Сформировать validation report по source/page/word/verse counts

### Фаза 3. Переключение приложения на БД

- [x] Ввести DB-backed репозиторий первоисточников
- [x] Убрать зависимость загрузки данных от `BuildContext`
- [x] Переделать `PrimarySourceReferenceResolver`, чтобы он резолвил данные из БД
- [x] Сделать `PrimarySourcesViewModel.loadPrimarySources()` асинхронным
- [x] Оставить старый репозиторий только как временный fallback до завершения
      валидации
- [ ] Удалить старые hardcoded данные после финальной проверки

### Фаза 4. Раздел первоисточников в `content_tool.py`

- [x] Добавить новый верхнеуровневый раздел/вкладку `Первоисточники` (проверить если она уже есть)
- [x] Добавить список источников с поиском и фильтрами по `group_kind`
- [x] Добавить индикаторы полноты локализаций для `en`, `es`, `uk`, `ru`
- [x] Добавить редактор common metadata источника
- [x] Добавить редактор локализованных текстов для текущей выбранной БД
- [x] Добавить редактор ссылок
- [x] Добавить редактор атрибуции/rights
- [x] Добавить редактор страниц
- [x] Добавить редактор слов для выбранной страницы
- [x] Добавить редактор стихов для выбранной страницы
- [x] Добавить потоки сохранения/удаления с согласованной записью в common и
      localized БД
- [x] Добавить validation warnings для дублирующихся IDs, дублирующихся page
      names, некорректного JSON, отсутствующих preview resources, отсутствующих
      image paths и конфликтующего sort order

### Фаза 5. Интеграция contour editor

- [x] Перенести workflow contour editor внутрь `content_tool.py`
- [x] Убрать зависимость от вставки `Verse(...)` snippets как основного сценария
      редактирования
- [x] Загружать verse contour data напрямую из `primary_source_verses`
- [x] Сохранять изменения contours напрямую обратно в БД
- [x] Оставить import/export helper для `Verse(...)` текста только как
      дополнительную утилиту
- [x] Добавить точки входа из выбранных source/page/verse строк в contour UI

### Фаза 6. Кнопки скачивания изображений в `content_tool.py`

- [ ] Добавить кнопку на уровне источника для скачивания всех страниц выбранного
      первоисточника
- [ ] Добавить кнопку на уровне страницы для скачивания только выбранного
      изображения
- [ ] Добавить опцию принудительного перекачивания
- [ ] Сохранять файлы в `%Documents%/revelation/primary_sources/...`
- [ ] Использовать ту же структуру относительных путей, которую приложение
      ожидает из `page.image`
- [ ] Добавить статус-вывод для downloaded, skipped и failed файлов
- [ ] Добавить проверку, существует ли картинка страницы локально

### Фаза 7. Валидация

- [ ] Проверить количество источников
- [ ] Проверить количества по группам
- [ ] Проверить количество страниц
- [ ] Проверить количество слов
- [ ] Проверить количество прямоугольников
- [ ] Проверить количество verse overlays
- [ ] Проверить, что preview resources существуют для всех источников
- [ ] Проверить word/verse navigation для `U001`, `U002`, `U004`
- [ ] Проверить, что источники с `can_show_images = false` ведут себя так же,
      как раньше
- [ ] Проверить, что источники без страниц по-прежнему корректно отображаются
- [ ] Проверить, что все 4 локали загружают корректные source metadata

### Фаза 8. Очистка

- [ ] Удалить source-specific ARB keys после перехода на БД
- [ ] Удалить obsolete код из `primary_sources_repository.dart`
- [ ] Решить, оставлять ли standalone `contour_editor.py` или убрать его
- [ ] Обновить `DEV_INFO.md`, если изменится maintenance workflow
- [ ] Добавить финальные заметки по будущему добавлению новых источников

## Журнал сессий

### 2026-03-07

- Создан initial migration ledger
- Добавлен baseline-скрипт: `scripts/primary_sources_baseline_report.py`
- Зафиксированы baseline counts:
  - 19 sources
  - 3 full
  - 4 significant
  - 12 fragment
  - 232 pages
  - 156 words
  - 172 rectangles
  - 8 verses
  - zero-page sources: `U025`, `U052`
  - overlay sources: `U001`, `U002`, `U004`
- Зафиксированы решения:
  - `primary_source_link_texts`
  - preview images в БД
  - встраивание contour editor в `content_tool.py`
  - прямое чтение/запись contour data через БД
  - кнопки скачивания изображений в app-compatible папку
    `%Documents%/revelation/primary_sources`
- Выполнена Фаза 1 на уровне схем:
  - добавлены новые таблицы в `db_common.dart`
  - добавлены новые таблицы в `db_localized.dart`
  - подняты schema versions
  - добавлены Drift migrations
  - обновлен DDL в `content_tool.py`
  - точный SQL DDL зафиксирован в этом файле
- Выполнена Фаза 2:
  - добавлен одноразовый импортёр `scripts/migrate_primary_sources_to_db.py`
  - скрипт поддерживает `dry-run`, `--apply`, backup и DB-level validation
  - при `--apply` созданы backup-копии всех 5 SQLite-файлов в
    `C:\Users\karna\OneDrive\Documents\revelation\db\backups\primary_sources_phase2_20260307_055906`
  - импортированы common rows в `revelation.sqlite`
  - импортированы localized rows в `revelation_en.sqlite`,
    `revelation_es.sqlite`, `revelation_ru.sqlite`, `revelation_uk.sqlite`
  - импортированы 19 preview resources в `common_resources`
  - DB-level validation подтвердила baseline counts:
    - 19 sources
    - 3 full
    - 4 significant
    - 12 fragment
    - 232 pages
    - 156 words
    - 172 rectangles
    - 8 verses
    - zero-page sources: `U025`, `U052`
    - overlay sources: `U001`, `U002`, `U004`
  - `PRAGMA user_version` обновлен до `3` для `revelation.sqlite` и до `5`
    для всех `revelation_<lang>.sqlite`
- Выполнена Фаза 3:
  - добавлен DB-backed runtime-репозиторий
    `lib/repositories/primary_sources_db_repository.dart`
  - `DBManager` теперь кэширует `primary_source_*` таблицы из common и localized БД
  - `PrimarySourcesViewModel` переведен на асинхронную загрузку без
    `BuildContext`
  - `PrimarySourceReferenceResolver` больше не зависит от `BuildContext` и
    резолвит данные через БД
  - `main.dart` переключен на новый DB-backed репозиторий
  - список первоисточников теперь использует preview bytes из DB resources
    вместо `Image.asset(...)` для migrated sources
  - роли ссылок (`wikipedia`, `intf`, `image_source`) локализуются в UI, а не в
    data-layer
  - старый `lib/repositories/primary_sources_repository.dart` оставлен в проекте
    как временный fallback-артефакт до финальной cleanup-фазы
  - `flutter analyze` и `flutter test` прошли успешно после переключения
- Выполнена Фаза 4:
  - вместо placeholder-секции в `scripts/content_tool.py` собран полноценный
    раздел `Первоисточники`
  - добавлены поиск по источникам, фильтр по `group_kind` и индикаторы
    локализаций `en/es/uk/ru`
  - добавлен редактор common metadata источника и локализованных полей для
    текущей выбранной БД
  - добавлены CRUD-редакторы для links, attributions, pages, words и verses
  - удаление источника теперь каскадно синхронизирует common БД и все
    `revelation_<lang>.sqlite`
  - добавлена загрузка и предпросмотр preview resources прямо из
    `common_resources`
  - добавлены validation warnings по preview resources, пустым image paths,
    конфликтующим sort order и некорректному JSON
  - smoke-test `TopicContentTool(...)` на реальных БД успешно поднимает UI и
    читает 19 imported sources
  - `python -m py_compile scripts/content_tool.py` прошел успешно
- Выполнена Фаза 5:
  - standalone-логика из `scripts/contour_editor.py` перенесена в
    `PrimarySourceContourEditorDialog` внутри `scripts/content_tool.py`
  - editor теперь открывается из выбранной page/verse строки раздела
    `Первоисточники`
  - verse contour data загружаются напрямую из `primary_source_verses`
  - `Save to DB` пишет изменения обратно в `primary_source_verses` без
    промежуточного `Verse(...)` snippet workflow
  - import/export `Verse(...)` сохранен как вспомогательный инструмент внутри
    самого editor dialog
  - smoke-test на `U001` подтвердил открытие dialog и direct-save обратно в БД
