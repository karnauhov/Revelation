import 'package:revelation/models/primary_source.dart';

class TopicRouteArgs {
  const TopicRouteArgs({required this.file, this.name, this.description});

  final String file;
  final String? name;
  final String? description;

  static TopicRouteArgs? tryParse(
    Object? extra,
    Map<String, String> queryParameters,
  ) {
    if (extra is TopicRouteArgs) {
      return extra;
    }

    String? file;
    String? name;
    String? description;

    file ??= queryParameters['file'];
    name ??= queryParameters['name'];
    description ??= queryParameters['description'];

    if (file == null || file.trim().isEmpty) {
      return null;
    }

    return TopicRouteArgs(file: file, name: name, description: description);
  }
}

class PrimarySourceRouteArgs {
  const PrimarySourceRouteArgs({
    required this.primarySource,
    this.pageName,
    this.wordIndex,
  });

  final PrimarySource primarySource;
  final String? pageName;
  final int? wordIndex;

  static PrimarySourceRouteArgs? tryParse(Object? extra) {
    if (extra is PrimarySourceRouteArgs) {
      return extra;
    }

    if (extra is PrimarySource) {
      return PrimarySourceRouteArgs(primarySource: extra);
    }
    return null;
  }
}
