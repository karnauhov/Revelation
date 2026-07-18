import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:revelation/features/strongs_dictionary/application/services/strong_usage_bible_reference_markdown_tokens.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strong_usage_bible_text_provider.dart';
import 'package:revelation/features/strongs_dictionary/application/services/strong_usage_reference_detail_registry.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

typedef StrongUsageBibleTextCopyHandler = Future<void> Function(String text);

final StrongUsageBibleTextProvider _defaultStrongUsageBibleTextProvider =
    DefaultStrongUsageBibleTextProvider();

Map<String, MarkdownElementBuilder> buildStrongUsageBibleReferenceBuilders({
  GreekStrongTapHandler? onGreekStrongTap,
  GreekStrongPickerTapHandler? onGreekStrongPickerTap,
  WordTapHandler? onWordTap,
  WordsTapHandler? onWordsTap,
  StrongUsageBibleTextProvider? bibleTextProvider,
  StrongUsageBibleTextCopyHandler? copyBibleText,
  bool popBeforeBibleNavigation = false,
}) {
  return <String, MarkdownElementBuilder>{
    'a': StrongUsageBibleReferenceElementBuilder(
      onGreekStrongTap: onGreekStrongTap,
      onGreekStrongPickerTap: onGreekStrongPickerTap,
      onWordTap: onWordTap,
      onWordsTap: onWordsTap,
      bibleTextProvider:
          bibleTextProvider ?? _defaultStrongUsageBibleTextProvider,
      copyBibleText:
          copyBibleText ??
          (String text) => Clipboard.setData(ClipboardData(text: text)),
      popBeforeBibleNavigation: popBeforeBibleNavigation,
    ),
  };
}

class StrongUsageBibleReferenceElementBuilder extends MarkdownElementBuilder {
  StrongUsageBibleReferenceElementBuilder({
    this.onGreekStrongTap,
    this.onGreekStrongPickerTap,
    this.onWordTap,
    this.onWordsTap,
    required this.bibleTextProvider,
    required this.copyBibleText,
    required this.popBeforeBibleNavigation,
  });

  final GreekStrongTapHandler? onGreekStrongTap;
  final GreekStrongPickerTapHandler? onGreekStrongPickerTap;
  final WordTapHandler? onWordTap;
  final WordsTapHandler? onWordsTap;
  final StrongUsageBibleTextProvider bibleTextProvider;
  final StrongUsageBibleTextCopyHandler copyBibleText;
  final bool popBeforeBibleNavigation;

  @override
  Widget? visitElementAfterWithContext(
    BuildContext context,
    md.Element element,
    TextStyle? preferredStyle,
    TextStyle? parentStyle,
  ) {
    final href = element.attributes['href'];
    final title = element.attributes['title'];
    final label = element.textContent.trim();
    if (href == null || href.trim().isEmpty || label.isEmpty) {
      return Text(label, style: preferredStyle);
    }

    final linkStyle = _linkStyle(context, preferredStyle, parentStyle);
    final moreReferenceId =
        strongUsageMoreReferenceIdFromTitle(title) ??
        strongUsageMoreReferenceIdFromHref(href);
    if (moreReferenceId != null) {
      return _StrongUsageMoreReferenceLink(
        label: label,
        detailId: moreReferenceId,
        style: linkStyle,
        onGreekStrongTap: onGreekStrongTap,
        onGreekStrongPickerTap: onGreekStrongPickerTap,
        onWordTap: onWordTap,
        onWordsTap: onWordsTap,
        bibleTextProvider: bibleTextProvider,
        copyBibleText: copyBibleText,
        popBeforeBibleNavigation: popBeforeBibleNavigation,
      );
    }

    final verseKey = strongUsageBibleReferenceVerseKeyFromTitle(title);
    if (verseKey == null || !href.toLowerCase().startsWith('bible:')) {
      return _MarkdownInlineLink(
        label: label,
        href: href,
        style: linkStyle,
        onGreekStrongTap: onGreekStrongTap,
        onGreekStrongPickerTap: onGreekStrongPickerTap,
        onWordTap: onWordTap,
        onWordsTap: onWordsTap,
      );
    }

    return _StrongUsageBibleReferenceLink(
      label: label,
      href: href,
      verseKey: verseKey,
      style: linkStyle,
      bibleTextProvider: bibleTextProvider,
      copyBibleText: copyBibleText,
      popBeforeBibleNavigation: popBeforeBibleNavigation,
    );
  }

  TextStyle _linkStyle(
    BuildContext context,
    TextStyle? preferredStyle,
    TextStyle? parentStyle,
  ) {
    final colorScheme = Theme.of(context).colorScheme;
    final baseStyle =
        preferredStyle ?? parentStyle ?? Theme.of(context).textTheme.bodyMedium;
    return (baseStyle ?? const TextStyle()).copyWith(
      color: colorScheme.primary,
      decoration: TextDecoration.underline,
      decorationColor: colorScheme.primary,
    );
  }
}

class _MarkdownInlineLink extends StatelessWidget {
  const _MarkdownInlineLink({
    required this.label,
    required this.href,
    required this.style,
    this.onGreekStrongTap,
    this.onGreekStrongPickerTap,
    this.onWordTap,
    this.onWordsTap,
  });

  final String label;
  final String href;
  final TextStyle style;
  final GreekStrongTapHandler? onGreekStrongTap;
  final GreekStrongPickerTapHandler? onGreekStrongPickerTap;
  final WordTapHandler? onWordTap;
  final WordsTapHandler? onWordsTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: () {
        unawaited(
          handleAppLink(
            context,
            href,
            onGreekStrongTap: onGreekStrongTap,
            onGreekStrongPickerTap: onGreekStrongPickerTap,
            onWordTap: onWordTap,
            onWordsTap: onWordsTap,
          ),
        );
      },
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        child: Text(label, style: style),
      ),
    );
  }
}

class _StrongUsageMoreReferenceLink extends StatelessWidget {
  const _StrongUsageMoreReferenceLink({
    required this.label,
    required this.detailId,
    required this.style,
    this.onGreekStrongTap,
    this.onGreekStrongPickerTap,
    this.onWordTap,
    this.onWordsTap,
    required this.bibleTextProvider,
    required this.copyBibleText,
    required this.popBeforeBibleNavigation,
  });

  final String label;
  final String detailId;
  final TextStyle style;
  final GreekStrongTapHandler? onGreekStrongTap;
  final GreekStrongPickerTapHandler? onGreekStrongPickerTap;
  final WordTapHandler? onWordTap;
  final WordsTapHandler? onWordsTap;
  final StrongUsageBibleTextProvider bibleTextProvider;
  final StrongUsageBibleTextCopyHandler copyBibleText;
  final bool popBeforeBibleNavigation;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: () => unawaited(_showDetailDialog(context)),
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        child: Text(label, style: style),
      ),
    );
  }

  Future<void> _showDetailDialog(BuildContext context) async {
    final detail = StrongUsageReferenceDetailRegistry.instance.find(detailId);
    if (detail == null) {
      return;
    }

    await showDialog<void>(
      context: context,
      routeSettings: const RouteSettings(
        name: 'strong_usage_reference_detail_dialog',
      ),
      builder: (dialogContext) {
        final theme = Theme.of(dialogContext);
        final colorScheme = theme.colorScheme;
        final localizations = AppLocalizations.of(dialogContext)!;
        final mediaSize = MediaQuery.sizeOf(dialogContext);
        final dialogWidth = (mediaSize.width - 40)
            .clamp(300.0, 720.0)
            .toDouble();
        final dialogHeight = (mediaSize.height - 120)
            .clamp(180.0, 520.0)
            .toDouble();
        final actionMarkdown = stripStrongUsageBibleReferenceTitles(
          detail.referencesMarkdown,
        );
        final documentTitle = '${detail.surface} (${detail.count})';

        return AlertDialog(
          insetPadding: const EdgeInsets.symmetric(
            horizontal: 20,
            vertical: 20,
          ),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          title: Text(
            '${detail.surface} (${detail.count})',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          content: SizedBox(
            width: dialogWidth,
            height: dialogHeight,
            child: DescriptionMarkdownView(
              data: detail.referencesMarkdown,
              exportPdfMarkdown: actionMarkdown,
              copyMarkdown: actionMarkdown,
              exportPdfDocumentTitle: documentTitle,
              padding: const EdgeInsets.all(4),
              elementBuilders: buildStrongUsageBibleReferenceBuilders(
                onGreekStrongTap: onGreekStrongTap,
                onGreekStrongPickerTap: onGreekStrongPickerTap,
                onWordTap: onWordTap,
                onWordsTap: onWordsTap,
                bibleTextProvider: bibleTextProvider,
                copyBibleText: copyBibleText,
                popBeforeBibleNavigation: popBeforeBibleNavigation,
              ),
              onGreekStrongTap: onGreekStrongTap,
              onGreekStrongPickerTap: onGreekStrongPickerTap,
              onWordTap: onWordTap,
              onWordsTap: onWordsTap,
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: Text(
                localizations.close,
                style: TextStyle(color: colorScheme.primary),
              ),
            ),
          ],
        );
      },
    );
  }
}

class _StrongUsageBibleReferenceLink extends StatefulWidget {
  const _StrongUsageBibleReferenceLink({
    required this.label,
    required this.href,
    required this.verseKey,
    required this.style,
    required this.bibleTextProvider,
    required this.copyBibleText,
    required this.popBeforeBibleNavigation,
  });

  final String label;
  final String href;
  final String verseKey;
  final TextStyle style;
  final StrongUsageBibleTextProvider bibleTextProvider;
  final StrongUsageBibleTextCopyHandler copyBibleText;
  final bool popBeforeBibleNavigation;

  @override
  State<_StrongUsageBibleReferenceLink> createState() =>
      _StrongUsageBibleReferenceLinkState();
}

class _StrongUsageBibleReferenceLinkState
    extends State<_StrongUsageBibleReferenceLink> {
  final GlobalKey<TooltipState> _tooltipKey = GlobalKey<TooltipState>();
  Future<String?>? _previewFuture;
  String? _previewText;
  String? _copyablePreviewText;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      key: _tooltipKey,
      message: _previewText ?? '',
      triggerMode: TooltipTriggerMode.manual,
      showDuration: const Duration(seconds: 12),
      waitDuration: const Duration(milliseconds: 300),
      preferBelow: false,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () {
          unawaited(
            handleAppLink(
              context,
              widget.href,
              popBeforeScreenPush: widget.popBeforeBibleNavigation,
            ),
          );
        },
        onLongPress: () {
          unawaited(_showPreview(copyText: true));
        },
        child: MouseRegion(
          cursor: SystemMouseCursors.click,
          child: Text(widget.label, style: widget.style),
        ),
      ),
    );
  }

  Future<void> _showPreview({required bool copyText}) async {
    await _loadPreviewText();
    if (!mounted) {
      return;
    }

    final copyablePreviewText = _copyablePreviewText;
    if (copyText &&
        copyablePreviewText != null &&
        copyablePreviewText.isNotEmpty) {
      try {
        await widget.copyBibleText(copyablePreviewText);
      } catch (_) {}
    }

    if (!mounted) {
      return;
    }
    _tooltipKey.currentState?.ensureTooltipVisible();
  }

  Future<String?> _loadPreviewText() {
    final existingFuture = _previewFuture;
    if (existingFuture != null) {
      return existingFuture;
    }

    final localizations = AppLocalizations.of(context)!;
    final future = widget.bibleTextProvider
        .loadVerseText(widget.verseKey)
        .then(
          (text) {
            final trimmedText = text?.trim();
            if (trimmedText == null || trimmedText.isEmpty) {
              _copyablePreviewText = null;
              return localizations.bible_reference_preview_unavailable;
            }
            _copyablePreviewText = trimmedText;
            return trimmedText;
          },
          onError: (_) {
            _copyablePreviewText = null;
            return localizations.bible_reference_preview_unavailable;
          },
        );
    _previewFuture = future;
    unawaited(
      future.then((text) {
        if (!mounted) {
          return;
        }
        setState(() {
          _previewText = text;
        });
      }),
    );
    setState(() {});
    return future;
  }
}
