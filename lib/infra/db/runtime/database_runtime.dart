import 'package:revelation/infra/db/runtime/gateways/articles_database_gateway.dart';
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';
import 'package:revelation/infra/db/runtime/gateways/primary_sources_database_gateway.dart';

abstract class DatabaseRuntime {
  Future<void> initialize(String language);

  Future<void> updateLanguage(String language);
}

class DbManagerDatabaseRuntime implements DatabaseRuntime {
  DbManagerDatabaseRuntime({
    ArticlesDatabaseGateway? articlesGateway,
    LexiconDatabaseGateway? lexiconGateway,
    PrimarySourcesDatabaseGateway? primarySourcesGateway,
  }) : _articlesGateway = articlesGateway ?? DbManagerArticlesDatabaseGateway(),
       _lexiconGateway = lexiconGateway ?? DbManagerLexiconDatabaseGateway(),
       _primarySourcesGateway =
           primarySourcesGateway ?? DbManagerPrimarySourcesDatabaseGateway();

  final ArticlesDatabaseGateway _articlesGateway;
  final LexiconDatabaseGateway _lexiconGateway;
  final PrimarySourcesDatabaseGateway _primarySourcesGateway;

  @override
  Future<void> initialize(String language) async {
    await _articlesGateway.initialize(language);
    await _lexiconGateway.initialize(language);
    await _primarySourcesGateway.initialize(language);
  }

  @override
  Future<void> updateLanguage(String language) async {
    await _articlesGateway.updateLanguage(language);
    await _lexiconGateway.updateLanguage(language);
    await _primarySourcesGateway.updateLanguage(language);
  }
}
