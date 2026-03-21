import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  late PathProviderPlatform previousPathProvider;
  late Directory tempDir;

  setUpAll(() async {
    previousPathProvider = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp('db_manager_test_');
    PathProviderPlatform.instance = _FakePathProviderPlatform(tempDir.path);

    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDownAll(() async {
    final manager = DBManager();
    if (manager.isInitialized) {
      await manager.localizedDB.close();
      await manager.commonDB.close();
    }

    await GetIt.I.reset();
    PathProviderPlatform.instance = previousPathProvider;
    await tempDir.delete(recursive: true);
  });

  test('DBManager factory returns singleton instance', () {
    expect(identical(DBManager(), DBManager()), isTrue);
  });

  test('DBManager init and updateLanguage preserve runtime contract', () async {
    final manager = DBManager();

    expect(manager.isInitialized, isFalse);
    await manager.updateLanguage('uk');
    expect(manager.isInitialized, isTrue);
    expect(manager.langDB, 'uk');

    final firstLocalized = manager.localizedDB;
    await manager.init('uk');
    expect(identical(manager.localizedDB, firstLocalized), isTrue);

    await manager.updateLanguage('   ');
    expect(manager.langDB, 'uk');
    expect(identical(manager.localizedDB, firstLocalized), isTrue);

    await manager.init('   ');
    expect(manager.langDB, 'en');
    expect(identical(manager.localizedDB, firstLocalized), isFalse);

    final secondLocalized = manager.localizedDB;
    await manager.updateLanguage('es');
    expect(manager.langDB, 'es');
    expect(identical(manager.localizedDB, secondLocalized), isFalse);
  });
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}
