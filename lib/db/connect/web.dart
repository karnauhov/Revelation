import 'package:http/http.dart' as http;
import 'package:drift/drift.dart';
import 'package:drift/wasm.dart';
import 'package:revelation/db/db_common.dart';
import 'package:revelation/db/db_localized.dart';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/utils/common.dart';

CommonDB getCommonDB() {
  return CommonDB(connectOnWeb(AppConstants.commonDB));
}

LocalizedDB getLocalizedDB(String loc) {
  final dbFile = AppConstants.localizedDB.replaceAll('@loc', loc);
  return LocalizedDB(connectOnWeb(dbFile));
}

DatabaseConnection connectOnWeb(String dbFile) {
  return DatabaseConnection.delayed(
    Future(() async {
      final result = await WasmDatabase.open(
        databaseName: dbFile.replaceAll(".sqlite", ""),
        sqlite3Uri: Uri.parse('sqlite3.wasm'),
        driftWorkerUri: Uri.parse('drift_worker.js'),
        initializeDatabase: () async {
          final response = await http.get(Uri.parse('/db/$dbFile'));
          if (response.statusCode == 200) {
            return response.bodyBytes;
          } else {
            log.e('Failed to load database file: $dbFile');
            return null;
          }
        },
      );

      if (result.missingFeatures.isNotEmpty) {
        log.i(
          "Using ${result.chosenImplementation} due to missing browser features: ${result.missingFeatures}",
        );
      }

      return result.resolvedExecutor;
    }),
  );
}
