import 'dart:io';

import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:sqlite3/sqlite3.dart';

const _schemaVersionKey = 'schema_version';
const _dataVersionKey = 'data_version';
const _dateKey = 'date';

DatabaseVersionInfo? loadDatabaseVersionInfoFromFile(File file) {
  Database? database;
  try {
    database = sqlite3.open(file.path, mode: OpenMode.readOnly);
    final rows = database.select(
      '''
      SELECT key, value
      FROM db_metadata
      WHERE key IN (?, ?, ?)
      ''',
      [_schemaVersionKey, _dataVersionKey, _dateKey],
    );

    if (rows.isEmpty) {
      return null;
    }

    final values = <String, String>{};
    for (final row in rows) {
      final key = row['key']?.toString();
      final value = row['value']?.toString();
      if (key != null && value != null) {
        values[key] = value;
      }
    }

    final schemaVersion = int.tryParse(values[_schemaVersionKey] ?? '');
    final dataVersion = int.tryParse(values[_dataVersionKey] ?? '');
    final date = DateTime.tryParse(values[_dateKey] ?? '');
    if (schemaVersion == null || dataVersion == null || date == null) {
      return null;
    }

    return DatabaseVersionInfo(
      schemaVersion: schemaVersion,
      dataVersion: dataVersion,
      date: date,
    );
  } catch (_) {
    return null;
  } finally {
    database?.dispose();
  }
}
