import 'dart:io';

Future<void> main(List<String> args) async {
  final inputPath = _readRequiredOption(args, 'input');
  final outputPath = _readRequiredOption(args, 'output');

  if (!await File(inputPath).exists()) {
    stderr.writeln('Input asset does not exist: $inputPath');
    exitCode = 1;
    return;
  }

  final outputFile = File(outputPath);
  await outputFile.parent.create(recursive: true);
  await outputFile.writeAsString(
    DateTime.now().toUtc().toIso8601String(),
    flush: true,
  );
}

String _readRequiredOption(List<String> args, String optionName) {
  final optionPrefix = '--$optionName=';
  for (final arg in args) {
    if (arg.startsWith(optionPrefix)) {
      return arg.substring(optionPrefix.length);
    }
  }

  stderr.writeln('Missing required option --$optionName');
  exitCode = 1;
  throw StateError('Missing required option --$optionName');
}
