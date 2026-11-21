import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/allusion_search/data/repositories/allusion_search_repository.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

enum AllusionStatus { loading, ready, searching, failure }

class AllusionSearchState {
  const AllusionSearchState({
    this.verseMap,
    this.query = (
      bookId: 66,
      chapter: 1,
      verse: 1,
      length: 1,
      scope: AllusionScope.wholeBible,
    ),
    this.status = AllusionStatus.ready,
    this.results,
    this.level = AllusionLevel.verse,
    this.page = 0,
    this.module,
    this.texts = const {},
    this.originals,
    this.index,
    this.loadingText = false,
    this.translationFailed = false,
    this.sourceExpanded = false,
    this.sourceWordsExpanded = false,
    this.expandedWords = '',
    this.expandedGroup = '',
  });

  static const pageSize = 20;
  final BibleVerseMap? verseMap;
  final AllusionQuery query;
  final AllusionStatus status;
  final AllusionResults? results;
  final AllusionLevel level;
  final int page;
  final BibleModuleInfo? module;
  final Map<String, String> texts;
  final Map<String, String>? originals;
  final AllusionIndex? index;
  final bool loadingText;
  final bool translationFailed;
  final bool sourceExpanded;
  final bool sourceWordsExpanded;
  final String expandedWords;
  final String expandedGroup;

  List<AllusionMatch> get matches => results?.forLevel(level) ?? const [];
  List<AllusionMatch> get visible =>
      matches.skip(page * pageSize).take(pageSize).toList(growable: false);
  int get pageCount => (matches.length / pageSize).ceil();

  List<BibleVerseReference> get sourceReferences {
    final map = verseMap;
    if (map == null) return const [];
    final first = map.normalizedReference(
      bookId: query.bookId,
      chapter: query.chapter,
      verse: query.verse,
    );
    final ordinal = int.parse(first.verseKey, radix: 36);
    final length = math.min(query.length, map.totalVerses - ordinal + 1);
    return [
      for (var n = ordinal; n < ordinal + length; n++)
        map.referenceForOrdinal(n),
    ];
  }

  AllusionSearchState copyWith({
    BibleVerseMap? verseMap,
    AllusionQuery? query,
    AllusionStatus? status,
    AllusionResults? results,
    bool clearResults = false,
    AllusionLevel? level,
    int? page,
    BibleModuleInfo? module,
    Map<String, String>? texts,
    Map<String, String>? originals,
    bool clearOriginal = false,
    AllusionIndex? index,
    bool clearTranslation = false,
    bool? loadingText,
    bool? translationFailed,
    bool? sourceExpanded,
    bool? sourceWordsExpanded,
    String? expandedWords,
    String? expandedGroup,
  }) => AllusionSearchState(
    verseMap: verseMap ?? this.verseMap,
    query: query ?? this.query,
    status: status ?? this.status,
    results: clearResults ? null : results ?? this.results,
    level: level ?? this.level,
    page: page ?? this.page,
    module: clearTranslation ? null : module ?? this.module,
    originals: clearOriginal ? null : originals ?? this.originals,
    index: index ?? this.index,
    texts: clearTranslation ? const {} : texts ?? this.texts,
    loadingText: loadingText ?? this.loadingText,
    translationFailed: translationFailed ?? this.translationFailed,
    sourceExpanded: sourceExpanded ?? this.sourceExpanded,
    sourceWordsExpanded: sourceWordsExpanded ?? this.sourceWordsExpanded,
    expandedWords: expandedWords ?? this.expandedWords,
    expandedGroup: expandedGroup ?? this.expandedGroup,
  );

  @override
  bool operator ==(Object other) =>
      other is AllusionSearchState &&
      verseMap == other.verseMap &&
      query == other.query &&
      status == other.status &&
      results == other.results &&
      level == other.level &&
      page == other.page &&
      module == other.module &&
      mapEquals(texts, other.texts) &&
      mapEquals(originals, other.originals) &&
      index == other.index &&
      loadingText == other.loadingText &&
      translationFailed == other.translationFailed &&
      sourceExpanded == other.sourceExpanded &&
      sourceWordsExpanded == other.sourceWordsExpanded &&
      expandedWords == other.expandedWords &&
      expandedGroup == other.expandedGroup;

  @override
  int get hashCode => Object.hash(
    verseMap,
    query,
    status,
    results,
    level,
    page,
    module,
    Object.hashAllUnordered(
      texts.entries.map((e) => Object.hash(e.key, e.value)),
    ),
    Object.hashAllUnordered(
      originals?.entries.map((e) => Object.hash(e.key, e.value)) ?? const [],
    ),
    index,
    loadingText,
    translationFailed,
    sourceExpanded,
    sourceWordsExpanded,
    expandedWords,
    expandedGroup,
  );
}

class AllusionSearchCubit extends Cubit<AllusionSearchState> {
  AllusionSearchCubit(
    this._repository,
    this._library, {
    BibleVerseMap? initialVerseMap,
  }) : super(AllusionSearchState(verseMap: initialVerseMap));
  final AllusionSearchRepository _repository;
  final BibleLibraryRepository _library;
  final _searches = LatestRequestGuard();
  final _originals = LatestRequestGuard();
  final _translations = LatestRequestGuard();
  Future<void>? _initializing;
  int _visit = 0;
  ({int visit, Future<AllusionIndex> future})? _indexCheck;

  Future<void> beginVisit() {
    _visit++;
    return ensureLoaded();
  }

  Future<void> ensureLoaded() =>
      _initializing ??= _open().whenComplete(() => _initializing = null);

  Future<void> _open() async {
    if (state.verseMap == null) {
      emit(state.copyWith(status: AllusionStatus.loading));
      try {
        final map = await _repository.loadVerseMap();
        if (isClosed) return;
        emit(state.copyWith(verseMap: map, status: AllusionStatus.ready));
      } catch (error, stackTrace) {
        if (isClosed) return;
        addError(error, stackTrace);
        emit(state.copyWith(status: AllusionStatus.failure));
        return;
      }
    }
    await Future.wait([_refreshOriginal(), refreshTranslation()]);
  }

  /// A failed warm-up can be retried when the user actually searches.
  Future<void> prepareIndex() async {
    try {
      final visit = _visit;
      final index = await _indexForVisit();
      if (!isClosed && visit == _visit) emit(state.copyWith(index: index));
    } catch (_) {
      // The form and source translation work independently of the Greek corpus.
    }
  }

  Future<AllusionIndex> _indexForVisit() {
    final prior = _indexCheck;
    if (prior != null && prior.visit == _visit) return prior.future;
    final future = _checkRevision(_visit, prior?.future);
    _indexCheck = (visit: _visit, future: future);
    return future;
  }

  Future<AllusionIndex> _checkRevision(
    int visit,
    Future<AllusionIndex>? prior,
  ) async {
    if (prior != null) {
      // Finish the previous snapshot before asking the repository to check this visit's revision.
      try {
        await prior;
      } catch (_) {
        // A failed check on the previous visit may now succeed.
      }
    }
    try {
      if (isClosed) throw StateError('Allusion search has closed');
      return await Future.sync(_repository.loadIndex);
    } catch (_) {
      if (_indexCheck?.visit == visit) _indexCheck = null;
      rethrow;
    }
  }

  void updateQuery({
    int? bookId,
    int? chapter,
    int? verse,
    int? length,
    AllusionScope? scope,
  }) {
    final map = state.verseMap;
    if (map == null) return;
    final old = state.query;
    final ref = map.normalizedReference(
      bookId: bookId ?? old.bookId,
      chapter: chapter ?? old.chapter,
      verse: verse ?? old.verse,
    );
    final lastLength = math.min(
      AllusionIndex.maxLength,
      map.totalVerses - int.parse(ref.verseKey, radix: 36) + 1,
    );
    final next = (
      bookId: ref.bookId,
      chapter: ref.chapter,
      verse: ref.verse,
      length: (length ?? old.length).clamp(1, lastLength).toInt(),
      scope: scope ?? old.scope,
    );
    if (old == next) return;
    _searches.cancelActive();
    final changedPassage =
        old.bookId != next.bookId ||
        old.chapter != next.chapter ||
        old.verse != next.verse ||
        old.length != next.length;
    emit(
      state.copyWith(
        query: next,
        status: AllusionStatus.ready,
        clearResults: true,
        page: 0,
        expandedWords: '',
        expandedGroup: '',
        clearOriginal: changedPassage,
        sourceExpanded: changedPassage ? false : state.sourceExpanded,
        sourceWordsExpanded: changedPassage ? false : state.sourceWordsExpanded,
      ),
    );
    if (changedPassage) {
      unawaited(_refreshOriginal());
      unawaited(refreshTranslation());
    }
  }

  Future<void> search() async {
    if (state.verseMap == null || state.status == AllusionStatus.searching)
      return;
    final request = _searches.start();
    final query = state.query;
    emit(
      state.copyWith(
        status: AllusionStatus.searching,
        clearResults: true,
        level: AllusionLevel.verse,
        page: 0,
        expandedWords: '',
        expandedGroup: '',
      ),
    );
    try {
      final index = await _indexForVisit();
      if (isClosed || !_searches.isActive(request)) return;
      final matches = await _repository.search(index, query);
      if (isClosed || !_searches.isActive(request)) return;
      emit(state.copyWith(results: matches, index: index));
      await refreshTranslation();
      if (isClosed || !_searches.isActive(request)) return;
      emit(state.copyWith(status: AllusionStatus.ready));
    } catch (error, stackTrace) {
      if (isClosed || !_searches.isActive(request)) return;
      addError(error, stackTrace);
      emit(state.copyWith(status: AllusionStatus.failure));
    }
  }

  void toggleSource() =>
      emit(state.copyWith(sourceExpanded: !state.sourceExpanded));
  void toggleSourceWords() =>
      emit(state.copyWith(sourceWordsExpanded: !state.sourceWordsExpanded));
  void toggleWords(String key) => emit(
    state.copyWith(expandedWords: state.expandedWords == key ? '' : key),
  );
  void toggleGroup(String key) => emit(
    state.copyWith(expandedGroup: state.expandedGroup == key ? '' : key),
  );

  Future<void> setLevel(AllusionLevel level) async {
    if (state.level == level) return;
    emit(
      state.copyWith(
        level: level,
        page: 0,
        expandedWords: '',
        expandedGroup: '',
      ),
    );
    await refreshTranslation();
  }

  Future<void> setPage(int page) async {
    if (page < 0 || page >= state.pageCount || page == state.page) return;
    emit(state.copyWith(page: page, expandedWords: '', expandedGroup: ''));
    await refreshTranslation();
  }

  Future<void> _refreshOriginal() async {
    final request = _originals.start();
    final keys = state.sourceReferences.map((r) => r.verseKey).toList();
    try {
      final preview = await _library.loadPreview(
        keys,
        moduleFile: AppConstants.defaultBibleModuleDB,
      );
      if (isClosed || !_originals.isActive(request)) return;
      emit(
        state.copyWith(
          originals: Map.unmodifiable({
            for (final verse in preview.verses) verse.verseKey: verse.text,
          }),
        ),
      );
    } catch (error, stackTrace) {
      if (isClosed || !_originals.isActive(request)) return;
      addError(error, stackTrace);
      emit(state.copyWith(originals: const {}));
    }
  }

  Future<void> refreshTranslation({bool preferenceChanged = false}) async {
    if (state.verseMap == null) return;
    final request = _translations.start();
    final keys = <String>{
      for (final ref in state.sourceReferences) ref.verseKey,
      for (final match in state.visible) match.reference.verseKey,
    };
    emit(
      state.copyWith(
        loadingText: true,
        clearTranslation: preferenceChanged,
        translationFailed: false,
      ),
    );
    try {
      final preview = await _library.loadPreview(keys.toList());
      if (isClosed || !_translations.isActive(request)) return;
      emit(
        state.copyWith(
          module: preview.module,
          texts: Map.unmodifiable({
            for (final item in preview.verses) item.verseKey: item.text,
          }),
          loadingText: false,
        ),
      );
    } catch (error, stackTrace) {
      if (isClosed || !_translations.isActive(request)) return;
      addError(error, stackTrace);
      emit(
        state.copyWith(
          clearTranslation: true,
          translationFailed: true,
          loadingText: false,
        ),
      );
    }
  }
}
