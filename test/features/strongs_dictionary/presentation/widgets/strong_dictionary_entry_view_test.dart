@Tags(['widget'])
import 'dart:ui' show PointerDeviceKind;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_markdown_tokens.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  setUp(() {
    StrongUsageReferenceDetailRegistry.instance.clearForTesting();
  });

  testWidgets(
    'StrongDictionaryEntryView renders word analysis tooltip marker',
    (tester) async {
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: StrongDictionaryEntryView(
            strongNumber: 1,
            markdown: 'Word analysis:$strongOriginInfoMarkdownMarker**Alpha**',
            onStrongNumberSelected: (_) {},
            onStrongNumberPickerRequested: (_, __) {},
            onNavigateBackward: () {},
            onNavigateForward: () {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      final context = tester.element(find.byType(StrongDictionaryEntryView));
      final localizations = AppLocalizations.of(context)!;
      final markdownView = tester.widget<DescriptionMarkdownView>(
        find.byType(DescriptionMarkdownView),
      );

      expect(
        find.byKey(const Key('description_markdown_strong_origin_info_button')),
        findsOneWidget,
      );
      expect(
        find.byTooltip(localizations.strong_origin_tooltip),
        findsOneWidget,
      );
      expect(find.textContaining(strongOriginInfoMarkdownMarker), findsNothing);
      expect(markdownView.exportPdfMarkdown, 'Word analysis: **Alpha**');
      expect(markdownView.copyMarkdown, 'Word analysis: **Alpha**');
    },
  );

  testWidgets(
    'StrongDictionaryEntryView renders usage Bible links with preview copy',
    (tester) async {
      String? copiedText;
      int? selectedStrongNumber;

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: StrongDictionaryEntryView(
            strongNumber: 1,
            markdown:
                'Usage:$strongUsageInfoMarkdownMarker **logos** (2): '
                '[Gen 1:1](bible:Gen1:1 "strong_usage_ref:001"); '
                '[G2](strong:G2)',
            bibleTextProvider: const _FakeStrongUsageBibleTextProvider(
              <String, String>{'001': 'verse text'},
            ),
            copyBibleText: (text) async {
              copiedText = text;
            },
            onStrongNumberSelected: (strongNumber) {
              selectedStrongNumber = strongNumber;
            },
            onStrongNumberPickerRequested: (_, __) {},
            onNavigateBackward: () {},
            onNavigateForward: () {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      final markdownView = tester.widget<DescriptionMarkdownView>(
        find.byType(DescriptionMarkdownView),
      );
      final context = tester.element(find.byType(StrongDictionaryEntryView));
      final localizations = AppLocalizations.of(context)!;
      expect(
        find.byKey(const Key('description_markdown_strong_usage_info_button')),
        findsOneWidget,
      );
      expect(
        find.byTooltip(localizations.bible_reference_preview_loading_hint),
        findsOneWidget,
      );
      expect(find.textContaining(strongUsageInfoMarkdownMarker), findsNothing);
      expect(markdownView.copyMarkdown, isNot(contains('strong_usage_info')));
      expect(markdownView.copyMarkdown, contains('[Gen 1:1](bible:Gen1:1)'));

      await tester.tap(find.text('G2'));
      await tester.pump();
      expect(selectedStrongNumber, 2);

      final mouseGesture = await tester.createGesture(
        kind: PointerDeviceKind.mouse,
      );
      await mouseGesture.addPointer(location: Offset.zero);
      await mouseGesture.moveTo(tester.getCenter(find.text('Gen 1:1')));
      await tester.pump(const Duration(milliseconds: 500));

      expect(copiedText, isNull);
      expect(find.text('verse text'), findsNothing);

      await mouseGesture.removePointer();
      await tester.longPress(find.text('Gen 1:1'));
      await tester.pumpAndSettle();

      expect(copiedText, 'verse text');
      expect(find.text('verse text'), findsOneWidget);
    },
  );

  testWidgets(
    'StrongDictionaryEntryView opens full usage reference dialog from ellipsis',
    (tester) async {
      String? copiedText;
      final detailId = StrongUsageReferenceDetailRegistry.instance.register(
        const StrongUsageReferenceDetail(
          surface: 'logos',
          count: 4,
          referencesMarkdown:
              '[Gen 1:1](bible:Gen1:1 "strong_usage_ref:001"); '
              '[Gen 1:2](bible:Gen1:2 "strong_usage_ref:002"); '
              '[Gen 1:3](bible:Gen1:3 "strong_usage_ref:003"); '
              '[Gen 1:4](bible:Gen1:4 "strong_usage_ref:004")',
        ),
      );

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: StrongDictionaryEntryView(
            strongNumber: 1,
            markdown:
                'Usage: **logos** (4): '
                '[Gen 1:1](bible:Gen1:1 "strong_usage_ref:001"); '
                '[Gen 1:2](bible:Gen1:2 "strong_usage_ref:002"); '
                '[Gen 1:3](bible:Gen1:3 "strong_usage_ref:003"); '
                '[...](strong_usage_more:$detailId '
                '"strong_usage_more:$detailId")',
            bibleTextProvider: const _FakeStrongUsageBibleTextProvider(
              <String, String>{'004': 'fourth verse'},
            ),
            copyBibleText: (text) async {
              copiedText = text;
            },
            onStrongNumberSelected: (_) {},
            onStrongNumberPickerRequested: (_, __) {},
            onNavigateBackward: () {},
            onNavigateForward: () {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      final markdownView = tester.widget<DescriptionMarkdownView>(
        find.byType(DescriptionMarkdownView),
      );
      expect(markdownView.copyMarkdown, isNot(contains('strong_usage_more')));

      await tester.tap(find.text('...'));
      await tester.pumpAndSettle();

      expect(find.text('logos (4)'), findsOneWidget);
      expect(find.text('Gen 1:4'), findsOneWidget);
      expect(
        find.descendant(
          of: find.byType(AlertDialog),
          matching: find.byKey(
            const Key('description_markdown_export_pdf_button'),
          ),
        ),
        findsOneWidget,
      );
      expect(
        find.descendant(
          of: find.byType(AlertDialog),
          matching: find.byKey(const Key('description_markdown_copy_button')),
        ),
        findsOneWidget,
      );

      final detailMarkdownView = tester
          .widgetList<DescriptionMarkdownView>(
            find.byType(DescriptionMarkdownView),
          )
          .singleWhere((view) => view.data.contains('Gen 1:4'));
      expect(
        detailMarkdownView.copyMarkdown,
        isNot(contains('strong_usage_ref')),
      );
      expect(
        detailMarkdownView.exportPdfMarkdown,
        isNot(contains('strong_usage_ref')),
      );
      expect(detailMarkdownView.exportPdfDocumentTitle, 'logos (4)');

      await tester.longPress(find.text('Gen 1:4'));
      await tester.pumpAndSettle();

      expect(copiedText, 'fourth verse');
      expect(find.text('fourth verse'), findsOneWidget);
    },
  );
}

class _FakeStrongUsageBibleTextProvider
    implements StrongUsageBibleTextProvider {
  const _FakeStrongUsageBibleTextProvider(this._textsByVerseKey);

  final Map<String, String> _textsByVerseKey;

  @override
  Future<String?> loadVerseText(String verseKey) async {
    return _textsByVerseKey[verseKey];
  }
}
