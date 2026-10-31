import 'package:drift/drift.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';

class BibleModuleDB extends GeneratedDatabase {
  BibleModuleDB(super.e);

  @override
  int get schemaVersion => 4;

  Future<bool>? _commentSupport;

  Future<bool> _hasCommentColumn() {
    return _commentSupport ??= customSelect('PRAGMA table_info(verses)')
        .get()
        .then(
          (rows) => rows.any((row) => row.read<String>('name') == 'comment'),
        );
  }

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
    final version = await readVersionInfo();

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
      hasStrongNumbers: await readHasStrongNumbers(),
      schemaVersion: version?.schemaVersion,
      dataVersion: version?.dataVersion,
      date: version?.date,
    );
  }

  /// Uses the reader's token contract across the whole module. SQL only narrows
  /// candidates; Dart checks token boundaries consistently on native and web.
  Future<bool> readHasStrongNumbers() async {
    const batchSize = 64;
    String? afterKey;
    while (true) {
      final rows = await customSelect(
        '''
        SELECT verse_key, text FROM verses
        WHERE ${afterKey == null ? '' : 'verse_key > ? AND '}
              text GLOB '*[GgHh][0-9]*'
        ORDER BY verse_key
        LIMIT $batchSize
        ''',
        variables: [if (afterKey != null) Variable.withString(afterKey)],
      ).get();
      for (final row in rows) {
        if (row
            .read<String>('text')
            .trim()
            .split(RegExp(r'\s+'))
            .any(bibleStrongTokenPattern.hasMatch)) {
          return true;
        }
      }
      if (rows.length < batchSize) {
        return false;
      }
      afterKey = rows.last.read<String>('verse_key');
    }
  }

  Future<DatabaseVersionInfo?> readVersionInfo() async {
    final metadataTable = await customSelect(
      "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'db_metadata'",
    ).get();
    if (metadataTable.isEmpty) {
      return null;
    }
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
    final commentColumn = await _hasCommentColumn()
        ? 'comment'
        : "'' AS comment";
    final rows = await customSelect(
      '''
      SELECT verse_key, text, $commentColumn
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
            comment: row.read<String>('comment'),
          ),
        )
        .toList(growable: false);
  }

  Future<List<BibleVerseText>> readAllVerses() async {
    final commentColumn = await _hasCommentColumn()
        ? 'comment'
        : "'' AS comment";
    final rows = await customSelect('''
      SELECT verse_key, text, $commentColumn
      FROM verses
      WHERE trim(text) <> ''
      ORDER BY verse_key
      ''').get();

    return rows
        .map(
          (row) => BibleVerseText(
            verseKey: row.read<String>('verse_key'),
            text: row.read<String>('text'),
            comment: row.read<String>('comment'),
          ),
        )
        .toList(growable: false);
  }
}
