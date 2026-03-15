import 'package:flutter_test/flutter_test.dart';

Future<void> pumpAndSettleSmoke(
  WidgetTester tester, {
  Duration step = const Duration(milliseconds: 16),
  Duration timeout = const Duration(seconds: 8),
}) {
  return tester.pumpAndSettle(step, EnginePhase.sendSemanticsUpdate, timeout);
}
