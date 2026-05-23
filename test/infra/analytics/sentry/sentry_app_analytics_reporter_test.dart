import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/analytics/app_analytics_reporter.dart';
import 'package:revelation/infra/analytics/sentry/sentry_app_analytics_reporter.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

void main() {
  setUp(() async {
    await Sentry.close();
  });

  tearDown(() async {
    await Sentry.close();
  });

  test('setAppContext writes app metadata to Sentry scope', () async {
    await _initSentry();
    final reporter = SentryAppAnalyticsReporter();
    const context = AppAnalyticsAppContext(
      appName: 'Revelation',
      packageName: 'ai11.link.revelation',
      version: '1.0.7',
      buildNumber: '157',
      platform: 'android',
      languageCode: 'en',
    );

    await reporter.setAppContext(context);

    await Sentry.configureScope((scope) {
      expect(scope.tags['app.version'], '1.0.7');
      expect(scope.tags['app.build'], '157');
      expect(scope.tags['app.platform'], 'android');
      expect(scope.tags['app.language'], 'en');
      expect(scope.contexts['revelation.app'], context.toJson());
    });
  });

  test('setDataContext writes database metadata to Sentry scope', () async {
    await _initSentry();
    final reporter = SentryAppAnalyticsReporter();
    final context = _dataContext();

    await reporter.setDataContext(context);

    await Sentry.configureScope((scope) {
      expect(scope.tags['db.language'], 'ru');
      expect(scope.tags['db.common.schema'], '1');
      expect(scope.tags['db.common.data'], '8');
      expect(scope.tags['db.localized.schema'], '2');
      expect(scope.tags['db.localized.data'], '9');
      expect(scope.contexts['revelation.data'], context.toJson());
    });
  });

  test(
    'trackAppSessionStarted reports app session transaction metadata',
    () async {
      SentryTransaction? capturedTransaction;
      await _initSentry(
        beforeSendTransaction: (transaction, hint) {
          capturedTransaction = transaction;
          return transaction;
        },
      );
      final reporter = SentryAppAnalyticsReporter();

      await reporter.setAppContext(
        const AppAnalyticsAppContext(
          appName: 'Revelation',
          packageName: 'ai11.link.revelation',
          version: '1.0.7',
          buildNumber: '157',
          platform: 'windows',
          languageCode: 'en',
        ),
      );
      await reporter.trackAppSessionStarted(_dataContext());

      expect(capturedTransaction?.transaction, 'app.session');
      expect(capturedTransaction?.tags?['app.version'], '1.0.7');
      expect(capturedTransaction?.tags?['app.build'], '157');
      expect(capturedTransaction?.tags?['app.platform'], 'windows');
      expect(capturedTransaction?.tags?['app.language'], 'en');
      expect(capturedTransaction?.tags?['db.language'], 'ru');
      expect(capturedTransaction?.tags?['db.common.schema'], '1');
      expect(capturedTransaction?.tags?['db.common.data'], '8');
      expect(capturedTransaction?.tags?['db.localized.schema'], '2');
      expect(capturedTransaction?.tags?['db.localized.data'], '9');
    },
  );

  test('captureException adds error metadata to captured event', () async {
    SentryEvent? capturedEvent;
    await _initSentry(
      beforeSend: (event, hint) {
        capturedEvent = event;
        return event;
      },
    );
    final reporter = SentryAppAnalyticsReporter();
    final error = StateError('boom');

    await reporter.captureException(
      error,
      StackTrace.current,
      source: 'bootstrap',
      fatal: true,
    );

    expect(capturedEvent?.throwable, same(error));
    expect(capturedEvent?.tags?['error.source'], 'bootstrap');
    expect(capturedEvent?.tags?['error.fatal'], 'true');
    expect(capturedEvent?.contexts['revelation.error'], <String, Object>{
      'source': 'bootstrap',
      'fatal': true,
    });
  });
}

Future<void> _initSentry({
  BeforeSendCallback? beforeSend,
  BeforeSendTransactionCallback? beforeSendTransaction,
}) {
  return Sentry.init((options) {
    options.dsn = 'https://public@example.com/1';
    options.debug = false;
    options.enableLogs = false;
    options.tracesSampleRate = 1;
    options.transport = _RecordingTransport();
    options.beforeSend = beforeSend;
    options.beforeSendTransaction = beforeSendTransaction;
  });
}

AppAnalyticsDataContext _dataContext() {
  return AppAnalyticsDataContext(
    languageCode: 'ru',
    commonDatabase: AppAnalyticsDatabaseVersion(
      schemaVersion: 1,
      dataVersion: 8,
      date: DateTime.utc(2026, 5, 3),
    ),
    localizedDatabase: AppAnalyticsDatabaseVersion(
      schemaVersion: 2,
      dataVersion: 9,
      date: DateTime.utc(2026, 5, 4),
    ),
  );
}

class _RecordingTransport implements Transport {
  final List<SentryEnvelope> envelopes = <SentryEnvelope>[];

  @override
  Future<SentryId?> send(SentryEnvelope envelope) async {
    envelopes.add(envelope);
    return envelope.header.eventId;
  }
}
