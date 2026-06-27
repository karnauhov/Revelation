@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('renders real Bible reader and toggles Strong numbers', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        withScaffold: false,
        child: BibleScreen(
          initialBookId: 1,
          initialChapter: 1,
          initialVerse: 1,
          bibleRepository: _FakeBibleRepository(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(BibleScreen));
    final localizations = AppLocalizations.of(context)!;

    expect(find.byType(BibleScreen), findsOneWidget);
    expect(find.byType(PlannedFeatureScreen), findsNothing);
    expect(find.text(localizations.bible_screen), findsOneWidget);
    expect(find.byKey(const Key('bible_module_dropdown')), findsOneWidget);
    expect(find.byKey(const Key('bible_book_dropdown')), findsOneWidget);
    expect(find.byKey(const Key('bible_chapter_dropdown')), findsOneWidget);
    expect(find.byKey(const Key('bible_verse_dropdown')), findsOneWidget);
    expect(find.text('G1722'), findsOneWidget);

    await tester.tap(find.byKey(const Key('bible_strong_toggle_button')));
    await tester.pumpAndSettle();

    expect(find.text('G1722'), findsNothing);
    expect(find.textContaining('ἀρχῇ'), findsOneWidget);
  });
}

class _FakeBibleRepository extends BibleRepository {
  _FakeBibleRepository() : super();

  final _modules = const <BibleModuleInfo>[
    BibleModuleInfo(
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
    ),
  ];

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
      modules: _modules,
      selectedModule: _modules.first,
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
    final verseKeys = map.verseKeysForChapter(bookId: bookId, chapter: chapter);
    return [
      for (var index = 0; index < verseKeys.length; index++)
        BibleChapterVerse(
          reference: map.referenceFor(
            bookId: bookId,
            chapter: chapter,
            verse: index + 1,
          ),
          text: index == 0 ? 'ἐν G1722 ἀρχῇ G746' : 'Verse ${index + 1} G1',
        ),
    ];
  }
}
