import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  late PathProviderPlatform previousPathProvider;
  late Directory tempDir;

  setUpAll(() async {
    previousPathProvider = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp('lexicon_gateway_test_');
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

  test(
    'DbManagerLexiconDatabaseGateway has empty data before initialization',
    () {
      final gateway = DbManagerLexiconDatabaseGateway();

      expect(gateway.isInitialized, isFalse);
      expect(gateway.greekWords, isEmpty);
      expect(gateway.greekDescs, isEmpty);
    },
  );

  test(
    'DbManagerLexiconDatabaseGateway reloads lexicon and exposes immutable lists',
    () async {
      final gateway = DbManagerLexiconDatabaseGateway();
      final manager = DBManager();
      await gateway.initialize('en');
      await _clearDatabases(manager);

      await manager.commonDB
          .into(manager.commonDB.greekWords)
          .insert(
            GreekWordsCompanion.insert(
              word: 'Logos',
              category: 'noun',
              synonyms: 'Word',
              origin: 'Greek',
              usage: 'John 1:1',
            ),
          );
      await manager.localizedDB
          .into(manager.localizedDB.greekDescs)
          .insert(GreekDescsCompanion.insert(desc: 'Meaning of Logos'));

      await gateway.updateLanguage('en');

      expect(gateway.languageCode, 'en');
      expect(gateway.greekWords, hasLength(1));
      expect(gateway.greekWords.single.word, 'Logos');
      expect(gateway.greekDescs, hasLength(1));
      expect(gateway.greekDescs.single.desc, 'Meaning of Logos');
      expect(
        () => gateway.greekWords.add(
          const GreekWord(
            id: 99,
            word: 'Test',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
        ),
        throwsUnsupportedError,
      );
      expect(
        () => gateway.greekDescs.add(const GreekDesc(id: 99, desc: 'Test')),
        throwsUnsupportedError,
      );
    },
  );

  test(
    'DbManagerLexiconDatabaseGateway updateLanguage reloads localized descriptions',
    () async {
      final gateway = DbManagerLexiconDatabaseGateway();
      final manager = DBManager();
      if (!gateway.isInitialized) {
        await gateway.initialize('en');
      }

      final previousLocalized = manager.localizedDB;
      await gateway.updateLanguage('es');

      expect(gateway.languageCode, 'es');
      expect(
        previousLocalized.customSelect('SELECT 1').get(),
        throwsA(anything),
      );
      expect(gateway.greekWords, isNotEmpty);
      expect(gateway.greekDescs, isEmpty);

      await manager.localizedDB
          .into(manager.localizedDB.greekDescs)
          .insert(GreekDescsCompanion.insert(desc: 'Descripcion'));
      await gateway.updateLanguage('es');
      expect(gateway.greekDescs.map((d) => d.desc).toList(), ['Descripcion']);
    },
  );
}

Future<void> _clearDatabases(DBManager manager) async {
  await manager.commonDB.delete(manager.commonDB.greekWords).go();
  await manager.localizedDB.delete(manager.localizedDB.greekDescs).go();
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}
