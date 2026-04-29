import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_body.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_pdf_export.dart';

typedef DescriptionMarkdownExportPdfHandler =
    Future<String?> Function({
      required String markdown,
      required String documentTitle,
    });
typedef DescriptionMarkdownCopyHandler = Future<void> Function(String markdown);

class DescriptionMarkdownView extends StatelessWidget {
  static const EdgeInsets _toolbarButtonInset = EdgeInsets.only(top: 44);

  final String data;
  final bool scrollable;
  final EdgeInsets padding;
  final GreekStrongTapHandler? onGreekStrongTap;
  final GreekStrongPickerTapHandler? onGreekStrongPickerTap;
  final WordTapHandler? onWordTap;
  final MarkdownImageLoader? markdownImageLoader;
  final bool showExportPdfButton;
  final bool exportPdfEnabled;
  final bool copyEnabled;
  final String? exportPdfDocumentTitle;
  final DescriptionMarkdownExportPdfHandler? onExportPdfRequested;
  final DescriptionMarkdownCopyHandler? onCopyRequested;
  final List<Widget> toolbarActions;
  final FontWeight? h2FontWeight;

  const DescriptionMarkdownView({
    required this.data,
    this.scrollable = true,
    this.padding = EdgeInsets.zero,
    this.onGreekStrongTap,
    this.onGreekStrongPickerTap,
    this.onWordTap,
    this.markdownImageLoader,
    this.showExportPdfButton = true,
    this.exportPdfEnabled = true,
    this.copyEnabled = true,
    this.exportPdfDocumentTitle,
    this.onExportPdfRequested,
    this.onCopyRequested,
    this.toolbarActions = const <Widget>[],
    this.h2FontWeight,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final hasToolbar = showExportPdfButton || toolbarActions.isNotEmpty;
    final effectivePadding = hasToolbar
        ? EdgeInsets.only(
            left: padding.left,
            top: padding.top + _toolbarButtonInset.top,
            right: padding.right,
            bottom: padding.bottom,
          )
        : padding;

    void handleTapLink(String text, String? href, String title) {
      handleAppLink(
        context,
        href,
        onGreekStrongTap: onGreekStrongTap,
        onGreekStrongPickerTap: onGreekStrongPickerTap,
        onWordTap: onWordTap,
      );
    }

    Future<void> handleExportPdf() async {
      try {
        final exportPdfHandler =
            onExportPdfRequested ??
            ({required String markdown, required String documentTitle}) =>
                exportRevelationMarkdownPdf(
                  markdown: markdown,
                  documentTitle: documentTitle,
                  markdownImageLoader: markdownImageLoader,
                );

        final location = await exportPdfHandler(
          markdown: data,
          documentTitle: exportPdfDocumentTitle ?? l10n.app_name,
        );

        if (!context.mounted) {
          return;
        }

        if (location != null && location.isNotEmpty) {
          final messenger = ScaffoldMessenger.maybeOf(context);
          messenger?.showSnackBar(
            SnackBar(content: Text(l10n.file_saved_at(location))),
          );
        }
      } catch (error, stackTrace) {
        try {
          log.handle(
            error,
            stackTrace,
            'Failed to export DescriptionMarkdownView PDF',
          );
        } catch (_) {}

        if (!context.mounted) {
          return;
        }

        final messenger = ScaffoldMessenger.maybeOf(context);
        if (messenger == null) {
          return;
        }

        messenger.showSnackBar(
          SnackBar(content: Text(l10n.markdown_pdf_export_failed)),
        );
      }
    }

    Future<void> handleCopy() async {
      try {
        final copyHandler =
            onCopyRequested ??
            (String markdown) =>
                Clipboard.setData(ClipboardData(text: markdown));
        await copyHandler(data);

        if (!context.mounted) {
          return;
        }

        final messenger = ScaffoldMessenger.maybeOf(context);
        if (messenger == null) {
          return;
        }

        messenger.showSnackBar(SnackBar(content: Text(l10n.markdown_copied)));
      } catch (error, stackTrace) {
        try {
          log.handle(
            error,
            stackTrace,
            'Failed to copy DescriptionMarkdownView content',
          );
        } catch (_) {}

        if (!context.mounted) {
          return;
        }

        final messenger = ScaffoldMessenger.maybeOf(context);
        if (messenger == null) {
          return;
        }

        messenger.showSnackBar(
          SnackBar(content: Text(l10n.markdown_copy_failed)),
        );
      }
    }

    final markdownBody = RevelationMarkdownBody(
      data: data,
      padding: effectivePadding,
      onTapLink: handleTapLink,
      markdownImageLoader: markdownImageLoader,
      h2FontWeight: h2FontWeight,
    );

    final content = scrollable
        ? SingleChildScrollView(child: markdownBody)
        : markdownBody;

    if (!hasToolbar) {
      return content;
    }

    final toolbarChildren = <Widget>[
      if (showExportPdfButton)
        DescriptionMarkdownToolbarButton(
          buttonKey: const Key('description_markdown_export_pdf_button'),
          tooltip: l10n.export_pdf_content,
          icon: Icons.file_download_outlined,
          enabled: exportPdfEnabled,
          onPressed: () => unawaited(handleExportPdf()),
        ),
      if (showExportPdfButton)
        DescriptionMarkdownToolbarButton(
          buttonKey: const Key('description_markdown_copy_button'),
          tooltip: l10n.copy_content,
          icon: Icons.content_copy_outlined,
          enabled: copyEnabled,
          onPressed: () => unawaited(handleCopy()),
        ),
      ...toolbarActions,
    ];

    return Stack(
      children: [
        content,
        Positioned(
          top: 4,
          left: 4,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              for (var i = 0; i < toolbarChildren.length; i++) ...[
                if (i > 0) const SizedBox(width: 8),
                toolbarChildren[i],
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class DescriptionMarkdownToolbarButton extends StatelessWidget {
  const DescriptionMarkdownToolbarButton({
    required this.buttonKey,
    required this.tooltip,
    required this.icon,
    required this.onPressed,
    this.enabled = true,
    this.iconSize = 20,
    super.key,
  });

  final Key buttonKey;
  final String tooltip;
  final IconData icon;
  final VoidCallback onPressed;
  final bool enabled;
  final double iconSize;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final iconColor = colorScheme.primary.withValues(alpha: enabled ? 1 : 0.35);

    return Tooltip(
      message: tooltip,
      child: IgnorePointer(
        ignoring: !enabled,
        child: Material(
          color: colorScheme.surface.withValues(alpha: 0.86),
          shape: const CircleBorder(),
          elevation: 1,
          child: InkWell(
            key: buttonKey,
            customBorder: const CircleBorder(),
            onTap: onPressed,
            child: SizedBox(
              width: 40,
              height: 40,
              child: Icon(icon, size: iconSize, color: iconColor),
            ),
          ),
        ),
      ),
    );
  }
}
