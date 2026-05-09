@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('renders real dictionary page with selected initial entry', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        withScaffold: false,
        child: StrongsDictionaryScreen(
          initialStrongNumber: 2,
          contentService: _FakeStrongsDictionaryContentService(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(StrongsDictionaryScreen));
    final localizations = AppLocalizations.of(context)!;
    final markdownView = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );

    expect(find.text(localizations.strongs_dictionary_screen), findsOneWidget);
    expect(find.text(localizations.strongs_dictionary_header), findsOneWidget);
    expect(
      find.byKey(const Key('strong_dictionary_search_field')),
      findsOneWidget,
    );
    expect(
      find.byTooltip(localizations.greek_keyboard_tooltip),
      findsOneWidget,
    );
    expect(markdownView.exportPdfDocumentTitle, 'G2');
    expect(find.byKey(const Key('strong_dictionary_entry_2')), findsOneWidget);
  });

  testWidgets('search filters entries and selecting a result updates content', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        withScaffold: false,
        child: StrongsDictionaryScreen(
          initialStrongNumber: 1,
          contentService: _FakeStrongsDictionaryContentService(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.enterText(
      find.byKey(const Key('strong_dictionary_search_field')),
      'beta',
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('strong_dictionary_entry_1')), findsNothing);
    expect(find.byKey(const Key('strong_dictionary_entry_2')), findsOneWidget);

    await tester.tap(find.byKey(const Key('strong_dictionary_entry_2')));
    await tester.pumpAndSettle();

    final markdownView = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    expect(markdownView.exportPdfDocumentTitle, 'G2');
  });

  testWidgets('search filters entries by dictionary description text', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        withScaffold: false,
        child: StrongsDictionaryScreen(
          initialStrongNumber: 1,
          contentService: _FakeStrongsDictionaryContentService(
            entries: const [
              StrongPickerEntry(number: 1, word: 'Alpha'),
              StrongPickerEntry(
                number: 2,
                word: 'Beta',
                description: 'Second letter',
              ),
            ],
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.enterText(
      find.byKey(const Key('strong_dictionary_search_field')),
      'LETTER',
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('strong_dictionary_entry_1')), findsNothing);
    expect(find.byKey(const Key('strong_dictionary_entry_2')), findsOneWidget);
  });

  testWidgets('selected initial entry is revealed in the selector list', (
    tester,
  ) async {
    final entries = List<StrongPickerEntry>.generate(
      80,
      (index) =>
          StrongPickerEntry(number: index + 1, word: 'Word ${index + 1}'),
    );

    await tester.pumpWidget(
      buildLocalizedTestApp(
        withScaffold: false,
        child: StrongsDictionaryScreen(
          initialStrongNumber: 75,
          contentService: _FakeStrongsDictionaryContentService(
            entries: entries,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('strong_dictionary_entry_75')), findsOneWidget);
  });

  testWidgets('navigation buttons move between dictionary entries', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        withScaffold: false,
        child: StrongsDictionaryScreen(
          initialStrongNumber: 2,
          contentService: _FakeStrongsDictionaryContentService(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('strong_dictionary_nav_forward')));
    await tester.pumpAndSettle();
    var markdownView = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    expect(markdownView.exportPdfDocumentTitle, 'G3');

    await tester.tap(find.byKey(const Key('strong_dictionary_nav_back')));
    await tester.pumpAndSettle();
    markdownView = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    expect(markdownView.exportPdfDocumentTitle, 'G2');
  });

  testWidgets('shows empty state when dictionary entries are unavailable', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        withScaffold: false,
        child: StrongsDictionaryScreen(
          contentService: _FakeStrongsDictionaryContentService(
            entries: const <StrongPickerEntry>[],
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(StrongsDictionaryScreen));
    final localizations = AppLocalizations.of(context)!;

    expect(
      find.text(localizations.strong_dictionary_no_entries),
      findsOneWidget,
    );
  });
}

class _FakeStrongsDictionaryContentService
    extends StrongsDictionaryContentService {
  _FakeStrongsDictionaryContentService({
    this.entries = const [
      StrongPickerEntry(number: 1, word: 'Alpha'),
      StrongPickerEntry(number: 2, word: 'Beta'),
      StrongPickerEntry(number: 3, word: 'Gamma'),
    ],
  });

  final List<StrongPickerEntry> entries;

  @override
  List<StrongPickerEntry> getPickerEntries() {
    return entries;
  }

  @override
  DescriptionContent? buildStrongContent(
    AppLocalizations localizations,
    int strongNumber,
  ) {
    for (final entry in entries) {
      if (entry.number == strongNumber) {
        return DescriptionContent(
          markdown: '## ${entry.word}\n\r${entry.code}',
          kind: DescriptionKind.strongNumber,
        );
      }
    }
    return null;
  }

  @override
  int getNeighborStrongNumber(int current, {bool forward = true}) {
    if (entries.isEmpty) {
      return current;
    }

    final index = entries.indexWhere((entry) => entry.number == current);
    if (index == -1) {
      return entries.first.number;
    }

    final nextIndex = forward
        ? (index + 1) % entries.length
        : (index - 1 + entries.length) % entries.length;
    return entries[nextIndex].number;
  }
}
