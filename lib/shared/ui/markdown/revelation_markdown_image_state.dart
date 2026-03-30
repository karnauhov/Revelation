import 'dart:typed_data';

enum RevelationMarkdownImageStatus { loading, ready, failure }

class RevelationMarkdownImageState {
  const RevelationMarkdownImageState._({
    required this.status,
    this.bytes,
    this.mimeType,
  });

  const RevelationMarkdownImageState.loading()
    : this._(status: RevelationMarkdownImageStatus.loading);

  const RevelationMarkdownImageState.ready({
    required Uint8List bytes,
    String? mimeType,
  }) : this._(
         status: RevelationMarkdownImageStatus.ready,
         bytes: bytes,
         mimeType: mimeType,
       );

  const RevelationMarkdownImageState.failure()
    : this._(status: RevelationMarkdownImageStatus.failure);

  final RevelationMarkdownImageStatus status;
  final Uint8List? bytes;
  final String? mimeType;

  bool get isSvg => mimeType == 'image/svg+xml';

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is RevelationMarkdownImageState &&
            runtimeType == other.runtimeType &&
            status == other.status &&
            identical(bytes, other.bytes) &&
            mimeType == other.mimeType;
  }

  @override
  int get hashCode => Object.hash(status, bytes, mimeType);
}
