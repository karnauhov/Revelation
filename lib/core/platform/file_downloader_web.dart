import 'dart:js_interop';
import 'dart:typed_data';
import 'package:web/web.dart' as web;

Future<String?> saveDownloadableFile({
  required Uint8List bytes,
  required String fileName,
  required String mimeType,
}) async {
  final sanitizedName = _sanitizeFileName(fileName);
  final blob = web.Blob(
    <JSAny>[bytes.toJS].toJS,
    web.BlobPropertyBag(type: mimeType),
  );
  final url = web.URL.createObjectURL(blob);

  final anchor = web.HTMLAnchorElement()
    ..href = url
    ..download = sanitizedName
    ..style.display = 'none';

  web.document.body?.appendChild(anchor);
  anchor.click();
  anchor.remove();
  web.URL.revokeObjectURL(url);

  return sanitizedName;
}

String _sanitizeFileName(String fileName) {
  final trimmed = fileName.trim();
  final normalized = trimmed.isEmpty ? 'download.bin' : trimmed;
  return normalized.replaceAll(RegExp(r'[\\/:*?"<>|]'), '_');
}
