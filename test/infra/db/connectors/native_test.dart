import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';

import 'package:drift/native.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/connectors/native.dart' as native_connector;
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  late PathProviderPlatform previousPathProvider;
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
    previousPathProvider = PathProviderPlatform.instance;
    tempDir = await Directory.systemTemp.createTemp('native_connector_test_');
    PathProviderPlatform.instance = _FakePathProviderPlatform(tempDir.path);

    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    await _disposeSupabaseIfInitialized();
    await GetIt.I.reset();
    PathProviderPlatform.instance = previousPathProvider;
    await tempDir.delete(recursive: true);
  });

  test('getCommonDB and getLocalizedDB open database instances', () async {
    final common = native_connector.getCommonDB();
    final localized = native_connector.getLocalizedDB('en');
    addTearDown(common.close);
    addTearDown(localized.close);

    final commonValue = await common
        .customSelect('SELECT 1 as value')
        .getSingle();
    final localizedValue = await localized
        .customSelect('SELECT 1 as value')
        .getSingle();

    expect(commonValue.read<int>('value'), 1);
    expect(localizedValue.read<int>('value'), 1);
  });

  test(
    'getLocalDatabaseUpdatedAt and getLocalDatabaseFileSize read file state',
    () async {
      final appFolder = await getAppFolder();
      final dbFile = File(p.join(appFolder, 'db', 'test.sqlite'));
      await dbFile.create(recursive: true);
      await dbFile.writeAsBytes(List<int>.generate(32, (index) => index));

      final updatedAt = await native_connector.getLocalDatabaseUpdatedAt(
        'test.sqlite',
      );
      final size = await native_connector.getLocalDatabaseFileSize(
        'test.sqlite',
      );

      expect(updatedAt, isNotNull);
      expect(size, 32);
      expect(
        await native_connector.getLocalDatabaseFileSize('missing.sqlite'),
        isNull,
      );
    },
  );

  test(
    'getLocalDatabaseVersionInfo returns null for missing DB file',
    () async {
      final info = await native_connector.getLocalDatabaseVersionInfo(
        'missing.sqlite',
      );
      expect(info, isNull);
    },
  );

  test(
    'getLocalDatabaseVersionInfo loads metadata for common and localized DBs',
    () async {
      final appFolder = await getAppFolder();
      final dbDir = Directory(p.join(appFolder, 'db'));
      await dbDir.create(recursive: true);

      final commonFile = File(p.join(dbDir.path, AppConstants.commonDB));
      final commonDb = CommonDB(NativeDatabase(commonFile));
      await commonDb.customStatement('''
      INSERT OR REPLACE INTO db_metadata(key, value) VALUES
        ('schema_version', '4'),
        ('data_version', '13'),
        ('date', '2026-03-21T10:00:00.000Z')
      ''');
      await commonDb.close();

      final localizedFile = File(
        p.join(dbDir.path, AppConstants.localizedDB.replaceAll('@loc', 'en')),
      );
      final localizedDb = LocalizedDB(NativeDatabase(localizedFile));
      await localizedDb.customStatement('''
      INSERT OR REPLACE INTO db_metadata(key, value) VALUES
        ('schema_version', '6'),
        ('data_version', '8'),
        ('date', '2026-03-21T11:00:00.000Z')
      ''');
      await localizedDb.close();

      final commonInfo = await native_connector.getLocalDatabaseVersionInfo(
        AppConstants.commonDB,
      );
      final localizedInfo = await native_connector.getLocalDatabaseVersionInfo(
        AppConstants.localizedDB.replaceAll('@loc', 'en'),
      );

      expect(commonInfo, isNotNull);
      expect(commonInfo!.schemaVersion, 4);
      expect(commonInfo.dataVersion, 13);
      expect(commonInfo.date.toUtc(), DateTime.utc(2026, 3, 21, 10, 0, 0));

      expect(localizedInfo, isNotNull);
      expect(localizedInfo!.schemaVersion, 6);
      expect(localizedInfo.dataVersion, 8);
      expect(localizedInfo.date.toUtc(), DateTime.utc(2026, 3, 21, 11, 0, 0));
    },
  );

  test(
    'getLocalPrimarySourceFilesInfo returns empty list when primary_sources folder is missing',
    () async {
      final files = await native_connector.getLocalPrimarySourceFilesInfo();

      expect(files, isEmpty);
    },
  );

  test(
    'getLocalPrimarySourceFilesInfo lists nested files with relative paths and sizes',
    () async {
      final appFolder = await getAppFolder();
      final root = Directory(p.join(appFolder, 'primary_sources'));
      await Directory(p.join(root.path, 'b')).create(recursive: true);
      await Directory(p.join(root.path, 'a')).create(recursive: true);
      final first = File(p.join(root.path, 'b', 'file2.txt'));
      final second = File(p.join(root.path, 'a', 'file1.txt'));
      await first.writeAsBytes(const [1, 2, 3, 4]);
      await second.writeAsBytes(const [5, 6]);

      final files = await native_connector.getLocalPrimarySourceFilesInfo();

      expect(files.map((e) => e.relativePath).toList(), [
        'primary_sources/a/file1.txt',
        'primary_sources/b/file2.txt',
      ]);
      expect(files.map((e) => e.sizeBytes).toList(), [2, 4]);
      expect(files.every((e) => e.error == null), isTrue);
    },
  );

  test(
    'getLocalPrimarySourceFilesInfo tolerates links removed during traversal',
    () async {
      final appFolder = await getAppFolder();
      final root = Directory(p.join(appFolder, 'primary_sources'));
      await root.create(recursive: true);
      final stableFile = File(p.join(root.path, 'stable.txt'));
      await stableFile.writeAsBytes(const [7]);

      final targetDir = Directory(p.join(appFolder, 'volatile_target'));
      await targetDir.create(recursive: true);
      await File(
        p.join(targetDir.path, 'target_file.txt'),
      ).writeAsBytes(const [1, 2, 3]);

      final volatileLink = Link(p.join(root.path, '000_volatile_link'));
      final linkCreated = await _tryCreateLink(volatileLink, targetDir.path);
      if (!linkCreated) {
        return;
      }

      for (var i = 0; i < 800; i++) {
        final file = File(p.join(root.path, 'file_$i.tmp'));
        await file.writeAsBytes(const [0]);
      }

      final deleteFuture = Future<void>(() async {
        await Future<void>.delayed(const Duration(milliseconds: 1));
        if (await volatileLink.exists()) {
          await volatileLink.delete();
        }
      });

      final files = await native_connector.getLocalPrimarySourceFilesInfo();
      await deleteFuture;

      if (await targetDir.exists()) {
        await targetDir.delete(recursive: true);
      }

      expect(
        files.any(
          (file) =>
              file.relativePath == 'primary_sources/stable.txt' &&
              file.sizeBytes == 1 &&
              file.error == null,
        ),
        isTrue,
      );
    },
  );

  test(
    'getLocalPrimarySourceFilesInfo follows symlinked file and directory when supported',
    () async {
      final appFolder = await getAppFolder();
      final root = Directory(p.join(appFolder, 'primary_sources'));
      await root.create(recursive: true);
      final realDir = Directory(p.join(appFolder, 'symlink_target'));
      await realDir.create(recursive: true);
      final realFile = File(p.join(realDir.path, 'real.txt'));
      await realFile.writeAsBytes(const [1, 2, 3]);

      final fileLink = Link(p.join(root.path, 'file_link.txt'));
      final dirLink = Link(p.join(root.path, 'dir_link'));
      final fileLinkCreated = await _tryCreateLink(fileLink, realFile.path);
      final dirLinkCreated = await _tryCreateLink(dirLink, realDir.path);
      if (!fileLinkCreated || !dirLinkCreated) {
        return;
      }

      final files = await native_connector.getLocalPrimarySourceFilesInfo();
      expect(files.any((f) => f.sizeBytes == 3), isTrue);
      expect(files.length, lessThan(10));
      expect(
        files.any(
          (f) =>
              f.relativePath.contains('file_link.txt') ||
              f.relativePath.contains('dir_link') ||
              f.relativePath.contains('symlink_target'),
        ),
        isTrue,
      );
    },
  );

  test(
    'getLocalPrimarySourceFilesInfo reports unreadable link target when supported',
    () async {
      final appFolder = await getAppFolder();
      final root = Directory(p.join(appFolder, 'primary_sources'));
      await root.create(recursive: true);
      final brokenLink = Link(p.join(root.path, 'missing_link'));
      final created = await _tryCreateLink(
        brokenLink,
        p.join(root.path, 'missing_target'),
      );
      if (!created) {
        return;
      }

      final files = await native_connector.getLocalPrimarySourceFilesInfo();
      final linkInfo = files
          .where((f) => f.relativePath.endsWith('missing_link'))
          .toList();
      if (linkInfo.isEmpty) {
        return;
      }

      expect(linkInfo.single.error, isNotNull);
    },
  );

  test(
    'getLazyDatabase uses existing local file path when update is not needed',
    () async {
      final dbName = 'lazy_existing.sqlite';
      final appFolder = await getAppFolder();
      final file = File(p.join(appFolder, 'db', dbName));
      await _createValidCommonDbAt(file);

      final db = CommonDB(native_connector.getLazyDatabase(dbName));
      addTearDown(db.close);

      final rows = await db.customSelect('SELECT 1 AS value').get();
      expect(rows.single.read<int>('value'), 1);
      expect(file.existsSync(), isTrue);
    },
  );

  test(
    'getLocalPrimarySourceFilesInfo returns contract error item when app folder fails',
    () async {
      PathProviderPlatform.instance = _ThrowingPathProviderPlatform(
        Exception('documents unavailable'),
      );

      final files = await native_connector.getLocalPrimarySourceFilesInfo();

      expect(files, hasLength(1));
      expect(files.single.relativePath, 'primary_sources');
      expect(files.single.error, contains('list failed:'));
    },
  );

  test(
    'getLazyDatabase downloads db file when server has newer version',
    () async {
      await _initializeSupabase(storageServer.baseUrl);
      final seededBytes = await _createValidCommonDbBytes();
      storageServer.seedFile(
        repository: 'db',
        path: 'lazy_download.sqlite',
        bytes: seededBytes,
        lastModified: DateTime.utc(2026, 3, 21, 12, 0, 0),
      );

      final dbName = 'lazy_download.sqlite';
      final db = CommonDB(native_connector.getLazyDatabase(dbName));
      addTearDown(db.close);

      final rows = await db.customSelect('SELECT 1 AS value').get();
      expect(rows.single.read<int>('value'), 1);

      final appFolder = await getAppFolder();
      final file = File(p.join(appFolder, 'db', dbName));
      expect(file.existsSync(), isTrue);
      expect(await file.readAsBytes(), seededBytes);
    },
  );

  test(
    'getLazyDatabase rethrows when file system path cannot be resolved',
    () async {
      PathProviderPlatform.instance = _ThrowingPathProviderPlatform(
        Exception('documents unavailable'),
      );
      final db = CommonDB(native_connector.getLazyDatabase('broken.sqlite'));
      addTearDown(() async {
        try {
          await db.close();
        } catch (_) {}
      });

      expect(db.customSelect('SELECT 1').get(), throwsA(anything));
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

Future<bool> _tryCreateLink(Link link, String target) async {
  try {
    await link.create(target);
    return true;
  } on FileSystemException {
    return false;
  } on UnsupportedError {
    return false;
  }
}

Future<void> _createValidCommonDbAt(File file) async {
  await file.parent.create(recursive: true);
  final db = CommonDB(NativeDatabase(file));
  try {
    await db.customSelect('SELECT 1 AS value').getSingle();
  } finally {
    await db.close();
  }
}

Future<List<int>> _createValidCommonDbBytes() async {
  final tempDir = await Directory.systemTemp.createTemp(
    'native_connector_seed_db_',
  );
  try {
    final file = File(p.join(tempDir.path, 'seed.sqlite'));
    await _createValidCommonDbAt(file);
    return await file.readAsBytes();
  } finally {
    await tempDir.delete(recursive: true);
  }
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.path);

  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}

class _ThrowingPathProviderPlatform extends PathProviderPlatform {
  _ThrowingPathProviderPlatform(this.error);

  final Object error;

  @override
  Future<String?> getApplicationDocumentsPath() async =>
      Future<String?>.error(error);
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
