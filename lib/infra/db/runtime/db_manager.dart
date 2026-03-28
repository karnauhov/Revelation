import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/connectors/shared.dart';
import 'package:revelation/core/logging/common_logger.dart';

class DBManager {
  static final DBManager _instance = DBManager._internal();
  DBManager._internal();

  factory DBManager() {
    return _instance;
  }

  String _dbLanguage = 'en';
  bool _isInitialized = false;
  late common_db.CommonDB _commonDB;
  late localized_db.LocalizedDB _localizedDB;
  common_db.CommonDB get commonDB => _commonDB;
  localized_db.LocalizedDB get localizedDB => _localizedDB;
  String get langDB => _dbLanguage;
  bool get isInitialized => _isInitialized;

  Future<void> init(String language) async {
    final normalizedLanguage = language.trim().isEmpty ? 'en' : language;
    if (_isInitialized) {
      if (_dbLanguage == normalizedLanguage) {
        return;
      }
      await updateLanguage(normalizedLanguage);
      return;
    }
    _dbLanguage = normalizedLanguage;
    _commonDB = getCommonDB();
    _localizedDB = getLocalizedDB(_dbLanguage);
    _isInitialized = true;
    log.info("DB runtime initialized (${_dbLanguage})");
  }

  Future<void> updateLanguage(String newLanguage) async {
    final normalizedLanguage = newLanguage.trim().isEmpty
        ? _dbLanguage
        : newLanguage;
    if (!_isInitialized) {
      await init(normalizedLanguage);
      return;
    }
    if (_dbLanguage != normalizedLanguage) {
      await _localizedDB.close();
      _dbLanguage = normalizedLanguage;
      _localizedDB = getLocalizedDB(_dbLanguage);
      log.info("DB runtime switched to language: ${_dbLanguage}");
    }
  }
}
