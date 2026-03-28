import 'package:drift/drift.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/database_runtime.dart';
import 'package:revelation/infra/db/runtime/gateways/articles_database_gateway.dart';
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';
import 'package:revelation/infra/db/runtime/gateways/primary_sources_database_gateway.dart';

void main() {
  test(
    'DbManagerDatabaseRuntime delegates initialize and update to all gateways',
    () async {
      final calls = <String>[];
      final articles = _FakeArticlesGateway(calls);
      final lexicon = _FakeLexiconGateway(calls);
      final primarySources = _FakePrimarySourcesGateway(calls);
      final runtime = DbManagerDatabaseRuntime(
        articlesGateway: articles,
        lexiconGateway: lexicon,
        primarySourcesGateway: primarySources,
      );

      await runtime.initialize('en');
      await runtime.updateLanguage('es');

      expect(calls, <String>[
        'articles.initialize:en',
        'lexicon.initialize:en',
        'primary.initialize:en',
        'articles.update:es',
        'lexicon.update:es',
        'primary.update:es',
      ]);
    },
  );
}

class _FakeArticlesGateway implements ArticlesDatabaseGateway {
  _FakeArticlesGateway(this.calls);

  final List<String> calls;

  @override
  bool get isInitialized => true;

  @override
  String get languageCode => 'en';

  @override
  GeneratedDatabase? getActiveDatabase(String dbFile) => null;

  @override
  Future<void> initialize(String language) async {
    calls.add('articles.initialize:$language');
  }

  @override
  Future<void> updateLanguage(String language) async {
    calls.add('articles.update:$language');
  }

  @override
  Future<List<localized_db.Article>> getArticles({
    bool onlyVisible = true,
  }) async => const [];

  @override
  Future<String> getArticleMarkdown(String route) async => '';

  @override
  Future<localized_db.Article?> getArticleByRoute(String route) async => null;

  @override
  Future<common_db.CommonResource?> getCommonResource(String key) async => null;
}

class _FakeLexiconGateway implements LexiconDatabaseGateway {
  _FakeLexiconGateway(this.calls);

  final List<String> calls;

  @override
  bool get isInitialized => true;

  @override
  String get languageCode => 'en';

  @override
  List<common_db.GreekWord> get greekWords => const [];

  @override
  List<localized_db.GreekDesc> get greekDescs => const [];

  @override
  Future<void> initialize(String language) async {
    calls.add('lexicon.initialize:$language');
  }

  @override
  Future<void> updateLanguage(String language) async {
    calls.add('lexicon.update:$language');
  }
}

class _FakePrimarySourcesGateway implements PrimarySourcesDatabaseGateway {
  _FakePrimarySourcesGateway(this.calls);

  final List<String> calls;

  @override
  bool get isInitialized => true;

  @override
  List<common_db.PrimarySource> get primarySourceRows => const [];

  @override
  List<common_db.PrimarySourceLink> get primarySourceLinkRows => const [];

  @override
  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows =>
      const [];

  @override
  List<common_db.PrimarySourcePage> get primarySourcePageRows => const [];

  @override
  List<common_db.PrimarySourceWord> get primarySourceWordRows => const [];

  @override
  List<common_db.PrimarySourceVerse> get primarySourceVerseRows => const [];

  @override
  List<localized_db.PrimarySourceText> get primarySourceTextRows => const [];

  @override
  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows =>
      const [];

  @override
  Future<void> initialize(String language) async {
    calls.add('primary.initialize:$language');
  }

  @override
  Future<void> updateLanguage(String language) async {
    calls.add('primary.update:$language');
  }

  @override
  Future<Uint8List?> getCommonResourceData(String key) async => null;
}
