import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/description_request.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';

class DescriptionPanelState {
  const DescriptionPanelState({
    required this.showDescription,
    required this.content,
    required this.currentType,
    required this.currentNumber,
  });

  final bool showDescription;
  final String? content;
  final DescriptionKind currentType;
  final int? currentNumber;

  static const DescriptionPanelState initial = DescriptionPanelState(
    showDescription: true,
    content: null,
    currentType: DescriptionKind.info,
    currentNumber: null,
  );

  DescriptionPanelState withVisibility(bool value) {
    return DescriptionPanelState(
      showDescription: value,
      content: content,
      currentType: currentType,
      currentNumber: currentNumber,
    );
  }

  DescriptionPanelState withContent({
    required String newContent,
    required DescriptionKind newType,
    required int? newNumber,
  }) {
    return DescriptionPanelState(
      showDescription: showDescription,
      content: newContent,
      currentType: newType,
      currentNumber: newNumber,
    );
  }
}

class PrimarySourceDescriptionPanelOrchestrator {
  PrimarySourceDescriptionPanelOrchestrator({
    DescriptionContentService? descriptionService,
  }) : _descriptionService = descriptionService ?? DescriptionContentService();

  final DescriptionContentService _descriptionService;
  DescriptionPanelState _state = DescriptionPanelState.initial;

  DescriptionPanelState get state => _state;

  void toggleDescriptionVisibility() {
    _state = _state.withVisibility(!_state.showDescription);
  }

  void updateDescriptionContent({
    required String content,
    required DescriptionKind type,
    required int? number,
  }) {
    _state = _state.withContent(
      newContent: content,
      newType: type,
      newNumber: number,
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
    if (_state.currentType == DescriptionKind.word) {
      final words = selectedPage?.words;
      final currentIndex = _state.currentNumber;
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

    if (_state.currentType == DescriptionKind.strongNumber) {
      final currentStrongNumber = _state.currentNumber;
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

    if (_state.currentType == DescriptionKind.verse) {
      final verses = selectedPage?.verses;
      final currentIndex = _state.currentNumber;
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
    return _descriptionService.getGreekStrongPickerEntries();
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
}
