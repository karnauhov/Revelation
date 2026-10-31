import 'dart:io';

import 'package:drift/drift.dart' hide isNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';

void main() {
  for (final version in [3, 4]) {
    test('detects Strong tokens throughout schema $version module', () async {
      final temporary = await Directory.systemTemp.createTemp('rev300-db-');
      addTearDown(() => temporary.delete(recursive: true));
      final db = BibleModuleDB(
        NativeDatabase(
          File('${temporary.path}/bible_test.sqlite'),
          enableMigrations: false,
          setup: (database) => database.execute('PRAGMA user_version=$version'),
        ),
      );
      addTearDown(db.close);
      await db.customStatement('''CREATE TABLE verses (
        verse_key TEXT PRIMARY KEY, text TEXT NOT NULL
        ${version == 4 ? ", comment TEXT NOT NULL DEFAULT ''" : ''}
      )''');
      expect(await db.readHasStrongNumbers(), isFalse);
      // Comments and partial words are not reader Strong tokens. More than one
      // candidate batch must not prevent finding a later genuine annotation.
      for (var i = 0; i < 65; i++) {
        await db.customStatement(
          'INSERT INTO verses VALUES (?, ?${version == 4 ? ', ?' : ''})',
          [
            i.toString().padLeft(3, '0'),
            'AG123 G12x H3. Gword',
            if (version == 4) 'G746',
          ],
        );
      }
      expect(await db.readHasStrongNumbers(), isFalse);
      for (final token in ['G746', 'H7225', 'g1722', 'h430']) {
        await db.customStatement(
          'INSERT INTO verses (verse_key, text) VALUES (?, ?)',
          ['999', 'Word\t$token\nnext'],
        );
        expect(await db.readHasStrongNumbers(), isTrue, reason: token);
        await db.customStatement("DELETE FROM verses WHERE verse_key = '999'");
      }
      expect(await db.readHasStrongNumbers(), isFalse);
    });
  }

  for (final version in [3, 4]) {
    test('reads schema $version without changing its version', () async {
      final temporary = await Directory.systemTemp.createTemp('rev201-db-');
      addTearDown(() => temporary.delete(recursive: true));
      final db = BibleModuleDB(
        NativeDatabase(
          File('${temporary.path}/bible_test.sqlite'),
          enableMigrations: false,
          setup: (database) {
            database.execute('PRAGMA user_version=$version');
            database.execute('''CREATE TABLE verses (
              verse_key TEXT PRIMARY KEY, text TEXT NOT NULL
              ${version == 4 ? ", comment TEXT NOT NULL DEFAULT ''" : ''}
            )''');
            database.execute(
              version == 4
                  ? "INSERT INTO verses VALUES ('001','Слово','Окрема примітка'),('002','Інше','')"
                  : "INSERT INTO verses VALUES ('001','Слово'),('002','Інше')",
            );
          },
        ),
      );
      addTearDown(db.close);
      final verses = await db.readVersesByKeys(['002', '001']);
      expect(verses.first.text, 'Слово');
      expect(verses.first.comment, version == 4 ? 'Окрема примітка' : '');
      expect(verses.last.comment, '');
      expect(await db.readAllVerses(), verses);
      expect(await db.readVersesByKeys([]), isEmpty);
      final pragma = await db.customSelect('PRAGMA user_version').getSingle();
      expect(pragma.read<int>('user_version'), version);
    });
  }

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
      final allVerses = await db.readAllVerses();

      expect(info.fileName, 'bible_lxx_tr.sqlite');
      expect(info.code, 'LXX_TR');
      expect(info.displayTitle, 'LXX_TR');
      expect(info.hasStrongNumbers, isTrue);
      expect(info.schemaVersion, 3);
      expect(info.dataVersion, 13);
      expect(info.date, DateTime.utc(2026, 5, 31, 6, 20, 48));
      expect(allVerses.map((verse) => verse.verseKey), ['001', '002']);
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

      for (final metadata in [
        "('schema_version','3'),('data_version','13')",
        "('schema_version','3'),('data_version','13'),('date','invalid')",
        "('schema_version','invalid'),('data_version','13'),('date','2026-10-24')",
      ]) {
        await db.customStatement('DELETE FROM db_metadata');
        await db.customStatement('INSERT INTO db_metadata VALUES $metadata');
        final incomplete = await db.readInfo('bible_lxx_tr.sqlite');
        expect(incomplete.schemaVersion, isNull);
        expect(incomplete.dataVersion, isNull);
        expect(incomplete.date, isNull);
        expect(incomplete.title, info.title);
      }
      await db.customStatement('DROP TABLE db_metadata');
      final legacy = await db.readInfo('bible_lxx_tr.sqlite');
      expect(legacy.schemaVersion, isNull);
      expect(legacy.dataVersion, isNull);
      expect(legacy.date, isNull);
      expect(legacy.title, info.title);
    },
  );
}
