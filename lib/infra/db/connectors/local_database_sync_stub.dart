import 'package:revelation/infra/db/connectors/local_database_sync_result.dart';
import 'package:revelation/shared/config/app_constants.dart';

Future<void> verifyAndUpdateKnownLocalDatabases({
  String? languageCode,
  bool force = false,
}) async {}

Future<LocalDatabaseSyncResult> verifyAndUpdateKnownLocalDatabasesWithResult({
  String? languageCode,
  bool force = false,
}) async {
  return LocalDatabaseSyncResult(
    files: knownLocalDatabaseFiles(languageCode: languageCode)
        .map(
          (fileName) => LocalDatabaseFileSyncResult(
            fileName: fileName,
            existedBeforeSync: false,
            healthyBeforeSync: false,
            sizeMatchedManifestBeforeSync: true,
            existsAfterSync: false,
            healthyAfterSync: false,
            sizeMatchedManifestAfterSync: true,
            updated: false,
          ),
        )
        .toList(growable: false),
  );
}

Future<bool> verifyAndUpdateLocalDatabaseFile(
  String dbFile, {
  bool force = false,
}) async {
  return false;
}

Future<LocalDatabaseFileSyncResult> verifyAndUpdateLocalDatabaseFileWithResult(
  String dbFile, {
  bool force = false,
}) async {
  return LocalDatabaseFileSyncResult(
    fileName: dbFile,
    existedBeforeSync: false,
    healthyBeforeSync: false,
    sizeMatchedManifestBeforeSync: true,
    existsAfterSync: false,
    healthyAfterSync: false,
    sizeMatchedManifestAfterSync: true,
    updated: false,
  );
}

List<String> knownLocalDatabaseFiles({
  String? languageCode,
  bool includeAllLanguages = true,
}) {
  final files = <String>[AppConstants.commonDB];
  if (includeAllLanguages) {
    files.addAll(
      AppConstants.languages.keys.map(
        (lang) => AppConstants.localizedDB.replaceAll('@loc', lang),
      ),
    );
    return files;
  }

  final normalizedLanguage = _normalizeLanguageCode(languageCode);
  files.add(AppConstants.localizedDB.replaceAll('@loc', normalizedLanguage));
  return files;
}

String _normalizeLanguageCode(String? languageCode) {
  final normalized = (languageCode ?? 'en').trim().toLowerCase();
  if (AppConstants.languages.containsKey(normalized)) {
    return normalized;
  }
  return 'en';
}
