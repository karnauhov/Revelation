import 'dart:typed_data';

class MarkdownImageLoadResult {
  const MarkdownImageLoadResult._({
    required this.isSuccess,
    this.bytes,
    this.mimeType,
  });

  const MarkdownImageLoadResult.success({
    required Uint8List bytes,
    String? mimeType,
  }) : this._(isSuccess: true, bytes: bytes, mimeType: mimeType);

  const MarkdownImageLoadResult.failure()
    : this._(isSuccess: false, bytes: null, mimeType: null);

  final bool isSuccess;
  final Uint8List? bytes;
  final String? mimeType;

  bool get isSvg => mimeType == 'image/svg+xml';
}
