import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/models/zoom_status.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/controllers/image_preview_controller.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class PrimarySourceViewModel extends ChangeNotifier {
  final PrimarySource primarySource;
  model.Page? selectedPage;
  Uint8List? imageData;
  bool isLoading = false;
  bool refreshError = false;
  final Map<String, bool?> localPageLoaded = {};
  late ImagePreviewController imageController;
  final ValueNotifier<ZoomStatus> zoomStatusNotifier = ValueNotifier(
      const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false));

  late final bool _isWeb;
  late final bool _isMobileWeb;
  int _maxTextureSize = 4096;

  PrimarySourceViewModel({required this.primarySource}) {
    imageController = ImagePreviewController(primarySource.maxScale);
    imageController.transformationController.addListener(_updateZoomStatus);

    // Check for mobile web environment and fetch texture limits
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
      // Transform imageData for mobile browsers if necessary
      if (downloaded && imageData != null) {
        imageData = await _transformImageDataForMobileBrowser(imageData!);
      }
      localPageLoaded[page] = downloaded;
    } else {
      final localFilePath = await _getLocalFilePath(page);
      final file = File(localFilePath);
      if (!isReload && await file.exists()) {
        final bytes = await file.readAsBytes();
        imageData = bytes;
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

  Future<String> _getLocalFilePath(String page) async {
    final directory = await getApplicationDocumentsDirectory();
    return '${directory.path}/$page';
  }

  Future<bool> _downloadImage(String page, bool isReload) async {
    try {
      final divider = page.indexOf("/");
      final repository = page.substring(0, divider);
      final image = page.substring(divider + 1);
      final supabase = Supabase.instance.client;
      final Uint8List fileBytes =
          await supabase.storage.from(repository).download(image);

      refreshError = false;
      imageData = fileBytes;
      return true;
    } catch (e) {
      log.e('Image downloading error: $e');
      if (isReload && localPageLoaded[page] != null) {
        refreshError = true;
        notifyListeners();
        return localPageLoaded[page]!;
      } else {
        imageData = null;
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

  /// Resizes [data] if running in a mobile browser to fit within GPU texture limits,
  /// preserving aspect ratio.
  Future<Uint8List> _transformImageDataForMobileBrowser(Uint8List data) async {
    if (!(_isMobileWeb && _maxTextureSize > 0)) {
      return data;
    }

    // Decode the image
    final ui.Codec codec = await ui.instantiateImageCodec(data);
    final ui.FrameInfo frame = await codec.getNextFrame();
    final ui.Image image = frame.image;
    final int width = image.width;
    final int height = image.height;

    // Calculate scaling ratio
    final int maxDim = (_maxTextureSize * 0.5).floor();
    final double ratio = math.min(maxDim / width, maxDim / height);
    if (ratio >= 1.0) {
      return data;
    }

    final int targetWidth = (width * ratio).floor();
    final int targetHeight = (height * ratio).floor();
    log.w(
        "Resizing image from $width x $height to $targetWidth x $targetHeight (max: $maxDim)");

    // Draw to new canvas
    final ui.PictureRecorder recorder = ui.PictureRecorder();
    final ui.Canvas canvas = ui.Canvas(recorder);
    final ui.Paint paint = ui.Paint();
    canvas.drawImageRect(
      image,
      ui.Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble()),
      ui.Rect.fromLTWH(0, 0, targetWidth.toDouble(), targetHeight.toDouble()),
      paint,
    );
    final ui.Image resized =
        await recorder.endRecording().toImage(targetWidth, targetHeight);
    final ByteData? bytes =
        await resized.toByteData(format: ui.ImageByteFormat.png);

    if (bytes == null) {
      log.e("Failed to encode resized image");
      return data;
    }

    return bytes.buffer.asUint8List();
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
