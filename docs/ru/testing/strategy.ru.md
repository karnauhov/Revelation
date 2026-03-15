# Testing Strategy (RU)

Doc-Version: `1.0.2`  
Last-Updated: `2026-03-15`  
Source-Commit: `working-tree`

## 1. Purpose
Определить обязательную стратегию тестирования для текущей архитектуры Revelation.

## 2. Test Suites
- Unit: `test/` (cubit, router args, async guards, domain/service логика).
- Widget: `test/widget/` с тегом `@Tags(['widget'])`.
- Integration smoke: `integration_test/smoke/` (ручной запуск workflow).
- Harness: `test/test_harness/` с `fake_env`, `fake_logger`, `fake_remote`.

## 3. Mandatory Local Checks
```bash
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test --exclude-tags widget
flutter test --tags widget
flutter test --coverage
dart run scripts/coverage_baseline.dart --min-all=90.0
dart run scripts/check_forbidden_patterns.dart
```

## 4. CI Gates
- `.github/workflows/flutter_build.yml`:
  - format check
  - analyze
  - unit tests
  - widget tests
  - coverage + thresholds
  - forbidden patterns
- `.github/workflows/integration_smoke.yml`:
  - запускается только через `workflow_dispatch`
  - выполняет `flutter test integration_test/smoke` на Android emulator.

## 5. Test Quality Rules
- Изменения в cubit/repository/router должны сопровождаться релевантными unit или widget тестами.
- Для исправлений дефектов добавляется regression-тест.
- Тесты не должны зависеть от внешней сети или нестабильного времени выполнения.
- Для UI-сценариев используются deterministic fake/stub зависимости.
- Для state-management изменений в high-risk потоках обязательны regression-сценарии:
  - stale async race (`latest request wins`);
  - lifecycle safety (`close before async completes`);
  - detail image-preview rapid-switch (stale geometry и call-count side effects).

## 6. Done Criteria
- Все обязательные проверки из разделов 3 и 4 проходят.
- Для изменений в RU/EN документах выполнен `dart run scripts/check_docs_sync.dart`.
