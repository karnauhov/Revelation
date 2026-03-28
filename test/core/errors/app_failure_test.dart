import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';

void main() {
  group('AppFailure', () {
    test('named constructors set failure type', () {
      const validation = AppFailure.validation('validation');
      const notFound = AppFailure.notFound('not found');
      const dataSource = AppFailure.dataSource('data source');
      const unknown = AppFailure.unknown('unknown');

      expect(validation.type, AppFailureType.validation);
      expect(notFound.type, AppFailureType.notFound);
      expect(dataSource.type, AppFailureType.dataSource);
      expect(unknown.type, AppFailureType.unknown);
    });

    test('equality uses type and message only', () {
      const first = AppFailure.validation(
        'message',
        cause: 'first',
        stackTrace: StackTrace.empty,
      );
      const second = AppFailure.validation('message', cause: 'second');
      const different = AppFailure.unknown('message');

      expect(first, equals(second));
      expect(first.hashCode, equals(second.hashCode));
      expect(first == different, isFalse);
    });

    test('toString includes type, message, and cause', () {
      const failure = AppFailure.dataSource('boom', cause: 'io');

      expect(
        failure.toString(),
        contains('AppFailure(type: ${AppFailureType.dataSource}'),
      );
      expect(failure.toString(), contains('message: boom'));
      expect(failure.toString(), contains('cause: io'));
    });
  });
}
