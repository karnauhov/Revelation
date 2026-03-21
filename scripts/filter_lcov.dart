import 'dart:io';

const String _defaultLcovPath = 'coverage/lcov.info';

void main(List<String> args) {
  final FilterArgs filterArgs = _parseArgs(args);
  if (!filterArgs.isValid) {
    exitCode = 2;
    return;
  }

  final File inputFile = File(filterArgs.lcovPath);
  if (!inputFile.existsSync()) {
    stderr.writeln('LCOV file not found: ${filterArgs.lcovPath}');
    stderr.writeln('Run: flutter test --coverage');
    exitCode = 2;
    return;
  }

  final List<String> lines = inputFile.readAsLinesSync();
  final _FilterResult result = _filterRecords(lines);

  stdout.writeln('LCOV filter summary');
  stdout.writeln('Input: ${filterArgs.lcovPath}');
  stdout.writeln('Records total: ${result.totalRecords}');
  stdout.writeln('Records kept: ${result.keptRecords}');
  stdout.writeln('Records excluded: ${result.excludedRecords}');
  stdout.writeln(
    '  generated (*.g.dart, *.freezed.dart): '
    '${result.generatedExcluded}',
  );
  stdout.writeln('  localization (lib/l10n/**): ${result.l10nExcluded}');

  if (filterArgs.dryRun) {
    stdout.writeln('Dry-run: output file was not modified.');
    return;
  }

  final File outputFile = File(filterArgs.outPath);
  outputFile.parent.createSync(recursive: true);
  final String outputText = result.filteredLines.join('\n');
  outputFile.writeAsStringSync('$outputText\n');
  stdout.writeln('Written: ${filterArgs.outPath}');
}

FilterArgs _parseArgs(List<String> args) {
  String? lcovPath;
  String? outPath;
  bool dryRun = false;
  bool isValid = true;

  for (final String arg in args) {
    if (arg == '--dry-run') {
      dryRun = true;
      continue;
    }
    if (arg.startsWith('--lcov=')) {
      lcovPath = arg.substring('--lcov='.length);
      continue;
    }
    if (arg.startsWith('--out=')) {
      outPath = arg.substring('--out='.length);
      continue;
    }
    if (arg.startsWith('--')) {
      stderr.writeln('Unknown option: $arg');
      isValid = false;
      continue;
    }
    lcovPath ??= arg;
  }

  final String resolvedLcov = lcovPath ?? _defaultLcovPath;
  return FilterArgs(
    lcovPath: resolvedLcov,
    outPath: outPath ?? resolvedLcov,
    dryRun: dryRun,
    isValid: isValid,
  );
}

_FilterResult _filterRecords(List<String> lines) {
  final List<String> filteredLines = <String>[];
  final List<String> currentRecord = <String>[];
  int totalRecords = 0;
  int keptRecords = 0;
  int excludedRecords = 0;
  int generatedExcluded = 0;
  int l10nExcluded = 0;

  void flushRecord() {
    if (currentRecord.isEmpty) {
      return;
    }
    totalRecords += 1;
    final String? path = _extractSourcePath(currentRecord);
    final _ExcludeReason reason = _excludeReason(path);
    if (reason == _ExcludeReason.none) {
      filteredLines.addAll(currentRecord);
      keptRecords += 1;
    } else {
      excludedRecords += 1;
      if (reason == _ExcludeReason.generated) {
        generatedExcluded += 1;
      } else if (reason == _ExcludeReason.l10n) {
        l10nExcluded += 1;
      }
    }
    currentRecord.clear();
  }

  for (final String line in lines) {
    currentRecord.add(line);
    if (line.trim() == 'end_of_record') {
      flushRecord();
    }
  }
  flushRecord();

  return _FilterResult(
    filteredLines: filteredLines,
    totalRecords: totalRecords,
    keptRecords: keptRecords,
    excludedRecords: excludedRecords,
    generatedExcluded: generatedExcluded,
    l10nExcluded: l10nExcluded,
  );
}

String? _extractSourcePath(List<String> recordLines) {
  for (final String line in recordLines) {
    if (line.startsWith('SF:')) {
      return _normalizePath(line.substring(3).trim());
    }
  }
  return null;
}

_ExcludeReason _excludeReason(String? normalizedPath) {
  if (normalizedPath == null || normalizedPath.isEmpty) {
    return _ExcludeReason.none;
  }
  if (_isGenerated(normalizedPath)) {
    return _ExcludeReason.generated;
  }
  if (_isL10n(normalizedPath)) {
    return _ExcludeReason.l10n;
  }
  return _ExcludeReason.none;
}

bool _isGenerated(String path) {
  return path.endsWith('.g.dart') || path.endsWith('.freezed.dart');
}

bool _isL10n(String path) {
  return path.startsWith('lib/l10n/') || path.contains('/lib/l10n/');
}

String _normalizePath(String input) {
  String path = input.replaceAll('\\', '/');
  if (path.startsWith('./')) {
    path = path.substring(2);
  }
  final String cwd = Directory.current.path.replaceAll('\\', '/');
  final String cwdPrefix = '$cwd/';
  if (path.startsWith(cwdPrefix)) {
    path = path.substring(cwdPrefix.length);
  }
  return path;
}

class FilterArgs {
  const FilterArgs({
    required this.lcovPath,
    required this.outPath,
    required this.dryRun,
    required this.isValid,
  });

  final String lcovPath;
  final String outPath;
  final bool dryRun;
  final bool isValid;
}

class _FilterResult {
  const _FilterResult({
    required this.filteredLines,
    required this.totalRecords,
    required this.keptRecords,
    required this.excludedRecords,
    required this.generatedExcluded,
    required this.l10nExcluded,
  });

  final List<String> filteredLines;
  final int totalRecords;
  final int keptRecords;
  final int excludedRecords;
  final int generatedExcluded;
  final int l10nExcluded;
}

enum _ExcludeReason { none, generated, l10n }
