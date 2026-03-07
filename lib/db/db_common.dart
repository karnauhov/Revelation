import 'package:drift/drift.dart';

part 'db_common.g.dart';

class GreekWords extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get word => text().named('word')();
  TextColumn get category => text().named('category')();
  TextColumn get synonyms => text().named('synonyms')();
  TextColumn get origin => text().named('origin')();
  TextColumn get usage => text().named('usage')();
}

class CommonResources extends Table {
  TextColumn get key => text()();
  TextColumn get fileName => text().named('file_name')();
  TextColumn get mimeType => text().named('mime_type')();
  BlobColumn get data => blob()();

  @override
  Set<Column> get primaryKey => {key};
}

class PrimarySources extends Table {
  TextColumn get id => text()();
  TextColumn get family => text().named('family')();
  IntColumn get number => integer().named('number')();
  TextColumn get groupKind => text().named('group_kind')();
  IntColumn get sortOrder =>
      integer().named('sort_order').withDefault(const Constant(0))();
  IntColumn get versesCount =>
      integer().named('verses_count').withDefault(const Constant(0))();
  TextColumn get previewResourceKey => text().named('preview_resource_key')();
  RealColumn get defaultMaxScale =>
      real().named('default_max_scale').withDefault(const Constant(3.0))();
  BoolColumn get canShowImages =>
      boolean().named('can_show_images').withDefault(const Constant(true))();
  BoolColumn get imagesAreMonochrome => boolean()
      .named('images_are_monochrome')
      .withDefault(const Constant(false))();
  TextColumn get notes => text().withDefault(const Constant(''))();

  @override
  Set<Column> get primaryKey => {id};
}

class PrimarySourceLinks extends Table {
  TextColumn get sourceId => text().named('source_id')();
  TextColumn get linkId => text().named('link_id')();
  IntColumn get sortOrder =>
      integer().named('sort_order').withDefault(const Constant(0))();
  TextColumn get linkRole => text().named('link_role')();
  TextColumn get url => text()();

  @override
  Set<Column> get primaryKey => {sourceId, linkId};
}

class PrimarySourceAttributions extends Table {
  TextColumn get sourceId => text().named('source_id')();
  TextColumn get attributionId => text().named('attribution_id')();
  IntColumn get sortOrder =>
      integer().named('sort_order').withDefault(const Constant(0))();
  TextColumn get displayText => text().named('text')();
  TextColumn get url => text()();

  @override
  Set<Column> get primaryKey => {sourceId, attributionId};
}

class PrimarySourcePages extends Table {
  TextColumn get sourceId => text().named('source_id')();
  TextColumn get pageName => text().named('page_name')();
  IntColumn get sortOrder =>
      integer().named('sort_order').withDefault(const Constant(0))();
  TextColumn get contentRef => text().named('content_ref')();
  TextColumn get imagePath => text().named('image_path')();

  @override
  Set<Column> get primaryKey => {sourceId, pageName};
}

class PrimarySourceWords extends Table {
  TextColumn get sourceId => text().named('source_id')();
  TextColumn get pageName => text().named('page_name')();
  IntColumn get wordIndex => integer().named('word_index')();
  TextColumn get wordText => text().named('text')();
  IntColumn get strongNumber => integer().named('strong_number').nullable()();
  BoolColumn get strongPronounce =>
      boolean().named('strong_pronounce').withDefault(const Constant(false))();
  RealColumn get strongXShift =>
      real().named('strong_x_shift').withDefault(const Constant(0.0))();
  TextColumn get missingCharIndexesJson => text()
      .named('missing_char_indexes_json')
      .withDefault(const Constant('[]'))();
  TextColumn get rectanglesJson =>
      text().named('rectangles_json').withDefault(const Constant('[]'))();

  @override
  Set<Column> get primaryKey => {sourceId, pageName, wordIndex};
}

class PrimarySourceVerses extends Table {
  TextColumn get sourceId => text().named('source_id')();
  TextColumn get pageName => text().named('page_name')();
  IntColumn get verseIndex => integer().named('verse_index')();
  IntColumn get chapterNumber => integer().named('chapter_number')();
  IntColumn get verseNumber => integer().named('verse_number')();
  RealColumn get labelX => real().named('label_x')();
  RealColumn get labelY => real().named('label_y')();
  TextColumn get wordIndexesJson =>
      text().named('word_indexes_json').withDefault(const Constant('[]'))();
  TextColumn get contoursJson =>
      text().named('contours_json').withDefault(const Constant('[]'))();

  @override
  Set<Column> get primaryKey => {sourceId, pageName, verseIndex};
}

@DriftDatabase(
  tables: [
    GreekWords,
    CommonResources,
    PrimarySources,
    PrimarySourceLinks,
    PrimarySourceAttributions,
    PrimarySourcePages,
    PrimarySourceWords,
    PrimarySourceVerses,
  ],
)
class CommonDB extends _$CommonDB {
  CommonDB(QueryExecutor e) : super(e);

  @override
  int get schemaVersion => 3;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (Migrator m) async {
      await m.createAll();
    },
    onUpgrade: (Migrator m, int from, int to) async {
      if (from < 2) {
        await customStatement("""
          CREATE TABLE IF NOT EXISTS common_resources (
            key TEXT NOT NULL PRIMARY KEY,
            file_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            data BLOB NOT NULL
          )
        """);
      }
      if (from < 3) {
        await customStatement("""
          CREATE TABLE IF NOT EXISTS primary_sources (
            id TEXT NOT NULL PRIMARY KEY,
            family TEXT NOT NULL,
            number INTEGER NOT NULL,
            group_kind TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            verses_count INTEGER NOT NULL DEFAULT 0,
            preview_resource_key TEXT NOT NULL,
            default_max_scale REAL NOT NULL DEFAULT 3.0,
            can_show_images INTEGER NOT NULL DEFAULT 1,
            images_are_monochrome INTEGER NOT NULL DEFAULT 0,
            notes TEXT NOT NULL DEFAULT ''
          )
        """);
        await customStatement("""
          CREATE TABLE IF NOT EXISTS primary_source_links (
            source_id TEXT NOT NULL,
            link_id TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            link_role TEXT NOT NULL,
            url TEXT NOT NULL,
            PRIMARY KEY (source_id, link_id)
          )
        """);
        await customStatement("""
          CREATE TABLE IF NOT EXISTS primary_source_attributions (
            source_id TEXT NOT NULL,
            attribution_id TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            text TEXT NOT NULL,
            url TEXT NOT NULL,
            PRIMARY KEY (source_id, attribution_id)
          )
        """);
        await customStatement("""
          CREATE TABLE IF NOT EXISTS primary_source_pages (
            source_id TEXT NOT NULL,
            page_name TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            content_ref TEXT NOT NULL,
            image_path TEXT NOT NULL,
            PRIMARY KEY (source_id, page_name)
          )
        """);
        await customStatement("""
          CREATE TABLE IF NOT EXISTS primary_source_words (
            source_id TEXT NOT NULL,
            page_name TEXT NOT NULL,
            word_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            strong_number INTEGER,
            strong_pronounce INTEGER NOT NULL DEFAULT 0,
            strong_x_shift REAL NOT NULL DEFAULT 0.0,
            missing_char_indexes_json TEXT NOT NULL DEFAULT '[]',
            rectangles_json TEXT NOT NULL DEFAULT '[]',
            PRIMARY KEY (source_id, page_name, word_index)
          )
        """);
        await customStatement("""
          CREATE TABLE IF NOT EXISTS primary_source_verses (
            source_id TEXT NOT NULL,
            page_name TEXT NOT NULL,
            verse_index INTEGER NOT NULL,
            chapter_number INTEGER NOT NULL,
            verse_number INTEGER NOT NULL,
            label_x REAL NOT NULL,
            label_y REAL NOT NULL,
            word_indexes_json TEXT NOT NULL DEFAULT '[]',
            contours_json TEXT NOT NULL DEFAULT '[]',
            PRIMARY KEY (source_id, page_name, verse_index)
          )
        """);
      }
    },
  );
}
