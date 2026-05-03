class AppAnalyticsAppContext {
  const AppAnalyticsAppContext({
    required this.appName,
    required this.packageName,
    required this.version,
    required this.buildNumber,
    required this.platform,
    required this.languageCode,
  });

  final String appName;
  final String packageName;
  final String version;
  final String buildNumber;
  final String platform;
  final String languageCode;

  Map<String, Object> toJson() {
    return <String, Object>{
      'app_name': appName,
      'package_name': packageName,
      'version': version,
      'build_number': buildNumber,
      'platform': platform,
      'language_code': languageCode,
    };
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is AppAnalyticsAppContext &&
            runtimeType == other.runtimeType &&
            appName == other.appName &&
            packageName == other.packageName &&
            version == other.version &&
            buildNumber == other.buildNumber &&
            platform == other.platform &&
            languageCode == other.languageCode;
  }

  @override
  int get hashCode => Object.hash(
    appName,
    packageName,
    version,
    buildNumber,
    platform,
    languageCode,
  );
}

class AppAnalyticsDatabaseVersion {
  const AppAnalyticsDatabaseVersion({
    required this.schemaVersion,
    required this.dataVersion,
    required this.date,
  });

  final int schemaVersion;
  final int dataVersion;
  final DateTime date;

  Map<String, Object> toJson() {
    return <String, Object>{
      'schema_version': schemaVersion,
      'data_version': dataVersion,
      'date': date.toIso8601String(),
    };
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is AppAnalyticsDatabaseVersion &&
            runtimeType == other.runtimeType &&
            schemaVersion == other.schemaVersion &&
            dataVersion == other.dataVersion &&
            date == other.date;
  }

  @override
  int get hashCode => Object.hash(schemaVersion, dataVersion, date);
}

class AppAnalyticsDataContext {
  const AppAnalyticsDataContext({
    required this.languageCode,
    required this.commonDatabase,
    required this.localizedDatabase,
  });

  final String languageCode;
  final AppAnalyticsDatabaseVersion? commonDatabase;
  final AppAnalyticsDatabaseVersion? localizedDatabase;

  Map<String, Object?> toJson() {
    return <String, Object?>{
      'language_code': languageCode,
      'common_database': commonDatabase?.toJson(),
      'localized_database': localizedDatabase?.toJson(),
    };
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is AppAnalyticsDataContext &&
            runtimeType == other.runtimeType &&
            languageCode == other.languageCode &&
            commonDatabase == other.commonDatabase &&
            localizedDatabase == other.localizedDatabase;
  }

  @override
  int get hashCode =>
      Object.hash(languageCode, commonDatabase, localizedDatabase);
}

abstract class AppAnalyticsReporter {
  Future<void> setAppContext(AppAnalyticsAppContext context);

  Future<void> setDataContext(AppAnalyticsDataContext context);

  Future<void> trackAppSessionStarted(AppAnalyticsDataContext context);

  Future<void> captureException(
    Object error,
    StackTrace stackTrace, {
    required String source,
    bool fatal = false,
  });
}

class NoopAppAnalyticsReporter implements AppAnalyticsReporter {
  const NoopAppAnalyticsReporter();

  @override
  Future<void> setAppContext(AppAnalyticsAppContext context) async {}

  @override
  Future<void> setDataContext(AppAnalyticsDataContext context) async {}

  @override
  Future<void> trackAppSessionStarted(AppAnalyticsDataContext context) async {}

  @override
  Future<void> captureException(
    Object error,
    StackTrace stackTrace, {
    required String source,
    bool fatal = false,
  }) async {}
}
