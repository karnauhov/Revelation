import 'package:flutter/foundation.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';

class TopicsCatalogState {
  TopicsCatalogState({
    required this.language,
    required List<TopicInfo> topics,
    required Map<String, TopicResource?> iconByKey,
    required this.isLoading,
    this.failure,
  }) : topics = List<TopicInfo>.unmodifiable(topics),
       iconByKey = Map<String, TopicResource?>.unmodifiable(iconByKey);

  factory TopicsCatalogState.initial() {
    return TopicsCatalogState(
      language: '',
      topics: <TopicInfo>[],
      iconByKey: <String, TopicResource?>{},
      isLoading: true,
    );
  }

  final String language;
  final List<TopicInfo> topics;
  final Map<String, TopicResource?> iconByKey;
  final bool isLoading;
  final AppFailure? failure;

  TopicsCatalogState copyWith({
    String? language,
    List<TopicInfo>? topics,
    Map<String, TopicResource?>? iconByKey,
    bool? isLoading,
    AppFailure? failure,
    bool clearFailure = false,
  }) {
    return TopicsCatalogState(
      language: language ?? this.language,
      topics: topics ?? this.topics,
      iconByKey: iconByKey ?? this.iconByKey,
      isLoading: isLoading ?? this.isLoading,
      failure: clearFailure ? null : (failure ?? this.failure),
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is TopicsCatalogState &&
            runtimeType == other.runtimeType &&
            language == other.language &&
            listEquals(topics, other.topics) &&
            mapEquals(iconByKey, other.iconByKey) &&
            isLoading == other.isLoading &&
            failure == other.failure;
  }

  @override
  int get hashCode => Object.hash(
    language,
    Object.hashAll(topics),
    Object.hashAllUnordered(iconByKey.entries),
    isLoading,
    failure,
  );
}
