import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../test_harness/fakes/fake_bible_module_data_source.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late AppSettings settings;
  late FakeBibleModuleDataSource source;
  late Map<String, WebDbManifestEntry> manifest;
  var calls = 0;

  BibleModuleInfo info(String file, String language) => BibleModuleInfo(
    fileName: file,
    code: language.toUpperCase(),
    moduleId: language,
    title: language,
    language: language,
    description: '',
    canon: 'protestant_66',
    versification: 'kjv_protestant',
    license: '',
    sourceSummary: '',
  );
  AppSettings preferences(String language, {String module = 'auto'}) =>
      AppSettings(
        selectedLanguage: language,
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
        defaultBibleModule: module,
      );
  WebDbManifestEntry entry(String language, {int schema = 4}) =>
      WebDbManifestEntry(
        versionToken: 'fixture-$language',
        versionInfo: DatabaseVersionInfo(
          schemaVersion: schema,
          dataVersion: 1,
          date: DateTime.utc(2026, 1, 1),
        ),
        bible: {
          'moduleId': language,
          'title': language,
          'code': language.toUpperCase(),
          'language': language,
        },
      );
  BibleLibraryRepository library({
    Future<Map<String, WebDbManifestEntry>> Function()? loader,
  }) => BibleLibraryRepository(
    dataSource: source,
    loadSettings: () async => settings,
    readInstalled: () async => [],
    loadManifest:
        loader ??
        () async {
          calls++;
          return manifest;
        },
  );

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    calls = 0;
    settings = preferences('en');
    source = FakeBibleModuleDataSource({
      'bible_kjv.sqlite': (
        info: info('bible_kjv.sqlite', 'en'),
        verses: [const BibleVerseText(verseKey: '001', text: 'English G10')],
      ),
      'bible_ohienko_1988.sqlite': (
        info: info('bible_ohienko_1988.sqlite', 'uk'),
        verses: [const BibleVerseText(verseKey: '001', text: 'Українська')],
      ),
    });
    manifest = {
      'bible_kjv.sqlite': entry('en'),
      'bible_ohienko_1988.sqlite': entry('uk'),
    };
  });

  test(
    'a cached passage opens in the same reader module when the manifest is offline',
    () async {
      const ukrainian = 'bible_ohienko_1988.sqlite';
      settings = preferences('en', module: ukrainian);
      await library().loadCatalog();
      final offline = library(loader: () async => throw StateError('Offline'));
      source.discoverableFiles = ['bible_lxx_tr.sqlite'];
      final preview = await offline.loadPreview(['001']);
      final reader = BibleRepository(
        moduleDataSource: source,
        loadModuleCatalog: offline.availableCatalog,
      );
      final passage = await reader.loadInitial(
        languageCode: 'en',
        initialBookId: 1,
        initialModuleFile: preview.module.fileName,
      );
      expect(preview.module.fileName, ukrainian);
      expect(passage.selectedModule.fileName, ukrainian);
      expect(passage.verses.first.text, preview.verses.single.text);
      expect(source.closed, source.opened);
    },
  );

  test(
    'reader retry discovers modules after a first offline start with no cache',
    () async {
      var online = false;
      final repository = library(
        loader: () async {
          if (!online) throw StateError('Offline');
          return manifest;
        },
      );
      final reader = BibleRepository(
        moduleDataSource: source,
        loadModuleCatalog: repository.availableCatalog,
      );
      await expectLater(
        reader.loadInitial(languageCode: 'en'),
        throwsA(isA<BibleModulesUnavailableException>()),
      );
      online = true;
      expect(
        (await reader.loadInitial(
          languageCode: 'en',
          initialModuleFile: 'bible_kjv.sqlite',
        )).selectedModule.fileName,
        'bible_kjv.sqlite',
      );
    },
  );

  test(
    'auto follows UI language and English fallback; manual choice survives language changes',
    () async {
      final repository = library();
      for (final language in ['en', 'es', 'ru']) {
        settings = preferences(language);
        expect(await repository.preferredModuleFile(), 'bible_kjv.sqlite');
      }
      settings = preferences('uk');
      expect(
        await repository.preferredModuleFile(),
        'bible_ohienko_1988.sqlite',
      );
      settings = preferences('ru', module: 'bible_ohienko_1988.sqlite');
      expect(
        await repository.preferredModuleFile(),
        'bible_ohienko_1988.sqlite',
      );
      expect(source.opened, isEmpty);
    },
  );

  test(
    'refresh discovers a new compatible translation without downloading a database',
    () async {
      settings = preferences('es');
      final repository = library();
      expect(await repository.preferredModuleFile(), 'bible_kjv.sqlite');
      manifest['bible_es_new.sqlite'] = entry('es');
      manifest['bible_incompatible.sqlite'] = entry('es', schema: 999);
      manifest['../bible_escape.sqlite'] = entry('es');
      final catalog = await repository.loadCatalog(refresh: true);
      expect(
        catalog.map((module) => module.fileName),
        contains('bible_es_new.sqlite'),
      );
      expect(
        catalog.map((module) => module.fileName),
        isNot(contains('bible_incompatible.sqlite')),
      );
      expect(await repository.preferredModuleFile(), 'bible_es_new.sqlite');
      expect(source.opened, isEmpty);
    },
  );

  test(
    'concurrent requests coalesce and a cached catalog survives offline restart',
    () async {
      final pending = Completer<Map<String, WebDbManifestEntry>>();
      final repository = library(
        loader: () {
          calls++;
          return pending.future;
        },
      );
      final first = repository.loadCatalog(refresh: true);
      final second = repository.loadCatalog(refresh: true);
      await Future<void>.delayed(Duration.zero);
      pending.complete(manifest);
      await Future.wait([first, second]);
      expect(calls, 1);
      final offline = library(loader: () async => throw StateError('Offline'));
      expect((await offline.cachedCatalog()).length, 2);
      expect(await offline.preferredModuleFile(), 'bible_kjv.sqlite');
      await expectLater(offline.loadCatalog(refresh: true), throwsStateError);
    },
  );

  test(
    'unavailable preferred file falls back without overwriting its preference and closes every handle',
    () async {
      settings = preferences('uk', module: 'bible_ohienko_1988.sqlite');
      source.unavailable.add('bible_ohienko_1988.sqlite');
      final repository = library();
      final preview = await repository.loadPreview(['001']);
      expect(preview.module.fileName, 'bible_kjv.sqlite');
      expect(settings.defaultBibleModule, 'bible_ohienko_1988.sqlite');
      expect(source.closed, source.opened);
    },
  );

  test(
    'regional locales and a failed local listing still use the matching server translation',
    () async {
      final repository = BibleLibraryRepository(
        dataSource: source,
        loadSettings: () async => preferences('ES_mx'),
        loadManifest: () async => {
          'bible_es_new.sqlite': entry('es-ES'),
          'bible_kjv.sqlite': entry('en-US'),
          'bible_unknown.sqlite': entry(''),
        },
        readInstalled: () async => throw StateError('Unavailable storage'),
      );
      expect(await repository.preferredModuleFile(), 'bible_es_new.sqlite');
      expect(repository.cachedModules, hasLength(2));
      expect(source.opened, isEmpty);
    },
  );
}
