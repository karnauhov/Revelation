import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  test('getTopics returns validation failure for empty language', () async {
    final dataSource = _FakeTopicsDataSource();
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getTopics(language: '  ');

    expect(result, isA<AppFailureResult<List<TopicInfo>>>());
    expect(
      (result as AppFailureResult<List<TopicInfo>>).error,
      const AppFailure.validation('Language must not be empty.'),
    );
    expect(dataSource.calls, isEmpty);
  });

  test('getTopics maps articles and preserves order', () async {
    final dataSource = _FakeTopicsDataSource(
      articles: [
        _article(
          route: 'r2',
          name: 'Second',
          description: 'Desc 2',
          idIcon: 'icon-2',
          sortOrder: 2,
        ),
        _article(
          route: 'r1',
          name: 'First',
          description: 'Desc 1',
          idIcon: 'icon-1',
          sortOrder: 1,
        ),
      ],
    );
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getTopics(language: 'en');

    expect(result, isA<AppSuccess<List<TopicInfo>>>());
    final topics = (result as AppSuccess<List<TopicInfo>>).data;
    expect(topics.map((item) => item.route), ['r2', 'r1']);
    expect(
      topics.first,
      TopicInfo(
        name: 'Second',
        idIcon: 'icon-2',
        description: 'Desc 2',
        route: 'r2',
      ),
    );
    expect(dataSource.calls, ['update:en', 'articles:true']);
  });

  test('getTopics returns empty list when no articles', () async {
    final dataSource = _FakeTopicsDataSource(articles: const []);
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getTopics(language: 'en');

    expect(result, isA<AppSuccess<List<TopicInfo>>>());
    expect((result as AppSuccess<List<TopicInfo>>).data, isEmpty);
  });

  test('getTopics returns data source failure when update fails', () async {
    final dataSource = _FakeTopicsDataSource(throwOnUpdateLanguage: true);
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getTopics(language: 'en');

    expect(result, isA<AppFailureResult<List<TopicInfo>>>());
    expect(
      (result as AppFailureResult<List<TopicInfo>>).error,
      const AppFailure.dataSource('Unable to load topics from local database.'),
    );
    expect(dataSource.calls, ['update:en']);
  });

  test('getTopics returns data source failure when fetch fails', () async {
    final dataSource = _FakeTopicsDataSource(throwOnFetchArticles: true);
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getTopics(language: 'en');

    expect(result, isA<AppFailureResult<List<TopicInfo>>>());
    expect(
      (result as AppFailureResult<List<TopicInfo>>).error,
      const AppFailure.dataSource('Unable to load topics from local database.'),
    );
    expect(dataSource.calls, ['update:en', 'articles:true']);
  });

  test(
    'getArticleMarkdown returns validation failure for empty route',
    () async {
      final dataSource = _FakeTopicsDataSource();
      final repository = TopicsRepository(dataSource: dataSource);

      final result = await repository.getArticleMarkdown(
        route: '',
        language: 'en',
      );

      expect(result, isA<AppFailureResult<String>>());
      expect(
        (result as AppFailureResult<String>).error,
        const AppFailure.validation('Article route must not be empty.'),
      );
      expect(dataSource.calls, isEmpty);
    },
  );

  test(
    'getArticleMarkdown returns validation failure for empty language',
    () async {
      final dataSource = _FakeTopicsDataSource();
      final repository = TopicsRepository(dataSource: dataSource);

      final result = await repository.getArticleMarkdown(
        route: 'route-1',
        language: ' ',
      );

      expect(result, isA<AppFailureResult<String>>());
      expect(
        (result as AppFailureResult<String>).error,
        const AppFailure.validation('Language must not be empty.'),
      );
      expect(dataSource.calls, isEmpty);
    },
  );

  test('getArticleMarkdown returns markdown content', () async {
    final dataSource = _FakeTopicsDataSource(
      markdownByRoute: const {'route-1': '# Title'},
    );
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getArticleMarkdown(
      route: 'route-1',
      language: 'en',
    );

    expect(result, isA<AppSuccess<String>>());
    expect((result as AppSuccess<String>).data, '# Title');
    expect(dataSource.calls, ['update:en', 'markdown:route-1']);
  });

  test('getArticleMarkdown returns data source failure on error', () async {
    final dataSource = _FakeTopicsDataSource(throwOnFetchMarkdown: true);
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getArticleMarkdown(
      route: 'route-1',
      language: 'en',
    );

    expect(result, isA<AppFailureResult<String>>());
    expect(
      (result as AppFailureResult<String>).error,
      const AppFailure.dataSource(
        'Unable to load article markdown from local database.',
      ),
    );
    expect(dataSource.calls, ['update:en', 'markdown:route-1']);
  });

  test('getTopicByRoute returns notFound when article is missing', () async {
    final dataSource = _FakeTopicsDataSource();
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getTopicByRoute(
      route: 'route-1',
      language: 'en',
    );

    expect(result, isA<AppFailureResult<TopicInfo?>>());
    expect(
      (result as AppFailureResult<TopicInfo?>).error,
      const AppFailure.notFound('Article was not found by route.'),
    );
    expect(dataSource.calls, ['update:en', 'article:route-1']);
  });

  test('getTopicByRoute maps article to TopicInfo', () async {
    final dataSource = _FakeTopicsDataSource(
      articleByRoute: _article(
        route: 'route-1',
        name: 'Topic',
        description: 'Desc',
        idIcon: 'icon',
      ),
    );
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getTopicByRoute(
      route: 'route-1',
      language: 'en',
    );

    expect(result, isA<AppSuccess<TopicInfo?>>());
    expect(
      (result as AppSuccess<TopicInfo?>).data,
      TopicInfo(
        name: 'Topic',
        idIcon: 'icon',
        description: 'Desc',
        route: 'route-1',
      ),
    );
  });

  test('getTopicByRoute returns data source failure on error', () async {
    final dataSource = _FakeTopicsDataSource(throwOnFetchArticleByRoute: true);
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getTopicByRoute(
      route: 'route-1',
      language: 'en',
    );

    expect(result, isA<AppFailureResult<TopicInfo?>>());
    expect(
      (result as AppFailureResult<TopicInfo?>).error,
      const AppFailure.dataSource(
        'Unable to load article metadata from local database.',
      ),
    );
    expect(dataSource.calls, ['update:en', 'article:route-1']);
  });

  test('getCommonResource returns validation failure for empty key', () async {
    final dataSource = _FakeTopicsDataSource();
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getCommonResource('');

    expect(result, isA<AppFailureResult<TopicResource?>>());
    expect(
      (result as AppFailureResult<TopicResource?>).error,
      const AppFailure.validation('Common resource key must not be empty.'),
    );
    expect(dataSource.calls, isEmpty);
  });

  test('getCommonResource returns null when resource missing', () async {
    final dataSource = _FakeTopicsDataSource(commonResource: null);
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getCommonResource('res-1');

    expect(result, isA<AppSuccess<TopicResource?>>());
    expect((result as AppSuccess<TopicResource?>).data, isNull);
    expect(dataSource.calls, ['resource:res-1']);
  });

  test('getCommonResource maps resource data', () async {
    final bytes = Uint8List.fromList([1, 2, 3]);
    final dataSource = _FakeTopicsDataSource(
      commonResource: common_db.CommonResource(
        key: 'res-1',
        fileName: 'file.png',
        mimeType: 'image/png',
        data: bytes,
      ),
    );
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getCommonResource('res-1');

    expect(result, isA<AppSuccess<TopicResource?>>());
    expect(
      (result as AppSuccess<TopicResource?>).data,
      TopicResource(
        fileName: 'file.png',
        mimeType: 'image/png',
        data: Uint8List.fromList([1, 2, 3]),
      ),
    );
  });

  test('getCommonResource returns data source failure on error', () async {
    final dataSource = _FakeTopicsDataSource(throwOnFetchCommonResource: true);
    final repository = TopicsRepository(dataSource: dataSource);

    final result = await repository.getCommonResource('res-1');

    expect(result, isA<AppFailureResult<TopicResource?>>());
    expect(
      (result as AppFailureResult<TopicResource?>).error,
      const AppFailure.dataSource(
        'Unable to load common resource from local database.',
      ),
    );
    expect(dataSource.calls, ['resource:res-1']);
  });

  test('getTopics returns fresh data when language changes', () async {
    final dataSource = _FakeTopicsDataSource(
      articles: [
        _article(
          route: 'r1',
          name: 'First',
          description: 'Desc 1',
          idIcon: 'icon-1',
        ),
      ],
    );
    final repository = TopicsRepository(dataSource: dataSource);

    final first = await repository.getTopics(language: 'en');
    dataSource.articles = [
      _article(
        route: 'r2',
        name: 'Second',
        description: 'Desc 2',
        idIcon: 'icon-2',
      ),
    ];
    final second = await repository.getTopics(language: 'ru');

    expect((first as AppSuccess<List<TopicInfo>>).data.single.route, 'r1');
    expect((second as AppSuccess<List<TopicInfo>>).data.single.route, 'r2');
    expect(dataSource.calls, [
      'update:en',
      'articles:true',
      'update:ru',
      'articles:true',
    ]);
  });
}

localized_db.Article _article({
  required String route,
  required String name,
  required String description,
  required String idIcon,
  int sortOrder = 0,
  bool isVisible = true,
  String markdown = '',
}) {
  return localized_db.Article(
    route: route,
    name: name,
    description: description,
    idIcon: idIcon,
    sortOrder: sortOrder,
    isVisible: isVisible,
    markdown: markdown,
  );
}

class _FakeTopicsDataSource implements TopicsDataSource {
  _FakeTopicsDataSource({
    this.articles = const [],
    this.articleByRoute,
    this.commonResource,
    this.markdownByRoute = const {},
    this.throwOnUpdateLanguage = false,
    this.throwOnFetchArticles = false,
    this.throwOnFetchMarkdown = false,
    this.throwOnFetchArticleByRoute = false,
    this.throwOnFetchCommonResource = false,
  });

  List<localized_db.Article> articles;
  localized_db.Article? articleByRoute;
  common_db.CommonResource? commonResource;
  Map<String, String> markdownByRoute;
  final List<String> calls = [];

  final bool throwOnUpdateLanguage;
  final bool throwOnFetchArticles;
  final bool throwOnFetchMarkdown;
  final bool throwOnFetchArticleByRoute;
  final bool throwOnFetchCommonResource;

  @override
  Future<void> updateLanguage(String language) async {
    calls.add('update:$language');
    if (throwOnUpdateLanguage) {
      throw StateError('update');
    }
  }

  @override
  Future<List<localized_db.Article>> fetchArticles({
    bool onlyVisible = true,
  }) async {
    calls.add('articles:$onlyVisible');
    if (throwOnFetchArticles) {
      throw StateError('articles');
    }
    return articles;
  }

  @override
  Future<String> fetchArticleMarkdown(String route) async {
    calls.add('markdown:$route');
    if (throwOnFetchMarkdown) {
      throw StateError('markdown');
    }
    return markdownByRoute[route] ?? '';
  }

  @override
  Future<localized_db.Article?> fetchArticleByRoute(String route) async {
    calls.add('article:$route');
    if (throwOnFetchArticleByRoute) {
      throw StateError('article');
    }
    return articleByRoute;
  }

  @override
  Future<common_db.CommonResource?> fetchCommonResource(String key) async {
    calls.add('resource:$key');
    if (throwOnFetchCommonResource) {
      throw StateError('resource');
    }
    return commonResource;
  }
}
