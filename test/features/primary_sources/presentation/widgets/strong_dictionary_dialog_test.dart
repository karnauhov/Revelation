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
    markdown.onGreekStrongPickerTap?.call(1, markdownContext);
    await tester.pumpAndSettle();
    expect(find.byType(StrongNumberPickerDialog), findsOneWidget);

    final pickerContext = tester.element(find.byType(StrongNumberPickerDialog));
    Navigator.of(pickerContext).pop(42);
    await tester.pumpAndSettle();

    markdown = tester.widget<DescriptionMarkdownView>(
      find.byType(DescriptionMarkdownView),
    );
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

  testWidgets('strong dictionary dialog exposes markdown PDF export action', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);

    unawaited(showStrongDictionaryDialog(context, 1));
    await tester.pumpAndSettle();

    expect(
      find.byKey(const Key('description_markdown_export_pdf_button')),
      findsOneWidget,
    );
    expect(
      find.byKey(const Key('description_markdown_copy_button')),
      findsOneWidget,
    );
  });
}
