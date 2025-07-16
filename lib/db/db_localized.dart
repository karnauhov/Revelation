import 'package:drift/drift.dart';

part 'db_localized.g.dart';

class GreekDescs extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get desc => text().named('desc')();
}

@DriftDatabase(tables: [GreekDescs])
class LocalizedDB extends _$LocalizedDB {
  LocalizedDB(QueryExecutor e) : super(e);

  // @override
  int get schemaVersion => 1;
}
