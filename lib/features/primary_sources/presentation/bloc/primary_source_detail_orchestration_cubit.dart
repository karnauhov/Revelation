import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_state.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_state.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';

class PrimarySourceDetailOrchestrationCubit
    extends Cubit<PrimarySourceDetailOrchestrationState> {
  PrimarySourceDetailOrchestrationCubit({
    required PrimarySource source,
    required PrimarySourceImageCubit imageCubit,
    required PrimarySourcePageSettingsCubit pageSettingsCubit,
    required PrimarySourceDescriptionCubit descriptionCubit,
    required PrimarySourceSessionCubit sessionCubit,
    required PrimarySourceViewportCubit viewportCubit,
  }) : _source = source,
       _imageCubit = imageCubit,
       _pageSettingsCubit = pageSettingsCubit,
       _descriptionCubit = descriptionCubit,
       _sessionCubit = sessionCubit,
       _viewportCubit = viewportCubit,
       super(PrimarySourceDetailOrchestrationState.initial) {
    imageController = ImagePreviewController(_source.maxScale);
    imageController.transformationController.addListener(
      _updateTransformStatus,
    );
    _viewportStateSubscription = _viewportCubit.stream.listen((state) {
      zoomStatusNotifier.value = state.zoomStatus;
    });

    final initialPage = selectedPage;
    if (initialPage != null) {
      unawaited(loadImage(initialPage.image));
    }
  }

  final PrimarySource _source;
  final PrimarySourceImageCubit _imageCubit;
  final PrimarySourcePageSettingsCubit _pageSettingsCubit;
  final PrimarySourceDescriptionCubit _descriptionCubit;
  final PrimarySourceSessionCubit _sessionCubit;
  final PrimarySourceViewportCubit _viewportCubit;

  late final ImagePreviewController imageController;
  final ValueNotifier<ZoomStatus> zoomStatusNotifier = ValueNotifier(
    const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
  );

  final LatestRequestGuard _imageLoadRequestGuard = LatestRequestGuard();
  StreamSubscription<PrimarySourceViewportState>? _viewportStateSubscription;
  Timer? _restoreDebounceTimer;
  Timer? _saveDebounceTimer;
  bool _isDisposed = false;

  Uint8List? get imageData => _imageCubit.state.imageData;
  model.Page? get selectedPage => _sessionCubit.state.selectedPage;
  bool get scaleAndPositionRestored =>
      _viewportCubit.state.scaleAndPositionRestored;
  double get dx => _viewportCubit.state.dx;
  double get dy => _viewportCubit.state.dy;
  double get scale => _viewportCubit.state.scale;
  double get savedX => _viewportCubit.state.savedX;
  double get savedY => _viewportCubit.state.savedY;
  double get savedScale => _viewportCubit.state.savedScale;

  Future<void> loadImage(String page, {bool isReload = false}) async {
    final requestToken = _imageLoadRequestGuard.start();
    try {
      _viewportCubit.markImageLoadingStarted();

      final pageSettings = await _pageSettingsCubit.loadSettingsForPage(
        source: _source,
        selectedPage: selectedPage,
      );
      if (!_canApplyImageRequest(requestToken)) {
        return;
      }
      _viewportCubit.applyViewportSettings(pageSettings);

      await _imageCubit.loadImage(
        page: page,
        sourceHashCode: _source.hashCode,
        isReload: isReload,
      );
      if (!_canApplyImageRequest(requestToken)) {
        return;
      }
    } catch (error, stackTrace) {
      if (_canApplyImageRequest(requestToken)) {
        log.error('Image loading error: $error', stackTrace);
      }
    }
    if (!_canApplyImageRequest(requestToken)) {
      return;
    }
    if (imageData != null) {
      _sessionCubit.setImageName('${_source.hashCode}_$page');
    } else {
      _sessionCubit.setImageName('');
    }
    _updateTransformStatus();
  }

  Future<void> changeSelectedPage(model.Page? newPage) async {
    _viewportCubit.markImageLoadingStarted();
    _sessionCubit.setSelectedPage(newPage);
    _viewportCubit.resetColorReplacement();

    if (newPage != null) {
      await loadImage(newPage.image);
    } else {
      _viewportCubit.resetViewportWithNoPage();
      _pageSettingsCubit.resetToDefaults();
    }
  }

  void toggleNegative() {
    _pageSettingsCubit.toggleNegative();
    savePageSettings();
  }

  void toggleMonochrome() {
    _pageSettingsCubit.toggleMonochrome();
    savePageSettings();
  }

  void applyBrightnessContrast(double brightness, double contrast) {
    _pageSettingsCubit.applyBrightnessContrast(brightness, contrast);
    savePageSettings();
  }

  void resetBrightnessContrast() {
    _pageSettingsCubit.resetBrightnessContrast();
    savePageSettings();
  }

  void toggleShowWordSeparators() {
    _pageSettingsCubit.toggleShowWordSeparators();
    savePageSettings();
  }

  void toggleShowStrongNumbers() {
    _pageSettingsCubit.toggleShowStrongNumbers();
    savePageSettings();
  }

  void toggleShowVerseNumbers() {
    _pageSettingsCubit.toggleShowVerseNumbers();
    savePageSettings();
  }

  void removePageSettings() {
    _pageSettingsCubit.clearSettingsForPage(
      source: _source,
      selectedPage: selectedPage,
    );
    _viewportCubit.resetViewportAndRenderControls();
    imageController.backToMinScale();
  }

  void startSelectAreaMode() {
    _viewportCubit.startSelectAreaMode();
  }

  void finishSelectAreaMode(Rect? selectedArea) {
    _viewportCubit.finishSelectAreaMode(selectedArea);
  }

  void startPipetteMode({required bool isColorToReplace}) {
    _viewportCubit.startPipetteMode(isColorToReplace: isColorToReplace);
  }

  void finishPipetteMode(Color? color) {
    _viewportCubit.finishPipetteMode(color);
  }

  void applyColorReplacement({
    required Rect? selectedArea,
    required Color colorToReplace,
    required Color newColor,
    required double tolerance,
  }) {
    _viewportCubit.applyColorReplacement(
      selectedArea: selectedArea,
      colorToReplace: colorToReplace,
      newColor: newColor,
      tolerance: tolerance,
    );
  }

  void resetColorReplacement() {
    _viewportCubit.resetColorReplacement();
  }

  void setMenuOpen(bool isMenuOpen) {
    _sessionCubit.setMenuOpen(isMenuOpen);
  }

  void updateDescriptionContent({
    required String content,
    required DescriptionKind type,
    required int? number,
  }) {
    _descriptionCubit.updateDescriptionContent(
      content: content,
      type: type,
      number: number,
    );
  }

  void showCommonInfo(AppLocalizations localizations) {
    _descriptionCubit.showCommonInfo(localizations);
  }

  bool navigateDescriptionSelection(
    AppLocalizations localizations, {
    required bool forward,
  }) {
    return _descriptionCubit.navigateSelection(
      localizations,
      forward: forward,
      source: _source,
      selectedPage: selectedPage,
    );
  }

  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() {
    return _descriptionCubit.getGreekStrongPickerEntries();
  }

  bool showInfoForStrongNumber({
    required int strongNumber,
    required AppLocalizations localizations,
  }) {
    return _descriptionCubit.showInfoForStrongNumber(
      strongNumber: strongNumber,
      localizations: localizations,
    );
  }

  bool showInfoForWord({
    required int wordIndex,
    required AppLocalizations localizations,
  }) {
    return _descriptionCubit.showInfoForWord(
      wordIndex: wordIndex,
      localizations: localizations,
      source: _source,
      selectedPage: selectedPage,
    );
  }

  bool showInfoForVerse({
    required int verseIndex,
    required AppLocalizations localizations,
  }) {
    return _descriptionCubit.showInfoForVerse(
      verseIndex: verseIndex,
      localizations: localizations,
      source: _source,
      selectedPage: selectedPage,
    );
  }

  void savePageSettings() {
    _pageSettingsCubit.saveSettingsForPage(
      source: _source,
      selectedPage: selectedPage,
      scaleAndPositionRestored: scaleAndPositionRestored,
      posX: dx,
      posY: dy,
      scale: scale,
    );
  }

  void restorePositionAndScale() {
    if (scaleAndPositionRestored) {
      return;
    }

    _restoreDebounceTimer?.cancel();
    _restoreDebounceTimer = Timer(const Duration(milliseconds: 1000), () {
      imageController.setTransformParams(savedX, savedY, savedScale);
      _viewportCubit.setScaleAndPositionRestored(true);
    });
  }

  bool _canApplyImageRequest(RequestToken token) {
    return !_isDisposed && _imageLoadRequestGuard.isActive(token);
  }

  void _updateTransformStatus() {
    if (_isDisposed) {
      return;
    }

    if (imageData == null) {
      _viewportCubit.setZoomStatus(
        const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
      );
      return;
    }

    final matrix = imageController.transformationController.value;
    final currentDx = matrix.storage[12];
    final currentDy = matrix.storage[13];
    final currentScale = matrix.getMaxScaleOnAxis();
    _viewportCubit.updateTransform(
      dx: currentDx,
      dy: currentDy,
      scale: currentScale,
      zoomStatus: ZoomStatus(
        canZoomIn: currentScale < imageController.maxScale,
        canZoomOut: currentScale > imageController.minScale,
        canReset: currentScale != imageController.minScale,
      ),
    );
    if (scaleAndPositionRestored) {
      _saveDebounceTimer?.cancel();
      _saveDebounceTimer = Timer(const Duration(seconds: 1), savePageSettings);
    }
  }

  @override
  Future<void> close() async {
    _isDisposed = true;
    _imageLoadRequestGuard.cancelActive();
    _viewportStateSubscription?.cancel();
    _restoreDebounceTimer?.cancel();
    _saveDebounceTimer?.cancel();
    imageController.transformationController.removeListener(
      _updateTransformStatus,
    );
    imageController.dispose();
    zoomStatusNotifier.dispose();
    return super.close();
  }
}
