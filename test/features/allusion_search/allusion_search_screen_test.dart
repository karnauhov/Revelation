@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/features/allusion_search/presentation/screens/allusion_search_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import '../../test_harness/fakes/fake_allusion_repositories.dart';

import '../../test_harness/allusion_search_scenario.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'same Settings screen and card background, global translation, dialogs and return',
    exerciseAllusionSearch,
  );

  testWidgets(
    'wide panes scroll independently and resizing preserves the search and current page',
    (tester) async {
      Future<void> resize(double width) async {
        await tester.binding.setSurfaceSize(Size(width, 600));
        await tester.pumpAndSettle();
      }

      await resize(1040);
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final map = (await tester.runAsync(BibleVerseMap.loadFromAssets))!;
      final repository = FakeAllusionRepository(map, genesisVerses: 25);
      final cubit = AllusionSearchCubit(repository, FakeBibleLibrary());
      addTearDown(cubit.close);
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: AllusionSearchScreen(cubit: cubit),
        ),
      );
      await tester.pumpAndSettle();
      final start = find.byKey(const Key('allusion_search'));
      final book = find.byKey(const Key('allusion_book'));
      final scope = find.byKey(const Key('allusion_scope'));
      final nextBottom = find.byKey(const Key('allusion_next_bottom'));
      final prevTop = find.byKey(const Key('allusion_prev_top'));
      expect(scope.hitTestable(), findsOneWidget);
      expect(
        tester.getRect(scope).top,
        greaterThan(tester.getRect(book).bottom),
      );
      await tester.tap(start);
      await tester.pumpAndSettle();
      final left = tester.getRect(start);
      expect(tester.getRect(prevTop).left, greaterThan(left.right));
      final stateBeforePaging = cubit.state.results;
      await tester.ensureVisible(nextBottom);
      await tester.pumpAndSettle();
      expect(tester.getRect(start), left);
      expect(start.hitTestable(), findsOneWidget);
      await tester.tap(nextBottom);
      await tester.pumpAndSettle();
      expect(prevTop.hitTestable(), findsOneWidget);
      expect(cubit.state.page, 1);
      await resize(1039);
      expect(
        tester.getRect(prevTop).top,
        greaterThan(tester.getRect(scope).bottom),
      );
      expect(
        Scrollable.of(tester.element(book)),
        same(Scrollable.of(tester.element(prevTop))),
      );
      await resize(390);
      expect(find.byKey(const Key('allusion_overflow')), findsOneWidget);
      await resize(1440);
      expect(
        tester.getRect(start).right,
        lessThan(tester.getRect(prevTop).left),
      );
      tester.platformDispatcher.textScaleFactorTestValue = 1.5;
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await tester.pumpAndSettle();
      expect(
        Scrollable.of(tester.element(book)),
        same(Scrollable.of(tester.element(prevTop))),
      );
      await resize(1600);
      expect(
        tester.getRect(start).right,
        lessThan(tester.getRect(prevTop).left),
      );
      expect(cubit.state.results, same(stateBeforePaging));
      expect(cubit.state.page, 1);
      expect(repository.searches, 1);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'form reflows at 320px and keeps all picker controls accessible',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(320, 560));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final map = (await tester.runAsync(BibleVerseMap.loadFromAssets))!;
      final cubit = AllusionSearchCubit(
        FakeAllusionRepository(map),
        FakeBibleLibrary(),
      );
      addTearDown(cubit.close);
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: AllusionSearchScreen(cubit: cubit),
        ),
      );
      await tester.pumpAndSettle();
      expect(
        find.text('The whole Ancient Greek Bible (LXX + TR)'),
        findsOneWidget,
      );
      final vocabulary = find.byKey(const Key('allusion_source_words'));
      expect(
        find.descendant(
          of: vocabulary,
          matching: find.text('Unique search words: 3 (weight 3)'),
        ),
        findsOneWidget,
      );
      final wordTip = find.descendant(
        of: vocabulary,
        matching: find.byTooltip(
          'Occurrences in passage: 1\nBase weight: 1\nSearch weight: 1',
        ),
      );
      expect(
        find.descendant(of: wordTip, matching: find.text('θεός G20')),
        findsOneWidget,
      );
      final menu = find.byType(DrawerButton);
      await tester.tap(menu);
      await tester.pumpAndSettle();
      expect(find.text('Settings'), findsOneWidget);
      Scaffold.of(tester.element(find.byType(Drawer))).closeDrawer();
      await tester.pumpAndSettle();
      for (final key in [
        'allusion_book',
        'allusion_chapter',
        'allusion_verse',
      ]) {
        expect(find.byKey(Key(key)).hitTestable(), findsOneWidget);
      }
      expect(find.byKey(const Key('allusion_scope')), findsNothing);
      await tester.tap(find.byKey(const Key('allusion_overflow')));
      await tester.pumpAndSettle();
      expect(
        find.byKey(const Key('allusion_scope')).hitTestable(),
        findsOneWidget,
      );
      await tester.tap(find.byKey(const Key('allusion_length')));
      await tester.pumpAndSettle();
      await tester.tap(find.text('3 verses').last);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Close'));
      await tester.pumpAndSettle();
      final sourceExpand = find.byKey(const Key('allusion_source_expand'));
      await tester.tap(sourceExpand);
      await tester.pumpAndSettle();
      final lastKey = cubit.state.sourceReferences.last.verseKey;
      expect(find.textContaining('English passage $lastKey'), findsOneWidget);
      await tester.ensureVisible(find.byKey(const Key('allusion_search')));
      await tester.tap(find.byKey(const Key('allusion_search')));
      await tester.pumpAndSettle();
      expect(cubit.state.results, isNotNull);
      expect(tester.takeException(), isNull);
      await tester.binding.setSurfaceSize(const Size(620, 580));
      await tester.pumpAndSettle();
      final length = find.byKey(const Key('allusion_length'));
      await tester.ensureVisible(length);
      expect(length.hitTestable(), findsOneWidget);
      expect(find.byKey(const Key('allusion_scope')), findsNothing);
      await tester.tap(find.byKey(const Key('allusion_overflow')));
      await tester.pumpAndSettle();
      expect(
        find.byKey(const Key('allusion_scope')).hitTestable(),
        findsOneWidget,
      );
      expect(
        find.descendant(of: find.byType(AlertDialog), matching: length),
        findsNothing,
      );
      await tester.tap(find.text('Close'));
      await tester.binding.setSurfaceSize(const Size(900, 580));
      await tester.pumpAndSettle();
      expect(
        find.byKey(const Key('allusion_scope')).hitTestable(),
        findsOneWidget,
      );
      expect(find.byKey(const Key('allusion_overflow')), findsNothing);
    },
  );
}
