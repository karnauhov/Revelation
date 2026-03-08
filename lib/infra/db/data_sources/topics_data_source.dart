import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/infra/db/runtime/db_manager_gateway.dart';

abstract class TopicsDataSource {
  Future<void> updateLanguage(String language);

  Future<List<Article>> fetchArticles({bool onlyVisible = true});

  Future<String> fetchArticleMarkdown(String route);

  Future<Article?> fetchArticleByRoute(String route);

  Future<CommonResource?> fetchCommonResource(String key);
}

class DbManagerTopicsDataSource implements TopicsDataSource {
  DbManagerTopicsDataSource({DatabaseGateway? databaseGateway})
    : _databaseGateway = databaseGateway ?? DbManagerDatabaseGateway();

  final DatabaseGateway _databaseGateway;

  @override
  Future<void> updateLanguage(String language) {
    return _databaseGateway.updateLanguage(language);
  }

  @override
  Future<List<Article>> fetchArticles({bool onlyVisible = true}) {
    return _databaseGateway.getArticles(onlyVisible: onlyVisible);
  }

  @override
  Future<String> fetchArticleMarkdown(String route) {
    return _databaseGateway.getArticleMarkdown(route);
  }

  @override
  Future<Article?> fetchArticleByRoute(String route) {
    return _databaseGateway.getArticleByRoute(route);
  }

  @override
  Future<CommonResource?> fetchCommonResource(String key) {
    return _databaseGateway.getCommonResource(key);
  }
}

