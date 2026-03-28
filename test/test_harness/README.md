# Test Harness

`test/test_harness` contains shared deterministic helpers for unit and widget tests.

## Contents

- `test_harness.dart` - barrel export for most tests
- `revelation_test_harness.dart` - repo-level harness setup
- `widget_test_harness.dart` - localized app/context wrappers
- `async_test_harness.dart` - stable `pump` helpers for async UI work

## Example

```dart
import '../../../../test_harness/test_harness.dart';

await tester.pumpWidget(
  buildLocalizedTestApp(child: const MyWidget()),
);

final context = await pumpLocalizedContext(tester);
await pumpFrames(tester, count: 2);
await pumpAndSettleSafe(tester);
```

## Rules

- Reuse harness helpers before adding feature-local duplicates.
- Prefer the shared localized wrapper for widget tests.
- Prefer harness `pump` helpers over ad-hoc `Future.delayed`.
