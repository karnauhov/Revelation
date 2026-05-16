import 'dart:typed_data';

abstract class PrimarySourceWordCropPersistentStore {
  Future<Uint8List?> read(String key);

  Future<void> write(String key, Uint8List bytes);
}

class NoopPrimarySourceWordCropPersistentStore
    implements PrimarySourceWordCropPersistentStore {
  const NoopPrimarySourceWordCropPersistentStore();

  @override
  Future<Uint8List?> read(String key) async => null;

  @override
  Future<void> write(String key, Uint8List bytes) async {}
}
