import 'package:flutter/foundation.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/topics/presentation/bloc/topic_markdown_image_state.dart';

class TopicContentState {
  TopicContentState({
    required this.route,
    required this.language,
    required this.name,
    required this.description,
    required this.markdown,
    required this.isLoading,
    required Map<String, TopicMarkdownImageState> markdownImages,
    required this.markdownImagesTotalCount,
    required this.markdownImagesCompletedCount,
    required this.markdownImagesFailedCount,
    this.failure,
  }) : markdownImages = Map<String, TopicMarkdownImageState>.unmodifiable(
         markdownImages,
       );

  factory TopicContentState.initial() {
    return TopicContentState(
      route: '',
      language: '',
      name: '',
      description: '',
      markdown: '',
      isLoading: true,
      markdownImages: const <String, TopicMarkdownImageState>{},
      markdownImagesTotalCount: 0,
      markdownImagesCompletedCount: 0,
      markdownImagesFailedCount: 0,
    );
  }

  final String route;
  final String language;
  final String name;
  final String description;
  final String markdown;
  final bool isLoading;
  final Map<String, TopicMarkdownImageState> markdownImages;
  final int markdownImagesTotalCount;
  final int markdownImagesCompletedCount;
  final int markdownImagesFailedCount;
  final AppFailure? failure;

  bool get hasMarkdownImagePreload => markdownImagesTotalCount > 0;

  bool get isMarkdownImagePreloadActive =>
      markdownImagesCompletedCount < markdownImagesTotalCount;

  double? get markdownImagePreloadProgress => markdownImagesTotalCount == 0
      ? null
      : markdownImagesCompletedCount / markdownImagesTotalCount;

  TopicContentState copyWith({
    String? route,
    String? language,
    String? name,
    String? description,
    String? markdown,
    bool? isLoading,
    Map<String, TopicMarkdownImageState>? markdownImages,
    int? markdownImagesTotalCount,
    int? markdownImagesCompletedCount,
    int? markdownImagesFailedCount,
    AppFailure? failure,
    bool clearFailure = false,
  }) {
    return TopicContentState(
      route: route ?? this.route,
      language: language ?? this.language,
      name: name ?? this.name,
      description: description ?? this.description,
      markdown: markdown ?? this.markdown,
      isLoading: isLoading ?? this.isLoading,
      markdownImages: markdownImages ?? this.markdownImages,
      markdownImagesTotalCount:
          markdownImagesTotalCount ?? this.markdownImagesTotalCount,
      markdownImagesCompletedCount:
          markdownImagesCompletedCount ?? this.markdownImagesCompletedCount,
      markdownImagesFailedCount:
          markdownImagesFailedCount ?? this.markdownImagesFailedCount,
      failure: clearFailure ? null : (failure ?? this.failure),
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is TopicContentState &&
            runtimeType == other.runtimeType &&
            route == other.route &&
            language == other.language &&
            name == other.name &&
            description == other.description &&
            markdown == other.markdown &&
            isLoading == other.isLoading &&
            mapEquals(markdownImages, other.markdownImages) &&
            markdownImagesTotalCount == other.markdownImagesTotalCount &&
            markdownImagesCompletedCount ==
                other.markdownImagesCompletedCount &&
            markdownImagesFailedCount == other.markdownImagesFailedCount &&
            failure == other.failure;
  }

  @override
  int get hashCode => Object.hash(
    route,
    language,
    name,
    description,
    markdown,
    isLoading,
    Object.hashAllUnordered(markdownImages.entries),
    markdownImagesTotalCount,
    markdownImagesCompletedCount,
    markdownImagesFailedCount,
    failure,
  );
}
