import 'dart:convert';
import 'dart:io';

const _criticalTextFiles = <String>[
  'lib/shared/config/app_constants.dart',
  'integration_test/smoke/settings_topics_language_sync_smoke_test.dart',
];

const _requiredSnippetsByFile = <String, List<String>>{
  'lib/shared/config/app_constants.dart': <String>[
    "'es': 'Español'",
    "'uk': 'Українська'",
    "'ru': 'Русский'",
  ],
  'integration_test/smoke/settings_topics_language_sync_smoke_test.dart':
      <String>["find.text('Русский')"],
};

const _requiredArbValues = <String, Map<String, String>>{
  'lib/l10n/app_es.arb': <String, String>{'version': 'Versión'},
  'lib/l10n/app_ru.arb': <String, String>{'app_name': 'Откровение'},
};

final _latinMojibakePattern = RegExp(r'(?:Ã|Â)[\u0080-\u00BF]');
final _unexpectedCyrillicForSpanish = RegExp(r'[А-Яа-яЁёІіЇїЄєҐґ]');
final _unexpectedCyrillicSupplement = RegExp(r'[ЃѓЂђЉљЊњЋћЌќЎўЏџ]');
final _unexpectedPunctuationMojibake = RegExp(r'[‚„…†‡€‰‹›™]');

void main() {
  final issues = <String>[];
  final files = _collectTargetFiles();
  final utf8ContentByPath = <String, String>{};
  final arbByPath = <String, Map<String, dynamic>>{};

  for (final filePath in files) {
    final file = File(filePath);
    if (!file.existsSync()) {
      issues.add('Missing file: $filePath');
      continue;
    }

    final bytes = file.readAsBytesSync();
    String content;
    try {
      content = utf8.decode(bytes, allowMalformed: false);
    } on FormatException catch (error) {
      issues.add('Invalid UTF-8 in $filePath: ${error.message}');
      continue;
    }

    utf8ContentByPath[filePath] = content;

    if (filePath.endsWith('.arb')) {
      try {
        final decoded = jsonDecode(content);
        if (decoded is! Map<String, dynamic>) {
          issues.add('ARB root is not an object: $filePath');
        } else {
          arbByPath[filePath] = decoded;
        }
      } on FormatException catch (error) {
        issues.add('Invalid JSON in $filePath: ${error.message}');
      }
    }

    _checkForMojibake(filePath: filePath, content: content, issues: issues);
  }

  _checkRequiredSnippets(utf8ContentByPath: utf8ContentByPath, issues: issues);
  _checkRequiredArbValues(arbByPath: arbByPath, issues: issues);

  if (issues.isNotEmpty) {
    stderr.writeln('Encoding sanity check failed:');
    for (final issue in issues) {
      stderr.writeln('  - $issue');
    }
    exitCode = 1;
    return;
  }

  stdout.writeln('Encoding sanity check passed.');
}

List<String> _collectTargetFiles() {
  final files = <String>[];
  final l10nDirectory = Directory('lib/l10n');
  if (l10nDirectory.existsSync()) {
    files.addAll(
      l10nDirectory
          .listSync()
          .whereType<File>()
          .map((file) => _normalizePath(file.path))
          .where((path) => path.endsWith('.arb')),
    );
  }
  files.addAll(_criticalTextFiles);
  final unique = files.toSet().toList()..sort();
  return unique;
}

void _checkForMojibake({
  required String filePath,
  required String content,
  required List<String> issues,
}) {
  if (_latinMojibakePattern.hasMatch(content)) {
    issues.add(
      'Possible Latin mojibake marker found in $filePath '
      '(contains Ã/Â sequences).',
    );
  }

  if (_unexpectedCyrillicSupplement.hasMatch(content)) {
    issues.add('Unexpected Cyrillic supplement characters found in $filePath.');
  }

  if (_unexpectedPunctuationMojibake.hasMatch(content)) {
    issues.add('Unexpected mojibake punctuation marker found in $filePath.');
  }

  if (filePath == 'lib/l10n/app_es.arb' &&
      _unexpectedCyrillicForSpanish.hasMatch(content)) {
    issues.add('Spanish ARB contains Cyrillic letters: $filePath');
  }
}

void _checkRequiredSnippets({
  required Map<String, String> utf8ContentByPath,
  required List<String> issues,
}) {
  for (final entry in _requiredSnippetsByFile.entries) {
    final filePath = entry.key;
    final content = utf8ContentByPath[filePath];
    if (content == null) {
      continue;
    }
    for (final snippet in entry.value) {
      if (!content.contains(snippet)) {
        issues.add('Expected UTF-8 snippet not found in $filePath: $snippet');
      }
    }
  }
}

void _checkRequiredArbValues({
  required Map<String, Map<String, dynamic>> arbByPath,
  required List<String> issues,
}) {
  for (final entry in _requiredArbValues.entries) {
    final filePath = entry.key;
    final arb = arbByPath[filePath];
    if (arb == null) {
      continue;
    }
    for (final expected in entry.value.entries) {
      final key = expected.key;
      final expectedValue = expected.value;
      final actualValue = arb[key];
      if (actualValue is! String || actualValue != expectedValue) {
        issues.add(
          'Unexpected value for "$key" in $filePath: '
          'expected "$expectedValue", got "$actualValue".',
        );
      }
    }
  }
}

String _normalizePath(String path) {
  final current = Directory.current.path.replaceAll('\\', '/');
  final normalized = path.replaceAll('\\', '/');
  if (normalized.startsWith('$current/')) {
    return normalized.substring(current.length + 1);
  }
  return normalized;
}
