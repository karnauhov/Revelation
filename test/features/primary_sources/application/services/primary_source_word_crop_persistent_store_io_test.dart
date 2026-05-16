import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/features/primary_sources/application/services/primary_source_word_crop_persistent_store_io.dart';

void main() {
  test('file store writes crops under revelation images folder', () async {
    final tempDir = await Directory.systemTemp.createTemp(
      'word_crop_cache_test_',
    );
    addTearDown(() async {
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    final appFolder = p.join(tempDir.path, 'revelation');
    final store = FilePrimarySourceWordCropPersistentStore(
      appFolderProvider: () async => appFolder,
    );
    final bytes = Uint8List.fromList(<int>[1, 2, 3, 4]);

    await store.write('v4|source:01|page/325v|word?1', bytes);

    final cacheDir = Directory(
      p.join(appFolder, 'images', 'primary_source_words'),
    );
    final files = (await cacheDir.list().toList()).whereType<File>().toList();

    expect(await cacheDir.exists(), isTrue);
    expect(files, hasLength(1));
    expect(p.extension(files.single.path), '.png');
    expect(
      await store.read('v4|source:01|page/325v|word?1'),
      orderedEquals(bytes),
    );
    expect(await store.read('missing'), isNull);
  });
}
