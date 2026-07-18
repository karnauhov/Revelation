import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/features/bible/data/repositories/bible_preferences_store.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  driftRuntimeOptions.dontWarnAboutMultipleDatabases = true;

  test('loads initial data and resolves selected module sources', () async {
    final source = _FakeBibleModuleDataSource(
      moduleFiles: const ['bible_alt.sqlite', 'bible_other.sqlite'],
      dataByFile: <String, _FakeBibleModuleData>{
        'bible_alt.sqlite': _FakeBibleModuleData(
          info: _moduleInfo('ALT'),
          verses: const [BibleVerseText(verseKey: '001', text: 'Alt verse')],
        ),
        'bible_other.sqlite': _FakeBibleModuleData(
          info: _moduleInfo('OTHER'),
          verses: const [],
        ),
      },
    );
    final preferences = _RecordingBiblePreferencesStore(
      lastModuleFile: 'bible_alt.sqlite',
    );
    final repository = BibleRepository(
      moduleDataSource: source,
      preferencesStore: preferences,
      loadVerseMap: BibleVerseMap.loadFromAssets,
    );

    final initial = await repository.loadInitial(
      languageCode: 'en',
      initialBookId: 0,
      initialChapter: 999,
      initialVerse: 999,
    );

    expect(initial.selectedModule.code, 'ALT');
    expect(initial.modules, hasLength(2));
    expect(initial.modules.last.code, 'OTHER');
    expect(initial.reference.bookId, 1);
    expect(initial.reference.chapter, greaterThan(1));
    expect(initial.verses, isNotEmpty);
    expect(initial.verses.first.text, 'Alt verse');

    final explicit = await repository.loadInitial(
      languageCode: 'en',
      initialModuleFile: 'bible_other.sqlite',
    );
    expect(explicit.selectedModule.code, 'OTHER');
    expect(
      source.openedModuleFiles,
      containsAll(<String>['bible_alt.sqlite', 'bible_other.sqlite']),
    );
  });

  test('falls back to the first module and reports missing modules', () async {
    final source = _FakeBibleModuleDataSource(
      moduleFiles: const ['bible_alt.sqlite'],
      dataByFile: <String, _FakeBibleModuleData>{
        'bible_alt.sqlite': _FakeBibleModuleData(
          info: _moduleInfo('ALT'),
          verses: const [],
        ),
      },
    );
    final repository = BibleRepository(
      moduleDataSource: source,
      preferencesStore: _RecordingBiblePreferencesStore(),
      loadVerseMap: BibleVerseMap.loadFromAssets,
    );

    final initial = await repository.loadInitial(languageCode: 'en');
    expect(initial.selectedModule.code, 'ALT');

    final unavailable = BibleRepository(
      moduleDataSource: _FakeBibleModuleDataSource.empty(),
      preferencesStore: _RecordingBiblePreferencesStore(),
      loadVerseMap: BibleVerseMap.loadFromAssets,
    );
    await expectLater(
      unavailable.loadInitial(languageCode: 'en'),
      throwsA(isA<BibleModulesUnavailableException>()),
    );
  });

  test(
    'loads chapter text with empty fallbacks and delegates preferences',
    () async {
      final preferences = _RecordingBiblePreferencesStore(
        lastSearchHistory: const ['logos'],
      );
      final repository = BibleRepository(
        moduleDataSource: _FakeBibleModuleDataSource(
          moduleFiles: const ['bible_alt.sqlite'],
          dataByFile: <String, _FakeBibleModuleData>{
            'bible_alt.sqlite': _FakeBibleModuleData(
              info: _moduleInfo('ALT'),
              verses: const [
                BibleVerseText(verseKey: '001', text: 'First verse'),
              ],
            ),
          },
        ),
        preferencesStore: preferences,
        loadVerseMap: BibleVerseMap.loadFromAssets,
      );

      final chapter = await repository.loadChapter(
        moduleFile: 'bible_alt.sqlite',
        bookId: 1,
        chapter: 1,
        verse: 1,
      );
      expect(chapter.verses.first.text, 'First verse');
      expect(chapter.verses[1].text, isEmpty);

      await repository.saveLastModuleFile('bible_alt.sqlite');
      expect(preferences.savedLastModuleFile, 'bible_alt.sqlite');
      expect(await repository.loadLastModuleFiles(), ['bible_alt.sqlite']);
      await repository.saveLastModuleFiles([
        'bible_alt.sqlite',
        'bible_other.sqlite',
      ]);
      expect(preferences.savedLastModuleFiles, [
        'bible_alt.sqlite',
        'bible_other.sqlite',
      ]);

      await repository.saveLastSearchQuery(
        moduleFile: 'bible_alt.sqlite',
        query: '  logos   words ',
      );
      expect(preferences.savedSearchQueries['bible_alt.sqlite'], 'logos words');
      expect(
        await repository.loadLastSearchQuery('bible_alt.sqlite'),
        'logos words',
      );
      expect(await repository.loadSearchHistory(), ['logos']);
    },
  );

  test(
    'handles empty searches and maintains normalized search history',
    () async {
      final preferences = _RecordingBiblePreferencesStore(
        lastSearchHistory: const ['logos', 'grace'],
      );
      final repository = BibleRepository(
        moduleDataSource: _FakeBibleModuleDataSource(
          moduleFiles: const ['bible_alt.sqlite'],
          dataByFile: <String, _FakeBibleModuleData>{
            'bible_alt.sqlite': _FakeBibleModuleData(
              info: _moduleInfo('ALT'),
              verses: const [],
            ),
          },
        ),
        preferencesStore: preferences,
        loadVerseMap: BibleVerseMap.loadFromAssets,
      );

      expect(
        await repository.searchModule(
          moduleFile: 'bible_alt.sqlite',
          query: '   ',
        ),
        isEmpty,
      );
      await repository.rememberSearchQuery('  LOGOS  ');
      expect(preferences.savedSearchHistory, ['LOGOS', 'grace']);
      await repository.rememberSearchQuery('   ');
      expect(preferences.savedSearchHistory, ['LOGOS', 'grace']);
    },
  );

  test('searches visible verse text without Strong tokens', () async {
    final db = BibleModuleDB(NativeDatabase.memory());
    await db.customStatement('''
      CREATE TABLE verses (
        verse_key TEXT NOT NULL PRIMARY KEY,
        text TEXT NOT NULL DEFAULT ''
      )
    ''');
    await db.customInsert('''
      INSERT INTO verses (verse_key, text)
      VALUES
        ('001', 'En G1722 arche G746'),
        ('002', 'No matching phrase G1'),
        ('003', 'En arche again G2')
    ''');

    final repository = BibleRepository(
      moduleDataSource: _SingleDbBibleModuleDataSource(db),
      preferencesStore: _FakeBiblePreferencesStore(),
      loadVerseMap: BibleVerseMap.loadFromAssets,
    );

    final results = await repository.searchModule(
      moduleFile: 'bible_lxx_tr.sqlite',
      query: 'en arche',
    );

    expect(results, hasLength(2));
    expect(results.first.reference.bookId, 1);
    expect(results.first.reference.chapter, 1);
    expect(results.first.reference.verse, 1);
    expect(results.first.text, 'En arche');
    expect(results.first.matchCount, 1);
  });
}

BibleModuleInfo _moduleInfo(String code) {
  return BibleModuleInfo(
    fileName: 'bible_${code.toLowerCase()}.sqlite',
    code: code,
    moduleId: code.toLowerCase(),
    title: '$code Bible',
    description: '$code description',
    language: 'en',
    canon: 'protestant_66',
    versification: 'kjv',
    license: 'CC BY 4.0',
    sourceSummary: 'Source',
  );
}

class _FakeBibleModuleData {
  const _FakeBibleModuleData({required this.info, required this.verses});

  final BibleModuleInfo info;
  final List<BibleVerseText> verses;
}

class _FakeBibleModuleDataSource implements BibleModuleDataSource {
  _FakeBibleModuleDataSource({
    required this.moduleFiles,
    required this.dataByFile,
  });

  factory _FakeBibleModuleDataSource.empty() {
    return _FakeBibleModuleDataSource(
      moduleFiles: const <String>[],
      dataByFile: const <String, _FakeBibleModuleData>{},
    );
  }

  final List<String> moduleFiles;
  final Map<String, _FakeBibleModuleData> dataByFile;
  final List<String> openedModuleFiles = <String>[];

  @override
  Future<List<String>> listModuleFiles({required String defaultModuleFile}) {
    return Future.value(moduleFiles);
  }

  @override
  BibleModuleDB openModule(String moduleFile) {
    openedModuleFiles.add(moduleFile);
    final data = dataByFile[moduleFile];
    if (data == null) {
      throw StateError('No fake data for $moduleFile');
    }
    return _FakeBibleModuleDB(data: data);
  }
}

class _FakeBibleModuleDB extends BibleModuleDB {
  _FakeBibleModuleDB({required this.data}) : super(NativeDatabase.memory());

  final _FakeBibleModuleData data;

  @override
  Future<BibleModuleInfo> readInfo(String fileName) async {
    return BibleModuleInfo(
      fileName: fileName,
      code: data.info.code,
      moduleId: data.info.moduleId,
      title: data.info.title,
      description: data.info.description,
      language: data.info.language,
      canon: data.info.canon,
      versification: data.info.versification,
      license: data.info.license,
      sourceSummary: data.info.sourceSummary,
    );
  }

  @override
  Future<List<BibleVerseText>> readVersesByKeys(List<String> verseKeys) async {
    if (data.verses.length == 1 && verseKeys.isNotEmpty) {
      return [
        BibleVerseText(verseKey: verseKeys.first, text: data.verses.first.text),
      ];
    }
    return data.verses
        .where((verse) => verseKeys.contains(verse.verseKey))
        .toList(growable: false);
  }

  @override
  Future<List<BibleVerseText>> readAllVerses() async => data.verses;

  @override
  Future<void> close() async {}
}

class _RecordingBiblePreferencesStore implements BiblePreferencesStore {
  _RecordingBiblePreferencesStore({
    this.lastModuleFile,
    List<String> lastSearchHistory = const <String>[],
  }) : savedSearchHistory = List<String>.of(lastSearchHistory);

  String? lastModuleFile;
  String? savedLastModuleFile;
  List<String> savedLastModuleFiles = const <String>[];
  List<String> savedSearchHistory;
  final Map<String, String> savedSearchQueries = <String, String>{};

  @override
  Future<String?> loadLastModuleFile() async => lastModuleFile;

  @override
  Future<List<String>> loadLastModuleFiles() async =>
      savedLastModuleFiles.isEmpty
      ? (lastModuleFile == null ? const <String>[] : [lastModuleFile!])
      : savedLastModuleFiles;

  @override
  Future<String?> loadLastSearchQuery(String moduleFile) async =>
      savedSearchQueries[moduleFile];

  @override
  Future<List<String>> loadSearchHistory() async => savedSearchHistory;

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {
    savedLastModuleFile = moduleFile;
    lastModuleFile = moduleFile;
  }

  @override
  Future<void> saveLastModuleFiles(List<String> moduleFiles) async {
    savedLastModuleFiles = List<String>.of(moduleFiles);
  }

  @override
  Future<void> saveLastSearchQuery({
    required String moduleFile,
    required String query,
  }) async {
    savedSearchQueries[moduleFile] = query;
  }

  @override
  Future<void> saveSearchHistory(List<String> queries) async {
    savedSearchHistory = List<String>.of(queries);
  }
}

class _SingleDbBibleModuleDataSource implements BibleModuleDataSource {
  const _SingleDbBibleModuleDataSource(this.db);

  final BibleModuleDB db;

  @override
  Future<List<String>> listModuleFiles({required String defaultModuleFile}) {
    return Future.value([defaultModuleFile]);
  }

  @override
  BibleModuleDB openModule(String moduleFile) => db;
}

class _FakeBiblePreferencesStore implements BiblePreferencesStore {
  @override
  Future<String?> loadLastModuleFile() async => null;

  @override
  Future<List<String>> loadLastModuleFiles() async => const <String>[];

  @override
  Future<String?> loadLastSearchQuery(String moduleFile) async => null;

  @override
  Future<List<String>> loadSearchHistory() async => const <String>[];

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {}

  @override
  Future<void> saveLastModuleFiles(List<String> moduleFiles) async {}

  @override
  Future<void> saveLastSearchQuery({
    required String moduleFile,
    required String query,
  }) async {}

  @override
  Future<void> saveSearchHistory(List<String> queries) async {}
}
