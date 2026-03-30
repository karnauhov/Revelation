import 'dart:js_interop';
import 'dart:typed_data';

import 'package:revelation/infra/remote/image/external_image_download_client.dart';
import 'package:web/web.dart' as web;

ExternalImageDownloadClient createExternalImageDownloadClient() {
  return const _WebExternalImageDownloadClient();
}

class _WebExternalImageDownloadClient implements ExternalImageDownloadClient {
  const _WebExternalImageDownloadClient();

  @override
  Future<Uint8List?> download(Uri uri) async {
    try {
      final response = await web.window.fetch(uri.toString().toJS).toDart;
      if (!response.ok) {
        return null;
      }
      final bytes = await response.bytes().toDart;
      return bytes.toDart;
    } catch (_) {
      return null;
    }
  }
}
