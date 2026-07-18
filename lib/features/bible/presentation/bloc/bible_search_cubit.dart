import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_search_state.dart';

class BibleSearchCubit extends Cubit<BibleSearchState> {
  BibleSearchCubit({
    required BibleRepository repository,
    required String moduleFile,
  }) : _repository = repository,
       super(BibleSearchState.initial(moduleFile: moduleFile));

  final BibleRepository _repository;
  final LatestRequestGuard _requestGuard = LatestRequestGuard();

  Future<void> loadInitial() async {
    final token = _requestGuard.start();
    try {
      final lastQuery = await _repository.loadLastSearchQuery(state.moduleFile);
      final history = await _repository.loadSearchHistory();
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      emit(
        state.copyWith(
          query: lastQuery ?? '',
          history: List<String>.unmodifiable(history),
          status: BibleSearchStatus.ready,
          errorMessage: null,
          errorMessageSet: true,
        ),
      );
      if (lastQuery != null && lastQuery.trim().isNotEmpty) {
        await search(query: lastQuery, rememberQuery: false);
      }
    } catch (error) {
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      emit(
        state.copyWith(
          status: BibleSearchStatus.failure,
          errorMessage: error.toString(),
          errorMessageSet: true,
        ),
      );
    }
  }

  void updateQuery(String query) {
    if (state.query == query) {
      return;
    }
    emit(state.copyWith(query: query));
  }

  void setResultTapAction(BibleSearchResultTapAction action) {
    if (state.resultTapAction == action) {
      return;
    }
    emit(state.copyWith(resultTapAction: action));
  }

  Future<void> search({String? query, bool rememberQuery = true}) async {
    final normalizedQuery = normalizeBibleSearchQuery(query ?? state.query);
    if (normalizedQuery.isEmpty) {
      _requestGuard.cancelActive();
      emit(
        state.copyWith(
          query: normalizedQuery,
          status: BibleSearchStatus.ready,
          results: const [],
          selectedVerseKeys: const <String>{},
          pageIndex: 0,
          searchedQuery: null,
          searchedQuerySet: true,
          errorMessage: null,
          errorMessageSet: true,
        ),
      );
      return;
    }

    final token = _requestGuard.start();
    emit(
      state.copyWith(
        query: normalizedQuery,
        status: BibleSearchStatus.loading,
        errorMessage: null,
        errorMessageSet: true,
      ),
    );

    try {
      final results = await _repository.searchModule(
        moduleFile: state.moduleFile,
        query: normalizedQuery,
      );
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      if (rememberQuery) {
        await _repository.saveLastSearchQuery(
          moduleFile: state.moduleFile,
          query: normalizedQuery,
        );
        await _repository.rememberSearchQuery(normalizedQuery);
      }
      final history = await _repository.loadSearchHistory();
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      emit(
        state.copyWith(
          query: normalizedQuery,
          history: List<String>.unmodifiable(history),
          status: BibleSearchStatus.ready,
          results: List.unmodifiable(results),
          selectedVerseKeys: const <String>{},
          pageIndex: 0,
          searchedQuery: normalizedQuery,
          searchedQuerySet: true,
          errorMessage: null,
          errorMessageSet: true,
        ),
      );
    } catch (error) {
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      emit(
        state.copyWith(
          status: BibleSearchStatus.failure,
          errorMessage: error.toString(),
          errorMessageSet: true,
        ),
      );
    }
  }

  void goToPage(int pageIndex) {
    if (state.pageCount == 0) {
      return;
    }
    final nextPage = pageIndex.clamp(0, state.pageCount - 1).toInt();
    if (nextPage == state.visiblePageIndex) {
      return;
    }
    emit(state.copyWith(pageIndex: nextPage));
  }

  void toggleResultSelection(String verseKey) {
    final selected = Set<String>.of(state.selectedVerseKeys);
    if (!selected.add(verseKey)) {
      selected.remove(verseKey);
    }
    emit(state.copyWith(selectedVerseKeys: Set<String>.unmodifiable(selected)));
  }

  @override
  Future<void> close() {
    _requestGuard.cancelActive();
    return super.close();
  }
}
