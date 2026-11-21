import 'package:drift/drift.dart';
import 'package:revelation/infra/db/connectors/web.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/shared/config/app_constants.dart';

Future<List<String>> listInstalledBibleModuleFiles({
  Set<String> exclude = const {},
}) async => (await installedBibleFilesOnWeb())
    .where((file) => !exclude.contains(file))
    .toList();
QueryExecutor? openInstalledBibleModuleExecutor(String dbFile) =>
    _isBibleModuleDatabaseFileName(dbFile)
    ? openInstalledBibleFileOnWeb(dbFile)
    : null;

Future<List<String>> listLocalBibleModuleFiles({
  String defaultModuleFile = AppConstants.defaultBibleModuleDB,
}) async {
  final files = {
    ...(await readBibleModuleManifest()).keys.where(
      _isBibleModuleDatabaseFileName,
    ),
    ...await listInstalledBibleModuleFiles(),
  };

  if (_isBibleModuleDatabaseFileName(defaultModuleFile)) {
    files.add(defaultModuleFile);
  }

  final sortedFiles = files.toList()..sort();
  if (sortedFiles.remove(defaultModuleFile)) {
    sortedFiles.insert(0, defaultModuleFile);
  }
  return List<String>.unmodifiable(sortedFiles);
}

Future<Map<String, WebDbManifestEntry>> readBibleModuleManifest() =>
    refreshWebDbManifestEntries();

QueryExecutor openBibleModuleExecutor(String dbFile) {
  if (!_isBibleModuleDatabaseFileName(dbFile)) {
    throw ArgumentError.value(dbFile, 'dbFile', 'Invalid Bible module file');
  }
  return connectOnWeb(dbFile);
}

bool _isBibleModuleDatabaseFileName(String fileName) {
  return RegExp(
    r'^bible_[A-Za-z0-9_]+\.sqlite$',
    caseSensitive: false,
  ).hasMatch(fileName);
}
