import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_state.dart';

void main() {
  test('constructor stores immutable copies of collections', () {
    final sourceTopics = <TopicInfo>[
      TopicInfo(
        name: 'Topic 1',
        idIcon: 'icon-1',
        description: 'Desc 1',
        route: 'route-1',
      ),
    ];
    final sourceIcons = <String, TopicResource?>{
      'icon-1': TopicResource(
        fileName: 'icon-1.svg',
        mimeType: 'image/svg+xml',
        data: Uint8List.fromList(const [1, 2, 3]),
      ),
    };

    final state = TopicsCatalogState(
      language: 'en',
      topics: sourceTopics,
      iconByKey: sourceIcons,
      isLoading: false,
    );

    sourceTopics.clear();
    sourceIcons.clear();

    expect(state.topics, hasLength(1));
    expect(state.iconByKey.keys, contains('icon-1'));
    expect(
      () => state.topics.add(
        TopicInfo(
          name: 'Topic 2',
          idIcon: 'icon-2',
          description: 'Desc 2',
          route: 'route-2',
        ),
      ),
      throwsUnsupportedError,
    );
    expect(() => state.iconByKey['new'] = null, throwsUnsupportedError);
  });

  test('copyWith keeps collections immutable', () {
    final initial = TopicsCatalogState.initial();
    final nextTopics = <TopicInfo>[
      TopicInfo(
        name: 'Topic X',
        idIcon: 'icon-x',
        description: 'Desc X',
        route: 'route-x',
      ),
    ];

    final updated = initial.copyWith(topics: nextTopics);
    nextTopics.add(
      TopicInfo(
        name: 'Topic Y',
        idIcon: 'icon-y',
        description: 'Desc Y',
        route: 'route-y',
      ),
    );

    expect(updated.topics, hasLength(1));
    expect(
      () => updated.topics.add(
        TopicInfo(
          name: 'Topic Z',
          idIcon: 'icon-z',
          description: 'Desc Z',
          route: 'route-z',
        ),
      ),
      throwsUnsupportedError,
    );
  });
}
