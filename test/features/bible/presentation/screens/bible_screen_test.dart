@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  tearDown(() {
    setDefaultGreekStrongTapHandler(null);
  });

  testWidgets('renders real Bible reader and toggles Strong numbers', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1700, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    int? openedStrongNumber;
    setDefaultGreekStrongTapHandler((strongNumber, context) {
      openedStrongNumber = strongNumber;
    });
    var clipboardText = '';
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(SystemChannels.platform, (methodCall) async {
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
    await _pumpUntilFound(tester, find.text('G1722'));

    final context = tester.element(find.byType(BibleScreen));
    final localizations = AppLocalizations.of(context)!;

    expect(find.byType(BibleScreen), findsOneWidget);
    expect(find.byType(PlannedFeatureScreen), findsNothing);
    expect(find.text(localizations.bible_screen), findsOneWidget);
    expect(find.byKey(const Key('bible_module_dropdown')), findsOneWidget);
    expect(find.byKey(const Key('bible_search_button')), findsOneWidget);
    expect(find.byKey(const Key('bible_book_dropdown')), findsOneWidget);
    expect(find.byKey(const Key('bible_chapter_dropdown')), findsOneWidget);
    expect(find.byKey(const Key('bible_verse_dropdown')), findsOneWidget);
    expect(find.text('G1722'), findsOneWidget);
    expect(find.text(localizations.bible_strong_toggle_label), findsNothing);

    await tester.tap(find.text('G1722'));
    await tester.pump();

    expect(openedStrongNumber, 1722);

    await tester.tap(find.byKey(const Key('bible_module_info_button')));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.byKey(const Key('bible_module_info_dialog')), findsOneWidget);
    expect(find.text(localizations.bible_module_info), findsOneWidget);
    expect(find.text('Greek Bible'), findsOneWidget);
    expect(find.text('Greek Bible module'), findsOneWidget);
    expect(
      find.text('https://example.com/source', findRichText: true),
      findsOneWidget,
    );

    await tester.tap(find.text(localizations.close));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    await tester.tap(find.byKey(const Key('bible_verse_2')));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));
    await tester.longPress(find.byKey(const Key('bible_verse_4')));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));
    await tester.tap(find.byKey(const Key('bible_copy_selection_button')));
    await tester.pump();

    final copiedData = await Clipboard.getData('text/plain');
    expect(copiedData?.text, contains('Genesis 1:2-4'));
    expect(copiedData?.text, contains('2. Verse 2'));
    expect(copiedData?.text, contains('4. Verse 4'));
    expect(copiedData?.text, isNot(contains('G1')));

    await tester.tap(
      find.byKey(const Key('bible_open_parallel_reader_button')),
    );
    await tester.pump();
    await _pumpUntilFound(
      tester,
      find.byKey(const Key('bible_reader_pane_parallel_2')),
    );

    expect(
      find.byKey(const Key('bible_parallel_layout_horizontal')),
      findsOneWidget,
    );
    expect(find.byKey(const Key('bible_reader_pane_primary')), findsOneWidget);
    expect(
      find.byKey(const Key('bible_reader_pane_parallel_2')),
      findsOneWidget,
    );
    expect(
      find.byKey(const Key('bible_linked_navigation_button')),
      findsOneWidget,
    );

    final workspaceContext = tester.element(
      find.byKey(const Key('bible_reader_pane_primary')),
    );
    final workspaceCubit = workspaceContext.read<BibleWorkspaceCubit>();
    final parallelCubit = workspaceCubit.readerCubitFor('parallel_2');

    await tester.tap(
      find.byKey(const Key('bible_open_parallel_reader_button')),
    );
    await tester.pump();
    await _pumpUntilFound(
      tester,
      find.byKey(const Key('bible_reader_pane_parallel_3')),
    );
    await tester.pump();

    expect(workspaceCubit.state.paneIds, [
      'primary',
      'parallel_2',
      'parallel_3',
    ]);
    final openParallelButton = tester.widget<IconButton>(
      find.byKey(const Key('bible_open_parallel_reader_button')),
    );
    expect(openParallelButton.onPressed, isNull);

    await workspaceCubit.closeReaderPane('parallel_3');
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    expect(find.byKey(const Key('bible_reader_pane_parallel_3')), findsNothing);
    expect(workspaceCubit.state.paneIds, ['primary', 'parallel_2']);

    await workspaceCubit
        .readerCubitFor('primary')
        .selectReference(bookId: 1, chapter: 1, verse: 1);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    await parallelCubit.selectModule(parallelCubit.state.modules.last);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));
    expect(workspaceCubit.state.linkedNavigation, isTrue);

    await tester.drag(
      find.descendant(
        of: find.byKey(const Key('bible_reader_pane_primary')),
        matching: find.byKey(const Key('bible_chapter_verses')),
      ),
      const Offset(0, -320),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));
    await tester.pump();

    expect(
      _topVisibleVerse(tester, 'parallel_2'),
      _topVisibleVerse(tester, 'primary'),
    );

    await tester.binding.setSurfaceSize(const Size(700, 900));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    expect(
      find.byKey(const Key('bible_parallel_layout_vertical')),
      findsOneWidget,
    );
    expect(
      _topVisibleVerse(tester, 'parallel_2'),
      _topVisibleVerse(tester, 'primary'),
    );

    await tester.drag(
      find.descendant(
        of: find.byKey(const Key('bible_reader_pane_parallel_2')),
        matching: find.byKey(const Key('bible_chapter_verses')),
      ),
      const Offset(0, -240),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));

    expect(
      _topVisibleVerse(tester, 'primary'),
      _topVisibleVerse(tester, 'parallel_2'),
    );

    await tester.binding.setSurfaceSize(const Size(1700, 900));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    await tester.tap(find.byKey(const Key('bible_next_chapter_button')).first);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    expect(
      workspaceCubit.readerCubitFor('primary').state.selectedReference?.chapter,
      2,
    );
    expect(
      workspaceCubit
          .readerCubitFor('parallel_2')
          .state
          .selectedReference
          ?.chapter,
      2,
    );

    await tester.tap(
      find.byKey(const Key('bible_linked_navigation_button')).first,
    );
    await tester.pump();

    await tester.tap(find.byKey(const Key('bible_next_chapter_button')).first);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    expect(
      workspaceCubit.readerCubitFor('primary').state.selectedReference?.chapter,
      3,
    );
    expect(
      workspaceCubit
          .readerCubitFor('parallel_2')
          .state
          .selectedReference
          ?.chapter,
      2,
    );

    await tester.binding.setSurfaceSize(const Size(700, 900));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    expect(
      find.byKey(const Key('bible_parallel_layout_vertical')),
      findsOneWidget,
    );
    expect(find.byIcon(Icons.more_vert), findsWidgets);

    await tester.tap(find.byIcon(Icons.more_vert).last);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    await tester.tap(
      find.widgetWithText(
        PopupMenuItem<String>,
        localizations.bible_close_parallel_reader,
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    expect(find.byKey(const Key('bible_reader_pane_parallel_2')), findsNothing);
    expect(workspaceCubit.state.paneIds, ['primary']);

    await tester.binding.setSurfaceSize(const Size(1700, 900));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    await tester.tap(find.byKey(const Key('bible_strong_toggle_button')));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 250));

    expect(find.text('G1722'), findsNothing);
    expect(find.text(localizations.bible_strong_toggle_label), findsNothing);
    expect(find.textContaining('ἀρχῇ'), findsOneWidget);
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

int? _topVisibleVerse(WidgetTester tester, String paneId) {
  final pane = find.byKey(Key('bible_reader_pane_$paneId'));
  final scrollView = find.descendant(
    of: pane,
    matching: find.byKey(const Key('bible_chapter_verses')),
  );
  final viewportTop = tester.getTopLeft(scrollView).dy;
  final viewportBottom = tester.getBottomLeft(scrollView).dy;
  for (var verse = 1; verse <= 31; verse++) {
    final verseFinder = find.descendant(
      of: pane,
      matching: find.byKey(Key('bible_verse_$verse')),
    );
    if (verseFinder.evaluate().isEmpty) {
      continue;
    }
    final verseTop = tester.getTopLeft(verseFinder).dy;
    final verseBottom = tester.getBottomLeft(verseFinder).dy;
    if (verseBottom > viewportTop + 1 && verseTop < viewportBottom - 1) {
      return verse;
    }
  }
  return null;
}

class _FakeBibleRepository extends BibleRepository {
  _FakeBibleRepository() : super();

  BibleVerseMap? _map;

  final _modules = const <BibleModuleInfo>[
    BibleModuleInfo(
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
    ),
    BibleModuleInfo(
      fileName: 'bible_alt.sqlite',
      code: 'ALT',
      moduleId: 'alt',
      title: 'Alternative Bible',
      description: 'Alternative Bible module',
      language: 'en',
      canon: 'protestant_66',
      versification: 'kjv_protestant',
      license: 'CC BY 4.0',
      sourceSummary: 'https://example.com/alt',
    ),
  ];
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
    final module = _moduleFor(initialModuleFile) ?? _modules.first;
    return BibleInitialData(
      verseMap: map,
      modules: _modules,
      selectedModule: module,
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter, module),
    );
  }

  @override
  Future<BibleModuleInfo> loadModuleInfo(String moduleFile) async {
    return _moduleFor(moduleFile) ?? _modules.first;
  }

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
    final module = _moduleFor(moduleFile) ?? _modules.first;
    return BibleChapterData(
      reference: reference,
      verses: _buildChapter(map, reference.bookId, reference.chapter, module),
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
    BibleModuleInfo module,
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
          text: _verseText(module, index + 1),
        ),
    ];
  }

  BibleModuleInfo? _moduleFor(String? moduleFile) {
    if (moduleFile == null) {
      return null;
    }
    for (final module in _modules) {
      if (module.fileName == moduleFile) {
        return module;
      }
    }
    return null;
  }

  String _verseText(BibleModuleInfo module, int verse) {
    if (verse == 1) {
      return 'ἐν G1722 ἀρχῇ G746';
    }
    if (module.fileName == 'bible_alt.sqlite') {
      return 'Alternative verse $verse with a deliberately longer reading '
          'that wraps across more lines in the parallel pane G1';
    }
    return 'Verse $verse G1';
  }
}
