import 'dart:io';

import 'package:drift/drift.dart' hide isNull;
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/infra/db/runtime/gateways/articles_database_gateway.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  late PathProviderPlatform previousPathProvider;
  late Directory tempDir;

  setUpAll(() async {
    previousPathProvider = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp('articles_gateway_test_');
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
    'DbManagerArticlesDatabaseGateway returns safe fallbacks before initialization',
    () async {
      final gateway = DbManagerArticlesDatabaseGateway();

      expect(gateway.isInitialized, isFalse);
      expect(await gateway.getArticles(), isEmpty);
      expect(await gateway.getArticleMarkdown('route'), '');
      expect(await gateway.getArticleByRoute('route'), isNull);
      expect(await gateway.getCommonResource('key'), isNull);

      expect(await gateway.getArticleMarkdown(''), '');
      expect(await gateway.getArticleByRoute(''), isNull);
      expect(await gateway.getCommonResource(''), isNull);
    },
  );

  test(
    'DbManagerArticlesDatabaseGateway queries and sorts data as contract',
    () async {
      final gateway = DbManagerArticlesDatabaseGateway();
      final manager = DBManager();
      await gateway.initialize('en');
      await _clearDatabases(manager);

      await manager.localizedDB
          .into(manager.localizedDB.articles)
          .insert(
            ArticlesCompanion.insert(
              route: 'b_route',
              name: 'B',
              description: 'B desc',
              idIcon: 'b',
              sortOrder: Value(1),
              isVisible: Value(true),
              markdown: '# B',
            ),
          );
      await manager.localizedDB
          .into(manager.localizedDB.articles)
          .insert(
            ArticlesCompanion.insert(
              route: 'a_route',
              name: 'A',
              description: 'A desc',
              idIcon: 'a',
              sortOrder: Value(1),
              isVisible: Value(true),
              markdown: '# A',
            ),
          );
      await manager.localizedDB
          .into(manager.localizedDB.articles)
          .insert(
            ArticlesCompanion.insert(
              route: 'hidden',
              name: 'Hidden',
              description: 'Hidden desc',
              idIcon: 'h',
              sortOrder: Value(0),
              isVisible: Value(false),
              markdown: '# Hidden',
            ),
          );
      await manager.commonDB
          .into(manager.commonDB.commonResources)
          .insert(
            CommonResourcesCompanion.insert(
              key: 'res-key',
              fileName: 'res.txt',
              mimeType: 'text/plain',
              data: Uint8List.fromList(const [1, 2, 3]),
            ),
          );

      final onlyVisible = await gateway.getArticles();
      final all = await gateway.getArticles(onlyVisible: false);
      final markdown = await gateway.getArticleMarkdown('a_route');
      final missingMarkdown = await gateway.getArticleMarkdown('missing');
      final byRoute = await gateway.getArticleByRoute('b_route');
      final missingByRoute = await gateway.getArticleByRoute('missing');
      final resource = await gateway.getCommonResource('res-key');

      expect(onlyVisible.map((a) => a.route).toList(), ['a_route', 'b_route']);
      expect(all.map((a) => a.route).toList(), [
        'hidden',
        'a_route',
        'b_route',
      ]);
      expect(markdown, '# A');
      expect(missingMarkdown, '');
      expect(byRoute?.route, 'b_route');
      expect(missingByRoute, isNull);
      expect(resource?.fileName, 'res.txt');
    },
  );

  test(
    'DbManagerArticlesDatabaseGateway updateLanguage switches localized database',
    () async {
      final gateway = DbManagerArticlesDatabaseGateway();
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
      expect(await gateway.getArticles(), isEmpty);
    },
  );
}

Future<void> _clearDatabases(DBManager manager) async {
  await manager.commonDB.delete(manager.commonDB.commonResources).go();
  await manager.localizedDB.delete(manager.localizedDB.articles).go();
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}
