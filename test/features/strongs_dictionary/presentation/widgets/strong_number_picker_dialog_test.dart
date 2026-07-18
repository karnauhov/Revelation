@Tags(['widget'])
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';

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
          entries: <StrongPickerEntry>[],
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
        entries: <StrongPickerEntry>[
          StrongPickerEntry(number: 2718, word: 'word-2718'),
          StrongPickerEntry(number: 3303, word: 'word-3303'),
          StrongPickerEntry(number: 5000, word: 'word-5000'),
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

  testWidgets('clamps out-of-range Strong numbers to classic boundary', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    final resultFuture = showDialog<int>(
      context: context,
      builder: (_) => const StrongNumberPickerDialog(
        entries: <StrongPickerEntry>[
          StrongPickerEntry(number: 1, word: 'classic-1'),
          StrongPickerEntry(number: 5624, word: 'classic-5624'),
          StrongPickerEntry(number: 5625, word: 'out-of-range-5625'),
        ],
        initialStrongNumber: 5625,
      ),
    );
    await tester.pumpAndSettle();

    final fieldFinder = find.byType(TextField);
    final field = tester.widget<TextField>(fieldFinder);
    expect(field.decoration?.hintText, '1 - 5624');
    expect(find.text('5624'), findsOneWidget);
    expect(find.text('classic-5624'), findsOneWidget);
    expect(find.text('out-of-range-5625'), findsNothing);

    await tester.enterText(fieldFinder, '99999');
    await tester.pumpAndSettle();

    expect(find.text('5624'), findsOneWidget);
    expect(find.text('classic-5624'), findsOneWidget);

    await tester.tap(find.text(l10n.ok));
    await tester.pumpAndSettle();

    expect(await resultFuture, 5624);
  });

  testWidgets('cancel and submit actions complete dialog result contract', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;

    final cancelFuture = showDialog<int>(
      context: context,
      builder: (_) => const StrongNumberPickerDialog(
        entries: <StrongPickerEntry>[
          StrongPickerEntry(number: 1, word: 'one'),
          StrongPickerEntry(number: 2, word: 'two'),
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
        entries: <StrongPickerEntry>[
          StrongPickerEntry(number: 1, word: 'one'),
          StrongPickerEntry(number: 2, word: 'two'),
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
