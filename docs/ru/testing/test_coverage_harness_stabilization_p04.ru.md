# Phase P04 - Harness Stabilization (RU)

Дата фиксации: **March 15, 2026**.

## 1) Выполненные изменения

### 1.1 Общие async/time helper-утилиты

Добавлен файл `test/test_harness/async_test_harness.dart`:
- `pumpFrames(...)` для стабильного пошагового `pump` без произвольных `Future.delayed`.
- `pumpAndSettleSafe(...)` c явными `step`/`timeout` для детерминированного ожидания widget-обновлений.

### 1.2 Стандартный app/context wrapper для widget-тестов

Добавлен файл `test/test_harness/widget_test_harness.dart`:
- `buildLocalizedTestApp(...)` для унифицированного `MaterialApp` с `AppLocalizations`.
- `pumpLocalizedContext(...)` для получения локализованного `BuildContext`.
- `pumpContext(...)` для базовых сценариев без локализации.

### 1.3 Нормализация повторяемых fake/mock builders

Добавлен shared fake:
- `test/test_harness/fakes/fake_settings_repository.dart`.

Подключен единый barrel:
- `test/test_harness/test_harness.dart`.

В существующих тестах удалены локальные дубли fake-репозитория и ручных wrapper-обвязок в пользу harness-утилит:
- `test/features/settings/presentation/screens/settings_screen_test.dart`
- `test/features/topics/presentation/widgets/topic_list_test.dart`
- `test/features/primary_sources/presentation/screens/primary_sources_screen_test.dart`
- `test/features/primary_sources/presentation/widgets/primary_source_detail_widgets_test.dart`
- `test/features/primary_sources/presentation/bloc/primary_source_description_cubit_test.dart`
- `test/shared/navigation/app_link_handler_test.dart`

### 1.4 Документация harness usage

Добавлен файл `test/test_harness/README.md` с:
- составом harness;
- минимальным примером использования;
- правилами переиспользования helper/fake без дублирования.

## 2) Валидация фазы

Выполнены команды:

```bash
flutter analyze
flutter test --exclude-tags widget
flutter test --tags widget
```

Результат:
- все команды завершены успешно;
- критичных предупреждений/ошибок нет;
- split widget/non-widget test execution сохраняется стабильным.

## 3) Статус checklist P04

- [x] Выделить повторяемые fake/mock builders из тестов.
- [x] Вынести time/async helper utilities для стабильных await flows.
- [x] Добавить стандартный app test wrapper для widget tests.
- [x] Документировать harness usage кратким README в `test_harness`.
