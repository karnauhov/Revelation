import 'package:drift/drift.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/gateways/articles_database_gateway.dart';

void main() {
  test('DbManagerTopicsDataSource delegates to gateway', () async {
    final gateway = _FakeArticlesGateway()
      ..articles = [
        localized_db.Article(
          route: 'r1',
          name: 'A',
          description: 'Desc',
          idIcon: 'icon',
          sortOrder: 0,
          isVisible: true,
          markdown: '# md',
        ),
      ]
      ..markdown = '# md'
      ..articleByRoute = localized_db.Article(
        route: 'r1',
        name: 'A',
        description: 'Desc',
        idIcon: 'icon',
        sortOrder: 0,
        isVisible: true,
        markdown: '# md',
      )
      ..commonResource = common_db.CommonResource(
        key: 'res',
        fileName: 'file',
        mimeType: 'text/plain',
        data: Uint8List.fromList([1, 2, 3]),
      );

    final dataSource = DbManagerTopicsDataSource(databaseGateway: gateway);

    await dataSource.updateLanguage('en');
    final articles = await dataSource.fetchArticles(onlyVisible: false);
    final markdown = await dataSource.fetchArticleMarkdown('r1');
    final article = await dataSource.fetchArticleByRoute('r1');
    final resource = await dataSource.fetchCommonResource('res');

    expect(gateway.updatedLanguage, 'en');
    expect(gateway.onlyVisibleArgs, [false]);
    expect(articles.single.route, 'r1');
    expect(markdown, '# md');
    expect(article?.route, 'r1');
    expect(resource?.key, 'res');
  });
}

class _FakeArticlesGateway implements ArticlesDatabaseGateway {
  String? initializedLanguage;
  String? updatedLanguage;
  List<bool> onlyVisibleArgs = [];
  List<localized_db.Article> articles = const [];
  String markdown = '';
  localized_db.Article? articleByRoute;
  common_db.CommonResource? commonResource;

  @override
  bool get isInitialized => true;

  @override
  String get languageCode => 'en';

  @override
  GeneratedDatabase? getActiveDatabase(String dbFile) => null;

  @override
  Future<void> initialize(String language) async {
    initializedLanguage = language;
  }

  @override
  Future<void> updateLanguage(String language) async {
    updatedLanguage = language;
  }

  @override
  Future<List<localized_db.Article>> getArticles({
    bool onlyVisible = true,
  }) async {
    onlyVisibleArgs.add(onlyVisible);
    return articles;
  }

  @override
  Future<String> getArticleMarkdown(String route) async {
    return markdown;
  }

  @override
  Future<localized_db.Article?> getArticleByRoute(String route) async {
    return articleByRoute;
  }

  @override
  Future<common_db.CommonResource?> getCommonResource(String key) async {
    return commonResource;
  }
}
