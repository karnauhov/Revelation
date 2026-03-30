import 'dart:io';
import 'dart:typed_data';

import 'package:revelation/infra/remote/image/external_image_download_client.dart';

ExternalImageDownloadClient createExternalImageDownloadClient() {
  return _NativeExternalImageDownloadClient();
}

class _NativeExternalImageDownloadClient
    implements ExternalImageDownloadClient {
  @override
  Future<Uint8List?> download(Uri uri) async {
    final client = HttpClient();
    try {
      final request = await client.getUrl(uri);
      final response = await request.close();
      if (response.statusCode != HttpStatus.ok) {
        return null;
      }

      final bytesBuilder = BytesBuilder(copy: false);
      await for (final chunk in response) {
        bytesBuilder.add(chunk);
      }
      final bytes = bytesBuilder.takeBytes();
      return bytes.isEmpty ? null : bytes;
    } catch (_) {
      return null;
    } finally {
      client.close(force: true);
    }
  }
}
