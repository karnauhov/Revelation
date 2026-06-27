import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/features/bible/data/repositories/bible_preferences_store.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

class BibleInitialData {
  const BibleInitialData({
    required this.verseMap,
    required this.modules,
    required this.selectedModule,
    required this.reference,
    required this.verses,
  });

  final BibleVerseMap verseMap;
  final List<BibleModuleInfo> modules;
  final BibleModuleInfo selectedModule;
  final BibleVerseReference reference;
  final List<BibleChapterVerse> verses;
}

class BibleChapterData {
  const BibleChapterData({required this.reference, required this.verses});

  final BibleVerseReference reference;
  final List<BibleChapterVerse> verses;
}

class BibleRepository {
  BibleRepository({
    BibleModuleDataSource moduleDataSource = const LocalBibleModuleDataSource(),
    BiblePreferencesStore preferencesStore =
        const SharedPreferencesBiblePreferencesStore(),
    Future<BibleVerseMap> Function()? loadVerseMap,
  }) : _moduleDataSource = moduleDataSource,
       _preferencesStore = preferencesStore,
       _loadVerseMap = loadVerseMap ?? BibleVerseMap.loadFromAssets;

  final BibleModuleDataSource _moduleDataSource;
  final BiblePreferencesStore _preferencesStore;
  final Future<BibleVerseMap> Function() _loadVerseMap;

  BibleVerseMap? _verseMapCache;

  Future<BibleInitialData> loadInitial({
    required String languageCode,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) async {
    final verseMap = await _getVerseMap();
    final defaultModuleFile = defaultBibleModuleFileForLanguage(languageCode);
    final moduleFiles = await _moduleDataSource.listModuleFiles(
      defaultModuleFile: defaultModuleFile,
    );
    if (moduleFiles.isEmpty) {
      throw const BibleModulesUnavailableException();
    }

    final selectedModuleFile = await _resolveSelectedModuleFile(
      moduleFiles: moduleFiles,
      initialModuleFile: initialModuleFile,
      defaultModuleFile: defaultModuleFile,
    );
    final selectedModule = await loadModuleInfo(selectedModuleFile);
    final modules = List<BibleModuleInfo>.unmodifiable(
      moduleFiles.map(
        (moduleFile) => moduleFile == selectedModuleFile
            ? selectedModule
            : _placeholderModuleInfo(moduleFile),
      ),
    );
    final reference = verseMap.normalizedReference(
      bookId: initialBookId,
      chapter: initialChapter,
      verse: initialVerse,
    );
    final chapterData = await loadChapter(
      moduleFile: selectedModule.fileName,
      bookId: reference.bookId,
      chapter: reference.chapter,
      verse: reference.verse,
    );

    return BibleInitialData(
      verseMap: verseMap,
      modules: modules,
      selectedModule: selectedModule,
      reference: chapterData.reference,
      verses: chapterData.verses,
    );
  }

  Future<BibleModuleInfo> loadModuleInfo(String moduleFile) {
    return _readModuleInfo(moduleFile);
  }

  Future<BibleChapterData> loadChapter({
    required String moduleFile,
    required int bookId,
    required int chapter,
    required int verse,
  }) async {
    final verseMap = await _getVerseMap();
    final reference = verseMap.normalizedReference(
      bookId: bookId,
      chapter: chapter,
      verse: verse,
    );
    final verseKeys = verseMap.verseKeysForChapter(
      bookId: reference.bookId,
      chapter: reference.chapter,
    );
    final verseTexts = await _readVerseTexts(moduleFile, verseKeys);
    final textByKey = <String, String>{
      for (final verseText in verseTexts) verseText.verseKey: verseText.text,
    };
    final verses = <BibleChapterVerse>[];
    for (var index = 0; index < verseKeys.length; index++) {
      final verseReference = verseMap.referenceFor(
        bookId: reference.bookId,
        chapter: reference.chapter,
        verse: index + 1,
      );
      verses.add(
        BibleChapterVerse(
          reference: verseReference,
          text: textByKey[verseReference.verseKey] ?? '',
        ),
      );
    }

    return BibleChapterData(
      reference: reference,
      verses: List<BibleChapterVerse>.unmodifiable(verses),
    );
  }

  Future<void> saveLastModuleFile(String moduleFile) {
    return _preferencesStore.saveLastModuleFile(moduleFile);
  }

  Future<BibleVerseMap> _getVerseMap() async {
    return _verseMapCache ??= await _loadVerseMap();
  }

  Future<String> _resolveSelectedModuleFile({
    required List<String> moduleFiles,
    required String? initialModuleFile,
    required String defaultModuleFile,
  }) async {
    if (initialModuleFile != null && moduleFiles.contains(initialModuleFile)) {
      return initialModuleFile;
    }

    final storedModuleFile = await _preferencesStore.loadLastModuleFile();
    if (storedModuleFile != null && moduleFiles.contains(storedModuleFile)) {
      return storedModuleFile;
    }

    if (moduleFiles.contains(defaultModuleFile)) {
      return defaultModuleFile;
    }

    return moduleFiles.first;
  }

  Future<BibleModuleInfo> _readModuleInfo(String moduleFile) async {
    final database = _moduleDataSource.openModule(moduleFile);
    try {
      return await database.readInfo(moduleFile);
    } finally {
      await database.close();
    }
  }

  BibleModuleInfo _placeholderModuleInfo(String moduleFile) {
    final code = moduleFile
        .replaceFirst(RegExp(r'^bible_', caseSensitive: false), '')
        .replaceFirst(RegExp(r'\.sqlite$', caseSensitive: false), '')
        .toUpperCase();
    return BibleModuleInfo(
      fileName: moduleFile,
      code: code,
      moduleId: code.toLowerCase(),
      title: code,
      description: '',
      language: '',
      canon: '',
      versification: '',
      license: '',
      sourceSummary: '',
    );
  }

  Future<List<BibleVerseText>> _readVerseTexts(
    String moduleFile,
    List<String> verseKeys,
  ) async {
    final database = _moduleDataSource.openModule(moduleFile);
    try {
      return await database.readVersesByKeys(verseKeys);
    } finally {
      await database.close();
    }
  }
}

class BibleModulesUnavailableException implements Exception {
  const BibleModulesUnavailableException();
}
