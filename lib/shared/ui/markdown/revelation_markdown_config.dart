import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_syntax.dart';

typedef RevelationMarkdownImageWidgetBuilder =
    Widget Function(BuildContext context, RevelationMarkdownImageData image);
typedef RevelationMarkdownUnknownBlockWidgetBuilder =
    Widget Function(
      BuildContext context,
      RevelationMarkdownUnknownBlockData block,
    );

md.ExtensionSet buildRevelationMarkdownExtensionSet() {
  return md.ExtensionSet(
    <md.BlockSyntax>[
      const RevelationMarkdownImageBlockSyntax(),
      const RevelationMarkdownUnknownBlockSyntax(),
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
  required RevelationMarkdownUnknownBlockWidgetBuilder unknownBlockBuilder,
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
    RevelationMarkdownUnknownBlockData.tag:
        _RevelationMarkdownUnknownBlockElementBuilder(
          unknownBlockBuilder: unknownBlockBuilder,
        ),
  };
}

Map<String, MarkdownPaddingBuilder> buildRevelationMarkdownPaddingBuilders() {
  return <String, MarkdownPaddingBuilder>{
    'img': _VerticalMarkdownImagePaddingBuilder(),
    RevelationMarkdownUnknownBlockData.tag:
        _VerticalMarkdownImagePaddingBuilder(),
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

class _RevelationMarkdownUnknownBlockElementBuilder
    extends MarkdownElementBuilder {
  _RevelationMarkdownUnknownBlockElementBuilder({
    required this.unknownBlockBuilder,
  });

  final RevelationMarkdownUnknownBlockWidgetBuilder unknownBlockBuilder;

  @override
  bool isBlockElement() => true;

  @override
  Widget? visitElementAfterWithContext(
    BuildContext context,
    md.Element element,
    TextStyle? preferredStyle,
    TextStyle? parentStyle,
  ) {
    final block = RevelationMarkdownUnknownBlockData.fromMarkdownElement(
      element,
    );
    if (block == null) {
      return const SizedBox.shrink();
    }
    return unknownBlockBuilder(context, block);
  }
}

class _VerticalMarkdownImagePaddingBuilder extends MarkdownPaddingBuilder {
  @override
  EdgeInsets getPadding() => const EdgeInsets.symmetric(vertical: 8);
}
