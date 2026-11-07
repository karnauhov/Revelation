import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';

Future<void> pumpAndSettleSmoke(
  WidgetTester tester, {
  Duration step = const Duration(milliseconds: 16),
  Duration timeout = const Duration(seconds: 8),
}) {
  return tester.pumpAndSettle(step, EnginePhase.sendSemanticsUpdate, timeout);
}

/// Waits for the scenario's result while unrelated animations may keep running.
Future<void> pumpUntilSmoke(
  WidgetTester tester, {
  required bool Function() isReady,
  required String reason,
  Duration step = const Duration(milliseconds: 16),
  Duration timeout = const Duration(seconds: 8),
}) {
  if (step <= Duration.zero || timeout <= Duration.zero) {
    throw ArgumentError('Smoke step and timeout must be positive.');
  }
  return TestAsyncUtils.guard<void>(() async {
    final endTime = tester.binding.clock.fromNowBy(timeout);
    do {
      if (tester.binding.clock.now().isAfter(endTime)) {
        throw FlutterError('pumpUntilSmoke timed out waiting for $reason');
      }
      await tester.pump(step, EnginePhase.sendSemanticsUpdate);
    } while (!isReady());
  });
}
