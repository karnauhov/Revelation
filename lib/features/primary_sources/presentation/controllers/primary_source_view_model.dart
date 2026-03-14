import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_state.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_state.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_state.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_selection_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_selection_state.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/shared/utils/common.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/image_preview_controller.dart';

class PrimarySourceViewModel extends ChangeNotifier {
  late final PrimarySourceDescriptionCubit _descriptionCubit;
  late final bool _ownsDescriptionCubit;
  StreamSubscription<PrimarySourceDescriptionState>?
  _descriptionStateSubscription;
  late final PrimarySourceImageCubit _imageCubit;
  late final bool _ownsImageCubit;
  StreamSubscription<PrimarySourceImageState>? _imageStateSubscription;
  late final PrimarySourcePageSettingsCubit _pageSettingsCubit;
  late final bool _ownsPageSettingsCubit;
  StreamSubscription<PrimarySourcePageSettingsState>?
  _pageSettingsStateSubscription;
  late final PrimarySourceSelectionCubit _selectionCubit;
  late final bool _ownsSelectionCubit;
  StreamSubscription<PrimarySourceSelectionState>? _selectionStateSubscription;
  final PrimarySourceSessionCubit _sessionCubit;
  final bool _ownsSessionCubit;
  bool scaleAndPositionRestored = false;
  double dx = 0;
  double dy = 0;
  double scale = 1;
  double savedX = 0;
  double savedY = 0;
  double savedScale = 0;
  Rect? selectedArea;
  Color colorToReplace = const Color(0xFFFFFFFF);
  Color newColor = const Color(0xFFFFFFFF);
  double tolerance = 0;

  late ImagePreviewController imageController;
  final ValueNotifier<ZoomStatus> zoomStatusNotifier = ValueNotifier(
    const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
  );

  late final bool _isWeb;
  late final bool _isMobileWeb;
  bool _pipetteMode = false;
  void Function(Color?)? _onPipettePicked;
  bool _isColorToReplace = true;
  bool _selectAreaMode = false;
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
  bool get pipetteMode => _pipetteMode;
  bool get selectAreaMode => _selectAreaMode;
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
    _imageStateSubscription = _imageCubit.stream.listen(
      (_) => notifyListeners(),
    );
    _ownsPageSettingsCubit = pageSettingsCubit == null;
    _pageSettingsCubit =
        pageSettingsCubit ??
        PrimarySourcePageSettingsCubit(
          pageSettingsOrchestrator ??
              PrimarySourcePageSettingsOrchestrator(pagesRepository),
        );
    _pageSettingsStateSubscription = _pageSettingsCubit.stream.listen(
      (_) => notifyListeners(),
    );
    _ownsDescriptionCubit = descriptionCubit == null;
    _descriptionCubit =
        descriptionCubit ??
        PrimarySourceDescriptionCubit(descriptionService: descriptionService);
    _descriptionStateSubscription = _descriptionCubit.stream.listen((_) {
      _syncSelectionFromDescriptionState();
      notifyListeners();
    });
    _ownsSelectionCubit = selectionCubit == null;
    _selectionCubit = selectionCubit ?? PrimarySourceSelectionCubit();
    _selectionStateSubscription = _selectionCubit.stream.listen(
      (_) => notifyListeners(),
    );
    _syncSelectionFromDescriptionState();

    if (selectedPage != null) {
      unawaited(loadImage(selectedPage!.image));
    }
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
      _imageCubit.setImageShown(false);
      scaleAndPositionRestored = false;
      notifyListeners();

      final pageSettings = await _pageSettingsCubit.loadSettingsForPage(
        source: primarySource,
        selectedPage: selectedPage,
      );
      if (!_canApplyImageRequest(requestToken)) {
        return;
      }
      _applyViewportSettings(pageSettings);

      if (!_canApplyImageRequest(requestToken)) {
        return;
      }
      notifyListeners();

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
    notifyListeners();
  }

  Future<void> changeSelectedPage(model.Page? newPage) async {
    _imageCubit.setImageShown(false);
    scaleAndPositionRestored = false;
    _sessionCubit.setSelectedPage(newPage);
    resetColorReplacement();
    notifyListeners();
    if (newPage != null) {
      await loadImage(newPage.image);
    } else {
      scaleAndPositionRestored = true;
      savedX = dx = 0;
      savedY = dy = 0;
      savedScale = scale = 0;
      _pageSettingsCubit.resetToDefaults();
      notifyListeners();
    }
  }

  void toggleNegative() {
    _pageSettingsCubit.toggleNegative();
    savePageSettings();
    notifyListeners();
  }

  void toggleMonochrome() {
    _pageSettingsCubit.toggleMonochrome();
    savePageSettings();
    notifyListeners();
  }

  void applyBrightnessContrast(double brightness, double contrast) {
    _pageSettingsCubit.applyBrightnessContrast(brightness, contrast);
    savePageSettings();
    notifyListeners();
  }

  void resetBrightnessContrast() {
    _pageSettingsCubit.resetBrightnessContrast();
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
    _pageSettingsCubit.toggleShowWordSeparators();
    savePageSettings();
    notifyListeners();
  }

  void toggleShowStrongNumbers() {
    _pageSettingsCubit.toggleShowStrongNumbers();
    savePageSettings();
    notifyListeners();
  }

  void toggleShowVerseNumbers() {
    _pageSettingsCubit.toggleShowVerseNumbers();
    savePageSettings();
    notifyListeners();
  }

  void setMenuOpen(bool value) {
    _sessionCubit.setMenuOpen(value);
    notifyListeners();
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
    savedX = dx = 0;
    savedY = dy = 0;
    savedScale = scale = 0;
    imageController.backToMinScale();
    resetColorReplacement();
    notifyListeners();
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
  }

  void showCommonInfo(BuildContext context) {
    _descriptionCubit.showCommonInfo(context);
  }

  bool navigateDescriptionSelection(
    BuildContext context, {
    required bool forward,
  }) {
    return _descriptionCubit.navigateSelection(
      context,
      forward: forward,
      source: primarySource,
      selectedPage: selectedPage,
    );
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
  }

  void _applyViewportSettings(PageSettingsState settings) {
    savedX = dx = settings.posX;
    savedY = dy = settings.posY;
    savedScale = scale = settings.scale;
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
    _descriptionStateSubscription?.cancel();
    _imageStateSubscription?.cancel();
    _pageSettingsStateSubscription?.cancel();
    _selectionStateSubscription?.cancel();
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
    if (_ownsSessionCubit) {
      unawaited(_sessionCubit.close());
    }
    super.dispose();
  }
}
