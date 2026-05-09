@Tags(['widget'])
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
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

  testWidgets('updateSearchQuery filters picker entries by word and number', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final cubit = StrongsDictionaryCubit(
      initialStrongNumber: 1,
      localizations: localizations,
      contentService: _FakeStrongsDictionaryContentService(),
    );
    addTearDown(cubit.close);

    cubit.updateSearchQuery('beta');
    expect(cubit.state.visiblePickerEntries, const [
      StrongPickerEntry(number: 2, word: 'beta'),
    ]);

    cubit.updateSearchQuery('G1');
    expect(cubit.state.visiblePickerEntries, const [
      StrongPickerEntry(number: 1, word: 'alpha'),
    ]);
  });
}

Future<AppLocalizations> _loadLocalizations(WidgetTester tester) async {
  final context = await pumpLocalizedContext(tester);
  return AppLocalizations.of(context)!;
}

class _FakeStrongsDictionaryContentService
    extends StrongsDictionaryContentService {
  _FakeStrongsDictionaryContentService({Set<int>? missingNumbers})
    : missingNumbers = missingNumbers ?? const <int>{};

  final Set<int> missingNumbers;

  List<StrongPickerEntry> entries = const [
    StrongPickerEntry(number: 1, word: 'alpha'),
    StrongPickerEntry(number: 2, word: 'beta'),
  ];

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
