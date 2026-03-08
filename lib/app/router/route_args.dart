import 'package:revelation/models/primary_source.dart';

class TopicRouteArgs {
  const TopicRouteArgs({required this.file, this.name, this.description});

  final String file;
  final String? name;
  final String? description;

  Map<String, dynamic> toLegacyExtra() {
    return <String, dynamic>{
      'file': file,
      if (name != null) 'name': name,
      if (description != null) 'description': description,
    };
  }

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

    if (extra is Map<String, dynamic>) {
      file = _readString(extra['file']) ?? _readString(extra['route']);
      name = _readString(extra['name']);
      description = _readString(extra['description']);
    }

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

  Map<String, dynamic> toLegacyExtra() {
    return <String, dynamic>{
      'primarySource': primarySource,
      if (pageName != null) 'pageName': pageName,
      if (wordIndex != null) 'wordIndex': wordIndex,
    };
  }

  static PrimarySourceRouteArgs? tryParse(Object? extra) {
    if (extra is PrimarySourceRouteArgs) {
      return extra;
    }

    if (extra is PrimarySource) {
      return PrimarySourceRouteArgs(primarySource: extra);
    }

    if (extra is! Map<String, dynamic>) {
      return null;
    }

    final source = extra['primarySource'];
    if (source is! PrimarySource) {
      return null;
    }

    final rawWordIndex = extra['wordIndex'];
    int? wordIndex;
    if (rawWordIndex is int) {
      wordIndex = rawWordIndex;
    } else if (rawWordIndex is String) {
      wordIndex = int.tryParse(rawWordIndex);
    }

    return PrimarySourceRouteArgs(
      primarySource: source,
      pageName: _readString(extra['pageName']),
      wordIndex: wordIndex,
    );
  }
}

String? _readString(Object? value) {
  if (value is! String) {
    return null;
  }
  return value.trim().isEmpty ? null : value;
}
