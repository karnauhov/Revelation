import 'dart:io';
import 'dart:typed_data';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

Future<File> _cacheFile() async => File(
  p.join((await getApplicationCacheDirectory()).path, 'lxx-allusions-v1.bin'),
);

Future<Uint8List?> readCachedAllusionIndex() async {
  final file = await _cacheFile();
  return await file.exists() ? await file.readAsBytes() : null;
}

Future<void> writeCachedAllusionIndex(Uint8List bytes) async {
  final file = await _cacheFile();
  await file.parent.create(recursive: true);
  final temp = await file.parent.createTemp('allusions-');
  try {
    final draft = File(p.join(temp.path, 'index'));
    await draft.writeAsBytes(bytes, flush: true);
    await _replaceIndex(draft, file.path);
  } finally {
    await temp.delete(recursive: true);
  }
}

Future<void> _replaceIndex(File draft, String path) async {
  for (var delayMs = 20; ; delayMs *= 2) {
    try {
      await draft.rename(path);
      return;
    } on FileSystemException catch (error) {
      // An open handle or concurrent rename can temporarily block replacement.
      const windowsAccessDenied = 5;
      const windowsSharingViolation = 32;
      if (!Platform.isWindows ||
          delayMs > 320 ||
          !const {
            windowsAccessDenied,
            windowsSharingViolation,
          }.contains(error.osError?.errorCode)) {
        rethrow;
      }
      await Future<void>.delayed(Duration(milliseconds: delayMs));
    }
  }
}
