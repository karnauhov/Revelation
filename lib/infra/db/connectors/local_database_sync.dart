import 'package:revelation/infra/db/connectors/local_database_sync_stub.dart'
    if (dart.library.io) 'package:revelation/infra/db/connectors/local_database_sync_native.dart'
    if (dart.library.js_interop) 'package:revelation/infra/db/connectors/local_database_sync_stub.dart'
    as impl;
import 'package:revelation/infra/db/connectors/local_database_sync_result.dart';

Future<void> verifyAndUpdateKnownLocalDatabases({
  String? languageCode,
  bool force = false,
}) {
  return impl.verifyAndUpdateKnownLocalDatabases(
    languageCode: languageCode,
    force: force,
  );
}

Future<LocalDatabaseSyncResult> verifyAndUpdateKnownLocalDatabasesWithResult({
  String? languageCode,
  bool force = false,
}) {
  return impl.verifyAndUpdateKnownLocalDatabasesWithResult(
    languageCode: languageCode,
    force: force,
  );
}

Future<bool> verifyAndUpdateLocalDatabaseFile(
  String dbFile, {
  bool force = false,
}) {
  return impl.verifyAndUpdateLocalDatabaseFile(dbFile, force: force);
}

Future<LocalDatabaseFileSyncResult> verifyAndUpdateLocalDatabaseFileWithResult(
  String dbFile, {
  bool force = false,
}) {
  return impl.verifyAndUpdateLocalDatabaseFileWithResult(dbFile, force: force);
}

List<String> knownLocalDatabaseFiles({
  String? languageCode,
  bool includeAllLanguages = true,
}) {
  return impl.knownLocalDatabaseFiles(
    languageCode: languageCode,
    includeAllLanguages: includeAllLanguages,
  );
}
