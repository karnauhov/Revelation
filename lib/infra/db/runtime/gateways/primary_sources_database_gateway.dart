import 'dart:typed_data';

import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/db_manager.dart';

abstract class PrimarySourcesDatabaseGateway {
  bool get isInitialized;

  List<common_db.PrimarySource> get primarySourceRows;

  List<common_db.PrimarySourceLink> get primarySourceLinkRows;

  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows;

  List<common_db.PrimarySourcePage> get primarySourcePageRows;

  List<common_db.PrimarySourceWord> get primarySourceWordRows;

  List<common_db.PrimarySourceVerse> get primarySourceVerseRows;

  List<localized_db.PrimarySourceText> get primarySourceTextRows;

  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows;

  Future<void> initialize(String language);

  Future<void> updateLanguage(String language);

  Future<Uint8List?> getCommonResourceData(String key);
}

class DbManagerPrimarySourcesDatabaseGateway
    implements PrimarySourcesDatabaseGateway {
  static final DbManagerPrimarySourcesDatabaseGateway _instance =
      DbManagerPrimarySourcesDatabaseGateway._internal();

  factory DbManagerPrimarySourcesDatabaseGateway() {
    return _instance;
  }

  DbManagerPrimarySourcesDatabaseGateway._internal();

  final DBManager _dbManager = DBManager();
  List<common_db.PrimarySource> _primarySourceRows = const [];
  List<common_db.PrimarySourceLink> _primarySourceLinkRows = const [];
  List<common_db.PrimarySourceAttribution> _primarySourceAttributionRows =
      const [];
  List<common_db.PrimarySourcePage> _primarySourcePageRows = const [];
  List<common_db.PrimarySourceWord> _primarySourceWordRows = const [];
  List<common_db.PrimarySourceVerse> _primarySourceVerseRows = const [];
  List<localized_db.PrimarySourceText> _primarySourceTextRows = const [];
  List<localized_db.PrimarySourceLinkText> _primarySourceLinkTextRows =
      const [];

  @override
  bool get isInitialized => _dbManager.isInitialized;

  @override
  List<common_db.PrimarySource> get primarySourceRows => _primarySourceRows;

  @override
  List<common_db.PrimarySourceLink> get primarySourceLinkRows =>
      _primarySourceLinkRows;

  @override
  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows =>
      _primarySourceAttributionRows;

  @override
  List<common_db.PrimarySourcePage> get primarySourcePageRows =>
      _primarySourcePageRows;

  @override
  List<common_db.PrimarySourceWord> get primarySourceWordRows =>
      _primarySourceWordRows;

  @override
  List<common_db.PrimarySourceVerse> get primarySourceVerseRows =>
      _primarySourceVerseRows;

  @override
  List<localized_db.PrimarySourceText> get primarySourceTextRows =>
      _primarySourceTextRows;

  @override
  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows =>
      _primarySourceLinkTextRows;

  @override
  Future<void> initialize(String language) async {
    await _dbManager.init(language);
    await _reloadPrimarySources();
  }

  @override
  Future<void> updateLanguage(String language) async {
    await _dbManager.updateLanguage(language);
    await _reloadPrimarySources();
  }

  @override
  Future<Uint8List?> getCommonResourceData(String key) async {
    if (!_dbManager.isInitialized || key.isEmpty) {
      return null;
    }
    final query = _dbManager.commonDB.select(
      _dbManager.commonDB.commonResources,
    )..where((resource) => resource.key.equals(key));
    final resource = await query.getSingleOrNull();
    return resource?.data;
  }

  Future<void> _reloadPrimarySources() async {
    if (!_dbManager.isInitialized) {
      _primarySourceRows = const [];
      _primarySourceLinkRows = const [];
      _primarySourceAttributionRows = const [];
      _primarySourcePageRows = const [];
      _primarySourceWordRows = const [];
      _primarySourceVerseRows = const [];
      _primarySourceTextRows = const [];
      _primarySourceLinkTextRows = const [];
      return;
    }
    _primarySourceRows = List<common_db.PrimarySource>.unmodifiable(
      await _dbManager.commonDB
          .select(_dbManager.commonDB.primarySources)
          .get(),
    );
    _primarySourceLinkRows = List<common_db.PrimarySourceLink>.unmodifiable(
      await _dbManager.commonDB
          .select(_dbManager.commonDB.primarySourceLinks)
          .get(),
    );
    _primarySourceAttributionRows =
        List<common_db.PrimarySourceAttribution>.unmodifiable(
          await _dbManager.commonDB
              .select(_dbManager.commonDB.primarySourceAttributions)
              .get(),
        );
    _primarySourcePageRows = List<common_db.PrimarySourcePage>.unmodifiable(
      await _dbManager.commonDB
          .select(_dbManager.commonDB.primarySourcePages)
          .get(),
    );
    _primarySourceWordRows = List<common_db.PrimarySourceWord>.unmodifiable(
      await _dbManager.commonDB
          .select(_dbManager.commonDB.primarySourceWords)
          .get(),
    );
    _primarySourceVerseRows = List<common_db.PrimarySourceVerse>.unmodifiable(
      await _dbManager.commonDB
          .select(_dbManager.commonDB.primarySourceVerses)
          .get(),
    );
    _primarySourceTextRows = List<localized_db.PrimarySourceText>.unmodifiable(
      await _dbManager.localizedDB
          .select(_dbManager.localizedDB.primarySourceTexts)
          .get(),
    );
    _primarySourceLinkTextRows =
        List<localized_db.PrimarySourceLinkText>.unmodifiable(
          await _dbManager.localizedDB
              .select(_dbManager.localizedDB.primarySourceLinkTexts)
              .get(),
        );
  }
}
