import 'dart:typed_data';

import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/db_manager_gateway.dart';

abstract class PrimarySourcesDataSource {
  bool get isInitialized;

  List<common_db.PrimarySource> get primarySourceRows;

  List<common_db.PrimarySourceLink> get primarySourceLinkRows;

  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows;

  List<common_db.PrimarySourcePage> get primarySourcePageRows;

  List<common_db.PrimarySourceWord> get primarySourceWordRows;

  List<common_db.PrimarySourceVerse> get primarySourceVerseRows;

  List<localized_db.PrimarySourceText> get primarySourceTextRows;

  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows;

  Future<Uint8List?> getCommonResourceData(String key);
}

class DbManagerPrimarySourcesDataSource implements PrimarySourcesDataSource {
  DbManagerPrimarySourcesDataSource({DatabaseGateway? databaseGateway})
    : _databaseGateway = databaseGateway ?? DbManagerDatabaseGateway();

  final DatabaseGateway _databaseGateway;

  @override
  bool get isInitialized => _databaseGateway.isInitialized;

  @override
  List<common_db.PrimarySource> get primarySourceRows =>
      _databaseGateway.primarySourceRows;

  @override
  List<common_db.PrimarySourceLink> get primarySourceLinkRows =>
      _databaseGateway.primarySourceLinkRows;

  @override
  List<common_db.PrimarySourceAttribution> get primarySourceAttributionRows =>
      _databaseGateway.primarySourceAttributionRows;

  @override
  List<common_db.PrimarySourcePage> get primarySourcePageRows =>
      _databaseGateway.primarySourcePageRows;

  @override
  List<common_db.PrimarySourceWord> get primarySourceWordRows =>
      _databaseGateway.primarySourceWordRows;

  @override
  List<common_db.PrimarySourceVerse> get primarySourceVerseRows =>
      _databaseGateway.primarySourceVerseRows;

  @override
  List<localized_db.PrimarySourceText> get primarySourceTextRows =>
      _databaseGateway.primarySourceTextRows;

  @override
  List<localized_db.PrimarySourceLinkText> get primarySourceLinkTextRows =>
      _databaseGateway.primarySourceLinkTextRows;

  @override
  Future<Uint8List?> getCommonResourceData(String key) {
    return _databaseGateway.getCommonResourceData(key);
  }
}
