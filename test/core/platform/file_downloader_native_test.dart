import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/core/platform/file_downloader_native.dart';

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform({
    this.downloadsPath,
    this.documentsPath,
    this.temporaryPath,
    this.throwDownloads = false,
  }) : super();

  String? downloadsPath;
  String? documentsPath;
  String? temporaryPath;
  bool throwDownloads;

  @override
  Future<String?> getDownloadsPath() async {
    if (throwDownloads) {
      throw Exception('downloads unavailable');
    }
    return downloadsPath;
  }

  @override
  Future<String?> getApplicationDocumentsPath() async => documentsPath;

  @override
  Future<String?> getTemporaryPath() async => temporaryPath;

  @override
  Future<String?> getApplicationSupportPath() async => null;

  @override
  Future<String?> getLibraryPath() async => null;

  @override
  Future<String?> getApplicationCachePath() async => null;

  @override
  Future<String?> getExternalStoragePath() async => null;

  @override
  Future<List<String>?> getExternalCachePaths() async => null;

  @override
  Future<List<String>?> getExternalStoragePaths({
    StorageDirectory? type,
  }) async => null;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late PathProviderPlatform originalPlatform;

  setUp(() {
    originalPlatform = PathProviderPlatform.instance;
  });

  tearDown(() {
    PathProviderPlatform.instance = originalPlatform;
  });

  test('saves file to downloads directory when available', () async {
    final downloadsDir = await Directory.systemTemp.createTemp('downloads-');
    final docsDir = await Directory.systemTemp.createTemp('docs-');
    addTearDown(() async {
      await downloadsDir.delete(recursive: true);
      await docsDir.delete(recursive: true);
    });

    final fakePlatform = _FakePathProviderPlatform(
      downloadsPath: downloadsDir.path,
      documentsPath: docsDir.path,
      temporaryPath: docsDir.path,
    );
    PathProviderPlatform.instance = fakePlatform;

    final bytes = Uint8List.fromList([1, 2, 3]);
    final path = await saveDownloadableFile(
      bytes: bytes,
      fileName: ' report:2024/03?.txt ',
      mimeType: 'text/plain',
    );

    expect(path, isNotNull);
    expect(path, startsWith(downloadsDir.path));
    expect(p.basename(path!), 'report_2024_03_.txt');
    expect(await File(path).readAsBytes(), bytes);
  });

  test(
    'falls back to documents/downloads when downloads unavailable',
    () async {
      final docsDir = await Directory.systemTemp.createTemp('docs-');
      addTearDown(() async {
        await docsDir.delete(recursive: true);
      });

      final fakePlatform = _FakePathProviderPlatform(
        downloadsPath: null,
        documentsPath: docsDir.path,
        temporaryPath: docsDir.path,
        throwDownloads: true,
      );
      PathProviderPlatform.instance = fakePlatform;

      final bytes = Uint8List.fromList([9, 8, 7]);
      final path = await saveDownloadableFile(
        bytes: bytes,
        fileName: '',
        mimeType: 'application/octet-stream',
      );

      final expectedDir = p.join(docsDir.path, 'downloads');
      expect(path, isNotNull);
      expect(path, startsWith(expectedDir));
      expect(p.basename(path!), 'download.bin');
      expect(await File(path).readAsBytes(), bytes);
    },
  );
}
