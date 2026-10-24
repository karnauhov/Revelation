import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/infra/storage/file_sync_utils.dart';

QueryExecutor openInstalledModule(String fileName) => LazyDatabase(() async {
  final folder = await getAppFolder();
  final file = File(p.join(folder, 'db', fileName));
  if (!file.existsSync()) {
    throw FileSystemException(
      'Install the reviewed local Bible candidate first',
      file.path,
    );
  }
  return NativeDatabase(file, enableMigrations: false);
});
