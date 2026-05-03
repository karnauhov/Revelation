import 'dart:async';

import 'package:flutter/foundation.dart';
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
}) {
  return SentryFlutter.init((options) async {
    options.dsn = _sentryDsn.isNotEmpty ? _sentryDsn : (options.dsn ?? '');
    if (_sentryEnvironment.isNotEmpty) {
      options.environment = _sentryEnvironment;
    }
    options.sendDefaultPii = false;
    options.attachScreenshot = false;
    options.attachViewHierarchy = false;
    options.enableLogs = false;
    options.enableAutoSessionTracking = true;
    options.enableAutoPerformanceTracing = false;
    options.enableUserInteractionBreadcrumbs = false;
    options.enableUserInteractionTracing = false;
    options.enableTimeToFullDisplayTracing = false;
    options.reportSilentFlutterErrors = false;
    options.profilesSampleRate = 0;
    options.tracesSampleRate = parseSentrySampleRate(
      _sentryTracesSampleRate,
      fallback: 1,
    );
    options.beforeSend = (event, hint) {
      event.user = null;
      return event;
    };
    await configureOptions?.call(options);
  }, appRunner: appRunner);
}

@visibleForTesting
double parseSentrySampleRate(String value, {required double fallback}) {
  final parsed = double.tryParse(value);
  if (parsed == null || parsed.isNaN || parsed < 0 || parsed > 1) {
    return fallback;
  }
  return parsed;
}
