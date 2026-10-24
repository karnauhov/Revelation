@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/intl.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_reader_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late BibleVerseMap verseMap;
  setUpAll(() async {
    verseMap = await BibleVerseMap.loadFromAssets();
  });
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
          bibleRepository: _FakeBibleRepository(verseMap: verseMap),
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
    expect(find.text('Greek Bible module'), findsNothing);
    expect(find.text('protestant_66'), findsNothing);
    expect(find.text('kjv_protestant'), findsNothing);
    await tester.tap(find.byKey(const Key('bible_module_info_details')));
    await tester.pumpAndSettle();
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

  for (final locale in ['en', 'es', 'uk', 'ru']) {
    for (final width in [420.0, 1700.0]) {
      testWidgets('module metadata is readable in $locale at width $width', (
        tester,
      ) async {
        await tester.binding.setSurfaceSize(Size(width, 900));
        addTearDown(() => tester.binding.setSurfaceSize(null));
        await tester.pumpWidget(
          buildLocalizedTestApp(
            locale: Locale(locale),
            withScaffold: false,
            child: BibleScreen(
              initialBookId: 1,
              bibleRepository: _FakeBibleRepository(verseMap: verseMap),
            ),
          ),
        );
        await _pumpUntilFound(tester, find.byKey(const Key('bible_verse_1')));
        final l10n = AppLocalizations.of(
          tester.element(find.byType(BibleScreen)),
        )!;
        Future<void> openInfo() async {
          final button = find.byKey(const Key('bible_module_info_button'));
          if (button.evaluate().isNotEmpty) {
            await tester.tap(button);
          } else {
            await tester.tap(find.byIcon(Icons.more_vert).first);
            await tester.pumpAndSettle();
            await tester.tap(
              find.widgetWithText(
                PopupMenuItem<String>,
                l10n.bible_module_info,
              ),
            );
          }
          await tester.pumpAndSettle();
        }

        String value(String key) => tester
            .widget<Text>(find.byKey(Key('bible_module_info_$key')))
            .data!;
        await openInfo();
        final dialogWidth = tester.getSize(_moduleInfoMaterial()).width;
        expect(dialogWidth, closeTo(width == 420 ? 372 : 560, 0.1));
        expect(value('data_version'), '17');
        expect(value('schema_version'), '3');
        expect(
          value('date'),
          DateFormat.yMMMd(locale).format(DateTime.utc(2026, 7, 25, 23, 59)),
        );
        expect(value('language'), l10n.bible_module_info_greek);
        expect(value('canon'), l10n.bible_module_info_66_books);
        expect(value('versification'), 'KJV');
        expect(find.text('Greek Bible module'), findsNothing);
        await tester.tap(find.byKey(const Key('bible_module_info_details')));
        await tester.pumpAndSettle();
        expect(tester.getSize(_moduleInfoMaterial()).width, dialogWidth);
        expect(find.text('Greek Bible module'), findsOneWidget);
        expect(
          find.text('https://example.com/source', findRichText: true),
          findsOneWidget,
        );
        expect(find.text('CC BY 4.0', findRichText: true), findsOneWidget);
        await tester.tap(find.text(l10n.close));
        await tester.pumpAndSettle();

        final reader = tester
            .element(find.byKey(const Key('bible_verse_1')))
            .read<BibleReaderCubit>();
        await reader.selectModule(reader.state.modules.last);
        await tester.pumpAndSettle();
        await openInfo();
        expect(tester.getSize(_moduleInfoMaterial()).width, dialogWidth);
        expect(value('data_version'), l10n.bible_module_info_unknown);
        expect(value('schema_version'), l10n.bible_module_info_unknown);
        expect(value('date'), l10n.bible_module_info_unknown);
        expect(value('language'), l10n.bible_module_info_language_en);
        expect(find.text('Greek Bible'), findsNothing);
        expect(find.text('Alternative Bible'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });
    }
  }

  for (final entry in {
    'uk': 'Украинский',
    'en': 'Английский',
    'ru': 'Русский',
    'es': 'Испанский',
  }.entries) {
    testWidgets(
      'module language uses the standalone Russian name for ${entry.key}',
      (tester) async {
        await tester.binding.setSurfaceSize(const Size(1000, 900));
        addTearDown(() => tester.binding.setSurfaceSize(null));
        final module = _moduleWithInfo(language: entry.key);
        await tester.pumpWidget(
          buildLocalizedTestApp(
            locale: const Locale('ru'),
            withScaffold: false,
            child: BibleScreen(
              initialBookId: 1,
              bibleRepository: _FakeBibleRepository(
                verseMap: verseMap,
                modules: [module],
              ),
            ),
          ),
        );
        await _pumpUntilFound(tester, find.byKey(const Key('bible_verse_1')));
        await tester.tap(find.byKey(const Key('bible_module_info_button')));
        await tester.pumpAndSettle();
        expect(
          tester
              .widget<Text>(find.byKey(const Key('bible_module_info_language')))
              .data,
          entry.value,
        );
        await tester.tap(find.byKey(const Key('bible_module_info_details')));
        await tester.pumpAndSettle();
        final dialog = find.byKey(const Key('bible_module_info_dialog'));
        for (final hidden in [
          'Код',
          'ID модуля',
          module.code,
          module.moduleId,
        ]) {
          expect(
            find.descendant(
              of: dialog,
              matching: find.text(hidden, findRichText: true),
            ),
            findsNothing,
          );
        }
        expect(tester.takeException(), isNull);
      },
    );
  }

  for (final width in [420.0, 1700.0]) {
    testWidgets('module dialog keeps its width and wraps long values at $width', (
      tester,
    ) async {
      await tester.binding.setSurfaceSize(Size(width, 900));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final longValue = List.filled(20, 'Длинное значение модуля').join(' ');
      final module = _moduleWithInfo(
        language: longValue,
        title: longValue,
        canon: longValue,
        versification: longValue,
        description: longValue,
      );
      await tester.pumpWidget(
        buildLocalizedTestApp(
          locale: const Locale('ru'),
          withScaffold: false,
          child: BibleScreen(
            initialBookId: 1,
            bibleRepository: _FakeBibleRepository(
              verseMap: verseMap,
              modules: [module],
            ),
          ),
        ),
      );
      await _pumpUntilFound(tester, find.byKey(const Key('bible_verse_1')));
      final button = find.byKey(const Key('bible_module_info_button'));
      if (button.evaluate().isNotEmpty) {
        await tester.tap(button);
      } else {
        await tester.tap(find.byIcon(Icons.more_vert).first);
        await tester.pumpAndSettle();
        await tester.tap(
          find.widgetWithText(PopupMenuItem<String>, 'О модуле'),
        );
      }
      await tester.pumpAndSettle();
      final dialogWidth = tester.getSize(_moduleInfoMaterial()).width;
      expect(dialogWidth, closeTo(width == 420 ? 372 : 560, 0.1));
      void expectWrapped(Finder finder, String text) {
        final paragraph = tester.renderObject<RenderParagraph>(finder);
        final boxes = paragraph.getBoxesForSelection(
          TextSelection(baseOffset: 0, extentOffset: text.length),
        );
        expect(boxes.map((box) => box.top).toSet().length, greaterThan(1));
        expect(paragraph.didExceedMaxLines, isFalse);
        // Selection boxes include trailing spaces at soft line breaks;
        // check the visible words rather than that invisible whitespace.
        final wordBoxes = [
          for (final word in RegExp(r'\S+').allMatches(text))
            ...paragraph.getBoxesForSelection(
              TextSelection(baseOffset: word.start, extentOffset: word.end),
            ),
        ];
        expect(
          wordBoxes.every(
            (box) =>
                box.left >= -0.1 && box.right <= paragraph.size.width + 0.1,
          ),
          isTrue,
          reason:
              '$finder: visible words must stay within width ${paragraph.size.width}',
        );
      }

      for (final key in ['title', 'language', 'canon', 'versification']) {
        expectWrapped(find.byKey(Key('bible_module_info_$key')), longValue);
      }
      final details = find.byKey(const Key('bible_module_info_details'));
      await tester.ensureVisible(details);
      await tester.tap(details);
      await tester.pumpAndSettle();
      expect(tester.getSize(_moduleInfoMaterial()).width, dialogWidth);
      final description = find.byKey(const Key('bible_module_info_Описание'));
      expectWrapped(
        find.descendant(of: description, matching: find.byType(Text)),
        longValue,
      );
      await tester.tap(find.text('Закрыть'));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('bible_module_info_dialog')), findsNothing);
      expect(tester.takeException(), isNull);
    });
  }
}

Finder _moduleInfoMaterial() => find
    .descendant(
      of: find.byKey(const Key('bible_module_info_dialog')),
      matching: find.byWidgetPredicate(
        (widget) => widget is Material && widget.type == MaterialType.card,
      ),
    )
    .first;

BibleModuleInfo _moduleWithInfo({
  required String language,
  String title = 'Test module',
  String canon = 'protestant_66',
  String versification = 'kjv_protestant',
  String description = 'Test description',
}) => BibleModuleInfo(
  fileName: 'bible_test.sqlite',
  code: 'TECHNICAL_CODE',
  moduleId: 'technical_module_id',
  title: title,
  description: description,
  language: language,
  canon: canon,
  versification: versification,
  license: 'CC BY 4.0',
  sourceSummary: 'https://example.com/source',
);

Future<void> _pumpUntilFound(WidgetTester tester, Finder finder) async {
  for (var attempt = 0; attempt < 40; attempt++) {
    await tester.pump(const Duration(milliseconds: 50));
    if (finder.evaluate().isNotEmpty) {
      return;
    }
  }
  final workspace = tester
      .element(find.byType(Scaffold).first)
      .read<BibleWorkspaceCubit>();
  final readers = [
    for (final id in workspace.state.paneIds)
      workspace.readerCubitFor(id).state,
  ];
  fail(
    'Widget was not found before pump timeout: $finder; readers: ${readers.map((state) => '${state.status}: ${state.errorMessage}')}',
  );
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
  _FakeBibleRepository({
    BibleVerseMap? verseMap,
    List<BibleModuleInfo>? modules,
  }) : _map = verseMap,
       _modules = modules ?? _defaultModules(),
       super();

  BibleVerseMap? _map;

  final List<BibleModuleInfo> _modules;
  static List<BibleModuleInfo> _defaultModules() => <BibleModuleInfo>[
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
      dataVersion: 17,
      schemaVersion: 3,
      date: DateTime.utc(2026, 7, 25, 23, 59),
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
  Future<List<String>> loadLastModuleFiles() async => const [
    'bible_lxx_tr.sqlite',
  ];

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
          comment: index == 1
              ? 'Separate test footnote excluded from verse copying.'
              : '',
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
