import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

/// First-party text fixtures; persistence uses the real preferences adapter.
class FakeParallelBibleRepository extends BibleRepository {
  FakeParallelBibleRepository(this.map, {this.modules = fixtureModules});

  static const original = 'bible_lxx_tr.sqlite';
  static const english = 'bible_kjv.sqlite';
  static const ukrainian = 'bible_ohienko_1988.sqlite';
  static const fixtureModules = [
    BibleModuleInfo(
      fileName: original,
      code: 'LXX_TR',
      moduleId: 'lxx_tr',
      title: 'Synthetic Greek',
      hasStrongNumbers: true,
      description: '',
      language: 'grc',
      canon: '',
      versification: '',
      license: '',
      sourceSummary: '',
    ),
    BibleModuleInfo(
      fileName: english,
      code: 'KJV',
      moduleId: 'kjv',
      title: 'Synthetic English',
      hasStrongNumbers: true,
      description: '',
      language: 'en',
      canon: '',
      versification: '',
      license: '',
      sourceSummary: '',
    ),
    BibleModuleInfo(
      fileName: ukrainian,
      code: 'OH1988',
      moduleId: 'oh1988',
      title: 'Synthetic Ukrainian',
      description: '',
      language: 'uk',
      canon: '',
      versification: '',
      license: '',
      sourceSummary: '',
    ),
  ];

  final BibleVerseMap map;
  final List<BibleModuleInfo> modules;
  Future<void>? preferencesGate;
  Future<void>? initialGate;
  Future<void>? translationGate;
  final chapterGates = <String, Future<void>>{};
  final initialFiles = <String?>[];
  final savedModuleLists = <List<String>>[];
  final unreadableFiles = <String>{};
  Future<void> Function(List<String>)? beforeSave;
  int singleModuleSaves = 0;
  int translationQueries = 0;
  bool failInitialLoad = false;

  @override
  Future<List<String>> loadLastModuleFiles() async {
    await preferencesGate;
    return super.loadLastModuleFiles();
  }

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {
    singleModuleSaves++;
    await super.saveLastModuleFile(moduleFile);
  }

  @override
  Future<void> saveLastModuleFiles(List<String> moduleFiles) async {
    savedModuleLists.add(List.of(moduleFiles));
    await beforeSave?.call(moduleFiles);
    await super.saveLastModuleFiles(moduleFiles);
  }

  @override
  Future<String?> findTranslationModuleFile({
    required String languageCode,
    required List<BibleModuleInfo> modules,
    required String primaryModuleFile,
  }) async {
    translationQueries++;
    await translationGate;
    return super.findTranslationModuleFile(
      languageCode: languageCode,
      modules: modules,
      primaryModuleFile: primaryModuleFile,
    );
  }

  @override
  Future<BibleModuleInfo> loadModuleInfo(String moduleFile) async {
    if (unreadableFiles.contains(moduleFile))
      throw StateError('Fixture unavailable');
    return modules.firstWhere((m) => m.fileName == moduleFile);
  }

  @override
  Future<BibleInitialData> loadInitial({
    required String languageCode,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) async {
    initialFiles.add(initialModuleFile);
    await initialGate;
    if (failInitialLoad) throw const BibleModulesUnavailableException();
    final module =
        modules.where((m) => m.fileName == initialModuleFile).firstOrNull ??
        modules.first;
    final chapter = await loadChapter(
      moduleFile: module.fileName,
      bookId: initialBookId,
      chapter: initialChapter,
      verse: initialVerse,
    );
    return BibleInitialData(
      verseMap: map,
      modules: modules,
      selectedModule: module,
      reference: chapter.reference,
      verses: chapter.verses,
    );
  }

  @override
  Future<BibleChapterData> loadChapter({
    required String moduleFile,
    required int bookId,
    required int chapter,
    required int verse,
  }) async {
    await chapterGates[moduleFile];
    final reference = map.normalizedReference(
      bookId: bookId,
      chapter: chapter,
      verse: verse,
    );
    final module = modules.firstWhere((m) => m.fileName == moduleFile);
    return BibleChapterData(
      reference: reference,
      verses: [
        for (
          var i = 1;
          i <=
              map.verseCount(
                bookId: reference.bookId,
                chapter: reference.chapter,
              );
          i++
        )
          BibleChapterVerse(
            reference: map.referenceFor(
              bookId: reference.bookId,
              chapter: reference.chapter,
              verse: i,
            ),
            text: '${module.code} sample $i',
          ),
      ],
    );
  }
}
