# Phase P03 - Structural Test Normalization (RU)

Дата фиксации: **March 15, 2026**.

## 1) Выполненные изменения структуры `test/`

### 1.1 Перенос misplaced тестов в feature-aligned пути

- `test/utils/pronunciation_test.dart`
  -> `test/features/primary_sources/application/services/pronunciation_service_test.dart`

### 1.2 Нормализация путей widget-тестов (синхронизация с `lib/features/**/presentation/**`)

- `test/widget/primary_sources/detail/image_preview_test.dart`
  -> `test/features/primary_sources/presentation/widgets/image_preview_test.dart`
- `test/widget/primary_sources/detail/primary_source_detail_widgets_test.dart`
  -> `test/features/primary_sources/presentation/widgets/primary_source_detail_widgets_test.dart`
- `test/widget/primary_sources/primary_sources_screen_test.dart`
  -> `test/features/primary_sources/presentation/screens/primary_sources_screen_test.dart`
- `test/widget/settings/settings_screen_test.dart`
  -> `test/features/settings/presentation/screens/settings_screen_test.dart`
- `test/widget/topics/topic_list_test.dart`
  -> `test/features/topics/presentation/widgets/topic_list_test.dart`

### 1.3 Cleanup legacy каталогов

- удалены пустые legacy директории:
  - `test/widget/`
  - `test/utils/`

## 2) Нормализация тегирования widget-тестов

Добавлен `@Tags(['widget'])` в файлы, где есть `testWidgets`, но тег отсутствовал:

- `test/shared/navigation/app_link_handler_test.dart`
- `test/features/primary_sources/presentation/bloc/primary_source_description_cubit_test.dart`

Итог:
- все файлы с `testWidgets` в текущем дереве `test/` имеют `@Tags(['widget'])`.

## 3) Review naming convention

- Файлы после переносов оставлены в формате `*_test.dart`.
- Пути тестов приведены к feature-first структуре и синхронизированы с зонами production-кода (`application/presentation/screens/widgets`).

## 4) Валидация фазы

Выполнены команды:

```bash
flutter test --exclude-tags widget
flutter test --tags widget
```

Результат:
- обе команды завершились успешно (`All tests passed`).

## 5) Статус checklist P03

- [x] Перенести misplaced тесты в feature-aligned пути.
- [x] Нормализовать `@Tags(['widget'])` для всех `testWidgets`.
- [x] Удалить/архивировать dead/stale тест-файлы и legacy-структуру.
- [x] Проверить naming convention тестов.
