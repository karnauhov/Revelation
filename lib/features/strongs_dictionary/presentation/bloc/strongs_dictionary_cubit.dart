import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_content_service.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strongs_dictionary_state.dart';
import 'package:revelation/l10n/app_localizations.dart';

class StrongsDictionaryCubit extends Cubit<StrongsDictionaryState> {
  StrongsDictionaryCubit({
    required int initialStrongNumber,
    required AppLocalizations localizations,
    StrongsDictionaryContentService? contentService,
  }) : this._(
         contentService ?? StrongsDictionaryContentService(),
         initialStrongNumber: initialStrongNumber,
         localizations: localizations,
       );

  StrongsDictionaryCubit._(
    StrongsDictionaryContentService contentService, {
    required int initialStrongNumber,
    required AppLocalizations localizations,
  }) : _contentService = contentService,
       super(
         StrongsDictionaryState.initial(
           strongNumber: initialStrongNumber,
           pickerEntries: contentService.getPickerEntries(),
         ),
       ) {
    showStrongNumber(
      localizations: localizations,
      strongNumber: initialStrongNumber,
    );
  }

  final StrongsDictionaryContentService _contentService;

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
  }) {
    final content = _contentService.buildStrongContent(
      localizations,
      strongNumber,
    );
    emit(
      state.copyWith(
        strongNumber: strongNumber,
        markdown: content?.markdown,
        markdownSet: true,
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
      if (a[i].number != b[i].number || a[i].word != b[i].word) {
        return false;
      }
    }
    return true;
  }
}
