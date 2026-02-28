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

@DriftDatabase(tables: [GreekWords, CommonResources])
class CommonDB extends _$CommonDB {
  CommonDB(QueryExecutor e) : super(e);

  @override
  int get schemaVersion => 2;

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
    },
  );
}
