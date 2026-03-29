import 'package:flutter/services.dart';

const String appBuildTimestampAssetPath = 'assets/meta/app_build_timestamp.txt';

Future<DateTime?>? _cachedAppBuildTimestampFuture;

DateTime? parseAppBuildTimestamp(String rawTimestamp) {
  final normalized = rawTimestamp.trim();
  if (normalized.isEmpty || normalized == 'BUILD_TIMESTAMP_PLACEHOLDER') {
    return null;
  }
  return DateTime.tryParse(normalized)?.toUtc();
}

Future<DateTime?> loadAppBuildTimestamp({AssetBundle? bundle}) async {
  try {
    final rawAssetTimestamp = await (bundle ?? rootBundle).loadString(
      appBuildTimestampAssetPath,
    );
    return parseAppBuildTimestamp(rawAssetTimestamp);
  } catch (_) {
    return null;
  }
}

Future<DateTime?> defaultAppBuildTimestampLoader() {
  return _cachedAppBuildTimestampFuture ??= loadAppBuildTimestamp();
}

Future<String?> loadAppBuildTimestampIso8601({AssetBundle? bundle}) async {
  final timestamp = await loadAppBuildTimestamp(bundle: bundle);
  return timestamp?.toIso8601String();
}
