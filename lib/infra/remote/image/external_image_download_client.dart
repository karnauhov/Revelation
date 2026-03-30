import 'dart:typed_data';

import 'package:revelation/infra/remote/image/external_image_download_client_native.dart'
    if (dart.library.html) 'package:revelation/infra/remote/image/external_image_download_client_web.dart'
    as impl;

abstract class ExternalImageDownloadClient {
  Future<Uint8List?> download(Uri uri);
}

ExternalImageDownloadClient createExternalImageDownloadClient() {
  return impl.createExternalImageDownloadClient();
}
