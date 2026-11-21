import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/features/settings/settings.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_dictionary_dialog.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';
import 'package:revelation/main.dart' as app;
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../test/test_harness/allusion_search_scenario.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'Main menu, global Bible settings, both pagers and both reference dialogs',
    exerciseAllusionSearch,
  );

  testWidgets('OH1988 and the Greek Psalms open from a real allusion result', (
    tester,
  ) async {
    final dispatcher = tester.binding.platformDispatcher;
    dispatcher.defaultRouteNameTestValue = '/allusion_search';
    addTearDown(dispatcher.clearDefaultRouteNameTestValue);
    await GetIt.I.reset();
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    SharedPreferences.setMockInitialValues({});
    final settings = SettingsCubit(SettingsRepository());
    await settings.loadSettings();
    await settings.changeLanguage('uk');
    await settings.changeDefaultBibleModule('bible_ohienko_1988.sqlite');
    Future<void> until(bool Function() check, String reason) async {
      final clock = Stopwatch()..start();
      while (!check() && clock.elapsed < const Duration(seconds: 60)) {
        await tester.pump(const Duration(milliseconds: 30));
        await tester.runAsync(
          () => Future<void>.delayed(const Duration(milliseconds: 15)),
        );
      }
      expect(check(), isTrue, reason: reason);
      await tester.pump();
    }

    Future<void> tap(Finder finder) async {
      await tester.ensureVisible(finder);
      await tester.pumpAndSettle();
      await tester.tap(finder);
      await tester.pump();
    }

    Future<void> select(String key, int value) async {
      await tap(find.byKey(Key(key)));
      await tester.pumpAndSettle();
      final menu = find.byType(Scrollable).last;
      final item = find.descendant(of: menu, matching: find.text('$value'));
      await tester.scrollUntilVisible(item, 140, scrollable: menu);
      await tap(item);
      await tester.pumpAndSettle();
    }

    try {
      await tester.runAsync(() async {
        AppDi.registerBibleVerseMap(await BibleVerseMap.loadFromAssets());
        await DbManagerLexiconDatabaseGateway().initialize('uk');
      });
      setDefaultGreekStrongTapHandler(
        (number, context) => showStrongDictionaryDialog(context, number),
      );
      await app.startApp(
        talker,
        initializeSettingsCubit: (_) async => settings,
      );
      final start = find.byKey(const Key('allusion_search'));
      await until(
        () => start.evaluate().isNotEmpty,
        'The passage controls are available',
      );
      final cubit = AppDi.allusionSearchCubit;
      await select('allusion_chapter', 2);
      await select('allusion_verse', 27);
      expect(
        (
          cubit.state.query.bookId,
          cubit.state.query.chapter,
          cubit.state.query.verse,
        ),
        (66, 2, 27),
      );
      await until(
        () =>
            find.byTooltip('G4464 · вага 1').evaluate().isNotEmpty &&
            find.byTooltip('G3588 · вага 0').evaluate().isNotEmpty,
        'Source words expose their actual Strong identifiers and base weights before search',
      );
      final sourceWords = find.byKey(const Key('allusion_source_words'));
      Finder withinSource(Finder widget) =>
          find.descendant(of: sourceWords, matching: widget);
      expect(find.text('Уся давньогрецька Біблія (LXX + TR)'), findsOneWidget);
      expect(
        withinSource(find.textContaining('11 (вага 36,74)')),
        findsOneWidget,
      );
      await tap(withinSource(find.text('+8')));
      await tester.pumpAndSettle();
      final repeated = withinSource(
        find.byTooltip(
          'Входжень в уривку: 2\nБазова вага: 1\nВага в пошуку: 3,94',
        ),
      );
      expect(
        find.descendant(of: repeated, matching: find.textContaining('G5613')),
        findsOneWidget,
      );
      expect(withinSource(find.textContaining('G3588')), findsNothing);
      cubit.updateQuery(length: 3);
      await until(
        () =>
            withinSource(
              find.textContaining('21 (вага 72,45)'),
            ).evaluate().isNotEmpty &&
            cubit.state.originals != null,
        'The summary describes all three verses before search, even with the text collapsed',
      );
      expect(cubit.state.sourceExpanded, isFalse);
      expect(withinSource(find.text('+18')), findsOneWidget);
      await tap(withinSource(find.text('+18')));
      await tester.pumpAndSettle();
      expect(
        find.descendant(
          of: withinSource(
            find.byTooltip(
              'Входжень в уривку: 2\nБазова вага: 0,15\nВага в пошуку: 0,25',
            ),
          ),
          matching: find.textContaining('G846'),
        ),
        findsOneWidget,
      );
      cubit.updateQuery(length: 1);
      await until(
        () => withinSource(
          find.textContaining('11 (вага 36,74)'),
        ).evaluate().isNotEmpty,
        'Restoring a single verse restores its total',
      );
      await tap(start);
      await until(
        () =>
            cubit.state.results != null &&
            cubit.state.status == AllusionStatus.ready,
        'Expected results for Revelation 2:27',
      );
      final match = cubit.state.visible.first;
      expect(
        (
          match.reference.bookId,
          match.reference.chapter,
          match.reference.verse,
        ),
        (19, 2, 9),
      );
      expect(cubit.state.module?.code, 'OH1988');
      final ranked = cubit.state.matches;
      final zechariah = ranked.firstWhere(
        (m) =>
            m.reference.bookId == 38 &&
            m.reference.chapter == 11 &&
            m.reference.verse == 7,
      );
      final deuteronomy = ranked.firstWhere(
        (m) =>
            m.reference.bookId == 5 &&
            m.reference.chapter == 4 &&
            m.reference.verse == 20,
      );
      expect(zechariah.numbers.length, 3);
      expect(deuteronomy.numbers.length, 4);
      expect(zechariah.score, closeTo(0.33925472, 0.000001));
      expect(deuteronomy.score, closeTo(0.33063262, 0.000001));
      expect(ranked.indexOf(zechariah), lessThan(ranked.indexOf(deuteronomy)));
      expect(find.textContaining('33,93'), findsWidgets);

      expect(cubit.state.texts[match.reference.verseKey], contains('залізним'));
      await tap(
        find.byKey(ValueKey('allusion_result_${match.reference.verseKey}')),
      );
      final dialog = find.byKey(const Key('bible_passage_dialog'));
      final greekWords = find.byKey(const ValueKey('bible_passage_word_G4464'));
      await until(
        () => greekWords.evaluate().isNotEmpty,
        'Expected the Greek staff word in Psalm 2:9',
      );
      expect(
        find.descendant(
          of: dialog,
          matching: find.textContaining('залізним', findRichText: true),
        ),
        findsWidgets,
      );
      expect(
        find.byKey(const ValueKey('bible_passage_word_G2763')),
        findsOneWidget,
      );
      expect(find.byTooltip('G1722'), findsWidgets);
      final pdfBytes = kIsWeb ? null : await _exportPassagePdf(tester, dialog);
      await tap(greekWords.first);
      await until(
        () => find
            .byKey(const Key('strong_dialog_open_page'))
            .evaluate()
            .isNotEmpty,
        'Expected Strong dictionary G4464',
      );
      expect(
        tester
            .widget<StrongDictionaryDialog>(find.byType(StrongDictionaryDialog))
            .initialStrongNumber,
        4464,
      );
      Navigator.of(tester.element(find.byType(StrongDictionaryDialog))).pop();
      await tester.pumpAndSettle();
      expect(dialog, findsOneWidget);
      Navigator.of(tester.element(dialog)).pop();
      await tester.pumpAndSettle();
      expect(cubit.state.visible.first.reference, match.reference);
      await select('allusion_chapter', 1);
      await tap(start);
      await until(
        () =>
            cubit.state.results != null &&
            cubit.state.status == AllusionStatus.ready,
        'Expected results for Revelation 1:1',
      );
      final first = cubit.state.visible.first.reference;
      expect((first.bookId, first.chapter, first.verse), (66, 22, 6));
      expect(cubit.state.pageCount, greaterThan(1));
      final sourceReference = find.byKey(
        const Key('allusion_source_reference'),
      );
      final firstResult = find.byKey(
        ValueKey('allusion_result_${first.verseKey}'),
      );
      const wideWidth = 1920.0;
      await binding.setSurfaceSize(const Size(wideWidth, 800));
      addTearDown(() => binding.setSurfaceSize(null));
      await tester.pumpAndSettle();
      expect(
        tester
            .getRect(find.byKey(const PageStorageKey('allusion_source_scroll')))
            .left,
        0,
      );
      expect(
        tester
            .getRect(
              find.byKey(const PageStorageKey('allusion_results_scroll')),
            )
            .right,
        wideWidth,
      );
      expect(
        tester.getRect(sourceReference).right,
        lessThan(tester.getRect(firstResult).left),
      );
      final sourceTop = tester.getTopLeft(sourceReference).dy;
      await tap(find.byKey(const Key('allusion_next_bottom')));
      await until(
        () => !cubit.state.loadingText && cubit.state.page == 1,
        'Expected the second page',
      );
      expect(tester.getTopLeft(sourceReference).dy, sourceTop);
      expect(
        find.byKey(const Key('allusion_prev_top')).hitTestable(),
        findsOneWidget,
      );
      final previousPage = find.byKey(const Key('allusion_prev_top'));
      await binding.setSurfaceSize(const Size(390, 780));
      await tester.pumpAndSettle();
      expect(
        Scrollable.of(tester.element(sourceReference)),
        same(Scrollable.of(tester.element(previousPage))),
      );
      expect(cubit.state.page, 1);
      await tap(previousPage);
      await until(
        () => !cubit.state.loadingText && cubit.state.page == 0,
        'Expected return to the first page',
      );
      expect(cubit.state.visible.first.reference, first);
      await binding.setSurfaceSize(null);
      await tester.pumpAndSettle();
      await settings.changeDefaultBibleModule('bible_kjv.sqlite');
      await until(
        () =>
            cubit.state.module?.code == 'KJV' &&
            find
                .byKey(const ValueKey('allusion_source_translation_G32'))
                .evaluate()
                .isNotEmpty,
        'The tagged English translation replaces the plain Ukrainian text',
      );
      await tap(find.byKey(ValueKey('allusion_result_${first.verseKey}')));
      final englishAngel = find.byKey(
        const ValueKey('bible_passage_translation_word_G32'),
      );
      await until(
        () => englishAngel.evaluate().isNotEmpty,
        'A matched English word in the passage dialog',
      );
      final englishUnmatched = find.byKey(
        const ValueKey('bible_passage_translation_word_G4103'),
      );
      final angelText = tester.widget<Text>(
        find.descendant(of: englishAngel, matching: find.byType(Text)),
      );
      final faithfulText = tester.widget<Text>(
        find.descendant(of: englishUnmatched, matching: find.byType(Text)),
      );
      expect(angelText.style!.color, isNot(faithfulText.style!.color));
      await tap(englishUnmatched);
      await until(
        () => find.byType(StrongDictionaryDialog).evaluate().isNotEmpty,
        'Unmatched English word also opens its dictionary entry',
      );
      expect(
        tester
            .widget<StrongDictionaryDialog>(find.byType(StrongDictionaryDialog))
            .initialStrongNumber,
        4103,
      );
      expect(tester.takeException(), isNull);
      binding.reportData = {
        'source': 'Rev 2:27',
        'sourceVocabulary': {
          'oneVerse': 11,
          'threeVerses': 21,
          'repeatedTerm': 'G5613',
          'occurrences': 2,
        },
        'firstResult': 'Ps 2:9',
        'translation': 'OH1988',
        'taggedTranslation': cubit.state.module?.code,
        'unmatchedTranslationLink': 4103,
        'weightedScores': {
          'Zech11:7': zechariah.score,
          'Deut4:20': deuteronomy.score,
        },
        'greek': 'LXX_TR',
        'strong': 4464,
        'secondSource': 'Rev 1:1',
        'secondResult': 'Rev 22:6',
        'pages': cubit.state.pageCount,
        'bothPagers': true,
        'layoutWidths': [wideWidth, 390],
        if (pdfBytes != null) 'pdfBytes': pdfBytes,
      };
    } finally {
      setDefaultGreekStrongTapHandler(null);
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
      await DBManager().close();
      await GetIt.I.reset();
    }
  });
}

Future<int> _exportPassagePdf(WidgetTester tester, Finder dialog) async {
  final directory = await Directory.systemTemp.createTemp(
    'revelation_passage_pdf_',
  );
  final previousPaths = PathProviderPlatform.instance;
  PathProviderPlatform.instance = _TestDownloads(directory.path);
  try {
    final button = find.descendant(
      of: dialog,
      matching: find.byKey(const Key('description_markdown_export_pdf_button')),
    );
    await tester.ensureVisible(button);
    await tester.tap(button);
    final elapsed = Stopwatch()..start();
    while (elapsed.elapsed < const Duration(seconds: 60)) {
      await tester.pump(const Duration(milliseconds: 100));
      final files = directory
          .listSync()
          .whereType<File>()
          .where((file) => file.path.endsWith('.pdf'))
          .toList();
      // The PDF footer can be visible before Windows finishes flushing and
      // closing the file. The app confirms the save after the write returns.
      if (files.length == 1 &&
          find.textContaining(files.single.path).evaluate().isNotEmpty) {
        final bytes = files.single.readAsBytesSync();
        if (bytes.length > 1000 &&
            String.fromCharCodes(
              bytes.skip(bytes.length - 12),
            ).trim().endsWith('%%EOF')) {
          expect(String.fromCharCodes(bytes.take(5)), '%PDF-');
          return bytes.length;
        }
      }
      await tester.runAsync(
        () => Future<void>.delayed(const Duration(milliseconds: 20)),
      );
    }
    fail(
      'The passage PDF did not finish saving in the isolated Downloads folder',
    );
  } finally {
    PathProviderPlatform.instance = previousPaths;
    await directory.delete(recursive: true);
  }
}

class _TestDownloads extends PathProviderPlatform {
  _TestDownloads(this.path);
  final String path;
  @override
  Future<String?> getDownloadsPath() async => path;
}
