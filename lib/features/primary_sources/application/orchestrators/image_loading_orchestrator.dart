import 'dart:io';
import 'dart:typed_data';

import 'package:revelation/infra/remote/image/image_download_client.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/infra/storage/file_sync_utils.dart';

enum ImageContentAction { replace, clear, keep }

class PageImageLoadResult {
  const PageImageLoadResult({
    required this.contentAction,
    required this.imageData,
    required this.imageName,
    required this.pageLoaded,
    required this.refreshError,
  });

  final ImageContentAction contentAction;
  final Uint8List? imageData;
  final String imageName;
  final bool pageLoaded;
  final bool refreshError;
}

class PrimarySourceImageLoadingOrchestrator {
  PrimarySourceImageLoadingOrchestrator({
    ImageDownloadClient? imageDownloadClient,
  }) : _imageDownloadClient =
           imageDownloadClient ?? ServerManagerImageDownloadClient();

  final ImageDownloadClient _imageDownloadClient;

  Future<Map<String, bool?>> detectLocalPageAvailability({
    required List<model.Page> pages,
    required bool isWeb,
  }) async {
    final result = <String, bool?>{};
    if (isWeb) {
      for (final page in pages) {
        result[page.image] = null;
      }
      return result;
    }

    for (final page in pages) {
      final localFilePath = await _getLocalFilePath(page.image);
      final exists = await File(localFilePath).exists();
      result[page.image] = exists;
    }
    return result;
  }

  Future<PageImageLoadResult> loadPageImage({
    required String page,
    required int sourceHashCode,
    required bool isWeb,
    required bool isMobileWeb,
    required bool isReload,
    bool? previousPageLoaded,
  }) async {
    if (isWeb) {
      return _downloadFromServer(
        page: page,
        sourceHashCode: sourceHashCode,
        isMobileWeb: isMobileWeb,
        isReload: isReload,
        previousPageLoaded: previousPageLoaded,
      );
    }

    final localFilePath = await _getLocalFilePath(page);
    final file = File(localFilePath);
    if (!isReload && await file.exists()) {
      final bytes = await file.readAsBytes();
      return PageImageLoadResult(
        contentAction: ImageContentAction.replace,
        imageData: bytes,
        imageName: _buildImageName(sourceHashCode, page),
        pageLoaded: true,
        refreshError: false,
      );
    }

    return _downloadFromServer(
      page: page,
      sourceHashCode: sourceHashCode,
      isMobileWeb: isMobileWeb,
      isReload: isReload,
      previousPageLoaded: previousPageLoaded,
      localFileToPersist: file,
    );
  }

  Future<PageImageLoadResult> _downloadFromServer({
    required String page,
    required int sourceHashCode,
    required bool isMobileWeb,
    required bool isReload,
    required bool? previousPageLoaded,
    File? localFileToPersist,
  }) async {
    final fileBytes = await _imageDownloadClient.downloadImage(
      page: page,
      isMobileWeb: isMobileWeb,
    );
    if (fileBytes != null) {
      if (localFileToPersist != null) {
        await _saveImage(localFileToPersist, fileBytes);
      }
      return PageImageLoadResult(
        contentAction: ImageContentAction.replace,
        imageData: fileBytes,
        imageName: _buildImageName(sourceHashCode, page),
        pageLoaded: true,
        refreshError: false,
      );
    }

    if (isReload && previousPageLoaded != null) {
      return PageImageLoadResult(
        contentAction: ImageContentAction.keep,
        imageData: null,
        imageName: '',
        pageLoaded: previousPageLoaded,
        refreshError: true,
      );
    }

    return const PageImageLoadResult(
      contentAction: ImageContentAction.clear,
      imageData: null,
      imageName: '',
      pageLoaded: false,
      refreshError: false,
    );
  }

  Future<String> _getLocalFilePath(String page) async {
    final appFolder = await getAppFolder();
    return '$appFolder/$page';
  }

  Future<void> _saveImage(File file, Uint8List imageBytes) async {
    try {
      await file.create(recursive: true);
      await file.writeAsBytes(imageBytes);
    } catch (_) {}
  }

  String _buildImageName(int sourceHashCode, String page) {
    return '${sourceHashCode}_$page';
  }
}
