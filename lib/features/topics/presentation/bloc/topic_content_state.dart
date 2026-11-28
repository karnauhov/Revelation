import 'package:revelation/core/errors/app_failure.dart';

class TopicContentState {
  TopicContentState({
    required this.route,
    required this.language,
    required this.name,
    required this.description,
    required this.markdown,
    required this.isLoading,
    this.isStudyExpanded = false,
    this.failure,
  });

  factory TopicContentState.initial() {
    return TopicContentState(
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
  final bool isStudyExpanded;
  static final _studyDivider = RegExp(
    r'^<!-- study:deeper -->\r?$',
    multiLine: true,
  );
  late final RegExpMatch? _division = _findDivision();

  RegExpMatch? _findDivision() {
    final matches = _studyDivider.allMatches(markdown).iterator;
    if (!matches.moveNext()) return null;
    final first = matches.current;
    if (matches.moveNext() ||
        markdown.substring(0, first.start).trim().isEmpty ||
        markdown.substring(first.end).trim().isEmpty)
      return null;
    return first;
  }

  String get openingMarkdown => _division == null
      ? markdown
      : markdown.substring(0, _division.start).trimRight();
  String? get deeperMarkdown =>
      _division == null ? null : markdown.substring(_division.end).trimLeft();
  String get fullReadingMarkdown =>
      _division == null ? markdown : '$openingMarkdown\n\n$deeperMarkdown';
  final bool isLoading;
  final AppFailure? failure;

  TopicContentState copyWith({
    String? route,
    String? language,
    String? name,
    String? description,
    String? markdown,
    bool? isLoading,
    bool? isStudyExpanded,
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
      isStudyExpanded: isStudyExpanded ?? this.isStudyExpanded,
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
            isStudyExpanded == other.isStudyExpanded &&
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
    isStudyExpanded,
    failure,
  );
}
