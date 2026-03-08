import 'package:revelation/db/db_common.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/managers/db_manager.dart';

class TopicsRepository {
  TopicsRepository({DBManager? dbManager})
    : _dbManager = dbManager ?? DBManager();

  final DBManager _dbManager;

  Future<List<TopicInfo>> getTopics({required String language}) async {
    await _dbManager.updateLanguage(language);
    final articles = await _dbManager.getArticles();
    return articles
        .map(
          (article) => TopicInfo(
            name: article.name,
            idIcon: article.idIcon,
            description: article.description,
            route: article.route,
          ),
        )
        .toList(growable: false);
  }

  Future<String> getArticleMarkdown({
    required String route,
    required String language,
  }) async {
    if (route.isEmpty) {
      return '';
    }
    await _dbManager.updateLanguage(language);
    return _dbManager.getArticleMarkdown(route);
  }

  Future<TopicInfo?> getTopicByRoute({
    required String route,
    required String language,
  }) async {
    if (route.isEmpty) {
      return null;
    }
    await _dbManager.updateLanguage(language);
    final article = await _dbManager.getArticleByRoute(route);
    if (article == null) {
      return null;
    }
    return TopicInfo(
      name: article.name,
      idIcon: article.idIcon,
      description: article.description,
      route: article.route,
    );
  }

  Future<CommonResource?> getCommonResource(String key) async {
    if (key.isEmpty) {
      return null;
    }
    return _dbManager.getCommonResource(key);
  }
}
