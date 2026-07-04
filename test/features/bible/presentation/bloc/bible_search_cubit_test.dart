import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_search_result.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_search_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_search_state.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';

void main() {
  test('loads last search and restores its results', () async {
    final repository = _FakeBibleRepository(
      lastQuery: 'logos',
      history: const ['logos', 'grace'],
      results: _buildResults(25),
    );
    final cubit = BibleSearchCubit(
      repository: repository,
      moduleFile: 'bible_lxx_tr.sqlite',
    );
    addTearDown(cubit.close);

    await cubit.loadInitial();

    expect(repository.searchQueries, ['logos']);
    expect(cubit.state.status, BibleSearchStatus.ready);
    expect(cubit.state.query, 'logos');
    expect(cubit.state.results, hasLength(25));
    expect(cubit.state.pageCount, 2);
    expect(cubit.state.pageResults, hasLength(bibleSearchResultsPerPage));
    expect(cubit.state.pageResults.first.reference.verse, 1);

    cubit.goToPage(1);

    expect(cubit.state.pageNumber, 2);
    expect(cubit.state.pageResults.first.reference.verse, 21);
  });

  test('persists explicit searches and keeps selected results', () async {
    final repository = _FakeBibleRepository(
      history: const ['logos'],
      results: _buildResults(2),
    );
    final cubit = BibleSearchCubit(
      repository: repository,
      moduleFile: 'bible_lxx_tr.sqlite',
    );
    addTearDown(cubit.close);

    await cubit.search(query: '  grace  ');
    cubit.toggleResultSelection('001');

    expect(repository.savedLastSearchQueries, ['grace']);
    expect(repository.rememberedQueries, ['grace']);
    expect(cubit.state.query, 'grace');
    expect(cubit.state.selectedResults.single.reference.verseKey, '001');
  });
}

List<BibleSearchResult> _buildResults(int count) {
  return [for (var index = 1; index <= count; index++) _result(index)];
}

BibleSearchResult _result(int index) {
  final text = 'verse $index with logos';
  final matchStart = text.indexOf('logos');
  return BibleSearchResult(
    reference: BibleVerseReference(
      verseKey: index.toRadixString(36).padLeft(3, '0').toUpperCase(),
      bookId: 1,
      chapter: 1,
      verse: index,
    ),
    text: text,
    matches: [BibleTextMatch(start: matchStart, end: matchStart + 5)],
  );
}

class _FakeBibleRepository extends BibleRepository {
  _FakeBibleRepository({
    this.lastQuery,
    List<String> history = const <String>[],
    List<BibleSearchResult> results = const <BibleSearchResult>[],
  }) : history = List<String>.of(history),
       results = List<BibleSearchResult>.of(results),
       super();

  final String? lastQuery;
  List<String> history;
  List<BibleSearchResult> results;
  final List<String> searchQueries = [];
  final List<String> savedLastSearchQueries = [];
  final List<String> rememberedQueries = [];

  @override
  Future<String?> loadLastSearchQuery(String moduleFile) async => lastQuery;

  @override
  Future<List<String>> loadSearchHistory() async => history;

  @override
  Future<List<BibleSearchResult>> searchModule({
    required String moduleFile,
    required String query,
  }) async {
    searchQueries.add(query);
    return results;
  }

  @override
  Future<void> saveLastSearchQuery({
    required String moduleFile,
    required String query,
  }) async {
    savedLastSearchQueries.add(query);
  }

  @override
  Future<void> rememberSearchQuery(String query) async {
    rememberedQueries.add(query);
    history = [query, ...history.where((item) => item != query)];
  }
}
