import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_marked_verse.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';

void main() {
  testWidgets(
    'source weighting, dictionary choices, hover and Hebrew namespaces',
    (tester) async {
      int? opened;
      setDefaultGreekStrongTapHandler((n, _) => opened = n);
      addTearDown(() => setDefaultGreekStrongTapHandler(null));
      await tester.pumpWidget(
        const MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          home: Scaffold(
            body: BibleMarkedVerse(
              text:
                  'staff G4464 weak g0846 and G2532 clay G2763 two G00846 G4464 token H4464 unmarked',
              highlights: {4464: 1, 846: .15, 2532: 0},
              showWeights: true,
              linkPrefix: 'source',
            ),
          ),
        ),
      );
      Color color(String word) =>
          tester.widget<Text>(find.text(word)).style!.color!;
      expect(
        color('weak').computeLuminance(),
        greaterThan(color('staff').computeLuminance()),
      );
      expect(color('two'), color('staff'));
      expect(color('and'), color('clay'));
      expect(color('token'), color('clay'));
      expect(find.byTooltip('G2532 · weight 0'), findsOneWidget);
      final mouse = await tester.createGesture(kind: PointerDeviceKind.mouse);
      await mouse.addPointer();
      await mouse.moveTo(tester.getCenter(find.text('weak')));
      await tester.pump(const Duration(seconds: 2));
      await tester.pump(const Duration(milliseconds: 200));
      expect(find.text('G846 · weight 0.15'), findsOneWidget);
      await mouse.removePointer();
      await tester.tap(find.text('and'));
      expect(opened, 2532);
      await tester.tap(find.text('two'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('G4464').last);
      await tester.pumpAndSettle();
      expect(opened, 4464);
      await tester.tap(find.text('token'));
      await tester.pumpAndSettle();
      expect(find.text('H4464'), findsOneWidget);
      expect(find.text('Open in dictionary'), findsOneWidget);
      expect(opened, 4464);
    },
  );

  testWidgets(
    'result translation colours only matching G identifiers and keeps punctuation',
    (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          home: Scaffold(
            body: BibleMarkedVerse(
              text: 'a staff, G4464 rod H4464 and unmarked.',
              highlights: {4464: 1},
            ),
          ),
        ),
      );
      final text = tester.widget<Text>(find.byType(Text));
      final span = text.textSpan! as TextSpan;
      expect(span.toPlainText(), 'a staff, rod and unmarked.');
      expect(
        span.children!
            .whereType<TextSpan>()
            .where((s) => s.style?.color != null)
            .map((s) => s.text),
        ['staff,'],
      );
    },
  );
}
