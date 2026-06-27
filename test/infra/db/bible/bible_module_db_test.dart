import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';

void main() {
  test(
    'reads module info, version metadata and verses from real schema',
    () async {
      final db = BibleModuleDB(NativeDatabase.memory());
      addTearDown(db.close);

      await db.customStatement('''
      CREATE TABLE info (
        code TEXT NOT NULL PRIMARY KEY,
        module_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        language TEXT NOT NULL,
        canon TEXT NOT NULL,
        versification TEXT NOT NULL,
        license TEXT NOT NULL,
        source_summary TEXT NOT NULL
      )
      ''');
      await db.customStatement('''
      CREATE TABLE db_metadata (
        key TEXT NOT NULL PRIMARY KEY,
        value TEXT NOT NULL
      )
      ''');
      await db.customStatement('''
      CREATE TABLE verses (
        verse_key TEXT NOT NULL PRIMARY KEY,
        text TEXT NOT NULL DEFAULT ''
      )
      ''');

      await db.customInsert(
        '''
      INSERT INTO info (
        code,
        module_id,
        title,
        description,
        language,
        canon,
        versification,
        license,
        source_summary
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
        variables: [
          Variable.withString('LXX_TR'),
          Variable.withString('lxx_tr'),
          Variable.withString('LXX / Textus Receptus'),
          Variable.withString('Greek Bible module'),
          Variable.withString('grc'),
          Variable.withString('protestant_66'),
          Variable.withString('kjv_protestant'),
          Variable.withString('CC BY 4.0'),
          Variable.withString('Test source'),
        ],
      );
      await db.customInsert('''
      INSERT INTO db_metadata (key, value)
      VALUES
        ('schema_version', '3'),
        ('data_version', '13'),
        ('date', '2026-05-31T06:20:48Z')
      ''');
      await db.customInsert('''
      INSERT INTO verses (verse_key, text)
      VALUES
        ('001', 'ἐν G1722 ἀρχῇ G746'),
        ('002', 'καὶ G2532 εἶπεν G2036')
      ''');

      final info = await db.readInfo('bible_lxx_tr.sqlite');
      final versionInfo = await db.readVersionInfo();
      final verses = await db.readVersesByKeys(const ['002', '001']);

      expect(info.fileName, 'bible_lxx_tr.sqlite');
      expect(info.code, 'LXX_TR');
      expect(info.displayTitle, 'LXX_TR');
      expect(versionInfo?.schemaVersion, 3);
      expect(versionInfo?.dataVersion, 13);
      expect(
        versionInfo?.date.toUtc().toIso8601String(),
        '2026-05-31T06:20:48.000Z',
      );
      expect(verses.map((verse) => '${verse.verseKey}:${verse.text}'), [
        '001:ἐν G1722 ἀρχῇ G746',
        '002:καὶ G2532 εἶπεν G2036',
      ]);
    },
  );
}
