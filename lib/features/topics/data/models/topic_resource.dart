import 'dart:typed_data';

class TopicResource {
  const TopicResource({
    required this.fileName,
    required this.mimeType,
    required this.data,
  });

  final String fileName;
  final String mimeType;
  final Uint8List data;
}
