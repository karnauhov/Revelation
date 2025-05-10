import 'dart:io';
import 'dart:ui';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/models/zoom_status.dart';
import 'package:revelation/utils/app_constants.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/controllers/image_preview_controller.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class PrimarySourceViewModel extends ChangeNotifier {
  final PrimarySource primarySource;
  model.Page? selectedPage;
  Uint8List? imageData;
  String imageName = "";
  bool isLoading = false;
  bool refreshError = false;
  bool isNegative = false;
  bool isMonochrome = false;
  double brightness = 0;
  double contrast = 100;
  Rect? selectedArea;
  Color colorToReplace = const Color(0xFFFFFFFF);
  Color newColor = const Color(0xFFFFFFFF);
  double tolerance = 0;

  final Map<String, bool?> localPageLoaded = {};
  late ImagePreviewController imageController;
  final ValueNotifier<ZoomStatus> zoomStatusNotifier = ValueNotifier(
      const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false));

  late final bool _isWeb;
  late final bool _isMobileWeb;
  int _maxTextureSize = 4096;
  bool _pipetteMode = false;
  void Function(Color?)? _onPipettePicked;
  bool _isColorToReplace = true;
  bool _selectAreaMode = false;
  void Function(Rect?)? _onAreaSelected;

  bool get isMobileWeb => _isMobileWeb;
  int get maxTextureSize => _maxTextureSize;
  bool get pipetteMode => _pipetteMode;
  bool get selectAreaMode => _selectAreaMode;

  PrimarySourceViewModel({required this.primarySource}) {
    imageController = ImagePreviewController(primarySource.maxScale);
    imageController.transformationController.addListener(_updateZoomStatus);

    _isWeb = isWeb();
    _isMobileWeb = _isWeb && isMobileBrowser();

    if (_isWeb) {
      fetchMaxTextureSize().then((size) {
        _maxTextureSize = size > 0 ? size : 4096;
        if (_isMobileWeb) {
          log.w(
              "A mobile browser with max texture size of $_maxTextureSize was detected.");
        } else {
          log.i(
              "A browser with max texture size of $_maxTextureSize was detected.");
        }
      });
    } else {
      _maxTextureSize = 0;
    }

    if (primarySource.pages.isNotEmpty && primarySource.permissionsReceived) {
      selectedPage = primarySource.pages.first;
      loadImage(selectedPage!.image);
    }
    checkLocalPages();
  }

  Future<void> checkLocalPages() async {
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

  Future<void> loadImage(String page, {bool isReload = false}) async {
    isLoading = true;
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
    isLoading = false;
    notifyListeners();

    _updateZoomStatus();
  }

  void changeSelectedPage(model.Page? newPage) {
    selectedPage = newPage;
    notifyListeners();
    if (newPage != null) {
      loadImage(newPage.image);
    }
  }

  void toggleNegative() {
    isNegative = !isNegative;
    notifyListeners();
  }

  void toggleMonochrome() {
    isMonochrome = !isMonochrome;
    notifyListeners();
  }

  void applyBrightnessContrast(double brightness, double contrast) {
    this.brightness = brightness;
    this.contrast = contrast;
    notifyListeners();
  }

  void resetBrightnessContrast() {
    brightness = 0;
    contrast = 100;
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

  void applyColorReplacement(Rect? selectedArea, Color colorToReplace,
      Color newColor, double tolerance) {
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

  Future<String> _getLocalFilePath(String page) async {
    final directory = await getApplicationDocumentsDirectory();
    return '${directory.path}/$page';
  }

  Future<bool> _downloadImage(String page, bool isReload) async {
    try {
      final divider = page.indexOf("/");
      final repository = page.substring(0, divider);
      final image = page.substring(divider + 1);

      // Fix image url for mobile browser
      String modifiedImage;
      if (_isMobileWeb) {
        final lastDotIndex = image.lastIndexOf('.');
        if (lastDotIndex != -1) {
          modifiedImage =
              '${image.substring(0, lastDotIndex)}${AppConstants.mobileBrowserSuffix}${image.substring(lastDotIndex)}';
        } else {
          modifiedImage = '$image${AppConstants.mobileBrowserSuffix}';
        }
      } else {
        modifiedImage = image;
      }
      final supabase = Supabase.instance.client;
      final Uint8List fileBytes =
          await supabase.storage.from(repository).download(modifiedImage);

      refreshError = false;
      imageData = fileBytes;
      imageName = "${primarySource.hashCode}_$page";
      return true;
    } catch (e) {
      log.e('Image downloading error: $e');
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

  void _updateZoomStatus() {
    if (imageData == null) {
      Future.microtask(() {
        zoomStatusNotifier.value = const ZoomStatus(
            canZoomIn: false, canZoomOut: false, canReset: false);
      });
    } else {
      final currentScale =
          imageController.transformationController.value.getMaxScaleOnAxis();
      Future.microtask(() {
        zoomStatusNotifier.value = ZoomStatus(
          canZoomIn: currentScale < imageController.maxScale,
          canZoomOut: currentScale > imageController.minScale,
          canReset: currentScale != imageController.minScale,
        );
      });
    }
  }
}
