import 'dart:io';

class PatternCheck {
  const PatternCheck({
    required this.name,
    required this.pattern,
    required this.roots,
    this.allowedFiles = const <String>{},
  });

  final String name;
  final RegExp pattern;
  final List<String> roots;
  final Set<String> allowedFiles;
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
      allowedFiles: <String>{
        'lib/screens/main/topic_card.dart',
        'lib/screens/main/topic_list.dart',
        'lib/screens/topic/topic_screen.dart',
      },
    ),
    PatternCheck(
      name: 'UI should not call ServerManager() directly',
      pattern: RegExp(r'\bServerManager\(\)'),
      roots: <String>['lib/screens', 'lib/common_widgets', 'lib/features'],
    ),
    PatternCheck(
      name: 'Critical routes should avoid map-based state.extra contracts',
      pattern: RegExp(
        r'state\.extra is Map<String,\s*dynamic>|as Map<String,\s*dynamic>',
      ),
      roots: <String>['lib'],
      allowedFiles: <String>{'lib/app_router.dart'},
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
