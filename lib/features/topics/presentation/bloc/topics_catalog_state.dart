import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';

class TopicsCatalogState {
  const TopicsCatalogState({
    required this.language,
    required this.topics,
    required this.iconByKey,
    required this.isLoading,
    this.failure,
  });

  factory TopicsCatalogState.initial() {
    return const TopicsCatalogState(
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
}
