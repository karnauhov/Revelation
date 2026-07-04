import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_state.dart';

class BibleReaderCubit extends Cubit<BibleReaderState> {
  BibleReaderCubit({
    required BibleRepository repository,
    required String languageCode,
    required this.loadingBibleMessage,
    required this.loadingChapterMessage,
    required this.loadingModuleMessage,
    required this.modulesUnavailableMessage,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) : _repository = repository,
       _languageCode = languageCode,
       _initialBookId = initialBookId,
       _initialChapter = initialChapter,
       _initialVerse = initialVerse,
       _initialModuleFile = initialModuleFile,
       super(const BibleReaderState.initial());

  final BibleRepository _repository;
  final String _languageCode;
  final int _initialBookId;
  final int _initialChapter;
  final int _initialVerse;
  final String? _initialModuleFile;
  final LatestRequestGuard _requestGuard = LatestRequestGuard();

  final String loadingBibleMessage;
  final String loadingChapterMessage;
  final String loadingModuleMessage;
  final String modulesUnavailableMessage;

  Future<void> loadInitial() async {
    final token = _requestGuard.start();
    emit(
      state.copyWith(
        status: BibleReaderStatus.initialLoading,
        loadingMessage: loadingBibleMessage,
        loadingMessageSet: true,
        errorMessage: null,
        errorMessageSet: true,
      ),
    );

    try {
      final data = await _repository.loadInitial(
        languageCode: _languageCode,
        initialBookId: _initialBookId,
        initialChapter: _initialChapter,
        initialVerse: _initialVerse,
        initialModuleFile: _initialModuleFile,
      );
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      emit(
        state.copyWith(
          status: BibleReaderStatus.ready,
          verseMap: data.verseMap,
          modules: data.modules,
          selectedModule: data.selectedModule,
          selectedModuleSet: true,
          selectedReference: data.reference,
          selectedReferenceSet: true,
          selectionStartVerse: data.reference.verse,
          selectionStartVerseSet: true,
          selectionEndVerse: data.reference.verse,
          selectionEndVerseSet: true,
          verses: data.verses,
          loadingMessage: null,
          loadingMessageSet: true,
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
          status: BibleReaderStatus.failure,
          loadingMessage: null,
          loadingMessageSet: true,
          errorMessage: _errorMessageFor(error),
          errorMessageSet: true,
        ),
      );
    }
  }

  Future<void> selectModule(BibleModuleInfo module) async {
    final currentReference = state.selectedReference;
    if (currentReference == null ||
        state.selectedModule?.fileName == module.fileName) {
      return;
    }

    final token = _requestGuard.start();
    emit(
      state.copyWith(
        status: BibleReaderStatus.loadingModule,
        selectedModule: module,
        selectedModuleSet: true,
        loadingMessage: loadingModuleMessage,
        loadingMessageSet: true,
        errorMessage: null,
        errorMessageSet: true,
      ),
    );

    try {
      final loadedModule = await _repository.loadModuleInfo(module.fileName);
      final chapterData = await _repository.loadChapter(
        moduleFile: loadedModule.fileName,
        bookId: currentReference.bookId,
        chapter: currentReference.chapter,
        verse: currentReference.verse,
      );
      await _repository.saveLastModuleFile(loadedModule.fileName);
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      final modules = [
        for (final item in state.modules)
          item.fileName == loadedModule.fileName ? loadedModule : item,
      ];
      emit(
        state.copyWith(
          status: BibleReaderStatus.ready,
          modules: List<BibleModuleInfo>.unmodifiable(modules),
          selectedModule: loadedModule,
          selectedModuleSet: true,
          selectedReference: chapterData.reference,
          selectedReferenceSet: true,
          selectionStartVerse: chapterData.reference.verse,
          selectionStartVerseSet: true,
          selectionEndVerse: chapterData.reference.verse,
          selectionEndVerseSet: true,
          verses: chapterData.verses,
          loadingMessage: null,
          loadingMessageSet: true,
        ),
      );
    } catch (error) {
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      emit(
        state.copyWith(
          status: BibleReaderStatus.failure,
          loadingMessage: null,
          loadingMessageSet: true,
          errorMessage: _errorMessageFor(error),
          errorMessageSet: true,
        ),
      );
    }
  }

  Future<void> selectReference({
    required int bookId,
    required int chapter,
    required int verse,
  }) {
    final reference = state.selectedReference;
    if (reference != null &&
        reference.bookId == bookId &&
        reference.chapter == chapter &&
        state.verses.isNotEmpty) {
      selectLoadedVerse(verse);
      return Future<void>.value();
    }

    return _loadReference(
      bookId: bookId,
      chapter: chapter,
      verse: verse,
      loadingStatus: BibleReaderStatus.loadingChapter,
      loadingMessage: loadingChapterMessage,
    );
  }

  Future<void> navigateChapter({required bool forward}) async {
    final map = state.verseMap;
    final reference = state.selectedReference;
    if (map == null || reference == null) {
      return;
    }

    final nextReference = map.adjacentChapterReference(
      bookId: reference.bookId,
      chapter: reference.chapter,
      forward: forward,
    );
    if (nextReference == null) {
      return;
    }

    await _loadReference(
      bookId: nextReference.bookId,
      chapter: nextReference.chapter,
      verse: nextReference.verse,
      loadingStatus: BibleReaderStatus.loadingChapter,
      loadingMessage: loadingChapterMessage,
    );
  }

  void toggleStrongNumbers() {
    emit(state.copyWith(showStrongNumbers: !state.showStrongNumbers));
  }

  void selectLoadedVerse(int verse) {
    final map = state.verseMap;
    final reference = state.selectedReference;
    if (map == null || reference == null) {
      return;
    }
    if (!map.containsReference(
      bookId: reference.bookId,
      chapter: reference.chapter,
      verse: verse,
    )) {
      return;
    }

    final selectedReference = map.referenceFor(
      bookId: reference.bookId,
      chapter: reference.chapter,
      verse: verse,
    );
    if (reference.verse == selectedReference.verse &&
        state.selectionStartVerse == selectedReference.verse &&
        state.selectionEndVerse == selectedReference.verse) {
      return;
    }
    emit(
      state.copyWith(
        selectedReference: selectedReference,
        selectedReferenceSet: true,
        selectionStartVerse: selectedReference.verse,
        selectionStartVerseSet: true,
        selectionEndVerse: selectedReference.verse,
        selectionEndVerseSet: true,
      ),
    );
  }

  void extendSelectionToVerse(int verse) {
    final map = state.verseMap;
    final reference = state.selectedReference;
    if (map == null || reference == null) {
      return;
    }
    if (!map.containsReference(
      bookId: reference.bookId,
      chapter: reference.chapter,
      verse: verse,
    )) {
      return;
    }

    final selectedReference = map.referenceFor(
      bookId: reference.bookId,
      chapter: reference.chapter,
      verse: verse,
    );
    emit(
      state.copyWith(
        selectedReference: selectedReference,
        selectedReferenceSet: true,
        selectionStartVerse: state.selectionStartVerse ?? reference.verse,
        selectionStartVerseSet: true,
        selectionEndVerse: selectedReference.verse,
        selectionEndVerseSet: true,
      ),
    );
  }

  Future<void> _loadReference({
    required int bookId,
    required int chapter,
    required int verse,
    required BibleReaderStatus loadingStatus,
    required String loadingMessage,
  }) async {
    final module = state.selectedModule;
    if (module == null) {
      return;
    }

    final token = _requestGuard.start();
    emit(
      state.copyWith(
        status: loadingStatus,
        loadingMessage: loadingMessage,
        loadingMessageSet: true,
        errorMessage: null,
        errorMessageSet: true,
      ),
    );

    try {
      final chapterData = await _repository.loadChapter(
        moduleFile: module.fileName,
        bookId: bookId,
        chapter: chapter,
        verse: verse,
      );
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      emit(
        state.copyWith(
          status: BibleReaderStatus.ready,
          selectedReference: chapterData.reference,
          selectedReferenceSet: true,
          selectionStartVerse: chapterData.reference.verse,
          selectionStartVerseSet: true,
          selectionEndVerse: chapterData.reference.verse,
          selectionEndVerseSet: true,
          verses: chapterData.verses,
          loadingMessage: null,
          loadingMessageSet: true,
        ),
      );
    } catch (error) {
      if (isClosed || !_requestGuard.isActive(token)) {
        return;
      }
      emit(
        state.copyWith(
          status: BibleReaderStatus.failure,
          loadingMessage: null,
          loadingMessageSet: true,
          errorMessage: _errorMessageFor(error),
          errorMessageSet: true,
        ),
      );
    }
  }

  String _errorMessageFor(Object error) {
    if (error is BibleModulesUnavailableException) {
      return modulesUnavailableMessage;
    }
    return error.toString();
  }

  @override
  Future<void> close() {
    _requestGuard.cancelActive();
    return super.close();
  }
}
