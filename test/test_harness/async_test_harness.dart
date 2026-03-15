import 'package:flutter_test/flutter_test.dart';

Future<void> pumpFrames(
  WidgetTester tester, {
  int count = 1,
  Duration step = const Duration(milliseconds: 16),
}) async {
  for (int i = 0; i < count; i++) {
    await tester.pump(step);
  }
}

Future<void> pumpAndSettleSafe(
  WidgetTester tester, {
  Duration step = const Duration(milliseconds: 16),
  Duration timeout = const Duration(seconds: 5),
}) {
  return tester.pumpAndSettle(step, EnginePhase.sendSemanticsUpdate, timeout);
}
