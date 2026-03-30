import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_load_result.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_extractor.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_state.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_images_state.dart';

class RevelationMarkdownImagesCubit
    extends Cubit<RevelationMarkdownImagesState> {
  RevelationMarkdownImagesCubit({required MarkdownImageLoader imageLoader})
    : _imageLoader = imageLoader,
      super(RevelationMarkdownImagesState.initial());

  final MarkdownImageLoader _imageLoader;
  int _activeRequestToken = 0;

  Future<void> setMarkdown(String markdown) async {
    final requestToken = ++_activeRequestToken;
    final asyncImages = _collectAsyncImages(markdown);

    emit(
      RevelationMarkdownImagesState(
        documentRevision: state.documentRevision + 1,
        images: _buildInitialImages(asyncImages),
        totalCount: asyncImages.length,
        completedCount: 0,
        failedCount: 0,
      ),
    );

    if (asyncImages.isEmpty) {
      return;
    }

    await Future.wait(
      asyncImages.map((image) => _preloadImage(image, requestToken)),
    );
  }

  List<RevelationMarkdownImageData> _collectAsyncImages(String markdown) {
    final seenCacheKeys = <String>{};
    final images = <RevelationMarkdownImageData>[];

    for (final image in extractRevelationMarkdownImages(markdown)) {
      final request = image.toLoadRequest();
      if (request == null || !seenCacheKeys.add(request.cacheKey)) {
        continue;
      }
      images.add(image);
    }

    return images;
  }

  Map<String, RevelationMarkdownImageState> _buildInitialImages(
    List<RevelationMarkdownImageData> images,
  ) {
    final initialImages = <String, RevelationMarkdownImageState>{};
    for (final image in images) {
      initialImages[image.cacheKey] =
          const RevelationMarkdownImageState.loading();
    }
    return initialImages;
  }

  Future<void> _preloadImage(
    RevelationMarkdownImageData image,
    int requestToken,
  ) async {
    final request = image.toLoadRequest();
    if (request == null) {
      return;
    }

    final result = await _imageLoader.loadImage(request);
    if (_isStale(requestToken)) {
      return;
    }

    final nextState = _toImageState(result);
    final updatedImages = Map<String, RevelationMarkdownImageState>.from(
      state.images,
    );
    final previousState = updatedImages[request.cacheKey];
    final wasCompleted =
        previousState != null &&
        previousState.status != RevelationMarkdownImageStatus.loading;
    final wasFailure =
        previousState?.status == RevelationMarkdownImageStatus.failure;

    updatedImages[request.cacheKey] = nextState;

    emit(
      state.copyWith(
        images: updatedImages,
        completedCount: wasCompleted
            ? state.completedCount
            : state.completedCount + 1,
        failedCount: _nextFailedCount(
          currentFailedCount: state.failedCount,
          wasFailure: wasFailure,
          isFailure: nextState.status == RevelationMarkdownImageStatus.failure,
        ),
      ),
    );
  }

  RevelationMarkdownImageState _toImageState(MarkdownImageLoadResult result) {
    if (!result.isSuccess || result.bytes == null) {
      return const RevelationMarkdownImageState.failure();
    }
    return RevelationMarkdownImageState.ready(
      bytes: result.bytes!,
      mimeType: result.mimeType,
    );
  }

  int _nextFailedCount({
    required int currentFailedCount,
    required bool wasFailure,
    required bool isFailure,
  }) {
    if (wasFailure == isFailure) {
      return currentFailedCount;
    }
    if (isFailure) {
      return currentFailedCount + 1;
    }
    return currentFailedCount > 0 ? currentFailedCount - 1 : 0;
  }

  bool _isStale(int requestToken) =>
      isClosed || requestToken != _activeRequestToken;
}
