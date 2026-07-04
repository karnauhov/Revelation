@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('opens toolbar chapter chooser from overflow menu', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(375, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      buildLocalizedTestApp(
        withScaffold: false,
        child: BibleScreen(
          initialBookId: 1,
          initialChapter: 1,
          initialVerse: 1,
          bibleRepository: _ChoiceDialogBibleRepository(),
        ),
      ),
    );
    await _pumpUntilFound(tester, find.byKey(const Key('bible_verse_1')));

    final context = tester.element(find.byType(BibleScreen));
    final localizations = AppLocalizations.of(context)!;
    final workspaceContext = tester.element(
      find.byKey(const Key('bible_reader_pane_primary')),
    );
    final workspaceCubit = workspaceContext.read<BibleWorkspaceCubit>();

    await tester.tap(find.byIcon(Icons.more_vert).last);
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('bible_toolbar_menu_chapter')));
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.byType(AlertDialog), findsOneWidget);
    expect(
      find.descendant(
        of: find.byType(AlertDialog),
        matching: find.text(localizations.bible_chapter),
      ),
      findsOneWidget,
    );
    final chapterTwo = find.descendant(
      of: find.byType(AlertDialog),
      matching: find.text('2'),
    );
    expect(chapterTwo, findsOneWidget);

    await tester.tap(chapterTwo);
    await tester.pumpAndSettle();

    expect(
      workspaceCubit.readerCubitFor('primary').state.selectedReference?.chapter,
      2,
    );
  });
}

Future<void> _pumpUntilFound(WidgetTester tester, Finder finder) async {
  for (var attempt = 0; attempt < 40; attempt++) {
    await tester.pump(const Duration(milliseconds: 50));
    if (finder.evaluate().isNotEmpty) {
      return;
    }
  }
  fail('Widget was not found before pump timeout: $finder');
}

class _ChoiceDialogBibleRepository extends BibleRepository {
  _ChoiceDialogBibleRepository() : super();

  BibleVerseMap? _map;

  static const _module = BibleModuleInfo(
    fileName: 'bible_lxx_tr.sqlite',
    code: 'LXX_TR',
    moduleId: 'lxx_tr',
    title: 'Greek Bible',
    description: 'Greek Bible module',
    language: 'grc',
    canon: 'protestant_66',
    versification: 'kjv_protestant',
    license: 'CC BY 4.0',
    sourceSummary: 'https://example.com/source',
  );

  @override
  Future<List<String>> loadLastModuleFiles() async => const <String>[];

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
    final map = await _loadVerseMap();
    final reference = map.normalizedReference(
      bookId: initialBookId,
      chapter: initialChapter,
      verse: initialVerse,
    );
    return BibleInitialData(
      verseMap: map,
      modules: const [_module],
      selectedModule: _module,
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter),
    );
  }

  @override
  Future<BibleModuleInfo> loadModuleInfo(String moduleFile) async => _module;

  @override
  Future<BibleChapterData> loadChapter({
    required String moduleFile,
    required int bookId,
    required int chapter,
    required int verse,
  }) async {
    final map = await _loadVerseMap();
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

  Future<BibleVerseMap> _loadVerseMap() async {
    return _map ??= await BibleVerseMap.loadFromAssets();
  }

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
