import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/shared/ui/widgets/error_message.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_cubit.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_content_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:revelation/shared/ui/dialogs/dialogs_utils.dart';
import 'package:revelation/shared/ui/markdown/markdown_utils.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/core/platform/file_downloader.dart';

class TopicScreen extends StatefulWidget {
  final String? name;
  final String? description;
  final String? file;

  const TopicScreen({super.key, this.name, this.description, this.file});

  @override
  State<TopicScreen> createState() => _TopicScreenState();
}

class _TopicScreenState extends State<TopicScreen> {
  static const String _dbResourceScheme = 'dbres:';
  static const String _dbFileScheme = 'dbfile:';
  static const String _assetResourceScheme = 'resource:';

  final ScrollController _scrollController = ScrollController();
  final TopicsRepository _topicsRepository = TopicsRepository();
  late final TopicContentCubit _topicContentCubit;

  bool _isDragging = false;
  Offset _lastOffset = Offset.zero;

  @override
  void initState() {
    super.initState();
    _topicContentCubit = TopicContentCubit(
      topicsRepository: _topicsRepository,
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
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
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
                padding: const EdgeInsets.all(8.0),
                child: MarkdownBody(
                  data: state.markdown,
                  styleSheet: getMarkdownStyleSheet(theme, colorScheme),
                  imageBuilder: (uri, title, alt) =>
                      _buildMarkdownImage(context, uri, alt),
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

  Widget _buildMarkdownImage(BuildContext context, Uri uri, String? alt) {
    final link = uri.toString().trim();
    if (link.toLowerCase().startsWith(_dbResourceScheme)) {
      final key = link.substring(_dbResourceScheme.length).trim();
      return _buildDbResourceImage(context, key, alt);
    }

    if (link.toLowerCase().startsWith(_assetResourceScheme)) {
      final assetPath = link.substring(_assetResourceScheme.length).trim();
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Image.asset(
          assetPath,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) =>
              _buildImageErrorWidget(context, assetPath, alt),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Image.network(
        link,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) =>
            _buildImageErrorWidget(context, link, alt),
      ),
    );
  }

  Widget _buildDbResourceImage(BuildContext context, String key, String? alt) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: FutureBuilder<AppResult<TopicResource?>>(
        future: _topicsRepository.getCommonResource(key),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          final result = snapshot.data;
          if (snapshot.hasError || result is! AppSuccess<TopicResource?>) {
            return _buildImageErrorWidget(context, key, alt);
          }
          final resource = result.data;
          if (resource == null) {
            return _buildImageErrorWidget(context, key, alt);
          }
          return Image.memory(resource.data, fit: BoxFit.contain);
        },
      ),
    );
  }

  Widget _buildImageErrorWidget(
    BuildContext context,
    String source,
    String? alt,
  ) {
    final message = (alt != null && alt.isNotEmpty)
        ? alt
        : 'Image not found: $source';
    return Text(
      message,
      style: Theme.of(context).textTheme.bodySmall?.copyWith(
        color: Theme.of(context).colorScheme.error,
      ),
    );
  }

  Future<bool> _downloadDbFile(BuildContext context, String key) async {
    final l10n = AppLocalizations.of(context)!;
    if (key.isEmpty) {
      showCustomDialog(MessageType.errorCommon, param: 'DB file key is empty');
      return false;
    }

    final resourceResult = await _topicsRepository.getCommonResource(key);
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
      final location = await saveDownloadableFile(
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
