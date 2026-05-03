import 'package:http/http.dart' as http;
import 'package:drift/drift.dart';
import 'package:drift/wasm.dart';
import 'package:get_it/get_it.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/database_version_loader.dart';
import 'package:revelation/infra/db/connectors/primary_source_file_info.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/infra/db/connectors/web_db_uri.dart';
import 'package:revelation/infra/db/connectors/web_db_version_probe_policy.dart';
import 'package:revelation/infra/db/connectors/web_db_version_sync_plan.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/core/logging/common_logger.dart';

CommonDB getCommonDB() {
  return CommonDB(connectOnWeb(AppConstants.commonDB));
}

LocalizedDB getLocalizedDB(String loc) {
  final dbFile = AppConstants.localizedDB.replaceAll('@loc', loc);
  return LocalizedDB(connectOnWeb(dbFile));
}

Future<DateTime?> getLocalDatabaseUpdatedAt(String dbFile) async {
  final databaseName = dbFile.replaceAll(".sqlite", "");
  final prefs = await SharedPreferences.getInstance();
  final createdAtIso = prefs.getString(_createdAtKey(databaseName));
  if (createdAtIso == null || createdAtIso.isEmpty) {
    return null;
  }
  return DateTime.tryParse(createdAtIso);
}

Future<DatabaseVersionInfo?> getLocalDatabaseVersionInfo(String dbFile) {
  return _getManifestDatabaseVersionInfo(dbFile).then((manifestInfo) {
    if (manifestInfo != null) {
      return manifestInfo;
    }

    if (dbFile == AppConstants.commonDB) {
      return loadDatabaseVersionInfo(CommonDB(connectOnWeb(dbFile)));
    }

    return loadDatabaseVersionInfo(LocalizedDB(connectOnWeb(dbFile)));
  });
}

Future<int?> getLocalDatabaseFileSize(String dbFile) async {
  final manifestEntry = await _getManifestDbEntry(dbFile);
  return manifestEntry?.fileSizeBytes;
}

Future<List<PrimarySourceFileInfo>> getLocalPrimarySourceFilesInfo() async =>
    const [];

Future<DatabaseVersionInfo?> _getManifestDatabaseVersionInfo(
  String dbFile,
) async {
  final manifestEntry = await _getManifestDbEntry(dbFile);
  return manifestEntry?.versionInfo;
}

Future<WebDbManifestEntry?> _getManifestDbEntry(String dbFile) async {
  final entries = await _loadWebDbManifestEntries();
  return entries[dbFile];
}

DatabaseConnection connectOnWeb(String dbFile) {
  return DatabaseConnection.delayed(
    Future(() async {
      final talker = GetIt.I<Talker>();
      final databaseName = dbFile.replaceAll(".sqlite", "");
      try {
        final result = await _openWasmDatabase(
          dbFile: dbFile,
          databaseName: databaseName,
          forceResetLocalDatabase: false,
        );

        return result.resolvedExecutor;
      } catch (e, st) {
        talker.handle(e, st, 'Failed to open Wasm DB before reset: $dbFile');
        try {
          final result = await _openWasmDatabase(
            dbFile: dbFile,
            databaseName: databaseName,
            forceResetLocalDatabase: true,
          );
          log.info('Web DB recovered after forced reset: $dbFile');
          return result.resolvedExecutor;
        } catch (retryError, retryStackTrace) {
          talker.handle(
            retryError,
            retryStackTrace,
            'Failed to open Wasm DB after reset: $dbFile',
          );
          rethrow;
        }
      }
    }),
  );
}

const _noCacheHeaders = <String, String>{
  'cache-control': 'no-cache, no-store, must-revalidate',
  'pragma': 'no-cache',
};

Future<Map<String, WebDbManifestEntry>>? _webDbManifestEntriesFuture;

String _versionKey(String databaseName) => 'web_db_version::$databaseName';

String _createdAtKey(String databaseName) => 'web_db_created_at::$databaseName';

Uri _buildDbUri(
  String dbFile, {
  String? versionToken,
  bool forceNoCache = false,
}) {
  return buildWebDbUri(
    dbFile,
    versionToken: versionToken,
    forceNoCache: forceNoCache,
  );
}

Future<WebDbVersionSyncPlan> _prepareWebDbVersionSync({
  required String dbFile,
  required String databaseName,
  required bool forceResetLocalDatabase,
}) async {
  final remoteVersionToken = await _fetchRemoteDbVersionToken(dbFile);
  if (remoteVersionToken == null) {
    log.warning('Unable to detect remote DB version for $dbFile');
    return planWebDbVersionSync(
      remoteVersionToken: null,
      localVersionToken: null,
      forceResetLocalDatabase: forceResetLocalDatabase,
    );
  }

  final prefs = await SharedPreferences.getInstance();
  final versionKey = _versionKey(databaseName);
  final localVersionToken = prefs.getString(versionKey);
  final syncPlan = planWebDbVersionSync(
    remoteVersionToken: remoteVersionToken,
    localVersionToken: localVersionToken,
    forceResetLocalDatabase: forceResetLocalDatabase,
  );
  if (!syncPlan.shouldResetLocalDatabase) {
    return syncPlan;
  }

  final probe = await WasmDatabase.probe(
    sqlite3Uri: Uri.parse('sqlite3.wasm'),
    driftWorkerUri: Uri.parse('drift_worker.js'),
    databaseName: databaseName,
  );

  final existingDatabases = probe.existingDatabases
      .where((entry) => entry.$2 == databaseName)
      .toList();

  if (existingDatabases.isNotEmpty) {
    for (final existingDb in existingDatabases) {
      await probe.deleteDatabase(existingDb);
    }
    log.info('Web DB recreated after update: $dbFile');
  }

  await prefs.remove(_createdAtKey(databaseName));
  return syncPlan;
}

Future<WasmDatabaseResult> _openWasmDatabase({
  required String dbFile,
  required String databaseName,
  required bool forceResetLocalDatabase,
}) async {
  final syncPlan = await _prepareWebDbVersionSync(
    dbFile: dbFile,
    databaseName: databaseName,
    forceResetLocalDatabase: forceResetLocalDatabase,
  );

  var downloadedDatabase = false;
  final result = await WasmDatabase.open(
    databaseName: databaseName,
    sqlite3Uri: Uri.parse('sqlite3.wasm'),
    driftWorkerUri: Uri.parse('drift_worker.js'),
    initializeDatabase: () async {
      final response = await http.get(
        _buildDbUri(
          dbFile,
          versionToken: syncPlan.versionToken,
          forceNoCache: true,
        ),
        headers: _noCacheHeaders,
      );
      if (response.statusCode == 200) {
        downloadedDatabase = true;
        return response.bodyBytes;
      } else {
        log.error(
          'Failed to load database file: $dbFile, status: ${response.statusCode}',
        );
        return null;
      }
    },
  );

  if (downloadedDatabase) {
    await _setWebDbCreatedAt(databaseName);
  }

  if (syncPlan.shouldCommitVersionAfterOpen) {
    await _commitWebDbVersion(databaseName, syncPlan.versionToken!);
  }

  if (result.missingFeatures.isNotEmpty) {
    log.info(
      'Using ${result.chosenImplementation} due to missing browser features: ${result.missingFeatures}',
    );
  }

  return result;
}

Future<void> _commitWebDbVersion(
  String databaseName,
  String versionToken,
) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(_versionKey(databaseName), versionToken);
}

Future<String?> _fetchRemoteDbVersionToken(String dbFile) async {
  final manifestVersionToken = await _fetchManifestDbVersionToken(dbFile);
  if (manifestVersionToken != null) {
    return manifestVersionToken;
  }

  final uri = _buildDbUri(dbFile, forceNoCache: true);

  if (shouldUseHeadForWebDbVersionProbe(uri: uri)) {
    try {
      final response = await http.head(uri, headers: _noCacheHeaders);
      if (response.statusCode >= 200 && response.statusCode < 400) {
        final token = _buildVersionToken(response.headers);
        if (token != null) {
          return token;
        }
      }
    } catch (e) {
      log.debug('HEAD request failed for DB version check ($dbFile): $e');
    }
  }

  try {
    final response = await http.get(
      uri,
      headers: {..._noCacheHeaders, 'range': 'bytes=0-0'},
    );
    if (response.statusCode == 200 || response.statusCode == 206) {
      final token = _buildVersionToken(response.headers);
      if (token != null) {
        return token;
      }
    }
  } catch (e) {
    log.debug('Range request failed for DB version check ($dbFile): $e');
  }

  // Fallback for servers that don't expose ETag/Last-Modified headers.
  try {
    final response = await http.get(uri, headers: _noCacheHeaders);
    if (response.statusCode == 200) {
      return 'body-fnv1a32:${_fnv1a32(response.bodyBytes)}';
    }
  } catch (e) {
    log.debug('GET request failed for DB version check ($dbFile): $e');
  }

  return null;
}

Future<String?> _fetchManifestDbVersionToken(String dbFile) async {
  final manifestEntry = await _getManifestDbEntry(dbFile);
  return manifestEntry?.versionToken;
}

Future<Map<String, WebDbManifestEntry>> _loadWebDbManifestEntries() {
  return _webDbManifestEntriesFuture ??= _fetchWebDbManifestEntries();
}

Future<Map<String, WebDbManifestEntry>> _fetchWebDbManifestEntries() async {
  final uri = buildWebDbManifestUri(forceNoCache: true);

  try {
    final response = await http.get(uri, headers: _noCacheHeaders);
    if (response.statusCode != 200) {
      if (response.statusCode != 404) {
        log.debug(
          'Manifest request returned ${response.statusCode} for DB version check: $uri',
        );
      }
      return const {};
    }

    final entries = parseWebDbManifestEntries(response.body);
    if (entries.isEmpty) {
      log.debug('Web DB manifest is empty or invalid: $uri');
    }
    return entries;
  } catch (e) {
    log.debug('Manifest request failed for DB version check: $e');
    return const {};
  }
}

String? _buildVersionToken(Map<String, String> headers) {
  final parts = <String>[];

  void addPart(String key) {
    final value = headers[key];
    if (value != null && value.isNotEmpty) {
      parts.add('$key:$value');
    }
  }

  addPart('etag');
  addPart('last-modified');
  addPart('content-length');
  addPart('content-range');
  addPart('x-amz-version-id');

  if (parts.isEmpty) {
    return null;
  }

  return parts.join('|');
}

Future<void> _setWebDbCreatedAt(String databaseName) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(
    _createdAtKey(databaseName),
    DateTime.now().toUtc().toIso8601String(),
  );
}

String _fnv1a32(List<int> bytes) {
  var hash = 0x811C9DC5;
  const prime = 0x01000193;
  const mask = 0xFFFFFFFF;

  for (final value in bytes) {
    hash ^= value;
    hash = (hash * prime) & mask;
  }

  return hash.toRadixString(16).padLeft(8, '0');
}
