import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/infra/remote/image/image_download_client.dart';
import 'package:revelation/shared/models/page.dart' as model;

void main() {
  test('detectLocalPageAvailability returns nulls on web', () async {
    final client = _FakeImageDownloadClient();
    final orchestrator = PrimarySourceImageLoadingOrchestrator(
      imageDownloadClient: client,
    );

    final availability = await orchestrator.detectLocalPageAvailability(
      pages: [
        model.Page(name: 'p1', content: '', image: 'p1.png'),
        model.Page(name: 'p2', content: '', image: 'p2.png'),
      ],
      isWeb: true,
    );

    expect(availability['p1.png'], isNull);
    expect(availability['p2.png'], isNull);
  });

  test('loadPageImage replaces content when download succeeds', () async {
    final bytes = Uint8List.fromList([1, 2, 3]);
    final client = _FakeImageDownloadClient()..response = bytes;
    final orchestrator = PrimarySourceImageLoadingOrchestrator(
      imageDownloadClient: client,
    );

    final result = await orchestrator.loadPageImage(
      page: 'p1.png',
      sourceHashCode: 7,
      isWeb: true,
      isMobileWeb: false,
      isReload: false,
    );

    expect(result.contentAction, ImageContentAction.replace);
    expect(result.imageData, bytes);
    expect(result.imageName, '7_p1.png');
    expect(result.pageLoaded, isTrue);
    expect(result.refreshError, isFalse);
  });

  test('loadPageImage keeps content on reload failure', () async {
    final client = _FakeImageDownloadClient()..response = null;
    final orchestrator = PrimarySourceImageLoadingOrchestrator(
      imageDownloadClient: client,
    );

    final result = await orchestrator.loadPageImage(
      page: 'p1.png',
      sourceHashCode: 7,
      isWeb: true,
      isMobileWeb: false,
      isReload: true,
      previousPageLoaded: true,
    );

    expect(result.contentAction, ImageContentAction.keep);
    expect(result.pageLoaded, isTrue);
    expect(result.refreshError, isTrue);
  });

  test('loadPageImage clears content on initial failure', () async {
    final client = _FakeImageDownloadClient()..response = null;
    final orchestrator = PrimarySourceImageLoadingOrchestrator(
      imageDownloadClient: client,
    );

    final result = await orchestrator.loadPageImage(
      page: 'p1.png',
      sourceHashCode: 7,
      isWeb: true,
      isMobileWeb: false,
      isReload: false,
    );

    expect(result.contentAction, ImageContentAction.clear);
    expect(result.pageLoaded, isFalse);
    expect(result.refreshError, isFalse);
  });
}

class _FakeImageDownloadClient implements ImageDownloadClient {
  Uint8List? response;

  @override
  Future<Uint8List?> downloadImage({
    required String page,
    required bool isMobileWeb,
  }) async {
    return response;
  }
}
