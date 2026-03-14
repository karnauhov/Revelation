import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/description_request.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

class PrimarySourceDescriptionCubit
    extends Cubit<PrimarySourceDescriptionState> {
  PrimarySourceDescriptionCubit({DescriptionContentService? descriptionService})
    : this._(descriptionService ?? DescriptionContentService());

  PrimarySourceDescriptionCubit._(DescriptionContentService descriptionService)
    : _descriptionService = descriptionService,
      super(
        PrimarySourceDescriptionState.initial(
          pickerEntries: descriptionService.getGreekStrongPickerEntries(),
        ),
      );

  final DescriptionContentService _descriptionService;

  void toggleDescriptionVisibility() {
    emit(state.copyWith(showDescription: !state.showDescription));
  }

  void updateDescriptionContent({
    required String content,
    required DescriptionKind type,
    required int? number,
  }) {
    emit(
      state.copyWith(
        content: content,
        contentSet: true,
        currentType: type,
        currentNumber: number,
        currentNumberSet: true,
      ),
    );
  }

  void showCommonInfo(BuildContext context) {
    updateDescriptionContent(
      content: AppLocalizations.of(context)!.click_for_info,
      type: DescriptionKind.info,
      number: null,
    );
  }

  bool navigateSelection(
    BuildContext context, {
    required bool forward,
    required PrimarySource source,
    required model.Page? selectedPage,
  }) {
    if (state.currentType == DescriptionKind.word) {
      final words = selectedPage?.words;
      final currentIndex = state.currentNumber;
      if (words == null ||
          words.isEmpty ||
          currentIndex == null ||
          currentIndex < 0 ||
          currentIndex >= words.length) {
        return false;
      }

      final int nextIndex = forward
          ? (currentIndex + 1) % words.length
          : (currentIndex - 1 + words.length) % words.length;
      return showInfoForWord(
        wordIndex: nextIndex,
        context: context,
        source: source,
        selectedPage: selectedPage,
      );
    }

    if (state.currentType == DescriptionKind.strongNumber) {
      final currentStrongNumber = state.currentNumber;
      if (currentStrongNumber == null) {
        return false;
      }

      final nextStrongNumber = _descriptionService.getNeighborStrongNumber(
        currentStrongNumber,
        forward: forward,
      );
      return showInfoForStrongNumber(
        strongNumber: nextStrongNumber,
        context: context,
      );
    }

    if (state.currentType == DescriptionKind.verse) {
      final verses = selectedPage?.verses;
      final currentIndex = state.currentNumber;
      if (verses == null ||
          verses.isEmpty ||
          currentIndex == null ||
          currentIndex < 0 ||
          currentIndex >= verses.length) {
        return false;
      }

      final int nextIndex = forward
          ? (currentIndex + 1) % verses.length
          : (currentIndex - 1 + verses.length) % verses.length;
      return showInfoForVerse(
        verseIndex: nextIndex,
        context: context,
        source: source,
        selectedPage: selectedPage,
      );
    }

    return false;
  }

  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() {
    final entries = _descriptionService.getGreekStrongPickerEntries();
    if (_samePickerEntries(entries, state.pickerEntries)) {
      return state.pickerEntries;
    }

    emit(
      state.copyWith(
        pickerEntries: List<GreekStrongPickerEntry>.unmodifiable(entries),
      ),
    );
    return state.pickerEntries;
  }

  bool showInfoForStrongNumber({
    required int strongNumber,
    required BuildContext context,
  }) {
    final content = _descriptionService.buildStrongContent(
      context,
      strongNumber,
    );
    if (content == null) {
      return false;
    }

    updateDescriptionContent(
      content: content.markdown,
      type: content.kind,
      number: strongNumber,
    );
    return true;
  }

  bool showInfoForWord({
    required int wordIndex,
    required BuildContext context,
    required PrimarySource source,
    required model.Page? selectedPage,
  }) {
    if (selectedPage == null) {
      return false;
    }

    final content = _descriptionService.buildContent(
      context,
      WordDescriptionRequest(
        sourceId: source.id,
        pageName: selectedPage.name,
        wordIndex: wordIndex,
      ),
      fallbackSource: source,
      fallbackPage: selectedPage,
    );
    if (content == null) {
      return false;
    }

    updateDescriptionContent(
      content: content.markdown,
      type: content.kind,
      number: wordIndex,
    );
    return true;
  }

  bool showInfoForVerse({
    required int verseIndex,
    required BuildContext context,
    required PrimarySource source,
    required model.Page? selectedPage,
  }) {
    if (selectedPage == null ||
        selectedPage.verses.isEmpty ||
        verseIndex < 0 ||
        verseIndex >= selectedPage.verses.length) {
      return false;
    }

    final verse = selectedPage.verses[verseIndex];
    final content = _descriptionService.buildContent(
      context,
      VerseDescriptionRequest(
        sourceId: source.id,
        chapterNumber: verse.chapterNumber,
        verseNumber: verse.verseNumber,
        pageName: selectedPage.name,
        combineAcrossPages: false,
      ),
      fallbackSource: source,
      fallbackPage: selectedPage,
    );
    if (content == null) {
      return false;
    }

    updateDescriptionContent(
      content: content.markdown,
      type: content.kind,
      number: verseIndex,
    );
    return true;
  }

  bool _samePickerEntries(
    List<GreekStrongPickerEntry> a,
    List<GreekStrongPickerEntry> b,
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
