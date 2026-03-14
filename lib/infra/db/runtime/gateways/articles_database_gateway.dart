import 'package:drift/drift.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/db_manager.dart';

abstract class ArticlesDatabaseGateway {
  bool get isInitialized;

  String get languageCode;

  Future<void> initialize(String language);

  Future<void> updateLanguage(String language);

  Future<List<localized_db.Article>> getArticles({bool onlyVisible = true});

  Future<String> getArticleMarkdown(String route);

  Future<localized_db.Article?> getArticleByRoute(String route);

  Future<common_db.CommonResource?> getCommonResource(String key);
}

class DbManagerArticlesDatabaseGateway implements ArticlesDatabaseGateway {
  static final DbManagerArticlesDatabaseGateway _instance =
      DbManagerArticlesDatabaseGateway._internal();

  factory DbManagerArticlesDatabaseGateway() {
    return _instance;
  }

  DbManagerArticlesDatabaseGateway._internal();

  final DBManager _dbManager = DBManager();

  @override
  bool get isInitialized => _dbManager.isInitialized;

  @override
  String get languageCode => _dbManager.langDB;

  @override
  Future<void> initialize(String language) {
    return _dbManager.init(language);
  }

  @override
  Future<void> updateLanguage(String language) {
    return _dbManager.updateLanguage(language);
  }

  @override
  Future<List<localized_db.Article>> getArticles({
    bool onlyVisible = true,
  }) async {
    if (!_dbManager.isInitialized) {
      return const [];
    }
    final query = _dbManager.localizedDB.select(_dbManager.localizedDB.articles)
      ..orderBy([
        (t) => OrderingTerm(expression: t.sortOrder, mode: OrderingMode.asc),
        (t) => OrderingTerm(expression: t.route, mode: OrderingMode.asc),
      ]);
    if (onlyVisible) {
      query.where((t) => t.isVisible.equals(true));
    }
    return query.get();
  }

  @override
  Future<String> getArticleMarkdown(String route) async {
    if (!_dbManager.isInitialized || route.isEmpty) {
      return '';
    }
    final query = _dbManager.localizedDB.select(_dbManager.localizedDB.articles)
      ..where((article) => article.route.equals(route));
    final article = await query.getSingleOrNull();
    return article?.markdown ?? '';
  }

  @override
  Future<localized_db.Article?> getArticleByRoute(String route) {
    if (!_dbManager.isInitialized || route.isEmpty) {
      return Future.value(null);
    }
    final query = _dbManager.localizedDB.select(_dbManager.localizedDB.articles)
      ..where((article) => article.route.equals(route));
    return query.getSingleOrNull();
  }

  @override
  Future<common_db.CommonResource?> getCommonResource(String key) {
    if (!_dbManager.isInitialized || key.isEmpty) {
      return Future.value(null);
    }
    final query = _dbManager.commonDB.select(
      _dbManager.commonDB.commonResources,
    )..where((resource) => resource.key.equals(key));
    return query.getSingleOrNull();
  }
}
