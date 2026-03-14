import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/db_manager.dart';

abstract class LexiconDatabaseGateway {
  bool get isInitialized;

  String get languageCode;

  List<common_db.GreekWord> get greekWords;

  List<localized_db.GreekDesc> get greekDescs;

  Future<void> initialize(String language);

  Future<void> updateLanguage(String language);
}

class DbManagerLexiconDatabaseGateway implements LexiconDatabaseGateway {
  static final DbManagerLexiconDatabaseGateway _instance =
      DbManagerLexiconDatabaseGateway._internal();

  factory DbManagerLexiconDatabaseGateway() {
    return _instance;
  }

  DbManagerLexiconDatabaseGateway._internal();

  final DBManager _dbManager = DBManager();
  List<common_db.GreekWord> _greekWords = const [];
  List<localized_db.GreekDesc> _greekDescs = const [];

  @override
  bool get isInitialized => _dbManager.isInitialized;

  @override
  String get languageCode => _dbManager.langDB;

  @override
  List<common_db.GreekWord> get greekWords => _greekWords;

  @override
  List<localized_db.GreekDesc> get greekDescs => _greekDescs;

  @override
  Future<void> initialize(String language) async {
    await _dbManager.init(language);
    await _reloadLexicon();
  }

  @override
  Future<void> updateLanguage(String language) async {
    await _dbManager.updateLanguage(language);
    await _reloadLexicon();
  }

  Future<void> _reloadLexicon() async {
    if (!_dbManager.isInitialized) {
      _greekWords = const [];
      _greekDescs = const [];
      return;
    }
    _greekWords = List<common_db.GreekWord>.unmodifiable(
      await _dbManager.commonDB.select(_dbManager.commonDB.greekWords).get(),
    );
    _greekDescs = List<localized_db.GreekDesc>.unmodifiable(
      await _dbManager.localizedDB
          .select(_dbManager.localizedDB.greekDescs)
          .get(),
    );
  }
}
