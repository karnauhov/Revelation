# Testing Strategy (RU)

Doc-Version: `0.1.0`  
Last-Updated: `2026-03-08`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать проверяемую стратегию тестирования для безопасного архитектурного рефакторинга.

## 2. Current Baseline
- Unit tests: минимальный baseline (существующий набор smoke/unit).
- Widget tests: минимальный smoke baseline присутствует и запускается отдельно в PR CI.
- Integration tests: отсутствуют в регулярном цикле.
- PR quality gates: `format + analyze + unit + widget + forbidden patterns` на PR в `main`.

## 3. Target Test Pyramid
- Unit tests: 60-70%.
- Widget tests: 25-35%.
- Integration smoke: 5-10% (селективно).

## 4. Phase 0 Mandatory Gates
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

## 7. Execution Commands
```bash
dart format .
flutter analyze
flutter test --exclude-tags widget
flutter test --tags widget
flutter test
dart run scripts/check_forbidden_patterns.dart
```
