import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';

typedef RevelationMarkdownImageWidgetBuilder =
    Widget Function(BuildContext context, RevelationMarkdownImageData image);

md.ExtensionSet buildRevelationMarkdownExtensionSet() {
  return md.ExtensionSet(
    <md.BlockSyntax>[
      const RevelationMarkdownImageBlockSyntax(),
      ...md.ExtensionSet.gitHubFlavored.blockSyntaxes,
    ],
    <md.InlineSyntax>[
      md.EmojiSyntax(),
      ...md.ExtensionSet.gitHubFlavored.inlineSyntaxes,
    ],
  );
}

Map<String, MarkdownElementBuilder> buildRevelationMarkdownBuilders({
  required RevelationMarkdownImageWidgetBuilder imageBuilder,
}) {
  final sharedBuilder = _RevelationMarkdownImageElementBuilder(
    imageBuilder: imageBuilder,
    isBlock: false,
  );
  return <String, MarkdownElementBuilder>{
    'img': sharedBuilder,
    RevelationMarkdownImageBlockSyntax.tag:
        _RevelationMarkdownImageElementBuilder(
          imageBuilder: imageBuilder,
          isBlock: true,
        ),
  };
}

Map<String, MarkdownPaddingBuilder> buildRevelationMarkdownPaddingBuilders() {
  return <String, MarkdownPaddingBuilder>{
    'img': _VerticalMarkdownImagePaddingBuilder(),
  };
}

class _RevelationMarkdownImageElementBuilder extends MarkdownElementBuilder {
  _RevelationMarkdownImageElementBuilder({
    required this.imageBuilder,
    required this.isBlock,
  });

  final RevelationMarkdownImageWidgetBuilder imageBuilder;
  final bool isBlock;

  @override
  bool isBlockElement() => isBlock;

  @override
  Widget? visitElementAfterWithContext(
    BuildContext context,
    md.Element element,
    TextStyle? preferredStyle,
    TextStyle? parentStyle,
  ) {
    final image = RevelationMarkdownImageData.fromMarkdownElement(element);
    if (image == null) {
      return const SizedBox.shrink();
    }
    return imageBuilder(context, image);
  }
}

class _VerticalMarkdownImagePaddingBuilder extends MarkdownPaddingBuilder {
  @override
  EdgeInsets getPadding() => const EdgeInsets.symmetric(vertical: 8);
}
