import 'package:flutter/foundation.dart';

class TopicResource {
  const TopicResource({
    required this.fileName,
    required this.mimeType,
    required this.data,
  });

  final String fileName;
  final String mimeType;
  final Uint8List data;

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is TopicResource &&
            runtimeType == other.runtimeType &&
            fileName == other.fileName &&
            mimeType == other.mimeType &&
            listEquals(data, other.data);
  }

  @override
  int get hashCode => Object.hash(fileName, mimeType, Object.hashAll(data));
}
