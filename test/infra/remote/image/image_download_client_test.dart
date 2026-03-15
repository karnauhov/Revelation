import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/remote/image/image_download_client.dart';
import 'package:revelation/infra/remote/supabase/server_manager.dart';

void main() {
  test('ServerManagerImageDownloadClient delegates to server manager',
      () async {
    final bytes = Uint8List.fromList([1, 2, 3]);
    final serverManager = _FakeServerManager()..response = bytes;
    final client =
        ServerManagerImageDownloadClient(serverManager: serverManager);

    final result = await client.downloadImage(
      page: 'repo/page.png',
      isMobileWeb: true,
    );

    expect(result, bytes);
    expect(serverManager.lastPage, 'repo/page.png');
    expect(serverManager.lastIsMobileWeb, isTrue);
  });
}

class _FakeServerManager implements ServerManager {
  Uint8List? response;
  String? lastPage;
  bool? lastIsMobileWeb;

  @override
  Future<bool> init() async => true;

  @override
  Future<Uint8List?> downloadDB(String repository, String fileName) async {
    return null;
  }

  @override
  Future<Uint8List?> downloadImage(String page, bool isMobileWeb) async {
    lastPage = page;
    lastIsMobileWeb = isMobileWeb;
    return response;
  }

  @override
  Future<DateTime?> getLastUpdateFileFromServer(
    String repository,
    String filePath,
  ) async {
    return null;
  }
}
