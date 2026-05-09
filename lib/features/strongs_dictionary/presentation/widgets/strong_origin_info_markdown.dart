import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_markdown_tokens.dart';
import 'package:revelation/l10n/app_localizations.dart';

List<md.InlineSyntax> buildStrongOriginInfoInlineSyntaxes() {
  return <md.InlineSyntax>[StrongOriginInfoMarkdownSyntax()];
}

Map<String, MarkdownElementBuilder> buildStrongOriginInfoMarkdownBuilders() {
  return <String, MarkdownElementBuilder>{
    strongOriginInfoMarkdownTag: StrongOriginInfoMarkdownElementBuilder(),
  };
}

class StrongOriginInfoMarkdownSyntax extends md.InlineSyntax {
  StrongOriginInfoMarkdownSyntax()
    : super(RegExp.escape(strongOriginInfoMarkdownMarker));

  @override
  bool onMatch(md.InlineParser parser, Match match) {
    parser.addNode(md.Element.empty(strongOriginInfoMarkdownTag));
    return true;
  }
}

class StrongOriginInfoMarkdownElementBuilder extends MarkdownElementBuilder {
  @override
  Widget? visitElementAfterWithContext(
    BuildContext context,
    md.Element element,
    TextStyle? preferredStyle,
    TextStyle? parentStyle,
  ) {
    final colorScheme = Theme.of(context).colorScheme;
    final localizations = AppLocalizations.of(context)!;
    final screenWidth = MediaQuery.sizeOf(context).width;
    final tooltipMaxWidth = screenWidth > 432 ? 420.0 : screenWidth - 12.0;
    final tooltipKey = GlobalKey<TooltipState>();

    return Tooltip(
      key: tooltipKey,
      message: localizations.strong_origin_tooltip,
      constraints: BoxConstraints(maxWidth: tooltipMaxWidth),
      showDuration: const Duration(seconds: 12),
      preferBelow: false,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          tooltipKey.currentState?.ensureTooltipVisible();
        },
        child: SizedBox(
          key: const Key('description_markdown_strong_origin_info_button'),
          width: 32,
          height: 32,
          child: Center(
            child: Icon(
              Icons.info_outline,
              size: 18,
              color: colorScheme.primary,
            ),
          ),
        ),
      ),
    );
  }
}
