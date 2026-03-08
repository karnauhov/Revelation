import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/shared/utils/common.dart';

class TopicsRepository {
  TopicsRepository({TopicsDataSource? dataSource})
    : _dataSource = dataSource ?? DbManagerTopicsDataSource();

  final TopicsDataSource _dataSource;

  Future<AppResult<List<TopicInfo>>> getTopics({
    required String language,
  }) async {
    if (language.trim().isEmpty) {
      return const AppFailureResult<List<TopicInfo>>(
        AppFailure.validation('Language must not be empty.'),
      );
    }

    try {
      await _dataSource.updateLanguage(language);
      final articles = await _dataSource.fetchArticles();
      final topics = articles
          .map(
            (article) => TopicInfo(
              name: article.name,
              idIcon: article.idIcon,
              description: article.description,
              route: article.route,
            ),
          )
          .toList(growable: false);
      return AppSuccess<List<TopicInfo>>(topics);
    } catch (error, stackTrace) {
      log.error('Topics loading error: $error', stackTrace);
      return AppFailureResult<List<TopicInfo>>(
        AppFailure.dataSource(
          'Unable to load topics from local database.',
          cause: error,
          stackTrace: stackTrace,
        ),
      );
    }
  }

  Future<AppResult<String>> getArticleMarkdown({
    required String route,
    required String language,
  }) async {
    if (route.isEmpty) {
      return const AppFailureResult<String>(
        AppFailure.validation('Article route must not be empty.'),
      );
    }
    if (language.trim().isEmpty) {
      return const AppFailureResult<String>(
        AppFailure.validation('Language must not be empty.'),
      );
    }

    try {
      await _dataSource.updateLanguage(language);
      final markdown = await _dataSource.fetchArticleMarkdown(route);
      return AppSuccess<String>(markdown);
    } catch (error, stackTrace) {
      log.error('Article markdown loading error: $error', stackTrace);
      return AppFailureResult<String>(
        AppFailure.dataSource(
          'Unable to load article markdown from local database.',
          cause: error,
          stackTrace: stackTrace,
        ),
      );
    }
  }

  Future<AppResult<TopicInfo?>> getTopicByRoute({
    required String route,
    required String language,
  }) async {
    if (route.isEmpty) {
      return const AppFailureResult<TopicInfo?>(
        AppFailure.validation('Article route must not be empty.'),
      );
    }
    if (language.trim().isEmpty) {
      return const AppFailureResult<TopicInfo?>(
        AppFailure.validation('Language must not be empty.'),
      );
    }

    try {
      await _dataSource.updateLanguage(language);
      final article = await _dataSource.fetchArticleByRoute(route);
      if (article == null) {
        return const AppFailureResult<TopicInfo?>(
          AppFailure.notFound('Article was not found by route.'),
        );
      }
      return AppSuccess<TopicInfo?>(
        TopicInfo(
          name: article.name,
          idIcon: article.idIcon,
          description: article.description,
          route: article.route,
        ),
      );
    } catch (error, stackTrace) {
      log.error('Topic by route loading error: $error', stackTrace);
      return AppFailureResult<TopicInfo?>(
        AppFailure.dataSource(
          'Unable to load article metadata from local database.',
          cause: error,
          stackTrace: stackTrace,
        ),
      );
    }
  }

  Future<AppResult<CommonResource?>> getCommonResource(String key) async {
    if (key.isEmpty) {
      return const AppFailureResult<CommonResource?>(
        AppFailure.validation('Common resource key must not be empty.'),
      );
    }

    try {
      return AppSuccess<CommonResource?>(
        await _dataSource.fetchCommonResource(key),
      );
    } catch (error, stackTrace) {
      log.error('Common resource loading error: $error', stackTrace);
      return AppFailureResult<CommonResource?>(
        AppFailure.dataSource(
          'Unable to load common resource from local database.',
          cause: error,
          stackTrace: stackTrace,
        ),
      );
    }
  }
}
