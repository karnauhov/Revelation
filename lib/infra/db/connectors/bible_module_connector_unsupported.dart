import 'package:drift/drift.dart';
import 'package:revelation/shared/config/app_constants.dart';

Future<List<String>> listLocalBibleModuleFiles({
  String defaultModuleFile = AppConstants.defaultBibleModuleDB,
}) async {
  return const <String>[];
}

QueryExecutor openBibleModuleExecutor(String dbFile) {
  throw UnsupportedError('Bible modules are not supported on this platform.');
}
