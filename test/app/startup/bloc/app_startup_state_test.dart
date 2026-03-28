import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/startup/bloc/app_startup_state.dart';
import 'package:revelation/core/errors/app_failure.dart';

void main() {
  group('AppStartupState', () {
    test('initial exposes preparing step and pending readiness', () {
      final state = AppStartupState.initial(localeCode: 'ru');

      expect(state.step, AppBootstrapStep.preparing);
      expect(state.stepNumber, 1);
      expect(state.progressValue, 0.12);
      expect(state.localeCode, 'ru');
      expect(state.isLoading, isTrue);
      expect(state.isReady, isFalse);
      expect(state.failure, isNull);
    });

    test('copyWith updates fields and clears failure on request', () {
      const failure = AppFailure.dataSource('forced startup failure');
      final state = AppStartupState.initial(
        localeCode: 'en',
      ).copyWith(failure: failure);

      final next = state.copyWith(
        step: AppBootstrapStep.initializingDatabases,
        appVersion: '1.0.5',
        buildNumber: '141',
        localeCode: 'uk',
        isLoading: false,
        isReady: true,
        clearFailure: true,
      );

      expect(next.step, AppBootstrapStep.initializingDatabases);
      expect(next.stepNumber, 4);
      expect(next.progressValue, 0.74);
      expect(next.appVersion, '1.0.5');
      expect(next.buildNumber, '141');
      expect(next.localeCode, 'uk');
      expect(next.isLoading, isFalse);
      expect(next.isReady, isTrue);
      expect(next.failure, isNull);
    });
  });
}
