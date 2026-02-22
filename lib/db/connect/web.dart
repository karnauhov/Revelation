import 'package:http/http.dart' as http;
import 'package:drift/drift.dart';
import 'package:drift/wasm.dart';
import 'package:get_it/get_it.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:revelation/db/db_common.dart';
import 'package:revelation/db/db_localized.dart';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/utils/common.dart';

CommonDB getCommonDB() {
  return CommonDB(connectOnWeb(AppConstants.commonDB));
}

LocalizedDB getLocalizedDB(String loc) {
  final dbFile = AppConstants.localizedDB.replaceAll('@loc', loc);
  return LocalizedDB(connectOnWeb(dbFile));
}

DatabaseConnection connectOnWeb(String dbFile) {
  return DatabaseConnection.delayed(
    Future(() async {
      final talker = GetIt.I<Talker>();
      final databaseName = dbFile.replaceAll(".sqlite", "");
      try {
        final remoteVersionToken = await _syncWebDbVersion(
          dbFile: dbFile,
          databaseName: databaseName,
        );

        final result = await WasmDatabase.open(
          databaseName: databaseName,
          sqlite3Uri: Uri.parse('sqlite3.wasm'),
          driftWorkerUri: Uri.parse('drift_worker.js'),
          initializeDatabase: () async {
            final response = await http.get(
              _buildDbUri(
                dbFile,
                versionToken: remoteVersionToken,
                forceNoCache: true,
              ),
              headers: _noCacheHeaders,
            );
            if (response.statusCode == 200) {
              await _setWebDbCreatedAt(databaseName);
              return response.bodyBytes;
            } else {
              log.error(
                'Failed to load database file: $dbFile, status: ${response.statusCode}',
              );
              return null;
            }
          },
        );

        if (result.missingFeatures.isNotEmpty) {
          log.info(
            'Using ${result.chosenImplementation} due to missing browser features: ${result.missingFeatures}',
          );
        }

        return result.resolvedExecutor;
      } catch (e, st) {
        talker.handle(e, st, 'Failed to open Wasm DB: $dbFile');
        rethrow;
      }
    }),
  );
}

const _noCacheHeaders = <String, String>{
  'cache-control': 'no-cache, no-store, must-revalidate',
  'pragma': 'no-cache',
};

String _versionKey(String databaseName) => 'web_db_version::$databaseName';

String _createdAtKey(String databaseName) => 'web_db_created_at::$databaseName';

Uri _buildDbUri(
  String dbFile, {
  String? versionToken,
  bool forceNoCache = false,
}) {
  final query = <String, String>{};
  if (versionToken != null && versionToken.isNotEmpty) {
    query['rev'] = versionToken;
  }
  if (forceNoCache) {
    query['ts'] = DateTime.now().millisecondsSinceEpoch.toString();
  }
  return Uri(path: '/db/$dbFile', queryParameters: query);
}

Future<String?> _syncWebDbVersion({
  required String dbFile,
  required String databaseName,
}) async {
  final remoteVersionToken = await _fetchRemoteDbVersionToken(dbFile);
  if (remoteVersionToken == null) {
    log.warning('Unable to detect remote DB version for $dbFile');
    return null;
  }

  final prefs = await SharedPreferences.getInstance();
  final versionKey = _versionKey(databaseName);
  final localVersionToken = prefs.getString(versionKey);
  if (localVersionToken == remoteVersionToken) {
    return remoteVersionToken;
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
  await prefs.setString(versionKey, remoteVersionToken);
  return remoteVersionToken;
}

Future<String?> _fetchRemoteDbVersionToken(String dbFile) async {
  final uri = _buildDbUri(dbFile, forceNoCache: true);

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
