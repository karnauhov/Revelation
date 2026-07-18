import 'package:drift/drift.dart';
import 'package:http/http.dart' as http;
import 'package:revelation/infra/db/connectors/web.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/infra/db/connectors/web_db_uri.dart';
import 'package:revelation/shared/config/app_constants.dart';

Future<List<String>> listLocalBibleModuleFiles({
  String defaultModuleFile = AppConstants.defaultBibleModuleDB,
}) async {
  final files = <String>{};
  try {
    final response = await http.get(buildWebDbManifestUri(forceNoCache: true));
    if (response.statusCode == 200) {
      files.addAll(
        parseWebDbManifestEntries(
          response.body,
        ).keys.where(_isBibleModuleDatabaseFileName),
      );
    }
  } catch (_) {}

  if (_isBibleModuleDatabaseFileName(defaultModuleFile)) {
    files.add(defaultModuleFile);
  }

  final sortedFiles = files.toList()..sort();
  if (sortedFiles.remove(defaultModuleFile)) {
    sortedFiles.insert(0, defaultModuleFile);
  }
  return List<String>.unmodifiable(sortedFiles);
}

QueryExecutor openBibleModuleExecutor(String dbFile) {
  return connectOnWeb(dbFile);
}

bool _isBibleModuleDatabaseFileName(String fileName) {
  return RegExp(
    r'^bible_[A-Za-z0-9_]+\.sqlite$',
    caseSensitive: false,
  ).hasMatch(fileName);
}
