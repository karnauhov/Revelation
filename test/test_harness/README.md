# Test Harness

`test/test_harness` содержит общие deterministic helper-утилиты для тестов.

## Состав

- `test_harness.dart` — единый barrel-экспорт для тестов.
- `widget_test_harness.dart` — стандартные app/context wrapper-утилиты.
- `async_test_harness.dart` — стабильные `pump`/`pumpAndSettle` helper-обертки.
- `fakes/*` — переиспользуемые fake-реализации для unit/widget тестов.

## Быстрое использование

```dart
import '../../../../test_harness/test_harness.dart';

await tester.pumpWidget(
  buildLocalizedTestApp(child: const MyWidget()),
);

final context = await pumpLocalizedContext(tester);
await pumpFrames(tester, count: 2);
await pumpAndSettleSafe(tester);
```

## Правила

- Не дублировать одинаковые fake/helper в feature-тестах, если они уже есть в harness.
- Для `testWidgets` использовать общий wrapper, чтобы локализация и базовая среда были консистентными.
- Для async-ожиданий предпочитать harness helper вместо произвольных `Future.delayed`.
