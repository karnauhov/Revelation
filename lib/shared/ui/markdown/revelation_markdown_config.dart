import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_strong_origin_info_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_syntax.dart';
import 'package:revelation/shared/utils/description_markdown_tokens.dart';

typedef RevelationMarkdownImageWidgetBuilder =
    Widget Function(BuildContext context, RevelationMarkdownImageData image);
typedef RevelationMarkdownYoutubeWidgetBuilder =
    Widget Function(BuildContext context, RevelationMarkdownYoutubeData video);
typedef RevelationMarkdownUnknownBlockWidgetBuilder =
    Widget Function(
      BuildContext context,
      RevelationMarkdownUnknownBlockData block,
    );

md.ExtensionSet buildRevelationMarkdownExtensionSet() {
  return md.ExtensionSet(
    <md.BlockSyntax>[
      const RevelationMarkdownImageBlockSyntax(),
      const RevelationMarkdownYoutubeBlockSyntax(),
      const RevelationMarkdownUnknownBlockSyntax(),
      ...md.ExtensionSet.gitHubFlavored.blockSyntaxes,
    ],
    <md.InlineSyntax>[
      RevelationMarkdownStrongOriginInfoSyntax(),
      md.EmojiSyntax(),
      ...md.ExtensionSet.gitHubFlavored.inlineSyntaxes,
    ],
  );
}

Map<String, MarkdownElementBuilder> buildRevelationMarkdownBuilders({
  required RevelationMarkdownImageWidgetBuilder imageBuilder,
  required RevelationMarkdownYoutubeWidgetBuilder youtubeBuilder,
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
    RevelationMarkdownYoutubeData.tag: _RevelationMarkdownYoutubeElementBuilder(
      youtubeBuilder: youtubeBuilder,
    ),
    strongOriginInfoMarkdownTag:
        _RevelationMarkdownStrongOriginInfoElementBuilder(),
    RevelationMarkdownUnknownBlockData.tag:
        _RevelationMarkdownUnknownBlockElementBuilder(
          unknownBlockBuilder: unknownBlockBuilder,
        ),
  };
}

Map<String, MarkdownPaddingBuilder> buildRevelationMarkdownPaddingBuilders() {
  return <String, MarkdownPaddingBuilder>{
    'img': _VerticalMarkdownImagePaddingBuilder(),
    RevelationMarkdownYoutubeData.tag: _VerticalMarkdownImagePaddingBuilder(),
    RevelationMarkdownUnknownBlockData.tag:
        _VerticalMarkdownImagePaddingBuilder(),
  };
}

class _RevelationMarkdownStrongOriginInfoElementBuilder
    extends MarkdownElementBuilder {
  @override
  Widget? visitElementAfterWithContext(
    BuildContext context,
    md.Element element,
    TextStyle? preferredStyle,
    TextStyle? parentStyle,
  ) {
    final colorScheme = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final screenWidth = MediaQuery.sizeOf(context).width;
    final tooltipMaxWidth = screenWidth > 432 ? 420.0 : screenWidth - 12.0;
    final tooltipKey = GlobalKey<TooltipState>();

    return Tooltip(
      key: tooltipKey,
      message: l10n.strong_origin_tooltip,
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

class _RevelationMarkdownYoutubeElementBuilder extends MarkdownElementBuilder {
  _RevelationMarkdownYoutubeElementBuilder({required this.youtubeBuilder});

  final RevelationMarkdownYoutubeWidgetBuilder youtubeBuilder;

  @override
  bool isBlockElement() => true;

  @override
  Widget? visitElementAfterWithContext(
    BuildContext context,
    md.Element element,
    TextStyle? preferredStyle,
    TextStyle? parentStyle,
  ) {
    final video = RevelationMarkdownYoutubeData.fromMarkdownElement(element);
    if (video == null) {
      return const SizedBox.shrink();
    }
    return youtubeBuilder(context, video);
  }
}

class _VerticalMarkdownImagePaddingBuilder extends MarkdownPaddingBuilder {
  @override
  EdgeInsets getPadding() => const EdgeInsets.symmetric(vertical: 8);
}
