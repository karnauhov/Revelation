import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';

CommonDB getCommonDB() => throw UnimplementedError();
LocalizedDB getLocalizedDB(String loc) => throw UnimplementedError();
Future<DateTime?> getLocalDatabaseUpdatedAt(String dbFile) async => null;
