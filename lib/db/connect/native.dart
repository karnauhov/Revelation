import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/db/db_common.dart';
import 'package:revelation/db/db_localized.dart';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/utils/common.dart';

CommonDB getCommonDB() {
  return CommonDB(getLazyDatabase(AppConstants.commonDB));
}

LocalizedDB getLocalizedDB(String loc) {
  final dbFile = AppConstants.localizedDB.replaceAll('@loc', loc);
  return LocalizedDB(getLazyDatabase(dbFile));
}

LazyDatabase getLazyDatabase(dbFile) {
  final folder = "db";
  final db = LazyDatabase(() async {
    final needsUpdate = await isUpdateNeeded(folder, dbFile);
    if (needsUpdate) {
      final pathToFile = await updateLocalFile(folder, dbFile);
      final file = File(pathToFile);
      return NativeDatabase(file);
    } else {
      final appFolder = await getAppFolder();
      final file = File(p.join(appFolder, folder, dbFile));
      return NativeDatabase(file);
    }
  });
  return db;
}
