import 'dart:convert';

import 'package:markdown/markdown.dart' as md;
import 'package:revelation/shared/ui/markdown/revelation_markdown_config.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';

List<RevelationMarkdownImageData> extractRevelationMarkdownImages(
  String markdown,
) {
  final document = md.Document(
    extensionSet: buildRevelationMarkdownExtensionSet(),
    encodeHtml: false,
  );
  final nodes = document.parseLines(const LineSplitter().convert(markdown));
  final images = <RevelationMarkdownImageData>[];

  void visit(md.Node node) {
    if (node is! md.Element) {
      return;
    }

    if (node.tag == 'img' ||
        node.tag == RevelationMarkdownImageBlockSyntax.tag) {
      final image = RevelationMarkdownImageData.fromMarkdownElement(node);
      if (image != null) {
        images.add(image);
      }
    }

    final children = node.children;
    if (children == null || children.isEmpty) {
      return;
    }
    for (final child in children) {
      visit(child);
    }
  }

  for (final node in nodes) {
    visit(node);
  }

  return images;
}
