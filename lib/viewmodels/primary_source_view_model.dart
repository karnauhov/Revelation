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
import 'package:revelation/utils/transliteration.dart';

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
  bool showWordSeparators = false;
  bool showStrongNumbers = false;

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
  bool _serviceSelectMode = false;
  void Function(Rect?)? _onAreaSelected;
  bool _isMenuOpen = false;
  Timer? _restoreDebounceTimer;
  Timer? _saveDebounceTimer;
  DBManager _dbManager = DBManager();
  Transliteration _translit = Transliteration();

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
      showWordSeparators = false;
      showStrongNumbers = false;
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
    _serviceSelectMode = false;
    _onAreaSelected = onSelected;
    notifyListeners();
  }

  void startGettingServiceRectangle(void Function(Rect?) onSelected) {
    _selectAreaMode = true;
    _serviceSelectMode = true;
    _onAreaSelected = onSelected;
    notifyListeners();
  }

  void finishSelectAreaMode(Rect? selectRect) {
    if (_selectAreaMode && _onAreaSelected != null) {
      _onAreaSelected!(selectRect);
    }
    if (!_serviceSelectMode) {
      selectedArea = selectRect;
    }
    _selectAreaMode = false;
    _serviceSelectMode = false;
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
        showWordSeparators: showWordSeparators,
        showStrongNumbers: showStrongNumbers,
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
    showWordSeparators = false;
    showStrongNumbers = false;
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
        final prevId = _getNeighborStrongNumber(
          _dbManager.greekWords[wordIndex].id,
          forward: false,
        );
        buffer.write(": [<](strong:G${prevId})**");
        buffer.write(_dbManager.greekWords[wordIndex].id);
        final nextId = _getNeighborStrongNumber(
          _dbManager.greekWords[wordIndex].id,
          forward: true,
        );
        buffer.write("**[>](strong:G${nextId})\n\r");
        buffer.write(AppLocalizations.of(context)!.strong_translit);
        buffer.write(": **");
        buffer.write(
          _translit
              .transliterate(word.toLowerCase().trim(), _dbManager.langDB)
              .toLowerCase(),
        );
        buffer.write("**\n\r");
        buffer.write(AppLocalizations.of(context)!.strong_part_of_speech);
        buffer.write(": **");
        buffer.write(
          _replaceKeys(context, _dbManager.greekWords[wordIndex].category),
        );
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

  void showInfoForWord(int wordIndex, BuildContext context) {
    if (selectedPage != null &&
        selectedPage!.words.isNotEmpty &&
        wordIndex >= 0 &&
        selectedPage!.words.length > wordIndex) {
      final word = selectedPage!.words[wordIndex];
      final buffer = StringBuffer();
      buffer.write("## ");
      buffer.write(_strikeThroughByIndexes(word.text, word.notExist));
      buffer.write("\n\r");
      if (word.sn != null) {
        buffer.write(AppLocalizations.of(context)!.strong_number);
        buffer.write(": **");
        buffer.write("[${word.sn!}](strong:G${word.sn!})");
        buffer.write("**\n\r");
      }
      if (_containsAnyLetter(word.text)) {
        buffer.write(AppLocalizations.of(context)!.strong_translit);
        buffer.write(": **");
        if (word.snTranslit && word.sn != null) {
          final wordIndex = _dbManager.greekWords.indexWhere(
            (w) => w.id == word.sn,
          );
          buffer.write(
            _translit
                .transliterate(
                  _dbManager.greekWords[wordIndex].word.toLowerCase().trim(),
                  _dbManager.langDB,
                )
                .toLowerCase(),
          );
        } else {
          buffer.write(
            _translit
                .transliterate(
                  word.text.toLowerCase().trim(),
                  _dbManager.langDB,
                )
                .toLowerCase(),
          );
        }
        buffer.write("**\n\r");
      }
      if (word.sn != null) {
        final descIndex = _dbManager.greekDescs.indexWhere(
          (desc) => desc.id == word.sn!,
        );
        if (descIndex != -1) {
          final desc = _dbManager.greekDescs[descIndex].desc.trim();
          if (desc != "") {
            buffer.write("\n\r>");
            buffer.write(_dbManager.greekDescs[descIndex].desc.trim());
          }
        }
      }
      updateDescriptionContent(buffer.toString());
    }
  }

  String _replaceKeys(BuildContext context, String input) {
    final regex = RegExp(r'@\w+');
    return input.replaceAllMapped(regex, (match) {
      final key = match.group(0)!;
      return locLinks(context, key);
    });
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
      showWordSeparators = pageSettings['wordSeparators'];
      showStrongNumbers = pageSettings['strongNumbers'];
    } else {
      savedX = dx = 0;
      savedY = dy = 0;
      savedScale = scale = 0;
      isNegative = false;
      isMonochrome = false;
      brightness = 0;
      contrast = 100;
      showWordSeparators = false;
      showStrongNumbers = false;
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

  int _getNeighborStrongNumber(int current, {bool forward = true}) {
    const int minVal = 1;
    const int maxVal = 5624;

    bool isForbidden(int x) => x == 2717 || (x >= 3203 && x <= 3302);

    if (current < minVal) {
      current = minVal;
    }
    if (current > maxVal) {
      current = maxVal;
    }

    int candidate = current;
    do {
      candidate = forward ? candidate + 1 : candidate - 1;
      if (candidate > maxVal) candidate = minVal;
      if (candidate < minVal) candidate = maxVal;
    } while (isForbidden(candidate));

    return candidate;
  }

  String _strikeThroughByIndexes(String word, Iterable<int> indices) {
    if (word.isEmpty) return word;
    final codePoints = word.runes.toList();
    final length = codePoints.length;
    final normalized = <int>{};
    for (final idx in indices) {
      final normalizedIdx = idx;
      if (normalizedIdx >= 0 && normalizedIdx < length) {
        normalized.add(normalizedIdx);
      }
    }
    if (normalized.isEmpty) return word;

    final buffer = StringBuffer();
    for (var i = 0; i < length; i++) {
      final ch = String.fromCharCode(codePoints[i]);
      if (normalized.contains(i)) {
        buffer.write('‎~~');
        buffer.write(ch);
        buffer.write('~~');
      } else {
        buffer.write(ch);
      }
    }
    return buffer.toString();
  }

  bool _containsAnyLetter(String text) {
    final regExp = RegExp(r'\p{L}', unicode: true);
    return regExp.hasMatch(text);
  }
}
