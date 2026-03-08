import 'package:revelation/db/db_common.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';

class TopicsRepository {
  TopicsRepository({TopicsDataSource? dataSource})
    : _dataSource = dataSource ?? DbManagerTopicsDataSource();

  final TopicsDataSource _dataSource;

  Future<List<TopicInfo>> getTopics({required String language}) async {
    await _dataSource.updateLanguage(language);
    final articles = await _dataSource.fetchArticles();
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
    await _dataSource.updateLanguage(language);
    return _dataSource.fetchArticleMarkdown(route);
  }

  Future<TopicInfo?> getTopicByRoute({
    required String route,
    required String language,
  }) async {
    if (route.isEmpty) {
      return null;
    }
    await _dataSource.updateLanguage(language);
    final article = await _dataSource.fetchArticleByRoute(route);
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
    return _dataSource.fetchCommonResource(key);
  }
}
