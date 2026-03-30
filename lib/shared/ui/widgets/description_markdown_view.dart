import 'package:flutter/material.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_body.dart';

class DescriptionMarkdownView extends StatelessWidget {
  final String data;
  final bool scrollable;
  final EdgeInsets padding;
  final GreekStrongTapHandler? onGreekStrongTap;
  final GreekStrongPickerTapHandler? onGreekStrongPickerTap;
  final WordTapHandler? onWordTap;
  final MarkdownImageLoader? markdownImageLoader;

  const DescriptionMarkdownView({
    required this.data,
    this.scrollable = true,
    this.padding = EdgeInsets.zero,
    this.onGreekStrongTap,
    this.onGreekStrongPickerTap,
    this.onWordTap,
    this.markdownImageLoader,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
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
      return SingleChildScrollView(
        child: RevelationMarkdownBody(
          data: data,
          padding: padding,
          onTapLink: handleTapLink,
          markdownImageLoader: markdownImageLoader,
        ),
      );
    }

    return RevelationMarkdownBody(
      data: data,
      padding: padding,
      onTapLink: handleTapLink,
      markdownImageLoader: markdownImageLoader,
    );
  }
}
