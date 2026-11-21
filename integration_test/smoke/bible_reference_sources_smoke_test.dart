import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_attributes_footer.dart';
import 'package:revelation/features/settings/settings.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_dictionary_dialog.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_dictionary_entry_view.dart';
import 'package:revelation/infra/db/runtime/database_runtime.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/main.dart' as app;
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/dialogs/study_text_dialog.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('Content links use the current default Bible on every visit', (
    tester,
  ) async {
    const kjv = 'bible_kjv.sqlite';
    const oh1988 = 'bible_ohienko_1988.sqlite';
    final dispatcher = tester.binding.platformDispatcher;
    dispatcher.defaultRouteNameTestValue = '/topic?file=test_page';
    addTearDown(dispatcher.clearDefaultRouteNameTestValue);
    await GetIt.I.reset();
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    // The test injects startup settings and therefore installs the usual link handler.
    setDefaultGreekStrongTapHandler(
      (number, context) => showStrongDictionaryDialog(context, number),
    );
    addTearDown(() => setDefaultGreekStrongTapHandler(null));
    SharedPreferences.setMockInitialValues({});
    final settings = SettingsCubit(SettingsRepository());
    await settings.loadSettings();
    await settings.changeLanguage('uk');
    await settings.setSoundEnabled(false);
    final results = <String, String>{};

    Future<void> waitFor(bool Function() ready, String description) async {
      final elapsed = Stopwatch()..start();
      while (!ready() && elapsed.elapsed < const Duration(seconds: 40)) {
        await tester.pump(const Duration(milliseconds: 80));
        await tester.runAsync(
          () => Future<void>.delayed(const Duration(milliseconds: 20)),
        );
      }
      expect(ready(), isTrue, reason: description);
      await tester.pump(const Duration(milliseconds: 400));
    }

    Future<void> tapReference(String label, {Finder? within}) async {
      final matches = find.byWidgetPredicate(
        (widget) =>
            widget is RichText && widget.text.toPlainText().contains(label),
      );
      final paragraphs = within == null
          ? matches
          : find.descendant(of: within, matching: matches);
      await waitFor(() => paragraphs.evaluate().isNotEmpty, 'Find link $label');
      final paragraph = paragraphs.last;
      final render = tester.renderObject<RenderParagraph>(paragraph);
      final start = render.text.toPlainText().indexOf(label);
      final rect = render
          .getBoxesForSelection(
            TextSelection(
              baseOffset: start,
              extentOffset: start + label.length,
            ),
          )
          .first
          .toRect();
      final element = tester.element(paragraph);
      // A long Markdown paragraph can be taller than the viewport.
      final scrollable = Scrollable.maybeOf(element);
      if (scrollable != null) {
        final viewport = scrollable.context.findRenderObject() as RenderBox;
        final y = viewport.globalToLocal(render.localToGlobal(rect.center)).dy;
        final position = scrollable.position;
        position.jumpTo(
          (position.pixels + y - viewport.size.height / 2).clamp(
            position.minScrollExtent,
            position.maxScrollExtent,
          ),
        );
        await tester.pump();
      }
      await tester.tapAt(render.localToGlobal(rect.center));
      await tester.pump();
    }

    Future<void> verify(
      String entry,
      String module,
      int book,
      int chapter,
      int verse,
    ) async {
      final preview = find.byKey(const Key('bible_passage_dialog'));
      await waitFor(
        () => preview.evaluate().isNotEmpty,
        '$entry opens a preview',
      );
      final open = find.byKey(const Key('bible_passage_open_reader'));
      await waitFor(
        () =>
            open.evaluate().isNotEmpty &&
            tester.widget<TextButton>(open).onPressed != null,
        'Reader action ready',
      );
      expect(find.byKey(const Key('bible_reader_pane_primary')), findsNothing);
      await tester.tap(open);
      await tester.pump();
      final pane = find.byKey(const Key('bible_reader_pane_primary'));
      await waitFor(() {
        if (pane.evaluate().isEmpty) return false;
        final reader = tester
            .element(pane)
            .read<BibleWorkspaceCubit>()
            .readerCubitFor('primary')
            .state;
        return reader.selectedModule?.fileName == module &&
            reader.selectedReference?.bookId == book &&
            reader.selectedReference?.chapter == chapter &&
            reader.selectedReference?.verse == verse &&
            reader.verses.any(
              (v) => v.reference.verse == verse && v.text.isNotEmpty,
            );
      }, '$entry opens $book/$chapter/$verse in $module');
      results[entry] = '$module $book/$chapter/$verse';
      AppRouter().router.pop();
      await tester.pump(const Duration(milliseconds: 500));
    }

    try {
      await tester.runAsync(() async {
        AppDi.registerBibleVerseMap(await BibleVerseMap.loadFromAssets());
        await DbManagerDatabaseRuntime().initialize('uk');
      });
      await app.startApp(
        talker,
        initializeSettingsCubit: (_) async => settings,
      );
      await tester.pump();
      await tapReference('Одкр 9:11');
      final preview = find.byKey(const Key('bible_passage_dialog'));
      await waitFor(() => preview.evaluate().isNotEmpty, 'Topic preview');
      Navigator.of(tester.element(preview)).pop();
      await waitFor(() => preview.evaluate().isEmpty, 'Dismiss to the topic');
      expect(find.byKey(const Key('bible_reader_pane_primary')), findsNothing);
      await tapReference('Одкр 9:11');
      await verify('topic.auto', oh1988, 66, 9, 11);
      await settings.changeDefaultBibleModule(kjv);
      await tapReference('Гал 4:24');
      await verify('topic.explicitPreference', kjv, 48, 4, 24);

      final router = AppRouter().router;
      final article = find.byType(StrongDictionaryEntryView);
      final dialog = find.byType(StrongDictionaryDialog);
      final store = AppDi.strongDictionaryReadingStore;
      await tapReference('G602');
      await waitFor(
        () => dialog.evaluate().isNotEmpty && article.evaluate().length == 1,
        'Topic opens the Strong preview',
      );
      expect(
        tester.widget<StrongDictionaryEntryView>(article).strongNumber,
        602,
      );
      final header = tester.widget<StudyTextDialog>(
        find.byType(StudyTextDialog),
      );
      expect(header.title, startsWith('G602 · '));
      expect(
        header.subtitle,
        AppLocalizations.of(tester.element(dialog))!.strongs_dictionary_screen,
      );
      expect(header.titleInfo, isNotNull);
      router.pop();
      await waitFor(
        () => dialog.evaluate().isEmpty,
        'Close the preview on the topic',
      );
      expect(await store.load(), isNull);
      await tapReference('G602');
      final openPage = find.byKey(const Key('strong_dialog_open_page'));
      await waitFor(
        () => openPage.hitTestable().evaluate().isNotEmpty,
        'Open dictionary action',
      );
      await tester.tap(openPage);
      await waitFor(
        () =>
            dialog.evaluate().isEmpty &&
            article.evaluate().length == 1 &&
            tester.widget<StrongDictionaryEntryView>(article).strongNumber ==
                602,
        'Topic preview opens full G602',
      );
      expect(await store.load(), (number: 602, offset: 0.0));
      router.pop();
      await waitFor(() => article.evaluate().isEmpty, 'Return to the topic');
      unawaited(router.push('/strongs_dictionary?number=G3056'));
      await tapReference('Ів. 1:1');
      await verify('dictionary.page', kjv, 43, 1, 1);
      await settings.changeDefaultBibleModule(oh1988);
      final navigator = router.routerDelegate.navigatorKey.currentState!;
      unawaited(showStrongDictionaryDialog(navigator.overlay!.context, 3056));
      await tester.pump(const Duration(milliseconds: 400));
      await tapReference('Ів. 1:1');
      await verify('dictionary.dialog', oh1988, 43, 1, 1);
      if (find.byType(StrongDictionaryDialog).evaluate().isNotEmpty) {
        navigator.pop();
        await tester.pump(const Duration(milliseconds: 500));
      }

      // Shipped source attributions are external URLs. Exercise the actual
      // footer with a Bible attribution without changing any published data.
      unawaited(
        showDialog<void>(
          context: navigator.overlay!.context,
          builder: (_) => const AlertDialog(
            content: PrimarySourceAttributesFooter(
              credits: [(text: 'Rev 1:3', url: 'bible:Rev1:3')],
              selectAreaMode: false,
              pipetteMode: false,
              isMobileWeb: false,
            ),
          ),
        ),
      );
      await tester.pump(const Duration(milliseconds: 400));
      await tapReference('Rev 1:3');
      await verify('source.attribution', oh1988, 66, 1, 3);
      navigator.popUntil((route) => route is! PopupRoute);
      await tester.pump(const Duration(milliseconds: 400));
      final dictionaryRoute = ModalRoute.of(tester.element(article));
      await tapReference('G3004', within: article);
      await waitFor(
        () =>
            article.evaluate().length == 1 &&
            tester.widget<StrongDictionaryEntryView>(article).strongNumber ==
                3004,
        'Dictionary cross-reference selects G3004 in place',
      );
      expect(dialog, findsNothing);
      expect(ModalRoute.of(tester.element(article)), same(dictionaryRoute));
      final selectedRow = find
          .byKey(const Key('strong_dictionary_entry_3004'))
          .hitTestable();
      await waitFor(
        () => selectedRow.evaluate().isNotEmpty,
        'Index scrolled to G3004',
      );
      expect(await store.load(), (number: 3004, offset: 0.0));
      final scrollable = find
          .descendant(of: article, matching: find.byType(Scrollable))
          .first;
      double scrollOffset() =>
          tester.state<ScrollableState>(scrollable).position.pixels;
      await tester.drag(scrollable, const Offset(0, -320));
      await tester.pumpAndSettle();
      final offset = scrollOffset();
      expect(offset, greaterThan(0));
      expect(await store.load(), (number: 3004, offset: offset));
      router.pop();
      await waitFor(
        () => article.evaluate().isEmpty,
        'Back returns to the topic',
      );
      results['dictionary.crossReference'] =
          'G3056 -> G3004 in the same dictionary page';
      router.go('/');
      final l10n = AppLocalizations.of(navigator.context)!;
      final menu = find.byTooltip(l10n.menu);
      await waitFor(
        () => menu.hitTestable().evaluate().isNotEmpty,
        'Main menu',
      );
      await tester.tap(menu);
      final dictionaryItem = find
          .text(l10n.strongs_dictionary_screen)
          .hitTestable();
      await waitFor(
        () => dictionaryItem.evaluate().isNotEmpty,
        'Dictionary menu item',
      );
      await tester.tap(dictionaryItem);
      await waitFor(
        () => selectedRow.evaluate().isNotEmpty,
        'Menu restores G3004 in the index',
      );
      expect(
        tester.widget<StrongDictionaryEntryView>(article).strongNumber,
        3004,
      );
      expect(scrollOffset(), closeTo(offset, 0.5));
      results['dictionary.lastVisit'] =
          'G3004 at offset $offset after reopening from the main menu';
      binding.reportData = results;
    } finally {
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
      await DBManager().close();
      await GetIt.I.reset();
    }
  });
}
