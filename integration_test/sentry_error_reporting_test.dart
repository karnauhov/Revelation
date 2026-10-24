import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/infra/analytics/sentry/sentry_app_analytics_reporter.dart';
import 'package:revelation/infra/analytics/sentry/sentry_app_runner.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Sentry serializes original and fallback error stacks', (
    tester,
  ) async {
    await tester.runAsync(() async {
      final transport = _RecordingTransport();
      await Sentry.close();
      try {
        await runWithSentry(
          () async {},
          configureOptions: (options) {
            options.dsn = 'https://public@example.invalid/1';
            options.transport = transport;
            options.autoInitializeNativeSdk = false;
            options.enableAutoSessionTracking = false;
            options.integrations.clear();
            options.debug = false;
          },
        );
        await Sentry.configureScope((scope) {
          scope.setUser(SentryUser(id: 'synthetic-test-user'));
        });
        final reporter = SentryAppAnalyticsReporter();
        await reporter.captureException(
          StateError('supplied trace'),
          StackTrace.fromString(
            '#0 originalThrow (package:revelation/original_throw.dart:17:9)',
          ),
          source: 'integration: supplied',
        );
        await reporter.captureException(
          _throwAndCatchError(),
          StackTrace.fromString(''),
          source: 'integration: recovered',
        );
        await reporter.captureException(
          StateError('never thrown'),
          StackTrace.fromString('   \n'),
          source: 'integration: snapshot',
        );
        await reporter.captureException(
          Exception('no Error.stackTrace'),
          StackTrace.empty,
          source: 'integration: empty sentinel',
        );

        expect(transport.events, hasLength(4));
        final frameCounts = <int>[];
        for (final event in transport.events) {
          final exception =
              (event['exception']['values'] as List).single as Map;
          final frames = exception['stacktrace']['frames'] as List;
          expect(frames, isNotEmpty);
          expect(event['user'], isNull);
          frameCounts.add(frames.length);
        }
        final provided = transport.events[0]['exception']['values'][0];
        expect(
          provided['stacktrace']['frames'].single['filename'],
          'original_throw.dart',
        );
        expect(provided['stacktrace']['frames'].single['lineno'], 17);
        for (var index = 0; index < transport.events.length; index++) {
          expect(
            transport
                .events[index]['contexts']['revelation.error']['stack_trace_origin'],
            ['provided', 'error', 'capture', 'capture'][index],
          );
          final exception = transport.events[index]['exception']['values'][0];
          if (index >= 2) {
            expect(exception['stacktrace']['snapshot'], isTrue);
          }
        }
        binding.reportData = {
          'serializedErrorEvents': transport.events.length,
          'stackFrameCounts': frameCounts,
          'fallbackSnapshots': 2,
          'networkTransport': 'in-memory only',
        };
      } finally {
        await Sentry.close();
      }
    });
  });
}

StateError _throwAndCatchError() {
  try {
    throw StateError('original throw site');
  } on StateError catch (error) {
    return error;
  }
}

class _RecordingTransport implements Transport {
  final events = <Map<String, dynamic>>[];

  @override
  Future<SentryId?> send(SentryEnvelope envelope) async {
    for (final item in envelope.items) {
      final data = jsonDecode(utf8.decode(await item.dataFactory()));
      if (data is Map<String, dynamic> && data.containsKey('exception')) {
        events.add(data);
      }
    }
    return envelope.header.eventId;
  }
}
