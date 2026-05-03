import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/analytics/app_analytics_reporter.dart';

void main() {
  group('AppAnalyticsReporter models', () {
    test('app context supports value equality and json conversion', () {
      const context = AppAnalyticsAppContext(
        appName: 'Revelation',
        packageName: 'ai11.link.revelation',
        version: '1.0.7',
        buildNumber: '157',
        platform: 'windows',
        languageCode: 'en',
      );

      expect(
        context,
        const AppAnalyticsAppContext(
          appName: 'Revelation',
          packageName: 'ai11.link.revelation',
          version: '1.0.7',
          buildNumber: '157',
          platform: 'windows',
          languageCode: 'en',
        ),
      );
      expect(context.toJson(), <String, Object>{
        'app_name': 'Revelation',
        'package_name': 'ai11.link.revelation',
        'version': '1.0.7',
        'build_number': '157',
        'platform': 'windows',
        'language_code': 'en',
      });
    });

    test('data context supports value equality and nested json conversion', () {
      final date = DateTime.utc(2026, 5, 3);
      final database = AppAnalyticsDatabaseVersion(
        schemaVersion: 1,
        dataVersion: 8,
        date: date,
      );
      final context = AppAnalyticsDataContext(
        languageCode: 'ru',
        commonDatabase: database,
        localizedDatabase: null,
      );

      expect(
        context,
        AppAnalyticsDataContext(
          languageCode: 'ru',
          commonDatabase: database,
          localizedDatabase: null,
        ),
      );
      expect(context.toJson(), <String, Object?>{
        'language_code': 'ru',
        'common_database': <String, Object>{
          'schema_version': 1,
          'data_version': 8,
          'date': date.toIso8601String(),
        },
        'localized_database': null,
      });
    });

    test('noop reporter accepts all calls', () async {
      const reporter = NoopAppAnalyticsReporter();
      final stackTrace = StackTrace.current;

      await reporter.setAppContext(
        const AppAnalyticsAppContext(
          appName: 'Revelation',
          packageName: 'ai11.link.revelation',
          version: '1.0.7',
          buildNumber: '157',
          platform: 'web',
          languageCode: 'en',
        ),
      );
      await reporter.setDataContext(
        const AppAnalyticsDataContext(
          languageCode: 'en',
          commonDatabase: null,
          localizedDatabase: null,
        ),
      );
      await reporter.trackAppSessionStarted(
        const AppAnalyticsDataContext(
          languageCode: 'en',
          commonDatabase: null,
          localizedDatabase: null,
        ),
      );
      await reporter.captureException(
        StateError('boom'),
        stackTrace,
        source: 'test',
      );
    });
  });
}
