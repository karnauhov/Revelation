import 'dart:async';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/core/errors/local_folder_open_exception.dart';
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

      expect(calls, <String>[
        'explorer.exe ${p.windows.normalize(tempDir.path)}',
      ]);
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

      final folderPath = '${tempDir.path.replaceAll('\\', '/')}/nested';

      await showLocalAppFolderWith(
        appFolderProvider: () async => folderPath,
        platformOverride: TargetPlatform.windows,
        processStarter:
            (executable, arguments, {mode = ProcessStartMode.normal}) async {
              calls.add('$executable ${arguments.join(' ')} $mode');
              return _FakeProcess();
            },
      );

      expect(calls, <String>[
        'explorer.exe ${p.windows.normalize(folderPath)} detached',
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
      throwsA(
        isA<LocalFolderOpenException>()
            .having((error) => error.folderPath, 'folderPath', tempDir.path)
            .having((error) => error.cause, 'cause', isA<StateError>()),
      ),
    );
  });

  test('process startup failure preserves the path, cause and stack', () async {
    final tempDir = await Directory.systemTemp.createTemp(
      'local_folder_throw_',
    );
    addTearDown(() => tempDir.delete(recursive: true));
    final folderPath = p.join(tempDir.path, 'Моя папка with spaces');
    final cause = ProcessException('explorer.exe', [folderPath], 'unavailable');
    final originalStack = StackTrace.fromString('folder opener origin');

    try {
      await showLocalAppFolderWith(
        appFolderProvider: () async => folderPath,
        platformOverride: TargetPlatform.windows,
        processStarter: (_, _, {mode = ProcessStartMode.normal}) async {
          Error.throwWithStackTrace(cause, originalStack);
        },
      );
      fail('The process failure must be reported.');
    } on LocalFolderOpenException catch (error, stack) {
      expect(error.folderPath, folderPath);
      expect(error.cause, same(cause));
      expect(error.toString(), contains(folderPath));
      expect(stack.toString(), originalStack.toString());
    }
  });

  test('folder creation failure preserves its resolved path', () async {
    final tempDir = await Directory.systemTemp.createTemp(
      'local_folder_create_',
    );
    addTearDown(() => tempDir.delete(recursive: true));
    final blocker = await File(p.join(tempDir.path, 'file')).writeAsString('x');
    final folderPath = p.join(blocker.path, 'folder');
    var launcherCalls = 0;

    await expectLater(
      showLocalAppFolderWith(
        appFolderProvider: () async => folderPath,
        platformOverride: TargetPlatform.android,
        urlLauncher: (_) async {
          launcherCalls++;
          return true;
        },
      ),
      throwsA(
        isA<LocalFolderOpenException>()
            .having((error) => error.folderPath, 'folderPath', folderPath)
            .having(
              (error) => error.cause,
              'cause',
              isA<FileSystemException>(),
            ),
      ),
    );
    expect(launcherCalls, 0);
  });

  test('mobile launcher rejection preserves the folder path', () async {
    final tempDir = await Directory.systemTemp.createTemp(
      'local_folder_mobile_',
    );
    addTearDown(() => tempDir.delete(recursive: true));
    await expectLater(
      showLocalAppFolderWith(
        appFolderProvider: () async => tempDir.path,
        platformOverride: TargetPlatform.android,
        urlLauncher: (_) async => false,
      ),
      throwsA(
        isA<LocalFolderOpenException>().having(
          (error) => error.folderPath,
          'folderPath',
          tempDir.path,
        ),
      ),
    );
  });

  test('unresolved folder errors do not invent a path', () async {
    final cause = FileSystemException('Documents is unavailable');
    await expectLater(
      showLocalAppFolderWith(appFolderProvider: () async => throw cause),
      throwsA(same(cause)),
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
