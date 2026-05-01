@Tags(['widget'])
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/strong_dictionary_dialog.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('showStrongDictionaryDialog opens and closes dialog', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    unawaited(showStrongDictionaryDialog(context, 1));
    await tester.pumpAndSettle();

    expect(find.byType(StrongDictionaryDialog), findsOneWidget);
    expect(find.text(l10n.strongsConcordance), findsOneWidget);

    await tester.tap(find.text(l10n.close));
    await tester.pumpAndSettle();
    expect(find.byType(StrongDictionaryDialog), findsNothing);
  });

  testWidgets('strong picker callback opens StrongNumberPickerDialog', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    unawaited(showStrongDictionaryDialog(context, 1));
    await tester.pumpAndSettle();

    final markdownView = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
    final linkContext = tester.element(find.byType(DescriptionMarkdownView));
    markdownView.onGreekStrongPickerTap?.call(1, linkContext);
    await tester.pumpAndSettle();

    expect(find.byType(StrongNumberPickerDialog), findsOneWidget);

    await tester.tap(
      find.descendant(
        of: find.byType(StrongNumberPickerDialog),
        matching: find.text(l10n.close),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byType(StrongNumberPickerDialog), findsNothing);
  });

  testWidgets('strong callbacks update in-dialog selection state contract', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    unawaited(showStrongDictionaryDialog(context, 1));
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

    await tester.tap(
      find.descendant(
        of: find.byType(StrongNumberPickerDialog),
        matching: find.text(l10n.close),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text(l10n.close).first);
    await tester.pumpAndSettle();
  });

  testWidgets('strong dictionary dialog exposes source info and PDF title', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    unawaited(showStrongDictionaryDialog(context, 1));
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
      find.byKey(const Key('strong_dictionary_nav_forward')),
      findsOneWidget,
    );
    expect(find.byTooltip(l10n.previous_dictionary_entry), findsOneWidget);
    expect(find.byTooltip(l10n.next_dictionary_entry), findsOneWidget);
    final titleText = find.text(l10n.strongsConcordance);
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
  });
}
