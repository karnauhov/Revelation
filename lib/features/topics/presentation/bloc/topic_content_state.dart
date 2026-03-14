import 'package:revelation/core/errors/app_failure.dart';

class TopicContentState {
  const TopicContentState({
    required this.route,
    required this.language,
    required this.name,
    required this.description,
    required this.markdown,
    required this.isLoading,
    this.failure,
  });

  factory TopicContentState.initial() {
    return const TopicContentState(
      route: '',
      language: '',
      name: '',
      description: '',
      markdown: '',
      isLoading: true,
    );
  }

  final String route;
  final String language;
  final String name;
  final String description;
  final String markdown;
  final bool isLoading;
  final AppFailure? failure;

  TopicContentState copyWith({
    String? route,
    String? language,
    String? name,
    String? description,
    String? markdown,
    bool? isLoading,
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
    failure,
  );
}
