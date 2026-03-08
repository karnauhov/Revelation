import 'dart:typed_data';

import 'package:revelation/db/db_common.dart' as common_db;
import 'package:revelation/db/db_localized.dart' as localized_db;
import 'package:revelation/managers/db_manager.dart';

abstract class DatabaseGateway {
  bool get isInitialized;

  String get languageCode;

  List<common_db.GreekWord> get greekWords;

  List<localized_db.GreekDesc> get greekDescs;

  List<common_db.PrimarySource> get primarySourceRows;

  List<common_db.PrimarySourceLink> get primarySourceLinkRows;

  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows;

  List<common_db.PrimarySourcePage> get primarySourcePageRows;

  List<common_db.PrimarySourceWord> get primarySourceWordRows;

  List<common_db.PrimarySourceVerse> get primarySourceVerseRows;

  List<localized_db.PrimarySourceText> get primarySourceTextRows;

  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows;

  Future<void> initialize(String language);

  Future<void> updateLanguage(String language);

  Future<List<localized_db.Article>> getArticles({bool onlyVisible = true});

  Future<String> getArticleMarkdown(String route);

  Future<localized_db.Article?> getArticleByRoute(String route);

  Future<common_db.CommonResource?> getCommonResource(String key);

  Future<Uint8List?> getCommonResourceData(String key);
}

class DbManagerDatabaseGateway implements DatabaseGateway {
  DbManagerDatabaseGateway({DBManager? dbManager})
    : _dbManager = dbManager ?? DBManager();

  final DBManager _dbManager;

  @override
  bool get isInitialized => _dbManager.isInitialized;

  @override
  String get languageCode => _dbManager.langDB;

  @override
  List<common_db.GreekWord> get greekWords => _dbManager.greekWords;

  @override
  List<localized_db.GreekDesc> get greekDescs => _dbManager.greekDescs;

  @override
  List<common_db.PrimarySource> get primarySourceRows =>
      _dbManager.primarySourceRows;

  @override
  List<common_db.PrimarySourceLink> get primarySourceLinkRows =>
      _dbManager.primarySourceLinkRows;

  @override
  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows =>
      _dbManager.primarySourceAttributionRows;

  @override
  List<common_db.PrimarySourcePage> get primarySourcePageRows =>
      _dbManager.primarySourcePageRows;

  @override
  List<common_db.PrimarySourceWord> get primarySourceWordRows =>
      _dbManager.primarySourceWordRows;

  @override
  List<common_db.PrimarySourceVerse> get primarySourceVerseRows =>
      _dbManager.primarySourceVerseRows;

  @override
  List<localized_db.PrimarySourceText> get primarySourceTextRows =>
      _dbManager.primarySourceTextRows;

  @override
  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows =>
      _dbManager.primarySourceLinkTextRows;

  @override
  Future<void> initialize(String language) {
    return _dbManager.init(language);
  }

  @override
  Future<void> updateLanguage(String language) {
    return _dbManager.updateLanguage(language);
  }

  @override
  Future<List<localized_db.Article>> getArticles({bool onlyVisible = true}) {
    return _dbManager.getArticles(onlyVisible: onlyVisible);
  }

  @override
  Future<String> getArticleMarkdown(String route) {
    return _dbManager.getArticleMarkdown(route);
  }

  @override
  Future<localized_db.Article?> getArticleByRoute(String route) {
    return _dbManager.getArticleByRoute(route);
  }

  @override
  Future<common_db.CommonResource?> getCommonResource(String key) {
    return _dbManager.getCommonResource(key);
  }

  @override
  Future<Uint8List?> getCommonResourceData(String key) {
    return _dbManager.getCommonResourceData(key);
  }
}
