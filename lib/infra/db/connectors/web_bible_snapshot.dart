import 'dart:async';
import 'dart:js_interop';
import 'dart:js_interop_unsafe';

import 'package:drift/drift.dart';
import 'package:drift/wasm.dart';
import 'package:http/http.dart' as http;
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/infra/db/connectors/web_db_uri.dart';
import 'package:revelation/infra/db/connectors/web_db_version_sync_plan.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:web/web.dart' as web;

// Called inside withWebDatabaseOpenLock, which serializes slot selection across tabs.
// Only the inactive slot is ever replaced. Existing readers keep their snapshot.
Future<QueryExecutor> openWebBibleSnapshot(
  String file, {
  WebDbManifestEntry? manifest,
  bool installedOnly = false,
}) async {
  final name = file.substring(0, file.length - '.sqlite'.length);
  final prefs = await SharedPreferences.getInstance();
  await prefs.reload();
  // "~" is outside the module filename alphabet, so new catalog IDs cannot collide with a slot.
  final alternate = '$name~snapshot-b';
  final slotKey = 'web_bible_active::$name';
  final versionKey = 'web_db_version::$name';
  final createdKey = 'web_db_created_at::$name';
  final saved = prefs.getString(slotKey);
  final marker =
      (saved?.startsWith('a|') == true || saved?.startsWith('b|') == true)
      ? saved
      : null;
  final active = marker?.startsWith('b|') == true ? alternate : name;
  final activeToken = marker?.substring(2) ?? prefs.getString(versionKey);
  final installed = marker != null || prefs.containsKey(createdKey);
  final version = manifest?.versionInfo;
  final remoteToken = manifest?.snapshotIdentity;
  Future<QueryExecutor> openActive() => _readSlot(active);

  if (installedOnly) return openActive();
  if (installed) {
    QueryExecutor? existing;
    try {
      existing = await openActive();
      if (remoteToken == null || activeToken == remoteToken) return existing;
      final actual = await _inspect(existing, (db) => db.readVersionInfo());
      if (actual != null && version != null) {
        // An older tab or manifest mirror must not downgrade a newer installation.
        if (actual.compareReleaseTo(version) > 0) return existing;
        // Older app builds stored only a version token, directly against the original slot.
        if (marker == null &&
            actual == version &&
            activeToken ==
                buildLocalWebDbVersionToken(manifest!.versionToken)) {
          await prefs.setString(slotKey, 'a|$remoteToken');
          return existing;
        }
      }
    } catch (_) {
      // Browser storage can be evicted independently from preferences.
    }
    await existing?.close();
  }
  final next = active == name ? alternate : name;
  // On a first install, leave any unmarked pre-catalog database untouched.
  final release = await _SlotLease.acquire(next, exclusive: true);
  if (release == null) return openActive();
  try {
    final response = await http.get(
      buildWebDbUri(
        file,
        versionToken: manifest?.versionToken,
        forceNoCache: true,
      ),
      headers: const {'cache-control': 'no-cache'},
    );
    if (response.statusCode != 200 ||
        (manifest?.fileSizeBytes != null &&
            manifest!.fileSizeBytes != response.bodyBytes.length)) {
      throw StateError(
        'Bible download unavailable or incomplete: $file (${response.statusCode})',
      );
    }
    final probe = await WasmDatabase.probe(
      databaseName: next,
      sqlite3Uri: Uri.parse('sqlite3.wasm'),
      driftWorkerUri: Uri.parse('drift_worker.js'),
    );
    for (final existing in probe.existingDatabases.where(
      (item) => item.$2 == next,
    )) {
      await probe.deleteDatabase(existing);
    }
    final candidate = await _openSlot(next, () => response.bodyBytes);
    try {
      // Check the real released database rather than trusting its URL or byte count.
      await _inspect(candidate.resolvedExecutor, (db) async {
        final info = await db.readInfo(file, includeStrongCapability: false);
        if (info.canon != 'protestant_66' ||
            info.versification != 'kjv_protestant' ||
            (manifest?.bible?['moduleId'] != null &&
                manifest!.bible!['moduleId'] != info.moduleId) ||
            (info.schemaVersion ?? 0) > BibleModuleDB.supportedSchemaVersion ||
            (version != null &&
                (info.dataVersion != version.dataVersion ||
                    info.schemaVersion != version.schemaVersion ||
                    info.date?.isAtSameMomentAs(version.date) != true))) {
          throw FormatException('Incompatible Bible database: $file');
        }
      });
      if (candidate.chosenImplementation !=
          WasmStorageImplementation.inMemory) {
        // The active pointer is committed only after the candidate was opened and verified.
        await prefs.setString(
          createdKey,
          DateTime.now().toUtc().toIso8601String(),
        );
        await prefs.setString(
          slotKey,
          "${next == alternate ? 'b' : 'a'}|${remoteToken ?? ''}",
        );
      }
      await release();
      return await _leaseConnection(next, candidate.resolvedExecutor);
    } catch (_) {
      await _closePhysicalConnection(candidate.resolvedExecutor);
      rethrow;
    }
  } catch (error) {
    log.warning('Bible snapshot update unavailable for $file: $error');
    // Also covers pre-catalog databases installed before a marker was recorded.
    return openActive();
  } finally {
    await release();
  }
}

Future<WasmDatabaseResult> _openSlot(
  String name,
  FutureOr<Uint8List?> Function() initialize,
) => WasmDatabase.open(
  enableMigrations: false,
  databaseName: name,
  sqlite3Uri: Uri.parse('sqlite3.wasm'),
  driftWorkerUri: Uri.parse('drift_worker.js'),
  initializeDatabase: initialize,
);

Future<QueryExecutor> _readSlot(String name) async {
  final probe = await WasmDatabase.probe(
    databaseName: name,
    sqlite3Uri: Uri.parse('sqlite3.wasm'),
    driftWorkerUri: Uri.parse('drift_worker.js'),
  );
  final installed = {
    for (final item in probe.existingDatabases)
      if (item.$2 == name) item.$1,
  };
  final implementation = WasmStorageImplementation.values
      .where(
        (s) =>
            installed.contains(s.storageApi) &&
            probe.availableStorages.contains(s),
      )
      .firstOrNull;
  if (implementation == null)
    throw StateError('Bible snapshot not installed: $name');
  final connection = await probe.open(
    implementation,
    name,
    enableMigrations: false,
  );
  try {
    return await _leaseConnection(name, connection);
  } catch (_) {
    await _closePhysicalConnection(connection);
    rethrow;
  }
}

Future<T> _inspect<T>(
  QueryExecutor executor,
  Future<T> Function(BibleModuleDB) read,
) async {
  final db = BibleModuleDB(executor.interceptWith(_BorrowedExecutor()));
  try {
    return await read(db);
  } finally {
    await db.close();
  }
}

Future<QueryExecutor> _leaseConnection(
  String name,
  DatabaseConnection connection,
) async {
  final release = await _SlotLease.acquire(name, exclusive: false);
  if (release == null)
    throw StateError('Bible snapshot is being updated: $name');
  return connection.executor.interceptWith(
    _ReleaseOnClose(() async {
      try {
        await _closePhysicalConnection(connection);
      } finally {
        await release();
      }
    }),
  );
}

// LazyDatabase owns only the executor. The remote connection also owns a stream
// store, which can hold a BroadcastChannel for its entire lifetime on OPFS.
Future<void> _closePhysicalConnection(DatabaseConnection connection) async {
  try {
    await connection.streamQueries.close();
  } finally {
    await connection.close();
  }
}

class _BorrowedExecutor extends QueryInterceptor {
  @override
  Future<void> close(QueryExecutor inner) async {}
}

class _ReleaseOnClose extends QueryInterceptor {
  _ReleaseOnClose(this.release);
  final Future<void> Function() release;
  Future<void>? _closing;
  @override
  Future<void> close(QueryExecutor inner) => _closing ??= release();
}

class _SlotLease {
  static final _readers = <String, int>{};
  static Future<Future<void> Function()?> acquire(
    String name, {
    required bool exclusive,
  }) async {
    if (!web.window.navigator.has('locks')) {
      if (exclusive && (_readers[name] ?? 0) > 0) return null;
      _readers[name] = (_readers[name] ?? 0) + 1;
      var released = false;
      return () async {
        if (released) return;
        released = true;
        final left = _readers[name]! - 1;
        if (left == 0) {
          _readers.remove(name);
        } else {
          _readers[name] = left;
        }
      };
    }
    final acquired = Completer<bool>();
    final held = Completer<void>();
    final request = web.window.navigator.locks
        .request(
          'revelation-bible-slot::$name',
          web.LockOptions(
            mode: exclusive ? 'exclusive' : 'shared',
            ifAvailable: exclusive,
          ),
          ((web.Lock? lock) {
            acquired.complete(lock != null);
            return lock == null ? null : held.future.toJS;
          }).toJS,
        )
        .toDart;
    if (!await Future.any([acquired.future, request.then((_) => false)]))
      return null;
    return () async {
      if (!held.isCompleted) held.complete();
      await request;
    };
  }
}
