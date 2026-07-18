import 'dart:convert';
import 'dart:io';

import 'package:path/path.dart' as p;
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/infra/db/connectors/database_version_file_loader.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/local_database_sync_result.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/infra/remote/supabase/server_manager.dart';
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
    final localVersionIsNewerThanManifest =
        localIsHealthy &&
        _isLocalDatabaseVersionNewerThanManifest(localFile, manifestEntry);

    if (!force &&
        localExists &&
        localIsHealthy &&
        (localSizeMatchesManifest || localVersionIsNewerThanManifest)) {
      if (localVersionIsNewerThanManifest && !localSizeMatchesManifest) {
        log.warning(
          'Local database $dbFile is newer than the manifest entry; '
          'keeping the local file.',
        );
      }
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

Future<List<String>> discoverKnownBibleModuleFiles({
  String defaultModuleFile = AppConstants.defaultBibleModuleDB,
}) async {
  final files = <String>{};
  final manifestEntries = await _loadLocalManifestEntries(
    refreshFromServer: true,
  );
  files.addAll(manifestEntries.keys.where(_isBibleModuleDatabaseFileName));

  try {
    final appFolder = await getAppFolder();
    final dbFolder = Directory(p.join(appFolder, _databaseFolder));
    if (dbFolder.existsSync()) {
      await for (final entity in dbFolder.list(
        recursive: false,
        followLinks: false,
      )) {
        if (entity is File) {
          final fileName = p.basename(entity.path);
          if (_isBibleModuleDatabaseFileName(fileName) &&
              isLocalDatabaseFileHealthy(entity)) {
            files.add(fileName);
          }
        }
      }
    }
  } catch (error) {
    log.warning('Local Bible module discovery failed: $error');
  }

  if (_isBibleModuleDatabaseFileName(defaultModuleFile)) {
    files.add(defaultModuleFile);
  }

  final sortedFiles = files.toList()..sort();
  if (sortedFiles.remove(defaultModuleFile)) {
    sortedFiles.insert(0, defaultModuleFile);
  }
  return List<String>.unmodifiable(sortedFiles);
}

bool _isBibleModuleDatabaseFileName(String fileName) {
  return RegExp(
    r'^bible_[A-Za-z0-9_]+\.sqlite$',
    caseSensitive: false,
  ).hasMatch(fileName);
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
  if (refreshFromServer) {
    await _refreshLocalManifestFromServer(manifestFile);
  } else if (!isLocalDatabaseManifestHealthy(manifestFile)) {
    await _downloadLocalManifestFile();
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

Future<void> _refreshLocalManifestFromServer(File manifestFile) async {
  final localEntries = _readManifestEntriesOrEmpty(manifestFile);
  final remoteEntries = await _downloadManifestEntriesFromServer();
  if (remoteEntries == null) {
    if (localEntries.isEmpty && !isLocalDatabaseManifestHealthy(manifestFile)) {
      await _downloadLocalManifestFile();
    }
    return;
  }

  final mergedEntries = _mergeManifestEntries(
    localEntries: localEntries,
    remoteEntries: remoteEntries,
  );
  if (mergedEntries.isEmpty) {
    return;
  }

  if (!manifestFile.existsSync() ||
      !_manifestEntriesEqual(localEntries, mergedEntries)) {
    await _writeManifestEntries(manifestFile, mergedEntries);
  }
}

Future<void> _downloadLocalManifestFile() async {
  await updateLocalFile(
    _databaseFolder,
    _databaseManifestFile,
    downloadedFileValidator: isLocalDatabaseManifestHealthy,
    refreshDbManifest: false,
  );
}

Future<Map<String, WebDbManifestEntry>?>
_downloadManifestEntriesFromServer() async {
  try {
    final bytes = await ServerManager().downloadDB(
      _databaseFolder,
      _databaseManifestFile,
    );
    if (bytes == null || bytes.isEmpty) {
      return null;
    }
    final entries = parseWebDbManifestEntries(utf8.decode(bytes));
    return entries.isEmpty ? null : entries;
  } catch (error) {
    log.warning('Remote database manifest refresh failed: $error');
    return null;
  }
}

Map<String, WebDbManifestEntry> _readManifestEntriesOrEmpty(File manifestFile) {
  if (!manifestFile.existsSync()) {
    return const {};
  }
  try {
    return parseWebDbManifestEntries(manifestFile.readAsStringSync());
  } catch (_) {
    return const {};
  }
}

Map<String, WebDbManifestEntry> _mergeManifestEntries({
  required Map<String, WebDbManifestEntry> localEntries,
  required Map<String, WebDbManifestEntry> remoteEntries,
}) {
  final merged = <String, WebDbManifestEntry>{};
  final names = <String>{...localEntries.keys, ...remoteEntries.keys}.toList()
    ..sort();
  for (final name in names) {
    final localEntry = localEntries[name];
    final remoteEntry = remoteEntries[name];
    if (localEntry == null) {
      merged[name] = remoteEntry!;
    } else if (remoteEntry == null) {
      merged[name] = localEntry;
    } else {
      final remoteIsAtLeastAsNew =
          _compareDatabaseReleaseVersion(
            remoteEntry.versionInfo,
            localEntry.versionInfo,
          ) >=
          0;
      merged[name] = remoteIsAtLeastAsNew ? remoteEntry : localEntry;
    }
  }
  return merged;
}

Future<void> _writeManifestEntries(
  File manifestFile,
  Map<String, WebDbManifestEntry> entries,
) async {
  await manifestFile.parent.create(recursive: true);
  final databases = <String, Object?>{};
  final sortedEntries = entries.entries.toList()
    ..sort((a, b) => a.key.compareTo(b.key));
  for (final entry in sortedEntries) {
    databases[entry.key] = <String, Object?>{
      'versionToken': entry.value.versionToken,
      'schemaVersion': entry.value.versionInfo.schemaVersion,
      'dataVersion': entry.value.versionInfo.dataVersion,
      'date': entry.value.versionInfo.date.toUtc().toIso8601String(),
      if (entry.value.fileSizeBytes != null)
        'fileSizeBytes': entry.value.fileSizeBytes,
    };
  }

  await manifestFile.writeAsString(
    jsonEncode(<String, Object?>{
          'version': 1,
          'generatedAt': DateTime.now().toUtc().toIso8601String(),
          'databases': databases,
        }) +
        '\n',
    flush: true,
  );
}

Future<File> _getLocalDatabaseFile(String fileName) async {
  final appFolder = await getAppFolder();
  return File(p.join(appFolder, _databaseFolder, fileName));
}

bool _isLocalDatabaseVersionNewerThanManifest(
  File localFile,
  WebDbManifestEntry? manifestEntry,
) {
  if (manifestEntry == null) {
    return false;
  }
  final localVersion = loadDatabaseVersionInfoFromFile(localFile);
  if (localVersion == null) {
    return false;
  }
  return _compareDatabaseReleaseVersion(
        localVersion,
        manifestEntry.versionInfo,
      ) >
      0;
}

int _compareDatabaseReleaseVersion(
  DatabaseVersionInfo left,
  DatabaseVersionInfo right,
) {
  final schemaVersionComparison = left.schemaVersion.compareTo(
    right.schemaVersion,
  );
  if (schemaVersionComparison != 0) {
    return schemaVersionComparison;
  }

  final dataVersionComparison = left.dataVersion.compareTo(right.dataVersion);
  if (dataVersionComparison != 0) {
    return dataVersionComparison;
  }

  return 0;
}

bool _manifestEntriesEqual(
  Map<String, WebDbManifestEntry> left,
  Map<String, WebDbManifestEntry> right,
) {
  if (left.length != right.length) {
    return false;
  }
  for (final entry in left.entries) {
    final rightEntry = right[entry.key];
    if (rightEntry == null ||
        rightEntry.versionToken != entry.value.versionToken ||
        rightEntry.versionInfo != entry.value.versionInfo ||
        rightEntry.fileSizeBytes != entry.value.fileSizeBytes) {
      return false;
    }
  }
  return true;
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
