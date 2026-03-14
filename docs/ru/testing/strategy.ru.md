# Testing Strategy (RU)

Doc-Version: `0.4.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Определить верифицируемую стратегию тестирования для безопасного архитектурного рефакторинга.

## 2. Current Baseline
- Unit tests: минимальный baseline (существующий набор smoke/unit тестов).
- Widget tests: существует минимальный smoke baseline и запускается как отдельный обязательный CI gate.
- Integration smoke tests: выделенный набор в `integration_test/smoke` с ручным запуском workflow.
- Build quality gates (pre-build): `format + analyze + unit + widget + forbidden patterns` в `.github/workflows/flutter_build.yml`.

## 3. Target Test Pyramid
- Unit tests: 60-70%.
- Widget tests: 25-35%.
- Integration smoke: 5-10% (выборочно).

## 4. Mandatory Gates
- Проверка форматирования: `dart format --output=none --set-exit-if-changed .`
- Статический анализ: `flutter analyze`
- Unit tests: `flutter test --exclude-tags widget`
- Widget tests: `flutter test --tags widget`
- Быстрые архитектурные grep-проверки на запрещенные паттерны.

## 5. Test Harness Baseline
- Fake logger: проверять side effects и error paths без реального Talker.
- Fake env: обеспечивать детерминированные значения окружения (например, SUPABASE defines).
- Fake remote: эмулировать загрузки DB/файлов без внешней сети.

## 6. Regression Policy
- Любая задача P0 считается завершенной только после успешных analyze/tests.
- Новые архитектурные ограничения сначала вводятся через baseline allowlist, чтобы блокировать новые нарушения без немедленного breaking legacy.
- Allowlist должен уменьшаться по мере миграции.
- Integration smoke запускается только вручную через `workflow_dispatch`.
- CI-исполнение integration smoke идет в отдельном workflow на Android emulator runner.

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
