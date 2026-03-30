import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_basic_image_builder.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_config.dart';
import 'package:revelation/shared/ui/markdown/markdown_utils.dart';

class DescriptionMarkdownView extends StatelessWidget {
  final String data;
  final bool scrollable;
  final EdgeInsets padding;
  final GreekStrongTapHandler? onGreekStrongTap;
  final GreekStrongPickerTapHandler? onGreekStrongPickerTap;
  final WordTapHandler? onWordTap;

  const DescriptionMarkdownView({
    required this.data,
    this.scrollable = true,
    this.padding = EdgeInsets.zero,
    this.onGreekStrongTap,
    this.onGreekStrongPickerTap,
    this.onWordTap,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    void handleTapLink(String text, String? href, String title) {
      handleAppLink(
        context,
        href,
        onGreekStrongTap: onGreekStrongTap,
        onGreekStrongPickerTap: onGreekStrongPickerTap,
        onWordTap: onWordTap,
      );
    }

    if (scrollable) {
      return Markdown(
        data: data,
        padding: padding,
        styleSheet: getMarkdownStyleSheet(theme, colorScheme),
        extensionSet: buildRevelationMarkdownExtensionSet(),
        builders: buildRevelationMarkdownBuilders(
          imageBuilder: buildBasicRevelationMarkdownImage,
        ),
        paddingBuilders: buildRevelationMarkdownPaddingBuilders(),
        onTapLink: handleTapLink,
      );
    }

    return Padding(
      padding: padding,
      child: MarkdownBody(
        data: data,
        styleSheet: getMarkdownStyleSheet(theme, colorScheme),
        extensionSet: buildRevelationMarkdownExtensionSet(),
        builders: buildRevelationMarkdownBuilders(
          imageBuilder: buildBasicRevelationMarkdownImage,
        ),
        paddingBuilders: buildRevelationMarkdownPaddingBuilders(),
        onTapLink: handleTapLink,
      ),
    );
  }
}
