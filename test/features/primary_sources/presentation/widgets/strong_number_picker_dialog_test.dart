@Tags(['widget'])
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/strong_number_picker_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('shows empty-state dialog when entries list is empty', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    unawaited(
      showDialog<int>(
        context: context,
        builder: (_) => const StrongNumberPickerDialog(
          entries: <GreekStrongPickerEntry>[],
          initialStrongNumber: 1,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(StrongNumberPickerDialog), findsOneWidget);
    expect(find.text('-'), findsOneWidget);

    await tester.tap(find.text(l10n.close));
    await tester.pumpAndSettle();
    expect(find.byType(StrongNumberPickerDialog), findsNothing);
  });

  testWidgets('normalizes blocked numbers and returns selected value', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    final resultFuture = showDialog<int>(
      context: context,
      builder: (_) => const StrongNumberPickerDialog(
        entries: <GreekStrongPickerEntry>[
          GreekStrongPickerEntry(number: 2718, word: 'word-2718'),
          GreekStrongPickerEntry(number: 3303, word: 'word-3303'),
          GreekStrongPickerEntry(number: 5000, word: 'word-5000'),
        ],
        initialStrongNumber: 2717,
      ),
    );
    await tester.pumpAndSettle();

    final fieldFinder = find.byType(TextField);
    expect(fieldFinder, findsOneWidget);
    expect(find.text('2718'), findsOneWidget);

    await tester.enterText(fieldFinder, '3203');
    await tester.pump();
    expect(find.text('3303'), findsOneWidget);
    expect(find.text('word-3303'), findsOneWidget);

    await tester.tap(find.text(l10n.ok));
    await tester.pumpAndSettle();

    expect(await resultFuture, 3303);
  });

  testWidgets('cancel and submit actions complete dialog result contract', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    final cancelFuture = showDialog<int>(
      context: context,
      builder: (_) => const StrongNumberPickerDialog(
        entries: <GreekStrongPickerEntry>[
          GreekStrongPickerEntry(number: 1, word: 'one'),
          GreekStrongPickerEntry(number: 2, word: 'two'),
        ],
        initialStrongNumber: 1,
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text(l10n.cancel));
    await tester.pumpAndSettle();
    expect(await cancelFuture, isNull);

    final submitFuture = showDialog<int>(
      context: context,
      builder: (_) => const StrongNumberPickerDialog(
        entries: <GreekStrongPickerEntry>[
          GreekStrongPickerEntry(number: 1, word: 'one'),
          GreekStrongPickerEntry(number: 2, word: 'two'),
        ],
        initialStrongNumber: 1,
      ),
    );
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), '2');
    await tester.pump();
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();

    expect(await submitFuture, 2);
  });
}
