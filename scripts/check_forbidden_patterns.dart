import 'dart:io';

class PatternCheck {
  const PatternCheck({
    required this.name,
    required this.pattern,
    required this.roots,
    this.allowedFiles = const <String>{},
    this.filePathPattern,
  });

  final String name;
  final RegExp pattern;
  final List<String> roots;
  final Set<String> allowedFiles;
  final RegExp? filePathPattern;
}

class PatternHit {
  const PatternHit({
    required this.path,
    required this.line,
    required this.snippet,
  });

  final String path;
  final int line;
  final String snippet;
}

void main() {
  final checks = <PatternCheck>[
    PatternCheck(
      name: 'UI should not call DBManager() directly',
      pattern: RegExp(r'\bDBManager\(\)'),
      roots: <String>['lib/screens', 'lib/common_widgets'],
    ),
    PatternCheck(
      name: 'UI should not call ServerManager() directly',
      pattern: RegExp(r'\bServerManager\(\)'),
      roots: <String>['lib/screens', 'lib/common_widgets', 'lib/features'],
    ),
    PatternCheck(
      name: 'Feature modules should not call DBManager() directly',
      pattern: RegExp(r'\bDBManager\(\)'),
      roots: <String>['lib/features'],
    ),
    PatternCheck(
      name: 'Primary sources repository should not call DBManager() directly',
      pattern: RegExp(r'\bDBManager\(\)'),
      roots: <String>['lib/repositories'],
      filePathPattern: RegExp(
        r'^lib/repositories/primary_sources_db_repository\.dart$',
      ),
    ),
    PatternCheck(
      name: 'Services should not call DBManager() directly',
      pattern: RegExp(r'\bDBManager\(\)'),
      roots: <String>['lib/services'],
    ),
    PatternCheck(
      name: 'App bootstrap should not call DBManager() directly',
      pattern: RegExp(r'\bDBManager\(\)'),
      roots: <String>['lib/app/bootstrap'],
      filePathPattern: RegExp(r'^lib/app/bootstrap/app_bootstrap\.dart$'),
    ),
    PatternCheck(
      name: 'Infra layers should instantiate DBManager() only via gateway',
      pattern: RegExp(r'\bDBManager\(\)'),
      roots: <String>['lib/infra'],
      allowedFiles: <String>{
        'lib/infra/db/runtime/db_manager.dart',
        'lib/infra/db/runtime/db_manager_gateway.dart',
      },
    ),
    PatternCheck(
      name: 'Critical routes should avoid map-based state.extra contracts',
      pattern: RegExp(
        r'state\.extra is Map<String,\s*dynamic>|as Map<String,\s*dynamic>',
      ),
      roots: <String>['lib'],
    ),
    PatternCheck(
      name: 'Feature presentation should not import legacy layer-first modules',
      pattern: RegExp(
        "import\\s+['\"]package:revelation/(screens|viewmodels|repositories|managers)/",
      ),
      roots: <String>['lib/features'],
      filePathPattern: RegExp(r'^lib/features/[^/]+/presentation/'),
    ),
    PatternCheck(
      name: 'Feature data should not import feature presentation modules',
      pattern: RegExp(
        "import\\s+['\"]package:revelation/features/[^/]+/presentation/",
      ),
      roots: <String>['lib/features'],
      filePathPattern: RegExp(r'^lib/features/[^/]+/data/'),
    ),
    PatternCheck(
      name: 'Runtime and tests must not import provider package',
      pattern: RegExp("import\\s+['\"]package:provider/"),
      roots: <String>['lib', 'test'],
    ),
    PatternCheck(
      name: 'Runtime and tests must not use ChangeNotifier',
      pattern: RegExp(r'\bChangeNotifier\b'),
      roots: <String>['lib', 'test'],
    ),
    PatternCheck(
      name: 'Runtime and tests must not call notifyListeners()',
      pattern: RegExp(r'\bnotifyListeners\s*\('),
      roots: <String>['lib', 'test'],
    ),
  ];

  var hasViolations = false;
  for (final check in checks) {
    final hits = _collectHits(check);
    if (hits.isEmpty) {
      stdout.writeln('PASS: ${check.name}');
      continue;
    }

    hasViolations = true;
    stdout.writeln('FAIL: ${check.name}');
    for (final hit in hits) {
      stdout.writeln('  - ${hit.path}:${hit.line} -> ${hit.snippet}');
    }
  }

  final structureChecks = <MapEntry<String, List<String>>>[
    MapEntry(
      'Legacy folders should not exist in lib/',
      _checkLegacyFoldersAbsent(
        legacyRoots: const <String>[
          'lib/screens',
          'lib/viewmodels',
          'lib/repositories',
          'lib/services',
          'lib/common_widgets',
          'lib/managers',
          'lib/controllers',
          'lib/models',
          'lib/db',
          'lib/utils',
        ],
      ),
    ),
    MapEntry(
      'lib top-level folders should match approved architecture set',
      _checkUnexpectedTopLevelFolders(
        approvedFolders: const <String>{
          'app',
          'core',
          'infra',
          'shared',
          'features',
          'l10n',
        },
      ),
    ),
  ];

  for (final check in structureChecks) {
    if (check.value.isEmpty) {
      stdout.writeln('PASS: ${check.key}');
      continue;
    }

    hasViolations = true;
    stdout.writeln('FAIL: ${check.key}');
    for (final violation in check.value) {
      stdout.writeln('  - $violation');
    }
  }

  if (hasViolations) {
    stderr.writeln('Forbidden pattern checks failed.');
    exitCode = 1;
    return;
  }

  stdout.writeln('All forbidden pattern checks passed.');
}

List<PatternHit> _collectHits(PatternCheck check) {
  final hits = <PatternHit>[];
  for (final root in check.roots) {
    final directory = Directory(root);
    if (!directory.existsSync()) {
      continue;
    }

    for (final entity in directory.listSync(recursive: true)) {
      if (entity is! File || !entity.path.endsWith('.dart')) {
        continue;
      }

      final relativePath = _normalizePath(entity.path);
      if (check.allowedFiles.contains(relativePath)) {
        continue;
      }
      if (check.filePathPattern != null &&
          !check.filePathPattern!.hasMatch(relativePath)) {
        continue;
      }

      final content = entity.readAsStringSync();
      final matches = check.pattern.allMatches(content);
      for (final match in matches) {
        final line = _lineNumberForOffset(content, match.start);
        final snippet = _lineAtOffset(content, match.start);
        hits.add(PatternHit(path: relativePath, line: line, snippet: snippet));
      }
    }
  }
  return hits;
}

String _normalizePath(String path) {
  final current = Directory.current.path.replaceAll('\\', '/');
  final normalized = path.replaceAll('\\', '/');
  if (normalized.startsWith('$current/')) {
    return normalized.substring(current.length + 1);
  }
  return normalized;
}

int _lineNumberForOffset(String content, int offset) {
  var line = 1;
  for (var i = 0; i < offset; i++) {
    if (content.codeUnitAt(i) == 10) {
      line++;
    }
  }
  return line;
}

String _lineAtOffset(String content, int offset) {
  final start = content.lastIndexOf('\n', offset - 1);
  final end = content.indexOf('\n', offset);
  final normalizedStart = start == -1 ? 0 : start + 1;
  final normalizedEnd = end == -1 ? content.length : end;
  return content.substring(normalizedStart, normalizedEnd).trim();
}

List<String> _checkLegacyFoldersAbsent({required List<String> legacyRoots}) {
  final violations = <String>[];
  for (final root in legacyRoots) {
    final directory = Directory(root);
    if (directory.existsSync()) {
      violations.add(
        'Legacy folder should be removed: ${_normalizePath(root)}',
      );
    }
  }
  return violations;
}

List<String> _checkUnexpectedTopLevelFolders({
  required Set<String> approvedFolders,
}) {
  final libDirectory = Directory('lib');
  if (!libDirectory.existsSync()) {
    return <String>['Missing lib directory.'];
  }

  final currentFolders = libDirectory
      .listSync()
      .whereType<Directory>()
      .map(
        (dir) =>
            dir.uri.pathSegments.lastWhere((segment) => segment.isNotEmpty),
      )
      .toSet();

  final unexpectedFolders = currentFolders.difference(approvedFolders).toList()
    ..sort();

  return unexpectedFolders
      .map((folder) => 'Unexpected top-level lib folder: lib/$folder')
      .toList(growable: false);
}
