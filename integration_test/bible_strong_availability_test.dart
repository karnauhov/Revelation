import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../test/test_harness/bible_strong_availability_scenario.dart';
import 'support/installed_bible_stub.dart'
    if (dart.library.io) 'support/installed_bible_native.dart'
    if (dart.library.js_interop) 'support/installed_bible_web.dart'
    as platform;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  for (final width in [375.0, 1700.0]) {
    testWidgets('installed module Strong availability at width $width', (
      tester,
    ) async {
      SharedPreferences.setMockInitialValues({});
      await exerciseBibleStrongAvailability(
        tester,
        _InstalledRepository(),
        width,
      );
    });
  }
}

class _InstalledRepository extends BibleRepository {
  _InstalledRepository() : super(moduleDataSource: _InstalledModules());

  @override
  Future<List<String>> loadLastModuleFiles() async => ['bible_lxx_tr.sqlite'];
}

class _InstalledModules implements BibleModuleDataSource {
  @override
  Future<List<String>> listModuleFiles({
    required String defaultModuleFile,
  }) async => [
    'bible_lxx_tr.sqlite',
    'bible_kjv.sqlite',
    'bible_ohienko_1988.sqlite',
  ];

  @override
  BibleModuleDB openModule(String file) =>
      BibleModuleDB(platform.openInstalledModule(file));
}
