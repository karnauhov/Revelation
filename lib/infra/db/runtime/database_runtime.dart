import 'package:revelation/infra/db/runtime/db_manager_gateway.dart';

abstract class DatabaseRuntime {
  Future<void> initialize(String language);

  Future<void> updateLanguage(String language);
}

class DbManagerDatabaseRuntime implements DatabaseRuntime {
  DbManagerDatabaseRuntime({DatabaseGateway? databaseGateway})
    : _databaseGateway = databaseGateway ?? DbManagerDatabaseGateway();

  final DatabaseGateway _databaseGateway;

  @override
  Future<void> initialize(String language) {
    return _databaseGateway.initialize(language);
  }

  @override
  Future<void> updateLanguage(String language) {
    return _databaseGateway.updateLanguage(language);
  }
}
