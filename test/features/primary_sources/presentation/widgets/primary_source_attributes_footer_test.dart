@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_attributes_footer.dart';
import 'package:revelation/l10n/app_localizations.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('a Strong credit selects the entry in its source panel', (
    tester,
  ) async {
    int? selected;
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: PrimarySourceAttributesFooter(
          credits: const [(text: 'G3056', url: 'strong:G3056')],
          onGreekStrongTap: (number, _) => selected = number,
        ),
      ),
    );
    final paragraph = tester.renderObject<RenderParagraph>(
      find.text('G3056', findRichText: true),
    );
    final link = paragraph
        .getBoxesForSelection(
          const TextSelection(baseOffset: 0, extentOffset: 5),
        )
        .single
        .toRect();
    await tester.tapAt(paragraph.localToGlobal(link.center));
    await tester.pump();
    expect(selected, 3056);
  });
  testWidgets('empty credits take no frame space', (tester) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const PrimarySourceAttributesFooter(credits: []),
      ),
    );
    expect(find.byType(Text), findsNothing);
  });

  testWidgets('long credits wrap in full at double text scale', (tester) async {
    const text =
        'The Center for the Study of New Testament Manuscripts digitized Codex Alexandrinus at the British Library';
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: Center(
          child: SizedBox(
            width: 240,
            child: MediaQuery(
              data: const MediaQueryData(textScaler: TextScaler.linear(2)),
              child: const PrimarySourceAttributesFooter(
                credits: [(text: text, url: '')],
              ),
            ),
          ),
        ),
      ),
    );
    final label = find.text(text, findRichText: true);
    expect(label, findsOneWidget);
    expect(tester.getSize(label).height, greaterThan(80));
    expect(tester.widget<RichText>(label).maxLines, isNull);
    expect(tester.takeException(), isNull);
  });

  testWidgets('shows explicit mode hints for area selection and pipette', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const PrimarySourceAttributesFooter(
          credits: [(text: 'A', url: 'https://example.com')],
          selectAreaMode: true,
          pipetteMode: false,
        ),
      ),
    );
    await tester.pump();
    final context = tester.element(find.byType(PrimarySourceAttributesFooter));
    final l10n = AppLocalizations.of(context)!;
    expect(find.text('A', findRichText: true), findsNothing);
    expect(find.text(l10n.select_area_description), findsOneWidget);

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const PrimarySourceAttributesFooter(
          credits: [(text: 'A', url: 'https://example.com')],
          selectAreaMode: false,
          pipetteMode: true,
        ),
      ),
    );
    await tester.pump();
    expect(find.text('A', findRichText: true), findsNothing);
    expect(find.text(l10n.pick_color_description), findsOneWidget);
  });

  testWidgets('renders links and mobile-web quality notice in default mode', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const PrimarySourceAttributesFooter(
          credits: [
            (text: 'Attr A', url: 'https://example.com/a'),
            (text: 'Attr B', url: ''),
          ],
          selectAreaMode: false,
          pipetteMode: false,
          hasReducedResolution: true,
        ),
      ),
    );
    await tester.pump();

    final context = tester.element(find.byType(PrimarySourceAttributesFooter));
    final l10n = AppLocalizations.of(context)!;

    expect(find.textContaining('Attr A', findRichText: true), findsOneWidget);
    expect(find.textContaining('Attr B', findRichText: true), findsOneWidget);
    expect(
      find.textContaining(l10n.low_quality, findRichText: true),
      findsOneWidget,
    );
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const PrimarySourceAttributesFooter(
          credits: [(text: 'Attr A', url: '')],
        ),
      ),
    );
    expect(
      find.textContaining(l10n.low_quality, findRichText: true),
      findsNothing,
    );
    expect(find.text('Attr A', findRichText: true), findsOneWidget);
  });
}
