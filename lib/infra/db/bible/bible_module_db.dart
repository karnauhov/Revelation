import 'package:drift/drift.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';

class BibleModuleDB extends GeneratedDatabase {
  BibleModuleDB(super.e);

  @override
  int get schemaVersion => 3;

  @override
  Iterable<TableInfo<Table, Object?>> get allTables => const [];

  Future<BibleModuleInfo> readInfo(String fileName) async {
    final row = await customSelect('''
      SELECT code,
             module_id,
             title,
             description,
             language,
             canon,
             versification,
             license,
             source_summary
      FROM info
      LIMIT 1
      ''').getSingle();

    return BibleModuleInfo(
      fileName: fileName,
      code: row.read<String>('code'),
      moduleId: row.read<String>('module_id'),
      title: row.read<String>('title'),
      description: row.read<String>('description'),
      language: row.read<String>('language'),
      canon: row.read<String>('canon'),
      versification: row.read<String>('versification'),
      license: row.read<String>('license'),
      sourceSummary: row.read<String>('source_summary'),
    );
  }

  Future<DatabaseVersionInfo?> readVersionInfo() async {
    final rows = await customSelect(
      '''
      SELECT key, value
      FROM db_metadata
      WHERE key IN (?, ?, ?)
      ''',
      variables: [
        Variable.withString('schema_version'),
        Variable.withString('data_version'),
        Variable.withString('date'),
      ],
    ).get();

    if (rows.isEmpty) {
      return null;
    }

    final values = <String, String>{};
    for (final row in rows) {
      values[row.read<String>('key')] = row.read<String>('value');
    }

    final schemaVersion = int.tryParse(values['schema_version'] ?? '');
    final dataVersion = int.tryParse(values['data_version'] ?? '');
    final date = DateTime.tryParse(values['date'] ?? '');
    if (schemaVersion == null || dataVersion == null || date == null) {
      return null;
    }

    return DatabaseVersionInfo(
      schemaVersion: schemaVersion,
      dataVersion: dataVersion,
      date: date,
    );
  }

  Future<List<BibleVerseText>> readVersesByKeys(List<String> verseKeys) async {
    if (verseKeys.isEmpty) {
      return const <BibleVerseText>[];
    }

    final placeholders = List<String>.filled(verseKeys.length, '?').join(',');
    final rows = await customSelect(
      '''
      SELECT verse_key, text
      FROM verses
      WHERE verse_key IN ($placeholders)
      ORDER BY verse_key
      ''',
      variables: [
        for (final verseKey in verseKeys) Variable.withString(verseKey),
      ],
    ).get();

    return rows
        .map(
          (row) => BibleVerseText(
            verseKey: row.read<String>('verse_key'),
            text: row.read<String>('text'),
          ),
        )
        .toList(growable: false);
  }
}
