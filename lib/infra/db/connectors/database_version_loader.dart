import 'package:drift/drift.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';

const _schemaVersionKey = 'schema_version';
const _dataVersionKey = 'data_version';
const _dateKey = 'date';

Future<DatabaseVersionInfo?> readDatabaseVersionInfo(
  GeneratedDatabase database,
) async {
  try {
    final rows = await database
        .customSelect(
          '''
      SELECT key, value
      FROM db_metadata
      WHERE key IN (?, ?, ?)
      ''',
          variables: [
            Variable.withString(_schemaVersionKey),
            Variable.withString(_dataVersionKey),
            Variable.withString(_dateKey),
          ],
        )
        .get();

    if (rows.isEmpty) {
      return null;
    }

    final values = <String, String>{};
    for (final row in rows) {
      final key = row.read<String>('key');
      final value = row.read<String>('value');
      values[key] = value;
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
  }
}

Future<DatabaseVersionInfo?> loadDatabaseVersionInfo(
  GeneratedDatabase database,
) async {
  try {
    return readDatabaseVersionInfo(database);
  } catch (_) {
    return null;
  } finally {
    await database.close();
  }
}
