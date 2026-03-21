import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';

void main() {
  test('value equality uses deep byte comparison', () {
    final a = TopicResource(
      fileName: 'icon.svg',
      mimeType: 'image/svg+xml',
      data: Uint8List.fromList(const <int>[1, 2, 3]),
    );
    final b = TopicResource(
      fileName: 'icon.svg',
      mimeType: 'image/svg+xml',
      data: Uint8List.fromList(const <int>[1, 2, 3]),
    );
    final c = TopicResource(
      fileName: 'icon.svg',
      mimeType: 'image/svg+xml',
      data: Uint8List.fromList(const <int>[1, 3, 2]),
    );

    expect(a, b);
    expect(a.hashCode, b.hashCode);
    expect(a, isNot(c));
  });
}
