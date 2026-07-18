import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_search_result.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_state.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_search_state.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('BibleReaderState derives selection and navigation state', () async {
    final map = await BibleVerseMap.loadFromAssets();
    final reference = map.referenceFor(bookId: 1, chapter: 1, verse: 1);
    final module = _module('TEST');
    final verse = BibleChapterVerse(reference: reference, text: 'text');

    const initial = BibleReaderState.initial();
    expect(initial.hasSelectedVerses, isFalse);
    expect(initial.selectedVerseRangeStart, isNull);
    expect(initial.selectedVerseRangeEnd, isNull);
    expect(initial.isBusy, isFalse);
    expect(initial.canNavigateBackward, isFalse);
    expect(initial.canNavigateForward, isFalse);

    final state = BibleReaderState(
      status: BibleReaderStatus.ready,
      verseMap: map,
      modules: [module],
      selectedModule: module,
      selectedReference: reference,
      selectionStartVerse: 4,
      selectionEndVerse: 2,
      verses: [verse],
      showStrongNumbers: false,
      loadingMessage: 'loading',
      errorMessage: 'error',
    );
    expect(state.hasSelectedVerses, isTrue);
    expect(state.selectedVerseRangeStart, 2);
    expect(state.selectedVerseRangeEnd, 4);
    expect(state.canNavigateBackward, isFalse);
    expect(state.canNavigateForward, isTrue);
    expect(
      state
          .copyWith(
            selectedReference: map.referenceFor(
              bookId: 1,
              chapter: 2,
              verse: 1,
            ),
            selectedReferenceSet: true,
          )
          .canNavigateBackward,
      isTrue,
    );

    final ascending = state.copyWith(
      selectionStartVerse: 2,
      selectionEndVerse: 4,
    );
    expect(ascending.selectedVerseRangeStart, 2);
    expect(ascending.selectedVerseRangeEnd, 4);

    for (final status in <BibleReaderStatus>[
      BibleReaderStatus.initialLoading,
      BibleReaderStatus.loadingChapter,
      BibleReaderStatus.loadingModule,
    ]) {
      expect(state.copyWith(status: status).isBusy, isTrue);
    }

    final cleared = state.copyWith(
      selectedModuleSet: true,
      selectedReferenceSet: true,
      selectionStartVerseSet: true,
      selectionEndVerseSet: true,
      loadingMessageSet: true,
      errorMessageSet: true,
    );
    expect(cleared.selectedModule, isNull);
    expect(cleared.selectedReference, isNull);
    expect(cleared.selectionStartVerse, isNull);
    expect(cleared.selectionEndVerse, isNull);
    expect(cleared.loadingMessage, isNull);
    expect(cleared.errorMessage, isNull);
    expect(state, state.copyWith());
    expect(state, isNot(state.copyWith(modules: const <BibleModuleInfo>[])));
    expect(state, isNot(state.copyWith(verses: const <BibleChapterVerse>[])));
    expect(state, state.copyWith(modules: [module], verses: [verse]));
    expect(state, isNot(state.copyWith(showStrongNumbers: true)));
    expect(state == Object(), isFalse);
    expect(state.hashCode, isA<int>());
  });

  test('BibleSearchState paginates, selects and compares results', () {
    final results = [for (var index = 0; index < 21; index++) _result(index)];
    final state = BibleSearchState(
      moduleFile: 'bible_test.sqlite',
      query: 'logos',
      history: const ['logos', 'grace'],
      status: BibleSearchStatus.ready,
      results: results,
      selectedVerseKeys: const {'001'},
      pageIndex: 99,
      resultTapAction: BibleSearchResultTapAction.open,
      searchedQuery: 'logos',
      errorMessage: 'error',
    );

    expect(state.isLoading, isFalse);
    expect(state.hasSearched, isTrue);
    expect(state.totalMatches, 21);
    expect(state.pageCount, 2);
    expect(state.visiblePageIndex, 1);
    expect(state.pageNumber, 2);
    expect(state.canGoPrevious, isTrue);
    expect(state.canGoNext, isFalse);
    expect(state.pageResults, hasLength(1));
    expect(state.selectedResults.single.reference.verseKey, '001');

    expect(state.copyWith(status: BibleSearchStatus.loading).isLoading, isTrue);
    expect(
      state.copyWith(searchedQuery: '  ', searchedQuerySet: true).hasSearched,
      isFalse,
    );
    expect(state.copyWith(pageIndex: -1).visiblePageIndex, 0);
    expect(state.copyWith(history: ['logos', 'grace']), state);

    final empty = BibleSearchState.initial(moduleFile: 'bible_test.sqlite');
    expect(empty.isLoading, isFalse);
    expect(empty.hasSearched, isFalse);
    expect(empty.pageCount, 0);
    expect(empty.visiblePageIndex, 0);
    expect(empty.pageNumber, 0);
    expect(empty.canGoPrevious, isFalse);
    expect(empty.canGoNext, isFalse);
    expect(empty.pageResults, isEmpty);
    expect(empty.selectedResults, isEmpty);

    final cleared = state.copyWith(
      searchedQuerySet: true,
      errorMessageSet: true,
    );
    expect(cleared.searchedQuery, isNull);
    expect(cleared.errorMessage, isNull);
    expect(state, state.copyWith());
    expect(state, state.copyWith(selectedVerseKeys: const {'001'}));
    expect(state, isNot(state.copyWith(selectedVerseKeys: const {'002'})));
    expect(state, isNot(state.copyWith(history: const ['other'])));
    expect(state, isNot(state.copyWith(results: const <BibleSearchResult>[])));
    expect(state == Object(), isFalse);
    expect(state.hashCode, isA<int>());
  });
}

BibleModuleInfo _module(String code) {
  return BibleModuleInfo(
    fileName: 'bible_$code.sqlite',
    code: code,
    moduleId: code.toLowerCase(),
    title: code,
    description: '',
    language: 'en',
    canon: '66',
    versification: 'kjv',
    license: '',
    sourceSummary: '',
  );
}

BibleSearchResult _result(int index) {
  return BibleSearchResult(
    reference: BibleVerseReference(
      verseKey: index.toRadixString(36).padLeft(3, '0').toUpperCase(),
      bookId: 1,
      chapter: 1,
      verse: index + 1,
    ),
    text: 'logos',
    matches: const [BibleTextMatch(start: 0, end: 5)],
  );
}
