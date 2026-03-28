import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/runtime/runtime_database_version_loader.dart';
import 'package:revelation/shared/config/app_constants.dart';

void main() {
  test(
    'getPreferredDatabaseVersionInfo uses the active runtime database when available',
    () async {
      final db = CommonDB(NativeDatabase.memory());
      addTearDown(db.close);
      await db.customStatement('''
      UPDATE db_metadata SET value = '4' WHERE key = 'schema_version'
      ''');
      await db.customStatement('''
      UPDATE db_metadata SET value = '21' WHERE key = 'data_version'
      ''');
      await db.customStatement('''
      UPDATE db_metadata
      SET value = '2026-03-23T09:00:00.000Z'
      WHERE key = 'date'
      ''');

      var fallbackCalls = 0;
      final info = await getPreferredDatabaseVersionInfo(
        AppConstants.commonDB,
        runtimeDatabaseAccessor: (dbFile) =>
            dbFile == AppConstants.commonDB ? db : null,
        fallbackLoader: (_) async {
          fallbackCalls += 1;
          return null;
        },
      );
      final probe = await db.customSelect('SELECT 1 AS value').getSingle();

      expect(info, isNotNull);
      expect(info!.schemaVersion, 4);
      expect(info.dataVersion, 21);
      expect(fallbackCalls, 0);
      expect(probe.read<int>('value'), 1);
    },
  );

  test(
    'getPreferredDatabaseVersionInfo falls back when runtime database is unavailable',
    () async {
      final fallbackInfo = DatabaseVersionInfo(
        schemaVersion: 7,
        dataVersion: 2,
        date: DateTime.utc(2026, 3, 24, 10, 0, 0),
      );

      final info = await getPreferredDatabaseVersionInfo(
        AppConstants.commonDB,
        runtimeDatabaseAccessor: (_) => null,
        fallbackLoader: (_) async => fallbackInfo,
      );

      expect(info, fallbackInfo);
    },
  );
}
