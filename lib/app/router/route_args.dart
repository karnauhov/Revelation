import 'package:revelation/shared/models/primary_source.dart';

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
    return null;
  }
}

class StrongDictionaryRouteArgs {
  const StrongDictionaryRouteArgs({this.initialStrongNumber});

  static const int defaultInitialStrongNumber = 1;

  final int? initialStrongNumber;

  int get resolvedInitialStrongNumber =>
      initialStrongNumber ?? defaultInitialStrongNumber;

  static StrongDictionaryRouteArgs? tryParse(
    Object? extra,
    Map<String, String> queryParameters,
  ) {
    if (extra is StrongDictionaryRouteArgs) {
      return extra;
    }

    final parsedStrongNumber = _parseStrongNumber(
      queryParameters['number'] ??
          queryParameters['strongNumber'] ??
          queryParameters['strong'],
    );
    if (parsedStrongNumber == null) {
      return const StrongDictionaryRouteArgs();
    }

    return StrongDictionaryRouteArgs(initialStrongNumber: parsedStrongNumber);
  }

  static int? _parseStrongNumber(String? value) {
    final normalized = value?.trim();
    if (normalized == null || normalized.isEmpty) {
      return null;
    }

    final numberText = normalized.startsWith('G') || normalized.startsWith('g')
        ? normalized.substring(1)
        : normalized;
    return int.tryParse(numberText);
  }
}
