import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/primary_source_file_info.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';

CommonDB getCommonDB() => throw UnimplementedError();
LocalizedDB getLocalizedDB(String loc) => throw UnimplementedError();
Future<DateTime?> getLocalDatabaseUpdatedAt(String dbFile) async => null;
Future<DatabaseVersionInfo?> getLocalDatabaseVersionInfo(String dbFile) async =>
    null;
Future<int?> getLocalDatabaseFileSize(String dbFile) async => null;
Future<List<PrimarySourceFileInfo>> getLocalPrimarySourceFilesInfo() async =>
    const [];
