import 'dart:typed_data';

class FakeRemoteStorage {
  final Map<String, Uint8List> _storage = <String, Uint8List>{};

  void addFile(String bucket, String path, List<int> bytes) {
    _storage[_key(bucket, path)] = Uint8List.fromList(bytes);
  }

  Future<Uint8List?> download(String bucket, String path) async {
    return _storage[_key(bucket, path)];
  }

  bool contains(String bucket, String path) {
    return _storage.containsKey(_key(bucket, path));
  }

  String _key(String bucket, String path) => '$bucket/$path';
}
