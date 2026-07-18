import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_state.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('loads initial chapter, navigates and toggles Strong numbers', () async {
    final cubit = BibleReaderCubit(
      repository: _FakeBibleRepository(),
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

    expect(cubit.state.status, BibleReaderStatus.ready);
    expect(cubit.state.selectedReference?.bookId, 1);
    expect(cubit.state.selectedReference?.chapter, 1);
    expect(cubit.state.selectionStartVerse, 1);
    expect(cubit.state.selectionEndVerse, 1);
    expect(cubit.state.verses, isNotEmpty);
    expect(cubit.state.showStrongNumbers, isTrue);

    cubit.selectLoadedVerse(3);

    expect(cubit.state.selectedReference?.verse, 3);
    expect(cubit.state.selectionStartVerse, 3);
    expect(cubit.state.selectionEndVerse, 3);

    cubit.extendSelectionToVerse(5);

    expect(cubit.state.selectedReference?.verse, 5);
    expect(cubit.state.selectedVerseRangeStart, 3);
    expect(cubit.state.selectedVerseRangeEnd, 5);

    await cubit.navigateChapter(forward: true);

    expect(cubit.state.status, BibleReaderStatus.ready);
    expect(cubit.state.selectedReference?.chapter, 2);
    expect(cubit.state.selectionStartVerse, 1);
    expect(cubit.state.selectionEndVerse, 1);

    cubit.toggleStrongNumbers();

    expect(cubit.state.showStrongNumbers, isFalse);
  });
}

class _FakeBibleRepository extends BibleRepository {
  _FakeBibleRepository() : super();

  final _module = const BibleModuleInfo(
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
  );

  @override
  Future<BibleInitialData> loadInitial({
    required String languageCode,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) async {
    final map = await BibleVerseMap.loadFromAssets();
    final reference = map.normalizedReference(
      bookId: initialBookId,
      chapter: initialChapter,
      verse: initialVerse,
    );
    return BibleInitialData(
      verseMap: map,
      modules: [_module],
      selectedModule: _module,
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter),
    );
  }

  @override
  Future<BibleModuleInfo> loadModuleInfo(String moduleFile) async => _module;

  @override
  Future<BibleChapterData> loadChapter({
    required String moduleFile,
    required int bookId,
    required int chapter,
    required int verse,
  }) async {
    final map = await BibleVerseMap.loadFromAssets();
    final reference = map.normalizedReference(
      bookId: bookId,
      chapter: chapter,
      verse: verse,
    );
    return BibleChapterData(
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter),
    );
  }

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {}

  List<BibleChapterVerse> _buildChapter(
    BibleVerseMap map,
    int bookId,
    int chapter,
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
          text: 'verse $verse G1722',
        ),
    ];
  }
}
