import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_load_result.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/markdown_utils.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_config.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_view.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_images_cubit.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_images_state.dart';

class RevelationMarkdownBody extends StatefulWidget {
  const RevelationMarkdownBody({
    required this.data,
    this.padding = EdgeInsets.zero,
    this.onTapLink,
    this.showImagePreloadProgress = false,
    this.markdownImageLoader,
    super.key,
  });

  final String data;
  final EdgeInsets padding;
  final MarkdownTapLinkCallback? onTapLink;
  final bool showImagePreloadProgress;
  final MarkdownImageLoader? markdownImageLoader;

  @override
  State<RevelationMarkdownBody> createState() => _RevelationMarkdownBodyState();
}

class _RevelationMarkdownBodyState extends State<RevelationMarkdownBody> {
  late RevelationMarkdownImagesCubit _imagesCubit;

  @override
  void initState() {
    super.initState();
    _imagesCubit = _createImagesCubit();
    unawaited(_imagesCubit.setMarkdown(widget.data));
  }

  @override
  void didUpdateWidget(covariant RevelationMarkdownBody oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.markdownImageLoader != widget.markdownImageLoader) {
      final previousCubit = _imagesCubit;
      _imagesCubit = _createImagesCubit();
      unawaited(previousCubit.close());
      unawaited(_imagesCubit.setMarkdown(widget.data));
      return;
    }
    if (oldWidget.data != widget.data) {
      unawaited(_imagesCubit.setMarkdown(widget.data));
    }
  }

  @override
  void dispose() {
    unawaited(_imagesCubit.close());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return BlocProvider<RevelationMarkdownImagesCubit>.value(
      value: _imagesCubit,
      child: BlocBuilder<RevelationMarkdownImagesCubit, RevelationMarkdownImagesState>(
        builder: (context, state) {
          final body = MarkdownBody(
            key: ValueKey(
              'revelation-markdown-${state.documentRevision}-${widget.data.hashCode}-${state.completedCount}-${state.failedCount}',
            ),
            data: widget.data,
            styleSheet: getMarkdownStyleSheet(theme, colorScheme),
            extensionSet: buildRevelationMarkdownExtensionSet(),
            builders: buildRevelationMarkdownBuilders(
              imageBuilder: (context, image) =>
                  _buildMarkdownImage(state, image),
            ),
            paddingBuilders: buildRevelationMarkdownPaddingBuilders(),
            onTapLink: widget.onTapLink,
          );

          final bodyWithPadding = Padding(padding: widget.padding, child: body);
          if (!widget.showImagePreloadProgress || !state.isPreloadActive) {
            return bodyWithPadding;
          }

          return Padding(
            padding: widget.padding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _MarkdownImagePreloadBanner(state: state),
                MarkdownBody(
                  key: ValueKey(
                    'revelation-markdown-content-${state.documentRevision}-${widget.data.hashCode}-${state.completedCount}-${state.failedCount}',
                  ),
                  data: widget.data,
                  styleSheet: getMarkdownStyleSheet(theme, colorScheme),
                  extensionSet: buildRevelationMarkdownExtensionSet(),
                  builders: buildRevelationMarkdownBuilders(
                    imageBuilder: (context, image) =>
                        _buildMarkdownImage(state, image),
                  ),
                  paddingBuilders: buildRevelationMarkdownPaddingBuilders(),
                  onTapLink: widget.onTapLink,
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildMarkdownImage(
    RevelationMarkdownImagesState state,
    RevelationMarkdownImageData image,
  ) {
    return RevelationMarkdownImageView(
      key: ValueKey(
        '${image.cacheKey}-${state.images[image.cacheKey]?.status.name ?? 'missing'}',
      ),
      image: image,
      imageState: state.images[image.cacheKey],
    );
  }

  MarkdownImageLoader _resolveMarkdownImageLoader() {
    if (GetIt.I.isRegistered<MarkdownImageLoader>()) {
      return GetIt.I<MarkdownImageLoader>();
    }
    return const _UnavailableMarkdownImageLoader();
  }

  RevelationMarkdownImagesCubit _createImagesCubit() {
    return RevelationMarkdownImagesCubit(
      imageLoader: widget.markdownImageLoader ?? _resolveMarkdownImageLoader(),
    );
  }
}

class _MarkdownImagePreloadBanner extends StatelessWidget {
  const _MarkdownImagePreloadBanner({required this.state});

  final RevelationMarkdownImagesState state;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final progress = state.preloadProgress ?? 0;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainer,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: colorScheme.outlineVariant),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                AppLocalizations.of(context)!.markdown_images_loading_progress(
                  state.completedCount,
                  state.totalCount,
                ),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),
              LinearProgressIndicator(value: progress),
            ],
          ),
        ),
      ),
    );
  }
}

class _UnavailableMarkdownImageLoader implements MarkdownImageLoader {
  const _UnavailableMarkdownImageLoader();

  @override
  Future<MarkdownImageLoadResult> loadImage(
    MarkdownImageRequest request,
  ) async {
    return const MarkdownImageLoadResult.failure();
  }
}
