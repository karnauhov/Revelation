import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/utils/image_preview_controller.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class PrimarySourceViewModel extends ChangeNotifier {
  final PrimarySource primarySource;
  model.Page? selectedPage;
  Uint8List? imageData;
  bool isLoading = false;
  final Map<String, bool> localPageLoaded = {};
  late ImagePreviewController imageController;

  PrimarySourceViewModel({required this.primarySource}) {
    imageController = ImagePreviewController(primarySource.maxScale);
    if (primarySource.pages.isNotEmpty) {
      selectedPage = primarySource.pages.first;
      loadImage(selectedPage!.image);
    }
    checkLocalPages();
  }

  Future<void> checkLocalPages() async {
    if (isWeb()) {
      for (var page in primarySource.pages) {
        localPageLoaded[page.image] = true;
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
      await _downloadImage(page);
      localPageLoaded[page] = true;
    } else {
      final localFilePath = await _getLocalFilePath(page);
      final file = File(localFilePath);
      if (!isReload && await file.exists()) {
        final bytes = await file.readAsBytes();
        imageData = bytes;
        isLoading = false;
        localPageLoaded[page] = true;
      } else {
        await _downloadImage(page);
        await _saveImage(file);
        localPageLoaded[page] = true;
      }
    }
    isLoading = false;
    notifyListeners();
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

  Future<void> _downloadImage(String page) async {
    try {
      final divider = page.indexOf("/");
      final repository = page.substring(0, divider);
      final image = page.substring(divider + 1);
      final supabase = Supabase.instance.client;
      final Uint8List fileBytes =
          await supabase.storage.from(repository).download(image);

      imageData = fileBytes;
    } catch (e) {
      log.e('Image downloading error: $e');
      imageData = null;
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
}
