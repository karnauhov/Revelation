import 'package:drift/drift.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/connectors/shared.dart';
import 'package:revelation/shared/utils/common.dart';

class DBManager {
  static final DBManager _instance = DBManager._internal();
  DBManager._internal();

  factory DBManager() {
    return _instance;
  }

  String _dbLanguage = 'en';
  bool _isInitialized = false;
  bool _hasLocalizedDb = false;
  late common_db.CommonDB _commonDB;
  late localized_db.LocalizedDB _localizedDB;
  late List<common_db.GreekWord> _greekWords;
  late List<localized_db.GreekDesc> _greekDescs;
  late List<localized_db.Article> _articles;
  late List<common_db.PrimarySource> _primarySourceRows;
  late List<common_db.PrimarySourceLink> _primarySourceLinkRows;
  late List<common_db.PrimarySourceAttribution> _primarySourceAttributionRows;
  late List<common_db.PrimarySourcePage> _primarySourcePageRows;
  late List<common_db.PrimarySourceWord> _primarySourceWordRows;
  late List<common_db.PrimarySourceVerse> _primarySourceVerseRows;
  late List<localized_db.PrimarySourceText> _primarySourceTextRows;
  late List<localized_db.PrimarySourceLinkText> _primarySourceLinkTextRows;

  List<common_db.GreekWord> get greekWords => _greekWords;
  List<localized_db.GreekDesc> get greekDescs => _greekDescs;
  List<localized_db.Article> get articles => _articles;
  List<common_db.PrimarySource> get primarySourceRows => _primarySourceRows;
  List<common_db.PrimarySourceLink> get primarySourceLinkRows =>
      _primarySourceLinkRows;
  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows =>
      _primarySourceAttributionRows;
  List<common_db.PrimarySourcePage> get primarySourcePageRows =>
      _primarySourcePageRows;
  List<common_db.PrimarySourceWord> get primarySourceWordRows =>
      _primarySourceWordRows;
  List<common_db.PrimarySourceVerse> get primarySourceVerseRows =>
      _primarySourceVerseRows;
  List<localized_db.PrimarySourceText> get primarySourceTextRows =>
      _primarySourceTextRows;
  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows =>
      _primarySourceLinkTextRows;
  String get langDB => _dbLanguage;
  bool get isInitialized => _isInitialized;

  Future<void> init(String language) async {
    _dbLanguage = language;
    _commonDB = getCommonDB();
    _localizedDB = getLocalizedDB(_dbLanguage);
    _hasLocalizedDb = true;
    _greekWords = await _commonDB.select(_commonDB.greekWords).get();
    _greekDescs = await _localizedDB.select(_localizedDB.greekDescs).get();
    _articles = await getArticles();
    await _loadPrimarySourceRows();
    _isInitialized = true;
    log.info("DB is initialized (${language})");
  }

  Future<void> updateLanguage(String newLanguage) async {
    if (!_isInitialized) {
      return;
    }
    if (_dbLanguage != newLanguage) {
      await _localizedDB.close();
      _dbLanguage = newLanguage;
      _localizedDB = getLocalizedDB(_dbLanguage);
      _hasLocalizedDb = true;
      _greekDescs = await _localizedDB.select(_localizedDB.greekDescs).get();
      _articles = await getArticles();
      await _loadPrimarySourceRows();
      log.info("The DB is reinitialized for the new language: ${newLanguage}");
    }
  }

  Future<void> _loadPrimarySourceRows() async {
    _primarySourceRows = await _commonDB.select(_commonDB.primarySources).get();
    _primarySourceLinkRows = await _commonDB
        .select(_commonDB.primarySourceLinks)
        .get();
    _primarySourceAttributionRows = await _commonDB
        .select(_commonDB.primarySourceAttributions)
        .get();
    _primarySourcePageRows = await _commonDB
        .select(_commonDB.primarySourcePages)
        .get();
    _primarySourceWordRows = await _commonDB
        .select(_commonDB.primarySourceWords)
        .get();
    _primarySourceVerseRows = await _commonDB
        .select(_commonDB.primarySourceVerses)
        .get();
    _primarySourceTextRows = await _localizedDB
        .select(_localizedDB.primarySourceTexts)
        .get();
    _primarySourceLinkTextRows = await _localizedDB
        .select(_localizedDB.primarySourceLinkTexts)
        .get();
  }

  Future<List<localized_db.Article>> getArticles({
    bool onlyVisible = true,
  }) async {
    if (!_hasLocalizedDb) {
      return [];
    }
    final query = _localizedDB.select(_localizedDB.articles)
      ..orderBy([
        (t) => OrderingTerm(expression: t.sortOrder, mode: OrderingMode.asc),
        (t) => OrderingTerm(expression: t.route, mode: OrderingMode.asc),
      ]);
    if (onlyVisible) {
      query.where((t) => t.isVisible.equals(true));
    }
    return query.get();
  }

  Future<String> getArticleMarkdown(String route) async {
    if (!_isInitialized || route.isEmpty) {
      return "";
    }
    final query = _localizedDB.select(_localizedDB.articles)
      ..where((a) => a.route.equals(route));
    final article = await query.getSingleOrNull();
    return article?.markdown ?? "";
  }

  Future<localized_db.Article?> getArticleByRoute(String route) async {
    if (!_isInitialized || route.isEmpty) {
      return null;
    }
    final query = _localizedDB.select(_localizedDB.articles)
      ..where((t) => t.route.equals(route));
    return query.getSingleOrNull();
  }

  Future<common_db.CommonResource?> getCommonResource(String key) async {
    if (!_isInitialized || key.isEmpty) {
      return null;
    }
    final query = _commonDB.select(_commonDB.commonResources)
      ..where((r) => r.key.equals(key));
    return query.getSingleOrNull();
  }

  Future<Uint8List?> getCommonResourceData(String key) async {
    final resource = await getCommonResource(key);
    return resource?.data;
  }
}
