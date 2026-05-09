@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_markdown_tokens.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
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
}
