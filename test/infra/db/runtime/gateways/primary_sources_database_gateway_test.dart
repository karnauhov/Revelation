import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/infra/db/runtime/gateways/primary_sources_database_gateway.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  late PathProviderPlatform previousPathProvider;
  late Directory tempDir;

  setUpAll(() async {
    previousPathProvider = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp('primary_gateway_test_');
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
    'DbManagerPrimarySourcesDatabaseGateway returns empty state before initialization',
    () async {
      final gateway = DbManagerPrimarySourcesDatabaseGateway();

      expect(gateway.isInitialized, isFalse);
      expect(gateway.primarySourceRows, isEmpty);
      expect(gateway.primarySourceLinkRows, isEmpty);
      expect(gateway.primarySourceAttributionRows, isEmpty);
      expect(gateway.primarySourcePageRows, isEmpty);
      expect(gateway.primarySourceWordRows, isEmpty);
      expect(gateway.primarySourceVerseRows, isEmpty);
      expect(gateway.primarySourceTextRows, isEmpty);
      expect(gateway.primarySourceLinkTextRows, isEmpty);
      expect(await gateway.getCommonResourceData('preview'), isNull);
      expect(await gateway.getCommonResourceData(''), isNull);
    },
  );

  test(
    'DbManagerPrimarySourcesDatabaseGateway reloads all primary source slices',
    () async {
      final gateway = DbManagerPrimarySourcesDatabaseGateway();
      final manager = DBManager();
      await gateway.initialize('en');
      await _clearDatabases(manager);

      await manager.commonDB
          .into(manager.commonDB.primarySources)
          .insert(
            PrimarySourcesCompanion.insert(
              id: 's1',
              family: 'fam',
              number: 1,
              groupKind: 'group',
              previewResourceKey: 'preview',
            ),
          );
      await manager.commonDB
          .into(manager.commonDB.primarySourceLinks)
          .insert(
            PrimarySourceLinksCompanion.insert(
              sourceId: 's1',
              linkId: 'l1',
              linkRole: 'official',
              url: 'https://example.com',
            ),
          );
      await manager.commonDB
          .into(manager.commonDB.primarySourceAttributions)
          .insert(
            PrimarySourceAttributionsCompanion.insert(
              sourceId: 's1',
              attributionId: 'a1',
              displayText: 'Attribution',
              url: 'https://example.com/a',
            ),
          );
      await manager.commonDB
          .into(manager.commonDB.primarySourcePages)
          .insert(
            PrimarySourcePagesCompanion.insert(
              sourceId: 's1',
              pageName: 'p1',
              contentRef: 'content',
              imagePath: 'img/p1.png',
            ),
          );
      await manager.commonDB
          .into(manager.commonDB.primarySourceWords)
          .insert(
            PrimarySourceWordsCompanion.insert(
              sourceId: 's1',
              pageName: 'p1',
              wordIndex: 0,
              wordText: 'word',
            ),
          );
      await manager.commonDB
          .into(manager.commonDB.primarySourceVerses)
          .insert(
            PrimarySourceVersesCompanion.insert(
              sourceId: 's1',
              pageName: 'p1',
              verseIndex: 0,
              chapterNumber: 1,
              verseNumber: 1,
              labelX: 10.0,
              labelY: 20.0,
            ),
          );
      await manager.commonDB
          .into(manager.commonDB.commonResources)
          .insert(
            CommonResourcesCompanion.insert(
              key: 'preview',
              fileName: 'preview.bin',
              mimeType: 'application/octet-stream',
              data: Uint8List.fromList(const [7, 8, 9]),
            ),
          );
      await manager.localizedDB
          .into(manager.localizedDB.primarySourceTexts)
          .insert(
            PrimarySourceTextsCompanion.insert(
              sourceId: 's1',
              titleMarkup: 'Title',
              dateLabel: 'Date',
              contentLabel: 'Content',
              materialText: 'Material',
              textStyleText: 'Style',
              foundText: 'Found',
              classificationText: 'Class',
              currentLocationText: 'Location',
            ),
          );
      await manager.localizedDB
          .into(manager.localizedDB.primarySourceLinkTexts)
          .insert(
            PrimarySourceLinkTextsCompanion.insert(
              sourceId: 's1',
              linkId: 'l1',
              title: 'Link title',
            ),
          );

      await gateway.updateLanguage('en');

      expect(gateway.primarySourceRows.map((e) => e.id).toList(), ['s1']);
      expect(gateway.primarySourceLinkRows.map((e) => e.linkId).toList(), [
        'l1',
      ]);
      expect(
        gateway.primarySourceAttributionRows
            .map((e) => e.attributionId)
            .toList(),
        ['a1'],
      );
      expect(gateway.primarySourcePageRows.map((e) => e.pageName).toList(), [
        'p1',
      ]);
      expect(gateway.primarySourceWordRows.map((e) => e.wordText).toList(), [
        'word',
      ]);
      expect(
        gateway.primarySourceVerseRows.map((e) => e.verseNumber).toList(),
        [1],
      );
      expect(gateway.primarySourceTextRows.map((e) => e.sourceId).toList(), [
        's1',
      ]);
      expect(gateway.primarySourceLinkTextRows.map((e) => e.title).toList(), [
        'Link title',
      ]);
      expect(
        await gateway.getCommonResourceData('preview'),
        Uint8List.fromList(const [7, 8, 9]),
      );
      expect(
        () => gateway.primarySourceRows.add(
          const PrimarySource(
            id: 'x',
            family: 'f',
            number: 1,
            groupKind: 'g',
            sortOrder: 0,
            versesCount: 0,
            previewResourceKey: 'p',
            defaultMaxScale: 3,
            canShowImages: true,
            imagesAreMonochrome: false,
            notes: '',
          ),
        ),
        throwsUnsupportedError,
      );
    },
  );

  test(
    'DbManagerPrimarySourcesDatabaseGateway updateLanguage refreshes localized slices',
    () async {
      final gateway = DbManagerPrimarySourcesDatabaseGateway();
      final manager = DBManager();
      if (!gateway.isInitialized) {
        await gateway.initialize('en');
      }

      final previousLocalized = manager.localizedDB;
      await gateway.updateLanguage('es');

      expect(
        previousLocalized.customSelect('SELECT 1').get(),
        throwsA(anything),
      );
      expect(gateway.primarySourceRows, isNotEmpty);
      expect(gateway.primarySourceTextRows, isEmpty);
      expect(gateway.primarySourceLinkTextRows, isEmpty);

      await manager.localizedDB
          .into(manager.localizedDB.primarySourceTexts)
          .insert(
            PrimarySourceTextsCompanion.insert(
              sourceId: 's1',
              titleMarkup: 'Titulo',
              dateLabel: 'Fecha',
              contentLabel: 'Contenido',
              materialText: 'Material',
              textStyleText: 'Estilo',
              foundText: 'Encontrado',
              classificationText: 'Clasificacion',
              currentLocationText: 'Ubicacion',
            ),
          );
      await gateway.updateLanguage('es');
      expect(gateway.primarySourceTextRows.map((e) => e.titleMarkup).toList(), [
        'Titulo',
      ]);
    },
  );
}

Future<void> _clearDatabases(DBManager manager) async {
  await manager.commonDB.delete(manager.commonDB.primarySourceVerses).go();
  await manager.commonDB.delete(manager.commonDB.primarySourceWords).go();
  await manager.commonDB.delete(manager.commonDB.primarySourcePages).go();
  await manager.commonDB
      .delete(manager.commonDB.primarySourceAttributions)
      .go();
  await manager.commonDB.delete(manager.commonDB.primarySourceLinks).go();
  await manager.commonDB.delete(manager.commonDB.primarySources).go();
  await manager.commonDB.delete(manager.commonDB.commonResources).go();
  await manager.localizedDB
      .delete(manager.localizedDB.primarySourceLinkTexts)
      .go();
  await manager.localizedDB.delete(manager.localizedDB.primarySourceTexts).go();
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}
