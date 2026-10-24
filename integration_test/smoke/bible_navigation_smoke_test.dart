import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';
import 'smoke_test_harness.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('Bible smoke: route renders real reader', (tester) async {
    int? openedStrong;
    setDefaultGreekStrongTapHandler((number, context) => openedStrong = number);
    addTearDown(() => setDefaultGreekStrongTapHandler(null));
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
    await tester.tap(find.text('G3004'));
    await tester.pump();
    expect(openedStrong, 3004);

    await tester.tap(find.byKey(const Key('bible_module_dropdown')));
    await pumpAndSettleSmoke(tester);
    await tester.tap(find.text('OH1988').last);
    await pumpAndSettleSmoke(tester);
    expect(find.text('G3004'), findsNothing);
    expect(find.byKey(const Key('bible_verse_comment_5')), findsOneWidget);
    expect(find.byKey(const Key('bible_verse_comment_4')), findsNothing);
    await tester.tap(find.byKey(const Key('bible_verse_comment_5')));
    await pumpAndSettleSmoke(tester);
    expect(find.byKey(const Key('bible_verse_comment_dialog')), findsOneWidget);
    expect(find.text('1 Окрема тестова сноска.'), findsOneWidget);
    await tester.tap(find.text(localizations.close));
    await pumpAndSettleSmoke(tester);
    expect(find.byKey(const Key('bible_verse_comment_dialog')), findsNothing);
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

  final _ukrainian = const BibleModuleInfo(
    fileName: 'bible_ohienko_1988.sqlite',
    code: 'OH1988',
    moduleId: 'ohienko_1988',
    title: 'Synthetic Ukrainian fixture',
    description: 'Test data',
    language: 'uk',
    canon: 'protestant_66',
    versification: 'kjv_protestant',
    license: 'CC0-1.0',
    sourceSummary: 'First-party test fixture',
  );

  @override
  Future<BibleModuleInfo> loadModuleInfo(String fileName) async =>
      fileName == _ukrainian.fileName ? _ukrainian : _module;

  @override
  Future<List<String>> loadLastModuleFiles() async => [];

  @override
  Future<void> saveLastModuleFiles(List<String> files) async {}

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
      modules: [_module, _ukrainian],
      selectedModule: initialModuleFile == _ukrainian.fileName
          ? _ukrainian
          : _module,
      reference: reference,
      verses: _buildChapter(
        map,
        reference.bookId,
        reference.chapter,
        ukrainian: initialModuleFile == _ukrainian.fileName,
      ),
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
      verses: _buildChapter(
        map,
        reference.bookId,
        reference.chapter,
        ukrainian: moduleFile == _ukrainian.fileName,
      ),
    );
  }

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {}

  List<BibleChapterVerse> _buildChapter(
    BibleVerseMap map,
    int bookId,
    int chapter, {
    required bool ukrainian,
  }) {
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
          text: ukrainian
              ? 'Тестовий вірш $verse'
              : verse == 5
              ? 'λέγει G3004 αὐτῷ G846'
              : 'verse $verse G1722',
          comment: ukrainian && verse == 5 ? '1 Окрема тестова сноска.' : '',
        ),
    ];
  }
}
