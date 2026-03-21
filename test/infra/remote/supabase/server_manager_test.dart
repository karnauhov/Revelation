import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/infra/remote/supabase/server_manager.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  test('ServerManager factory returns singleton', () {
    expect(identical(ServerManager(), ServerManager()), isTrue);
  });

  test(
    'init returns false when SUPABASE compile-time defines are absent',
    () async {
      await _disposeSupabaseIfInitialized();
      final manager = ServerManager();

      final initialized = await manager.init();

      expect(initialized, isFalse);
    },
  );

  test('downloadImage returns null for malformed page', () async {
    await _disposeSupabaseIfInitialized();
    final manager = ServerManager();

    final result = await manager.downloadImage('no-slash', false);

    expect(result, isNull);
  });

  test('downloadDB returns null when supabase is not initialized', () async {
    await _disposeSupabaseIfInitialized();
    final manager = ServerManager();

    final result = await manager.downloadDB('repo', 'file.sqlite');

    expect(result, isNull);
  });

  test(
    'getLastUpdateFileFromServer returns null when not initialized',
    () async {
      await _disposeSupabaseIfInitialized();
      final manager = ServerManager();

      final result = await manager.getLastUpdateFileFromServer('repo', 'file');

      expect(result, isNull);
    },
  );

  group('with initialized supabase storage', () {
    late _FakeStorageServer storageServer;

    setUpAll(() async {
      storageServer = await _FakeStorageServer.start();
      await _disposeSupabaseIfInitialized();
      await Supabase.initialize(
        url: storageServer.baseUrl,
        anonKey: 'test-anon-key',
        authOptions: FlutterAuthClientOptions(
          localStorage: const EmptyLocalStorage(),
          pkceAsyncStorage: _InMemoryGotrueAsyncStorage(),
        ),
      );
    });

    tearDownAll(() async {
      await _disposeSupabaseIfInitialized();
      await storageServer.close();
    });

    test(
      'downloadDB returns bytes and removes problematic storage header',
      () async {
        storageServer.seedFile(
          repository: 'repo',
          path: 'file.sqlite',
          bytes: const [1, 2, 3, 4],
          lastModified: DateTime.utc(2026, 3, 21, 12, 0, 0),
        );
        final manager = ServerManager();
        Supabase
                .instance
                .client
                .storage
                .headers['X-Supabase-Client-Platform-Version'] =
            'кириллица';

        final bytes = await manager.downloadDB('repo', 'file.sqlite');

        expect(bytes, Uint8List.fromList(const [1, 2, 3, 4]));
        expect(
          Supabase.instance.client.storage.headers.containsKey(
            'X-Supabase-Client-Platform-Version',
          ),
          isFalse,
        );
      },
    );

    test('downloadImage resolves desktop and mobile-browser paths', () async {
      storageServer.seedFile(
        repository: 'repo',
        path: 'folder/image.png',
        bytes: const [10],
        lastModified: DateTime.utc(2026, 3, 21, 12, 0, 0),
      );
      storageServer.seedFile(
        repository: 'repo',
        path: 'folder/image_mb.png',
        bytes: const [20],
        lastModified: DateTime.utc(2026, 3, 21, 12, 1, 0),
      );
      storageServer.seedFile(
        repository: 'repo',
        path: 'folder/image_mb',
        bytes: const [30],
        lastModified: DateTime.utc(2026, 3, 21, 12, 2, 0),
      );
      final manager = ServerManager();

      final desktop = await manager.downloadImage(
        'repo/folder/image.png',
        false,
      );
      final mobileWithExtension = await manager.downloadImage(
        'repo/folder/image.png',
        true,
      );
      final mobileWithoutExtension = await manager.downloadImage(
        'repo/folder/image',
        true,
      );

      expect(desktop, Uint8List.fromList(const [10]));
      expect(mobileWithExtension, Uint8List.fromList(const [20]));
      expect(mobileWithoutExtension, Uint8List.fromList(const [30]));
    });

    test('getLastUpdateFileFromServer returns parsed timestamp', () async {
      final modifiedAt = DateTime.utc(2026, 3, 21, 12, 34, 56);
      storageServer.seedFile(
        repository: 'repo',
        path: 'updates.sqlite',
        bytes: const [7, 8],
        lastModified: modifiedAt,
      );
      final manager = ServerManager();

      final updatedAt = await manager.getLastUpdateFileFromServer(
        'repo',
        'updates.sqlite',
      );

      expect(updatedAt, modifiedAt);
    });

    test(
      'downloadDB and getLastUpdateFileFromServer return null for missing files',
      () async {
        final manager = ServerManager();

        final bytes = await manager.downloadDB('repo', 'missing.sqlite');
        final updatedAt = await manager.getLastUpdateFileFromServer(
          'repo',
          'missing.sqlite',
        );

        expect(bytes, isNull);
        expect(updatedAt, isNull);
      },
    );
  });
}

Future<void> _disposeSupabaseIfInitialized() async {
  try {
    await Supabase.instance.dispose();
  } catch (_) {}
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
