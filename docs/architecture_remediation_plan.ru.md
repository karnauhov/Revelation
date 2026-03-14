# План приведения архитектуры в порядок (чеклист)

Документ-статус: `рабочий`  
Версия плана: `1.0`  
Создан: `2026-03-14`  
Основание: архитектурный аудит после рефакторинга + актуальные практики Flutter/BLoC (feature-first, layer boundaries, test pyramid).

## 1. Выбранная стратегия по конфликтам «документация vs код»

Принято решение: **комбинированный вариант**.

Почему:
- По критичным инвариантам (направление зависимостей, запрет infra в presentation, immutable state) правильнее **следовать архитектурным правилам** и исправлять код.
- По спорным местам, где документация сейчас избыточно жесткая или конфликтует с фактической моделью (например, обязательность всех слоев для каждого feature, трактовка UI orchestration), правильнее **уточнить документацию** и синхронизировать RU/EN.
- По дублирующим/переходным решениям (legacy-остатки) нужен **и кодовый cleanup, и документирование итоговой модели**.

Решения по ключевым конфликтам:
- `core -> features` и `shared -> feature-specific logic`: **исправляем код** (критичное нарушение направления зависимостей).
- `presentation -> infra` в `topics`: **исправляем код**.
- Строгое требование «у каждого feature всегда `presentation/application/data`»: **уточняем документацию** (допускаем облегченный модуль для простых/stateless feature, но сохраняем правило границ там, где слой присутствует).
- Роль `ViewModel/Coordinator` в сложном UI: **уточняем документацию + убираем дубли** (сохраняем BLoC как source of truth состояния).
- Противоречие по `lib/main.dart`: **уточняем документацию** (entrypoint-файл в `lib/` допустим по контракту runtime).

## 2. Как работать с чеклистом

- Отмечать завершенные пункты через `[x]`.
- Не закрывать пункт без локальной проверки из блока `Проверка`.
- После закрытия фазы фиксировать результат в PR/коммите.

## 3. Приоритетный пошаговый план

### Фаза A. Критичные нарушения зависимостей (сначала)

- [x] `A1` Развязать `core/audio` от `features/settings`.
Файлы-кандидаты: `lib/core/audio/audio_controller.dart`, `lib/app/di/app_di.dart`, `lib/main.dart`, `lib/features/settings/...`.
Ожидаемый результат: `lib/core/**` больше не импортирует `package:revelation/features/...`.
Проверка: `rg -n "package:revelation/features/" lib/core`.

- [x] `A2` Убрать feature-specific orchestration из `shared/navigation`.
Файлы-кандидаты: `lib/shared/navigation/app_link_handler.dart`, `lib/features/primary_sources/application/services/primary_source_reference_resolver.dart`, `lib/app/router/...` или `lib/features/primary_sources/...`.
Ожидаемый результат: `shared` не зависит от feature-логики.
Проверка: `rg -n "package:revelation/features/" lib/shared`.

- [x] `A3` Убрать прямые импорты `infra` из `topics/presentation`.
Файлы-кандидаты: `lib/features/topics/presentation/bloc/topics_catalog_cubit.dart`, `lib/features/topics/presentation/bloc/topics_catalog_state.dart`, `lib/features/topics/presentation/screens/topic_screen.dart`, `lib/features/topics/presentation/widgets/topic_card.dart`, `lib/features/topics/data/repositories/topics_repository.dart`.
Ожидаемый результат: presentation опирается на feature-контракты/DTO, а не на `infra` типы.
Проверка: `rg -n --glob "lib/features/**/presentation/**/*.dart" "package:revelation/infra/" lib/features`.

### Фаза B. Корректная декомпозиция слоев внутри feature

- [x] `B1` Убрать обход `cubit` в `TopicScreen` (прямые вызовы repository из UI).
Файлы-кандидаты: `lib/features/topics/presentation/screens/topic_screen.dart`, `lib/features/topics/presentation/bloc/topic_content_cubit.dart`, `lib/features/topics/application/...` (при необходимости).
Ожидаемый результат: экран получает данные через cubit/application orchestration.
Проверка: code review + widget/unit tests для сценариев загрузки ресурсов.

- [x] `B2` Нормализовать orchestration в `primary_sources` и устранить дубли.
Файлы-кандидаты: `lib/features/primary_sources/presentation/controllers/primary_source_view_model.dart`, `lib/features/primary_sources/presentation/coordinators/primary_source_detail_coordinator.dart`, `lib/features/primary_sources/application/orchestrators/description_panel_orchestrator.dart`.
Ожидаемый результат: один консистентный orchestration path, без «мертвых» дубликатов.
Проверка: `rg -n "PrimarySourceDescriptionPanelOrchestrator|DescriptionPanelState" lib test`.

### Фаза C. Контракты state management

- [x] `C1` Усилить immutability состояний с коллекциями (`List/Map`).
Файлы-кандидаты: `lib/features/topics/presentation/bloc/topics_catalog_state.dart`, `lib/features/primary_sources/presentation/bloc/primary_sources_state.dart`, `lib/features/primary_sources/presentation/bloc/primary_source_image_state.dart`, сопутствующие cubit.
Ожидаемый результат: коллекции в state не мутируются извне.
Проверка: unit tests + ручная проверка `copyWith`/constructor semantics.

- [x] `C2` Проверить, что state ownership остается только в Cubit/BLoC.
Файлы-кандидаты: весь `lib/features/**/presentation`.
Ожидаемый результат: source of truth состояния не уходит в viewmodel/coordinator.
Проверка: архитектурный code review + `rg "package:provider|ChangeNotifier|notifyListeners" lib test`.

### Фаза D. Legacy cleanup

- [ ] `D1` Удалить пустые legacy/directories после миграции.
Файлы-кандидаты: `lib/features/about/presentation/viewmodels`, `lib/features/settings/presentation/viewmodels`, `lib/features/topics/presentation/viewmodels`, `lib/core/state`, `test/viewmodels` (если пустая).
Ожидаемый результат: отсутствуют переходные пустые папки.
Проверка: `Get-ChildItem -Path lib -Directory -Recurse` + `Get-ChildItem -Path test -Directory -Recurse`.

- [ ] `D2` Перепроверить отсутствие layer-first импортов/путей.
Ожидаемый результат: нет регрессии к legacy-структуре.
Проверка: `dart run scripts/check_forbidden_patterns.dart`.

### Фаза E. Тестовая стратегия и покрытие

- [ ] `E1` Добавить unit-тесты для `AboutCubit`.
Файлы-кандидаты: `test/features/about/presentation/bloc/about_cubit_test.dart`.
Ожидаемый результат: нет «висящих» cubit без unit coverage.
Проверка: `flutter test --exclude-tags widget`.

- [ ] `E2` Добавить regression-тесты на исправленные архитектурные баги.
Файлы-кандидаты: `test/features/...`, `test/app/router/...`, `test/widget/...` по факту правок.
Ожидаемый результат: ключевые сценарии зафиксированы тестами и не деградируют.
Проверка: `flutter test --exclude-tags widget` и `flutter test --tags widget`.

### Фаза F. Синхронизация архитектурной документации (RU/EN)

- [ ] `F1` Обновить RU/EN архитектурные документы по фактической целевой модели.
Обязательные пары:
- `docs/ru/architecture/overview.ru.md` <-> `docs/en/architecture/overview.en.md`
- `docs/ru/architecture/module-boundaries.ru.md` <-> `docs/en/architecture/module-boundaries.en.md`
- `docs/ru/architecture/state_management_matrix.ru.md` <-> `docs/en/architecture/state_management_matrix.en.md`
- `docs/ru/testing/strategy.ru.md` <-> `docs/en/testing/strategy.en.md` (если затронута тестовая политика)
Ожидаемый результат: нет конфликтов между документами и принятым кодом.

- [ ] `F2` Синхронизировать поля метаданных в RU/EN-парах.
Ожидаемый результат: `Doc-Version`, `Last-Updated`, `Source-Commit` совпадают в каждой паре.

- [ ] `F3` Проверить docs sync скриптом.
Проверка: `dart run scripts/check_docs_sync.dart`.

### Фаза G. Финальная валидация перед завершением

- [ ] `G1` Форматирование.
Проверка: `dart format .`

- [ ] `G2` Статический анализ.
Проверка: `flutter analyze`

- [ ] `G3` Unit + widget тесты.
Проверка:
- `flutter test --exclude-tags widget`
- `flutter test --tags widget`

- [ ] `G4` Архитектурные guardrails.
Проверка: `dart run scripts/check_forbidden_patterns.dart`

### Фаза N. Naming, форматирование и орфография

- [ ] `N1` Проверить snake_case для имен файлов (`lib/`, `test/`, `integration_test/`), исключая generated (`*.g.dart`, `app_localizations*.dart`).
Ожидаемый результат: все ручные Dart-файлы в lower_snake_case.
Проверка: выборка файлов + ручная ревизия исключений.

- [ ] `N2` Проверить именование классов/виджетов по Dart conventions.
Ожидаемый результат: `PascalCase` для типов, логичные имена без двусмысленности и legacy-терминов.
Проверка: ревизия сигнатур `class ...` в изменяемых модулях.

- [ ] `N3` Проверить консистентность суффиксов/ролей по слоям.
Ожидаемый результат:
- presentation state-management: `*Cubit`, `*State`
- presentation экраны: `*Screen`
- data слой: `*Repository`
- application orchestration/service: `*Orchestrator`, `*Service`
Проверка: точечный grep по именам классов и файлов в затронутых feature.

- [ ] `N4` Проверить орфографию и смысловую читаемость публичных имен.
Ожидаемый результат: нет опечаток/неясных сокращений в public API (классы, методы, поля state, route args, docs).
Проверка: ручная ревизия + при необходимости правки с регресс-тестами на переименованные контракты.

## 4. Definition of Done

- [ ] Критичные нарушения зависимостей устранены.
- [ ] Presentation слой не импортирует `infra` напрямую.
- [ ] Stateful логика остается в Cubit/BLoC, states иммутабельны.
- [ ] Legacy-остатки удалены.
- [ ] Проверка naming/суффиксов/орфографии пройдена и зафиксирована.
- [ ] Тестовое покрытие расширено (включая `AboutCubit` и regression-кейсы).
- [ ] RU/EN архитектурные документы синхронизированы и отражают фактическую целевую архитектуру.
- [ ] Все обязательные проверки проходят локально и в CI.
