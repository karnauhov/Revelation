import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_content_service.dart';
import 'package:revelation/features/strongs_dictionary/data/repositories/strong_dictionary_reading_store.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strongs_dictionary_state.dart';
import 'package:revelation/l10n/app_localizations.dart';

class StrongsDictionaryCubit extends Cubit<StrongsDictionaryState> {
  StrongsDictionaryCubit({
    int? initialStrongNumber,
    required AppLocalizations localizations,
    StrongsDictionaryContentService? contentService,
    StrongDictionaryReadingStore? readingStore,
  }) : this._(
         contentService ?? StrongsDictionaryContentService(),
         readingStore: readingStore,
         initialStrongNumber: initialStrongNumber,
         localizations: localizations,
       );

  StrongsDictionaryCubit._(
    StrongsDictionaryContentService contentService, {
    required StrongDictionaryReadingStore? readingStore,
    int? initialStrongNumber,
    required AppLocalizations localizations,
  }) : _contentService = contentService,
       _readingStore = readingStore,
       super(
         StrongsDictionaryState.initial(
           strongNumber: initialStrongNumber ?? 1,
           pickerEntries: contentService.getPickerEntries(),
           restoring: initialStrongNumber == null && readingStore != null,
         ),
       ) {
    if (initialStrongNumber == null && readingStore != null) {
      unawaited(_restore(localizations, readingStore));
    } else {
      showStrongNumber(
        localizations: localizations,
        strongNumber: initialStrongNumber ?? state.strongNumber,
      );
    }
  }

  final StrongsDictionaryContentService _contentService;
  final StrongDictionaryReadingStore? _readingStore;
  double _articleOffset = 0;
  double get articleOffset => _articleOffset;

  Future<void> _restore(
    AppLocalizations localizations,
    StrongDictionaryReadingStore store,
  ) async {
    StrongDictionaryPlace? place;
    try {
      place = await store.load();
    } catch (error, trace) {
      if (!isClosed) addError(error, trace);
    }
    if (isClosed || !state.restoring) return;
    final saved = place;
    if (saved != null &&
        state.pickerEntries.any((entry) => entry.number == saved.number)) {
      _articleOffset = saved.offset;
      _display(localizations, saved.number, clearSearch: false);
    } else {
      _display(
        localizations,
        state.pickerEntries.firstOrNull?.number ?? state.strongNumber,
        clearSearch: false,
      );
    }
  }

  void rememberArticleOffset(int number, double offset) {
    if (isClosed ||
        !state.hasContent ||
        number != state.strongNumber ||
        !offset.isFinite ||
        offset < 0 ||
        offset == _articleOffset) {
      return;
    }
    _articleOffset = offset;
    _savePlace();
  }

  void _savePlace() {
    final store = _readingStore;
    if (store == null) return;
    unawaited(
      store
          .save((number: state.strongNumber, offset: _articleOffset))
          .catchError((Object error, StackTrace trace) {
            if (!isClosed) addError(error, trace);
          }),
    );
  }

  List<StrongPickerEntry> getPickerEntries() {
    final entries = _contentService.getPickerEntries();
    if (_samePickerEntries(entries, state.pickerEntries)) {
      return state.pickerEntries;
    }

    emit(
      state.copyWith(
        pickerEntries: List<StrongPickerEntry>.unmodifiable(entries),
      ),
    );
    return state.pickerEntries;
  }

  bool showStrongNumber({
    required AppLocalizations localizations,
    required int strongNumber,
    bool clearSearch = false,
  }) {
    final changed = state.strongNumber != strongNumber || state.restoring;
    if (changed) _articleOffset = 0;
    final hasContent = _display(
      localizations,
      strongNumber,
      clearSearch: clearSearch,
    );
    if (hasContent) _savePlace();
    return hasContent;
  }

  bool _display(
    AppLocalizations localizations,
    int strongNumber, {
    required bool clearSearch,
  }) {
    final content = _contentService.buildStrongContent(
      localizations,
      strongNumber,
    );
    emit(
      state.copyWith(
        strongNumber: strongNumber,
        restoring: false,
        markdown: content?.markdown,
        markdownSet: true,
        searchQuery: clearSearch ? '' : null,
      ),
    );
    return content != null;
  }

  bool navigate({
    required AppLocalizations localizations,
    required bool forward,
  }) {
    final nextStrongNumber = _contentService.getNeighborStrongNumber(
      state.strongNumber,
      forward: forward,
    );
    return showStrongNumber(
      localizations: localizations,
      strongNumber: nextStrongNumber,
      clearSearch: true,
    );
  }

  void updateSearchQuery(String query) {
    if (state.searchQuery == query) {
      return;
    }
    emit(state.copyWith(searchQuery: query));
  }

  bool _samePickerEntries(
    List<StrongPickerEntry> a,
    List<StrongPickerEntry> b,
  ) {
    if (identical(a, b)) {
      return true;
    }
    if (a.length != b.length) {
      return false;
    }
    for (var i = 0; i < a.length; i++) {
      if (a[i].number != b[i].number ||
          a[i].word != b[i].word ||
          a[i].description != b[i].description ||
          a[i].searchText != b[i].searchText) {
        return false;
      }
    }
    return true;
  }
}
