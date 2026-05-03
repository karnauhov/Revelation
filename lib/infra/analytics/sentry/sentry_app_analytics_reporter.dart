import 'package:revelation/core/analytics/app_analytics_reporter.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

class SentryAppAnalyticsReporter implements AppAnalyticsReporter {
  SentryAppAnalyticsReporter();

  AppAnalyticsAppContext? _appContext;

  @override
  Future<void> setAppContext(AppAnalyticsAppContext context) async {
    _appContext = context;
    await Sentry.configureScope((scope) async {
      await scope.setTag('app.version', context.version);
      await scope.setTag('app.build', context.buildNumber);
      await scope.setTag('app.platform', context.platform);
      await scope.setTag('app.language', context.languageCode);
      await scope.setContexts('revelation.app', context.toJson());
    });
  }

  @override
  Future<void> setDataContext(AppAnalyticsDataContext context) async {
    await Sentry.configureScope((scope) async {
      await _setDataTags(scope, context);
      await scope.setContexts('revelation.data', context.toJson());
    });
  }

  @override
  Future<void> trackAppSessionStarted(AppAnalyticsDataContext context) async {
    await setDataContext(context);
    final transaction = Sentry.startTransaction(
      'app.session',
      'app.lifecycle',
      bindToScope: false,
    );
    final appContext = _appContext;
    if (appContext != null) {
      _setAppOnSpan(transaction, appContext);
    }
    _setDataOnSpan(transaction, context);
    await transaction.finish(status: SpanStatus.ok());
  }

  @override
  Future<void> captureException(
    Object error,
    StackTrace stackTrace, {
    required String source,
    bool fatal = false,
  }) {
    return Sentry.captureException(
      error,
      stackTrace: stackTrace,
      withScope: (scope) async {
        await scope.setTag('error.source', source);
        await scope.setTag('error.fatal', fatal ? 'true' : 'false');
        await scope.setContexts('revelation.error', <String, Object>{
          'source': source,
          'fatal': fatal,
        });
      },
    ).then((_) {});
  }

  static Future<void> _setDataTags(
    Scope scope,
    AppAnalyticsDataContext context,
  ) async {
    await scope.setTag('db.language', context.languageCode);
    final commonDatabase = context.commonDatabase;
    if (commonDatabase != null) {
      await scope.setTag(
        'db.common.schema',
        commonDatabase.schemaVersion.toString(),
      );
      await scope.setTag(
        'db.common.data',
        commonDatabase.dataVersion.toString(),
      );
    }
    final localizedDatabase = context.localizedDatabase;
    if (localizedDatabase != null) {
      await scope.setTag(
        'db.localized.schema',
        localizedDatabase.schemaVersion.toString(),
      );
      await scope.setTag(
        'db.localized.data',
        localizedDatabase.dataVersion.toString(),
      );
    }
  }

  static void _setDataOnSpan(
    ISentrySpan span,
    AppAnalyticsDataContext context,
  ) {
    span.setTag('db.language', context.languageCode);
    span.setData('revelation.data', context.toJson());
    final commonDatabase = context.commonDatabase;
    if (commonDatabase != null) {
      span.setTag('db.common.schema', commonDatabase.schemaVersion.toString());
      span.setTag('db.common.data', commonDatabase.dataVersion.toString());
    }
    final localizedDatabase = context.localizedDatabase;
    if (localizedDatabase != null) {
      span.setTag(
        'db.localized.schema',
        localizedDatabase.schemaVersion.toString(),
      );
      span.setTag(
        'db.localized.data',
        localizedDatabase.dataVersion.toString(),
      );
    }
  }

  static void _setAppOnSpan(ISentrySpan span, AppAnalyticsAppContext context) {
    span.setTag('app.version', context.version);
    span.setTag('app.build', context.buildNumber);
    span.setTag('app.platform', context.platform);
    span.setTag('app.language', context.languageCode);
    span.setData('revelation.app', context.toJson());
  }
}
