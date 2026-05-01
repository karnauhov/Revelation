import 'dart:async';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter/services.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/core/platform/file_downloader.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_cubit.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/dialogs/dialogs_utils.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_pdf_export.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_body.dart';
import 'package:revelation/shared/ui/widgets/error_message.dart';

typedef TopicContentCubitBuilder =
    TopicContentCubit Function({
      required SettingsCubit settingsCubit,
      required String route,
      String? name,
      String? description,
    });

typedef DownloadableFileSaver =
    Future<String?> Function({
      required Uint8List bytes,
      required String fileName,
      required String mimeType,
    });

typedef TopicScreenExportPdfHandler =
    Future<String?> Function({
      required String markdown,
      required String documentTitle,
    });
typedef TopicScreenCopyHandler = Future<void> Function(String markdown);

class TopicScreen extends StatefulWidget {
  final String? name;
  final String? description;
  final String? file;
  final TopicContentCubitBuilder? topicContentCubitBuilder;
  final TopicScreenExportPdfHandler? onExportPdfRequested;
  final TopicScreenCopyHandler? onCopyRequested;

  const TopicScreen({
    super.key,
    this.name,
    this.description,
    this.file,
    this.topicContentCubitBuilder,
    this.onExportPdfRequested,
    this.onCopyRequested,
  });

  @visibleForTesting
  static DownloadableFileSaver saveDownloadableFileForTest =
      saveDownloadableFile;

  @visibleForTesting
  static void resetTestOverrides() {
    saveDownloadableFileForTest = saveDownloadableFile;
  }

  @override
  State<TopicScreen> createState() => _TopicScreenState();
}

class _TopicScreenState extends State<TopicScreen> {
  static const String _dbFileScheme = 'dbfile:';
  static const String _assetResourceScheme = 'resource:';

  final ScrollController _scrollController = ScrollController();
  late final TopicContentCubit _topicContentCubit;

  bool _isDragging = false;
  Offset _lastOffset = Offset.zero;

  @override
  void initState() {
    super.initState();
    final cubitBuilder =
        widget.topicContentCubitBuilder ?? AppDi.createTopicContentCubit;
    _topicContentCubit = cubitBuilder(
      settingsCubit: context.read<SettingsCubit>(),
      route: widget.file ?? '',
      name: widget.name,
      description: widget.description,
    );
  }

  @override
  void dispose() {
    _topicContentCubit.close();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return BlocProvider.value(
      value: _topicContentCubit,
      child: BlocBuilder<TopicContentCubit, TopicContentState>(
        builder: (context, state) {
          Widget content;
          if (state.isLoading) {
            content = const Center(child: CircularProgressIndicator());
          } else if (state.failure != null) {
            content = ErrorMessage(errorMessage: l10n.error_loading_topics);
          } else {
            content = SizedBox.expand(
              child: SingleChildScrollView(
                controller: _scrollController,
                child: RevelationMarkdownBody(
                  key: ValueKey(
                    'topic-markdown-${state.route}-${state.language}-${state.markdown.hashCode}',
                  ),
                  data: state.markdown,
                  padding: const EdgeInsets.all(8.0),
                  showImagePreloadProgress: true,
                  onTapLink: (text, href, title) async {
                    await _handleTopicLink(context, href);
                  },
                ),
              ),
            );
          }

          if (isDesktop() || isWeb()) {
            content = Listener(
              onPointerDown: (event) {
                if (event.buttons == kPrimaryMouseButton) {
                  setState(() {
                    _isDragging = true;
                    _lastOffset = event.position;
                  });
                }
              },
              onPointerMove: (event) {
                if (_isDragging) {
                  final dy = event.position.dy - _lastOffset.dy;
                  _scrollController.jumpTo(_scrollController.offset - dy);
                  setState(() {
                    _lastOffset = event.position;
                  });
                }
              },
              onPointerUp: (event) {
                if (event.buttons == 0) {
                  setState(() {
                    _isDragging = false;
                  });
                }
              },
              child: content,
            );
          }

          final title = _firstNonEmpty(widget.name, state.name, l10n.topic);
          final subtitle = _firstNonEmpty(
            widget.description,
            state.description,
            '',
          );
          final canExportPdf = !state.isLoading && state.failure == null;

          return Scaffold(
            appBar: AppBar(
              title: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      height: 0.9,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.normal,
                    ),
                  ),
                ],
              ),
              foregroundColor: colorScheme.primary,
              actions: [
                if (canExportPdf)
                  IconButton(
                    key: const Key('topic_screen_export_pdf_button'),
                    tooltip: l10n.export_pdf_content,
                    onPressed: () =>
                        unawaited(_handleExportPdf(title, state.markdown)),
                    icon: const Icon(Icons.file_download_outlined),
                  ),
                if (canExportPdf)
                  IconButton(
                    key: const Key('topic_screen_copy_button'),
                    tooltip: l10n.copy_content,
                    onPressed: () => unawaited(_handleCopy(state.markdown)),
                    icon: const Icon(Icons.content_copy_outlined),
                  ),
              ],
            ),
            body: content,
          );
        },
      ),
    );
  }

  String _firstNonEmpty(String? first, String? second, [String fallback = '']) {
    if (first != null && first.trim().isNotEmpty) {
      return first;
    }
    if (second != null && second.trim().isNotEmpty) {
      return second;
    }
    return fallback;
  }

  Future<void> _handleExportPdf(String documentTitle, String markdown) async {
    try {
      final appName = AppLocalizations.of(context)!.app_name;
      final exportPdfHandler =
          widget.onExportPdfRequested ??
          ({required String markdown, required String documentTitle}) =>
              exportRevelationMarkdownPdf(
                markdown: markdown,
                documentTitle: documentTitle,
                appName: appName,
                saveFile: TopicScreen.saveDownloadableFileForTest,
              );

      final location = await exportPdfHandler(
        markdown: markdown,
        documentTitle: documentTitle,
      );

      if (!mounted) {
        return;
      }

      if (location != null && location.isNotEmpty) {
        final messenger = ScaffoldMessenger.maybeOf(context);
        messenger?.showSnackBar(
          SnackBar(
            content: Text(
              AppLocalizations.of(context)!.file_saved_at(location),
            ),
          ),
        );
      }
    } catch (error, stackTrace) {
      try {
        log.handle(error, stackTrace, 'Failed to export TopicScreen PDF');
      } catch (_) {}

      if (!mounted) {
        return;
      }

      final messenger = ScaffoldMessenger.maybeOf(context);
      if (messenger == null) {
        return;
      }

      messenger.showSnackBar(
        SnackBar(
          content: Text(
            AppLocalizations.of(context)!.markdown_pdf_export_failed,
          ),
        ),
      );
    }
  }

  Future<void> _handleCopy(String markdown) async {
    try {
      final copyHandler =
          widget.onCopyRequested ??
          (String markdown) => Clipboard.setData(ClipboardData(text: markdown));

      await copyHandler(markdown);
    } catch (error, stackTrace) {
      try {
        log.handle(error, stackTrace, 'Failed to copy TopicScreen article');
      } catch (_) {}

      if (!mounted) {
        return;
      }

      final messenger = ScaffoldMessenger.maybeOf(context);
      if (messenger == null) {
        return;
      }

      messenger.showSnackBar(
        SnackBar(
          content: Text(AppLocalizations.of(context)!.markdown_copy_failed),
        ),
      );
      return;
    }

    if (!mounted) {
      return;
    }

    final messenger = ScaffoldMessenger.maybeOf(context);
    if (messenger == null) {
      return;
    }

    messenger.showSnackBar(
      SnackBar(content: Text(AppLocalizations.of(context)!.markdown_copied)),
    );
  }

  Future<bool> _handleTopicLink(BuildContext context, String? href) async {
    final link = href?.trim();
    if (link == null || link.isEmpty) {
      return false;
    }

    if (link.toLowerCase().startsWith(_dbFileScheme)) {
      final key = link.substring(_dbFileScheme.length).trim();
      return _downloadDbFile(context, key);
    }

    if (link.toLowerCase().startsWith(_assetResourceScheme)) {
      final assetPath = link.substring(_assetResourceScheme.length).trim();
      return _downloadAssetFile(context, assetPath);
    }

    return handleAppLink(context, link, popBeforeScreenPush: true);
  }

  Future<bool> _downloadDbFile(BuildContext context, String key) async {
    final l10n = AppLocalizations.of(context)!;
    if (key.isEmpty) {
      showCustomDialog(MessageType.errorCommon, param: 'DB file key is empty');
      return false;
    }

    final resourceResult = await _topicContentCubit.loadCommonResource(key);
    if (resourceResult is! AppSuccess<TopicResource?>) {
      showCustomDialog(
        MessageType.errorCommon,
        param: 'Resource not found in DB: $key',
      );
      return false;
    }

    final resource = resourceResult.data;
    if (resource == null) {
      showCustomDialog(
        MessageType.errorCommon,
        param: 'Resource not found in DB: $key',
      );
      return false;
    }

    return _saveBytesAsDownload(
      bytes: resource.data,
      fileName: resource.fileName,
      mimeType: resource.mimeType,
      savedMessageBuilder: l10n.file_saved_at,
    );
  }

  Future<bool> _downloadAssetFile(
    BuildContext context,
    String assetPath,
  ) async {
    final l10n = AppLocalizations.of(context)!;
    if (assetPath.isEmpty) {
      showCustomDialog(MessageType.errorCommon, param: 'Asset path is empty');
      return false;
    }

    try {
      final bytes = (await rootBundle.load(assetPath)).buffer.asUint8List();
      final fileName = p.basename(assetPath);
      final mimeType = _guessMimeType(fileName);
      return _saveBytesAsDownload(
        bytes: bytes,
        fileName: fileName,
        mimeType: mimeType,
        savedMessageBuilder: l10n.file_saved_at,
      );
    } catch (e) {
      showCustomDialog(
        MessageType.errorCommon,
        param: 'Asset not found: $assetPath',
        markdownExtension: e.toString(),
      );
      return false;
    }
  }

  Future<bool> _saveBytesAsDownload({
    required Uint8List bytes,
    required String fileName,
    required String mimeType,
    required String Function(String location) savedMessageBuilder,
  }) async {
    try {
      final location = await TopicScreen.saveDownloadableFileForTest(
        bytes: bytes,
        fileName: fileName,
        mimeType: mimeType,
      );
      if (location == null || location.isEmpty) {
        showCustomDialog(
          MessageType.infoCommon,
          param: 'Download started: $fileName',
        );
      } else {
        final savedMessage = savedMessageBuilder(location);
        showCustomDialog(MessageType.infoCommon, param: savedMessage);
      }
      return true;
    } catch (e) {
      showCustomDialog(
        MessageType.errorCommon,
        param: 'Unable to download file: $fileName',
        markdownExtension: e.toString(),
      );
      return false;
    }
  }

  String _guessMimeType(String fileName) {
    final ext = p.extension(fileName).toLowerCase();
    switch (ext) {
      case '.png':
        return 'image/png';
      case '.jpg':
      case '.jpeg':
        return 'image/jpeg';
      case '.gif':
        return 'image/gif';
      case '.svg':
        return 'image/svg+xml';
      case '.pdf':
        return 'application/pdf';
      case '.zip':
        return 'application/zip';
      case '.txt':
        return 'text/plain';
      case '.md':
        return 'text/markdown';
      default:
        return 'application/octet-stream';
    }
  }
}
