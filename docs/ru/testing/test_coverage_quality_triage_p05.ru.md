# Phase P05 - Existing Tests Quality Triage (RU)

Дата фиксации: **March 15, 2026**.

## 1) Что сделано в фазе

### 1.1 Точечное усиление слабых assert-паттернов

- Убраны слабые `isNotNull`-проверки там, где можно проверять точный контракт/тип:
  - `test/app/router/route_args_test.dart`
  - `test/features/about/presentation/bloc/about_cubit_test.dart`
  - `test/features/settings/presentation/bloc/settings_cubit_test.dart`
  - `test/features/primary_sources/presentation/bloc/primary_sources_cubit_test.dart`
  - `test/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit_test.dart`
  - `test/features/topics/presentation/bloc/topic_content_cubit_test.dart`
  - `test/features/topics/presentation/bloc/topics_catalog_cubit_test.dart`
  - `test/test_harness/revelation_test_harness_test.dart`

### 1.2 Устранение недетерминизма

- Интеграционные smoke-тесты переведены на bounded-settle helper с явным timeout:
  - добавлен `integration_test/smoke/smoke_test_harness.dart`
  - обновлены все `integration_test/smoke/*_test.dart`
- Убрана зависимость widget-теста от файловой системы/ассетов:
  - `test/features/primary_sources/presentation/widgets/image_preview_test.dart`
  - вместо чтения `assets/images/**` используется встроенный deterministic PNG byte-array.

### 1.3 Закрытие списка `rewrite later` (follow-up в рамках P05)

Дополнительно в этом же цикле закрыты пункты, которые были изначально вынесены в `rewrite later`:
- `test/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit_test.dart`
  - wall-clock debounce ожидание заменено на `fake_async` (`elapse`) без реального ожидания.
- `test/features/primary_sources/presentation/bloc/primary_source_viewport_cubit_test.dart`
  - убраны microtask-flush ожидания, проверки переписаны на state-based dedup контракты.
- `test/features/primary_sources/presentation/widgets/primary_source_detail_widgets_test.dart`
  - убран `warnIfMissed: false`; отключенная навигация теперь проверяется через `IgnorePointer` contract.
- `integration_test/smoke/settings_topics_language_sync_smoke_test.dart`
  - убран hardcoded UI-текст для языка; используется источник из `AppConstants.languages['ru']`.

---

## 2) Полная классификация текущих тестов (keep/strengthen/rewrite/remove)

| Test file | Status | Краткая оценка | Action |
|---|---|---|---|
| `test/app/router/route_args_test.dart` | strengthen (done) | Контракты роут-аргументов, добавлен edge-case blank file | keep |
| `test/core/async/latest_request_guard_test.dart` | keep | Четкий behavioral contract latest-token | keep |
| `test/features/about/presentation/bloc/about_cubit_test.dart` | strengthen (done) | Ошибки проверяются по точному `AppFailure` | keep |
| `test/features/primary_sources/application/services/pronunciation_service_test.dart` | keep | Высокая регрессионная ценность словаря/локалей | keep |
| `test/features/primary_sources/presentation/bloc/primary_source_description_cubit_test.dart` | keep | Поведенческие переходы состояния покрыты | keep |
| `test/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit_test.dart` | strengthen (done) | debounce-проверка переведена на `fake_async` | keep |
| `test/features/primary_sources/presentation/bloc/primary_source_image_cubit_test.dart` | keep | Контракты loading/replace/keep покрыты | keep |
| `test/features/primary_sources/presentation/bloc/primary_source_image_state_test.dart` | keep | Иммутабельность state защищена | keep |
| `test/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit_test.dart` | strengthen (done) | Убрана слабая nullable-проверка save-call | keep |
| `test/features/primary_sources/presentation/bloc/primary_source_session_cubit_test.dart` | keep | Базовые session-контракты корректны | keep |
| `test/features/primary_sources/presentation/bloc/primary_source_viewport_cubit_test.dart` | strengthen (done) | dedup-контракт проверяется без microtask-задержек | keep |
| `test/features/primary_sources/presentation/bloc/primary_sources_cubit_test.dart` | strengthen (done) | Failure assertions усилены до точных контрактов | keep |
| `test/features/primary_sources/presentation/bloc/primary_sources_expansion_cubit_test.dart` | keep | Contract narrow и достаточный | keep |
| `test/features/primary_sources/presentation/bloc/primary_sources_state_test.dart` | keep | Иммутабельность коллекций покрыта | keep |
| `test/features/primary_sources/presentation/screens/primary_sources_screen_test.dart` | keep | State-rendering/interaction покрыты, ценность высокая | keep |
| `test/features/primary_sources/presentation/widgets/image_preview_test.dart` | strengthen (done) | Убрана asset/filesystem зависимость | keep |
| `test/features/primary_sources/presentation/widgets/primary_source_detail_widgets_test.dart` | strengthen (done) | убран `warnIfMissed: false`, проверен disabled-nav contract | keep |
| `test/features/settings/presentation/bloc/settings_cubit_test.dart` | strengthen (done) | Failure assertions усилены до точных контрактов | keep |
| `test/features/settings/presentation/screens/settings_screen_test.dart` | keep | Полезный UI contract + persistence side-effect | keep |
| `test/features/topics/presentation/bloc/topic_content_cubit_test.dart` | strengthen (done) | Failure assertions усилены | keep |
| `test/features/topics/presentation/bloc/topics_catalog_cubit_test.dart` | strengthen (done) | Failure/icon assertions усилены | keep |
| `test/features/topics/presentation/bloc/topics_catalog_state_test.dart` | keep | Иммутабельность state-контракта | keep |
| `test/features/topics/presentation/widgets/topic_list_test.dart` | keep | Loading/error/content states покрыты | keep |
| `test/shared/navigation/app_link_handler_test.dart` | keep | Контракт fallback/default callback корректен | keep |
| `test/test_harness/revelation_test_harness_test.dart` | strengthen (done) | Убрана weak nullable-проверка bytes | keep |
| `integration_test/smoke/about_download_navigation_smoke_test.dart` | strengthen (done) | bounded settle + стабильнее | keep |
| `integration_test/smoke/primary_sources_navigation_smoke_test.dart` | strengthen (done) | bounded settle + более точный finder-contract | keep |
| `integration_test/smoke/settings_topics_language_sync_smoke_test.dart` | strengthen (done) | убран hardcoded язык, bounded settle | keep |

Итог классификации:
- keep: 18
- strengthen (done): 10
- rewrite later: 0
- remove: 0

---

## 3) Проверка недетерминизма

Закрыто в P05:
- исключены неограниченные `pumpAndSettle` в integration smoke;
- исключена зависимость от реального ассета/файловой системы в `image_preview_test`;
- исключено wall-clock ожидание debounce в orchestration cubit тесте;
- исключены microtask-flush ожидания в viewport cubit dedup тестах.

Остаток в рамках P05: `none`.

---

## 4) Rewrite Later Backlog

`rewrite later` backlog по P05 закрыт полностью в follow-up.

---

## 5) Валидация фазы

Команды:

```bash
flutter analyze
flutter test
flutter test integration_test/smoke
```

Результат:
- `flutter analyze` — успешно.
- `flutter test` — успешно.
- `flutter test integration_test/smoke` — успешно (`All tests passed`).

---

## 6) Статус checklist P05

- [x] Классифицировать тесты по ценности регресс-защиты.
- [x] Усилить слабые asserts (behavior over implementation).
- [x] Убрать недетерминизм (assets/time/network dependencies) в пределах безопасного P05 scope.
- [x] Зафиксировать backlog “rewrite later” отдельно.
