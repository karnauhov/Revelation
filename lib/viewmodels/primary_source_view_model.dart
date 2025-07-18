import 'dart:io';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/managers/db_manager.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/pages_settings.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/models/zoom_status.dart';
import 'package:revelation/repositories/pages_repository.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/controllers/image_preview_controller.dart';
import 'package:revelation/managers/server_manager.dart';

class PrimarySourceViewModel extends ChangeNotifier {
  final PrimarySource primarySource;
  final PagesRepository _pagesRepository;
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
  bool showDescription = true;
  String? descriptionContent;

  final Map<String, bool?> localPageLoaded = {};
  late ImagePreviewController imageController;
  final ValueNotifier<ZoomStatus> zoomStatusNotifier = ValueNotifier(
    const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
  );

  PagesSettings? _pagesSettings;
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
  DBManager _dbManager = DBManager();

  bool get isMobileWeb => _isMobileWeb;
  int get maxTextureSize => _maxTextureSize;
  bool get pipetteMode => _pipetteMode;
  bool get selectAreaMode => _selectAreaMode;
  bool get isMenuOpen => _isMenuOpen;
  String get pageSettings => _pageSettings;

  PrimarySourceViewModel(this._pagesRepository, {required this.primarySource}) {
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
          log.w(
            "A mobile browser with max texture size of $_maxTextureSize was detected.",
          );
        } else {
          log.i(
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

  Future<void> loadImage(String page, {bool isReload = false}) async {
    try {
      isLoading = true;
      imageShown = false;
      scaleAndPositionRestored = false;
      await _getPagesSettings();
      notifyListeners();

      if (_isWeb) {
        final downloaded = await _downloadImage(page, false);
        localPageLoaded[page] = downloaded;
      } else {
        final localFilePath = await _getLocalFilePath(page);
        final file = File(localFilePath);
        if (!isReload && await file.exists()) {
          final bytes = await file.readAsBytes();
          imageData = bytes;
          imageName = "${primarySource.hashCode}_$page";
          isLoading = false;
          localPageLoaded[page] = true;
        } else {
          final downloaded = await _downloadImage(page, isReload);
          if (downloaded) {
            await _saveImage(file);
          }
          localPageLoaded[page] = downloaded;
        }
      }
    } catch (e) {
      log.e('Image loading error: $e');
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
      loadImage(newPage.image);
    } else {
      scaleAndPositionRestored = true;
      savedX = dx = 0;
      savedY = dy = 0;
      savedScale = scale = 0;
      isNegative = false;
      isMonochrome = false;
      brightness = 0;
      contrast = 100;
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

  void setMenuOpen(bool value) {
    _isMenuOpen = value;
    notifyListeners();
  }

  void savePageSettings() {
    if (_pagesSettings != null &&
        selectedPage != null &&
        scaleAndPositionRestored) {
      final pageId = "${primarySource.id}_${selectedPage!.name}";
      _pageSettings = PagesSettings.packData(
        posX: dx,
        posY: dy,
        scale: scale,
        isNegative: isNegative,
        isMonochrome: isMonochrome,
        brightness: brightness,
        contrast: contrast,
      );
      _pagesSettings!.pages[pageId] = _pageSettings;
      _pagesRepository.savePages(_pagesSettings!);
    } else {
      _pageSettings = "";
    }
  }

  void removePageSettings() {
    if (_pagesSettings != null && selectedPage != null) {
      final pageId = "${primarySource.id}_${selectedPage!.name}";
      _pageSettings = "";
      _pagesSettings!.pages[pageId] = _pageSettings;
      _pagesRepository.savePages(_pagesSettings!);
    } else {
      _pageSettings = "";
    }
    savedX = dx = 0;
    savedY = dy = 0;
    savedScale = scale = 0;
    isNegative = false;
    isMonochrome = false;
    brightness = 0;
    contrast = 100;
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
    showDescription = !showDescription;
    notifyListeners();
  }

  void updateDescriptionContent(String content) {
    descriptionContent = content;
    notifyListeners();
  }

  void showInfoForStrongNumber(int strongNumber, BuildContext context) {
    final wordIndex = _dbManager.greekWords.indexWhere(
      (word) => word.id == strongNumber,
    );
    if (wordIndex != -1) {
      final word = _dbManager.greekWords[wordIndex].word;
      if (word != "") {
        final buffer = StringBuffer();
        buffer.write("## ");
        buffer.write(word.trim());
        buffer.write("\n\r");
        buffer.write(AppLocalizations.of(context)!.strong_number);
        buffer.write(": **");
        buffer.write(_dbManager.greekWords[wordIndex].id);
        buffer.write("**\n\r");
        buffer.write(AppLocalizations.of(context)!.strong_translit);
        buffer.write(": **");
        buffer.write(_dbManager.greekWords[wordIndex].translit);
        buffer.write("**\n\r");
        final descIndex = _dbManager.greekDescs.indexWhere(
          (desc) => desc.id == strongNumber,
        );
        if (descIndex != -1) {
          final desc = _dbManager.greekDescs[descIndex].desc.trim();
          if (desc != "") {
            buffer.write("\n\r>");
            buffer.write(_dbManager.greekDescs[descIndex].desc.trim());
          }
        }
        updateDescriptionContent(buffer.toString());
      }
    }
  }

  Future<void> _getPagesSettings() async {
    _pagesSettings ??= await _pagesRepository.getPages();
    if (selectedPage != null) {
      final pageId = "${primarySource.id}_${selectedPage!.name}";
      if (_pagesSettings!.pages.containsKey(pageId)) {
        _pageSettings = _pagesSettings!.pages[pageId] ?? "";
      } else {
        _pageSettings = "";
      }
    } else {
      _pageSettings = "";
    }
    if (_pageSettings.isNotEmpty) {
      final pageSettings = PagesSettings.unpackData(_pageSettings);
      savedX = dx = pageSettings['position']['x'];
      savedY = dy = pageSettings['position']['y'];
      savedScale = scale = pageSettings['scale'];
      isNegative = pageSettings['isNegative'];
      isMonochrome = pageSettings['isMonochrome'];
      brightness = pageSettings['brightness'];
      contrast = pageSettings['contrast'];
    } else {
      savedX = dx = 0;
      savedY = dy = 0;
      savedScale = scale = 0;
      isNegative = false;
      isMonochrome = false;
      brightness = 0;
      contrast = 100;
    }
  }

  Future<void> _checkLocalPages() async {
    if (_isWeb) {
      for (var page in primarySource.pages) {
        localPageLoaded[page.image] = null;
      }
    } else {
      for (var page in primarySource.pages) {
        final localFilePath = await _getLocalFilePath(page.image);
        final exists = await File(localFilePath).exists();
        localPageLoaded[page.image] = exists;
      }
    }
    notifyListeners();
  }

  Future<String> _getLocalFilePath(String page) async {
    final appFolder = await getAppFolder();
    return '${appFolder}/$page';
  }

  Future<bool> _downloadImage(String page, bool isReload) async {
    final Uint8List? fileBytes = await ServerManager().downloadImage(
      page,
      _isMobileWeb,
    );
    if (fileBytes != null) {
      refreshError = false;
      imageData = fileBytes;
      imageName = "${primarySource.hashCode}_$page";
      return true;
    } else {
      if (isReload && localPageLoaded[page] != null) {
        refreshError = true;
        notifyListeners();
        return localPageLoaded[page]!;
      } else {
        imageData = null;
        imageName = "";
        return false;
      }
    }
  }

  Future<void> _saveImage(File file) async {
    try {
      if (imageData != null) {
        await file.create(recursive: true);
        await file.writeAsBytes(imageData!);
      }
    } catch (e) {
      log.e('Image save error: $e');
    }
  }

  void _updateTransformStatus() {
    if (imageData == null) {
      Future.microtask(() {
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
}
