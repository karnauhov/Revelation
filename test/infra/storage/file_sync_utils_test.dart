import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  late PathProviderPlatform previous;
  late Directory tempDir;
  late _FakeStorageServer storageServer;

  setUpAll(() async {
    storageServer = await _FakeStorageServer.start();
  });

  tearDownAll(() async {
    await _disposeSupabaseIfInitialized();
    await storageServer.close();
  });

  setUp(() async {
    await _disposeSupabaseIfInitialized();
    previous = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp('revelation_test');
    PathProviderPlatform.instance = _FakePathProviderPlatform(tempDir.path);
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    await GetIt.I.reset();
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

  test(
    'isUpdateNeeded returns false when server metadata cannot be fetched',
    () async {
      final appFolder = await getAppFolder();
      final file = File(p.join(appFolder, 'db', 'local.sqlite'));
      await file.create(recursive: true);
      await file.writeAsString('data');

      final needed = await isUpdateNeeded('db', 'local.sqlite');

      expect(needed, isFalse);
    },
  );

  test('isUpdateNeeded returns true when local file is missing', () async {
    final needed = await isUpdateNeeded('db', 'missing.sqlite');

    expect(needed, isTrue);
  });

  test(
    'updateLocalFile returns path and keeps existing file when download failed',
    () async {
      final appFolder = await getAppFolder();
      final file = File(p.join(appFolder, 'db', 'local.sqlite'));
      await file.create(recursive: true);
      await file.writeAsString('before');

      final path = await updateLocalFile('db', 'local.sqlite');

      expect(path, file.path);
      expect(await file.readAsString(), 'before');
    },
  );

  test(
    'updateLocalFile returns target path even when source is missing remotely',
    () async {
      final appFolder = await getAppFolder();

      final path = await updateLocalFile('db', 'missing.sqlite');

      expect(path, p.join(appFolder, 'db', 'missing.sqlite'));
      expect(File(path).existsSync(), isFalse);
    },
  );

  test('isUpdateNeeded compares local and server timestamps', () async {
    await _initializeSupabase(storageServer.baseUrl);
    storageServer.seedFile(
      repository: 'db',
      path: 'versioned.sqlite',
      bytes: const [1, 2, 3],
      lastModified: DateTime.utc(2026, 3, 21, 12, 0, 0),
    );

    final appFolder = await getAppFolder();
    final file = File(p.join(appFolder, 'db', 'versioned.sqlite'));
    await file.create(recursive: true);
    await file.writeAsString('old');

    await file.setLastModified(DateTime.utc(2026, 3, 21, 11, 0, 0));
    final shouldUpdate = await isUpdateNeeded('db', 'versioned.sqlite');

    await file.setLastModified(DateTime.utc(2026, 3, 21, 13, 0, 0));
    final shouldSkip = await isUpdateNeeded('db', 'versioned.sqlite');

    expect(shouldUpdate, isTrue);
    expect(shouldSkip, isFalse);
  });

  test(
    'updateLocalFile downloads bytes and overwrites existing file',
    () async {
      await _initializeSupabase(storageServer.baseUrl);
      storageServer.seedFile(
        repository: 'db',
        path: 'sync.sqlite',
        bytes: const [10, 11, 12, 13],
        lastModified: DateTime.utc(2026, 3, 21, 12, 0, 0),
      );

      final appFolder = await getAppFolder();
      final file = File(p.join(appFolder, 'db', 'sync.sqlite'));
      await file.create(recursive: true);
      await file.writeAsBytes(const [99, 99]);

      final path = await updateLocalFile('db', 'sync.sqlite');

      expect(path, file.path);
      expect(await file.readAsBytes(), [10, 11, 12, 13]);
    },
  );

  test('updateLocalFile creates a new file when download succeeds', () async {
    await _initializeSupabase(storageServer.baseUrl);
    storageServer.seedFile(
      repository: 'db',
      path: 'fresh.sqlite',
      bytes: const [21, 22],
      lastModified: DateTime.utc(2026, 3, 21, 12, 0, 0),
    );

    final path = await updateLocalFile('db', 'fresh.sqlite');

    expect(File(path).existsSync(), isTrue);
    expect(await File(path).readAsBytes(), [21, 22]);
  });

  test(
    'getLastUpdateFileLocal returns null when path provider throws',
    () async {
      PathProviderPlatform.instance = _ThrowingPathProviderPlatform();

      final updated = await getLastUpdateFileLocal('db', 'local.sqlite');

      expect(updated, isNull);
    },
  );
}

Future<void> _initializeSupabase(String url) async {
  await _disposeSupabaseIfInitialized();
  await Supabase.initialize(
    url: url,
    anonKey: 'test-anon-key',
    authOptions: FlutterAuthClientOptions(
      localStorage: const EmptyLocalStorage(),
      pkceAsyncStorage: _InMemoryGotrueAsyncStorage(),
    ),
  );
}

Future<void> _disposeSupabaseIfInitialized() async {
  try {
    await Supabase.instance.dispose();
  } catch (_) {}
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}

class _ThrowingPathProviderPlatform extends PathProviderPlatform {
  @override
  Future<String?> getApplicationDocumentsPath() async {
    throw Exception('documents unavailable');
  }
}

class _FakeStorageServer {
  _FakeStorageServer._(this._server)
    : baseUrl = 'http://${_server.address.address}:${_server.port}' {
    _server.listen(_handleRequest);
  }

  final HttpServer _server;
  final String baseUrl;
  final Map<String, Uint8List> _files = <String, Uint8List>{};
  final Map<String, DateTime> _modifiedByFile = <String, DateTime>{};

  static Future<_FakeStorageServer> start() async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    return _FakeStorageServer._(server);
  }

  Future<void> close() => _server.close(force: true);

  void seedFile({
    required String repository,
    required String path,
    required List<int> bytes,
    required DateTime lastModified,
  }) {
    final key = '$repository/$path';
    _files[key] = Uint8List.fromList(bytes);
    _modifiedByFile[key] = lastModified.toUtc();
  }

  Future<void> _handleRequest(HttpRequest request) async {
    final segments = request.uri.pathSegments;
    if (segments.length < 4 ||
        segments[0] != 'storage' ||
        segments[1] != 'v1' ||
        segments[2] != 'object') {
      request.response.statusCode = HttpStatus.notFound;
      await request.response.close();
      return;
    }

    if (segments[3] == 'info' && segments.length >= 6) {
      await _handleInfoRequest(request, segments);
      return;
    }

    if (segments.length >= 5) {
      await _handleDownloadRequest(request, segments);
      return;
    }

    request.response.statusCode = HttpStatus.notFound;
    await request.response.close();
  }

  Future<void> _handleInfoRequest(
    HttpRequest request,
    List<String> segments,
  ) async {
    final repository = segments[4];
    final filePath = segments.sublist(5).join('/');
    final key = '$repository/$filePath';
    final modified = _modifiedByFile[key];
    final bytes = _files[key];
    if (modified == null || bytes == null) {
      request.response.statusCode = HttpStatus.notFound;
      await request.response.close();
      return;
    }

    request.response.statusCode = HttpStatus.ok;
    request.response.headers.contentType = ContentType.json;
    request.response.write(
      jsonEncode(<String, Object?>{
        'id': 'id-$filePath',
        'version': 'v1',
        'name': filePath,
        'bucket_id': repository,
        'updated_at': modified.toIso8601String(),
        'created_at': modified.toIso8601String(),
        'last_accessed_at': null,
        'size': bytes.length,
        'cache_control': null,
        'content_type': 'application/octet-stream',
        'etag': 'etag-$filePath',
        'last_modified': modified.toIso8601String(),
        'metadata': <String, Object?>{},
      }),
    );
    await request.response.close();
  }

  Future<void> _handleDownloadRequest(
    HttpRequest request,
    List<String> segments,
  ) async {
    final repository = segments[3];
    final filePath = segments.sublist(4).join('/');
    final key = '$repository/$filePath';
    final bytes = _files[key];
    if (bytes == null) {
      request.response.statusCode = HttpStatus.notFound;
      await request.response.close();
      return;
    }

    request.response.statusCode = HttpStatus.ok;
    request.response.add(bytes);
    await request.response.close();
  }
}

class _InMemoryGotrueAsyncStorage extends GotrueAsyncStorage {
  final Map<String, String> _data = <String, String>{};

  @override
  Future<String?> getItem({required String key}) async => _data[key];

  @override
  Future<void> removeItem({required String key}) async {
    _data.remove(key);
  }

  @override
  Future<void> setItem({required String key, required String value}) async {
    _data[key] = value;
  }
}
