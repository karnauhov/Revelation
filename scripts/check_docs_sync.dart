import 'dart:io';

class DocsPair {
  const DocsPair({
    required this.ruPath,
    required this.enPath,
    required this.name,
  });

  final String ruPath;
  final String enPath;
  final String name;
}

void main() {
  const pairs = <DocsPair>[
    DocsPair(
      name: 'Architecture overview',
      ruPath: 'docs/ru/architecture/overview.ru.md',
      enPath: 'docs/en/architecture/overview.en.md',
    ),
    DocsPair(
      name: 'Module boundaries',
      ruPath: 'docs/ru/architecture/module-boundaries.ru.md',
      enPath: 'docs/en/architecture/module-boundaries.en.md',
    ),
    DocsPair(
      name: 'State management matrix',
      ruPath: 'docs/ru/architecture/state_management_matrix.ru.md',
      enPath: 'docs/en/architecture/state_management_matrix.en.md',
    ),
    DocsPair(
      name: 'Testing strategy',
      ruPath: 'docs/ru/testing/strategy.ru.md',
      enPath: 'docs/en/testing/strategy.en.md',
    ),
  ];

  var hasFailures = false;
  for (final pair in pairs) {
    final ruFile = File(pair.ruPath);
    final enFile = File(pair.enPath);

    if (!ruFile.existsSync() || !enFile.existsSync()) {
      hasFailures = true;
      stderr.writeln(
        'FAIL: ${pair.name} -> missing pair file(s): '
        '${!ruFile.existsSync() ? pair.ruPath : ''} '
        '${!enFile.existsSync() ? pair.enPath : ''}',
      );
      continue;
    }

    final ruContent = ruFile.readAsStringSync();
    final enContent = enFile.readAsStringSync();

    final ruDocVersion = _headerValue(ruContent, 'Doc-Version');
    final enDocVersion = _headerValue(enContent, 'Doc-Version');
    final ruLastUpdated = _headerValue(ruContent, 'Last-Updated');
    final enLastUpdated = _headerValue(enContent, 'Last-Updated');
    final ruSourceCommit = _headerValue(ruContent, 'Source-Commit');
    final enSourceCommit = _headerValue(enContent, 'Source-Commit');

    final pairFailures = <String>[];
    if (ruDocVersion == null || enDocVersion == null) {
      pairFailures.add('missing `Doc-Version` header');
    } else if (ruDocVersion != enDocVersion) {
      pairFailures.add(
        '`Doc-Version` mismatch (`$ruDocVersion` != `$enDocVersion`)',
      );
    }

    if (ruLastUpdated == null || enLastUpdated == null) {
      pairFailures.add('missing `Last-Updated` header');
    } else if (ruLastUpdated != enLastUpdated) {
      pairFailures.add(
        '`Last-Updated` mismatch (`$ruLastUpdated` != `$enLastUpdated`)',
      );
    }

    if (ruSourceCommit == null || enSourceCommit == null) {
      pairFailures.add('missing `Source-Commit` header');
    } else if (ruSourceCommit != enSourceCommit) {
      pairFailures.add(
        '`Source-Commit` mismatch (`$ruSourceCommit` != `$enSourceCommit`)',
      );
    }

    if (pairFailures.isEmpty) {
      stdout.writeln('PASS: ${pair.name}');
      continue;
    }

    hasFailures = true;
    stderr.writeln('FAIL: ${pair.name}');
    for (final failure in pairFailures) {
      stderr.writeln('  - $failure');
    }
  }

  if (hasFailures) {
    stderr.writeln('Docs sync checks failed.');
    exitCode = 1;
    return;
  }

  stdout.writeln('All docs sync checks passed.');
}

String? _headerValue(String content, String headerName) {
  final pattern = RegExp(
    '^${RegExp.escape(headerName)}:\\s*`?([^`\\r\\n]+)`?',
    multiLine: true,
  );
  return pattern.firstMatch(content)?.group(1)?.trim();
}
