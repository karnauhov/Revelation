import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_markdown_tokens.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strong_usage_bible_reference_markdown_tokens.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strong_usage_bible_text_provider.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_origin_info_markdown.dart';
import 'package:revelation/features/strongs_dictionary/presentation/widgets/strong_usage_bible_reference_markdown.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

class StrongDictionaryEntryView extends StatelessWidget {
  const StrongDictionaryEntryView({
    required this.strongNumber,
    required this.markdown,
    required this.onStrongNumberSelected,
    required this.onStrongNumberPickerRequested,
    required this.onNavigateBackward,
    required this.onNavigateForward,
    this.padding = const EdgeInsets.fromLTRB(6, 0, 6, 6),
    this.navigationEnabled = true,
    this.exportPdfEnabled = true,
    this.copyEnabled = true,
    this.backButtonKey = const Key('strong_dictionary_nav_back'),
    this.pickerButtonKey = const Key('strong_dictionary_nav_picker'),
    this.forwardButtonKey = const Key('strong_dictionary_nav_forward'),
    this.bibleTextProvider,
    this.copyBibleText,
    this.popBeforeBibleNavigation = false,
    super.key,
  });

  final int strongNumber;
  final String markdown;
  final ValueChanged<int> onStrongNumberSelected;
  final void Function(BuildContext context, int strongNumber)
  onStrongNumberPickerRequested;
  final VoidCallback onNavigateBackward;
  final VoidCallback onNavigateForward;
  final EdgeInsets padding;
  final bool navigationEnabled;
  final bool exportPdfEnabled;
  final bool copyEnabled;
  final Key backButtonKey;
  final Key pickerButtonKey;
  final Key forwardButtonKey;
  final StrongUsageBibleTextProvider? bibleTextProvider;
  final StrongUsageBibleTextCopyHandler? copyBibleText;
  final bool popBeforeBibleNavigation;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final actionMarkdown = stripStrongUsageBibleReferenceTitles(
      stripStrongArticleInfoMarkdownMarkers(markdown),
    );

    return DescriptionMarkdownView(
      data: markdown,
      exportPdfMarkdown: actionMarkdown,
      copyMarkdown: actionMarkdown,
      inlineSyntaxes: buildStrongArticleInfoInlineSyntaxes(),
      elementBuilders: <String, MarkdownElementBuilder>{
        ...buildStrongArticleInfoMarkdownBuilders(),
        ...buildStrongUsageBibleReferenceBuilders(
          onGreekStrongTap: (selectedStrongNumber, _) {
            onStrongNumberSelected(selectedStrongNumber);
          },
          onGreekStrongPickerTap: (selectedStrongNumber, linkContext) {
            onStrongNumberPickerRequested(linkContext, selectedStrongNumber);
          },
          bibleTextProvider: bibleTextProvider,
          copyBibleText: copyBibleText,
          popBeforeBibleNavigation: popBeforeBibleNavigation,
        ),
      },
      padding: padding,
      toolbarButtonExtent: 36,
      exportPdfEnabled: exportPdfEnabled,
      copyEnabled: copyEnabled,
      exportPdfDocumentTitle: 'G$strongNumber',
      toolbarActions: [
        DescriptionMarkdownToolbarButton(
          buttonKey: backButtonKey,
          tooltip: localizations.previous_dictionary_entry,
          icon: Icons.arrow_back_ios_new_rounded,
          iconSize: 18,
          buttonExtent: 36,
          enabled: navigationEnabled,
          onPressed: onNavigateBackward,
        ),
        DescriptionMarkdownToolbarButton(
          buttonKey: pickerButtonKey,
          tooltip: localizations.strong_number,
          icon: Icons.numbers_rounded,
          iconSize: 20,
          buttonExtent: 36,
          enabled: navigationEnabled,
          onPressed: () => onStrongNumberPickerRequested(context, strongNumber),
        ),
        DescriptionMarkdownToolbarButton(
          buttonKey: forwardButtonKey,
          tooltip: localizations.next_dictionary_entry,
          icon: Icons.arrow_forward_ios_rounded,
          iconSize: 18,
          buttonExtent: 36,
          enabled: navigationEnabled,
          onPressed: onNavigateForward,
        ),
      ],
      onGreekStrongTap: (selectedStrongNumber, _) {
        onStrongNumberSelected(selectedStrongNumber);
      },
      onGreekStrongPickerTap: (selectedStrongNumber, linkContext) {
        onStrongNumberPickerRequested(linkContext, selectedStrongNumber);
      },
    );
  }
}
