import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_selection_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_state.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/shared/utils/common.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/image_preview_controller.dart';

class PrimarySourceViewModel {
  late final PrimarySourceDescriptionCubit _descriptionCubit;
  late final bool _ownsDescriptionCubit;
  late final PrimarySourceImageCubit _imageCubit;
  late final bool _ownsImageCubit;
  late final PrimarySourcePageSettingsCubit _pageSettingsCubit;
  late final bool _ownsPageSettingsCubit;
  late final PrimarySourceSelectionCubit _selectionCubit;
  late final bool _ownsSelectionCubit;
  late final PrimarySourceViewportCubit _viewportCubit;
  late final bool _ownsViewportCubit;
  StreamSubscription<PrimarySourceViewportState>? _viewportStateSubscription;
  final PrimarySourceSessionCubit _sessionCubit;
  final bool _ownsSessionCubit;

  late ImagePreviewController imageController;
  final ValueNotifier<ZoomStatus> zoomStatusNotifier = ValueNotifier(
    const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
  );

  late final bool _isWeb;
  late final bool _isMobileWeb;
  void Function(Color?)? _onPipettePicked;
  void Function(Rect?)? _onAreaSelected;
  Timer? _restoreDebounceTimer;
  Timer? _saveDebounceTimer;
  final LatestRequestGuard _imageLoadRequestGuard = LatestRequestGuard();
  bool _isDisposed = false;

  bool get isMobileWeb => _isMobileWeb;
  Uint8List? get imageData => _imageCubit.state.imageData;
  bool get isLoading => _imageCubit.state.isLoading;
  bool get refreshError => _imageCubit.state.refreshError;
  bool get imageShown => _imageCubit.state.imageShown;
  Map<String, bool?> get localPageLoaded => _imageCubit.state.localPageLoaded;
  bool get isNegative => _pageSettingsCubit.state.isNegative;
  bool get isMonochrome => _pageSettingsCubit.state.isMonochrome;
  double get brightness => _pageSettingsCubit.state.brightness;
  double get contrast => _pageSettingsCubit.state.contrast;
  bool get showWordSeparators => _pageSettingsCubit.state.showWordSeparators;
  bool get showStrongNumbers => _pageSettingsCubit.state.showStrongNumbers;
  bool get showVerseNumbers => _pageSettingsCubit.state.showVerseNumbers;
  int get maxTextureSize => _imageCubit.state.maxTextureSize;
  bool get pipetteMode => _viewportCubit.state.pipetteMode;
  bool get selectAreaMode => _viewportCubit.state.selectAreaMode;
  Rect? get selectedArea => _viewportCubit.state.selectedArea;
  Color get colorToReplace => _viewportCubit.state.colorToReplace;
  Color get newColor => _viewportCubit.state.newColor;
  double get tolerance => _viewportCubit.state.tolerance;
  bool get scaleAndPositionRestored =>
      _viewportCubit.state.scaleAndPositionRestored;
  double get dx => _viewportCubit.state.dx;
  double get dy => _viewportCubit.state.dy;
  double get scale => _viewportCubit.state.scale;
  double get savedX => _viewportCubit.state.savedX;
  double get savedY => _viewportCubit.state.savedY;
  double get savedScale => _viewportCubit.state.savedScale;
  PrimarySource get primarySource => _sessionCubit.state.source;
  model.Page? get selectedPage => _sessionCubit.state.selectedPage;
  String get imageName => _sessionCubit.state.imageName;
  bool get isMenuOpen => _sessionCubit.state.isMenuOpen;
  String get pageSettings => _pageSettingsCubit.state.rawSettings;
  bool get showDescription => _descriptionCubit.state.showDescription;
  String? get descriptionContent => _descriptionCubit.state.content;
  DescriptionKind get currentDescriptionType =>
      _selectionCubit.state.currentType;
  int? get currentDescriptionNumber => _selectionCubit.state.currentNumber;

  PrimarySourceViewModel(
    PagesRepository pagesRepository, {
    required PrimarySource primarySource,
    PrimarySourceImageCubit? imageCubit,
    PrimarySourcePageSettingsCubit? pageSettingsCubit,
    PrimarySourceSelectionCubit? selectionCubit,
    PrimarySourceDescriptionCubit? descriptionCubit,
    PrimarySourceViewportCubit? viewportCubit,
    PrimarySourceSessionCubit? sessionCubit,
    DescriptionContentService? descriptionService,
    PrimarySourcePageSettingsOrchestrator? pageSettingsOrchestrator,
  }) : _sessionCubit =
           sessionCubit ?? PrimarySourceSessionCubit(source: primarySource),
       _ownsSessionCubit = sessionCubit == null {
    imageController = ImagePreviewController(primarySource.maxScale);
    imageController.transformationController.addListener(
      _updateTransformStatus,
    );

    _isWeb = isWeb();
    _isMobileWeb = _isWeb && isMobileBrowser();

    _ownsImageCubit = imageCubit == null;
    _imageCubit =
        imageCubit ??
        PrimarySourceImageCubit(
          source: primarySource,
          isWeb: _isWeb,
          isMobileWeb: _isMobileWeb,
        );
    _ownsPageSettingsCubit = pageSettingsCubit == null;
    _pageSettingsCubit =
        pageSettingsCubit ??
        PrimarySourcePageSettingsCubit(
          pageSettingsOrchestrator ??
              PrimarySourcePageSettingsOrchestrator(pagesRepository),
        );
    _ownsDescriptionCubit = descriptionCubit == null;
    _descriptionCubit =
        descriptionCubit ??
        PrimarySourceDescriptionCubit(descriptionService: descriptionService);
    _ownsViewportCubit = viewportCubit == null;
    _viewportCubit = viewportCubit ?? PrimarySourceViewportCubit();
    _viewportStateSubscription = _viewportCubit.stream.listen((state) {
      zoomStatusNotifier.value = state.zoomStatus;
    });
    _ownsSelectionCubit = selectionCubit == null;
    _selectionCubit = selectionCubit ?? PrimarySourceSelectionCubit();
    _syncSelectionFromDescriptionState();

    if (selectedPage != null) {
      unawaited(loadImage(selectedPage!.image));
    }
  }

  Future<void> loadImage(String page, {bool isReload = false}) async {
    final requestToken = _imageLoadRequestGuard.start();
    try {
      _imageCubit.setImageShown(false);
      _viewportCubit.markImageLoadingStarted();

      final pageSettings = await _pageSettingsCubit.loadSettingsForPage(
        source: primarySource,
        selectedPage: selectedPage,
      );
      if (!_canApplyImageRequest(requestToken)) {
        return;
      }
      _applyViewportSettings(pageSettings);

      await _imageCubit.loadImage(
        page: page,
        sourceHashCode: primarySource.hashCode,
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
      _sessionCubit.setImageName('${primarySource.hashCode}_$page');
    } else {
      _sessionCubit.setImageName('');
    }
    _updateTransformStatus();
  }

  Future<void> changeSelectedPage(model.Page? newPage) async {
    _imageCubit.setImageShown(false);
    _viewportCubit.markImageLoadingStarted();
    _sessionCubit.setSelectedPage(newPage);
    resetColorReplacement();
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

  void startSelectAreaMode(void Function(Rect?) onSelected) {
    _viewportCubit.startSelectAreaMode();
    _onAreaSelected = onSelected;
  }

  void finishSelectAreaMode(Rect? selectRect) {
    if (selectAreaMode && _onAreaSelected != null) {
      _onAreaSelected!(selectRect);
    }
    _viewportCubit.finishSelectAreaMode(selectRect);
    _onAreaSelected = null;
  }

  void startPipetteMode(void Function(Color?) onPicked, bool isColorToReplace) {
    _viewportCubit.startPipetteMode(isColorToReplace: isColorToReplace);
    _onPipettePicked = onPicked;
  }

  void finishPipetteMode(Color? color) {
    if (pipetteMode && _onPipettePicked != null) {
      _onPipettePicked!(color);
    }
    _viewportCubit.finishPipetteMode(color);
    _onPipettePicked = null;
  }

  void applyColorReplacement(
    Rect? selectedArea,
    Color colorToReplace,
    Color newColor,
    double tolerance,
  ) {
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

  void setMenuOpen(bool value) {
    _sessionCubit.setMenuOpen(value);
  }

  void savePageSettings() {
    _pageSettingsCubit.saveSettingsForPage(
      source: primarySource,
      selectedPage: selectedPage,
      scaleAndPositionRestored: scaleAndPositionRestored,
      posX: dx,
      posY: dy,
      scale: scale,
    );
  }

  void removePageSettings() {
    _pageSettingsCubit.clearSettingsForPage(
      source: primarySource,
      selectedPage: selectedPage,
    );
    _viewportCubit.resetViewportAndRenderControls();
    imageController.backToMinScale();
  }

  void restorePositionAndScale() {
    if (!scaleAndPositionRestored) {
      _restoreDebounceTimer?.cancel();
      _restoreDebounceTimer = Timer(const Duration(milliseconds: 1000), () {
        imageController.setTransformParams(savedX, savedY, savedScale);
        _viewportCubit.setScaleAndPositionRestored(true);
      });
    }
  }

  void toggleDescription() {
    _descriptionCubit.toggleDescriptionVisibility();
  }

  void updateDescriptionContent(
    String content,
    DescriptionKind type,
    int? number,
  ) {
    _descriptionCubit.updateDescriptionContent(
      content: content,
      type: type,
      number: number,
    );
    _syncSelectionFromDescriptionState();
  }

  void showCommonInfo(BuildContext context) {
    _descriptionCubit.showCommonInfo(context);
    _syncSelectionFromDescriptionState();
  }

  bool navigateDescriptionSelection(
    BuildContext context, {
    required bool forward,
  }) {
    final navigated = _descriptionCubit.navigateSelection(
      context,
      forward: forward,
      source: primarySource,
      selectedPage: selectedPage,
    );
    if (navigated) {
      _syncSelectionFromDescriptionState();
    }
    return navigated;
  }

  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() {
    return _descriptionCubit.getGreekStrongPickerEntries();
  }

  void showInfoForStrongNumber(int strongNumber, BuildContext context) {
    final shown = _descriptionCubit.showInfoForStrongNumber(
      strongNumber: strongNumber,
      context: context,
    );
    if (!shown) {
      return;
    }
    _syncSelectionFromDescriptionState();
  }

  void showInfoForWord(int wordIndex, BuildContext context) {
    final shown = _descriptionCubit.showInfoForWord(
      wordIndex: wordIndex,
      context: context,
      source: primarySource,
      selectedPage: selectedPage,
    );
    if (!shown) {
      return;
    }
    _syncSelectionFromDescriptionState();
  }

  void showInfoForVerse(int verseIndex, BuildContext context) {
    final shown = _descriptionCubit.showInfoForVerse(
      verseIndex: verseIndex,
      context: context,
      source: primarySource,
      selectedPage: selectedPage,
    );
    if (!shown) {
      return;
    }
    _syncSelectionFromDescriptionState();
  }

  void _applyViewportSettings(PageSettingsState settings) {
    _viewportCubit.applyViewportSettings(settings);
  }

  void _syncSelectionFromDescriptionState() {
    final descriptionState = _descriptionCubit.state;
    _selectionCubit.setSelection(
      type: descriptionState.currentType,
      number: descriptionState.currentNumber,
    );
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
    } else {
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
        _saveDebounceTimer = Timer(
          const Duration(seconds: 1),
          savePageSettings,
        );
      }
    }
  }

  void dispose() {
    _imageLoadRequestGuard.cancelActive();
    _viewportStateSubscription?.cancel();
    _restoreDebounceTimer?.cancel();
    _saveDebounceTimer?.cancel();
    imageController.transformationController.removeListener(
      _updateTransformStatus,
    );
    imageController.dispose();
    zoomStatusNotifier.dispose();
    _onPipettePicked = null;
    _onAreaSelected = null;
    _isDisposed = true;
    if (_ownsDescriptionCubit) {
      unawaited(_descriptionCubit.close());
    }
    if (_ownsImageCubit) {
      unawaited(_imageCubit.close());
    }
    if (_ownsPageSettingsCubit) {
      unawaited(_pageSettingsCubit.close());
    }
    if (_ownsSelectionCubit) {
      unawaited(_selectionCubit.close());
    }
    if (_ownsViewportCubit) {
      unawaited(_viewportCubit.close());
    }
    if (_ownsSessionCubit) {
      unawaited(_sessionCubit.close());
    }
  }
}
