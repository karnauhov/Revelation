@Tags(['widget'])
import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/data/repositories/strong_dictionary_reading_store.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets(
    'restores an available entry and discards other articles’ scroll events',
    (tester) async {
      final l10n = await _loadLocalizations(tester);
      SharedPreferences.setMockInitialValues({
        StrongDictionaryReadingStore.preferenceKey: <String>['2', '180.5'],
      });
      final store = StrongDictionaryReadingStore();
      final cubit = StrongsDictionaryCubit(
        localizations: l10n,
        contentService: _FakeStrongsDictionaryContentService(),
        readingStore: store,
      );
      addTearDown(cubit.close);
      await tester.pump();
      expect(cubit.state.strongNumber, 2);
      expect(cubit.articleOffset, 180.5);
      cubit.rememberArticleOffset(2, 240);
      cubit.showStrongNumber(localizations: l10n, strongNumber: 1);
      cubit.rememberArticleOffset(2, 555);
      expect(cubit.articleOffset, 0);
      expect(await store.load(), (number: 1, offset: 0.0));
    },
  );

  testWidgets(
    'missing entries and damaged saved positions open the first available entry',
    (tester) async {
      final l10n = await _loadLocalizations(tester);
      for (final value in [
        <String>['9000', '23'],
        <String>['2', 'NaN'],
        <String>['2', '-1'],
        'broken',
      ]) {
        SharedPreferences.setMockInitialValues({
          StrongDictionaryReadingStore.preferenceKey: value,
        });
        final cubit = StrongsDictionaryCubit(
          localizations: l10n,
          contentService: _FakeStrongsDictionaryContentService(),
          readingStore: StrongDictionaryReadingStore(),
        );
        await tester.pump();
        expect(cubit.state.strongNumber, 1);
        expect(cubit.state.hasContent, isTrue);
        expect(cubit.articleOffset, 0);
        await cubit.close();
      }
    },
  );

  testWidgets(
    'a late restore cannot replace a selection or reopen a closed cubit',
    (tester) async {
      final l10n = await _loadLocalizations(tester);
      for (final close in [true, false]) {
        final store = _DelayedReadingStore();
        final cubit = StrongsDictionaryCubit(
          localizations: l10n,
          contentService: _FakeStrongsDictionaryContentService(),
          readingStore: store,
        );
        if (close) {
          await cubit.close();
        } else {
          cubit.showStrongNumber(localizations: l10n, strongNumber: 2);
        }
        store.loaded.complete((number: 1, offset: 142.0));
        await tester.pump();
        expect(store.written, close ? isEmpty : [(number: 2, offset: 0.0)]);
        if (!close) {
          expect(cubit.state.strongNumber, 2);
          await cubit.close();
        }
      }
    },
  );

  testWidgets('each linked page replaces the previous place before scrolling', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final service = _FakeStrongsDictionaryContentService(missingNumbers: {42});
    final store = _DelayedReadingStore();
    for (final number in [2, 1, 1, 42]) {
      final page = StrongsDictionaryCubit(
        initialStrongNumber: number,
        localizations: localizations,
        contentService: service,
        readingStore: store,
      );
      expect(page.state.strongNumber, number);
      expect(page.state.restoring, isFalse);
      expect(page.articleOffset, 0);
      await page.close();
    }
    expect(store.written, [
      (number: 2, offset: 0.0),
      (number: 1, offset: 0.0),
      (number: 1, offset: 0.0),
    ]);
  });

  testWidgets('loads initial entry content and picker entries', (tester) async {
    final localizations = await _loadLocalizations(tester);
    final service = _FakeStrongsDictionaryContentService();
    final cubit = StrongsDictionaryCubit(
      initialStrongNumber: 1,
      localizations: localizations,
      contentService: service,
    );
    addTearDown(cubit.close);

    expect(cubit.state.strongNumber, 1);
    expect(cubit.state.markdown, 'strong-1');
    expect(cubit.state.hasContent, isTrue);
    expect(cubit.state.pickerEntries, service.entries);
  });

  testWidgets('showStrongNumber records missing entries as empty content', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final service = _FakeStrongsDictionaryContentService(missingNumbers: {42});
    final cubit = StrongsDictionaryCubit(
      initialStrongNumber: 1,
      localizations: localizations,
      contentService: service,
    );
    addTearDown(cubit.close);

    final shown = cubit.showStrongNumber(
      localizations: localizations,
      strongNumber: 42,
    );

    expect(shown, isFalse);
    expect(cubit.state.strongNumber, 42);
    expect(cubit.state.hasContent, isFalse);
    expect(cubit.state.displayMarkdown, '-');
  });

  testWidgets('navigate uses Strong neighbor policy from content service', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final cubit = StrongsDictionaryCubit(
      initialStrongNumber: 10,
      localizations: localizations,
      contentService: _FakeStrongsDictionaryContentService(),
    );
    addTearDown(cubit.close);

    final forward = cubit.navigate(localizations: localizations, forward: true);
    final backward = cubit.navigate(
      localizations: localizations,
      forward: false,
    );

    expect(forward, isTrue);
    expect(backward, isTrue);
    expect(cubit.state.strongNumber, 10);
    expect(cubit.state.markdown, 'strong-10');
  });

  testWidgets('getPickerEntries refreshes state when service entries change', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final service = _FakeStrongsDictionaryContentService();
    final cubit = StrongsDictionaryCubit(
      initialStrongNumber: 1,
      localizations: localizations,
      contentService: service,
    );
    addTearDown(cubit.close);

    service.entries = const [
      StrongPickerEntry(number: 7, word: 'hepta'),
      StrongPickerEntry(number: 8, word: 'okto'),
    ];
    final entries = cubit.getPickerEntries();

    expect(entries, service.entries);
    expect(
      () => entries.add(const StrongPickerEntry(number: 9, word: 'ennea')),
      throwsUnsupportedError,
    );
  });

  testWidgets('updateSearchQuery filters by number, word and description', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final service = _FakeStrongsDictionaryContentService(
      entries: const [
        StrongPickerEntry(
          number: 1,
          word: 'ἀγάπη',
          description: 'Love and affection',
        ),
        StrongPickerEntry(
          number: 2,
          word: 'βῆτα',
          description: 'Second letter',
        ),
      ],
    );
    final cubit = StrongsDictionaryCubit(
      initialStrongNumber: 1,
      localizations: localizations,
      contentService: service,
    );
    addTearDown(cubit.close);

    cubit.updateSearchQuery('αγαπη');
    expect(cubit.state.visiblePickerEntries, const [
      StrongPickerEntry(
        number: 1,
        word: 'ἀγάπη',
        description: 'Love and affection',
      ),
    ]);

    cubit.updateSearchQuery('LETTER');
    expect(cubit.state.visiblePickerEntries, const [
      StrongPickerEntry(number: 2, word: 'βῆτα', description: 'Second letter'),
    ]);

    cubit.updateSearchQuery('G1');
    expect(cubit.state.visiblePickerEntries, const [
      StrongPickerEntry(
        number: 1,
        word: 'ἀγάπη',
        description: 'Love and affection',
      ),
    ]);
  });
}

Future<AppLocalizations> _loadLocalizations(WidgetTester tester) async {
  final context = await pumpLocalizedContext(tester);
  return AppLocalizations.of(context)!;
}

class _FakeStrongsDictionaryContentService
    extends StrongsDictionaryContentService {
  _FakeStrongsDictionaryContentService({
    Set<int>? missingNumbers,
    List<StrongPickerEntry>? entries,
  }) : missingNumbers = missingNumbers ?? const <int>{},
       entries =
           entries ??
           const [
             StrongPickerEntry(number: 1, word: 'alpha'),
             StrongPickerEntry(number: 2, word: 'beta'),
           ];

  final Set<int> missingNumbers;

  List<StrongPickerEntry> entries;

  @override
  List<StrongPickerEntry> getPickerEntries() {
    return entries;
  }

  @override
  DescriptionContent? buildStrongContent(
    AppLocalizations localizations,
    int strongNumber,
  ) {
    if (missingNumbers.contains(strongNumber)) {
      return null;
    }

    return DescriptionContent(
      markdown: 'strong-$strongNumber',
      kind: DescriptionKind.strongNumber,
    );
  }

  @override
  int getNeighborStrongNumber(int current, {bool forward = true}) {
    return forward ? current + 1 : current - 1;
  }
}

class _DelayedReadingStore extends StrongDictionaryReadingStore {
  final loaded = Completer<StrongDictionaryPlace?>();
  final written = <StrongDictionaryPlace>[];
  @override
  Future<StrongDictionaryPlace?> load() => loaded.future;
  @override
  Future<void> save(StrongDictionaryPlace place) async {
    written.add(place);
  }
}
