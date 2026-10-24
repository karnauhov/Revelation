@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  late BibleVerseMap verseMap;
  setUpAll(() async {
    verseMap = await BibleVerseMap.loadFromAssets();
  });
  for (final language in ['en', 'es', 'uk', 'ru']) {
    testWidgets('retries first module load in place ($language)', (
      tester,
    ) async {
      final repository = _RecoveringRepository(verseMap);
      await tester.pumpWidget(
        MaterialApp(
          locale: Locale(language),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: BibleScreen(bibleRepository: repository),
        ),
      );
      await tester.pumpAndSettle();
      expect(repository.calls, 1);
      final retry = find.byKey(const Key('bible_retry_button'));
      expect(retry, findsOneWidget);
      final l10n = AppLocalizations.of(
        tester.element(find.byType(BibleScreen)),
      )!;
      expect(find.text(l10n.startup_retry), findsOneWidget);
      await tester.tap(retry);
      await tester.pumpAndSettle();
      expect(repository.calls, 2);
      expect(
        find.text('1. Recovered readable verse', findRichText: true),
        findsOneWidget,
      );
      expect(retry, findsNothing);
      expect(find.byType(BibleScreen), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }
}

class _RecoveringRepository extends BibleRepository {
  _RecoveringRepository(this.map);
  final BibleVerseMap map;
  int calls = 0;

  @override
  Future<List<String>> loadLastModuleFiles() async => [];

  @override
  Future<void> saveLastModuleFiles(List<String> moduleFiles) async {}

  @override
  Future<BibleInitialData> loadInitial({
    required String languageCode,
    int initialBookId = 66,
    int initialChapter = 1,
    int initialVerse = 1,
    String? initialModuleFile,
  }) async {
    if (++calls == 1) throw const BibleModulesUnavailableException();
    final reference = map.referenceFor(bookId: 66, chapter: 1, verse: 1);
    const module = BibleModuleInfo(
      fileName: 'bible_test.sqlite',
      code: 'TEST',
      moduleId: 'test',
      title: 'Synthetic module',
      description: '',
      language: 'en',
      canon: '',
      versification: '',
      license: '',
      sourceSummary: '',
    );
    return BibleInitialData(
      verseMap: map,
      modules: [module],
      selectedModule: module,
      reference: reference,
      verses: [
        BibleChapterVerse(
          reference: reference,
          text: 'Recovered readable verse',
        ),
      ],
    );
  }
}
