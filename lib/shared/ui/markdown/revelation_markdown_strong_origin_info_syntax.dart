import 'package:markdown/markdown.dart' as md;
import 'package:revelation/shared/utils/description_markdown_tokens.dart';

class RevelationMarkdownStrongOriginInfoSyntax extends md.InlineSyntax {
  RevelationMarkdownStrongOriginInfoSyntax()
    : super(RegExp.escape(strongOriginInfoMarkdownMarker));

  @override
  bool onMatch(md.InlineParser parser, Match match) {
    parser.addNode(md.Element.empty(strongOriginInfoMarkdownTag));
    return true;
  }
}
