import 'package:drift/drift.dart';

part 'db_localized.g.dart';

class LocalizedDbMetadata extends Table {
  @override
  String get tableName => 'db_metadata';

  TextColumn get key => text()();
  TextColumn get value => text()();

  @override
  Set<Column> get primaryKey => {key};
}

class GreekDescs extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get desc => text().named('desc')();
}

class Articles extends Table {
  TextColumn get route => text()();
  TextColumn get name => text()();
  TextColumn get description => text()();
  TextColumn get idIcon => text().named('id_icon')();
  IntColumn get sortOrder =>
      integer().named('sort_order').withDefault(const Constant(0))();
  BoolColumn get isVisible =>
      boolean().named('is_visible').withDefault(const Constant(true))();
  TextColumn get markdown => text()();

  @override
  Set<Column> get primaryKey => {route};
}

class PrimarySourceTexts extends Table {
  TextColumn get sourceId => text().named('source_id')();
  TextColumn get titleMarkup => text().named('title_markup')();
  TextColumn get dateLabel => text().named('date_label')();
  TextColumn get contentLabel => text().named('content_label')();
  TextColumn get materialText => text().named('material_text')();
  TextColumn get textStyleText => text().named('text_style_text')();
  TextColumn get foundText => text().named('found_text')();
  TextColumn get classificationText => text().named('classification_text')();
  TextColumn get currentLocationText => text().named('current_location_text')();

  @override
  Set<Column> get primaryKey => {sourceId};
}

class PrimarySourceLinkTexts extends Table {
  TextColumn get sourceId => text().named('source_id')();
  TextColumn get linkId => text().named('link_id')();
  TextColumn get title => text().named('title')();

  @override
  Set<Column> get primaryKey => {sourceId, linkId};
}

@DriftDatabase(
  tables: [
    LocalizedDbMetadata,
    GreekDescs,
    Articles,
    PrimarySourceTexts,
    PrimarySourceLinkTexts,
  ],
)
class LocalizedDB extends _$LocalizedDB {
  LocalizedDB(QueryExecutor e) : super(e);

  @override
  int get schemaVersion => 6;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (Migrator m) async {
      await m.createAll();
      await _ensureDbMetadataInitialized(initializeDataVersionAndDate: true);
    },
    onUpgrade: (Migrator m, int from, int to) async {
      if (from < 4) {
        // Ensure legacy tables exist for safe migration from custom/older DBs.
        await customStatement("""
          CREATE TABLE IF NOT EXISTS topic_texts (
            route TEXT NOT NULL PRIMARY KEY,
            markdown TEXT NOT NULL
          )
        """);
        await customStatement("""
          CREATE TABLE IF NOT EXISTS topics (
            route TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            id_icon TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            is_visible INTEGER NOT NULL DEFAULT 1
          )
        """);

        await customStatement("""
          CREATE TABLE IF NOT EXISTS articles (
            route TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            id_icon TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            is_visible INTEGER NOT NULL DEFAULT 1,
            markdown TEXT NOT NULL
          )
        """);

        // 1) Migrate records that existed in `topics`.
        await customStatement("""
          INSERT INTO articles(route, name, description, id_icon, sort_order, is_visible, markdown)
          SELECT
            t.route,
            t.name,
            t.description,
            t.id_icon,
            t.sort_order,
            t.is_visible,
            COALESCE(tt.markdown, '')
          FROM topics t
          LEFT JOIN topic_texts tt ON tt.route = t.route
          WHERE NOT EXISTS (
            SELECT 1
            FROM articles a
            WHERE a.route = t.route
          )
        """);

        // 2) Migrate orphan markdown-only records (hidden by default).
        await customStatement("""
          INSERT INTO articles(route, name, description, id_icon, sort_order, is_visible, markdown)
          SELECT
            tt.route,
            tt.route,
            '',
            '',
            0,
            0,
            tt.markdown
          FROM topic_texts tt
          WHERE NOT EXISTS (
            SELECT 1
            FROM articles a
            WHERE a.route = tt.route
          )
        """);

        await customStatement('DROP TABLE IF EXISTS topics');
        await customStatement('DROP TABLE IF EXISTS topic_texts');
      }
      if (from < 5) {
        await customStatement("""
          CREATE TABLE IF NOT EXISTS primary_source_texts (
            source_id TEXT NOT NULL PRIMARY KEY,
            title_markup TEXT NOT NULL,
            date_label TEXT NOT NULL,
            content_label TEXT NOT NULL,
            material_text TEXT NOT NULL,
            text_style_text TEXT NOT NULL,
            found_text TEXT NOT NULL,
            classification_text TEXT NOT NULL,
            current_location_text TEXT NOT NULL
          )
        """);
        await customStatement("""
          CREATE TABLE IF NOT EXISTS primary_source_link_texts (
            source_id TEXT NOT NULL,
            link_id TEXT NOT NULL,
            title TEXT NOT NULL,
            PRIMARY KEY (source_id, link_id)
          )
        """);
      }
      if (from < 6) {
        await customStatement("""
          CREATE TABLE IF NOT EXISTS db_metadata (
            key TEXT NOT NULL PRIMARY KEY,
            value TEXT NOT NULL
          )
        """);
      }
      await _ensureDbMetadataInitialized(
        initializeDataVersionAndDate: from < 6,
      );
    },
  );

  Future<void> _ensureDbMetadataInitialized({
    required bool initializeDataVersionAndDate,
  }) async {
    await customStatement(
      """
      INSERT INTO db_metadata(key, value)
      VALUES('schema_version', ?)
      ON CONFLICT(key) DO UPDATE SET value = excluded.value
      """,
      [schemaVersion.toString()],
    );
    if (!initializeDataVersionAndDate) {
      return;
    }
    final now = DateTime.now().toUtc().toIso8601String();
    await customStatement("""
      INSERT INTO db_metadata(key, value)
      VALUES('data_version', '1')
      ON CONFLICT(key) DO NOTHING
      """);
    await customStatement(
      """
      INSERT INTO db_metadata(key, value)
      VALUES('date', ?)
      ON CONFLICT(key) DO NOTHING
      """,
      [now],
    );
  }
}
