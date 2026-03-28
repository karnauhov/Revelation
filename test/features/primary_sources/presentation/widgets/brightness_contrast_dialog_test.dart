@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/brightness_contrast_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('shows initial brightness and contrast values', (tester) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: BrightnessContrastDialog(
          brightness: 12,
          contrast: 88,
          onApply: (_, __) {},
          onCancel: () {},
        ),
      ),
    );
    await tester.pump();

    final context = tester.element(find.byType(BrightnessContrastDialog));
    final l10n = AppLocalizations.of(context)!;

    expect(find.text('${l10n.brightness}: 12'), findsOneWidget);
    expect(find.text('${l10n.contrast}: 88'), findsOneWidget);
  });

  testWidgets('brightness slider commits value through onApply on change end', (
    tester,
  ) async {
    final applied = <(double, double)>[];

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: BrightnessContrastDialog(
          brightness: 0,
          contrast: 100,
          onApply: (b, c) => applied.add((b, c)),
          onCancel: () {},
        ),
      ),
    );
    await tester.pump();

    final sliders = tester.widgetList<Slider>(find.byType(Slider)).toList();
    sliders.first.onChanged!(25);
    await tester.pump();
    sliders.first.onChangeEnd!(25);
    await tester.pump();

    expect(applied, isNotEmpty);
    expect(applied.last.$1, 25);
    expect(applied.last.$2, 100);
  });

  testWidgets('contrast slider commits value through onApply on change end', (
    tester,
  ) async {
    final applied = <(double, double)>[];

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: BrightnessContrastDialog(
          brightness: 10,
          contrast: 100,
          onApply: (b, c) => applied.add((b, c)),
          onCancel: () {},
        ),
      ),
    );
    await tester.pump();

    final sliders = tester.widgetList<Slider>(find.byType(Slider)).toList();
    sliders.last.onChanged!(120);
    await tester.pump();
    sliders.last.onChangeEnd!(120);
    await tester.pump();

    expect(applied, isNotEmpty);
    expect(applied.last.$1, 10);
    expect(applied.last.$2, 120);
  });

  testWidgets('reset button triggers onCancel callback', (tester) async {
    var canceled = false;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: BrightnessContrastDialog(
          onApply: (_, __) {},
          onCancel: () {
            canceled = true;
          },
        ),
      ),
    );
    await tester.pump();

    final context = tester.element(find.byType(BrightnessContrastDialog));
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.text(l10n.reset));
    await tester.pump();

    expect(canceled, isTrue);
  });
}
