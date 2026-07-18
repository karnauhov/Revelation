import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';
import 'smoke_test_harness.dart';

void main() {
  testWidgets('Bible smoke: route renders real reader', (tester) async {
    final repository = _FakeBibleRepository();
    final router = GoRouter(
      initialLocation: '/bible?book=40&chapter=17&verse=5',
      routes: <RouteBase>[
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
              initialModuleFile: args.initialModuleFile,
              bibleRepository: repository,
            );
          },
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(
      MaterialApp.router(
        locale: const Locale('en'),
        routerConfig: router,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
      ),
    );
    await pumpAndSettleSmoke(tester);

    final context = tester.element(find.byType(BibleScreen));
    final localizations = AppLocalizations.of(context)!;

    expect(find.byType(BibleScreen), findsOneWidget);
    expect(find.byType(PlannedFeatureScreen), findsNothing);
    expect(find.text(localizations.bible_screen), findsOneWidget);
    expect(find.byKey(const Key('bible_module_dropdown')), findsOneWidget);
    expect(find.byKey(const Key('bible_chapter_verses')), findsOneWidget);
    expect(find.text('G3004'), findsOneWidget);
  });
}

class _FakeBibleRepository extends BibleRepository {
  _FakeBibleRepository() : super();

  final _module = const BibleModuleInfo(
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

  @override
  Future<BibleInitialData> loadInitial({
    required String languageCode,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) async {
    final map = await BibleVerseMap.loadFromAssets();
    final reference = map.normalizedReference(
      bookId: initialBookId,
      chapter: initialChapter,
      verse: initialVerse,
    );
    return BibleInitialData(
      verseMap: map,
      modules: [_module],
      selectedModule: _module,
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter),
    );
  }

  @override
  Future<BibleChapterData> loadChapter({
    required String moduleFile,
    required int bookId,
    required int chapter,
    required int verse,
  }) async {
    final map = await BibleVerseMap.loadFromAssets();
    final reference = map.normalizedReference(
      bookId: bookId,
      chapter: chapter,
      verse: verse,
    );
    return BibleChapterData(
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter),
    );
  }

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {}

  List<BibleChapterVerse> _buildChapter(
    BibleVerseMap map,
    int bookId,
    int chapter,
  ) {
    return [
      for (
        var verse = 1;
        verse <= map.verseCount(bookId: bookId, chapter: chapter);
        verse++
      )
        BibleChapterVerse(
          reference: map.referenceFor(
            bookId: bookId,
            chapter: chapter,
            verse: verse,
          ),
          text: verse == 5 ? 'λέγει G3004 αὐτῷ G846' : 'verse $verse G1722',
        ),
    ];
  }
}
