import 'dart:typed_data';

enum TopicMarkdownImageStatus { loading, ready, failure }

class TopicMarkdownImageState {
  const TopicMarkdownImageState._({
    required this.status,
    this.bytes,
    this.mimeType,
  });

  const TopicMarkdownImageState.loading()
    : this._(status: TopicMarkdownImageStatus.loading);

  const TopicMarkdownImageState.ready({
    required Uint8List bytes,
    String? mimeType,
  }) : this._(
         status: TopicMarkdownImageStatus.ready,
         bytes: bytes,
         mimeType: mimeType,
       );

  const TopicMarkdownImageState.failure()
    : this._(status: TopicMarkdownImageStatus.failure);

  final TopicMarkdownImageStatus status;
  final Uint8List? bytes;
  final String? mimeType;

  bool get isSvg => mimeType == 'image/svg+xml';

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is TopicMarkdownImageState &&
            runtimeType == other.runtimeType &&
            status == other.status &&
            identical(bytes, other.bytes) &&
            mimeType == other.mimeType;
  }

  @override
  int get hashCode => Object.hash(status, bytes, mimeType);
}
