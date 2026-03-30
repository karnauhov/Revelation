import 'dart:typed_data';
import 'package:revelation/infra/storage/markdown_image_local_store_native.dart'
    if (dart.library.html) 'package:revelation/infra/storage/markdown_image_local_store_web.dart'
    as impl;

class MarkdownImageLocalStoreEntry {
  const MarkdownImageLocalStoreEntry({
    required this.bytes,
    required this.filePath,
  });

  final Uint8List bytes;
  final String filePath;
}

abstract class MarkdownImageLocalStore {
  Future<MarkdownImageLocalStoreEntry?> read(String relativePath);

  Future<String?> write(String relativePath, Uint8List bytes);
}

MarkdownImageLocalStore createMarkdownImageLocalStore() {
  return impl.createMarkdownImageLocalStore();
}
