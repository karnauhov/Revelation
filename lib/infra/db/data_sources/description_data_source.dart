import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';

abstract class DescriptionDataSource {
  bool get isInitialized;

  String get languageCode;

  List<common_db.GreekWord> get greekWords;

  List<localized_db.GreekDesc> get greekDescs;
}

class DbManagerDescriptionDataSource implements DescriptionDataSource {
  DbManagerDescriptionDataSource({LexiconDatabaseGateway? databaseGateway})
    : _databaseGateway = databaseGateway ?? DbManagerLexiconDatabaseGateway();

  final LexiconDatabaseGateway _databaseGateway;

  @override
  bool get isInitialized => _databaseGateway.isInitialized;

  @override
  String get languageCode => _databaseGateway.languageCode;

  @override
  List<common_db.GreekWord> get greekWords => _databaseGateway.greekWords;

  @override
  List<localized_db.GreekDesc> get greekDescs => _databaseGateway.greekDescs;
}
