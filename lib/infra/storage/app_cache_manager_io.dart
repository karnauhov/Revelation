import 'dart:io';

import 'package:path/path.dart' as p;
import 'package:revelation/core/cache/app_runtime_cache_registry.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';

Future<void> clearAppCache() async {
  final appFolder = await getAppFolder();
  final imagesDirectory = Directory(p.join(appFolder, 'images'));

  final appFolderPath = p.normalize(p.absolute(appFolder));
  final imagesPath = p.normalize(p.absolute(imagesDirectory.path));
  final isImagesFolder =
      p.basename(imagesPath) == 'images' &&
      p.isWithin(appFolderPath, imagesPath);
  if (!isImagesFolder) {
    throw StateError('Refusing to clear cache outside app folder: $imagesPath');
  }

  if (await imagesDirectory.exists()) {
    await imagesDirectory.delete(recursive: true);
  }
  AppRuntimeCacheRegistry.clearAll();
}
