import 'package:flutter_test/flutter_test.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/infra/analytics/sentry/sentry_app_runner.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() {
    PackageInfo.setMockInitialValues(
      appName: 'Revelation',
      packageName: 'ai11.link.revelation',
      version: '1.0.8',
      buildNumber: '174',
      buildSignature: '',
    );
  });

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
        expect(options.release, 'revelation@1.0.8+174');
        expect(options.dist, '174');
        expect(options.enableAutoNativeBreadcrumbs, isFalse);
        expect(options.recordHttpBreadcrumbs, isFalse);
        expect(options.replay.sessionSampleRate, 0);
        expect(options.replay.onErrorSampleRate, 0);
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

  test('metadata failure still configures privacy and starts once', () async {
    var calls = 0;
    addTearDown(Sentry.close);
    await runWithSentry(
      () async {
        calls++;
      },
      packageInfoLoader: () async => throw StateError('platform unavailable'),
      configureOptions: (options) {
        expect(options.beforeSend, isNotNull);
        expect(options.beforeBreadcrumb, isNotNull);
        expect(options.sendDefaultPii, isFalse);
      },
    );
    expect(calls, 1);
  });

  test('an app failure is propagated without starting it twice', () async {
    var calls = 0;
    final failure = StateError('app failed');
    addTearDown(Sentry.close);
    await expectLater(
      runWithSentry(() async {
        calls++;
        throw failure;
      }),
      throwsA(same(failure)),
    );
    expect(calls, 1);
  });

  test('invalid SDK configuration still starts the app once', () async {
    var calls = 0;
    addTearDown(Sentry.close);
    await runWithSentry(
      () async {
        calls++;
      },
      configureOptions: (options) {
        options.dsn = 'invalid-dsn';
        options.autoInitializeNativeSdk = false;
      },
    );
    expect(calls, 1);
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
