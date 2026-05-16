import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:path/path.dart' as p;
import 'package:revelation/features/primary_sources/application/services/primary_source_word_crop_persistent_store.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';

typedef PrimarySourceWordCropAppFolderProvider = Future<String> Function();

PrimarySourceWordCropPersistentStore
createPrimarySourceWordCropPersistentStore() {
  return FilePrimarySourceWordCropPersistentStore();
}

class FilePrimarySourceWordCropPersistentStore
    implements PrimarySourceWordCropPersistentStore {
  FilePrimarySourceWordCropPersistentStore({
    PrimarySourceWordCropAppFolderProvider? appFolderProvider,
  }) : _appFolderProvider = appFolderProvider ?? getAppFolder;

  static const imagesFolder = 'images';
  static const wordCropsFolder = 'primary_source_words';

  final PrimarySourceWordCropAppFolderProvider _appFolderProvider;

  @override
  Future<Uint8List?> read(String key) async {
    try {
      final file = await _fileForKey(key);
      if (!await file.exists()) {
        return null;
      }
      final bytes = await file.readAsBytes();
      if (bytes.isEmpty) {
        await file.delete();
        return null;
      }
      return bytes;
    } catch (_) {
      return null;
    }
  }

  @override
  Future<void> write(String key, Uint8List bytes) async {
    if (bytes.isEmpty) {
      return;
    }
    try {
      final file = await _fileForKey(key);
      await file.create(recursive: true);
      await file.writeAsBytes(bytes);
    } catch (_) {
      return;
    }
  }

  Future<File> _fileForKey(String key) async {
    final appFolder = await _appFolderProvider();
    return File(
      p.join(
        appFolder,
        imagesFolder,
        wordCropsFolder,
        '${_stableHash(key)}.png',
      ),
    );
  }
}

String _stableHash(String value) {
  var hash = 0xcbf29ce484222325;
  for (final byte in utf8.encode(value)) {
    hash ^= byte;
    hash = (hash * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF;
  }
  return hash.toRadixString(16).padLeft(16, '0');
}
