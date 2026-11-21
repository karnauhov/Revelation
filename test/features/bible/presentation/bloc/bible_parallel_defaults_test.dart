import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_preferences_store.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../test_harness/fakes/fake_parallel_bible_repository.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late BibleVerseMap map;
  setUpAll(() async => map = await BibleVerseMap.loadFromAssets());
  setUp(() => SharedPreferences.setMockInitialValues({}));

  for (final language in ['en', 'uk', 'es', 'ru']) {
    test(
      'opens only the available translation for $language and remembers the first session',
      () async {
        final repository = FakeParallelBibleRepository(map);
        final cubit = _workspace(repository, language: language);
        addTearDown(cubit.close);
        await cubit.loadInitial();
        expect(_files(cubit), [
          FakeParallelBibleRepository.original,
          if (language == 'en') FakeParallelBibleRepository.english,
          if (language == 'uk') FakeParallelBibleRepository.ukrainian,
        ]);
        expect(repository.savedModuleLists.single, _files(cubit));
        cubit.readerCubitFor('primary').selectLoadedVerse(6);
        await _drain();
        expect(repository.translationQueries, 1);
        for (final pane in cubit.state.paneIds) {
          expect(cubit.readerCubitFor(pane).state.selectedReference?.verse, 6);
        }
      },
    );
  }

  test('a reference overrides stored panes without overwriting them', () async {
    await _store([FakeParallelBibleRepository.english]);
    final repository = FakeParallelBibleRepository(map);
    final link = _workspace(repository, language: 'uk', reference: true);
    await link.loadInitial();
    expect(_files(link), [FakeParallelBibleRepository.english]);
    expect(
      await const SharedPreferencesBiblePreferencesStore()
          .loadLastModuleFiles(),
      [FakeParallelBibleRepository.english],
    );
    expect(repository.savedModuleLists, isEmpty);
    await link.close();
    final normal = _workspace(repository, language: 'uk');
    addTearDown(normal.close);
    await normal.loadInitial();
    expect(_files(normal), [FakeParallelBibleRepository.english]);
  });

  test(
    'three independent places survive a temporary link and a new workspace',
    () async {
      final repository = FakeParallelBibleRepository(map);
      await _store(repository.modules.map((m) => m.fileName).toList());
      final normal = _workspace(repository);
      await normal.loadInitial();
      normal.toggleLinkedNavigation();
      for (var i = 0; i < 3; i++) {
        final id = normal.state.paneIds[i];
        await normal
            .readerCubitFor(id)
            .selectReference(bookId: i + 1, chapter: 2, verse: 4 + i);
        await _drain();
        normal.rememberScroll(id, 10 + i);
      }
      await normal.close();
      final baseline = await const SharedPreferencesBiblePreferencesStore()
          .loadReadingSession();
      expect(baseline!.panes.map((p) => (p.book, p.verse, p.topVerse)), [
        (1, 4, 10),
        (2, 5, 11),
        (3, 6, 12),
      ]);

      final linked = _workspace(
        repository,
        reference: true,
        module: FakeParallelBibleRepository.english,
      );
      await linked.loadInitial();
      expect(linked.state.linkedNavigation, isFalse);
      expect(_files(linked), repository.modules.map((m) => m.fileName));
      for (final id in linked.state.paneIds) {
        final ref = linked.readerCubitFor(id).state.selectedReference!;
        expect((ref.bookId, ref.chapter, ref.verse), (40, 17, 5));
      }
      linked.toggleLinkedNavigation();
      await linked
          .readerCubitFor('primary')
          .selectReference(bookId: 66, chapter: 2, verse: 2);
      await linked.closeReaderPane(linked.state.paneIds.last);
      await linked.close();
      expect(
        await const SharedPreferencesBiblePreferencesStore()
            .loadReadingSession(),
        baseline,
      );
      final restored = _workspace(repository);
      addTearDown(restored.close);
      await restored.loadInitial();
      expect(restored.state.linkedNavigation, isFalse);
      for (var i = 0; i < 3; i++) {
        final id = restored.state.paneIds[i];
        final ref = restored.readerCubitFor(id).state.selectedReference!;
        expect(
          (ref.bookId, ref.chapter, ref.verse, restored.viewportVerseFor(id)),
          (i + 1, 2, 4 + i, 10 + i),
        );
      }
    },
  );

  test(
    'rapid linked navigation keeps the latest reference after a slow parallel load',
    () async {
      final repository = FakeParallelBibleRepository(map);
      final normal = _workspace(repository);
      await normal.loadInitial();
      final gate = Completer<void>();
      repository.chapterGates[FakeParallelBibleRepository.english] =
          gate.future;
      final primary = normal.readerCubitFor('primary');
      await primary.selectReference(bookId: 43, chapter: 1, verse: 2);
      await _drain();
      await primary.selectReference(bookId: 43, chapter: 2, verse: 5);
      await _drain();
      gate.complete();
      await _drain();
      for (final id in normal.state.paneIds) {
        expect(
          normal.readerCubitFor(id).state.selectedReference,
          primary.state.selectedReference,
        );
      }
      await normal.close();
      final saved = await const SharedPreferencesBiblePreferencesStore()
          .loadReadingSession();
      expect(saved!.panes.map((p) => (p.book, p.chapter, p.verse)), [
        (43, 2, 5),
        (43, 2, 5),
      ]);
    },
  );

  test('an explicit module wins over the saved layout', () async {
    await _store([FakeParallelBibleRepository.ukrainian]);
    final cubit = _workspace(
      FakeParallelBibleRepository(map),
      module: FakeParallelBibleRepository.english,
    );
    addTearDown(cubit.close);
    await cubit.loadInitial();
    expect(_files(cubit), [FakeParallelBibleRepository.english]);
  });

  test(
    'closing the translation persists one pane for both menu and reference visits',
    () async {
      final repository = FakeParallelBibleRepository(map);
      final cubit = _workspace(repository);
      await cubit.loadInitial();
      repository.savedModuleLists.clear();
      await cubit.closeReaderPane(cubit.state.paneIds.last);
      expect(repository.savedModuleLists, [
        [FakeParallelBibleRepository.original],
      ]);
      await cubit.close();
      final reopened = _workspace(repository);
      await reopened.loadInitial();
      expect(_files(reopened), [FakeParallelBibleRepository.original]);
      await reopened.close();
      final link = _workspace(repository, reference: true);
      addTearDown(link.close);
      await link.loadInitial();
      expect(_files(link), [FakeParallelBibleRepository.original]);
    },
  );

  test('coalesces concurrent initial loads', () async {
    final gate = Completer<void>();
    final repository = FakeParallelBibleRepository(map)
      ..preferencesGate = gate.future;
    final cubit = _workspace(repository);
    addTearDown(cubit.close);
    final first = cubit.loadInitial();
    final second = cubit.loadInitial();
    gate.complete();
    await Future.wait([first, second]);
    expect(repository.initialFiles, [
      FakeParallelBibleRepository.original,
      FakeParallelBibleRepository.english,
    ]);
  });

  test(
    'a delayed translation follows the latest primary reference without navigating it back',
    () async {
      final gate = Completer<void>();
      final repository = FakeParallelBibleRepository(map);
      repository.chapterGates[FakeParallelBibleRepository.english] =
          gate.future;
      final cubit = _workspace(repository);
      addTearDown(cubit.close);
      final load = cubit.loadInitial();
      await _drain();
      await cubit
          .readerCubitFor('primary')
          .selectReference(bookId: 40, chapter: 18, verse: 6);
      gate.complete();
      await load;
      await _drain();
      for (final pane in cubit.state.paneIds) {
        final reference = cubit.readerCubitFor(pane).state.selectedReference!;
        expect(
          [reference.bookId, reference.chapter, reference.verse],
          [40, 18, 6],
        );
      }
    },
  );

  test(
    'a successful initial retry also opens the default translation',
    () async {
      final repository = FakeParallelBibleRepository(map)
        ..failInitialLoad = true;
      final cubit = _workspace(repository);
      addTearDown(cubit.close);
      await cubit.loadInitial();
      expect(cubit.state.paneIds, hasLength(1));
      repository.failInitialLoad = false;
      await cubit.readerCubitFor('primary').retryInitialLoad();
      await _drain();
      expect(_files(cubit), [
        FakeParallelBibleRepository.original,
        FakeParallelBibleRepository.english,
      ]);
      expect(repository.savedModuleLists.last, _files(cubit));
    },
  );

  test(
    'closing during a module switch prevents late preference writes',
    () async {
      await _store([FakeParallelBibleRepository.original]);
      final repository = FakeParallelBibleRepository(map);
      final cubit = _workspace(repository);
      await cubit.loadInitial();
      repository.savedModuleLists.clear();
      final gate = Completer<void>();
      repository.chapterGates[FakeParallelBibleRepository.english] =
          gate.future;
      final load = cubit
          .readerCubitFor('primary')
          .selectModule(repository.modules[1]);
      await _drain();
      await cubit.close();
      gate.complete();
      await load;
      expect(repository.savedModuleLists, isEmpty);
      expect(repository.singleModuleSaves, 0);
    },
  );

  test(
    'a failed preference write does not block the next user change',
    () async {
      final repository = FakeParallelBibleRepository(map);
      final cubit = _workspace(repository);
      addTearDown(cubit.close);
      await cubit.loadInitial();
      repository.savedModuleLists.clear();
      repository.beforeSave = (_) async =>
          throw StateError('Synthetic write failure');
      await cubit
          .readerCubitFor('primary')
          .selectModule(repository.modules.last);
      await _drain();
      repository.beforeSave = null;
      await cubit.closeReaderPane(cubit.state.paneIds.last);
      expect(repository.savedModuleLists, hasLength(2));
      expect(
        await const SharedPreferencesBiblePreferencesStore()
            .loadLastModuleFiles(),
        [FakeParallelBibleRepository.ukrainian],
      );
    },
  );

  for (final phase in ['preferences', 'translation', 'reader']) {
    test(
      'close before $phase completes never creates panes or writes preferences',
      () async {
        final gate = Completer<void>();
        final repository = FakeParallelBibleRepository(map);
        switch (phase) {
          case 'preferences':
            repository.preferencesGate = gate.future;
          case 'translation':
            repository.translationGate = gate.future;
          case 'reader':
            repository.initialGate = gate.future;
        }
        final cubit = _workspace(repository);
        final load = cubit.loadInitial();
        await _drain();
        await cubit.close();
        gate.complete();
        await load;
        expect(repository.savedModuleLists, isEmpty);
        expect(repository.initialFiles.length, lessThanOrEqualTo(1));
      },
    );
  }

  test(
    'a manual module change wins over delayed default translation discovery',
    () async {
      final gate = Completer<void>();
      final repository = FakeParallelBibleRepository(map)
        ..translationGate = gate.future;
      final cubit = _workspace(repository);
      addTearDown(cubit.close);
      final load = cubit.loadInitial();
      await _drain();
      await cubit
          .readerCubitFor('primary')
          .selectModule(repository.modules.last);
      await _drain();
      gate.complete();
      await load;
      expect(_files(cubit), [FakeParallelBibleRepository.ukrainian]);
      expect(repository.savedModuleLists, [
        [FakeParallelBibleRepository.ukrainian],
      ]);
    },
  );

  test(
    'latest module switch wins without stale or per-reader preference writes',
    () async {
      await _store([FakeParallelBibleRepository.original]);
      final repository = FakeParallelBibleRepository(map);
      final cubit = _workspace(repository);
      addTearDown(cubit.close);
      await cubit.loadInitial();
      repository.savedModuleLists.clear();
      final gate = Completer<void>();
      repository.chapterGates[FakeParallelBibleRepository.english] =
          gate.future;
      final reader = cubit.readerCubitFor('primary');
      final old = reader.selectModule(repository.modules[1]);
      await _drain();
      await reader.selectModule(repository.modules[2]);
      await _drain();
      gate.complete();
      await old;
      expect(_files(cubit), [FakeParallelBibleRepository.ukrainian]);
      expect(repository.singleModuleSaves, 0);
      expect(repository.savedModuleLists, [
        [FakeParallelBibleRepository.ukrainian],
      ]);
    },
  );

  test(
    'serializes rapid layout saves so the final preference is the latest choice',
    () async {
      final repository = FakeParallelBibleRepository(map);
      final cubit = _workspace(repository);
      addTearDown(cubit.close);
      await cubit.loadInitial();
      repository.savedModuleLists.clear();
      final gate = Completer<void>();
      repository.beforeSave = (_) => gate.future;
      await cubit
          .readerCubitFor('primary')
          .selectModule(repository.modules.last);
      await _drain();
      final closing = cubit.closeReaderPane(cubit.state.paneIds.last);
      await _drain();
      expect(repository.savedModuleLists, hasLength(1));
      gate.complete();
      await closing;
      expect(
        await const SharedPreferencesBiblePreferencesStore()
            .loadLastModuleFiles(),
        [FakeParallelBibleRepository.ukrainian],
      );
      expect(repository.savedModuleLists, hasLength(2));
    },
  );
}

BibleWorkspaceCubit _workspace(
  FakeParallelBibleRepository repository, {
  String language = 'en',
  bool reference = false,
  String? module,
}) => BibleWorkspaceCubit(
  repositoryFactory: () => repository,
  languageCode: language,
  initialBookId: 40,
  initialChapter: 17,
  initialVerse: 5,
  initialModuleFile: module,
  isReferenceLink: reference,
  loadingBibleMessage: 'Loading',
  loadingChapterMessage: 'Chapter',
  loadingModuleMessage: 'Module',
  modulesUnavailableMessage: 'Unavailable',
);

List<String?> _files(BibleWorkspaceCubit cubit) => [
  for (final pane in cubit.state.paneIds)
    cubit.readerCubitFor(pane).state.selectedModule?.fileName,
];
Future<void> _store(List<String> files) =>
    const SharedPreferencesBiblePreferencesStore().saveLastModuleFiles(files);
Future<void> _drain() async {
  for (var i = 0; i < 20; i++) {
    await Future<void>.delayed(Duration.zero);
  }
}
