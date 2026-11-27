import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/data/repositories/bible_bookmark_store.dart';
import 'package:revelation/features/bible/domain/models/bible_bookmark.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/dialogs/study_text_dialog.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shared_preferences_platform_interface/in_memory_shared_preferences_async.dart';
import 'package:shared_preferences_platform_interface/shared_preferences_async_platform_interface.dart';

import '../../../../../integration_test/support/bible_bookmarks_scenario.dart';
import '../../../../../integration_test/support/fake_parallel_bible_repository.dart';

void main() {
  setUp(() {
    final previous = SharedPreferencesAsyncPlatform.instance;
    SharedPreferencesAsyncPlatform.instance =
        InMemorySharedPreferencesAsync.empty();
    addTearDown(() => SharedPreferencesAsyncPlatform.instance = previous);
  });

  testWidgets('bookmark interactions preserve the correct verse and color', (
    tester,
  ) async {
    await exerciseBibleBookmarks(tester);
  });

  testWidgets('only bookmark rows scroll at narrow width and large dark text', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    await tester.binding.setSurfaceSize(const Size(320, 620));
    tester.binding.platformDispatcher.textScaleFactorTestValue = 1.5;
    addTearDown(
      tester.binding.platformDispatcher.clearTextScaleFactorTestValue,
    );
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final map = (await tester.runAsync(BibleVerseMap.loadFromAssets))!;
    final store = BibleBookmarkStore();
    for (var index = 1; index <= 18; index++) {
      await store.save(
        BibleBookmark(
          id: 'bookmark-$index',
          location: (bookId: 66, chapter: 1, verse: index),
          name: 'Закладка $index',
          color: BibleBookmarkColor.violet,
        ),
      );
    }

    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData.dark(),
        locale: const Locale('ru'),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: BibleScreen(
          bibleRepository: FakeParallelBibleRepository(map),
          initialVerse: 13,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('bible_bookmarks_button')).first);
    await tester.pumpAndSettle();

    final title = find.text('Закладки');
    final label = find.text('Добавить закладку (Откр. 1:13)');
    final titlePosition = tester.getTopLeft(title);
    final addPosition = tester.getTopLeft(label);
    final list = find.byKey(const Key('bible_bookmarks_list'));
    expect(find.text('Закладка 18').hitTestable(), findsOneWidget);
    expect(find.text('Закладка 1').hitTestable(), findsNothing);
    await tester.drag(list, const Offset(0, -260));
    await tester.pumpAndSettle();
    expect(find.text('Закладка 18').hitTestable(), findsNothing);
    expect(tester.getTopLeft(title), titlePosition);
    expect(tester.getTopLeft(label), addPosition);
    expect(tester.takeException(), isNull);

    await tester.tap(label);
    await tester.pumpAndSettle();
    final editor = find.byType(StudyTextDialog).last;
    expect(find.descendant(of: editor, matching: title), findsNothing);
    expect(
      find.descendant(
        of: editor,
        matching: find.text(
          'Revelation хранит закладки только на этом устройстве.',
        ),
      ),
      findsNothing,
    );
    expect(
      tester.widget<TextFormField>(find.byType(TextFormField)).initialValue,
      'Закладка 19',
    );
    expect(tester.takeException(), isNull);
  });
}
