import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_load_result.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_image_service.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_word_images_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_word_images_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_pdf_export.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';
import 'package:revelation/shared/utils/description_markdown_tokens.dart';

Future<void> showPrimarySourceWordsDialog(
  BuildContext context,
  List<PrimarySourceWordLinkTarget> targets, {
  PrimarySourceWordImagesCubit? cubit,
  WordTapHandler? onWordTap,
  DescriptionMarkdownExportPdfHandler? onExportPdfRequested,
}) {
  return showDialog<void>(
    context: context,
    routeSettings: const RouteSettings(name: 'primary_source_words_dialog'),
    builder: (_) => PrimarySourceWordsDialog(
      targets: targets,
      cubit: cubit,
      linkContext: context,
      onWordTap: onWordTap,
      onExportPdfRequested: onExportPdfRequested,
    ),
  );
}

class PrimarySourceWordsDialog extends StatelessWidget {
  const PrimarySourceWordsDialog({
    required this.targets,
    this.cubit,
    this.linkContext,
    this.onWordTap,
    this.onExportPdfRequested,
    super.key,
  });

  final List<PrimarySourceWordLinkTarget> targets;
  final PrimarySourceWordImagesCubit? cubit;
  final BuildContext? linkContext;
  final WordTapHandler? onWordTap;
  final DescriptionMarkdownExportPdfHandler? onExportPdfRequested;

  @override
  Widget build(BuildContext context) {
    final targetLinkContext = linkContext ?? context;
    final providedCubit = cubit;
    if (providedCubit != null) {
      return BlocProvider<PrimarySourceWordImagesCubit>.value(
        value: providedCubit,
        child: _PrimarySourceWordsDialogContent(
          targets: targets,
          linkContext: targetLinkContext,
          onWordTap: onWordTap,
          onExportPdfRequested: onExportPdfRequested,
        ),
      );
    }

    return BlocProvider<PrimarySourceWordImagesCubit>(
      create: (_) => PrimarySourceWordImagesCubit(
        targets: targets,
        isWeb: isWeb(),
        isMobileWeb: isWeb() && isMobileBrowser(),
        localizations: AppLocalizations.of(context)!,
      ),
      child: _PrimarySourceWordsDialogContent(
        targets: targets,
        linkContext: targetLinkContext,
        onWordTap: onWordTap,
        onExportPdfRequested: onExportPdfRequested,
      ),
    );
  }
}

class _PrimarySourceWordsDialogContent extends StatelessWidget {
  const _PrimarySourceWordsDialogContent({
    required this.targets,
    required this.linkContext,
    this.onWordTap,
    this.onExportPdfRequested,
  });

  final List<PrimarySourceWordLinkTarget> targets;
  final BuildContext linkContext;
  final WordTapHandler? onWordTap;
  final DescriptionMarkdownExportPdfHandler? onExportPdfRequested;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final mediaSize = MediaQuery.sizeOf(context);

    final dialogWidth = (mediaSize.width - 20).clamp(320.0, 820.0).toDouble();
    final dialogHeight = (mediaSize.height - 36).clamp(240.0, 620.0).toDouble();

    return AlertDialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
      backgroundColor: colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: colorScheme.primary),
        borderRadius: BorderRadius.circular(8),
      ),
      titlePadding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      contentPadding: const EdgeInsets.fromLTRB(10, 0, 10, 0),
      actionsPadding: const EdgeInsets.fromLTRB(8, 0, 8, 6),
      title:
          BlocBuilder<
            PrimarySourceWordImagesCubit,
            PrimarySourceWordImagesState
          >(
            builder: (context, state) {
              final title = _resolveTitle(state);
              final canExport =
                  !state.isLoading && _hasExportableContent(state);
              if (title.isEmpty && !canExport) {
                return const SizedBox.shrink();
              }
              return SizedBox(
                width: dialogWidth,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    if (title.isNotEmpty)
                      Center(
                        child: Padding(
                          padding: EdgeInsets.symmetric(
                            horizontal: canExport ? 48 : 0,
                          ),
                          child: Text(
                            title,
                            textAlign: TextAlign.center,
                            maxLines: 3,
                            overflow: TextOverflow.ellipsis,
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.normal,
                            ),
                          ),
                        ),
                      ),
                    if (canExport)
                      Align(
                        alignment: Alignment.centerRight,
                        child: DescriptionMarkdownToolbarButton(
                          buttonKey: const Key(
                            'description_markdown_export_pdf_button',
                          ),
                          tooltip: l10n.export_pdf_content,
                          icon: Icons.file_download_outlined,
                          onPressed: () =>
                              unawaited(_handleExportPdf(context, state)),
                        ),
                      ),
                  ],
                ),
              );
            },
          ),
      content: SizedBox(
        width: dialogWidth,
        height: dialogHeight,
        child:
            BlocBuilder<
              PrimarySourceWordImagesCubit,
              PrimarySourceWordImagesState
            >(
              builder: (context, state) {
                if (state.isLoading) {
                  return Center(
                    child: CircularProgressIndicator(
                      color: colorScheme.primary,
                    ),
                  );
                }
                if (state.items.isEmpty &&
                    (state.sharedWordDetailsMarkdown == null ||
                        state.sharedWordDetailsMarkdown!.trim().isEmpty)) {
                  return const SizedBox.shrink();
                }
                return _PrimarySourceWordsList(
                  items: state.items,
                  sharedWordDetailsMarkdown: state.sharedWordDetailsMarkdown,
                  linkContext: linkContext,
                  onWordTap: onWordTap,
                );
              },
            ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.close),
        ),
      ],
    );
  }

  String _resolveTitle(PrimarySourceWordImagesState state) {
    final seen = <String>{};
    final words = <String>[];
    for (final item in state.items) {
      final word = _normalizeTitleWord(item.displayWordText);
      if (word != null && word.isNotEmpty && seen.add(word)) {
        words.add(word);
      }
    }
    return words.join(', ');
  }

  String? _normalizeTitleWord(String? value) {
    final word = value?.replaceAll('~', '').replaceAll('\u200E', '').trim();
    if (word == null || word.isEmpty) {
      return null;
    }
    return word;
  }

  Future<void> _handleExportPdf(
    BuildContext context,
    PrimarySourceWordImagesState state,
  ) async {
    try {
      final l10n = AppLocalizations.of(context)!;
      final exportData = _buildExportData(l10n, state);
      final exportPdfHandler =
          onExportPdfRequested ??
          ({required String markdown, required String documentTitle}) =>
              exportRevelationMarkdownPdf(
                markdown: markdown,
                documentTitle: documentTitle,
                appName: l10n.app_name,
                markdownImageLoader: exportData.markdownImageLoader,
                strings: RevelationMarkdownPdfStrings.fromLocalizations(l10n),
              );

      final location = await exportPdfHandler(
        markdown: stripDescriptionMarkdownPresentationMarkers(
          exportData.markdown,
        ),
        documentTitle: exportData.documentTitle,
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
          'Failed to export PrimarySourceWordsDialog PDF',
        );
      } catch (_) {}

      if (!context.mounted) {
        return;
      }

      final messenger = ScaffoldMessenger.maybeOf(context);
      messenger?.showSnackBar(
        SnackBar(
          content: Text(
            AppLocalizations.of(context)!.markdown_pdf_export_failed,
          ),
        ),
      );
    }
  }

  _PrimarySourceWordsExportData _buildExportData(
    AppLocalizations l10n,
    PrimarySourceWordImagesState state,
  ) {
    final imageBytesByUri = <String, Uint8List>{};
    final lines = <String>[];
    final title = _resolveTitle(state);
    if (title.isNotEmpty) {
      lines.add('# ${_escapeMarkdownText(title)}');
    }

    for (var i = 0; i < state.items.length; i++) {
      final item = state.items[i];
      lines.add(
        '**${_escapeMarkdownText(_stripMarkupTags(item.sourceTitle, item.target.sourceId))}**',
      );
      final imageBytes = item.imageBytes;
      if (imageBytes != null && imageBytes.isNotEmpty) {
        final imageUri = _exportImageUri(i);
        imageBytesByUri[imageUri] = imageBytes;
        lines.add(
          '{{image}}\n'
          'src: $imageUri\n'
          'alt: ${_markdownImageAlt(item)}\n'
          '{{/image}}',
        );
      } else {
        lines.add(
          _escapeMarkdownText(_unavailableText(l10n, item.unavailableReason)),
        );
      }
    }

    final sharedDetailsMarkdown = state.sharedWordDetailsMarkdown?.trim();
    if (sharedDetailsMarkdown != null && sharedDetailsMarkdown.isNotEmpty) {
      lines.add('---');
      lines.add(sharedDetailsMarkdown);
    }

    final markdown = lines.join('\n\n').trim();
    return _PrimarySourceWordsExportData(
      markdown: markdown.isEmpty ? '-' : markdown,
      documentTitle: _exportDocumentTitle(targets),
      markdownImageLoader: _PrimarySourceWordsExportImageLoader(
        imageBytesByUri,
      ),
    );
  }

  String _exportDocumentTitle(List<PrimarySourceWordLinkTarget> targets) {
    final payload = targets.map((target) => target.fallbackLabel).join(';');
    final sanitized = payload
        .replaceAll(';', '_')
        .replaceAll(RegExp(r'[\\/:*?"<>|\x00-\x1F]'), '.')
        .trim();
    return sanitized.isEmpty ? 'words' : sanitized;
  }

  String _exportImageUri(int index) {
    return Uri.https(
      'revelation.local',
      '/primary-source-words/$index.png',
    ).toString();
  }

  String _markdownImageAlt(PrimarySourceWordImageResult item) {
    return item.target.sourceId
        .replaceAll('[', r'\[')
        .replaceAll(']', r'\]')
        .replaceAll('\r', ' ')
        .replaceAll('\n', ' ')
        .trim();
  }
}

class _PrimarySourceWordsList extends StatelessWidget {
  const _PrimarySourceWordsList({
    required this.items,
    this.sharedWordDetailsMarkdown,
    required this.linkContext,
    this.onWordTap,
  });

  final List<PrimarySourceWordImageResult> items;
  final String? sharedWordDetailsMarkdown;
  final BuildContext linkContext;
  final WordTapHandler? onWordTap;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final hasClickableImages = _hasClickableImages(items);
    final hasSharedWordDetails =
        sharedWordDetailsMarkdown != null &&
        sharedWordDetailsMarkdown!.trim().isNotEmpty;
    final totalItemCount =
        items.length +
        (hasClickableImages ? 1 : 0) +
        (hasSharedWordDetails ? 1 : 0);

    return ListView.separated(
      padding: const EdgeInsets.symmetric(horizontal: 2),
      itemCount: totalItemCount,
      separatorBuilder: (_, _) =>
          Divider(height: 5, thickness: 1, color: colorScheme.outlineVariant),
      itemBuilder: (context, index) {
        if (index < items.length) {
          return _PrimarySourceWordSection(
            item: items[index],
            linkContext: linkContext,
            onWordTap: onWordTap,
          );
        }
        if (hasClickableImages && index == items.length) {
          return const _PrimarySourceWordsImageHint();
        }
        if (hasSharedWordDetails) {
          return _SharedWordDetailsSection(
            markdown: sharedWordDetailsMarkdown!,
          );
        }
        return const SizedBox.shrink();
      },
    );
  }
}

class _PrimarySourceWordSection extends StatelessWidget {
  const _PrimarySourceWordSection({
    required this.item,
    required this.linkContext,
    this.onWordTap,
  });

  final PrimarySourceWordImageResult item;
  final BuildContext linkContext;
  final WordTapHandler? onWordTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final sourceIdStyle = theme.textTheme.labelLarge?.copyWith(
      fontWeight: FontWeight.w700,
      color: theme.colorScheme.onSurfaceVariant,
    );

    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        SizedBox(
          width: 24,
          child: Center(
            child: Tooltip(
              message: _stripMarkupTags(item.sourceTitle, item.target.sourceId),
              triggerMode: TooltipTriggerMode.tap,
              child: RotatedBox(
                quarterTurns: 3,
                child: Text(
                  item.target.sourceId,
                  maxLines: 1,
                  overflow: TextOverflow.visible,
                  style: sourceIdStyle,
                ),
              ),
            ),
          ),
        ),
        const SizedBox(width: 4),
        Expanded(
          child: _PrimarySourceWordPreview(
            item: item,
            linkContext: linkContext,
            onWordTap: onWordTap,
          ),
        ),
      ],
    );
  }
}

class _PrimarySourceWordPreview extends StatelessWidget {
  const _PrimarySourceWordPreview({
    required this.item,
    required this.linkContext,
    this.onWordTap,
  });

  final PrimarySourceWordImageResult item;
  final BuildContext linkContext;
  final WordTapHandler? onWordTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final imageBytes = item.imageBytes;

    if (imageBytes != null && imageBytes.isNotEmpty) {
      final image = Image.memory(
        imageBytes,
        fit: BoxFit.contain,
        gaplessPlayback: true,
        filterQuality: FilterQuality.high,
      );
      final wordLink = item.target.wordLink;
      if (wordLink == null) {
        return Align(alignment: Alignment.centerLeft, child: image);
      }

      return Align(
        alignment: Alignment.centerLeft,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            key: ValueKey(
              'primary-source-word-image-${item.target.fallbackLabel}',
            ),
            borderRadius: BorderRadius.circular(4),
            onTap: () {
              unawaited(_openWord(context, wordLink));
            },
            child: image,
          ),
        ),
      );
    }

    return Align(
      alignment: Alignment.centerLeft,
      child: Text(
        _unavailableText(l10n, item.unavailableReason),
        textAlign: TextAlign.start,
        style: theme.textTheme.bodyMedium?.copyWith(
          color: colorScheme.onSurfaceVariant,
        ),
      ),
    );
  }

  Future<void> _openWord(BuildContext context, String wordLink) async {
    final navigator = Navigator.of(context);
    if (navigator.canPop()) {
      navigator.pop();
    }
    await Future<void>.delayed(Duration.zero);
    if (!linkContext.mounted) {
      return;
    }
    await handleAppLink(linkContext, wordLink, onWordTap: onWordTap);
  }
}

class _PrimarySourceWordsImageHint extends StatelessWidget {
  const _PrimarySourceWordsImageHint();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
      child: Text(
        AppLocalizations.of(context)!.primary_source_words_image_hint,
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onSurfaceVariant,
        ),
      ),
    );
  }
}

class _SharedWordDetailsSection extends StatelessWidget {
  const _SharedWordDetailsSection({required this.markdown});

  final String markdown;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 2),
      child: DescriptionMarkdownView(
        data: markdown,
        scrollable: false,
        padding: const EdgeInsets.fromLTRB(0, 0, 0, 0),
        showExportPdfButton: false,
      ),
    );
  }
}

class _PrimarySourceWordsExportData {
  const _PrimarySourceWordsExportData({
    required this.markdown,
    required this.documentTitle,
    required this.markdownImageLoader,
  });

  final String markdown;
  final String documentTitle;
  final MarkdownImageLoader markdownImageLoader;
}

class _PrimarySourceWordsExportImageLoader implements MarkdownImageLoader {
  const _PrimarySourceWordsExportImageLoader(this._imageBytesByUri);

  final Map<String, Uint8List> _imageBytesByUri;

  @override
  Future<MarkdownImageLoadResult> loadImage(
    MarkdownImageRequest request,
  ) async {
    final uri = request.networkUri?.toString();
    final bytes = uri == null ? null : _imageBytesByUri[uri];
    if (bytes == null || bytes.isEmpty) {
      return const MarkdownImageLoadResult.failure();
    }
    return MarkdownImageLoadResult.success(bytes: bytes, mimeType: 'image/png');
  }
}

bool _hasClickableImages(List<PrimarySourceWordImageResult> items) {
  return items.any((item) => item.hasImage && item.target.wordLink != null);
}

bool _hasExportableContent(PrimarySourceWordImagesState state) {
  return state.items.isNotEmpty ||
      (state.sharedWordDetailsMarkdown != null &&
          state.sharedWordDetailsMarkdown!.trim().isNotEmpty);
}

String _stripMarkupTags(String value, String fallback) {
  final normalized = value
      .replaceAll(RegExp(r'<[^>]*>'), '')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
  return normalized.isEmpty ? fallback : normalized;
}

String _escapeMarkdownText(String value) {
  return value
      .replaceAll(r'\', r'\\')
      .replaceAll('*', r'\*')
      .replaceAll('_', r'\_')
      .replaceAll('[', r'\[')
      .replaceAll(']', r'\]')
      .replaceAll('(', r'\(')
      .replaceAll(')', r'\)')
      .replaceAll('#', r'\#')
      .replaceAll('+', r'\+')
      .replaceAll('-', r'\-')
      .replaceAll('!', r'\!')
      .replaceAll('`', r'\`')
      .replaceAll('>', r'\>');
}

String _unavailableText(
  AppLocalizations l10n,
  PrimarySourceWordImageUnavailableReason reason,
) {
  return switch (reason) {
    PrimarySourceWordImageUnavailableReason.sourceUnavailable =>
      l10n.primary_source_word_source_unavailable,
    PrimarySourceWordImageUnavailableReason.pageUnavailable =>
      l10n.primary_source_word_page_unavailable,
    PrimarySourceWordImageUnavailableReason.wordUnavailable =>
      l10n.primary_source_word_word_unavailable,
    PrimarySourceWordImageUnavailableReason.none ||
    PrimarySourceWordImageUnavailableReason.imageUnavailable =>
      l10n.primary_source_word_image_unavailable,
  };
}
