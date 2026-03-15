import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/shared/config/app_constants.dart';

void main() {
  late PathProviderPlatform previous;
  late Directory tempDir;

  setUp(() async {
    previous = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp('revelation_test');
    PathProviderPlatform.instance = _FakePathProviderPlatform(tempDir.path);
  });

  tearDown(() async {
    PathProviderPlatform.instance = previous;
    await tempDir.delete(recursive: true);
  });

  test('getAppFolder returns app folder inside documents dir', () async {
    final folder = await getAppFolder();

    expect(folder, '${tempDir.path}/${AppConstants.folder}');
  });

  test('getLastUpdateFileLocal returns null when file is missing', () async {
    final updated = await getLastUpdateFileLocal('db', 'missing.sqlite');

    expect(updated, isNull);
  });

  test('getLastUpdateFileLocal returns last modified time', () async {
    final appFolder = await getAppFolder();
    final file = File(p.join(appFolder, 'db', 'local.sqlite'));
    await file.create(recursive: true);
    await file.writeAsString('data');
    final expected = file.lastModifiedSync();

    final updated = await getLastUpdateFileLocal('db', 'local.sqlite');

    expect(updated?.isAtSameMomentAs(expected), isTrue);
  });
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}
