import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/infra/analytics/sentry/sentry_privacy.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

typedef SentryOptionsConfigurator =
    FutureOr<void> Function(SentryFlutterOptions options);

const String _sentryDsn = String.fromEnvironment(
  'SENTRY_DSN',
  defaultValue: '',
);
const String _sentryEnvironment = String.fromEnvironment(
  'SENTRY_ENVIRONMENT',
  defaultValue: '',
);
const String _sentryTracesSampleRate = String.fromEnvironment(
  'SENTRY_TRACES_SAMPLE_RATE',
  defaultValue: '1.0',
);

Future<void> runWithSentry(
  Future<void> Function() appRunner, {
  SentryOptionsConfigurator? configureOptions,
  Future<PackageInfo> Function() packageInfoLoader = PackageInfo.fromPlatform,
}) async {
  var started = false;
  try {
    await SentryFlutter.init(
      (options) async {
        options.dsn = _sentryDsn.isNotEmpty ? _sentryDsn : (options.dsn ?? '');
        if (_sentryEnvironment.isNotEmpty) {
          options.environment = _sentryEnvironment;
        }
        options.sendDefaultPii = false;
        options.attachStacktrace = true;
        options.attachScreenshot = false;
        // Keep the explicit privacy opt-out while this SDK flag is experimental.
        // ignore: experimental_member_use
        options.attachViewHierarchy = false;
        options.enableLogs = false;
        options.enableAutoSessionTracking = true;
        options.enableAutoPerformanceTracing = false;
        options.enableUserInteractionBreadcrumbs = false;
        options.enableAutoNativeBreadcrumbs = false;
        options.recordHttpBreadcrumbs = false;
        options.enableUserInteractionTracing = false;
        options.enableTimeToFullDisplayTracing = false;
        options.reportSilentFlutterErrors = false;
        // Profiling remains disabled; the SDK exposes this opt-out as experimental.
        // ignore: experimental_member_use
        options.profilesSampleRate = 0;
        options.replay.sessionSampleRate = 0;
        options.replay.onErrorSampleRate = 0;
        options.tracesSampleRate = parseSentrySampleRate(
          _sentryTracesSampleRate,
          fallback: 1,
        );
        options.beforeSend = scrubSentryEvent;
        options.beforeSendTransaction = (transaction, hint) {
          scrubSentryEvent(transaction, hint);
          return transaction;
        };
        options.beforeBreadcrumb = scrubSentryBreadcrumb;
        // The uploader uses the pubspec package name on every platform. SDK
        // defaults can instead use an Android applicationId or a Windows name.
        try {
          var version = const String.fromEnvironment('SENTRY_APP_VERSION');
          var build = const String.fromEnvironment('SENTRY_APP_BUILD');
          if (version.isEmpty || build.isEmpty) {
            final package = await packageInfoLoader().timeout(
              const Duration(seconds: 3),
            );
            version = package.version.trim();
            build = package.buildNumber.trim();
          }
          if (version.isNotEmpty && build.isNotEmpty) {
            options.release = 'revelation@$version+$build';
            options.dist = build;
          }
        } catch (_) {
          // Optional metadata must not block startup or change the privacy profile.
          debugPrint('Sentry release metadata unavailable.');
        }
        await configureOptions?.call(options);
      },
      appRunner: () async {
        started = true;
        await appRunner();
      },
    );
  } catch (error, stack) {
    if (started) Error.throwWithStackTrace(error, stack);
    // A telemetry SDK failure must leave the local guarded app startup usable.
    debugPrint('Sentry unavailable; starting with local diagnostics.');
    await appRunner();
  }
}

@visibleForTesting
double parseSentrySampleRate(String value, {required double fallback}) {
  final parsed = double.tryParse(value);
  if (parsed == null || parsed.isNaN || parsed < 0 || parsed > 1) {
    return fallback;
  }
  return parsed;
}
