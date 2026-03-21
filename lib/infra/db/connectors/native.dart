import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:get_it/get_it.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/database_version_loader.dart';
import 'package:revelation/infra/db/connectors/primary_source_file_info.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';

CommonDB getCommonDB() {
  return CommonDB(getLazyDatabase(AppConstants.commonDB));
}

LocalizedDB getLocalizedDB(String loc) {
  final dbFile = AppConstants.localizedDB.replaceAll('@loc', loc);
  return LocalizedDB(getLazyDatabase(dbFile));
}

Future<DateTime?> getLocalDatabaseUpdatedAt(String dbFile) {
  const folder = "db";
  return getLastUpdateFileLocal(folder, dbFile);
}

Future<DatabaseVersionInfo?> getLocalDatabaseVersionInfo(String dbFile) async {
  final appFolder = await getAppFolder();
  final file = File(p.join(appFolder, 'db', dbFile));
  if (!file.existsSync()) {
    return null;
  }

  if (dbFile == AppConstants.commonDB) {
    return loadDatabaseVersionInfo(CommonDB(NativeDatabase(file)));
  }

  return loadDatabaseVersionInfo(LocalizedDB(NativeDatabase(file)));
}

Future<int?> getLocalDatabaseFileSize(String dbFile) async {
  final appFolder = await getAppFolder();
  final file = File(p.join(appFolder, 'db', dbFile));
  if (!file.existsSync()) {
    return null;
  }
  return file.lengthSync();
}

Future<List<PrimarySourceFileInfo>> getLocalPrimarySourceFilesInfo() async {
  try {
    final appFolder = await getAppFolder();
    final root = Directory(p.join(appFolder, 'primary_sources'));
    if (!root.existsSync()) {
      return const [];
    }

    final result = <PrimarySourceFileInfo>[];
    final visitedDirs = <String>{};
    final queue = <Directory>[root];

    while (queue.isNotEmpty) {
      final dir = queue.removeLast();
      final dirKey = await _directoryVisitKey(dir);
      if (!visitedDirs.add(dirKey)) {
        continue;
      }

      try {
        await for (final entity in dir.list(
          recursive: false,
          followLinks: false,
        )) {
          if (entity is Directory) {
            queue.add(entity);
            continue;
          }
          if (entity is File) {
            final relativePath = p
                .relative(entity.path, from: appFolder)
                .replaceAll('\\', '/');
            try {
              final stat = await entity.stat();
              result.add(
                PrimarySourceFileInfo(
                  relativePath: relativePath,
                  sizeBytes: stat.size,
                ),
              );
            } catch (error) {
              result.add(
                PrimarySourceFileInfo(
                  relativePath: relativePath,
                  error: 'stat failed: $error',
                ),
              );
            }
            continue;
          }
          if (entity is Link) {
            final linkPath = entity.path;
            final relativePath = p
                .relative(linkPath, from: appFolder)
                .replaceAll('\\', '/');
            try {
              final type = await FileSystemEntity.type(
                linkPath,
                followLinks: true,
              );
              if (type == FileSystemEntityType.directory) {
                queue.add(Directory(linkPath));
              } else if (type == FileSystemEntityType.file) {
                final file = File(linkPath);
                final stat = await file.stat();
                result.add(
                  PrimarySourceFileInfo(
                    relativePath: relativePath,
                    sizeBytes: stat.size,
                  ),
                );
              } else {
                result.add(
                  PrimarySourceFileInfo(
                    relativePath: relativePath,
                    error: 'link target is not readable',
                  ),
                );
              }
            } catch (error) {
              result.add(
                PrimarySourceFileInfo(
                  relativePath: relativePath,
                  error: 'link resolve failed: $error',
                ),
              );
            }
          }
        }
      } catch (error) {
        final relativePath = p
            .relative(dir.path, from: appFolder)
            .replaceAll('\\', '/');
        result.add(
          PrimarySourceFileInfo(
            relativePath: relativePath,
            error: 'list failed: $error',
          ),
        );
      }
    }

    result.sort((a, b) => a.relativePath.compareTo(b.relativePath));
    return result;
  } catch (error) {
    return [
      PrimarySourceFileInfo(
        relativePath: 'primary_sources',
        error: 'list failed: $error',
      ),
    ];
  }
}

Future<String> _directoryVisitKey(Directory dir) async {
  try {
    return (await dir.resolveSymbolicLinks()).toLowerCase();
  } catch (_) {
    return p.normalize(dir.absolute.path).toLowerCase();
  }
}

LazyDatabase getLazyDatabase(dbFile) {
  final folder = "db";
  final db = LazyDatabase(() async {
    final talker = GetIt.I<Talker>();

    try {
      final needsUpdate = await isUpdateNeeded(folder, dbFile);
      if (needsUpdate) {
        final pathToFile = await updateLocalFile(folder, dbFile);
        final file = File(pathToFile);
        return NativeDatabase(file);
      } else {
        final appFolder = await getAppFolder();
        final file = File(p.join(appFolder, folder, dbFile));
        await file.parent.create(recursive: true);
        return NativeDatabase(file);
      }
    } catch (e, st) {
      talker.handle(e, st, 'Failed to open native DB: $dbFile');
      rethrow;
    }
  });
  return db;
}
