import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test(
    'restores open module panes, syncs linked references and persists closes',
    () async {
      final repository = _FakeBibleRepository(
        storedModuleFiles: [
          'bible_lxx_tr.sqlite',
          'bible_alt.sqlite',
          'bible_third.sqlite',
        ],
      );
      final cubit = BibleWorkspaceCubit(
        repositoryFactory: () => repository,
        languageCode: 'en',
        initialBookId: 1,
        initialChapter: 1,
        initialVerse: 1,
        loadingBibleMessage: 'loading bible',
        loadingChapterMessage: 'loading chapter',
        loadingModuleMessage: 'loading module',
        modulesUnavailableMessage: 'no modules',
      );
      addTearDown(cubit.close);

      await cubit.loadInitial();

      expect(cubit.state.paneIds, ['primary', 'parallel_2', 'parallel_3']);
      expect(
        cubit.readerCubitFor('parallel_2').state.selectedModule?.fileName,
        'bible_alt.sqlite',
      );
      expect(
        cubit.readerCubitFor('parallel_3').state.selectedModule?.fileName,
        'bible_third.sqlite',
      );

      await cubit
          .readerCubitFor('primary')
          .selectReference(bookId: 1, chapter: 2, verse: 3);
      await _drainAsyncWork();

      for (final paneId in cubit.state.paneIds) {
        final reference = cubit.readerCubitFor(paneId).state.selectedReference;
        expect(reference?.chapter, 2, reason: paneId);
        expect(reference?.verse, 3, reason: paneId);
      }

      cubit.toggleLinkedNavigation();
      await cubit
          .readerCubitFor('primary')
          .selectReference(bookId: 1, chapter: 3, verse: 1);
      await _drainAsyncWork();

      expect(
        cubit.readerCubitFor('primary').state.selectedReference?.chapter,
        3,
      );
      expect(
        cubit.readerCubitFor('parallel_2').state.selectedReference?.chapter,
        2,
      );

      cubit.toggleLinkedNavigation();
      await _drainAsyncWork();

      expect(
        cubit.readerCubitFor('parallel_2').state.selectedReference?.chapter,
        3,
      );

      await cubit.closeReaderPane('parallel_2');

      expect(cubit.state.paneIds, ['primary', 'parallel_3']);
      expect(repository.savedModuleFileLists.last, [
        'bible_lxx_tr.sqlite',
        'bible_third.sqlite',
      ]);
    },
  );
}

Future<void> _drainAsyncWork() async {
  for (var index = 0; index < 8; index++) {
    await Future<void>.delayed(Duration.zero);
  }
}

class _FakeBibleRepository extends BibleRepository {
  _FakeBibleRepository({required List<String> storedModuleFiles})
    : storedModuleFiles = List<String>.from(storedModuleFiles),
      super();

  List<String> storedModuleFiles;
  final savedModuleFileLists = <List<String>>[];

  final _modules = const <BibleModuleInfo>[
    BibleModuleInfo(
      fileName: 'bible_lxx_tr.sqlite',
      code: 'LXX_TR',
      moduleId: 'lxx_tr',
      title: 'Greek Bible',
      description: '',
      language: 'grc',
      canon: 'protestant_66',
      versification: 'kjv_protestant',
      license: '',
      sourceSummary: '',
    ),
    BibleModuleInfo(
      fileName: 'bible_alt.sqlite',
      code: 'ALT',
      moduleId: 'alt',
      title: 'Alternative Bible',
      description: '',
      language: 'en',
      canon: 'protestant_66',
      versification: 'kjv_protestant',
      license: '',
      sourceSummary: '',
    ),
    BibleModuleInfo(
      fileName: 'bible_third.sqlite',
      code: 'THIRD',
      moduleId: 'third',
      title: 'Third Bible',
      description: '',
      language: 'en',
      canon: 'protestant_66',
      versification: 'kjv_protestant',
      license: '',
      sourceSummary: '',
    ),
  ];

  @override
  Future<List<String>> loadLastModuleFiles() async {
    return List<String>.unmodifiable(storedModuleFiles);
  }

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {}

  @override
  Future<void> saveLastModuleFiles(List<String> moduleFiles) async {
    storedModuleFiles = List<String>.from(moduleFiles);
    savedModuleFileLists.add(List<String>.from(moduleFiles));
  }

  @override
  Future<BibleInitialData> loadInitial({
    required String languageCode,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) async {
    final map = await BibleVerseMap.loadFromAssets();
    final module = _moduleFor(initialModuleFile) ?? _modules.first;
    final reference = map.normalizedReference(
      bookId: initialBookId,
      chapter: initialChapter,
      verse: initialVerse,
    );
    return BibleInitialData(
      verseMap: map,
      modules: _modules,
      selectedModule: module,
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter, module),
    );
  }

  @override
  Future<BibleModuleInfo> loadModuleInfo(String moduleFile) async {
    return _moduleFor(moduleFile) ?? _modules.first;
  }

  @override
  Future<BibleChapterData> loadChapter({
    required String moduleFile,
    required int bookId,
    required int chapter,
    required int verse,
  }) async {
    final map = await BibleVerseMap.loadFromAssets();
    final module = _moduleFor(moduleFile) ?? _modules.first;
    final reference = map.normalizedReference(
      bookId: bookId,
      chapter: chapter,
      verse: verse,
    );
    return BibleChapterData(
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter, module),
    );
  }

  BibleModuleInfo? _moduleFor(String? moduleFile) {
    if (moduleFile == null) {
      return null;
    }
    for (final module in _modules) {
      if (module.fileName == moduleFile) {
        return module;
      }
    }
    return null;
  }

  List<BibleChapterVerse> _buildChapter(
    BibleVerseMap map,
    int bookId,
    int chapter,
    BibleModuleInfo module,
  ) {
    return [
      for (
        var verse = 1;
        verse <= map.verseCount(bookId: bookId, chapter: chapter);
        verse++
      )
        BibleChapterVerse(
          reference: map.referenceFor(
            bookId: bookId,
            chapter: chapter,
            verse: verse,
          ),
          text: '${module.code} verse $verse G1722',
        ),
    ];
  }
}
