import 'package:markdown/markdown.dart' as md;

class RevelationMarkdownUnknownBlockData {
  const RevelationMarkdownUnknownBlockData({required this.name});

  static const String tag = 'revelation-unknown-block';

  final String name;

  static RevelationMarkdownUnknownBlockData? fromMarkdownElement(
    md.Element element,
  ) {
    final name = (element.attributes['name'] ?? '').trim();
    if (name.isEmpty) {
      return null;
    }
    return RevelationMarkdownUnknownBlockData(name: name);
  }
}
