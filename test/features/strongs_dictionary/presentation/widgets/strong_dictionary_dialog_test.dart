@Tags(['widget'])
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('showStrongDictionaryDialog opens and closes dialog', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    unawaited(
      showStrongDictionaryDialog(
        context,
        1,
        contentService: _FakeStrongsDictionaryContentService(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(StrongDictionaryDialog), findsOneWidget);
    expect(find.text(l10n.strongs_dictionary_screen), findsOneWidget);

    await tester.tap(find.text(l10n.close));
    await tester.pumpAndSettle();
    expect(find.byType(StrongDictionaryDialog), findsNothing);
  });

  testWidgets('strong picker callback opens StrongNumberPickerDialog', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);

    unawaited(
      showStrongDictionaryDialog(
        context,
        1,
        contentService: _FakeStrongsDictionaryContentService(),
      ),
    );
    await tester.pumpAndSettle();

    final markdownView = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    final linkContext = tester.element(find.byType(DescriptionMarkdownView));
    markdownView.onGreekStrongPickerTap?.call(1, linkContext);
    await tester.pumpAndSettle();

    expect(find.byType(StrongNumberPickerDialog), findsOneWidget);

    final pickerContext = tester.element(find.byType(StrongNumberPickerDialog));
    Navigator.of(pickerContext).pop();
    await tester.pumpAndSettle();
    expect(find.byType(StrongNumberPickerDialog), findsNothing);
  });

  testWidgets('strong callbacks update in-dialog selection state contract', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    unawaited(
      showStrongDictionaryDialog(
        context,
        1,
        contentService: _FakeStrongsDictionaryContentService(),
      ),
    );
    await tester.pumpAndSettle();

    var markdown = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    final markdownContext = tester.element(
      find.byType(DescriptionMarkdownView),
    );

    markdown.onGreekStrongTap?.call(2, markdownContext);
    await tester.pumpAndSettle();

    markdown = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    expect(markdown.exportPdfDocumentTitle, 'G2');
    markdown.onGreekStrongPickerTap?.call(1, markdownContext);
    await tester.pumpAndSettle();
    expect(find.byType(StrongNumberPickerDialog), findsOneWidget);

    final pickerContext = tester.element(find.byType(StrongNumberPickerDialog));
    Navigator.of(pickerContext).pop(42);
    await tester.pumpAndSettle();

    markdown = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    expect(markdown.exportPdfDocumentTitle, 'G42');
    markdown.onGreekStrongPickerTap?.call(1, markdownContext);
    await tester.pumpAndSettle();
    expect(find.byType(StrongNumberPickerDialog), findsOneWidget);

    final secondPickerContext = tester.element(
      find.byType(StrongNumberPickerDialog),
    );
    Navigator.of(secondPickerContext).pop();
    await tester.pumpAndSettle();
    await tester.tap(find.text(l10n.close).first);
    await tester.pumpAndSettle();
  });

  testWidgets('strong dictionary dialog exposes source info and PDF title', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    unawaited(
      showStrongDictionaryDialog(
        context,
        1,
        contentService: _FakeStrongsDictionaryContentService(),
      ),
    );
    await tester.pumpAndSettle();

    final markdown = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    expect(markdown.exportPdfDocumentTitle, 'G1');
    expect(
      find.byKey(const Key('description_markdown_export_pdf_button')),
      findsOneWidget,
    );
    expect(
      find.byKey(const Key('description_markdown_copy_button')),
      findsOneWidget,
    );
    expect(find.byKey(const Key('strong_dictionary_nav_back')), findsOneWidget);
    expect(
      find.byKey(const Key('strong_dictionary_nav_picker')),
      findsOneWidget,
    );
    expect(
      find.byKey(const Key('strong_dictionary_nav_forward')),
      findsOneWidget,
    );
    expect(find.byTooltip(l10n.previous_dictionary_entry), findsOneWidget);
    expect(find.byTooltip(l10n.next_dictionary_entry), findsOneWidget);
    final titleText = find.text(l10n.strongs_dictionary_screen);
    final infoIcon = find.byKey(const Key('strong_reference_info_icon'));
    expect(infoIcon, findsOneWidget);
    expect(
      tester.getTopLeft(infoIcon).dx,
      greaterThan(tester.getTopRight(titleText).dx - 4),
    );
    expect(
      tester.getTopLeft(infoIcon).dy,
      lessThan(tester.getTopLeft(titleText).dy),
    );
    expect(find.byTooltip(l10n.strong_reference_commentary), findsOneWidget);

    await tester.tap(find.byKey(const Key('strong_dictionary_nav_forward')));
    await tester.pumpAndSettle();
    var updatedMarkdown = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    expect(updatedMarkdown.exportPdfDocumentTitle, 'G2');

    await tester.tap(find.byKey(const Key('strong_dictionary_nav_back')));
    await tester.pumpAndSettle();
    updatedMarkdown = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    expect(updatedMarkdown.exportPdfDocumentTitle, 'G1');

    await tester.tap(find.byKey(const Key('strong_dictionary_nav_picker')));
    await tester.pumpAndSettle();
    expect(find.byType(StrongNumberPickerDialog), findsOneWidget);
    final pickerContext = tester.element(find.byType(StrongNumberPickerDialog));
    Navigator.of(pickerContext).pop();
    await tester.pumpAndSettle();
  });
}

class _FakeStrongsDictionaryContentService
    extends StrongsDictionaryContentService {
  static const _entries = <StrongPickerEntry>[
    StrongPickerEntry(number: 1, word: 'Alpha'),
    StrongPickerEntry(number: 2, word: 'Beta'),
    StrongPickerEntry(number: 42, word: 'Answer'),
  ];

  @override
  List<StrongPickerEntry> getPickerEntries() {
    return _entries;
  }

  @override
  DescriptionContent? buildStrongContent(
    AppLocalizations localizations,
    int strongNumber,
  ) {
    final entry = _entries.firstWhere(
      (entry) => entry.number == strongNumber,
      orElse: () =>
          StrongPickerEntry(number: strongNumber, word: 'G$strongNumber'),
    );
    return DescriptionContent(
      markdown: '## ${entry.word}\n\r${entry.code}',
      kind: DescriptionKind.strongNumber,
    );
  }

  @override
  int getNeighborStrongNumber(int current, {bool forward = true}) {
    final index = _entries.indexWhere((entry) => entry.number == current);
    if (index == -1) {
      return _entries.first.number;
    }
    final nextIndex = forward
        ? (index + 1) % _entries.length
        : (index - 1 + _entries.length) % _entries.length;
    return _entries[nextIndex].number;
  }
}
