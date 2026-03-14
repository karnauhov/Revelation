# Testing Strategy (RU)

Doc-Version: `0.4.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать проверяемую стратегию тестирования для безопасного архитектурного рефакторинга.

## 2. Current Baseline
- Unit tests: минимальный baseline (существующий набор smoke/unit).
- Widget tests: минимальный smoke baseline присутствует и запускается отдельно в PR CI.
- Integration smoke tests: отдельный suite в `integration_test/smoke` с ручным запуском workflow.
- Build quality gates (pre-build): `format + analyze + unit + widget + forbidden patterns` в `.github/workflows/flutter_build.yml`.

## 3. Target Test Pyramid
- Unit tests: 60-70%.
- Widget tests: 25-35%.
- Integration smoke: 5-10% (селективно).

## 4. Mandatory Gates
- Проверка форматирования: `dart format --output=none --set-exit-if-changed .`
- Статический анализ: `flutter analyze`
- Unit tests: `flutter test --exclude-tags widget`
- Widget tests: `flutter test --tags widget`
- Быстрые архитектурные grep-checks для forbidden patterns.

## 5. Test Harness Baseline
- Fake logger: для проверки side effects и ошибок без реального Talker.
- Fake env: для контролируемых значений окружения (например, SUPABASE defines).
- Fake remote: для эмуляции загрузок DB/файлов без внешней сети.

## 6. Regression Policy
- Любой P0 шаг считается завершенным только после analyze/tests.
- Новые архитектурные запреты включаются через baseline allowlist, чтобы блокировать новые нарушения без мгновенного “big bang” исправления legacy.
- По мере миграции allowlist должен уменьшаться.
- Integration smoke запускается только вручную через `workflow_dispatch`.
- CI выполнение integration smoke идет в отдельном workflow на Android emulator runner.

## 7. Execution Commands
```bash
dart format .
flutter analyze
flutter test --exclude-tags widget
flutter test --tags widget
flutter test integration_test/smoke
flutter test
dart run scripts/check_forbidden_patterns.dart
```
