import 'dart:io';

import 'package:path/path.dart' as p;
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/infra/db/connectors/local_database_sync_result.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:sqlite3/sqlite3.dart';

const _databaseFolder = 'db';
const _databaseManifestFile = 'manifest.json';

Future<void> verifyAndUpdateKnownLocalDatabases({
  String? languageCode,
  bool force = false,
}) async {
  await verifyAndUpdateKnownLocalDatabasesWithResult(
    languageCode: languageCode,
    force: force,
  );
}

Future<LocalDatabaseSyncResult> verifyAndUpdateKnownLocalDatabasesWithResult({
  String? languageCode,
  bool force = false,
}) async {
  final manifestEntries = await _loadLocalManifestEntries(
    refreshFromServer: true,
  );
  final results = <LocalDatabaseFileSyncResult>[];
  for (final dbFile in knownLocalDatabaseFiles(languageCode: languageCode)) {
    results.add(
      await _verifyAndUpdateLocalDatabaseFile(
        dbFile,
        force: force,
        manifestEntries: manifestEntries,
      ),
    );
  }
  return LocalDatabaseSyncResult(files: results);
}

Future<bool> verifyAndUpdateLocalDatabaseFile(
  String dbFile, {
  bool force = false,
}) async {
  final result = await verifyAndUpdateLocalDatabaseFileWithResult(
    dbFile,
    force: force,
  );
  return result.updated;
}

Future<LocalDatabaseFileSyncResult> verifyAndUpdateLocalDatabaseFileWithResult(
  String dbFile, {
  bool force = false,
}) async {
  final manifestEntries = await _loadLocalManifestEntries(
    refreshFromServer: true,
  );
  return _verifyAndUpdateLocalDatabaseFile(
    dbFile,
    force: force,
    manifestEntries: manifestEntries,
  );
}

Future<LocalDatabaseFileSyncResult> _verifyAndUpdateLocalDatabaseFile(
  String dbFile, {
  required bool force,
  required Map<String, WebDbManifestEntry> manifestEntries,
}) async {
  try {
    final manifestEntry = manifestEntries[dbFile];
    final localFile = await _getLocalDatabaseFile(dbFile);
    final localExists = localFile.existsSync();
    final localSize = _fileSizeOrNull(localFile);
    final localSizeMatchesManifest = _matchesManifestSize(
      localFile,
      manifestEntry,
    );
    final localIsHealthy = localExists && isLocalDatabaseFileHealthy(localFile);

    if (!force && localExists && localSizeMatchesManifest && localIsHealthy) {
      return LocalDatabaseFileSyncResult(
        fileName: dbFile,
        existedBeforeSync: localExists,
        healthyBeforeSync: localIsHealthy,
        sizeMatchedManifestBeforeSync: localSizeMatchesManifest,
        existsAfterSync: localExists,
        healthyAfterSync: localIsHealthy,
        sizeMatchedManifestAfterSync: localSizeMatchesManifest,
        updated: false,
        expectedSizeBytes: manifestEntry?.fileSizeBytes,
        sizeBytesBeforeSync: localSize,
        sizeBytesAfterSync: localSize,
        manifestEntryMissing: manifestEntry == null,
      );
    }

    if (manifestEntry == null) {
      log.warning(
        'Local database manifest has no size entry for $dbFile; '
        'falling back to integrity-only validation.',
      );
    } else if (localExists && !localSizeMatchesManifest) {
      log.warning(
        'Local database size mismatch for $dbFile: '
        '${localFile.lengthSync()} != ${manifestEntry.fileSizeBytes}',
      );
    }

    final path = await updateLocalFile(
      _databaseFolder,
      dbFile,
      expectedSizeBytes: manifestEntry?.fileSizeBytes,
      downloadedFileValidator: isLocalDatabaseFileHealthy,
    );
    final updatedFile = File(path);
    final updatedExists = updatedFile.existsSync();
    final updatedHealthy =
        updatedExists && isLocalDatabaseFileHealthy(updatedFile);
    final updatedSize = _fileSizeOrNull(updatedFile);
    final updatedManifestEntries = await _loadLocalManifestEntries();
    final updatedManifestEntry =
        updatedManifestEntries[dbFile] ?? manifestEntry;
    final updatedSizeMatchesManifest = _matchesManifestSize(
      updatedFile,
      updatedManifestEntry,
    );

    return LocalDatabaseFileSyncResult(
      fileName: dbFile,
      existedBeforeSync: localExists,
      healthyBeforeSync: localIsHealthy,
      sizeMatchedManifestBeforeSync: localSizeMatchesManifest,
      existsAfterSync: updatedExists,
      healthyAfterSync: updatedHealthy,
      sizeMatchedManifestAfterSync: updatedSizeMatchesManifest,
      updated: updatedExists && updatedHealthy && updatedSizeMatchesManifest,
      expectedSizeBytes: updatedManifestEntry?.fileSizeBytes,
      sizeBytesBeforeSync: localSize,
      sizeBytesAfterSync: updatedSize,
      manifestEntryMissing: updatedManifestEntry == null,
    );
  } catch (error, stackTrace) {
    log.handle(
      error,
      stackTrace,
      'Failed to verify or update local database: $dbFile',
    );
    return LocalDatabaseFileSyncResult(
      fileName: dbFile,
      existedBeforeSync: false,
      healthyBeforeSync: false,
      sizeMatchedManifestBeforeSync: false,
      existsAfterSync: false,
      healthyAfterSync: false,
      sizeMatchedManifestAfterSync: false,
      updated: false,
    );
  }
}

bool isLocalDatabaseManifestHealthy(File file) {
  if (!file.existsSync()) {
    return false;
  }
  try {
    if (file.lengthSync() == 0) {
      return false;
    }
    return parseWebDbManifestEntries(file.readAsStringSync()).isNotEmpty;
  } catch (_) {
    return false;
  }
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

bool isLocalDatabaseFileHealthy(File file) {
  if (!file.existsSync()) {
    return false;
  }
  try {
    if (file.lengthSync() == 0) {
      return false;
    }
  } catch (_) {
    return false;
  }

  Database? database;
  try {
    database = sqlite3.open(file.path, mode: OpenMode.readOnly);
    final rows = database.select('PRAGMA integrity_check');
    if (rows.length != 1) {
      return false;
    }
    final values = rows.first.values;
    final value = values.isEmpty ? null : values.first.toString().toLowerCase();
    return value == 'ok';
  } catch (error) {
    final fileName = p.basename(file.path);
    log.warning('Local database integrity check failed for $fileName: $error');
    return false;
  } finally {
    database?.dispose();
  }
}

Future<Map<String, WebDbManifestEntry>> _loadLocalManifestEntries({
  bool refreshFromServer = false,
}) async {
  final manifestFile = await _getLocalDatabaseFile(_databaseManifestFile);
  if (refreshFromServer || !isLocalDatabaseManifestHealthy(manifestFile)) {
    await updateLocalFile(
      _databaseFolder,
      _databaseManifestFile,
      downloadedFileValidator: isLocalDatabaseManifestHealthy,
      refreshDbManifest: false,
    );
  }

  if (!manifestFile.existsSync()) {
    return const {};
  }
  try {
    return parseWebDbManifestEntries(await manifestFile.readAsString());
  } catch (error) {
    log.warning('Local database manifest read failed: $error');
    return const {};
  }
}

Future<File> _getLocalDatabaseFile(String fileName) async {
  final appFolder = await getAppFolder();
  return File(p.join(appFolder, _databaseFolder, fileName));
}

bool _matchesManifestSize(File file, WebDbManifestEntry? manifestEntry) {
  final expectedSize = manifestEntry?.fileSizeBytes;
  if (expectedSize == null) {
    return true;
  }
  try {
    return file.existsSync() && file.lengthSync() == expectedSize;
  } catch (_) {
    return false;
  }
}

int? _fileSizeOrNull(File file) {
  try {
    if (!file.existsSync()) {
      return null;
    }
    return file.lengthSync();
  } catch (_) {
    return null;
  }
}

String _normalizeLanguageCode(String? languageCode) {
  final normalized = (languageCode ?? 'en').trim().toLowerCase();
  if (AppConstants.languages.containsKey(normalized)) {
    return normalized;
  }
  return 'en';
}
