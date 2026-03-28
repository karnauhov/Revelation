@Tags(['widget'])
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/replace_color_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('shows selected area dimensions and applies tolerance changes', (
    tester,
  ) async {
    final hostContext = await _pumpHost(tester);
    final applied = <(Rect?, Color, Color, double)>[];
    Rect? selectedArea = const Rect.fromLTWH(10, 10, 30, 20);

    await _openDialog(
      tester,
      hostContext,
      buildDialog: (context) => ReplaceColorDialog(
        parentContext: hostContext,
        onApply: (area, from, to, tol) {
          applied.add((area, from, to, tol));
        },
        onCancel: () {},
        onStartSelectAreaMode: (_) {},
        onStartPipetteMode: (_, __) {},
        readSelectedArea: () => selectedArea,
        readColorToReplace: () => const Color(0xFF111111),
        readNewColor: () => const Color(0xFF222222),
        readTolerance: () => 7,
        selectedArea: selectedArea,
        colorToReplace: const Color(0xFF111111),
        newColor: const Color(0xFF222222),
        tolerance: 7,
      ),
    );

    expect(find.textContaining('30 x 20'), findsOneWidget);

    final slider = tester.widget<Slider>(find.byType(Slider));
    slider.onChanged!(35);
    await tester.pump();
    slider.onChangeEnd!(35);
    await tester.pump();

    expect(applied, isNotEmpty);
    expect(applied.last.$1, selectedArea);
    expect(applied.last.$4, 35);
  });

  testWidgets('reset button calls onCancel and closes dialog', (tester) async {
    final hostContext = await _pumpHost(tester);
    var canceled = false;

    await _openDialog(
      tester,
      hostContext,
      buildDialog: (context) => ReplaceColorDialog(
        parentContext: hostContext,
        onApply: (_, __, ___, ____) {},
        onCancel: () {
          canceled = true;
        },
        onStartSelectAreaMode: (_) {},
        onStartPipetteMode: (_, __) {},
        readSelectedArea: () => null,
        readColorToReplace: () => const Color(0xFFFFFFFF),
        readNewColor: () => const Color(0xFFFFFFFF),
        readTolerance: () => 0,
      ),
    );

    final l10n = AppLocalizations.of(hostContext)!;
    await tester.tap(find.text(l10n.reset));
    await tester.pumpAndSettle();

    expect(canceled, isTrue);
    expect(find.byType(ReplaceColorDialog), findsNothing);
  });

  testWidgets(
    'area selection action closes dialog and supports reopening callback',
    (tester) async {
      final hostContext = await _pumpHost(tester);
      VoidCallback? reopen;

      await _openDialog(
        tester,
        hostContext,
        buildDialog: (context) => ReplaceColorDialog(
          parentContext: hostContext,
          onApply: (_, __, ___, ____) {},
          onCancel: () {},
          onStartSelectAreaMode: (onSelected) {
            reopen = () => onSelected(null);
          },
          onStartPipetteMode: (_, __) {},
          readSelectedArea: () => null,
          readColorToReplace: () => const Color(0xFFFFFFFF),
          readNewColor: () => const Color(0xFFFFFFFF),
          readTolerance: () => 0,
        ),
      );

      final l10n = AppLocalizations.of(hostContext)!;
      await tester.tap(find.byTooltip(l10n.area_selection));
      await tester.pumpAndSettle();
      expect(reopen, isNotNull);
      expect(find.byType(ReplaceColorDialog), findsNothing);

      reopen!();
      await tester.pumpAndSettle();
      expect(find.byType(ReplaceColorDialog), findsOneWidget);
    },
  );

  testWidgets(
    'palette dialogs honor cancel/apply contracts for both color targets',
    (tester) async {
      final hostContext = await _pumpHost(tester);
      final l10n = AppLocalizations.of(hostContext)!;
      final applied = <(Rect?, Color, Color, double)>[];

      await _openDialog(
        tester,
        hostContext,
        buildDialog: (context) => ReplaceColorDialog(
          parentContext: hostContext,
          onApply: (area, from, to, tol) {
            applied.add((area, from, to, tol));
          },
          onCancel: () {},
          onStartSelectAreaMode: (_) {},
          onStartPipetteMode: (_, __) {},
          readSelectedArea: () => null,
          readColorToReplace: () => const Color(0xFF111111),
          readNewColor: () => const Color(0xFF222222),
          readTolerance: () => 5,
          colorToReplace: const Color(0xFF111111),
          newColor: const Color(0xFF222222),
          tolerance: 5,
        ),
      );

      await tester.tap(find.byTooltip(l10n.palette).first);
      await tester.pumpAndSettle();
      await tester.tap(find.text(l10n.cancel).last);
      await tester.pumpAndSettle();
      expect(applied, isEmpty);

      await tester.tap(find.byTooltip(l10n.palette).first);
      await tester.pumpAndSettle();
      await tester.tap(find.text(l10n.ok).last);
      await tester.pumpAndSettle();
      expect(applied, isNotEmpty);

      final applyCountAfterFirstPalette = applied.length;
      await tester.tap(find.byTooltip(l10n.palette).last);
      await tester.pumpAndSettle();
      await tester.tap(find.text(l10n.ok).last);
      await tester.pumpAndSettle();
      expect(applied.length, greaterThan(applyCountAfterFirstPalette));
    },
  );

  testWidgets('eyedropper actions close and can reopen dialog via callback', (
    tester,
  ) async {
    final hostContext = await _pumpHost(tester);
    final l10n = AppLocalizations.of(hostContext)!;
    final pipetteModes = <bool>[];
    void Function(Color?)? reopen;

    await _openDialog(
      tester,
      hostContext,
      buildDialog: (context) => ReplaceColorDialog(
        parentContext: hostContext,
        onApply: (_, __, ___, ____) {},
        onCancel: () {},
        onStartSelectAreaMode: (_) {},
        onStartPipetteMode: (onPicked, isColorToReplace) {
          pipetteModes.add(isColorToReplace);
          reopen = onPicked;
        },
        readSelectedArea: () => null,
        readColorToReplace: () => const Color(0xFFFFFFFF),
        readNewColor: () => const Color(0xFFFFFFFF),
        readTolerance: () => 0,
      ),
    );

    await tester.tap(find.byTooltip(l10n.eyedropper).first);
    await tester.pumpAndSettle();
    expect(find.byType(ReplaceColorDialog), findsNothing);
    expect(pipetteModes, <bool>[true]);
    reopen?.call(const Color(0xFF010203));
    await tester.pumpAndSettle();
    expect(find.byType(ReplaceColorDialog), findsOneWidget);

    await tester.tap(find.byTooltip(l10n.eyedropper).last);
    await tester.pumpAndSettle();
    expect(find.byType(ReplaceColorDialog), findsNothing);
    expect(pipetteModes, <bool>[true, false]);
    reopen?.call(const Color(0xFF040506));
    await tester.pumpAndSettle();
    expect(find.byType(ReplaceColorDialog), findsOneWidget);
  });

  testWidgets('ok action applies current values and closes dialog', (
    tester,
  ) async {
    final hostContext = await _pumpHost(tester);
    final l10n = AppLocalizations.of(hostContext)!;
    (Rect?, Color, Color, double)? applied;

    await _openDialog(
      tester,
      hostContext,
      buildDialog: (context) => ReplaceColorDialog(
        parentContext: hostContext,
        onApply: (area, from, to, tol) {
          applied = (area, from, to, tol);
        },
        onCancel: () {},
        onStartSelectAreaMode: (_) {},
        onStartPipetteMode: (_, __) {},
        readSelectedArea: () => const Rect.fromLTWH(5, 6, 7, 8),
        readColorToReplace: () => const Color(0xFF111111),
        readNewColor: () => const Color(0xFF222222),
        readTolerance: () => 9,
        selectedArea: const Rect.fromLTWH(5, 6, 7, 8),
        colorToReplace: const Color(0xFF111111),
        newColor: const Color(0xFF222222),
        tolerance: 9,
      ),
    );

    await tester.tap(find.text(l10n.ok).last);
    await tester.pumpAndSettle();

    expect(applied, isNotNull);
    expect(applied!.$1, const Rect.fromLTWH(5, 6, 7, 8));
    expect(applied!.$4, 9);
    expect(find.byType(ReplaceColorDialog), findsNothing);
  });
}

Future<BuildContext> _pumpHost(WidgetTester tester) async {
  late BuildContext context;
  await tester.pumpWidget(
    buildLocalizedTestApp(
      withScaffold: false,
      child: Builder(
        builder: (buildContext) {
          context = buildContext;
          return const SizedBox.shrink();
        },
      ),
    ),
  );
  await tester.pump();
  return context;
}

Future<void> _openDialog(
  WidgetTester tester,
  BuildContext hostContext, {
  required Widget Function(BuildContext context) buildDialog,
}) async {
  unawaited(showDialog<void>(context: hostContext, builder: buildDialog));
  await tester.pumpAndSettle();
}
