import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_selection_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/controllers/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/coordinators/primary_source_detail_coordinator.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';

class PrimarySourceViewModel {
  final PrimarySourceDetailCoordinator _coordinator;

  bool get isMobileWeb => _coordinator.isMobileWeb;
  Uint8List? get imageData => _coordinator.imageData;
  bool get isLoading => _coordinator.isLoading;
  bool get refreshError => _coordinator.refreshError;
  bool get imageShown => _coordinator.imageShown;
  Map<String, bool?> get localPageLoaded => _coordinator.localPageLoaded;
  bool get isNegative => _coordinator.isNegative;
  bool get isMonochrome => _coordinator.isMonochrome;
  double get brightness => _coordinator.brightness;
  double get contrast => _coordinator.contrast;
  bool get showWordSeparators => _coordinator.showWordSeparators;
  bool get showStrongNumbers => _coordinator.showStrongNumbers;
  bool get showVerseNumbers => _coordinator.showVerseNumbers;
  int get maxTextureSize => _coordinator.maxTextureSize;
  bool get pipetteMode => _coordinator.pipetteMode;
  bool get selectAreaMode => _coordinator.selectAreaMode;
  Rect? get selectedArea => _coordinator.selectedArea;
  Color get colorToReplace => _coordinator.colorToReplace;
  Color get newColor => _coordinator.newColor;
  double get tolerance => _coordinator.tolerance;
  bool get scaleAndPositionRestored => _coordinator.scaleAndPositionRestored;
  double get dx => _coordinator.dx;
  double get dy => _coordinator.dy;
  double get scale => _coordinator.scale;
  double get savedX => _coordinator.savedX;
  double get savedY => _coordinator.savedY;
  double get savedScale => _coordinator.savedScale;
  PrimarySource get primarySource => _coordinator.primarySource;
  model.Page? get selectedPage => _coordinator.selectedPage;
  String get imageName => _coordinator.imageName;
  bool get isMenuOpen => _coordinator.isMenuOpen;
  String get pageSettings => _coordinator.pageSettings;
  bool get showDescription => _coordinator.showDescription;
  String? get descriptionContent => _coordinator.descriptionContent;
  DescriptionKind get currentDescriptionType =>
      _coordinator.currentDescriptionType;
  int? get currentDescriptionNumber => _coordinator.currentDescriptionNumber;
  ImagePreviewController get imageController => _coordinator.imageController;
  ValueNotifier<ZoomStatus> get zoomStatusNotifier =>
      _coordinator.zoomStatusNotifier;

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
  }) : _coordinator = PrimarySourceDetailCoordinator(
         pagesRepository,
         primarySource: primarySource,
         imageCubit: imageCubit,
         pageSettingsCubit: pageSettingsCubit,
         selectionCubit: selectionCubit,
         descriptionCubit: descriptionCubit,
         viewportCubit: viewportCubit,
         sessionCubit: sessionCubit,
         descriptionService: descriptionService,
         pageSettingsOrchestrator: pageSettingsOrchestrator,
       );

  Future<void> loadImage(String page, {bool isReload = false}) =>
      _coordinator.loadImage(page, isReload: isReload);

  Future<void> changeSelectedPage(model.Page? newPage) =>
      _coordinator.changeSelectedPage(newPage);

  void toggleNegative() => _coordinator.toggleNegative();

  void toggleMonochrome() => _coordinator.toggleMonochrome();

  void applyBrightnessContrast(double brightness, double contrast) =>
      _coordinator.applyBrightnessContrast(brightness, contrast);

  void resetBrightnessContrast() => _coordinator.resetBrightnessContrast();

  void startSelectAreaMode(void Function(Rect?) onSelected) =>
      _coordinator.startSelectAreaMode(onSelected);

  void finishSelectAreaMode(Rect? selectRect) =>
      _coordinator.finishSelectAreaMode(selectRect);

  void startPipetteMode(
    void Function(Color?) onPicked,
    bool isColorToReplace,
  ) => _coordinator.startPipetteMode(onPicked, isColorToReplace);

  void finishPipetteMode(Color? color) => _coordinator.finishPipetteMode(color);

  void applyColorReplacement(
    Rect? selectedArea,
    Color colorToReplace,
    Color newColor,
    double tolerance,
  ) => _coordinator.applyColorReplacement(
    selectedArea,
    colorToReplace,
    newColor,
    tolerance,
  );

  void resetColorReplacement() => _coordinator.resetColorReplacement();

  void toggleShowWordSeparators() => _coordinator.toggleShowWordSeparators();

  void toggleShowStrongNumbers() => _coordinator.toggleShowStrongNumbers();

  void toggleShowVerseNumbers() => _coordinator.toggleShowVerseNumbers();

  void setMenuOpen(bool value) => _coordinator.setMenuOpen(value);

  void savePageSettings() => _coordinator.savePageSettings();

  void removePageSettings() => _coordinator.removePageSettings();

  void restorePositionAndScale() => _coordinator.restorePositionAndScale();

  void toggleDescription() => _coordinator.toggleDescription();

  void updateDescriptionContent(
    String content,
    DescriptionKind type,
    int? number,
  ) => _coordinator.updateDescriptionContent(content, type, number);

  void showCommonInfo(BuildContext context) =>
      _coordinator.showCommonInfo(context);

  bool navigateDescriptionSelection(
    BuildContext context, {
    required bool forward,
  }) => _coordinator.navigateDescriptionSelection(context, forward: forward);

  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() =>
      _coordinator.getGreekStrongPickerEntries();

  void showInfoForStrongNumber(int strongNumber, BuildContext context) =>
      _coordinator.showInfoForStrongNumber(strongNumber, context);

  void showInfoForWord(int wordIndex, BuildContext context) =>
      _coordinator.showInfoForWord(wordIndex, context);

  void showInfoForVerse(int verseIndex, BuildContext context) =>
      _coordinator.showInfoForVerse(verseIndex, context);

  void dispose() => _coordinator.dispose();
}
