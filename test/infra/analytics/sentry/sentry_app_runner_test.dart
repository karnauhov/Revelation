import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/analytics/sentry/sentry_app_runner.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('Sentry keeps privacy attachments and profiling disabled', () async {
    var runnerCalls = 0;
    var configured = false;
    addTearDown(Sentry.close);
    await runWithSentry(
      () async {
        runnerCalls++;
      },
      configureOptions: (options) {
        configured = true;
        expect(options.sendDefaultPii, isFalse);
        expect(options.attachStacktrace, isTrue);
        expect(options.attachScreenshot, isFalse);
        // These SDK opt-out flags are deliberately experimental.
        // ignore: experimental_member_use
        expect(options.attachViewHierarchy, isFalse);
        // ignore: experimental_member_use
        expect(options.profilesSampleRate, 0);
      },
    );
    expect(configured, isTrue);
    expect(runnerCalls, 1);
  });

  group('parseSentrySampleRate', () {
    test('accepts values in Sentry sample-rate range', () {
      expect(parseSentrySampleRate('0', fallback: 1), 0);
      expect(parseSentrySampleRate('0.25', fallback: 1), 0.25);
      expect(parseSentrySampleRate('1', fallback: 0), 1);
    });

    test('falls back for invalid values', () {
      expect(parseSentrySampleRate('', fallback: 0.5), 0.5);
      expect(parseSentrySampleRate('nope', fallback: 0.5), 0.5);
      expect(parseSentrySampleRate('-0.1', fallback: 0.5), 0.5);
      expect(parseSentrySampleRate('1.1', fallback: 0.5), 0.5);
      expect(parseSentrySampleRate('NaN', fallback: 0.5), 0.5);
    });
  });
}
