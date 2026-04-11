import 'package:markdown/markdown.dart' as md;
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_data.dart';

class RevelationMarkdownUnknownBlockSyntax extends md.BlockSyntax {
  const RevelationMarkdownUnknownBlockSyntax();

  static final RegExp _openingPattern = RegExp(
    r'^\s*\{\{([A-Za-z][A-Za-z0-9_-]*)\}\}\s*$',
  );
  static final RegExp _closingPattern = RegExp(
    r'^\s*\{\{\/([A-Za-z][A-Za-z0-9_-]*)\}\}\s*$',
  );

  @override
  RegExp get pattern => _openingPattern;

  @override
  bool canParse(md.BlockParser parser) {
    final blockName = _parseBlockName(
      line: parser.current.content,
      pattern: _openingPattern,
    );
    return blockName != null &&
        blockName != RevelationMarkdownImageBlockSyntax.blockName;
  }

  @override
  md.Node parse(md.BlockParser parser) {
    final blockName =
        _parseBlockName(
          line: parser.current.content,
          pattern: _openingPattern,
        ) ??
        'unknown';
    parser.advance();

    while (!parser.isDone) {
      final closingBlockName = _parseBlockName(
        line: parser.current.content,
        pattern: _closingPattern,
      );
      if (closingBlockName == blockName) {
        parser.advance();
        break;
      }
      parser.advance();
    }

    final element = md.Element.empty(RevelationMarkdownUnknownBlockData.tag);
    element.attributes['name'] = blockName;
    return element;
  }

  String? _parseBlockName({required String line, required RegExp pattern}) {
    final match = pattern.firstMatch(line);
    return match?.group(1)?.trim();
  }
}
