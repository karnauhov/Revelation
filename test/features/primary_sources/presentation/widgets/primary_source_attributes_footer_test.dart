@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_attributes_footer.dart';
import 'package:revelation/l10n/app_localizations.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets(
    'renders nothing when attributes are missing or permissions denied',
    (tester) async {
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: const PrimarySourceAttributesFooter(
            attributes: null,
            permissionsReceived: true,
            selectAreaMode: false,
            pipetteMode: false,
            isMobileWeb: false,
          ),
        ),
      );
      await tester.pump();
      expect(find.byType(SizedBox), findsOneWidget);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: const PrimarySourceAttributesFooter(
            attributes: <Map<String, String>>[
              {'text': 'A', 'url': 'https://example.com'},
            ],
            permissionsReceived: false,
            selectAreaMode: false,
            pipetteMode: false,
            isMobileWeb: false,
          ),
        ),
      );
      await tester.pump();
      expect(find.text('A'), findsNothing);
    },
  );

  testWidgets('shows explicit mode hints for area selection and pipette', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const PrimarySourceAttributesFooter(
          attributes: <Map<String, String>>[
            {'text': 'A', 'url': 'https://example.com'},
          ],
          permissionsReceived: true,
          selectAreaMode: true,
          pipetteMode: false,
          isMobileWeb: false,
        ),
      ),
    );
    await tester.pump();
    final context = tester.element(find.byType(PrimarySourceAttributesFooter));
    final l10n = AppLocalizations.of(context)!;
    expect(find.text(l10n.select_area_description), findsOneWidget);

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const PrimarySourceAttributesFooter(
          attributes: <Map<String, String>>[
            {'text': 'A', 'url': 'https://example.com'},
          ],
          permissionsReceived: true,
          selectAreaMode: false,
          pipetteMode: true,
          isMobileWeb: false,
        ),
      ),
    );
    await tester.pump();
    expect(find.text(l10n.pick_color_description), findsOneWidget);
  });

  testWidgets('renders links and mobile-web quality notice in default mode', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const PrimarySourceAttributesFooter(
          attributes: <Map<String, String>>[
            {'text': 'Attr A', 'url': 'https://example.com/a'},
            {'text': 'Attr B', 'url': ''},
          ],
          permissionsReceived: true,
          selectAreaMode: false,
          pipetteMode: false,
          isMobileWeb: true,
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
  });
}
