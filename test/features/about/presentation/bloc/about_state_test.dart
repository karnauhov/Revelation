import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/about/presentation/bloc/about_state.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';

void main() {
  group('AboutState', () {
    test('initial creates loading state with empty content', () {
      final state = AboutState.initial();

      expect(state.appVersion, isEmpty);
      expect(state.buildNumber, isEmpty);
      expect(state.changelog, isEmpty);
      expect(state.isLoading, isTrue);
      expect(state.isChangelogExpanded, isFalse);
      expect(state.isAcknowledgementsExpanded, isFalse);
      expect(state.isRecommendedExpanded, isFalse);
      expect(state.commonDbVersionInfo, isNull);
      expect(state.localizedDbVersionInfo, isNull);
      expect(state.failure, isNull);
    });

    test('copyWith updates only provided scalar fields', () {
      final base = AboutState.initial();

      final next = base.copyWith(
        appVersion: '1.2.3',
        buildNumber: '42',
        changelog: '# New',
        isLoading: false,
        isChangelogExpanded: true,
        isAcknowledgementsExpanded: true,
        isRecommendedExpanded: true,
      );

      expect(next.appVersion, '1.2.3');
      expect(next.buildNumber, '42');
      expect(next.changelog, '# New');
      expect(next.isLoading, isFalse);
      expect(next.isChangelogExpanded, isTrue);
      expect(next.isAcknowledgementsExpanded, isTrue);
      expect(next.isRecommendedExpanded, isTrue);
      expect(next.commonDbVersionInfo, isNull);
      expect(next.localizedDbVersionInfo, isNull);
    });

    test('copyWith keeps db versions when fields are omitted', () {
      final common = DatabaseVersionInfo(
        schemaVersion: 4,
        dataVersion: 7,
        date: DateTime.utc(2026, 3, 20),
      );
      final localized = DatabaseVersionInfo(
        schemaVersion: 5,
        dataVersion: 8,
        date: DateTime.utc(2026, 3, 21),
      );
      final state = AboutState.initial().copyWith(
        isLoading: false,
        commonDbVersionInfo: common,
        localizedDbVersionInfo: localized,
      );

      final next = state.copyWith(changelog: '# Updated');

      expect(next.commonDbVersionInfo, common);
      expect(next.localizedDbVersionInfo, localized);
      expect(next.changelog, '# Updated');
    });

    test('copyWith allows explicit clearing of db versions with null', () {
      final common = DatabaseVersionInfo(
        schemaVersion: 4,
        dataVersion: 7,
        date: DateTime.utc(2026, 3, 20),
      );
      final localized = DatabaseVersionInfo(
        schemaVersion: 5,
        dataVersion: 8,
        date: DateTime.utc(2026, 3, 21),
      );
      final state = AboutState.initial().copyWith(
        commonDbVersionInfo: common,
        localizedDbVersionInfo: localized,
      );

      final cleared = state.copyWith(
        commonDbVersionInfo: null,
        localizedDbVersionInfo: null,
      );

      expect(cleared.commonDbVersionInfo, isNull);
      expect(cleared.localizedDbVersionInfo, isNull);
    });

    test('copyWith failure can be replaced and cleared independently', () {
      const firstFailure = AppFailure.dataSource('first');
      const secondFailure = AppFailure.validation('second');
      final state = AboutState.initial().copyWith(
        isLoading: false,
        failure: firstFailure,
      );

      final replaced = state.copyWith(failure: secondFailure);
      final cleared = replaced.copyWith(clearFailure: true);

      expect(replaced.failure, secondFailure);
      expect(cleared.failure, isNull);
    });

    test('equality and hashCode depend on all fields', () {
      final common = DatabaseVersionInfo(
        schemaVersion: 1,
        dataVersion: 2,
        date: DateTime.utc(2026, 1, 1),
      );
      final localized = DatabaseVersionInfo(
        schemaVersion: 3,
        dataVersion: 4,
        date: DateTime.utc(2026, 1, 2),
      );
      const failure = AppFailure.unknown('x');
      final a = AboutState.initial().copyWith(
        appVersion: '1.0.0',
        buildNumber: '10',
        changelog: 'changelog',
        isLoading: false,
        isChangelogExpanded: true,
        isAcknowledgementsExpanded: true,
        isRecommendedExpanded: true,
        commonDbVersionInfo: common,
        localizedDbVersionInfo: localized,
        failure: failure,
      );
      final b = AboutState.initial().copyWith(
        appVersion: '1.0.0',
        buildNumber: '10',
        changelog: 'changelog',
        isLoading: false,
        isChangelogExpanded: true,
        isAcknowledgementsExpanded: true,
        isRecommendedExpanded: true,
        commonDbVersionInfo: common,
        localizedDbVersionInfo: localized,
        failure: failure,
      );

      expect(a, b);
      expect(a.hashCode, b.hashCode);
      expect(a.copyWith(isRecommendedExpanded: false), isNot(b));
    });
  });
}
