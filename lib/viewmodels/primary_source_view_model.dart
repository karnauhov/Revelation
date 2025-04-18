import 'dart:io';
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

  PrimarySourceViewModel({required this.primarySource}) {
    imageController = ImagePreviewController(primarySource.maxScale);
    imageController.transformationController.addListener(_updateZoomStatus);

    if (primarySource.pages.isNotEmpty) {
      selectedPage = primarySource.pages.first;
      loadImage(selectedPage!.image);
    }
    checkLocalPages();
  }

  Future<void> checkLocalPages() async {
    if (isWeb()) {
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

    if (isWeb()) {
      final downloaded = await _downloadImage(page, false);
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
