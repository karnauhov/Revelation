import 'package:drift/drift.dart';

part 'db_localized.g.dart';

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

@DriftDatabase(tables: [GreekDescs, Articles])
class LocalizedDB extends _$LocalizedDB {
  LocalizedDB(QueryExecutor e) : super(e);

  @override
  int get schemaVersion => 4;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (Migrator m) async {
      await m.createAll();
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
    },
  );
}
