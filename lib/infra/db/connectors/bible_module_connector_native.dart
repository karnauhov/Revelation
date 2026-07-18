import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/infra/db/connectors/local_database_sync_native.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/shared/config/app_constants.dart';

final _bibleModuleFilePattern = RegExp(
  r'^bible_[A-Za-z0-9_]+\.sqlite$',
  caseSensitive: false,
);

Future<List<String>> listLocalBibleModuleFiles({
  String defaultModuleFile = AppConstants.defaultBibleModuleDB,
}) async {
  return discoverKnownBibleModuleFiles(defaultModuleFile: defaultModuleFile);
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
