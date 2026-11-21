import 'dart:typed_data';

import 'package:drift/wasm.dart';
import 'package:sqlite3/wasm.dart';
import 'package:revelation/infra/db/connectors/web_database_open_lock.dart';
import 'catalog_sqlite_fixture.dart';

class CatalogSandbox {
  CatalogSandbox._(this.sqlite, this.fs);
  final WasmSqlite3 sqlite;
  final InMemoryFileSystem fs;
  static Future<CatalogSandbox> create() async {
    final sqlite = await WasmSqlite3.loadFromUrl(Uri.parse('sqlite3.wasm'));
    final fs = InMemoryFileSystem();
    sqlite.registerVirtualFileSystem(fs, makeDefault: true);
    return CatalogSandbox._(sqlite, fs);
  }

  Future<Uint8List> moduleBytes(String language, int revision) async {
    final path = '/${language}_$revision.sqlite';
    final db = sqlite.open(path);
    try {
      populateCatalogModule(db, language, revision);
    } finally {
      db.dispose();
    }
    return Uint8List.fromList(fs.fileData[path]!);
  }

  Future<void> forgetCatalogManifest() async {}
  void reopenPreferences() {}
  Future<void> dispose(List<String> files) async {
    sqlite.unregisterVirtualFileSystem(fs);
    final names = {
      for (final file in files) ...[
        file.replaceAll('.sqlite', ''),
        "${file.replaceAll('.sqlite', '')}~snapshot-b",
      ],
    };
    await withWebDatabaseOpenLock(() async {
      for (final name in names) {
        final probe = await WasmDatabase.probe(
          databaseName: name,
          sqlite3Uri: Uri.parse('sqlite3.wasm'),
          driftWorkerUri: Uri.parse('drift_worker.js'),
        );
        for (final item in probe.existingDatabases.where(
          (item) => item.$2 == name,
        )) {
          await probe.deleteDatabase(item);
        }
      }
    });
  }
}
