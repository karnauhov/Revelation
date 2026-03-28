import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/async/latest_request_guard.dart';

void main() {
  group('LatestRequestGuard', () {
    test('marks only latest token as active', () {
      final guard = LatestRequestGuard();

      final first = guard.start();
      final second = guard.start();

      expect(guard.isActive(first), isFalse);
      expect(guard.isActive(second), isTrue);
    });

    test('cancels active token', () {
      final guard = LatestRequestGuard();

      final token = guard.start();
      guard.cancelActive();

      expect(guard.isActive(token), isFalse);
    });
  });
}
