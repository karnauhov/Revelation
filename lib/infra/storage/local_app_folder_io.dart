import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:url_launcher/url_launcher.dart' show LaunchMode, launchUrl;

typedef LocalFolderProcessRunner =
    Future<ProcessResult> Function(String executable, List<String> arguments);
typedef LocalFolderProcessStarter =
    Future<Process> Function(
      String executable,
      List<String> arguments, {
      ProcessStartMode mode,
    });
typedef LocalFolderUrlLauncher = Future<bool> Function(Uri uri);

Future<void> showLocalAppFolder() {
  return showLocalAppFolderWith();
}

@visibleForTesting
Future<void> showLocalAppFolderWith({
  Future<String> Function()? appFolderProvider,
  LocalFolderProcessRunner? processRunner,
  LocalFolderProcessStarter? processStarter,
  LocalFolderUrlLauncher? urlLauncher,
  TargetPlatform? platformOverride,
}) async {
  final folderPath = await (appFolderProvider ?? getAppFolder)();
  final folder = Directory(folderPath);
  await folder.create(recursive: true);

  final platform = platformOverride ?? defaultTargetPlatform;
  final launched = await _launchFolder(
    folder,
    platform: platform,
    processRunner: processRunner,
    processStarter: processStarter ?? Process.start,
    urlLauncher:
        urlLauncher ??
        (uri) => launchUrl(uri, mode: LaunchMode.externalApplication),
  );
  if (!launched) {
    throw StateError('Unable to open local app folder: ${folder.path}');
  }
}

Future<bool> _launchFolder(
  Directory folder, {
  required TargetPlatform platform,
  LocalFolderProcessRunner? processRunner,
  required LocalFolderProcessStarter processStarter,
  required LocalFolderUrlLauncher urlLauncher,
}) async {
  switch (platform) {
    case TargetPlatform.windows:
      return _runOpenCommand(
        processRunner: processRunner,
        processStarter: processStarter,
        executable: 'explorer.exe',
        arguments: [_platformFolderPath(folder, platform)],
      );
    case TargetPlatform.macOS:
      return _runOpenCommand(
        processRunner: processRunner,
        processStarter: processStarter,
        executable: 'open',
        arguments: [_platformFolderPath(folder, platform)],
      );
    case TargetPlatform.linux:
      return _runOpenCommand(
        processRunner: processRunner,
        processStarter: processStarter,
        executable: 'xdg-open',
        arguments: [_platformFolderPath(folder, platform)],
      );
    case TargetPlatform.android:
    case TargetPlatform.iOS:
    case TargetPlatform.fuchsia:
      return urlLauncher(folder.uri);
  }
}

Future<bool> _runOpenCommand({
  required LocalFolderProcessRunner? processRunner,
  required LocalFolderProcessStarter processStarter,
  required String executable,
  required List<String> arguments,
}) async {
  if (processRunner != null) {
    final result = await processRunner(executable, arguments);
    return result.exitCode == 0;
  }

  await processStarter(executable, arguments, mode: ProcessStartMode.detached);
  return true;
}

String _platformFolderPath(Directory folder, TargetPlatform platform) {
  if (platform == TargetPlatform.windows) {
    return p.windows.normalize(folder.path);
  }
  return folder.path;
}
