import 'package:drift/drift.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';

Future<List<String>> listInstalledBibleModuleFiles({
  Set<String> exclude = const {},
}) async => const [];
QueryExecutor? openInstalledBibleModuleExecutor(String dbFile) => null;

Future<Map<String, WebDbManifestEntry>> readBibleModuleManifest() async =>
    const {};

Future<List<String>> listLocalBibleModuleFiles({
  String defaultModuleFile = AppConstants.defaultBibleModuleDB,
}) async {
  return const <String>[];
}

QueryExecutor openBibleModuleExecutor(String dbFile) {
  throw UnsupportedError('Bible modules are not supported on this platform.');
}
