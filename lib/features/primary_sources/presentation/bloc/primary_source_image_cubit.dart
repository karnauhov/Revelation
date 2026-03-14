import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_state.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/core/platform/platform_utils.dart';

class PrimarySourceImageCubit extends Cubit<PrimarySourceImageState> {
  PrimarySourceImageCubit({
    required PrimarySource source,
    required bool isWeb,
    required bool isMobileWeb,
    PrimarySourceImageLoadingOrchestrator? imageLoadingOrchestrator,
    Future<int> Function()? maxTextureSizeLoader,
    bool autoInitialize = true,
  }) : _source = source,
       _isWeb = isWeb,
       _isMobileWeb = isMobileWeb,
       _imageLoadingOrchestrator =
           imageLoadingOrchestrator ?? PrimarySourceImageLoadingOrchestrator(),
       _maxTextureSizeLoader = maxTextureSizeLoader ?? fetchMaxTextureSize,
       super(
         PrimarySourceImageState.initial(maxTextureSize: isWeb ? 4096 : 0),
       ) {
    if (autoInitialize) {
      _initialize();
    }
  }

  final PrimarySource _source;
  final bool _isWeb;
  final bool _isMobileWeb;
  final PrimarySourceImageLoadingOrchestrator _imageLoadingOrchestrator;
  final Future<int> Function() _maxTextureSizeLoader;
  final LatestRequestGuard _imageLoadRequestGuard = LatestRequestGuard();
  final LatestRequestGuard _localPagesRequestGuard = LatestRequestGuard();

  Future<void> loadImage({
    required String page,
    required int sourceHashCode,
    bool isReload = false,
  }) async {
    final requestToken = _imageLoadRequestGuard.start();
    emit(state.copyWith(isLoading: true, imageShown: false));

    try {
      final loadResult = await _imageLoadingOrchestrator.loadPageImage(
        page: page,
        sourceHashCode: sourceHashCode,
        isWeb: _isWeb,
        isMobileWeb: _isMobileWeb,
        isReload: _isWeb ? false : isReload,
        previousPageLoaded: state.localPageLoaded[page],
      );
      if (!_canApplyImageRequest(requestToken)) {
        return;
      }

      final updatedLocalPageLoaded = Map<String, bool?>.from(
        state.localPageLoaded,
      )..[page] = loadResult.pageLoaded;

      switch (loadResult.contentAction) {
        case ImageContentAction.replace:
          emit(
            state.copyWith(
              imageDataSet: true,
              imageData: loadResult.imageData,
              isLoading: false,
              refreshError: loadResult.refreshError,
              localPageLoaded: updatedLocalPageLoaded,
            ),
          );
          break;
        case ImageContentAction.clear:
          emit(
            state.copyWith(
              imageDataSet: true,
              imageData: null,
              isLoading: false,
              refreshError: loadResult.refreshError,
              localPageLoaded: updatedLocalPageLoaded,
            ),
          );
          break;
        case ImageContentAction.keep:
          emit(
            state.copyWith(
              isLoading: false,
              refreshError: loadResult.refreshError,
              localPageLoaded: updatedLocalPageLoaded,
            ),
          );
          break;
      }
    } catch (error, stackTrace) {
      if (_canApplyImageRequest(requestToken)) {
        log.error('Image loading error: $error', stackTrace);
        emit(state.copyWith(isLoading: false));
      }
    }
  }

  void setImageShown(bool shown) {
    emit(state.copyWith(imageShown: shown));
  }

  Future<void> refreshLocalPageAvailability() async {
    final requestToken = _localPagesRequestGuard.start();
    final availability = await _imageLoadingOrchestrator
        .detectLocalPageAvailability(pages: _source.pages, isWeb: _isWeb);
    if (!_canApplyLocalPagesRequest(requestToken)) {
      return;
    }
    emit(state.copyWith(localPageLoaded: availability));
  }

  Future<void> _initialize() async {
    if (_isWeb) {
      await _detectMaxTextureSize();
    }
    await refreshLocalPageAvailability();
  }

  Future<void> _detectMaxTextureSize() async {
    try {
      final size = await _maxTextureSizeLoader();
      if (isClosed) {
        return;
      }

      final effectiveSize = size > 0 ? size : 4096;
      emit(state.copyWith(maxTextureSize: effectiveSize));

      if (_isMobileWeb) {
        log.warning(
          'A mobile browser with max texture size of $effectiveSize was detected.',
        );
      } else {
        log.info(
          'A browser with max texture size of $effectiveSize was detected.',
        );
      }
    } catch (error, stackTrace) {
      if (isClosed) {
        return;
      }
      log.error('Max texture size detection error: $error', stackTrace);
    }
  }

  bool _canApplyImageRequest(RequestToken token) {
    return !isClosed && _imageLoadRequestGuard.isActive(token);
  }

  bool _canApplyLocalPagesRequest(RequestToken token) {
    return !isClosed && _localPagesRequestGuard.isActive(token);
  }

  @override
  Future<void> close() async {
    _imageLoadRequestGuard.cancelActive();
    _localPagesRequestGuard.cancelActive();
    return super.close();
  }
}
