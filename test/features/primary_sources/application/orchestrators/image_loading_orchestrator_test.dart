import 'dart:io';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/infra/remote/image/image_download_client.dart';
import 'package:revelation/shared/models/page.dart' as model;

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const pathProviderChannel = MethodChannel('plugins.flutter.io/path_provider');

  late Directory tempDir;

  setUp(() async {
    tempDir = await Directory.systemTemp.createTemp('image_orch_test_');
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(pathProviderChannel, (call) async {
          if (call.method == 'getApplicationDocumentsDirectory') {
            return tempDir.path;
          }
          return null;
        });
  });

  tearDown(() async {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(pathProviderChannel, null);
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

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

  test(
    'detectLocalPageAvailability checks local files on native targets',
    () async {
      final client = _FakeImageDownloadClient();
      final orchestrator = PrimarySourceImageLoadingOrchestrator(
        imageDownloadClient: client,
      );

      final existing = File('${tempDir.path}/revelation/p1.png');
      await existing.create(recursive: true);
      await existing.writeAsBytes(<int>[1]);

      final availability = await orchestrator.detectLocalPageAvailability(
        pages: [
          model.Page(name: 'p1', content: '', image: 'p1.png'),
          model.Page(name: 'p2', content: '', image: 'p2.png'),
        ],
        isWeb: false,
      );

      expect(availability['p1.png'], isTrue);
      expect(availability['p2.png'], isFalse);
    },
  );

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

  test(
    'loadPageImage uses local file when available and not reloading',
    () async {
      final localBytes = Uint8List.fromList(<int>[7, 8, 9]);
      final client = _FakeImageDownloadClient()..response = Uint8List(0);
      final orchestrator = PrimarySourceImageLoadingOrchestrator(
        imageDownloadClient: client,
      );
      final localFile = File('${tempDir.path}/revelation/p1.png');
      await localFile.create(recursive: true);
      await localFile.writeAsBytes(localBytes);

      final result = await orchestrator.loadPageImage(
        page: 'p1.png',
        sourceHashCode: 99,
        isWeb: false,
        isMobileWeb: false,
        isReload: false,
      );

      expect(result.contentAction, ImageContentAction.replace);
      expect(result.imageData, localBytes);
      expect(result.imageName, '99_p1.png');
      expect(result.pageLoaded, isTrue);
      expect(client.downloadCallCount, 0);
    },
  );

  test('loadPageImage downloads and persists file on native reload', () async {
    final bytes = Uint8List.fromList(<int>[3, 4, 5]);
    final client = _FakeImageDownloadClient()..response = bytes;
    final orchestrator = PrimarySourceImageLoadingOrchestrator(
      imageDownloadClient: client,
    );

    final result = await orchestrator.loadPageImage(
      page: 'p2.png',
      sourceHashCode: 11,
      isWeb: false,
      isMobileWeb: true,
      isReload: true,
      previousPageLoaded: false,
    );

    final savedFile = File('${tempDir.path}/revelation/p2.png');
    expect(result.contentAction, ImageContentAction.replace);
    expect(result.imageData, bytes);
    expect(result.pageLoaded, isTrue);
    expect(await savedFile.exists(), isTrue);
    expect(await savedFile.readAsBytes(), bytes);
    expect(client.lastIsMobileWeb, isTrue);
    expect(client.downloadCallCount, 1);
  });
}

class _FakeImageDownloadClient implements ImageDownloadClient {
  Uint8List? response;
  int downloadCallCount = 0;
  bool? lastIsMobileWeb;

  @override
  Future<Uint8List?> downloadImage({
    required String page,
    required bool isMobileWeb,
  }) async {
    downloadCallCount++;
    lastIsMobileWeb = isMobileWeb;
    return response;
  }
}
