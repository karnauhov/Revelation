# Стратегия тестирования (RU)

Doc-Version: `2.0.0`  
Last-Updated: `2026-03-28`  
Source-Commit: `working-tree`

## Назначение

Определить текущую тестовую базу проекта Revelation.

## Слои тестов

- Unit-тесты лежат в `test/` и покрывают cubit-ы, сервисы, репозитории, router-контракты и shared helper-ы.
- Widget-тесты проверяют поведение экранов и виджетов. При необходимости слой можно запускать отдельно через теги.
- Smoke integration-тесты лежат в `integration_test/smoke/`.
- Общие test helper-ы описаны в [`test/test_harness/README.md`](../../../test/test_harness/README.md).

## Базовые локальные проверки

```bash
dart format .
flutter analyze
flutter test
flutter test --tags widget
dart run scripts/check_forbidden_patterns.dart
dart run scripts/check_docs_sync.dart
```

`dart run scripts/check_docs_sync.dart` запускается, когда меняется синхронизируемая RU/EN пара документов.

## Автоматизация

- `.github/workflows/flutter_build.yml` повторяет форматирование, анализ, тесты, фильтрацию coverage и проверки forbidden patterns.
- `.github/workflows/integration_smoke.yml` запускает smoke-suite на Android по расписанию или вручную.

## Правила качества

- Новое поведение и исправления ошибок должны приходить с ближайшим релевантным unit- или widget-тестом.
- Тесты должны использовать deterministic fake/stub зависимости и не зависеть от внешней сети.
- Для high-risk state-потоков нужны сценарии на:
  - stale async race (`latest request wins`)
  - lifecycle safety (`close before async completes`)
  - rapid switching в image-preview потоках primary source
