import 'package:markdown/markdown.dart' as md;

class RevelationMarkdownImageBlockSyntax extends md.BlockSyntax {
  const RevelationMarkdownImageBlockSyntax();

  static const String tag = 'revelation-image';
  static final RegExp _openingPattern = RegExp(r'^\s*\{\{image\}\}\s*$');
  static final RegExp _closingPattern = RegExp(r'^\s*\{\{\/image\}\}\s*$');

  @override
  RegExp get pattern => _openingPattern;

  @override
  bool canParse(md.BlockParser parser) {
    return _openingPattern.hasMatch(parser.current.content);
  }

  @override
  md.Node parse(md.BlockParser parser) {
    parser.advance();

    final attributes = <String, String>{};
    while (!parser.isDone &&
        !_closingPattern.hasMatch(parser.current.content)) {
      final line = parser.current.content.trim();
      if (line.isNotEmpty) {
        final separatorIndex = line.indexOf(':');
        if (separatorIndex > 0) {
          final key = line.substring(0, separatorIndex).trim().toLowerCase();
          final value = _normalizeValue(line.substring(separatorIndex + 1));
          if (key.isNotEmpty && value.isNotEmpty) {
            attributes[key] = value;
          }
        }
      }
      parser.advance();
    }

    if (!parser.isDone && _closingPattern.hasMatch(parser.current.content)) {
      parser.advance();
    }

    final element = md.Element.empty(tag);
    for (final entry in attributes.entries) {
      element.attributes[entry.key] = entry.value;
    }
    return element;
  }

  String _normalizeValue(String value) {
    final trimmed = value.trim();
    if (trimmed.length >= 2) {
      final first = trimmed[0];
      final last = trimmed[trimmed.length - 1];
      if ((first == '"' && last == '"') || (first == '\'' && last == '\'')) {
        return trimmed.substring(1, trimmed.length - 1).trim();
      }
    }
    return trimmed;
  }
}
