@Tags(['unit'])
library;

import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/storage/allusion_index_cache_io.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late Directory temp;
  late Uint8List first;
  late Uint8List second;

  setUp(() async {
    temp = await Directory.systemTemp.createTemp('revelation-index-test-');
    final original = PathProviderPlatform.instance;
    PathProviderPlatform.instance = _CacheLocation(temp.path);
    addTearDown(() async {
      PathProviderPlatform.instance = original;
      await temp.delete(recursive: true);
    });
    first = Uint8List.fromList([1, 2, 3]);
    second = Uint8List.fromList([5, 8, 13, 21, 34]);
  });

  test(
    'replacing an index leaves one complete version in the application cache',
    () async {
      expect(await readCachedAllusionIndex(), isNull);
      await writeCachedAllusionIndex(first);
      expect(await readCachedAllusionIndex(), orderedEquals(first));

      await Future.wait([
        writeCachedAllusionIndex(first),
        writeCachedAllusionIndex(second),
      ]);
      expect(
        await readCachedAllusionIndex(),
        anyOf(orderedEquals(first), orderedEquals(second)),
      );
      await writeCachedAllusionIndex(second);
      expect(await readCachedAllusionIndex(), orderedEquals(second));
      final contents = await temp.list().toList();
      expect(contents.single, isA<File>());
    },
  );

  test(
    'replaces the cached index after Windows releases an open file',
    () async {
      await writeCachedAllusionIndex(first);
      final file = (await temp.list().single) as File;
      final reader = await file.open();
      final replacement = writeCachedAllusionIndex(second);
      try {
        await expectLater(
          replacement.timeout(const Duration(milliseconds: 60)),
          throwsA(isA<TimeoutException>()),
        );
        expect(await reader.read(first.length), orderedEquals(first));
      } finally {
        await reader.close();
      }
      await replacement;
      expect(await readCachedAllusionIndex(), orderedEquals(second));
      expect(await temp.list().length, 1);
    },
    testOn: 'windows',
  );

  test(
    'a blocked replacement leaves the previous cache and removes its draft',
    () async {
      await writeCachedAllusionIndex(first);
      final file = (await temp.list().single) as File;
      final reader = await file.open();
      try {
        await expectLater(
          writeCachedAllusionIndex(second),
          throwsA(isA<FileSystemException>()),
        );
      } finally {
        await reader.close();
      }

      expect(await readCachedAllusionIndex(), orderedEquals(first));
      expect(await temp.list().length, 1);
      await writeCachedAllusionIndex(second);
      expect(await readCachedAllusionIndex(), orderedEquals(second));
    },
    testOn: 'windows',
  );
}

class _CacheLocation extends PathProviderPlatform {
  _CacheLocation(this.path);
  final String path;

  @override
  Future<String?> getApplicationCachePath() async => path;
}
