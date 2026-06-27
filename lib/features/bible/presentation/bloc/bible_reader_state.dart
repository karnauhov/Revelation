import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

class BibleReaderState {
  const BibleReaderState({
    required this.status,
    required this.modules,
    required this.verses,
    this.verseMap,
    this.selectedModule,
    this.selectedReference,
    this.selectionStartVerse,
    this.selectionEndVerse,
    this.showStrongNumbers = true,
    this.loadingMessage,
    this.errorMessage,
  });

  const BibleReaderState.initial()
    : status = BibleReaderStatus.initial,
      modules = const <BibleModuleInfo>[],
      verses = const <BibleChapterVerse>[],
      verseMap = null,
      selectedModule = null,
      selectedReference = null,
      selectionStartVerse = null,
      selectionEndVerse = null,
      showStrongNumbers = true,
      loadingMessage = null,
      errorMessage = null;

  final BibleReaderStatus status;
  final BibleVerseMap? verseMap;
  final List<BibleModuleInfo> modules;
  final BibleModuleInfo? selectedModule;
  final BibleVerseReference? selectedReference;
  final int? selectionStartVerse;
  final int? selectionEndVerse;
  final List<BibleChapterVerse> verses;
  final bool showStrongNumbers;
  final String? loadingMessage;
  final String? errorMessage;

  bool get hasSelectedVerses =>
      selectedReference != null &&
      selectedVerseRangeStart != null &&
      selectedVerseRangeEnd != null;

  int? get selectedVerseRangeStart {
    final start = selectionStartVerse;
    final end = selectionEndVerse;
    if (start == null || end == null) {
      return null;
    }
    return start <= end ? start : end;
  }

  int? get selectedVerseRangeEnd {
    final start = selectionStartVerse;
    final end = selectionEndVerse;
    if (start == null || end == null) {
      return null;
    }
    return start <= end ? end : start;
  }

  bool get isBusy =>
      status == BibleReaderStatus.initialLoading ||
      status == BibleReaderStatus.loadingChapter ||
      status == BibleReaderStatus.loadingModule;

  bool get canNavigateBackward {
    final map = verseMap;
    final reference = selectedReference;
    if (map == null || reference == null) {
      return false;
    }
    return map.adjacentChapterReference(
          bookId: reference.bookId,
          chapter: reference.chapter,
          forward: false,
        ) !=
        null;
  }

  bool get canNavigateForward {
    final map = verseMap;
    final reference = selectedReference;
    if (map == null || reference == null) {
      return false;
    }
    return map.adjacentChapterReference(
          bookId: reference.bookId,
          chapter: reference.chapter,
          forward: true,
        ) !=
        null;
  }

  BibleReaderState copyWith({
    BibleReaderStatus? status,
    BibleVerseMap? verseMap,
    List<BibleModuleInfo>? modules,
    BibleModuleInfo? selectedModule,
    bool selectedModuleSet = false,
    BibleVerseReference? selectedReference,
    bool selectedReferenceSet = false,
    int? selectionStartVerse,
    bool selectionStartVerseSet = false,
    int? selectionEndVerse,
    bool selectionEndVerseSet = false,
    List<BibleChapterVerse>? verses,
    bool? showStrongNumbers,
    String? loadingMessage,
    bool loadingMessageSet = false,
    String? errorMessage,
    bool errorMessageSet = false,
  }) {
    return BibleReaderState(
      status: status ?? this.status,
      verseMap: verseMap ?? this.verseMap,
      modules: modules ?? this.modules,
      selectedModule: selectedModuleSet ? selectedModule : this.selectedModule,
      selectedReference: selectedReferenceSet
          ? selectedReference
          : this.selectedReference,
      selectionStartVerse: selectionStartVerseSet
          ? selectionStartVerse
          : this.selectionStartVerse,
      selectionEndVerse: selectionEndVerseSet
          ? selectionEndVerse
          : this.selectionEndVerse,
      verses: verses ?? this.verses,
      showStrongNumbers: showStrongNumbers ?? this.showStrongNumbers,
      loadingMessage: loadingMessageSet ? loadingMessage : this.loadingMessage,
      errorMessage: errorMessageSet ? errorMessage : this.errorMessage,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is BibleReaderState &&
            other.status == status &&
            other.verseMap == verseMap &&
            _listEquals(other.modules, modules) &&
            other.selectedModule == selectedModule &&
            other.selectedReference == selectedReference &&
            other.selectionStartVerse == selectionStartVerse &&
            other.selectionEndVerse == selectionEndVerse &&
            _listEquals(other.verses, verses) &&
            other.showStrongNumbers == showStrongNumbers &&
            other.loadingMessage == loadingMessage &&
            other.errorMessage == errorMessage;
  }

  @override
  int get hashCode => Object.hash(
    status,
    verseMap,
    Object.hashAll(modules),
    selectedModule,
    selectedReference,
    selectionStartVerse,
    selectionEndVerse,
    Object.hashAll(verses),
    showStrongNumbers,
    loadingMessage,
    errorMessage,
  );
}

enum BibleReaderStatus {
  initial,
  initialLoading,
  ready,
  loadingChapter,
  loadingModule,
  failure,
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
