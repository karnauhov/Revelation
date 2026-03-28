import 'package:drift/drift.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/database_version_loader.dart';
import 'package:revelation/infra/db/connectors/shared.dart';
import 'package:revelation/infra/db/runtime/gateways/articles_database_gateway.dart';

typedef RuntimeDatabaseAccessor = GeneratedDatabase? Function(String dbFile);
typedef DatabaseVersionFallbackLoader =
    Future<DatabaseVersionInfo?> Function(String dbFile);

Future<DatabaseVersionInfo?> getPreferredDatabaseVersionInfo(
  String dbFile, {
  RuntimeDatabaseAccessor? runtimeDatabaseAccessor,
  ArticlesDatabaseGateway? runtimeDatabaseGateway,
  DatabaseVersionFallbackLoader? fallbackLoader,
}) async {
  final runtimeDatabase =
      runtimeDatabaseAccessor?.call(dbFile) ??
      (runtimeDatabaseGateway ?? DbManagerArticlesDatabaseGateway())
          .getActiveDatabase(dbFile);
  if (runtimeDatabase != null) {
    return readDatabaseVersionInfo(runtimeDatabase);
  }

  return (fallbackLoader ?? getLocalDatabaseVersionInfo)(dbFile);
}
