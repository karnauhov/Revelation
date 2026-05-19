import 'dart:async';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/infra/storage/local_app_folder_io.dart';

void main() {
  test(
    'showLocalAppFolderWith opens desktop folder with platform command',
    () async {
      final tempDir = await Directory.systemTemp.createTemp(
        'local_folder_open_test_',
      );
      final calls = <String>[];
      addTearDown(() async {
        if (await tempDir.exists()) {
          await tempDir.delete(recursive: true);
        }
      });

      await showLocalAppFolderWith(
        appFolderProvider: () async => tempDir.path,
        platformOverride: TargetPlatform.windows,
        processRunner: (executable, arguments) async {
          calls.add('$executable ${arguments.join(' ')}');
          return ProcessResult(1, 0, '', '');
        },
      );

      expect(calls, <String>['explorer.exe ${tempDir.path}']);
    },
  );

  test(
    'showLocalAppFolderWith starts Windows explorer detached with normalized path',
    () async {
      final tempDir = await Directory.systemTemp.createTemp(
        'local_folder_start_test_',
      );
      final calls = <String>[];
      addTearDown(() async {
        if (await tempDir.exists()) {
          await tempDir.delete(recursive: true);
        }
      });

      await showLocalAppFolderWith(
        appFolderProvider: () async =>
            '${tempDir.path.replaceAll('\\', '/')}/nested',
        platformOverride: TargetPlatform.windows,
        processStarter:
            (executable, arguments, {mode = ProcessStartMode.normal}) async {
              calls.add('$executable ${arguments.join(' ')} $mode');
              return _FakeProcess();
            },
      );

      expect(calls, <String>[
        'explorer.exe ${p.windows.join(tempDir.path, 'nested')} detached',
      ]);
    },
  );

  test('showLocalAppFolderWith uses file URI launcher on mobile', () async {
    final tempDir = await Directory.systemTemp.createTemp(
      'local_folder_mobile_test_',
    );
    Uri? launchedUri;
    addTearDown(() async {
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    await showLocalAppFolderWith(
      appFolderProvider: () async => tempDir.path,
      platformOverride: TargetPlatform.android,
      urlLauncher: (uri) async {
        launchedUri = uri;
        return true;
      },
    );

    expect(launchedUri, Directory(tempDir.path).uri);
  });

  test('showLocalAppFolderWith reports launcher failures', () async {
    final tempDir = await Directory.systemTemp.createTemp(
      'local_folder_fail_test_',
    );
    addTearDown(() async {
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    expect(
      showLocalAppFolderWith(
        appFolderProvider: () async => tempDir.path,
        platformOverride: TargetPlatform.linux,
        processRunner: (_, _) async => ProcessResult(1, 1, '', 'no opener'),
      ),
      throwsA(isA<StateError>()),
    );
  });
}

class _FakeProcess implements Process {
  @override
  Future<int> get exitCode async => 0;

  @override
  int get pid => 1;

  @override
  Stream<List<int>> get stderr => const Stream<List<int>>.empty();

  @override
  IOSink get stdin => IOSink(StreamController<List<int>>().sink);

  @override
  Stream<List<int>> get stdout => const Stream<List<int>>.empty();

  @override
  bool kill([ProcessSignal signal = ProcessSignal.sigterm]) => true;
}
