import 'package:drift/drift.dart';

part 'db_localized.g.dart';

class GreekDescs extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get desc => text().named('desc')();
}

class TopicTexts extends Table {
  TextColumn get route => text()();
  TextColumn get markdown => text()();

  @override
  Set<Column> get primaryKey => {route};
}

class Topics extends Table {
  TextColumn get route => text()();
  TextColumn get name => text()();
  TextColumn get description => text()();
  TextColumn get idIcon => text().named('id_icon')();
  IntColumn get sortOrder => integer().named('sort_order').withDefault(
    const Constant(0),
  )();
  BoolColumn get isVisible =>
      boolean().named('is_visible').withDefault(const Constant(true))();

  @override
  Set<Column> get primaryKey => {route};
}

@DriftDatabase(tables: [GreekDescs, TopicTexts, Topics])
class LocalizedDB extends _$LocalizedDB {
  LocalizedDB(QueryExecutor e) : super(e);

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
          CREATE TABLE IF NOT EXISTS topic_texts (
            route TEXT NOT NULL PRIMARY KEY,
            markdown TEXT NOT NULL
          )
        """);
      }
      if (from < 3) {
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
          INSERT INTO topics(route, name, description, id_icon, sort_order, is_visible)
          SELECT tt.route, tt.route, '', 'code', 0, 1
          FROM topic_texts tt
          WHERE NOT EXISTS (
            SELECT 1 FROM topics t WHERE t.route = tt.route
          )
        """);
      }
    },
  );
}
