import 'dart:typed_data';

import 'package:revelation/infra/remote/supabase/server_manager.dart';

abstract class SupabaseStorageDownloadClient {
  Future<Uint8List?> downloadObject({
    required String bucket,
    required String path,
  });
}

class ServerManagerSupabaseStorageDownloadClient
    implements SupabaseStorageDownloadClient {
  ServerManagerSupabaseStorageDownloadClient({ServerManager? serverManager})
    : _serverManager = serverManager ?? ServerManager();

  final ServerManager _serverManager;

  @override
  Future<Uint8List?> downloadObject({
    required String bucket,
    required String path,
  }) {
    return _serverManager.downloadDB(bucket, path);
  }
}
