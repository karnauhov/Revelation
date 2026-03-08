import 'dart:typed_data';

import 'package:revelation/infra/remote/supabase/server_manager.dart';

abstract class ImageDownloadClient {
  Future<Uint8List?> downloadImage({
    required String page,
    required bool isMobileWeb,
  });
}

class ServerManagerImageDownloadClient implements ImageDownloadClient {
  ServerManagerImageDownloadClient({ServerManager? serverManager})
    : _serverManager = serverManager ?? ServerManager();

  final ServerManager _serverManager;

  @override
  Future<Uint8List?> downloadImage({
    required String page,
    required bool isMobileWeb,
  }) {
    return _serverManager.downloadImage(page, isMobileWeb);
  }
}

