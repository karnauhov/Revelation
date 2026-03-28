import 'dart:io';

import 'package:drift/drift.dart' hide isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/infra/db/localized/db_localized.dart';

void main() {
  test(
    'Raw localized table declarations fail fast outside generated DB context',
    () {
      void expectUnsupported(Object? Function() callback) {
        expect(callback, throwsA(isA<UnsupportedError>()));
      }

      expect(LocalizedDbMetadata().tableName, 'db_metadata');
      expectUnsupported(() => LocalizedDbMetadata().key);
      expectUnsupported(() => LocalizedDbMetadata().value);
      expectUnsupported(() => LocalizedDbMetadata().primaryKey);

      expectUnsupported(() => GreekDescs().id);
      expectUnsupported(() => GreekDescs().desc);

      expectUnsupported(() => Articles().route);
      expectUnsupported(() => Articles().name);
      expectUnsupported(() => Articles().description);
      expectUnsupported(() => Articles().idIcon);
      expectUnsupported(() => Articles().sortOrder);
      expectUnsupported(() => Articles().isVisible);
      expectUnsupported(() => Articles().markdown);
      expectUnsupported(() => Articles().primaryKey);

      expectUnsupported(() => PrimarySourceTexts().sourceId);
      expectUnsupported(() => PrimarySourceTexts().titleMarkup);
      expectUnsupported(() => PrimarySourceTexts().dateLabel);
      expectUnsupported(() => PrimarySourceTexts().contentLabel);
      expectUnsupported(() => PrimarySourceTexts().materialText);
      expectUnsupported(() => PrimarySourceTexts().textStyleText);
      expectUnsupported(() => PrimarySourceTexts().foundText);
      expectUnsupported(() => PrimarySourceTexts().classificationText);
      expectUnsupported(() => PrimarySourceTexts().currentLocationText);
      expectUnsupported(() => PrimarySourceTexts().primaryKey);

      expectUnsupported(() => PrimarySourceLinkTexts().sourceId);
      expectUnsupported(() => PrimarySourceLinkTexts().linkId);
      expectUnsupported(() => PrimarySourceLinkTexts().title);
      expectUnsupported(() => PrimarySourceLinkTexts().primaryKey);
    },
  );

  test('Localized table definitions expose stable schema contract', () {
    final db = LocalizedDB(NativeDatabase.memory());
    addTearDown(db.close);

    final metadata = db.localizedDbMetadata;
    expect(metadata.tableName, 'db_metadata');
    expect(metadata.primaryKey, {metadata.key});
    expect(metadata.value.name, 'value');

    final descs = db.greekDescs;
    expect(descs.id.name, 'id');
    expect(descs.desc.name, 'desc');

    final articles = db.articles;
    expect(articles.primaryKey, {articles.route});
    expect(articles.route.name, 'route');
    expect(articles.name.name, 'name');
    expect(articles.description.name, 'description');
    expect(articles.idIcon.name, 'id_icon');
    expect(articles.sortOrder.name, 'sort_order');
    expect(articles.isVisible.name, 'is_visible');
    expect(articles.markdown.name, 'markdown');

    final sourceTexts = db.primarySourceTexts;
    expect(sourceTexts.primaryKey, {sourceTexts.sourceId});
    expect(sourceTexts.sourceId.name, 'source_id');
    expect(sourceTexts.titleMarkup.name, 'title_markup');
    expect(sourceTexts.dateLabel.name, 'date_label');
    expect(sourceTexts.contentLabel.name, 'content_label');
    expect(sourceTexts.materialText.name, 'material_text');
    expect(sourceTexts.textStyleText.name, 'text_style_text');
    expect(sourceTexts.foundText.name, 'found_text');
    expect(sourceTexts.classificationText.name, 'classification_text');
    expect(sourceTexts.currentLocationText.name, 'current_location_text');

    final linkTexts = db.primarySourceLinkTexts;
    expect(linkTexts.primaryKey, {linkTexts.sourceId, linkTexts.linkId});
    expect(linkTexts.sourceId.name, 'source_id');
    expect(linkTexts.linkId.name, 'link_id');
    expect(linkTexts.title.name, 'title');
  });

  test('LocalizedDB onCreate initializes schema/data/date metadata', () async {
    final db = LocalizedDB(NativeDatabase.memory());
    addTearDown(db.close);

    expect(db.schemaVersion, 6);
    expect(await _readMetadata(db, 'schema_version'), '6');
    expect(await _readMetadata(db, 'data_version'), '1');
    expect(DateTime.tryParse((await _readMetadata(db, 'date'))!), isNotNull);
  });

  test(
    'LocalizedDB upgrade from v3 migrates topics and topic_texts into articles',
    () async {
      final tempDir = await Directory.systemTemp.createTemp(
        'localized_db_upgrade_v3_',
      );
      addTearDown(() async => tempDir.delete(recursive: true));
      final file = File(p.join(tempDir.path, 'localized_upgrade_v3.sqlite'));
      final db = LocalizedDB(
        NativeDatabase(
          file,
          setup: (rawDb) {
            rawDb.execute('PRAGMA user_version = 3;');
            rawDb.execute('''
            CREATE TABLE topics (
              route TEXT NOT NULL PRIMARY KEY,
              name TEXT NOT NULL,
              description TEXT NOT NULL,
              id_icon TEXT NOT NULL,
              sort_order INTEGER NOT NULL DEFAULT 0,
              is_visible INTEGER NOT NULL DEFAULT 1
            );
          ''');
            rawDb.execute('''
            CREATE TABLE topic_texts (
              route TEXT NOT NULL PRIMARY KEY,
              markdown TEXT NOT NULL
            );
          ''');
            rawDb.execute('''
            CREATE TABLE articles (
              route TEXT NOT NULL PRIMARY KEY,
              name TEXT NOT NULL,
              description TEXT NOT NULL,
              id_icon TEXT NOT NULL,
              sort_order INTEGER NOT NULL DEFAULT 0,
              is_visible INTEGER NOT NULL DEFAULT 1,
              markdown TEXT NOT NULL
            );
          ''');
            rawDb.execute("""
            INSERT INTO topics(route, name, description, id_icon, sort_order, is_visible)
            VALUES
              ('topic_alpha', 'Alpha', 'Alpha desc', 'icon_a', 2, 1),
              ('already_exists', 'Will be ignored', 'Old', 'icon_old', 3, 1);
          """);
            rawDb.execute("""
            INSERT INTO topic_texts(route, markdown)
            VALUES
              ('topic_alpha', '# Alpha markdown'),
              ('orphan_markdown', '# Orphan markdown'),
              ('already_exists', '# Should not override existing article');
          """);
            rawDb.execute("""
            INSERT INTO articles(route, name, description, id_icon, sort_order, is_visible, markdown)
            VALUES
              ('already_exists', 'Existing article', 'Exists', 'icon_existing', 1, 1, '# Existing markdown');
          """);
          },
        ),
      );
      addTearDown(db.close);

      final articles = await (db.select(
        db.articles,
      )..orderBy([(t) => OrderingTerm(expression: t.route)])).get();
      final byRoute = {for (final article in articles) article.route: article};

      expect(
        byRoute.keys,
        containsAll(<String>[
          'already_exists',
          'orphan_markdown',
          'topic_alpha',
        ]),
      );
      expect(byRoute['already_exists']!.name, 'Existing article');
      expect(byRoute['already_exists']!.markdown, '# Existing markdown');

      expect(byRoute['topic_alpha']!.name, 'Alpha');
      expect(byRoute['topic_alpha']!.description, 'Alpha desc');
      expect(byRoute['topic_alpha']!.idIcon, 'icon_a');
      expect(byRoute['topic_alpha']!.sortOrder, 2);
      expect(byRoute['topic_alpha']!.isVisible, isTrue);
      expect(byRoute['topic_alpha']!.markdown, '# Alpha markdown');

      expect(byRoute['orphan_markdown']!.name, 'orphan_markdown');
      expect(byRoute['orphan_markdown']!.description, '');
      expect(byRoute['orphan_markdown']!.idIcon, '');
      expect(byRoute['orphan_markdown']!.sortOrder, 0);
      expect(byRoute['orphan_markdown']!.isVisible, isFalse);
      expect(byRoute['orphan_markdown']!.markdown, '# Orphan markdown');

      expect(await _tableExists(db, 'topics'), isFalse);
      expect(await _tableExists(db, 'topic_texts'), isFalse);
      expect(await _tableExists(db, 'primary_source_texts'), isTrue);
      expect(await _tableExists(db, 'primary_source_link_texts'), isTrue);
      expect(await _tableExists(db, 'db_metadata'), isTrue);

      expect(await _readMetadata(db, 'schema_version'), '6');
      expect(await _readMetadata(db, 'data_version'), '1');
      expect(DateTime.tryParse((await _readMetadata(db, 'date'))!), isNotNull);
    },
  );

  test(
    'LocalizedDB upgrade from v5 creates db_metadata and keeps data tables',
    () async {
      final tempDir = await Directory.systemTemp.createTemp(
        'localized_db_upgrade_v5_',
      );
      addTearDown(() async => tempDir.delete(recursive: true));
      final file = File(p.join(tempDir.path, 'localized_upgrade_v5.sqlite'));
      final db = LocalizedDB(
        NativeDatabase(
          file,
          setup: (rawDb) {
            rawDb.execute('PRAGMA user_version = 5;');
            rawDb.execute('''
            CREATE TABLE greek_descs (
              id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
              "desc" TEXT NOT NULL
            );
          ''');
            rawDb.execute('''
            CREATE TABLE articles (
              route TEXT NOT NULL PRIMARY KEY,
              name TEXT NOT NULL,
              description TEXT NOT NULL,
              id_icon TEXT NOT NULL,
              sort_order INTEGER NOT NULL DEFAULT 0,
              is_visible INTEGER NOT NULL DEFAULT 1,
              markdown TEXT NOT NULL
            );
          ''');
            rawDb.execute('''
            CREATE TABLE primary_source_texts (
              source_id TEXT NOT NULL PRIMARY KEY,
              title_markup TEXT NOT NULL,
              date_label TEXT NOT NULL,
              content_label TEXT NOT NULL,
              material_text TEXT NOT NULL,
              text_style_text TEXT NOT NULL,
              found_text TEXT NOT NULL,
              classification_text TEXT NOT NULL,
              current_location_text TEXT NOT NULL
            );
          ''');
            rawDb.execute('''
            CREATE TABLE primary_source_link_texts (
              source_id TEXT NOT NULL,
              link_id TEXT NOT NULL,
              title TEXT NOT NULL,
              PRIMARY KEY (source_id, link_id)
            );
          ''');
          },
        ),
      );
      addTearDown(db.close);

      expect(await _tableExists(db, 'db_metadata'), isTrue);
      expect(await _tableExists(db, 'articles'), isTrue);
      expect(await _tableExists(db, 'greek_descs'), isTrue);
      expect(await _tableExists(db, 'primary_source_texts'), isTrue);
      expect(await _tableExists(db, 'primary_source_link_texts'), isTrue);
      expect(await _readMetadata(db, 'schema_version'), '6');
      expect(await _readMetadata(db, 'data_version'), '1');
      expect(DateTime.tryParse((await _readMetadata(db, 'date'))!), isNotNull);
    },
  );
}

Future<bool> _tableExists(LocalizedDB db, String tableName) async {
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

Future<String?> _readMetadata(LocalizedDB db, String key) async {
  final row = await db
      .customSelect(
        'SELECT value FROM db_metadata WHERE key = ?',
        variables: [Variable.withString(key)],
      )
      .getSingleOrNull();
  return row?.read<String>('value');
}
