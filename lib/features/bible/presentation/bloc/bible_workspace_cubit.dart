import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_reading_session.dart';
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
    int initialVerseCount = 1,
    String? initialModuleFile,
    bool isReferenceLink = false,
    Future<String?> Function()? resolveDefaultModule,
  }) : _repositoryFactory = repositoryFactory,
       _persistenceRepository = repositoryFactory(),
       _languageCode = languageCode,
       _initialBookId = initialBookId,
       _initialChapter = initialChapter,
       _initialVerse = initialVerse,
       _initialVerseCount = initialVerseCount,
       _initialModuleFile = initialModuleFile,
       _isReferenceLink = isReferenceLink,
       _resolveDefaultModule = resolveDefaultModule,
       super(const BibleWorkspaceState.initial());

  static const primaryPaneId = 'primary';

  final BibleRepositoryFactory _repositoryFactory;
  final BibleRepository _persistenceRepository;
  final String _languageCode;
  final int _initialBookId;
  final int _initialChapter;
  final int _initialVerse;
  final int _initialVerseCount;
  final String? _initialModuleFile;
  final bool _isReferenceLink;
  final Future<String?> Function()? _resolveDefaultModule;
  String? _preferredModuleFile;
  final Map<String, BibleReaderCubit> _readerCubits =
      <String, BibleReaderCubit>{};
  final Map<String, StreamSubscription<BibleReaderState>> _subscriptions =
      <String, StreamSubscription<BibleReaderState>>{};
  BibleReadingSession? _lastSession;
  final _viewport = <String, ({int book, int chapter, int verse, int top})>{};
  bool _initializing = true;
  bool get _temporary => _isReferenceLink || _initialModuleFile != null;
  int _nextParallelPaneIndex = 2;
  final _mirroredReferences = <String, BibleVerseReference>{};
  Future<void>? _initialLoad;
  Future<void>? _translationLoad;
  Future<void> _saveQueue = Future<void>.value();
  bool _useDefaultLayout = false;
  bool _defaultTranslationResolved = false;
  bool _closing = false;
  int _layoutRevision = 0;

  final String loadingBibleMessage;
  final String loadingChapterMessage;
  final String loadingModuleMessage;
  final String modulesUnavailableMessage;

  Future<void> loadInitial() => _initialLoad ??= _loadInitial();

  Future<void> _loadInitial() async {
    final session = await _persistenceRepository.loadReadingSession();
    if (isClosed || _closing) return;
    final storedFiles = session == null
        ? await _persistenceRepository.loadLastModuleFiles()
        : [for (final p in session.panes) p.module];
    if (isClosed || _closing) return;
    _lastSession = session;
    final files = storedFiles
        .where((f) => f.trim().isNotEmpty)
        .take(AppConstants.maxParallelBibleReaders)
        .toList();
    _useDefaultLayout = files.isEmpty;
    if (_useDefaultLayout) {
      if (_initialModuleFile == null)
        _preferredModuleFile = await _resolveDefaultModule?.call();
      if (isClosed || _closing) return;
      files.add(
        _initialModuleFile ??
            (_isReferenceLink ? _preferredModuleFile : null) ??
            AppConstants.defaultBibleModuleDB,
      );
    } else if (_initialModuleFile != null &&
        !files.contains(_initialModuleFile)) {
      // Honour a module-specific link for this visit without adding a pane.
      files[0] = _initialModuleFile;
    }
    final paneIds = <String>[];
    for (var i = 0; i < files.length; i++) {
      final id = i == 0 ? primaryPaneId : _newParallelPaneId();
      final place = _temporary ? null : session?.panes[i];
      final reader = _createReaderCubit(
        initialBookId: place?.book ?? _initialBookId,
        initialChapter: place?.chapter ?? _initialChapter,
        initialVerse: place?.verse ?? _initialVerse,
        initialModuleFile: files[i],
        savedPlace: place,
        initialShowStrongNumbers: session?.panes[i].showStrongNumbers,
      );
      if (place != null && place.topVerse != null) {
        _viewport[id] = (
          book: place.book,
          chapter: place.chapter,
          verse: place.verse,
          top: place.topVerse!,
        );
      }
      paneIds.add(id);
      _addReaderPane(id, reader);
    }
    emit(
      state.copyWith(
        paneIds: List.unmodifiable(paneIds),
        linkedNavigation: session?.linkedNavigation ?? true,
      ),
    );
    await Future.wait([
      for (final id in paneIds) _readerCubits[id]!.loadInitial(),
    ]);
    if (isClosed || _closing) return;
    await _ensureDefaultTranslation();
    if (isClosed || _closing) return;
    _initializing = false;
    await _saveSession();
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
    emit(state.copyWith(paneIds: List<String>.unmodifiable(nextPaneIds)));

    _viewport.remove(paneId);
    _mirroredReferences.remove(paneId);
    unawaited(subscription?.cancel());
    unawaited(readerCubit?.close());
    await _saveSession();
  }

  String _newParallelPaneId() {
    return 'parallel_${_nextParallelPaneIndex++}';
  }

  void toggleLinkedNavigation() {
    final nextLinkedNavigation = !state.linkedNavigation;
    _mirroredReferences.clear();
    emit(state.copyWith(linkedNavigation: nextLinkedNavigation));
    if (nextLinkedNavigation) {
      unawaited(_syncReadersToPrimaryReference());
    }
    unawaited(_saveSession());
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
    BiblePanePlace? savedPlace,
    bool? initialShowStrongNumbers,
  }) {
    return BibleReaderCubit(
      repository: _repositoryFactory(),
      languageCode: _languageCode,
      initialBookId: initialBookId,
      initialChapter: initialChapter,
      initialVerse: initialVerse,
      initialVerseCount: _initialVerseCount,
      savedPlace: savedPlace,
      initialShowStrongNumbers: initialShowStrongNumbers,
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
    BibleVerseReference? previousReference;
    _subscriptions[paneId] = readerCubit.stream.listen((readerState) {
      final firstReady =
          previousModuleFile == null &&
          readerState.status == BibleReaderStatus.ready;
      final moved = readerState.selectedReference != previousReference;
      if (readerState.status == BibleReaderStatus.ready) {
        final reference = readerState.selectedReference;
        if (previousReference != null && previousReference != reference) {
          _viewport.remove(paneId);
        }
        previousReference = reference;
        final moduleFile = readerState.selectedModule?.fileName;
        if (previousModuleFile != null && previousModuleFile != moduleFile) {
          _layoutRevision++;
        }
        previousModuleFile = moduleFile;
      }
      _handleReaderStateChanged(
        paneId,
        readerState,
        firstReady: firstReady,
        moved: moved,
      );
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
    final preferred = _preferredModuleFile;
    final primaryFile = primary!.selectedModule!.fileName;
    final translation =
        _isReferenceLink &&
            preferred == primaryFile &&
            primaryFile != AppConstants.defaultBibleModuleDB
        ? AppConstants.defaultBibleModuleDB
        : preferred != null && preferred != primaryFile
        ? preferred
        : await _persistenceRepository.findTranslationModuleFile(
            languageCode: _languageCode,
            modules: primary.modules,
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
    await _saveSession();
  }

  Future<void> _loadParallelReader(BibleReaderCubit readerCubit) async {
    await readerCubit.loadInitial();
    if (isClosed || _closing || !state.linkedNavigation) {
      unawaited(_saveSession());
      return;
    }
    await _syncReadersToPrimaryReference();
    unawaited(_saveSession());
  }

  void _handleReaderStateChanged(
    String paneId,
    BibleReaderState readerState, {
    required bool firstReady,
    required bool moved,
  }) {
    if (isClosed || _closing) {
      return;
    }
    if (paneId == primaryPaneId &&
        readerState.status == BibleReaderStatus.ready) {
      unawaited(_ensureDefaultTranslation());
    }
    // A newly opened pane catches up to the primary when its loader completes.
    final reference = readerState.selectedReference;
    if (moved &&
        (!firstReady || paneId == primaryPaneId) &&
        state.hasMultiplePanes &&
        state.linkedNavigation &&
        !readerState.isBusy &&
        reference != null &&
        _readerCubits[paneId]?.state.selectedReference == reference &&
        _mirroredReferences.remove(paneId) != reference) {
      unawaited(_syncReferenceFrom(paneId, reference));
    }
    unawaited(_saveSession());
  }

  Future<void> _syncReadersToPrimaryReference() async {
    if (isClosed || _closing || !state.linkedNavigation) {
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
    final changes = <Future<void>>[];
    for (final entry in _readerCubits.entries) {
      if (entry.key == sourcePaneId) continue;
      final reader = entry.value;
      if (reader.state.selectedModule == null ||
          _mirroredReferences[entry.key] == reference)
        continue;
      if (!reader.state.isBusy && reader.state.selectedReference == reference)
        continue;
      _mirroredReferences[entry.key] = reference;
      changes.add(
        reader.selectReference(
          bookId: reference.bookId,
          chapter: reference.chapter,
          verse: reference.verse,
        ),
      );
    }
    await Future.wait(changes);
  }

  int? viewportVerseFor(String paneId) {
    final ref = _readerCubits[paneId]?.state.selectedReference;
    final anchor = _viewport[paneId];
    return ref != null &&
            anchor != null &&
            anchor.book == ref.bookId &&
            anchor.chapter == ref.chapter &&
            anchor.verse == ref.verse
        ? anchor.top
        : null;
  }

  void rememberScroll(String paneId, int verse) {
    if (_closing || isClosed) return;
    final ids = state.linkedNavigation ? state.paneIds : [paneId];
    for (final id in ids) {
      final ref = _readerCubits[id]?.state.selectedReference;
      if (ref != null)
        _viewport[id] = (
          book: ref.bookId,
          chapter: ref.chapter,
          verse: ref.verse,
          top: verse,
        );
    }
    unawaited(_saveSession());
  }

  Future<void> _saveSession() {
    if (_temporary ||
        _initializing ||
        _closing ||
        isClosed ||
        state.paneIds.isEmpty)
      return _saveQueue;
    final panes = <BiblePanePlace>[];
    for (final id in state.paneIds) {
      final reader = _readerCubits[id]!.state;
      final mirrored = state.linkedNavigation ? _mirroredReferences[id] : null;
      final ref = mirrored ?? reader.selectedReference;
      final module = reader.selectedModule;
      if ((reader.status != BibleReaderStatus.ready && mirrored == null) ||
          ref == null ||
          module == null)
        return _saveQueue;
      final moving = mirrored != null && mirrored != reader.selectedReference;
      panes.add((
        module: module.fileName,
        book: ref.bookId,
        chapter: ref.chapter,
        verse: ref.verse,
        topVerse: moving ? null : viewportVerseFor(id),
        selectionStart: moving
            ? ref.verse
            : reader.selectionStartVerse ?? ref.verse,
        selectionEnd: moving
            ? ref.verse
            : reader.selectionEndVerse ?? ref.verse,
        showStrongNumbers: reader.showStrongNumbers,
      ));
    }
    final next = BibleReadingSession(
      linkedNavigation: state.linkedNavigation,
      panes: panes,
    );
    if (next == _lastSession) return _saveQueue;
    _lastSession = next;
    _saveQueue = _persistenceRepository.saveReadingSession(next).catchError((
      Object error,
      StackTrace trace,
    ) {
      if (_lastSession == next) _lastSession = null;
      if (!isClosed) addError(error, trace);
    });
    return _saveQueue;
  }

  @override
  Future<void> close() async {
    _saveSession();
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
