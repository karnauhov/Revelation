@Tags(['widget'])
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/description_request.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/verse.dart';
import '../../../../test_harness/test_harness.dart';

void main() {
  test('initial state contains picker entries from service', () {
    final cubit = PrimarySourceDescriptionCubit(
      descriptionService: _FakeDescriptionContentService(),
    );
    addTearDown(cubit.close);

    expect(cubit.state.pickerEntries, hasLength(2));
    expect(cubit.state.pickerEntries.first.number, 1);
    expect(cubit.state.currentType, DescriptionKind.info);
    expect(cubit.state.currentNumber, isNull);
  });

  testWidgets('showCommonInfo switches state to info mode', (tester) async {
    final context = await pumpLocalizedContext(tester);
    final localizations = AppLocalizations.of(context)!;
    final cubit = PrimarySourceDescriptionCubit(
      descriptionService: _FakeDescriptionContentService(),
    );
    addTearDown(cubit.close);

    cubit.showCommonInfo(localizations);

    expect(cubit.state.currentType, DescriptionKind.info);
    expect(cubit.state.currentNumber, isNull);
    expect(cubit.state.content, localizations.click_for_info);
  });

  testWidgets(
    'showInfoForWord and navigateSelection move through word indexes',
    (tester) async {
      final context = await pumpLocalizedContext(tester);
      final localizations = AppLocalizations.of(context)!;
      final source = _buildSource();
      final page = source.pages.first;
      final cubit = PrimarySourceDescriptionCubit(
        descriptionService: _FakeDescriptionContentService(),
      );
      addTearDown(cubit.close);

      final shown = cubit.showInfoForWord(
        wordIndex: 0,
        localizations: localizations,
        source: source,
        selectedPage: page,
      );
      final navigated = cubit.navigateSelection(
        localizations,
        forward: true,
        source: source,
        selectedPage: page,
      );

      expect(shown, isTrue);
      expect(navigated, isTrue);
      expect(cubit.state.currentType, DescriptionKind.word);
      expect(cubit.state.currentNumber, 1);
      expect(cubit.state.content, 'word-1');
    },
  );

  testWidgets(
    'showInfoForStrongNumber and navigateSelection use strong neighbors',
    (tester) async {
      final context = await pumpLocalizedContext(tester);
      final localizations = AppLocalizations.of(context)!;
      final source = _buildSource();
      final cubit = PrimarySourceDescriptionCubit(
        descriptionService: _FakeDescriptionContentService(),
      );
      addTearDown(cubit.close);

      final shown = cubit.showInfoForStrongNumber(
        strongNumber: 10,
        localizations: localizations,
      );
      final navigated = cubit.navigateSelection(
        localizations,
        forward: true,
        source: source,
        selectedPage: source.pages.first,
      );

      expect(shown, isTrue);
      expect(navigated, isTrue);
      expect(cubit.state.currentType, DescriptionKind.strongNumber);
      expect(cubit.state.currentNumber, 11);
      expect(cubit.state.content, 'strong-11');
    },
  );

  testWidgets('navigateSelection returns false in info mode', (tester) async {
    final context = await pumpLocalizedContext(tester);
    final localizations = AppLocalizations.of(context)!;
    final source = _buildSource();
    final cubit = PrimarySourceDescriptionCubit(
      descriptionService: _FakeDescriptionContentService(),
    );
    addTearDown(cubit.close);

    final navigated = cubit.navigateSelection(
      localizations,
      forward: true,
      source: source,
      selectedPage: source.pages.first,
    );

    expect(navigated, isFalse);
    expect(cubit.state.currentType, DescriptionKind.info);
    expect(cubit.state.currentNumber, isNull);
  });

  testWidgets('showInfoForWord returns false when selectedPage is null', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final localizations = AppLocalizations.of(context)!;
    final source = _buildSource();
    final cubit = PrimarySourceDescriptionCubit(
      descriptionService: _FakeDescriptionContentService(),
    );
    addTearDown(cubit.close);

    final shown = cubit.showInfoForWord(
      wordIndex: 0,
      localizations: localizations,
      source: source,
      selectedPage: null,
    );

    expect(shown, isFalse);
    expect(cubit.state.currentType, DescriptionKind.info);
    expect(cubit.state.currentNumber, isNull);
  });

  testWidgets(
    'showInfoForVerse returns false for out-of-range index and empty verses',
    (tester) async {
      final context = await pumpLocalizedContext(tester);
      final localizations = AppLocalizations.of(context)!;
      final source = _buildSource();
      final pageWithNoVerses = model.Page(
        name: 'Empty',
        content: '',
        image: 'empty.png',
        words: const [],
        verses: const [],
      );
      final cubit = PrimarySourceDescriptionCubit(
        descriptionService: _FakeDescriptionContentService(),
      );
      addTearDown(cubit.close);

      final outOfRange = cubit.showInfoForVerse(
        verseIndex: 99,
        localizations: localizations,
        source: source,
        selectedPage: source.pages.first,
      );
      final emptyVerses = cubit.showInfoForVerse(
        verseIndex: 0,
        localizations: localizations,
        source: source,
        selectedPage: pageWithNoVerses,
      );

      expect(outOfRange, isFalse);
      expect(emptyVerses, isFalse);
    },
  );

  testWidgets('navigateSelection wraps backward for verse selection', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final localizations = AppLocalizations.of(context)!;
    final source = _buildSource();
    final page = source.pages.first;
    final cubit = PrimarySourceDescriptionCubit(
      descriptionService: _FakeDescriptionContentService(),
    );
    addTearDown(cubit.close);

    final shown = cubit.showInfoForVerse(
      verseIndex: 0,
      localizations: localizations,
      source: source,
      selectedPage: page,
    );
    final navigated = cubit.navigateSelection(
      localizations,
      forward: false,
      source: source,
      selectedPage: page,
    );

    expect(shown, isTrue);
    expect(navigated, isTrue);
    expect(cubit.state.currentType, DescriptionKind.verse);
    expect(cubit.state.currentNumber, 1);
    expect(cubit.state.content, 'verse-2');
  });

  testWidgets('navigateSelection for strong number returns false on null id', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final localizations = AppLocalizations.of(context)!;
    final source = _buildSource();
    final cubit = PrimarySourceDescriptionCubit(
      descriptionService: _FakeDescriptionContentService(),
    );
    addTearDown(cubit.close);
    cubit.updateDescriptionContent(
      content: 'strong-none',
      type: DescriptionKind.strongNumber,
      number: null,
    );

    final navigated = cubit.navigateSelection(
      localizations,
      forward: true,
      source: source,
      selectedPage: source.pages.first,
    );

    expect(navigated, isFalse);
    expect(cubit.state.currentType, DescriptionKind.strongNumber);
    expect(cubit.state.currentNumber, isNull);
  });

  testWidgets(
    'showInfoForStrongNumber returns false when service cannot resolve content',
    (tester) async {
      final context = await pumpLocalizedContext(tester);
      final localizations = AppLocalizations.of(context)!;
      final cubit = PrimarySourceDescriptionCubit(
        descriptionService: _NullStrongDescriptionContentService(),
      );
      addTearDown(cubit.close);

      final shown = cubit.showInfoForStrongNumber(
        strongNumber: 10,
        localizations: localizations,
      );

      expect(shown, isFalse);
      expect(cubit.state.currentType, DescriptionKind.info);
      expect(cubit.state.currentNumber, isNull);
    },
  );

  test(
    'getGreekStrongPickerEntries keeps state when entries are unchanged',
    () {
      final service = _FakeDescriptionContentService();
      final cubit = PrimarySourceDescriptionCubit(descriptionService: service);
      addTearDown(cubit.close);

      final entries = cubit.getGreekStrongPickerEntries();

      expect(identical(entries, cubit.state.pickerEntries), isTrue);
      expect(entries, hasLength(2));
    },
  );

  test('getGreekStrongPickerEntries updates state when entries change', () {
    final service = _MutablePickerDescriptionContentService();
    final cubit = PrimarySourceDescriptionCubit(descriptionService: service);
    addTearDown(cubit.close);

    service.entries = const [
      GreekStrongPickerEntry(number: 10, word: 'deka'),
      GreekStrongPickerEntry(number: 20, word: 'eikosi'),
      GreekStrongPickerEntry(number: 30, word: 'triakonta'),
    ];
    final entries = cubit.getGreekStrongPickerEntries();

    expect(entries, hasLength(3));
    expect(cubit.state.pickerEntries.first.number, 10);
    expect(
      () =>
          entries.add(const GreekStrongPickerEntry(number: 40, word: 'forty')),
      throwsUnsupportedError,
    );
  });
}

class _FakeDescriptionContentService extends DescriptionContentService {
  @override
  DescriptionContent? buildStrongContent(
    AppLocalizations localizations,
    int strongNumber,
  ) {
    return DescriptionContent(
      markdown: 'strong-$strongNumber',
      kind: DescriptionKind.strongNumber,
    );
  }

  @override
  DescriptionContent? buildContent(
    AppLocalizations localizations,
    DescriptionRequest request, {
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    return switch (request) {
      StrongDescriptionRequest strongRequest => DescriptionContent(
        markdown: 'strong-${strongRequest.strongNumber}',
        kind: DescriptionKind.strongNumber,
      ),
      WordDescriptionRequest wordRequest => DescriptionContent(
        markdown: 'word-${wordRequest.wordIndex}',
        kind: DescriptionKind.word,
      ),
      VerseDescriptionRequest verseRequest => DescriptionContent(
        markdown: 'verse-${verseRequest.verseNumber}',
        kind: DescriptionKind.verse,
      ),
    };
  }

  @override
  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() {
    return const [
      GreekStrongPickerEntry(number: 1, word: 'alpha'),
      GreekStrongPickerEntry(number: 2, word: 'beta'),
    ];
  }

  @override
  int getNeighborStrongNumber(int current, {bool forward = true}) {
    return forward ? current + 1 : current - 1;
  }
}

class _NullStrongDescriptionContentService
    extends _FakeDescriptionContentService {
  @override
  DescriptionContent? buildStrongContent(
    AppLocalizations localizations,
    int strongNumber,
  ) {
    return null;
  }
}

class _MutablePickerDescriptionContentService
    extends _FakeDescriptionContentService {
  List<GreekStrongPickerEntry> entries = const [
    GreekStrongPickerEntry(number: 1, word: 'alpha'),
    GreekStrongPickerEntry(number: 2, word: 'beta'),
  ];

  @override
  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() {
    return entries;
  }
}

PrimarySource _buildSource() {
  return PrimarySource(
    id: 'source-1',
    title: 'Source',
    date: '',
    content: '',
    quantity: 0,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 1,
    isMonochrome: false,
    pages: [
      model.Page(
        name: 'P1',
        content: 'C1',
        image: 'p1.png',
        words: [PageWord('w1', []), PageWord('w2', [])],
        verses: [
          const Verse(
            chapterNumber: 1,
            verseNumber: 1,
            labelPosition: Offset.zero,
          ),
          const Verse(
            chapterNumber: 1,
            verseNumber: 2,
            labelPosition: Offset.zero,
          ),
        ],
      ),
    ],
    attributes: const [],
    permissionsReceived: true,
  );
}
