# Индекс покрытия тестами (RU)

Этот документ является единой точкой входа для всех материалов по плану повышения test coverage.

## Основные документы
- [План аудита и фаз](./test_coverage_audit_plan.ru.md)
- [Базовая фиксация P01](./test_coverage_baseline_p01.ru.md)
- [Traceability-карта P02](./test_coverage_traceability_p02.ru.md)
- [Структурная нормализация P03](./test_coverage_structural_normalization_p03.ru.md)
- [Стабилизация test harness P04](./test_coverage_harness_stabilization_p04.ru.md)

## Базовый расчёт покрытия (P01)
```bash
flutter test --coverage
dart run scripts/coverage_baseline.dart
```

## Правило обновления
- Все новые материалы по фазам покрытия добавляются в этот индекс.
