// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use

import 'dart:html' as html;
import 'dart:typed_data';

Future<String?> saveDownloadableFile({
  required Uint8List bytes,
  required String fileName,
  required String mimeType,
}) async {
  final sanitizedName = _sanitizeFileName(fileName);
  final blob = html.Blob(<dynamic>[bytes], mimeType);
  final url = html.Url.createObjectUrlFromBlob(blob);

  final anchor = html.AnchorElement(href: url)
    ..download = sanitizedName
    ..style.display = 'none';

  html.document.body?.append(anchor);
  anchor.click();
  anchor.remove();
  html.Url.revokeObjectUrl(url);

  return sanitizedName;
}

String _sanitizeFileName(String fileName) {
  final trimmed = fileName.trim();
  final normalized = trimmed.isEmpty ? 'download.bin' : trimmed;
  return normalized.replaceAll(RegExp(r'[\\/:*?"<>|]'), '_');
}
