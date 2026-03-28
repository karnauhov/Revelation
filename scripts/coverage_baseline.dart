import 'dart:io';

const String _defaultLcovPath = 'coverage/lcov.info';

const Set<String> _platformGlueFiles = <String>{
  'lib/core/platform/dependent.dart',
  'lib/core/platform/file_downloader.dart',
  'lib/infra/db/connectors/shared.dart',
};

void main(List<String> args) {
  final CoverageArgs coverageArgs = _parseArgs(args);
  if (!coverageArgs.isValid) {
    exitCode = 2;
    return;
  }

  final String lcovPath = coverageArgs.lcovPath;
  final File lcovFile = File(lcovPath);
  if (!lcovFile.existsSync()) {
    stderr.writeln('LCOV file not found: $lcovPath');
    stderr.writeln('Run: flutter test --coverage');
    exitCode = 2;
    return;
  }

  final Map<String, CoverageRecord> coverageByFile = _parseLcov(lcovFile);
  if (coverageByFile.isEmpty) {
    stderr.writeln('No coverage records found in $lcovPath');
    exitCode = 3;
    return;
  }

  int allLf = 0;
  int allLh = 0;
  int effectiveLf = 0;
  int effectiveLh = 0;
  int generatedCount = 0;
  int l10nCount = 0;
  int barrelCount = 0;
  int platformGlueCount = 0;

  for (final MapEntry<String, CoverageRecord> entry in coverageByFile.entries) {
    final String path = entry.key;
    final CoverageRecord record = entry.value;

    allLf += record.lf;
    allLh += record.lh;

    final bool generated = _isGenerated(path);
    final bool l10n = _isL10n(path);
    final bool barrel = _isBarrelFile(path);
    final bool platformGlue = _isPlatformGlue(path);

    if (generated) {
      generatedCount += 1;
    }
    if (l10n) {
      l10nCount += 1;
    }
    if (barrel) {
      barrelCount += 1;
    }
    if (platformGlue) {
      platformGlueCount += 1;
    }

    if (generated || l10n || barrel || platformGlue) {
      continue;
    }

    effectiveLf += record.lf;
    effectiveLh += record.lh;
  }

  final List<String> allLibFiles = _collectLibFiles();
  final Set<String> lcovFiles = coverageByFile.keys.toSet();
  final List<String> missingInLcov =
      allLibFiles.where((String path) => !lcovFiles.contains(path)).toList()
        ..sort();

  stdout.writeln('Coverage Baseline Summary');
  stdout.writeln('Date: ${DateTime.now().toIso8601String()}');
  stdout.writeln('LCOV: $lcovPath');
  stdout.writeln('');
  final double allPercent = _percentValue(allLh, allLf);
  final double effectivePercent = _percentValue(effectiveLh, effectiveLf);

  stdout.writeln('ALL_LIB: $allLh/$allLf (${_formatPercent(allLh, allLf)}%)');
  stdout.writeln(
    'EFFECTIVE_LIB: $effectiveLh/$effectiveLf (${_formatPercent(effectiveLh, effectiveLf)}%)',
  );
  if (coverageArgs.minAll != null) {
    stdout.writeln(
      'ALL_LIB threshold: ${coverageArgs.minAll!.toStringAsFixed(2)}%',
    );
  }
  if (coverageArgs.minEffective != null) {
    stdout.writeln(
      'EFFECTIVE_LIB threshold: ${coverageArgs.minEffective!.toStringAsFixed(2)}%',
    );
  }
  stdout.writeln('');
  stdout.writeln('Effective scope exclusions (file-level from LCOV):');
  stdout.writeln('  generated (*.g.dart, *.freezed.dart): $generatedCount');
  stdout.writeln('  localization (lib/l10n/**): $l10nCount');
  stdout.writeln('  export-only barrel files: $barrelCount');
  stdout.writeln('  platform glue shims: $platformGlueCount');
  stdout.writeln('');
  stdout.writeln(
    'Files in lib/**/*.dart not present in LCOV: ${missingInLcov.length}',
  );
  if (missingInLcov.isNotEmpty) {
    for (final String path in missingInLcov) {
      stdout.writeln('  - $path');
    }
  }

  bool failed = false;
  if (coverageArgs.minAll != null && allPercent < coverageArgs.minAll!) {
    stderr.writeln(
      'ALL_LIB coverage ${_formatPercent(allLh, allLf)}% is below ${coverageArgs.minAll!.toStringAsFixed(2)}%',
    );
    failed = true;
  }
  if (coverageArgs.minEffective != null &&
      effectivePercent < coverageArgs.minEffective!) {
    stderr.writeln(
      'EFFECTIVE_LIB coverage ${_formatPercent(effectiveLh, effectiveLf)}% is below ${coverageArgs.minEffective!.toStringAsFixed(2)}%',
    );
    failed = true;
  }
  if (failed) {
    exitCode = 4;
  }
}

class CoverageArgs {
  const CoverageArgs({
    required this.lcovPath,
    required this.isValid,
    this.minAll,
    this.minEffective,
  });

  final String lcovPath;
  final double? minAll;
  final double? minEffective;
  final bool isValid;
}

CoverageArgs _parseArgs(List<String> args) {
  String? lcovPath;
  double? minAll;
  double? minEffective;
  bool isValid = true;

  for (final String arg in args) {
    if (arg.startsWith('--lcov=')) {
      lcovPath = arg.substring('--lcov='.length);
      continue;
    }
    if (arg.startsWith('--min-all=')) {
      final String raw = arg.substring('--min-all='.length);
      final double? parsed = double.tryParse(raw);
      if (parsed == null) {
        stderr.writeln('Invalid --min-all value: $raw');
        isValid = false;
      } else {
        minAll = parsed;
      }
      continue;
    }
    if (arg.startsWith('--min-effective=')) {
      final String raw = arg.substring('--min-effective='.length);
      final double? parsed = double.tryParse(raw);
      if (parsed == null) {
        stderr.writeln('Invalid --min-effective value: $raw');
        isValid = false;
      } else {
        minEffective = parsed;
      }
      continue;
    }
    if (!arg.startsWith('--') && lcovPath == null) {
      lcovPath = arg;
    }
  }

  return CoverageArgs(
    lcovPath: lcovPath ?? _defaultLcovPath,
    minAll: minAll,
    minEffective: minEffective,
    isValid: isValid,
  );
}

Map<String, CoverageRecord> _parseLcov(File lcovFile) {
  final Map<String, CoverageRecord> records = <String, CoverageRecord>{};
  String? currentFile;

  for (final String rawLine in lcovFile.readAsLinesSync()) {
    final String line = rawLine.trim();
    if (line.startsWith('SF:')) {
      currentFile = _normalizePath(line.substring(3));
      records.putIfAbsent(currentFile, CoverageRecord.new);
      continue;
    }

    if (currentFile == null) {
      continue;
    }

    if (line.startsWith('LF:')) {
      records[currentFile]!.lf = int.tryParse(line.substring(3)) ?? 0;
      continue;
    }

    if (line.startsWith('LH:')) {
      records[currentFile]!.lh = int.tryParse(line.substring(3)) ?? 0;
      continue;
    }
  }

  return records;
}

List<String> _collectLibFiles() {
  final Directory libDir = Directory('lib');
  if (!libDir.existsSync()) {
    return <String>[];
  }

  final String cwd = _normalizePath(Directory.current.path);
  final List<String> files = <String>[];
  for (final FileSystemEntity entity in libDir.listSync(recursive: true)) {
    if (entity is! File || !entity.path.endsWith('.dart')) {
      continue;
    }
    files.add(_normalizePath(entity.path, cwd: cwd));
  }
  files.sort();
  return files;
}

bool _isGenerated(String path) {
  return path.endsWith('.g.dart') || path.endsWith('.freezed.dart');
}

bool _isL10n(String path) {
  return path.startsWith('lib/l10n/');
}

bool _isPlatformGlue(String path) {
  return _platformGlueFiles.contains(path);
}

bool _isBarrelFile(String path) {
  final File file = File(path);
  if (!file.existsSync()) {
    return false;
  }

  final List<String> lines = file.readAsLinesSync();
  final List<String> meaningful = <String>[];
  bool inBlockComment = false;

  for (String line in lines) {
    String trimmed = line.trim();
    if (trimmed.isEmpty) {
      continue;
    }

    if (inBlockComment) {
      final int endIdx = trimmed.indexOf('*/');
      if (endIdx == -1) {
        continue;
      }
      trimmed = trimmed.substring(endIdx + 2).trim();
      inBlockComment = false;
      if (trimmed.isEmpty) {
        continue;
      }
    }

    if (trimmed.startsWith('//')) {
      continue;
    }

    if (trimmed.startsWith('/*')) {
      final int endIdx = trimmed.indexOf('*/', 2);
      if (endIdx == -1) {
        inBlockComment = true;
        continue;
      }
      trimmed = trimmed.substring(endIdx + 2).trim();
      if (trimmed.isEmpty) {
        continue;
      }
    }

    if (trimmed.startsWith('*')) {
      continue;
    }

    meaningful.add(trimmed);
  }

  if (meaningful.isEmpty) {
    return false;
  }

  return meaningful.every((String line) => line.startsWith('export '));
}

String _normalizePath(String input, {String? cwd}) {
  String path = _normalizeSlashes(input);
  if (path.startsWith('./')) {
    path = path.substring(2);
  }

  final String normalizedCwd = _normalizeSlashes(cwd ?? Directory.current.path);
  final String cwdPrefix = '$normalizedCwd/';
  if (path.startsWith(cwdPrefix)) {
    path = path.substring(cwdPrefix.length);
  }
  return path;
}

String _normalizeSlashes(String input) {
  return input.replaceAll('\\', '/');
}

String _formatPercent(int covered, int total) {
  if (total == 0) {
    return '0.00';
  }
  final double value = (covered * 100.0) / total;
  return value.toStringAsFixed(2);
}

double _percentValue(int covered, int total) {
  if (total == 0) {
    return 0;
  }
  return (covered * 100.0) / total;
}

class CoverageRecord {
  int lf = 0;
  int lh = 0;
}
