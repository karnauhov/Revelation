import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/description_panel_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/image_preview_controller.dart';

class PrimarySourceViewModel extends ChangeNotifier {
  final PrimarySource primarySource;
  final PrimarySourceDescriptionPanelOrchestrator _descriptionPanelOrchestrator;
  final PrimarySourceImageLoadingOrchestrator _imageLoadingOrchestrator;
  final PrimarySourcePageSettingsOrchestrator _pageSettingsOrchestrator;
  model.Page? selectedPage;
  Uint8List? imageData;
  String imageName = "";
  bool isLoading = false;
  bool refreshError = false;
  bool imageShown = false;
  bool scaleAndPositionRestored = false;
  double dx = 0;
  double dy = 0;
  double scale = 1;
  double savedX = 0;
  double savedY = 0;
  double savedScale = 0;
  bool isNegative = false;
  bool isMonochrome = false;
  double brightness = 0;
  double contrast = 100;
  Rect? selectedArea;
  Color colorToReplace = const Color(0xFFFFFFFF);
  Color newColor = const Color(0xFFFFFFFF);
  double tolerance = 0;
  bool showWordSeparators = false;
  bool showStrongNumbers = false;
  bool showVerseNumbers = true;

  final Map<String, bool?> localPageLoaded = {};
  late ImagePreviewController imageController;
  final ValueNotifier<ZoomStatus> zoomStatusNotifier = ValueNotifier(
    const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
  );

  late String _pageSettings;
  late final bool _isWeb;
  late final bool _isMobileWeb;
  int _maxTextureSize = 4096;
  bool _pipetteMode = false;
  void Function(Color?)? _onPipettePicked;
  bool _isColorToReplace = true;
  bool _selectAreaMode = false;
  void Function(Rect?)? _onAreaSelected;
  bool _isMenuOpen = false;
  Timer? _restoreDebounceTimer;
  Timer? _saveDebounceTimer;
  final LatestRequestGuard _imageLoadRequestGuard = LatestRequestGuard();
  final LatestRequestGuard _localPagesRequestGuard = LatestRequestGuard();
  bool _isDisposed = false;

  bool get isMobileWeb => _isMobileWeb;
  int get maxTextureSize => _maxTextureSize;
  bool get pipetteMode => _pipetteMode;
  bool get selectAreaMode => _selectAreaMode;
  bool get isMenuOpen => _isMenuOpen;
  String get pageSettings => _pageSettings;
  bool get showDescription =>
      _descriptionPanelOrchestrator.state.showDescription;
  String? get descriptionContent => _descriptionPanelOrchestrator.state.content;
  DescriptionKind get currentDescriptionType =>
      _descriptionPanelOrchestrator.state.currentType;
  int? get currentDescriptionNumber =>
      _descriptionPanelOrchestrator.state.currentNumber;

  PrimarySourceViewModel(
    PagesRepository pagesRepository, {
    required this.primarySource,
    DescriptionContentService? descriptionService,
    PrimarySourceImageLoadingOrchestrator? imageLoadingOrchestrator,
    PrimarySourcePageSettingsOrchestrator? pageSettingsOrchestrator,
    PrimarySourceDescriptionPanelOrchestrator? descriptionPanelOrchestrator,
  }) : _descriptionPanelOrchestrator =
           descriptionPanelOrchestrator ??
           PrimarySourceDescriptionPanelOrchestrator(
             descriptionService: descriptionService,
           ),
       _imageLoadingOrchestrator =
           imageLoadingOrchestrator ?? PrimarySourceImageLoadingOrchestrator(),
       _pageSettingsOrchestrator =
           pageSettingsOrchestrator ??
           PrimarySourcePageSettingsOrchestrator(pagesRepository) {
    imageController = ImagePreviewController(primarySource.maxScale);
    imageController.transformationController.addListener(
      _updateTransformStatus,
    );

    _isWeb = isWeb();
    _isMobileWeb = _isWeb && isMobileBrowser();

    if (_isWeb) {
      fetchMaxTextureSize().then((size) {
        _maxTextureSize = size > 0 ? size : 4096;
        if (_isMobileWeb) {
          log.warning(
            "A mobile browser with max texture size of $_maxTextureSize was detected.",
          );
        } else {
          log.info(
            "A browser with max texture size of $_maxTextureSize was detected.",
          );
        }
      });
    } else {
      _maxTextureSize = 0;
    }

    if (primarySource.pages.isNotEmpty && primarySource.permissionsReceived) {
      selectedPage = primarySource.pages.first;
      loadImage(selectedPage!.image);
    }
    _checkLocalPages();
  }

  @override
  void notifyListeners() {
    if (_isDisposed) {
      return;
    }
    super.notifyListeners();
  }

  Future<void> loadImage(String page, {bool isReload = false}) async {
    final requestToken = _imageLoadRequestGuard.start();
    try {
      isLoading = true;
      imageShown = false;
      scaleAndPositionRestored = false;
      notifyListeners();

      final pageSettings = await _getPagesSettings();
      if (!_canApplyImageRequest(requestToken)) {
        return;
      }
      _applyPageSettings(pageSettings);

      if (!_canApplyImageRequest(requestToken)) {
        return;
      }
      notifyListeners();

      final loadResult = await _imageLoadingOrchestrator.loadPageImage(
        page: page,
        sourceHashCode: primarySource.hashCode,
        isWeb: _isWeb,
        isMobileWeb: _isMobileWeb,
        isReload: _isWeb ? false : isReload,
        previousPageLoaded: localPageLoaded[page],
      );
      if (!_canApplyImageRequest(requestToken)) {
        return;
      }

      localPageLoaded[page] = loadResult.pageLoaded;
      refreshError = loadResult.refreshError;
      switch (loadResult.contentAction) {
        case ImageContentAction.replace:
          imageData = loadResult.imageData;
          imageName = loadResult.imageName;
          break;
        case ImageContentAction.clear:
          imageData = null;
          imageName = '';
          break;
        case ImageContentAction.keep:
          break;
      }
    } catch (error, stackTrace) {
      if (_canApplyImageRequest(requestToken)) {
        log.error('Image loading error: $error', stackTrace);
      }
    }
    if (!_canApplyImageRequest(requestToken)) {
      return;
    }
    _updateTransformStatus();
    isLoading = false;
    notifyListeners();
  }

  Future<void> changeSelectedPage(model.Page? newPage) async {
    imageShown = false;
    scaleAndPositionRestored = false;
    selectedPage = newPage;
    resetColorReplacement();
    notifyListeners();
    if (newPage != null) {
      await loadImage(newPage.image);
    } else {
      scaleAndPositionRestored = true;
      savedX = dx = 0;
      savedY = dy = 0;
      savedScale = scale = 0;
      isNegative = false;
      isMonochrome = false;
      brightness = 0;
      contrast = 100;
      showWordSeparators = false;
      showStrongNumbers = false;
      showVerseNumbers = true;
      notifyListeners();
    }
  }

  void toggleNegative() {
    isNegative = !isNegative;
    savePageSettings();
    notifyListeners();
  }

  void toggleMonochrome() {
    isMonochrome = !isMonochrome;
    savePageSettings();
    notifyListeners();
  }

  void applyBrightnessContrast(double brightness, double contrast) {
    this.brightness = brightness;
    this.contrast = contrast;
    savePageSettings();
    notifyListeners();
  }

  void resetBrightnessContrast() {
    brightness = 0;
    contrast = 100;
    savePageSettings();
    notifyListeners();
  }

  void startSelectAreaMode(void Function(Rect?) onSelected) {
    _selectAreaMode = true;
    _onAreaSelected = onSelected;
    notifyListeners();
  }

  void finishSelectAreaMode(Rect? selectRect) {
    if (_selectAreaMode && _onAreaSelected != null) {
      _onAreaSelected!(selectRect);
    }
    selectedArea = selectRect;
    _selectAreaMode = false;
    _onAreaSelected = null;
    notifyListeners();
  }

  void startPipetteMode(void Function(Color?) onPicked, bool isColorToReplace) {
    _pipetteMode = true;
    _onPipettePicked = onPicked;
    _isColorToReplace = isColorToReplace;
    notifyListeners();
  }

  void finishPipetteMode(Color? color) {
    if (_pipetteMode && _onPipettePicked != null) {
      _onPipettePicked!(color);
    }
    if (color != null) {
      if (_isColorToReplace) {
        colorToReplace = color;
      } else {
        newColor = color;
      }
    }
    _pipetteMode = false;
    _onPipettePicked = null;
    notifyListeners();
  }

  void applyColorReplacement(
    Rect? selectedArea,
    Color colorToReplace,
    Color newColor,
    double tolerance,
  ) {
    this.selectedArea = selectedArea;
    this.colorToReplace = colorToReplace;
    this.newColor = newColor;
    this.tolerance = tolerance;
    notifyListeners();
  }

  void resetColorReplacement() {
    selectedArea = null;
    colorToReplace = const Color(0xFFFFFFFF);
    newColor = const Color(0xFFFFFFFF);
    tolerance = 0;
    notifyListeners();
  }

  void toggleShowWordSeparators() {
    showWordSeparators = !showWordSeparators;
    savePageSettings();
    notifyListeners();
  }

  void toggleShowStrongNumbers() {
    showStrongNumbers = !showStrongNumbers;
    savePageSettings();
    notifyListeners();
  }

  void toggleShowVerseNumbers() {
    showVerseNumbers = !showVerseNumbers;
    savePageSettings();
    notifyListeners();
  }

  void setMenuOpen(bool value) {
    _isMenuOpen = value;
    notifyListeners();
  }

  void savePageSettings() {
    _pageSettings = _pageSettingsOrchestrator.saveSettingsForPage(
      source: primarySource,
      selectedPage: selectedPage,
      scaleAndPositionRestored: scaleAndPositionRestored,
      posX: dx,
      posY: dy,
      scale: scale,
      isNegative: isNegative,
      isMonochrome: isMonochrome,
      brightness: brightness,
      contrast: contrast,
      showWordSeparators: showWordSeparators,
      showStrongNumbers: showStrongNumbers,
      showVerseNumbers: showVerseNumbers,
    );
  }

  void removePageSettings() {
    _pageSettings = _pageSettingsOrchestrator.clearSettingsForPage(
      source: primarySource,
      selectedPage: selectedPage,
    );
    savedX = dx = 0;
    savedY = dy = 0;
    savedScale = scale = 0;
    isNegative = false;
    isMonochrome = false;
    brightness = 0;
    contrast = 100;
    showWordSeparators = false;
    showStrongNumbers = false;
    showVerseNumbers = true;
    imageController.backToMinScale();
    resetColorReplacement();
  }

  void restorePositionAndScale() {
    if (!scaleAndPositionRestored) {
      _restoreDebounceTimer?.cancel();
      _restoreDebounceTimer = Timer(const Duration(milliseconds: 1000), () {
        imageController.setTransformParams(savedX, savedY, savedScale);
        scaleAndPositionRestored = true;
      });
    }
  }

  void toggleDescription() {
    _descriptionPanelOrchestrator.toggleDescriptionVisibility();
    notifyListeners();
  }

  void updateDescriptionContent(
    String content,
    DescriptionKind type,
    int? number,
  ) {
    _descriptionPanelOrchestrator.updateDescriptionContent(
      content: content,
      type: type,
      number: number,
    );
    notifyListeners();
  }

  void showCommonInfo(BuildContext context) {
    _descriptionPanelOrchestrator.showCommonInfo(context);
    notifyListeners();
  }

  bool navigateDescriptionSelection(
    BuildContext context, {
    required bool forward,
  }) {
    final navigated = _descriptionPanelOrchestrator.navigateSelection(
      context,
      forward: forward,
      source: primarySource,
      selectedPage: selectedPage,
    );
    if (navigated) {
      notifyListeners();
    }
    return navigated;
  }

  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() {
    return _descriptionPanelOrchestrator.getGreekStrongPickerEntries();
  }

  void showInfoForStrongNumber(int strongNumber, BuildContext context) {
    final shown = _descriptionPanelOrchestrator.showInfoForStrongNumber(
      strongNumber: strongNumber,
      context: context,
    );
    if (!shown) {
      return;
    }
    notifyListeners();
  }

  void showInfoForWord(int wordIndex, BuildContext context) {
    final shown = _descriptionPanelOrchestrator.showInfoForWord(
      wordIndex: wordIndex,
      context: context,
      source: primarySource,
      selectedPage: selectedPage,
    );
    if (!shown) {
      return;
    }
    notifyListeners();
  }

  void showInfoForVerse(int verseIndex, BuildContext context) {
    final shown = _descriptionPanelOrchestrator.showInfoForVerse(
      verseIndex: verseIndex,
      context: context,
      source: primarySource,
      selectedPage: selectedPage,
    );
    if (!shown) {
      return;
    }
    notifyListeners();
  }

  Future<PageSettingsState> _getPagesSettings() {
    return _pageSettingsOrchestrator.loadSettingsForPage(
      source: primarySource,
      selectedPage: selectedPage,
    );
  }

  void _applyPageSettings(PageSettingsState settings) {
    _pageSettings = settings.rawSettings;
    savedX = dx = settings.posX;
    savedY = dy = settings.posY;
    savedScale = scale = settings.scale;
    isNegative = settings.isNegative;
    isMonochrome = settings.isMonochrome;
    brightness = settings.brightness;
    contrast = settings.contrast;
    showWordSeparators = settings.showWordSeparators;
    showStrongNumbers = settings.showStrongNumbers;
    showVerseNumbers = settings.showVerseNumbers;
  }

  Future<void> _checkLocalPages() async {
    final requestToken = _localPagesRequestGuard.start();
    final availability = await _imageLoadingOrchestrator
        .detectLocalPageAvailability(pages: primarySource.pages, isWeb: _isWeb);
    if (!_canApplyLocalPagesRequest(requestToken)) {
      return;
    }
    localPageLoaded
      ..clear()
      ..addAll(availability);
    notifyListeners();
  }

  bool _canApplyImageRequest(RequestToken token) {
    return !_isDisposed && _imageLoadRequestGuard.isActive(token);
  }

  bool _canApplyLocalPagesRequest(RequestToken token) {
    return !_isDisposed && _localPagesRequestGuard.isActive(token);
  }

  void _updateTransformStatus() {
    if (_isDisposed) {
      return;
    }

    if (imageData == null) {
      Future.microtask(() {
        if (_isDisposed) {
          return;
        }
        zoomStatusNotifier.value = const ZoomStatus(
          canZoomIn: false,
          canZoomOut: false,
          canReset: false,
        );
      });
    } else {
      final matrix = imageController.transformationController.value;
      dx = matrix.storage[12];
      dy = matrix.storage[13];
      scale = matrix.getMaxScaleOnAxis();
      Future.microtask(() {
        if (_isDisposed) {
          return;
        }
        zoomStatusNotifier.value = ZoomStatus(
          canZoomIn: scale < imageController.maxScale,
          canZoomOut: scale > imageController.minScale,
          canReset: scale != imageController.minScale,
        );
      });
      if (scaleAndPositionRestored) {
        _saveDebounceTimer?.cancel();
        _saveDebounceTimer = Timer(
          const Duration(seconds: 1),
          savePageSettings,
        );
      }
    }
  }

  @override
  void dispose() {
    _imageLoadRequestGuard.cancelActive();
    _localPagesRequestGuard.cancelActive();
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
    super.dispose();
  }
}
