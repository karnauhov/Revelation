import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/l10n/app_localizations.dart';

class PrimarySourceDetailCoordinator {
  late final PrimarySourceDescriptionCubit _descriptionCubit;
  late final bool _ownsDescriptionCubit;
  late final PrimarySourceImageCubit _imageCubit;
  late final bool _ownsImageCubit;
  late final PrimarySourcePageSettingsCubit _pageSettingsCubit;
  late final bool _ownsPageSettingsCubit;
  late final PrimarySourceViewportCubit _viewportCubit;
  late final bool _ownsViewportCubit;
  final PrimarySourceSessionCubit _sessionCubit;
  final bool _ownsSessionCubit;
  late final PrimarySourceDetailOrchestrationCubit _orchestrationCubit;
  late final bool _ownsOrchestrationCubit;

  ImagePreviewController get imageController =>
      _orchestrationCubit.imageController;
  ValueNotifier<ZoomStatus> get zoomStatusNotifier =>
      _orchestrationCubit.zoomStatusNotifier;

  late final bool _isWeb;
  late final bool _isMobileWeb;
  void Function(Color?)? _onPipettePicked;
  void Function(Rect?)? _onAreaSelected;

  bool get isMobileWeb => _isMobileWeb;
  Uint8List? get imageData => _imageCubit.state.imageData;
  bool get isLoading => _imageCubit.state.isLoading;
  bool get refreshError => _imageCubit.state.refreshError;
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
  String? get descriptionContent => _descriptionCubit.state.content;
  DescriptionKind get currentDescriptionType =>
      _descriptionCubit.state.currentType;
  int? get currentDescriptionNumber => _descriptionCubit.state.currentNumber;

  PrimarySourceDetailCoordinator(
    PagesRepository pagesRepository, {
    required PrimarySource primarySource,
    PrimarySourceImageCubit? imageCubit,
    PrimarySourcePageSettingsCubit? pageSettingsCubit,
    PrimarySourceDescriptionCubit? descriptionCubit,
    PrimarySourceViewportCubit? viewportCubit,
    PrimarySourceSessionCubit? sessionCubit,
    PrimarySourceDetailOrchestrationCubit? orchestrationCubit,
    DescriptionContentService? descriptionService,
    PrimarySourcePageSettingsOrchestrator? pageSettingsOrchestrator,
  }) : _sessionCubit =
           sessionCubit ?? PrimarySourceSessionCubit(source: primarySource),
       _ownsSessionCubit = sessionCubit == null {
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
    _ownsOrchestrationCubit = orchestrationCubit == null;
    _orchestrationCubit =
        orchestrationCubit ??
        PrimarySourceDetailOrchestrationCubit(
          source: primarySource,
          imageCubit: _imageCubit,
          pageSettingsCubit: _pageSettingsCubit,
          descriptionCubit: _descriptionCubit,
          sessionCubit: _sessionCubit,
          viewportCubit: _viewportCubit,
        );
  }

  Future<void> loadImage(String page, {bool isReload = false}) async {
    await _orchestrationCubit.loadImage(page, isReload: isReload);
  }

  Future<void> changeSelectedPage(model.Page? newPage) async {
    await _orchestrationCubit.changeSelectedPage(newPage);
  }

  void toggleNegative() {
    _orchestrationCubit.toggleNegative();
  }

  void toggleMonochrome() {
    _orchestrationCubit.toggleMonochrome();
  }

  void applyBrightnessContrast(double brightness, double contrast) {
    _orchestrationCubit.applyBrightnessContrast(brightness, contrast);
  }

  void resetBrightnessContrast() {
    _orchestrationCubit.resetBrightnessContrast();
  }

  void startSelectAreaMode(void Function(Rect?) onSelected) {
    _orchestrationCubit.startSelectAreaMode();
    _onAreaSelected = onSelected;
  }

  void finishSelectAreaMode(Rect? selectRect) {
    if (selectAreaMode && _onAreaSelected != null) {
      _onAreaSelected!(selectRect);
    }
    _orchestrationCubit.finishSelectAreaMode(selectRect);
    _onAreaSelected = null;
  }

  void startPipetteMode(void Function(Color?) onPicked, bool isColorToReplace) {
    _orchestrationCubit.startPipetteMode(isColorToReplace: isColorToReplace);
    _onPipettePicked = onPicked;
  }

  void finishPipetteMode(Color? color) {
    if (pipetteMode && _onPipettePicked != null) {
      _onPipettePicked!(color);
    }
    _orchestrationCubit.finishPipetteMode(color);
    _onPipettePicked = null;
  }

  void applyColorReplacement(
    Rect? selectedArea,
    Color colorToReplace,
    Color newColor,
    double tolerance,
  ) {
    _orchestrationCubit.applyColorReplacement(
      selectedArea: selectedArea,
      colorToReplace: colorToReplace,
      newColor: newColor,
      tolerance: tolerance,
    );
  }

  void resetColorReplacement() {
    _orchestrationCubit.resetColorReplacement();
  }

  void toggleShowWordSeparators() {
    _orchestrationCubit.toggleShowWordSeparators();
  }

  void toggleShowStrongNumbers() {
    _orchestrationCubit.toggleShowStrongNumbers();
  }

  void toggleShowVerseNumbers() {
    _orchestrationCubit.toggleShowVerseNumbers();
  }

  void setMenuOpen(bool value) {
    _orchestrationCubit.setMenuOpen(value);
  }

  void savePageSettings() {
    _orchestrationCubit.savePageSettings();
  }

  void removePageSettings() {
    _orchestrationCubit.removePageSettings();
  }

  void restorePositionAndScale() {
    _orchestrationCubit.restorePositionAndScale();
  }

  void updateDescriptionContent(
    String content,
    DescriptionKind type,
    int? number,
  ) {
    _orchestrationCubit.updateDescriptionContent(
      content: content,
      type: type,
      number: number,
    );
  }

  void showCommonInfo(AppLocalizations localizations) {
    _orchestrationCubit.showCommonInfo(localizations);
  }

  bool navigateDescriptionSelection(
    AppLocalizations localizations, {
    required bool forward,
  }) {
    final navigated = _orchestrationCubit.navigateDescriptionSelection(
      localizations,
      forward: forward,
    );
    return navigated;
  }

  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() {
    return _orchestrationCubit.getGreekStrongPickerEntries();
  }

  void showInfoForStrongNumber(
    int strongNumber,
    AppLocalizations localizations,
  ) {
    final shown = _orchestrationCubit.showInfoForStrongNumber(
      strongNumber: strongNumber,
      localizations: localizations,
    );
    if (!shown) {
      return;
    }
  }

  void showInfoForWord(int wordIndex, AppLocalizations localizations) {
    final shown = _orchestrationCubit.showInfoForWord(
      wordIndex: wordIndex,
      localizations: localizations,
    );
    if (!shown) {
      return;
    }
  }

  void showInfoForVerse(int verseIndex, AppLocalizations localizations) {
    final shown = _orchestrationCubit.showInfoForVerse(
      verseIndex: verseIndex,
      localizations: localizations,
    );
    if (!shown) {
      return;
    }
  }

  void dispose() {
    _onPipettePicked = null;
    _onAreaSelected = null;
    if (_ownsOrchestrationCubit) {
      unawaited(_orchestrationCubit.close());
    }
    if (_ownsDescriptionCubit) {
      unawaited(_descriptionCubit.close());
    }
    if (_ownsImageCubit) {
      unawaited(_imageCubit.close());
    }
    if (_ownsPageSettingsCubit) {
      unawaited(_pageSettingsCubit.close());
    }
    if (_ownsViewportCubit) {
      unawaited(_viewportCubit.close());
    }
    if (_ownsSessionCubit) {
      unawaited(_sessionCubit.close());
    }
  }
}
