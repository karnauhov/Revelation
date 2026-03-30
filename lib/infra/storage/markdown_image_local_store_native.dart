import 'dart:io';
import 'dart:typed_data';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/infra/storage/markdown_image_local_store.dart';

MarkdownImageLocalStore createMarkdownImageLocalStore() {
  return _NativeMarkdownImageLocalStore();
}

class _NativeMarkdownImageLocalStore implements MarkdownImageLocalStore {
  @override
  Future<MarkdownImageLocalStoreEntry?> read(String relativePath) async {
    final file = await _resolveFile(relativePath);
    if (!await file.exists()) {
      return null;
    }
    return MarkdownImageLocalStoreEntry(
      bytes: await file.readAsBytes(),
      filePath: file.path,
    );
  }

  @override
  Future<String?> write(String relativePath, Uint8List bytes) async {
    final file = await _resolveFile(relativePath);
    await file.parent.create(recursive: true);
    await file.writeAsBytes(bytes, flush: true);
    return file.path;
  }

  Future<File> _resolveFile(String relativePath) async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final folder = p.join(
      documentsDirectory.path,
      AppConstants.folder,
      'images',
    );
    return File(p.join(folder, relativePath));
  }
}
