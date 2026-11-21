import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/data/repositories/bible_preferences_store.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'fakes/fake_parallel_bible_repository.dart';

Future<void> exerciseParallelBibleReading(
  WidgetTester tester,
  String language,
) async {
  SharedPreferences.setMockInitialValues({});
  final map = (await tester.runAsync(BibleVerseMap.loadFromAssets))!;
  final repository = FakeParallelBibleRepository(map);
  final translation = language == 'uk'
      ? FakeParallelBibleRepository.ukrainian
      : FakeParallelBibleRepository.english;
  var preferred = translation;
  final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => Scaffold(
          body: Column(
            children: [
              TextButton(
                key: const Key('open-bible'),
                onPressed: () => context.push('/bible'),
                child: const Text('Bible'),
              ),
              TextButton(
                key: const Key('open-reference'),
                onPressed: () =>
                    context.push('/bible?book=40&chapter=17&verse=5'),
                child: const Text('Reference'),
              ),
              TextButton(
                key: const Key('open-module-reference'),
                onPressed: () => context.push(
                  '/bible?book=1&chapter=2&verse=3&length=2&module=bible_ohienko_1988.sqlite',
                ),
                child: const Text('Module reference'),
              ),
            ],
          ),
        ),
      ),
      GoRoute(
        path: '/bible',
        builder: (context, state) {
          final args = BibleRouteArgs.tryParse(
            state.extra,
            state.uri.queryParameters,
          );
          return BibleScreen(
            initialBookId: args.initialBookId,
            initialChapter: args.initialChapter,
            initialVerse: args.initialVerse,
            initialVerseCount: args.initialVerseCount,
            initialModuleFile: args.initialModuleFile,
            isReferenceLink: args.isReferenceLink,
            bibleRepository: repository,
            resolveDefaultModule: () async => preferred,
          );
        },
      ),
    ],
  );
  addTearDown(router.dispose);
  await tester.pumpWidget(
    MaterialApp.router(
      locale: Locale(language),
      routerConfig: router,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
    ),
  );
  await tester.pumpAndSettle();
  await tester.tap(find.byKey(const Key('open-bible')));
  await tester.pumpAndSettle();
  var workspace = _workspace(tester);
  expect(_files(workspace), [
    FakeParallelBibleRepository.original,
    translation,
  ]);
  expect(find.text('1. LXX_TR sample 1', findRichText: true), findsOneWidget);
  expect(
    find.text(
      '1. ${language == 'uk' ? 'OH1988' : 'KJV'} sample 1',
      findRichText: true,
    ),
    findsOneWidget,
  );
  expect(repository.savedModuleLists.last, _files(workspace));
  await tester.tap(find.byKey(const Key('bible_linked_navigation_button')));
  await tester.pump();
  final ids = workspace.state.paneIds;
  await workspace
      .readerCubitFor(ids.first)
      .selectReference(bookId: 19, chapter: 119, verse: 4);
  workspace.readerCubitFor(ids.last).selectLoadedVerse(7);
  await tester.pumpAndSettle();
  final chapter = find.descendant(
    of: find.byKey(const Key('bible_reader_pane_primary')),
    matching: find.byKey(const Key('bible_chapter_verses')),
  );
  await tester.drag(chapter, const Offset(0, -160));
  await tester.pumpAndSettle();
  final anchor = workspace.viewportVerseFor(ids.first);
  expect(anchor, isNotNull);
  final before = await const SharedPreferencesBiblePreferencesStore()
      .loadReadingSession();
  await tester.tap(find.byType(BackButton));
  await tester.pumpAndSettle();
  await tester.tap(find.byKey(const Key('open-reference')));
  await tester.pumpAndSettle();
  workspace = _workspace(tester);
  expect(workspace.state.linkedNavigation, isFalse);
  for (final id in workspace.state.paneIds) {
    final ref = workspace.readerCubitFor(id).state.selectedReference!;
    expect((ref.bookId, ref.chapter, ref.verse), (40, 17, 5));
  }
  workspace.readerCubitFor('primary').selectLoadedVerse(9);
  await tester.tap(find.byType(BackButton));
  await tester.pumpAndSettle();
  expect(
    await const SharedPreferencesBiblePreferencesStore().loadReadingSession(),
    before,
  );
  await tester.tap(find.byKey(const Key('open-bible')));
  await tester.pumpAndSettle();
  workspace = _workspace(tester);
  expect(workspace.state.linkedNavigation, isFalse);
  expect(workspace.readerCubitFor(ids.first).state.selectedReference?.verse, 4);
  expect(workspace.readerCubitFor(ids.last).state.selectedReference?.verse, 7);
  expect(workspace.viewportVerseFor(ids.first), anchor);
  final secondary = find.byKey(
    Key('bible_reader_pane_${workspace.state.paneIds.last}'),
  );
  final close = find.descendant(
    of: secondary,
    matching: find.byKey(const Key('bible_close_parallel_reader_button')),
  );
  if (close.evaluate().isNotEmpty) {
    await tester.tap(close);
  } else {
    await tester.tap(
      find.descendant(of: secondary, matching: find.byIcon(Icons.more_vert)),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('bible_toolbar_menu_close_pane')));
  }
  await tester.pumpAndSettle();
  expect(workspace.state.paneIds, hasLength(1));
  expect(
    await const SharedPreferencesBiblePreferencesStore().loadLastModuleFiles(),
    [FakeParallelBibleRepository.original],
  );
  await tester.tap(find.byType(BackButton));
  await tester.pumpAndSettle();
  await tester.tap(find.byKey(const Key('open-bible')));
  await tester.pumpAndSettle();
  expect(_files(_workspace(tester)), [FakeParallelBibleRepository.original]);
  await tester.tap(find.byType(BackButton));
  await tester.pumpAndSettle();
  await tester.tap(find.byKey(const Key('open-reference')));
  await tester.pumpAndSettle();
  workspace = _workspace(tester);
  expect(_files(workspace), [FakeParallelBibleRepository.original]);
  for (final pane in workspace.state.paneIds) {
    final reference = workspace.readerCubitFor(pane).state.selectedReference!;
    expect([reference.bookId, reference.chapter, reference.verse], [40, 17, 5]);
  }
  await tester.tap(find.byType(BackButton));
  await tester.pumpAndSettle();
  preferred = translation == FakeParallelBibleRepository.english
      ? FakeParallelBibleRepository.ukrainian
      : FakeParallelBibleRepository.english;
  await tester.tap(find.byKey(const Key('open-reference')));
  await tester.pumpAndSettle();
  expect(_files(_workspace(tester)), [FakeParallelBibleRepository.original]);
  await tester.tap(find.byType(BackButton));
  await tester.pumpAndSettle();
  await tester.tap(find.byKey(const Key('open-module-reference')));
  await tester.pumpAndSettle();
  expect(_files(_workspace(tester)), [FakeParallelBibleRepository.ukrainian]);
  final selection = _workspace(tester).readerCubitFor('primary').state;
  expect(selection.selectionStartVerse, 3);
  expect(selection.selectionEndVerse, 4);
  for (final paneId in _workspace(tester).state.paneIds) {
    final state = _workspace(tester).readerCubitFor(paneId).state;
    expect(state.selectionStartVerse, 3, reason: paneId);
    expect(state.selectionEndVerse, 4, reason: paneId);
  }
  expect(
    await const SharedPreferencesBiblePreferencesStore().loadLastModuleFiles(),
    [FakeParallelBibleRepository.original],
  );
  expect(repository.savedModuleLists.last, [
    FakeParallelBibleRepository.original,
  ]);
  expect(tester.takeException(), isNull);
  await tester.pumpWidget(const SizedBox.shrink());
  await tester.pumpAndSettle();
}

BibleWorkspaceCubit _workspace(WidgetTester tester) => tester
    .element(find.byKey(const Key('bible_reader_pane_primary')))
    .read<BibleWorkspaceCubit>();
List<String?> _files(BibleWorkspaceCubit cubit) => [
  for (final id in cubit.state.paneIds)
    cubit.readerCubitFor(id).state.selectedModule?.fileName,
];
