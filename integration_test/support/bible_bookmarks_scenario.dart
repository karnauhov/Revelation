import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/data/repositories/bible_bookmark_store.dart';
import 'package:revelation/features/bible/domain/models/bible_bookmark.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_bookmark_marker.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/dialogs/study_text_dialog.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'fake_parallel_bible_repository.dart';

Future<void> exerciseBibleBookmarks(WidgetTester tester) async {
  await tester.binding.setSurfaceSize(const Size(1100, 820));
  addTearDown(() => tester.binding.setSurfaceSize(null));
  SharedPreferences.setMockInitialValues({});
  final map = (await tester.runAsync(BibleVerseMap.loadFromAssets))!;
  final repository = FakeParallelBibleRepository(map);
  final store = BibleBookmarkStore();
  expect(await store.load(), isEmpty);

  Future<void> openReader() async {
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('en'),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: BibleScreen(
          bibleRepository: repository,
          resolveDefaultModule: () async => FakeParallelBibleRepository.english,
          initialBookId: 1,
          initialVerse: 3,
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  final primary = find.byKey(const Key('bible_reader_pane_primary'));
  final toolbarButton = find.descendant(
    of: primary,
    matching: find.byKey(const Key('bible_bookmarks_button')),
  );
  Finder verse(Finder pane, int number) => find.descendant(
    of: pane,
    matching: find.byKey(Key('bible_verse_$number')),
  );
  final name = find.byType(TextFormField);
  final dialog = find.byType(StudyTextDialog);

  await openReader();
  final strings = AppLocalizations.of(tester.element(primary))!;
  final workspace = tester.element(primary).read<BibleWorkspaceCubit>();
  expect(workspace.state.paneIds, hasLength(2));
  final secondaryId = workspace.state.paneIds.last;
  final secondary = find.byKey(Key('bible_reader_pane_$secondaryId'));
  expect(secondary, findsOneWidget);
  final sourceVerse = verse(primary, 3);
  final pointer = TestPointer(8, PointerDeviceKind.mouse);
  await tester.sendEventToBinding(
    pointer.addPointer(location: const Offset(1, 1)),
  );
  await tester.sendEventToBinding(
    pointer.hover(_verseNumberCenter(tester, sourceVerse)),
  );
  expect(
    tester.binding.mouseTracker.debugDeviceActiveCursor(pointer.device),
    SystemMouseCursors.basic,
  );
  await tester.sendEventToBinding(pointer.removePointer());

  await _doubleTap(tester, sourceVerse);
  expect(find.text(strings.bible_bookmark_add), findsOneWidget);
  expect(tester.widget<TextFormField>(name).initialValue, 'Bookmark 1');
  await tester.tap(find.text(strings.bible_bookmark_green));
  await tester.tap(find.text(strings.bible_bookmark_save));
  await tester.pumpAndSettle();
  final created = (await store.load()).single;
  expect(created.location, (bookId: 1, chapter: 1, verse: 3));
  expect(created.color, BibleBookmarkColor.green);
  expect(find.byType(BibleBookmarkMarker), findsNWidgets(2));
  expect(find.byTooltip('Bookmark 1'), findsNWidgets(2));

  await _doubleTap(tester, sourceVerse);
  expect(find.text(strings.bible_bookmark_edit), findsOneWidget);
  await tester.enterText(name, 'Bookmark 7');
  await tester.tap(find.text(strings.bible_bookmark_amber));
  await tester.tap(find.text(strings.bible_bookmark_save));
  await tester.pumpAndSettle();

  await tester.tap(toolbarButton);
  await tester.pumpAndSettle();
  final heading = find.text(strings.bible_bookmarks);
  final beforeMove = tester.getCenter(heading);
  await tester.drag(heading, const Offset(90, 70));
  await tester.pumpAndSettle();
  final movement = tester.getCenter(heading) - beforeMove;
  expect(movement.dx, greaterThan(50));
  expect(movement.dy, greaterThan(30));
  expect(find.text(strings.bible_bookmarks_local_storage), findsOneWidget);
  final addForSelection = find.textContaining(
    '${strings.bible_bookmark_add} (Gen. 1:3)',
  );
  expect(addForSelection, findsOneWidget);
  await tester.tap(addForSelection);
  await tester.pumpAndSettle();
  expect(tester.widget<TextFormField>(name).initialValue, 'Bookmark 8');
  expect(
    find.descendant(
      of: dialog.last,
      matching: find.text(strings.bible_bookmarks_local_storage),
    ),
    findsNothing,
  );
  await tester.tap(find.text(strings.cancel));
  await tester.pumpAndSettle();
  await tester.tap(find.text(strings.close));
  await tester.pumpAndSettle();

  if (workspace.state.linkedNavigation) {
    workspace.toggleLinkedNavigation();
    await tester.pumpAndSettle();
  }
  final otherReader = workspace.readerCubitFor(secondaryId);
  await otherReader.selectReference(bookId: 1, chapter: 2, verse: 4);
  await tester.pumpAndSettle();
  final marker = find.byType(BibleBookmarkMarker);
  expect(marker, findsOneWidget);
  final drag = await tester.startGesture(
    tester.getCenter(marker),
    kind: PointerDeviceKind.mouse,
  );
  await drag.moveBy(const Offset(24, 0));
  await tester.pump();
  await drag.moveTo(tester.getCenter(verse(secondary, 4)));
  await tester.pump();
  await drag.up();
  await tester.pumpAndSettle();
  final moved = (await store.load()).single;
  expect(moved.id, created.id);
  expect(moved.location, (bookId: 1, chapter: 2, verse: 4));
  expect(moved.color, BibleBookmarkColor.amber);
  expect(moved.name, 'Bookmark 7');
  expect(find.descendant(of: secondary, matching: marker), findsOneWidget);

  await tester.tap(marker);
  await tester.pumpAndSettle();
  expect(find.text(strings.bible_bookmark_edit), findsOneWidget);
  final book = find.byKey(const Key('bible_bookmark_book'));
  Finder chapter(int bookId) =>
      find.byKey(ValueKey(('bible_bookmark_chapter', bookId)));
  Finder verseField(int bookId, int chapter) =>
      find.byKey(ValueKey(('bible_bookmark_verse', bookId, chapter)));
  expect(tester.getCenter(book).dy, tester.getCenter(chapter(1)).dy);
  expect(
    tester.getCenter(chapter(1)).dy,
    tester.getCenter(verseField(1, 2)).dy,
  );
  await _choose(tester, book, 'Exodus');
  await _choose(tester, chapter(2), '2');
  await _choose(tester, verseField(2, 2), '5');
  await tester.tap(find.text(strings.bible_bookmark_save));
  await tester.pumpAndSettle();
  expect((await store.load()).single.location, (
    bookId: 2,
    chapter: 2,
    verse: 5,
  ));

  await tester.pumpWidget(const SizedBox.shrink());
  await tester.pumpAndSettle();
  await openReader();
  await tester.tap(toolbarButton);
  await tester.pumpAndSettle();
  expect(find.text('Exodus 2:5'), findsOneWidget);
  await tester.tap(find.text('Bookmark 7'));
  await tester.pumpAndSettle();
  final reopened = tester.element(primary).read<BibleWorkspaceCubit>();
  final target = reopened.readerCubitFor('primary').state.selectedReference!;
  expect((target.bookId, target.chapter, target.verse), (2, 2, 5));
  expect(find.descendant(of: primary, matching: marker), findsOneWidget);

  await tester.tap(toolbarButton);
  await tester.pumpAndSettle();
  await tester.tap(find.byTooltip(strings.bible_bookmark_delete));
  await tester.pumpAndSettle();
  final confirm = dialog.last;
  expect(
    find.descendant(of: confirm, matching: find.text('Bookmark 7')),
    findsOneWidget,
  );
  expect(
    find.descendant(of: confirm, matching: find.text('Exodus 2:5')),
    findsOneWidget,
  );
  await tester.tap(find.text(strings.cancel));
  await tester.pumpAndSettle();
  expect((await store.load()).single.id, created.id);
  await tester.tap(find.byTooltip(strings.bible_bookmark_delete));
  await tester.pumpAndSettle();
  final delete = find.descendant(
    of: dialog.last,
    matching: find.widgetWithText(FilledButton, strings.bible_bookmark_delete),
  );
  final deleteButton = tester.widget<FilledButton>(delete);
  final deleteColors = Theme.of(tester.element(delete)).colorScheme;
  expect(deleteButton.style?.backgroundColor?.resolve({}), deleteColors.error);
  expect(
    deleteButton.style?.foregroundColor?.resolve({}),
    deleteColors.onError,
  );
  await tester.tap(delete);
  await tester.pumpAndSettle();
  expect(find.text(strings.bible_bookmarks_empty), findsOneWidget);
  expect(await store.load(), isEmpty);
  expect(tester.takeException(), isNull);
}

Future<void> _doubleTap(WidgetTester tester, Finder finder) async {
  final verseNumber = _verseNumberCenter(tester, finder);
  await tester.tapAt(verseNumber);
  const interval = Duration(milliseconds: 70);
  if (tester.binding is LiveTestWidgetsFlutterBinding) {
    // The second pointer event must arrive even when a browser frame is slow.
    await tester.runAsync(() => Future<void>.delayed(interval));
  } else {
    await tester.pump(interval);
  }
  await tester.tapAt(verseNumber);
  await tester.pumpAndSettle();
}

Offset _verseNumberCenter(WidgetTester tester, Finder finder) {
  final paragraph = tester.renderObject<RenderParagraph>(finder);
  final glyph = paragraph
      .getBoxesForSelection(const TextSelection(baseOffset: 0, extentOffset: 1))
      .first;
  return paragraph.localToGlobal(glyph.toRect().center);
}

Future<void> _choose(WidgetTester tester, Finder field, String value) async {
  await tester.tap(field);
  await tester.pumpAndSettle();
  await tester.tap(find.text(value).hitTestable().last);
  await tester.pumpAndSettle();
}
