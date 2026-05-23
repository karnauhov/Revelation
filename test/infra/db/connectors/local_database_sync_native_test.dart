import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/infra/db/connectors/database_version_file_loader.dart';
import 'package:revelation/infra/db/connectors/local_database_sync_native.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:sqlite3/sqlite3.dart';
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
    tempDir = await Directory.systemTemp.createTemp('revelation_db_sync_test');
    PathProviderPlatform.instance = _FakePathProviderPlatform(tempDir.path);
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    storageServer.clear();
    await _initializeSupabase(storageServer.baseUrl);
  });

  tearDown(() async {
    await GetIt.I.reset();
    PathProviderPlatform.instance = previous;
    await tempDir.delete(recursive: true);
  });

  test(
    'keeps newer local database and manifest when remote manifest is older',
    () async {
      final appFolder = await getAppFolder();
      final dbFile = File(p.join(appFolder, 'db', AppConstants.commonDB));
      final manifestFile = File(p.join(appFolder, 'db', 'manifest.json'));
      await _writeDatabaseFile(
        dbFile,
        schemaVersion: 4,
        dataVersion: 7,
        date: '2026-05-23T17:55:51Z',
        payloadBytes: 25000,
      );
      await manifestFile.create(recursive: true);
      await manifestFile.writeAsBytes(
        _manifestBytes({
          AppConstants.commonDB: _ManifestEntry(
            schemaVersion: 4,
            dataVersion: 7,
            date: '2026-05-23T17:55:51Z',
            fileSizeBytes: dbFile.lengthSync(),
          ),
        }),
      );

      final oldRemoteBytes = await _databaseBytes(
        schemaVersion: 4,
        dataVersion: 6,
        date: '2026-05-23T02:35:34Z',
        payloadBytes: 1000,
      );
      storageServer.seedFile(
        repository: 'db',
        path: AppConstants.commonDB,
        bytes: oldRemoteBytes,
      );
      storageServer.seedFile(
        repository: 'db',
        path: 'manifest.json',
        bytes: _manifestBytes({
          AppConstants.commonDB: _ManifestEntry(
            schemaVersion: 4,
            dataVersion: 6,
            date: '2026-05-23T02:35:34Z',
            fileSizeBytes: oldRemoteBytes.length,
          ),
        }),
      );

      final result = await verifyAndUpdateLocalDatabaseFileWithResult(
        AppConstants.commonDB,
      );

      final localVersion = loadDatabaseVersionInfoFromFile(dbFile)!;
      final manifestEntry = parseWebDbManifestEntries(
        await manifestFile.readAsString(),
      )[AppConstants.commonDB]!;
      expect(result.updated, isFalse);
      expect(localVersion.dataVersion, 7);
      expect(manifestEntry.versionInfo.dataVersion, 7);
      expect(dbFile.lengthSync(), isNot(oldRemoteBytes.length));
    },
  );

  test('updates local database when remote manifest is newer', () async {
    final appFolder = await getAppFolder();
    final dbFile = File(p.join(appFolder, 'db', AppConstants.commonDB));
    final manifestFile = File(p.join(appFolder, 'db', 'manifest.json'));
    await _writeDatabaseFile(
      dbFile,
      schemaVersion: 4,
      dataVersion: 6,
      date: '2026-05-23T02:35:34Z',
      payloadBytes: 1000,
    );
    await manifestFile.create(recursive: true);
    await manifestFile.writeAsBytes(
      _manifestBytes({
        AppConstants.commonDB: _ManifestEntry(
          schemaVersion: 4,
          dataVersion: 6,
          date: '2026-05-23T02:35:34Z',
          fileSizeBytes: dbFile.lengthSync(),
        ),
      }),
    );

    final newRemoteBytes = await _databaseBytes(
      schemaVersion: 4,
      dataVersion: 7,
      date: '2026-05-23T17:55:51Z',
      payloadBytes: 25000,
    );
    storageServer.seedFile(
      repository: 'db',
      path: AppConstants.commonDB,
      bytes: newRemoteBytes,
    );
    storageServer.seedFile(
      repository: 'db',
      path: 'manifest.json',
      bytes: _manifestBytes({
        AppConstants.commonDB: _ManifestEntry(
          schemaVersion: 4,
          dataVersion: 7,
          date: '2026-05-23T17:55:51Z',
          fileSizeBytes: newRemoteBytes.length,
        ),
      }),
    );

    final result = await verifyAndUpdateLocalDatabaseFileWithResult(
      AppConstants.commonDB,
    );

    final localVersion = loadDatabaseVersionInfoFromFile(dbFile)!;
    final manifestEntry = parseWebDbManifestEntries(
      await manifestFile.readAsString(),
    )[AppConstants.commonDB]!;
    expect(result.updated, isTrue);
    expect(localVersion.dataVersion, 7);
    expect(manifestEntry.versionInfo.dataVersion, 7);
    expect(await dbFile.readAsBytes(), newRemoteBytes);
  });
}

Future<void> _writeDatabaseFile(
  File file, {
  required int schemaVersion,
  required int dataVersion,
  required String date,
  required int payloadBytes,
}) async {
  await file.parent.create(recursive: true);
  if (file.existsSync()) {
    await file.delete();
  }
  final database = sqlite3.open(file.path);
  try {
    database.execute('PRAGMA user_version = $schemaVersion');
    database.execute(
      'CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)',
    );
    database.execute(
      'INSERT INTO db_metadata(key, value) VALUES (?, ?), (?, ?), (?, ?)',
      [
        'schema_version',
        schemaVersion.toString(),
        'data_version',
        dataVersion.toString(),
        'date',
        date,
      ],
    );
    database.execute('CREATE TABLE payload(value BLOB NOT NULL)');
    database.execute('INSERT INTO payload(value) VALUES (zeroblob(?))', [
      payloadBytes,
    ]);
  } finally {
    database.dispose();
  }
}

Future<List<int>> _databaseBytes({
  required int schemaVersion,
  required int dataVersion,
  required String date,
  required int payloadBytes,
}) async {
  final tempDir = await Directory.systemTemp.createTemp('revelation_db_bytes');
  try {
    final file = File(p.join(tempDir.path, 'db.sqlite'));
    await _writeDatabaseFile(
      file,
      schemaVersion: schemaVersion,
      dataVersion: dataVersion,
      date: date,
      payloadBytes: payloadBytes,
    );
    return await file.readAsBytes();
  } finally {
    await tempDir.delete(recursive: true);
  }
}

List<int> _manifestBytes(Map<String, _ManifestEntry> entries) {
  return utf8.encode(
    jsonEncode(<String, Object?>{
      'version': 1,
      'generatedAt': '2026-05-23T17:55:51Z',
      'databases': <String, Object?>{
        for (final entry in entries.entries)
          entry.key: <String, Object?>{
            'versionToken': buildWebDbManifestVersionToken(
              schemaVersion: entry.value.schemaVersion,
              dataVersion: entry.value.dataVersion,
              date: entry.value.date,
              fileSizeBytes: entry.value.fileSizeBytes,
            ),
            'schemaVersion': entry.value.schemaVersion,
            'dataVersion': entry.value.dataVersion,
            'date': entry.value.date,
            'fileSizeBytes': entry.value.fileSizeBytes,
          },
      },
    }),
  );
}

class _ManifestEntry {
  const _ManifestEntry({
    required this.schemaVersion,
    required this.dataVersion,
    required this.date,
    required this.fileSizeBytes,
  });

  final int schemaVersion;
  final int dataVersion;
  final String date;
  final int fileSizeBytes;
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

class _FakeStorageServer {
  _FakeStorageServer._(this._server)
    : baseUrl = 'http://${_server.address.address}:${_server.port}' {
    _server.listen(_handleRequest);
  }

  final HttpServer _server;
  final String baseUrl;
  final Map<String, Uint8List> _files = <String, Uint8List>{};

  static Future<_FakeStorageServer> start() async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    return _FakeStorageServer._(server);
  }

  Future<void> close() => _server.close(force: true);

  void clear() {
    _files.clear();
  }

  void seedFile({
    required String repository,
    required String path,
    required List<int> bytes,
  }) {
    _files['$repository/$path'] = Uint8List.fromList(bytes);
  }

  Future<void> _handleRequest(HttpRequest request) async {
    final segments = request.uri.pathSegments;
    if (segments.length < 5 ||
        segments[0] != 'storage' ||
        segments[1] != 'v1' ||
        segments[2] != 'object') {
      request.response.statusCode = HttpStatus.notFound;
      await request.response.close();
      return;
    }

    final repository = segments[3];
    final filePath = segments.sublist(4).join('/');
    final bytes = _files['$repository/$filePath'];
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
