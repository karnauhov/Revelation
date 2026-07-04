import 'package:revelation/features/bible/domain/models/bible_search_result.dart';

const int bibleSearchResultsPerPage = 20;

enum BibleSearchStatus { initial, loading, ready, failure }

enum BibleSearchResultTapAction { copy, open }

class BibleSearchState {
  const BibleSearchState({
    required this.moduleFile,
    required this.query,
    required this.history,
    required this.status,
    required this.results,
    required this.selectedVerseKeys,
    required this.pageIndex,
    required this.resultTapAction,
    this.searchedQuery,
    this.errorMessage,
  });

  BibleSearchState.initial({required String moduleFile})
    : moduleFile = moduleFile,
      query = '',
      history = const <String>[],
      status = BibleSearchStatus.initial,
      results = const <BibleSearchResult>[],
      selectedVerseKeys = const <String>{},
      pageIndex = 0,
      resultTapAction = BibleSearchResultTapAction.copy,
      searchedQuery = null,
      errorMessage = null;

  final String moduleFile;
  final String query;
  final List<String> history;
  final BibleSearchStatus status;
  final List<BibleSearchResult> results;
  final Set<String> selectedVerseKeys;
  final int pageIndex;
  final BibleSearchResultTapAction resultTapAction;
  final String? searchedQuery;
  final String? errorMessage;

  bool get isLoading => status == BibleSearchStatus.loading;

  bool get hasSearched =>
      searchedQuery != null && searchedQuery!.trim().isNotEmpty;

  int get totalMatches =>
      results.fold<int>(0, (total, result) => total + result.matchCount);

  int get pageCount {
    if (results.isEmpty) {
      return 0;
    }
    return ((results.length - 1) ~/ bibleSearchResultsPerPage) + 1;
  }

  int get visiblePageIndex {
    if (pageCount == 0) {
      return 0;
    }
    return pageIndex.clamp(0, pageCount - 1).toInt();
  }

  int get pageNumber => pageCount == 0 ? 0 : visiblePageIndex + 1;

  bool get canGoPrevious => visiblePageIndex > 0;

  bool get canGoNext => visiblePageIndex < pageCount - 1;

  List<BibleSearchResult> get pageResults {
    if (results.isEmpty) {
      return const <BibleSearchResult>[];
    }
    final start = visiblePageIndex * bibleSearchResultsPerPage;
    final end = (start + bibleSearchResultsPerPage)
        .clamp(0, results.length)
        .toInt();
    return results.sublist(start, end);
  }

  List<BibleSearchResult> get selectedResults {
    if (selectedVerseKeys.isEmpty) {
      return const <BibleSearchResult>[];
    }
    return results
        .where(
          (result) => selectedVerseKeys.contains(result.reference.verseKey),
        )
        .toList(growable: false);
  }

  BibleSearchState copyWith({
    String? query,
    List<String>? history,
    BibleSearchStatus? status,
    List<BibleSearchResult>? results,
    Set<String>? selectedVerseKeys,
    int? pageIndex,
    BibleSearchResultTapAction? resultTapAction,
    String? searchedQuery,
    bool searchedQuerySet = false,
    String? errorMessage,
    bool errorMessageSet = false,
  }) {
    return BibleSearchState(
      moduleFile: moduleFile,
      query: query ?? this.query,
      history: history ?? this.history,
      status: status ?? this.status,
      results: results ?? this.results,
      selectedVerseKeys: selectedVerseKeys ?? this.selectedVerseKeys,
      pageIndex: pageIndex ?? this.pageIndex,
      resultTapAction: resultTapAction ?? this.resultTapAction,
      searchedQuery: searchedQuerySet ? searchedQuery : this.searchedQuery,
      errorMessage: errorMessageSet ? errorMessage : this.errorMessage,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleSearchState &&
            moduleFile == other.moduleFile &&
            query == other.query &&
            _listEquals(history, other.history) &&
            status == other.status &&
            _listEquals(results, other.results) &&
            _setEquals(selectedVerseKeys, other.selectedVerseKeys) &&
            pageIndex == other.pageIndex &&
            resultTapAction == other.resultTapAction &&
            searchedQuery == other.searchedQuery &&
            errorMessage == other.errorMessage;
  }

  @override
  int get hashCode => Object.hash(
    moduleFile,
    query,
    Object.hashAll(history),
    status,
    Object.hashAll(results),
    Object.hashAll(_sortedStrings(selectedVerseKeys)),
    pageIndex,
    resultTapAction,
    searchedQuery,
    errorMessage,
  );
}

bool _listEquals<T>(List<T> left, List<T> right) {
  if (identical(left, right)) {
    return true;
  }
  if (left.length != right.length) {
    return false;
  }
  for (var index = 0; index < left.length; index++) {
    if (left[index] != right[index]) {
      return false;
    }
  }
  return true;
}

bool _setEquals<T>(Set<T> left, Set<T> right) {
  if (identical(left, right)) {
    return true;
  }
  if (left.length != right.length) {
    return false;
  }
  for (final item in left) {
    if (!right.contains(item)) {
      return false;
    }
  }
  return true;
}

List<String> _sortedStrings(Set<String> values) {
  return values.toList(growable: false)..sort();
}
