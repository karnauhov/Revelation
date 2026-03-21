import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';

void main() {
  test('value equality compares all fields', () {
    final a = TopicInfo(
      name: 'Topic',
      idIcon: 'topic-icon',
      description: 'Topic description',
      route: 'topic-route',
    );
    final b = TopicInfo(
      name: 'Topic',
      idIcon: 'topic-icon',
      description: 'Topic description',
      route: 'topic-route',
    );
    final c = TopicInfo(
      name: 'Topic',
      idIcon: 'topic-icon',
      description: 'Topic description',
      route: 'another-route',
    );

    expect(a, b);
    expect(a.hashCode, b.hashCode);
    expect(a, isNot(c));
  });
}
