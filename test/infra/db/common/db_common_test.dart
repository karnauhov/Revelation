import 'dart:io';

import 'package:drift/drift.dart' hide isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/infra/db/common/db_common.dart';

void main() {
  test('Raw common table declarations fail fast outside generated DB context', () {
    void expectUnsupported(Object? Function() callback) {
      expect(callback, throwsA(isA<UnsupportedError>()));
    }

    expect(CommonDbMetadata().tableName, 'db_metadata');
    expectUnsupported(() => CommonDbMetadata().key);
    expectUnsupported(() => CommonDbMetadata().value);
    expectUnsupported(() => CommonDbMetadata().primaryKey);

    expectUnsupported(() => GreekWords().id);
    expectUnsupported(() => GreekWords().word);
    expectUnsupported(() => GreekWords().category);
    expectUnsupported(() => GreekWords().synonyms);
    expectUnsupported(() => GreekWords().origin);
    expectUnsupported(() => GreekWords().usage);

    expectUnsupported(() => CommonResources().key);
    expectUnsupported(() => CommonResources().fileName);
    expectUnsupported(() => CommonResources().mimeType);
    expectUnsupported(() => CommonResources().data);
    expectUnsupported(() => CommonResources().primaryKey);

    expectUnsupported(() => PrimarySources().id);
    expectUnsupported(() => PrimarySources().family);
    expectUnsupported(() => PrimarySources().number);
    expectUnsupported(() => PrimarySources().groupKind);
    expectUnsupported(() => PrimarySources().sortOrder);
    expectUnsupported(() => PrimarySources().versesCount);
    expectUnsupported(() => PrimarySources().previewResourceKey);
    expectUnsupported(() => PrimarySources().defaultMaxScale);
    expectUnsupported(() => PrimarySources().canShowImages);
    expectUnsupported(() => PrimarySources().imagesAreMonochrome);
    expectUnsupported(() => PrimarySources().notes);
    expectUnsupported(() => PrimarySources().primaryKey);

    expectUnsupported(() => PrimarySourceLinks().sourceId);
    expectUnsupported(() => PrimarySourceLinks().linkId);
    expectUnsupported(() => PrimarySourceLinks().sortOrder);
    expectUnsupported(() => PrimarySourceLinks().linkRole);
    expectUnsupported(() => PrimarySourceLinks().url);
    expectUnsupported(() => PrimarySourceLinks().primaryKey);

    expectUnsupported(() => PrimarySourceAttributions().sourceId);
    expectUnsupported(() => PrimarySourceAttributions().attributionId);
    expectUnsupported(() => PrimarySourceAttributions().sortOrder);
    expectUnsupported(() => PrimarySourceAttributions().displayText);
    expectUnsupported(() => PrimarySourceAttributions().url);
    expectUnsupported(() => PrimarySourceAttributions().primaryKey);

    expectUnsupported(() => PrimarySourcePages().sourceId);
    expectUnsupported(() => PrimarySourcePages().pageName);
    expectUnsupported(() => PrimarySourcePages().sortOrder);
    expectUnsupported(() => PrimarySourcePages().contentRef);
    expectUnsupported(() => PrimarySourcePages().imagePath);
    expectUnsupported(() => PrimarySourcePages().primaryKey);

    expectUnsupported(() => PrimarySourceWords().sourceId);
    expectUnsupported(() => PrimarySourceWords().pageName);
    expectUnsupported(() => PrimarySourceWords().wordIndex);
    expectUnsupported(() => PrimarySourceWords().wordText);
    expectUnsupported(() => PrimarySourceWords().strongNumber);
    expectUnsupported(() => PrimarySourceWords().strongPronounce);
    expectUnsupported(() => PrimarySourceWords().strongXShift);
    expectUnsupported(() => PrimarySourceWords().missingCharIndexesJson);
    expectUnsupported(() => PrimarySourceWords().rectanglesJson);
    expectUnsupported(() => PrimarySourceWords().primaryKey);

    expectUnsupported(() => PrimarySourceVerses().sourceId);
    expectUnsupported(() => PrimarySourceVerses().pageName);
    expectUnsupported(() => PrimarySourceVerses().verseIndex);
    expectUnsupported(() => PrimarySourceVerses().chapterNumber);
    expectUnsupported(() => PrimarySourceVerses().verseNumber);
    expectUnsupported(() => PrimarySourceVerses().labelX);
    expectUnsupported(() => PrimarySourceVerses().labelY);
    expectUnsupported(() => PrimarySourceVerses().wordIndexesJson);
    expectUnsupported(() => PrimarySourceVerses().contoursJson);
    expectUnsupported(() => PrimarySourceVerses().primaryKey);
  });

  test('Common table definitions expose stable schema contract', () {
    final db = CommonDB(NativeDatabase.memory());
    addTearDown(db.close);

    final metadata = db.commonDbMetadata;
    expect(metadata.tableName, 'db_metadata');
    expect(metadata.primaryKey, {metadata.key});
    expect(metadata.value.name, 'value');

    final greekWords = db.greekWords;
    expect(greekWords.id.name, 'id');
    expect(greekWords.word.name, 'word');
    expect(greekWords.category.name, 'category');
    expect(greekWords.synonyms.name, 'synonyms');
    expect(greekWords.origin.name, 'origin');
    expect(greekWords.usage.name, 'usage');

    final resources = db.commonResources;
    expect(resources.primaryKey, {resources.key});
    expect(resources.fileName.name, 'file_name');
    expect(resources.mimeType.name, 'mime_type');
    expect(resources.data.name, 'data');

    final sources = db.primarySources;
    expect(sources.primaryKey, {sources.id});
    expect(sources.family.name, 'family');
    expect(sources.number.name, 'number');
    expect(sources.groupKind.name, 'group_kind');
    expect(sources.sortOrder.name, 'sort_order');
    expect(sources.versesCount.name, 'verses_count');
    expect(sources.previewResourceKey.name, 'preview_resource_key');
    expect(sources.defaultMaxScale.name, 'default_max_scale');
    expect(sources.canShowImages.name, 'can_show_images');
    expect(sources.imagesAreMonochrome.name, 'images_are_monochrome');
    expect(sources.notes.name, 'notes');

    final links = db.primarySourceLinks;
    expect(links.primaryKey, {links.sourceId, links.linkId});
    expect(links.sourceId.name, 'source_id');
    expect(links.linkId.name, 'link_id');
    expect(links.sortOrder.name, 'sort_order');
    expect(links.linkRole.name, 'link_role');
    expect(links.url.name, 'url');

    final attributions = db.primarySourceAttributions;
    expect(attributions.primaryKey, {
      attributions.sourceId,
      attributions.attributionId,
    });
    expect(attributions.sourceId.name, 'source_id');
    expect(attributions.attributionId.name, 'attribution_id');
    expect(attributions.sortOrder.name, 'sort_order');
    expect(attributions.displayText.name, 'text');
    expect(attributions.url.name, 'url');

    final pages = db.primarySourcePages;
    expect(pages.primaryKey, {pages.sourceId, pages.pageName});
    expect(pages.sourceId.name, 'source_id');
    expect(pages.pageName.name, 'page_name');
    expect(pages.sortOrder.name, 'sort_order');
    expect(pages.contentRef.name, 'content_ref');
    expect(pages.imagePath.name, 'image_path');

    final words = db.primarySourceWords;
    expect(words.primaryKey, {words.sourceId, words.pageName, words.wordIndex});
    expect(words.sourceId.name, 'source_id');
    expect(words.pageName.name, 'page_name');
    expect(words.wordIndex.name, 'word_index');
    expect(words.wordText.name, 'text');
    expect(words.strongNumber.name, 'strong_number');
    expect(words.strongPronounce.name, 'strong_pronounce');
    expect(words.strongXShift.name, 'strong_x_shift');
    expect(words.missingCharIndexesJson.name, 'missing_char_indexes_json');
    expect(words.rectanglesJson.name, 'rectangles_json');

    final verses = db.primarySourceVerses;
    expect(verses.primaryKey, {
      verses.sourceId,
      verses.pageName,
      verses.verseIndex,
    });
    expect(verses.sourceId.name, 'source_id');
    expect(verses.pageName.name, 'page_name');
    expect(verses.verseIndex.name, 'verse_index');
    expect(verses.chapterNumber.name, 'chapter_number');
    expect(verses.verseNumber.name, 'verse_number');
    expect(verses.labelX.name, 'label_x');
    expect(verses.labelY.name, 'label_y');
    expect(verses.wordIndexesJson.name, 'word_indexes_json');
    expect(verses.contoursJson.name, 'contours_json');
  });

  test('CommonDB onCreate initializes schema/data/date metadata', () async {
    final db = CommonDB(NativeDatabase.memory());
    addTearDown(db.close);

    expect(db.schemaVersion, 4);
    expect(await _readMetadata(db, 'schema_version'), '4');
    expect(await _readMetadata(db, 'data_version'), '1');
    expect(DateTime.tryParse((await _readMetadata(db, 'date'))!), isNotNull);
  });

  test(
    'CommonDB upgrade from v1 creates missing tables and metadata',
    () async {
      final tempDir = await Directory.systemTemp.createTemp(
        'common_db_upgrade_v1_',
      );
      addTearDown(() async => tempDir.delete(recursive: true));
      final file = File(p.join(tempDir.path, 'common_upgrade.sqlite'));
      final db = CommonDB(
        NativeDatabase(
          file,
          setup: (rawDb) {
            rawDb.execute('PRAGMA user_version = 1;');
            rawDb.execute('''
            CREATE TABLE greek_words (
              id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
              word TEXT NOT NULL,
              category TEXT NOT NULL,
              synonyms TEXT NOT NULL,
              origin TEXT NOT NULL,
              usage TEXT NOT NULL
            );
          ''');
          },
        ),
      );
      addTearDown(db.close);

      expect(await _tableExists(db, 'common_resources'), isTrue);
      expect(await _tableExists(db, 'primary_sources'), isTrue);
      expect(await _tableExists(db, 'primary_source_links'), isTrue);
      expect(await _tableExists(db, 'primary_source_attributions'), isTrue);
      expect(await _tableExists(db, 'primary_source_pages'), isTrue);
      expect(await _tableExists(db, 'primary_source_words'), isTrue);
      expect(await _tableExists(db, 'primary_source_verses'), isTrue);
      expect(await _tableExists(db, 'db_metadata'), isTrue);

      expect(await _readMetadata(db, 'schema_version'), '4');
      expect(await _readMetadata(db, 'data_version'), '1');
      expect(DateTime.tryParse((await _readMetadata(db, 'date'))!), isNotNull);
    },
  );

  test('PrimarySources defaults are applied as DB contract', () async {
    final db = CommonDB(NativeDatabase.memory());
    addTearDown(db.close);
    await db
        .into(db.primarySources)
        .insert(
          PrimarySourcesCompanion.insert(
            id: 'src-1',
            family: 'fam',
            number: 1,
            groupKind: 'group',
            previewResourceKey: 'preview',
          ),
        );

    final row = await (db.select(
      db.primarySources,
    )..where((t) => t.id.equals('src-1'))).getSingle();

    expect(row.sortOrder, 0);
    expect(row.versesCount, 0);
    expect(row.defaultMaxScale, 3.0);
    expect(row.canShowImages, isTrue);
    expect(row.imagesAreMonochrome, isFalse);
    expect(row.notes, '');
  });
}

Future<bool> _tableExists(CommonDB db, String tableName) async {
  final rows = await db
      .customSelect(
        'SELECT name FROM sqlite_master WHERE type = ? AND name = ?',
        variables: [
          Variable.withString('table'),
          Variable.withString(tableName),
        ],
      )
      .get();
  return rows.isNotEmpty;
}

Future<String?> _readMetadata(CommonDB db, String key) async {
  final row = await db
      .customSelect(
        'SELECT value FROM db_metadata WHERE key = ?',
        variables: [Variable.withString(key)],
      )
      .getSingleOrNull();
  return row?.read<String>('value');
}
