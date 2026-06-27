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

class BibleRouteArgs {
  const BibleRouteArgs({
    this.initialBookId = 66,
    this.initialChapter = 1,
    this.initialVerse = 1,
    this.initialModuleFile,
  });

  final int initialBookId;
  final int initialChapter;
  final int initialVerse;
  final String? initialModuleFile;

  static BibleRouteArgs tryParse(
    Object? extra,
    Map<String, String> queryParameters,
  ) {
    if (extra is BibleRouteArgs) {
      return extra;
    }

    return BibleRouteArgs(
      initialBookId: _parsePositiveInt(queryParameters['book']) ?? 66,
      initialChapter: _parsePositiveInt(queryParameters['chapter']) ?? 1,
      initialVerse: _parsePositiveInt(queryParameters['verse']) ?? 1,
      initialModuleFile: _parseModuleFile(queryParameters['module']),
    );
  }

  static int? _parsePositiveInt(String? value) {
    final parsed = int.tryParse(value?.trim() ?? '');
    return parsed == null || parsed <= 0 ? null : parsed;
  }

  static String? _parseModuleFile(String? value) {
    final normalized = value?.trim();
    return normalized == null || normalized.isEmpty ? null : normalized;
  }
}
