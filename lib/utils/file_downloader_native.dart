import 'dart:io';
import 'dart:typed_data';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

Future<String?> saveDownloadableFile({
  required Uint8List bytes,
  required String fileName,
  required String mimeType,
}) async {
  final sanitizedName = _sanitizeFileName(fileName);

  Directory? targetDir;
  try {
    targetDir = await getDownloadsDirectory();
  } catch (_) {
    targetDir = null;
  }

  if (targetDir == null) {
    final docsDir = await getApplicationDocumentsDirectory();
    targetDir = Directory(p.join(docsDir.path, 'downloads'));
  }

  await targetDir.create(recursive: true);
  final targetFile = File(p.join(targetDir.path, sanitizedName));
  await targetFile.writeAsBytes(bytes, flush: true);
  return targetFile.path;
}

String _sanitizeFileName(String fileName) {
  final trimmed = fileName.trim();
  final normalized = trimmed.isEmpty ? 'download.bin' : trimmed;
  return normalized.replaceAll(RegExp(r'[\\/:*?"<>|]'), '_');
}
