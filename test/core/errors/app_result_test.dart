import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';

void main() {
  group('AppResult', () {
    test('isSuccess/isFailure reflect the result type', () {
      const success = AppSuccess<int>(10);
      const failure = AppFailureResult<int>(AppFailure.validation('bad'));

      expect(success.isSuccess, isTrue);
      expect(success.isFailure, isFalse);
      expect(failure.isSuccess, isFalse);
      expect(failure.isFailure, isTrue);
    });

    test('when dispatches to success branch', () {
      const result = AppSuccess<String>('payload');

      final value = result.when(
        success: (data) => 'ok:$data',
        failure: (failure) => 'fail:${failure.message}',
      );

      expect(value, 'ok:payload');
    });

    test('when dispatches to failure branch', () {
      const failure = AppFailure.notFound('missing');
      const result = AppFailureResult<String>(failure);

      final value = result.when(
        success: (data) => 'ok:$data',
        failure: (err) => 'fail:${err.message}',
      );

      expect(value, 'fail:missing');
    });
  });
}
