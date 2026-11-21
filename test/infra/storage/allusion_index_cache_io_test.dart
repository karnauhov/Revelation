@Tags(['unit'])
library;

import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/storage/allusion_index_cache_io.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test(
    'replacing an index leaves one complete version in the application cache',
    () async {
      final temp = await Directory.systemTemp.createTemp(
        'revelation-index-test-',
      );
      final original = PathProviderPlatform.instance;
      PathProviderPlatform.instance = _CacheLocation(temp.path);
      addTearDown(() async {
        PathProviderPlatform.instance = original;
        await temp.delete(recursive: true);
      });

      expect(await readCachedAllusionIndex(), isNull);
      final first = Uint8List.fromList([1, 2, 3]);
      final second = Uint8List.fromList([5, 8, 13, 21, 34]);
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
}

class _CacheLocation extends PathProviderPlatform {
  _CacheLocation(this.path);
  final String path;

  @override
  Future<String?> getApplicationCachePath() async => path;
}
