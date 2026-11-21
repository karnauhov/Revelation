import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/infra/db/connectors/local_database_sync_native.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:sqlite3/sqlite3.dart';

export 'local_database_sync_native.dart' show listInstalledBibleModuleFiles;

final _bibleModuleFilePattern = RegExp(
  r'^bible_[A-Za-z0-9_]+\.sqlite$',
  caseSensitive: false,
);

Future<List<String>> listLocalBibleModuleFiles({
  String defaultModuleFile = AppConstants.defaultBibleModuleDB,
}) async {
  return discoverKnownBibleModuleFiles(defaultModuleFile: defaultModuleFile);
}

Future<Map<String, WebDbManifestEntry>> readBibleModuleManifest() =>
    readLocalBibleModuleManifest();

QueryExecutor? openInstalledBibleModuleExecutor(String dbFile) {
  if (!_bibleModuleFilePattern.hasMatch(dbFile)) return null;
  return LazyDatabase(() async {
    final appFolder = await getAppFolder();
    final file = File(p.join(appFolder, 'db', dbFile));
    if (!file.existsSync())
      throw FileSystemException('Bible module file not found', file.path);
    return NativeDatabase.opened(
      sqlite3.open(file.path, mode: OpenMode.readOnly),
      enableMigrations: false,
    );
  });
}

QueryExecutor openBibleModuleExecutor(String dbFile) {
  if (!_bibleModuleFilePattern.hasMatch(dbFile)) {
    throw ArgumentError.value(dbFile, 'dbFile', 'Invalid Bible module file');
  }

  return LazyDatabase(() async {
    await verifyAndUpdateLocalDatabaseFile(dbFile);
    final appFolder = await getAppFolder();
    final file = File(p.join(appFolder, 'db', dbFile));
    if (!file.existsSync()) {
      throw FileSystemException('Bible module file not found', file.path);
    }
    return NativeDatabase(file, enableMigrations: false);
  });
}
