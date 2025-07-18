import 'package:drift/drift.dart';

part 'db_common.g.dart';

class GreekWords extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get word => text().named('word')();
}

@DriftDatabase(tables: [GreekWords])
class CommonDB extends _$CommonDB {
  CommonDB(QueryExecutor e) : super(e);

  // @override
  int get schemaVersion => 1;
}
