import 'dart:typed_data';

import 'package:revelation/infra/storage/markdown_image_local_store.dart';

MarkdownImageLocalStore createMarkdownImageLocalStore() {
  return const _WebMarkdownImageLocalStore();
}

class _WebMarkdownImageLocalStore implements MarkdownImageLocalStore {
  const _WebMarkdownImageLocalStore();

  @override
  Future<MarkdownImageLocalStoreEntry?> read(String relativePath) async => null;

  @override
  Future<String?> write(String relativePath, Uint8List bytes) async => null;
}
