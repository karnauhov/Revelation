import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_state.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_state.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';

typedef BibleRepositoryFactory = BibleRepository Function();

class BibleWorkspaceCubit extends Cubit<BibleWorkspaceState> {
  BibleWorkspaceCubit({
    required BibleRepositoryFactory repositoryFactory,
    required String languageCode,
    required this.loadingBibleMessage,
    required this.loadingChapterMessage,
    required this.loadingModuleMessage,
    required this.modulesUnavailableMessage,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) : _repositoryFactory = repositoryFactory,
       _persistenceRepository = repositoryFactory(),
       _languageCode = languageCode,
       _initialBookId = initialBookId,
       _initialChapter = initialChapter,
       _initialVerse = initialVerse,
       _initialModuleFile = initialModuleFile,
       super(const BibleWorkspaceState.initial());

  static const primaryPaneId = 'primary';

  final BibleRepositoryFactory _repositoryFactory;
  final BibleRepository _persistenceRepository;
  final String _languageCode;
  final int _initialBookId;
  final int _initialChapter;
  final int _initialVerse;
  final String? _initialModuleFile;
  final Map<String, BibleReaderCubit> _readerCubits =
      <String, BibleReaderCubit>{};
  final Map<String, StreamSubscription<BibleReaderState>> _subscriptions =
      <String, StreamSubscription<BibleReaderState>>{};
  List<String> _lastSavedModuleFiles = const <String>[];
  int _nextParallelPaneIndex = 2;
  bool _syncingReference = false;

  final String loadingBibleMessage;
  final String loadingChapterMessage;
  final String loadingModuleMessage;
  final String modulesUnavailableMessage;

  Future<void> loadInitial() async {
    if (_readerCubits.containsKey(primaryPaneId)) {
      return;
    }

    final storedModuleFiles = await _persistenceRepository
        .loadLastModuleFiles();
    if (isClosed) {
      return;
    }
    final paneModuleFiles = _initialPaneModuleFiles(storedModuleFiles);
    final paneIds = <String>[];
    for (var index = 0; index < paneModuleFiles.length; index++) {
      paneIds.add(index == 0 ? primaryPaneId : _newParallelPaneId());
    }

    for (var index = 0; index < paneIds.length; index++) {
      final readerCubit = _createReaderCubit(
        initialBookId: _initialBookId,
        initialChapter: _initialChapter,
        initialVerse: _initialVerse,
        initialModuleFile: paneModuleFiles[index],
      );
      _addReaderPane(paneIds[index], readerCubit);
    }
    emit(state.copyWith(paneIds: List<String>.unmodifiable(paneIds)));

    await Future.wait([
      for (final paneId in paneIds) _readerCubits[paneId]!.loadInitial(),
    ]);
    unawaited(_saveOpenModuleFiles());
  }

  List<String?> _initialPaneModuleFiles(List<String> storedModuleFiles) {
    final normalizedStored = storedModuleFiles
        .map((moduleFile) => moduleFile.trim())
        .where((moduleFile) => moduleFile.isNotEmpty)
        .toList(growable: false);
    if (normalizedStored.isEmpty) {
      return <String?>[_initialModuleFile];
    }
    return List<String?>.unmodifiable(
      normalizedStored.take(AppConstants.maxParallelBibleReaders),
    );
  }

  void openParallelReader() {
    if (!state.canOpenParallelReader ||
        state.paneIds.length >= AppConstants.maxParallelBibleReaders) {
      return;
    }

    final sourceState = _readerCubits[primaryPaneId]?.state;
    final sourceReference = sourceState?.selectedReference;
    final readerCubit = _createReaderCubit(
      initialBookId: sourceReference?.bookId ?? _initialBookId,
      initialChapter: sourceReference?.chapter ?? _initialChapter,
      initialVerse: sourceReference?.verse ?? _initialVerse,
      initialModuleFile: sourceState?.selectedModule?.fileName,
    );
    final paneId = _newParallelPaneId();
    _addReaderPane(paneId, readerCubit);
    emit(
      state.copyWith(
        paneIds: List<String>.unmodifiable([...state.paneIds, paneId]),
      ),
    );
    unawaited(_loadParallelReader(readerCubit));
  }

  Future<void> closeReaderPane(String paneId) async {
    if (paneId == primaryPaneId || !_readerCubits.containsKey(paneId)) {
      return;
    }

    final nextPaneIds = state.paneIds
        .where((candidatePaneId) => candidatePaneId != paneId)
        .toList(growable: false);
    final subscription = _subscriptions.remove(paneId);
    final readerCubit = _readerCubits.remove(paneId);
    emit(state.copyWith(paneIds: List<String>.unmodifiable(nextPaneIds)));

    unawaited(subscription?.cancel());
    unawaited(readerCubit?.close());
    await _saveOpenModuleFiles();
  }

  String _newParallelPaneId() {
    return 'parallel_${_nextParallelPaneIndex++}';
  }

  void toggleLinkedNavigation() {
    final nextLinkedNavigation = !state.linkedNavigation;
    emit(state.copyWith(linkedNavigation: nextLinkedNavigation));
    if (nextLinkedNavigation) {
      unawaited(_syncReadersToPrimaryReference());
    }
  }

  BibleReaderCubit readerCubitFor(String paneId) {
    final readerCubit = _readerCubits[paneId];
    if (readerCubit == null) {
      throw StateError('Bible reader pane is not registered: $paneId');
    }
    return readerCubit;
  }

  BibleReaderCubit _createReaderCubit({
    required int initialBookId,
    required int initialChapter,
    required int initialVerse,
    String? initialModuleFile,
  }) {
    return BibleReaderCubit(
      repository: _repositoryFactory(),
      languageCode: _languageCode,
      initialBookId: initialBookId,
      initialChapter: initialChapter,
      initialVerse: initialVerse,
      initialModuleFile: initialModuleFile,
      loadingBibleMessage: loadingBibleMessage,
      loadingChapterMessage: loadingChapterMessage,
      loadingModuleMessage: loadingModuleMessage,
      modulesUnavailableMessage: modulesUnavailableMessage,
    );
  }

  void _addReaderPane(String paneId, BibleReaderCubit readerCubit) {
    _readerCubits[paneId] = readerCubit;
    _subscriptions[paneId] = readerCubit.stream.listen(
      (readerState) => _handleReaderStateChanged(paneId, readerState),
    );
  }

  Future<void> _loadParallelReader(BibleReaderCubit readerCubit) async {
    await readerCubit.loadInitial();
    if (isClosed || !state.linkedNavigation) {
      unawaited(_saveOpenModuleFiles());
      return;
    }
    await _syncReadersToPrimaryReference();
    unawaited(_saveOpenModuleFiles());
  }

  void _handleReaderStateChanged(String paneId, BibleReaderState readerState) {
    if (readerState.selectedModule != null) {
      unawaited(_saveOpenModuleFiles());
    }

    if (!state.hasMultiplePanes ||
        !state.linkedNavigation ||
        _syncingReference ||
        readerState.isBusy) {
      return;
    }

    final reference = readerState.selectedReference;
    if (reference == null) {
      return;
    }
    unawaited(_syncReferenceFrom(paneId, reference));
  }

  Future<void> _syncReadersToPrimaryReference() async {
    final reference = _readerCubits[primaryPaneId]?.state.selectedReference;
    if (reference == null) {
      return;
    }
    await _syncReferenceFrom(primaryPaneId, reference);
  }

  Future<void> _syncReferenceFrom(
    String sourcePaneId,
    BibleVerseReference reference,
  ) async {
    if (_syncingReference) {
      return;
    }

    final targets = <BibleReaderCubit>[
      for (final entry in _readerCubits.entries)
        if (entry.key != sourcePaneId) entry.value,
    ];
    if (targets.isEmpty) {
      return;
    }

    _syncingReference = true;
    try {
      await Future.wait([
        for (final readerCubit in targets)
          readerCubit.selectReference(
            bookId: reference.bookId,
            chapter: reference.chapter,
            verse: reference.verse,
          ),
      ]);
    } finally {
      _syncingReference = false;
    }
  }

  Future<void> _saveOpenModuleFiles() async {
    final moduleFiles = <String>[];
    for (final paneId in state.paneIds) {
      final module = _readerCubits[paneId]?.state.selectedModule;
      if (module != null) {
        moduleFiles.add(module.fileName);
      }
    }
    if (moduleFiles.isEmpty ||
        _sameStringList(moduleFiles, _lastSavedModuleFiles)) {
      return;
    }
    _lastSavedModuleFiles = List<String>.unmodifiable(moduleFiles);
    await _persistenceRepository.saveLastModuleFiles(_lastSavedModuleFiles);
  }

  @override
  Future<void> close() async {
    for (final subscription in _subscriptions.values) {
      await subscription.cancel();
    }
    _subscriptions.clear();
    for (final readerCubit in _readerCubits.values) {
      await readerCubit.close();
    }
    _readerCubits.clear();
    return super.close();
  }
}

bool _sameStringList(List<String> left, List<String> right) {
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
