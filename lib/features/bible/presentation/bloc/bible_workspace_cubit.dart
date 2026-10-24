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
    bool isReferenceLink = false,
  }) : _repositoryFactory = repositoryFactory,
       _persistenceRepository = repositoryFactory(),
       _languageCode = languageCode,
       _initialBookId = initialBookId,
       _initialChapter = initialChapter,
       _initialVerse = initialVerse,
       _initialModuleFile = initialModuleFile,
       _isReferenceLink = isReferenceLink,
       super(const BibleWorkspaceState.initial());

  static const primaryPaneId = 'primary';

  final BibleRepositoryFactory _repositoryFactory;
  final BibleRepository _persistenceRepository;
  final String _languageCode;
  final int _initialBookId;
  final int _initialChapter;
  final int _initialVerse;
  final String? _initialModuleFile;
  final bool _isReferenceLink;
  final Map<String, BibleReaderCubit> _readerCubits =
      <String, BibleReaderCubit>{};
  final Map<String, StreamSubscription<BibleReaderState>> _subscriptions =
      <String, StreamSubscription<BibleReaderState>>{};
  List<String> _lastSavedModuleFiles = const <String>[];
  int _nextParallelPaneIndex = 2;
  Future<void>? _referenceSync;
  Future<void>? _initialLoad;
  Future<void>? _translationLoad;
  Future<void> _saveQueue = Future<void>.value();
  bool _useDefaultLayout = false;
  bool _defaultTranslationResolved = false;
  bool _pendingSave = false;
  bool _closing = false;
  int _layoutRevision = 0;

  final String loadingBibleMessage;
  final String loadingChapterMessage;
  final String loadingModuleMessage;
  final String modulesUnavailableMessage;

  Future<void> loadInitial() => _initialLoad ??= _loadInitial();

  Future<void> _loadInitial() async {
    final storedModuleFiles = await _persistenceRepository
        .loadLastModuleFiles();
    if (isClosed || _closing) {
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
    if (isClosed || _closing) {
      return;
    }
    await _ensureDefaultTranslation();
  }

  List<String?> _initialPaneModuleFiles(List<String> storedModuleFiles) {
    final normalizedStored = storedModuleFiles
        .map((moduleFile) => moduleFile.trim())
        .where((moduleFile) => moduleFile.isNotEmpty)
        .toList(growable: false);
    _lastSavedModuleFiles = List<String>.unmodifiable(normalizedStored);
    _useDefaultLayout =
        _isReferenceLink ||
        _initialModuleFile != null ||
        normalizedStored.isEmpty;
    if (_useDefaultLayout) {
      return <String?>[_initialModuleFile ?? AppConstants.defaultBibleModuleDB];
    }
    return List<String?>.unmodifiable(
      normalizedStored.take(AppConstants.maxParallelBibleReaders),
    );
  }

  void openParallelReader() {
    if (isClosed ||
        _closing ||
        !state.canOpenParallelReader ||
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
    _layoutRevision++;
    _pendingSave = true;
    _addReaderPane(paneId, readerCubit);
    emit(
      state.copyWith(
        paneIds: List<String>.unmodifiable([...state.paneIds, paneId]),
      ),
    );
    unawaited(_loadParallelReader(readerCubit));
  }

  Future<void> closeReaderPane(String paneId) async {
    if (isClosed ||
        _closing ||
        paneId == primaryPaneId ||
        !_readerCubits.containsKey(paneId)) {
      return;
    }

    final nextPaneIds = state.paneIds
        .where((candidatePaneId) => candidatePaneId != paneId)
        .toList(growable: false);
    final subscription = _subscriptions.remove(paneId);
    final readerCubit = _readerCubits.remove(paneId);
    _layoutRevision++;
    _pendingSave = true;
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
    String? previousModuleFile;
    _subscriptions[paneId] = readerCubit.stream.listen((readerState) {
      final firstReady =
          previousModuleFile == null &&
          readerState.status == BibleReaderStatus.ready;
      if (readerState.status == BibleReaderStatus.ready) {
        final moduleFile = readerState.selectedModule?.fileName;
        if (previousModuleFile != null && previousModuleFile != moduleFile) {
          _layoutRevision++;
          _pendingSave = true;
        }
        previousModuleFile = moduleFile;
      }
      _handleReaderStateChanged(paneId, readerState, firstReady: firstReady);
    });
  }

  Future<void> _ensureDefaultTranslation() {
    return _translationLoad ??= _loadDefaultTranslation().whenComplete(() {
      _translationLoad = null;
    });
  }

  Future<void> _loadDefaultTranslation() async {
    final primary = _readerCubits[primaryPaneId]?.state;
    if (isClosed ||
        _closing ||
        !_useDefaultLayout ||
        _defaultTranslationResolved ||
        _layoutRevision != 0 ||
        state.hasMultiplePanes ||
        primary?.status != BibleReaderStatus.ready) {
      return;
    }
    _defaultTranslationResolved = true;
    final translation = await _persistenceRepository.findTranslationModuleFile(
      languageCode: _languageCode,
      modules: primary!.modules,
      primaryModuleFile: primary.selectedModule!.fileName,
    );
    if (isClosed || _closing || _layoutRevision != 0 || translation == null) {
      return;
    }
    final reference = _readerCubits[primaryPaneId]!.state.selectedReference!;
    final reader = _createReaderCubit(
      initialBookId: reference.bookId,
      initialChapter: reference.chapter,
      initialVerse: reference.verse,
      initialModuleFile: translation,
    );
    final paneId = _newParallelPaneId();
    _addReaderPane(paneId, reader);
    emit(
      state.copyWith(
        paneIds: List<String>.unmodifiable([...state.paneIds, paneId]),
      ),
    );
    await reader.loadInitial();
    if (isClosed || _closing) {
      return;
    }
    if (state.linkedNavigation) {
      await _syncReadersToPrimaryReference();
    }
    await _saveOpenModuleFiles();
  }

  Future<void> _loadParallelReader(BibleReaderCubit readerCubit) async {
    await readerCubit.loadInitial();
    if (isClosed || _closing || !state.linkedNavigation) {
      unawaited(_saveOpenModuleFiles());
      return;
    }
    await _syncReadersToPrimaryReference();
    unawaited(_saveOpenModuleFiles());
  }

  void _handleReaderStateChanged(
    String paneId,
    BibleReaderState readerState, {
    required bool firstReady,
  }) {
    if (isClosed || _closing) {
      return;
    }
    if (paneId == primaryPaneId &&
        readerState.status == BibleReaderStatus.ready) {
      unawaited(_ensureDefaultTranslation());
    }
    if (_pendingSave) {
      unawaited(_saveOpenModuleFiles());
    }

    // A new pane's initial reference may already be stale. Its loader will
    // synchronize it to the current primary, never navigate the primary back.
    if (firstReady && paneId != primaryPaneId) {
      return;
    }

    if (!state.hasMultiplePanes ||
        !state.linkedNavigation ||
        _referenceSync != null ||
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
    await _referenceSync;
    if (isClosed || _closing) {
      return;
    }
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
    if (isClosed || _closing) {
      return;
    }
    final running = _referenceSync;
    if (running != null) {
      await running;
      return;
    }

    final targets = <BibleReaderCubit>[
      for (final entry in _readerCubits.entries)
        if (entry.key != sourcePaneId) entry.value,
    ];
    if (targets.isEmpty) {
      return;
    }

    _referenceSync =
        Future.wait([
          for (final readerCubit in targets)
            readerCubit.selectReference(
              bookId: reference.bookId,
              chapter: reference.chapter,
              verse: reference.verse,
            ),
        ]).then<void>((_) {}).whenComplete(() {
          _referenceSync = null;
        });
    await _referenceSync;
  }

  Future<void> _saveOpenModuleFiles() async {
    if (isClosed || _closing || !_pendingSave) {
      return;
    }
    final moduleFiles = <String>[];
    for (final paneId in state.paneIds) {
      final readerState = _readerCubits[paneId]?.state;
      if (readerState?.status != BibleReaderStatus.ready) {
        return; // Never save a partially loaded parallel layout.
      }
      final module = readerState?.selectedModule;
      if (module != null) {
        moduleFiles.add(module.fileName);
      }
    }
    if (moduleFiles.isEmpty ||
        _sameStringList(moduleFiles, _lastSavedModuleFiles)) {
      _pendingSave = false;
      return;
    }
    _pendingSave = false;
    _lastSavedModuleFiles = List<String>.unmodifiable(moduleFiles);
    final snapshot = _lastSavedModuleFiles;
    _saveQueue = _saveQueue.then((_) async {
      try {
        await _persistenceRepository.saveLastModuleFiles(snapshot);
      } catch (error, stackTrace) {
        if (_sameStringList(_lastSavedModuleFiles, snapshot)) {
          _lastSavedModuleFiles = const [];
          _pendingSave = true;
        }
        // Report through AppBlocObserver without poisoning subsequent saves.
        addError(error, stackTrace);
      }
    });
    await _saveQueue;
  }

  @override
  Future<void> close() async {
    _closing = true;
    _layoutRevision++;
    for (final subscription in _subscriptions.values) {
      await subscription.cancel();
    }
    _subscriptions.clear();
    for (final readerCubit in _readerCubits.values) {
      await readerCubit.close();
    }
    _readerCubits.clear();
    await _saveQueue;
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
