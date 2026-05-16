import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/storage/app_cache_manager_io.dart';
import 'package:revelation/shared/config/app_constants.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late PathProviderPlatform previous;
  late Directory tempDir;

  setUp(() async {
    previous = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp('app_cache_test_');
    PathProviderPlatform.instance = _FakePathProviderPlatform(tempDir.path);
  });

  tearDown(() async {
    PathProviderPlatform.instance = previous;
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  test(
    'clearAppCache deletes images cache without touching data files',
    () async {
      final appFolder = p.join(tempDir.path, AppConstants.folder);
      final cachedWord = File(
        p.join(appFolder, 'images', 'primary_source_words', 'word.png'),
      );
      final cachedPage = File(p.join(appFolder, 'images', 'pages', 'page.jpg'));
      final dbFile = File(p.join(appFolder, 'db', AppConstants.commonDB));

      await cachedWord.create(recursive: true);
      await cachedWord.writeAsBytes(<int>[1, 2, 3]);
      await cachedPage.create(recursive: true);
      await cachedPage.writeAsBytes(<int>[4, 5, 6]);
      await dbFile.create(recursive: true);
      await dbFile.writeAsBytes(<int>[7, 8, 9]);

      await clearAppCache();

      expect(await Directory(p.join(appFolder, 'images')).exists(), isFalse);
      expect(await dbFile.exists(), isTrue);
      expect(await dbFile.readAsBytes(), <int>[7, 8, 9]);
    },
  );

  test('clearAppCache succeeds when images cache does not exist', () async {
    await clearAppCache();

    final appFolder = p.join(tempDir.path, AppConstants.folder);
    expect(await Directory(p.join(appFolder, 'images')).exists(), isFalse);
  });
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}
