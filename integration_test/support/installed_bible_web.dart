import 'package:drift/drift.dart';
import 'package:revelation/infra/db/connectors/web.dart';
import 'package:get_it/get_it.dart';
import 'package:talker_flutter/talker_flutter.dart';

QueryExecutor openInstalledModule(String fileName) {
  if (!GetIt.I.isRegistered<Talker>()) {
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  }
  return connectOnWeb(fileName);
}
