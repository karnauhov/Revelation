@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_search_result.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_search_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets(
    'search dialog searches, pages, copies and returns opened verse',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(900, 700));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      var clipboardText = '';
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(SystemChannels.platform, (
            methodCall,
          ) async {
            switch (methodCall.method) {
              case 'Clipboard.setData':
                final arguments = methodCall.arguments as Map<Object?, Object?>;
                clipboardText = arguments['text']! as String;
                return null;
              case 'Clipboard.getData':
                return <String, Object?>{'text': clipboardText};
            }
            return null;
          });
      addTearDown(() {
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(SystemChannels.platform, null);
      });

      BibleSearchResult? openedResult;
      final repository = _FakeBibleRepository(
        history: const ['logos history'],
        results: _buildResults(25),
      );

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () async {
                  openedResult = await showDialog<BibleSearchResult>(
                    context: context,
                    builder: (_) => BibleSearchDialog(
                      repository: repository,
                      module: _module,
                    ),
                  );
                },
                child: const Text('open'),
              );
            },
          ),
        ),
      );

      await tester.tap(find.text('open'));
      await tester.pumpAndSettle();

      final dialogContext = tester.element(
        find.byKey(const Key('bible_search_dialog')),
      );
      final localizations = AppLocalizations.of(dialogContext)!;

      expect(
        find.text(
          '${localizations.bible_search_dialog_title} '
          '(${_module.displayTitle})',
        ),
        findsOneWidget,
      );

      await tester.tap(find.byKey(const Key('bible_search_query_field')));
      await tester.pumpAndSettle();

      expect(find.text('logos history'), findsOneWidget);

      await tester.tap(find.text('logos history'));
      await tester.pumpAndSettle();
      expect(
        tester
            .widget<TextField>(
              find.byKey(const Key('bible_search_query_field')),
            )
            .controller
            ?.text,
        'logos history',
      );

      await tester.enterText(
        find.byKey(const Key('bible_search_query_field')),
        'logos',
      );
      await tester.tap(find.byKey(const Key('bible_search_submit_button')));
      await tester.pumpAndSettle();

      expect(repository.searchQueries, ['logos']);
      expect(
        find.text(localizations.bible_search_match_count(25, 25)),
        findsOneWidget,
      );
      expect(find.byKey(const Key('bible_search_result_001')), findsOneWidget);
      expect(find.byKey(const Key('bible_search_result_00L')), findsNothing);

      await tester.tap(
        find.byKey(const Key('bible_search_copy_results_button')),
      );
      await tester.pump();
      expect(
        (await Clipboard.getData('text/plain'))?.text,
        contains('Gen 1:1'),
      );
      expect(
        (await Clipboard.getData('text/plain'))?.text,
        isNot(contains('verse 1')),
      );

      await tester.tap(find.byKey(const Key('bible_search_next_page_button')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('bible_search_result_00L')), findsOneWidget);

      await tester.tap(find.byKey(const Key('bible_search_select_00L')));
      await tester.pump();
      await tester.tap(
        find.byKey(const Key('bible_search_copy_results_button')),
      );
      await tester.pump();

      expect(
        (await Clipboard.getData('text/plain'))?.text,
        contains('Gen 1:21\nverse 21 with logos'),
      );

      await tester.tap(find.byKey(const Key('bible_search_action_dropdown')));
      await tester.pumpAndSettle();
      await tester.tap(find.text(localizations.bible_search_action_open).last);
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('bible_search_result_00L')));
      await tester.pumpAndSettle();

      expect(openedResult?.reference.verse, 21);
      expect(find.byKey(const Key('bible_search_dialog')), findsNothing);
    },
  );

  testWidgets('search dialog moves overflowing controls into menu', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(360, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    BibleSearchResult? openedResult;
    final repository = _FakeBibleRepository(results: _buildResults(1));

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: Builder(
          builder: (context) {
            return ElevatedButton(
              onPressed: () async {
                openedResult = await showDialog<BibleSearchResult>(
                  context: context,
                  builder: (_) => BibleSearchDialog(
                    repository: repository,
                    module: _module,
                  ),
                );
              },
              child: const Text('open'),
            );
          },
        ),
      ),
    );

    await tester.tap(find.text('open'));
    await tester.pumpAndSettle();

    final dialogContext = tester.element(
      find.byKey(const Key('bible_search_dialog')),
    );
    final localizations = AppLocalizations.of(dialogContext)!;

    expect(find.byKey(const Key('bible_search_query_field')), findsOneWidget);
    expect(
      find.byKey(const Key('bible_search_overflow_button')),
      findsOneWidget,
    );
    expect(find.byKey(const Key('bible_search_submit_button')), findsNothing);
    expect(find.byKey(const Key('bible_search_action_dropdown')), findsNothing);

    await tester.enterText(
      find.byKey(const Key('bible_search_query_field')),
      'logos',
    );

    await tester.tap(find.byKey(const Key('bible_search_overflow_button')));
    await tester.pumpAndSettle();
    await tester.tap(find.text(localizations.bible_search_action_open).last);
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('bible_search_overflow_button')));
    await tester.pumpAndSettle();
    await tester.tap(find.text(localizations.bible_search_button).last);
    await tester.pumpAndSettle();

    expect(repository.searchQueries, ['logos']);
    expect(find.byKey(const Key('bible_search_result_001')), findsOneWidget);

    await tester.tap(find.byKey(const Key('bible_search_result_001')));
    await tester.pumpAndSettle();

    expect(openedResult?.reference.verse, 1);
    expect(find.byKey(const Key('bible_search_dialog')), findsNothing);
  });
}

const _module = BibleModuleInfo(
  fileName: 'bible_lxx_tr.sqlite',
  code: 'LXX_TR',
  moduleId: 'lxx_tr',
  title: 'Greek Bible',
  description: '',
  language: 'grc',
  canon: 'protestant_66',
  versification: 'kjv_protestant',
  license: '',
  sourceSummary: '',
);

List<BibleSearchResult> _buildResults(int count) {
  return [for (var index = 1; index <= count; index++) _result(index)];
}

BibleSearchResult _result(int index) {
  final text = 'verse $index with logos';
  final matchStart = text.indexOf('logos');
  return BibleSearchResult(
    reference: BibleVerseReference(
      verseKey: index.toRadixString(36).padLeft(3, '0').toUpperCase(),
      bookId: 1,
      chapter: 1,
      verse: index,
    ),
    text: text,
    matches: [BibleTextMatch(start: matchStart, end: matchStart + 5)],
  );
}

class _FakeBibleRepository extends BibleRepository {
  _FakeBibleRepository({
    List<String> history = const <String>[],
    List<BibleSearchResult> results = const <BibleSearchResult>[],
  }) : history = List<String>.of(history),
       results = List<BibleSearchResult>.of(results),
       super();

  List<String> history;
  final List<BibleSearchResult> results;
  final List<String> searchQueries = [];

  @override
  Future<String?> loadLastSearchQuery(String moduleFile) async => null;

  @override
  Future<List<String>> loadSearchHistory() async => history;

  @override
  Future<List<BibleSearchResult>> searchModule({
    required String moduleFile,
    required String query,
  }) async {
    searchQueries.add(query);
    return results;
  }

  @override
  Future<void> saveLastSearchQuery({
    required String moduleFile,
    required String query,
  }) async {}

  @override
  Future<void> rememberSearchQuery(String query) async {
    history = [query, ...history.where((item) => item != query)];
  }
}
