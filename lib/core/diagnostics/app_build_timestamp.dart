final DateTime _localBuildTimestampFallback = DateTime.now().toUtc();

DateTime resolveAppBuildTimestamp({String? rawTimestampOverride}) {
  final rawTimestamp =
      rawTimestampOverride ??
      const String.fromEnvironment('APP_BUILD_TIMESTAMP');
  if (rawTimestamp.isEmpty) {
    return _localBuildTimestampFallback;
  }
  return DateTime.tryParse(rawTimestamp)?.toUtc() ??
      _localBuildTimestampFallback;
}

String resolveAppBuildTimestampIso8601({String? rawTimestampOverride}) {
  return resolveAppBuildTimestamp(
    rawTimestampOverride: rawTimestampOverride,
  ).toIso8601String();
}
