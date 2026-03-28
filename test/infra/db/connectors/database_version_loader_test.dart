import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/connectors/database_version_loader.dart';

void main() {
  test(
    'loadDatabaseVersionInfo returns parsed values and closes database',
    () async {
      final db = CommonDB(NativeDatabase.memory());
      await db.customStatement('''
      UPDATE db_metadata SET value = '4' WHERE key = 'schema_version'
      ''');
      await db.customStatement('''
      UPDATE db_metadata SET value = '42' WHERE key = 'data_version'
      ''');
      await db.customStatement('''
      UPDATE db_metadata
      SET value = '2026-03-21T12:34:56.000Z'
      WHERE key = 'date'
      ''');

      final info = await loadDatabaseVersionInfo(db);

      expect(info, isNotNull);
      expect(info!.schemaVersion, 4);
      expect(info.dataVersion, 42);
      expect(info.date.toUtc(), DateTime.utc(2026, 3, 21, 12, 34, 56));
      expect(db.customSelect('SELECT 1').get(), throwsA(anything));
    },
  );

  test(
    'readDatabaseVersionInfo returns parsed values without closing database',
    () async {
      final db = CommonDB(NativeDatabase.memory());
      addTearDown(db.close);
      await db.customStatement('''
      UPDATE db_metadata SET value = '5' WHERE key = 'schema_version'
      ''');
      await db.customStatement('''
      UPDATE db_metadata SET value = '17' WHERE key = 'data_version'
      ''');
      await db.customStatement('''
      UPDATE db_metadata
      SET value = '2026-03-22T08:15:00.000Z'
      WHERE key = 'date'
      ''');

      final info = await readDatabaseVersionInfo(db);
      final probe = await db.customSelect('SELECT 1 AS value').getSingle();

      expect(info, isNotNull);
      expect(info!.schemaVersion, 5);
      expect(info.dataVersion, 17);
      expect(info.date.toUtc(), DateTime.utc(2026, 3, 22, 8, 15, 0));
      expect(probe.read<int>('value'), 1);
    },
  );

  test(
    'loadDatabaseVersionInfo returns null for missing metadata rows',
    () async {
      final db = CommonDB(NativeDatabase.memory());
      await db.customStatement('DELETE FROM db_metadata');

      final info = await loadDatabaseVersionInfo(db);

      expect(info, isNull);
      expect(db.customSelect('SELECT 1').get(), throwsA(anything));
    },
  );

  test(
    'loadDatabaseVersionInfo returns null for invalid metadata values',
    () async {
      final db = CommonDB(NativeDatabase.memory());
      await db.customStatement('''
      UPDATE db_metadata SET value = 'x' WHERE key = 'schema_version'
      ''');
      await db.customStatement('''
      UPDATE db_metadata SET value = '1' WHERE key = 'data_version'
      ''');
      await db.customStatement('''
      UPDATE db_metadata SET value = 'invalid-date' WHERE key = 'date'
      ''');

      final info = await loadDatabaseVersionInfo(db);

      expect(info, isNull);
      expect(db.customSelect('SELECT 1').get(), throwsA(anything));
    },
  );

  test(
    'loadDatabaseVersionInfo returns null when metadata table is absent',
    () async {
      final db = CommonDB(NativeDatabase.memory());
      await db.customStatement('DROP TABLE db_metadata');

      final info = await loadDatabaseVersionInfo(db);

      expect(info, isNull);
      expect(db.customSelect('SELECT 1').get(), throwsA(anything));
    },
  );
}
