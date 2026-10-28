import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/features/bible/presentation/screens/bible_screen.dart';
import 'package:revelation/infra/db/connectors/database_version_file_loader.dart';
import 'package:revelation/infra/db/connectors/local_database_sync_native.dart';
import 'package:revelation/infra/db/connectors/local_database_sync_result.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqlite3/sqlite3.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:talker_flutter/talker_flutter.dart';

const _moduleFile = 'bible_rev192.sqlite';
const _moduleDate = '2026-10-24T00:00:00Z';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('reader installs and reads a same-size module update safely', (
    tester,
  ) async {
    late _ModuleServer server;
    late Directory temp;
    late File localFile;
    late List<int> firstBytes;
    late List<int> secondBytes;
    final originalPathProvider = PathProviderPlatform.instance;
    await tester.runAsync(() async {
      temp = await Directory.systemTemp.createTemp('rev192_integration_');
      PathProviderPlatform.instance = _TemporaryDocuments(temp.path);
      await GetIt.I.reset();
      GetIt.I.registerSingleton<Talker>(
        Talker(settings: TalkerSettings(useConsoleLogs: false)),
      );
      SharedPreferences.setMockInitialValues({});
      server = await _ModuleServer.start();
      await Supabase.initialize(
        url: server.url,
        anonKey: 'local-integration-key',
        authOptions: const FlutterAuthClientOptions(
          localStorage: EmptyLocalStorage(),
        ),
      );
      localFile = File(p.join(await getAppFolder(), 'db', _moduleFile));
      firstBytes = await _moduleBytes(temp, 1, 'Original sample verse');
      secondBytes = await _moduleBytes(temp, 2, 'Replaced sample verse');
      expect(firstBytes.length, secondBytes.length);
      await localFile.parent.create(recursive: true);
      await localFile.writeAsBytes(firstBytes);
      server.publish(1, firstBytes);
    });
    try {
      await _openReader(tester, 1, 'Original sample verse');
      expect(server.moduleDownloads, 0);

      await tester.pumpWidget(const SizedBox.shrink());
      server.publish(2, secondBytes);
      await _openReader(tester, 2, 'Replaced sample verse');
      await tester.runAsync(() async {
        expect(await localFile.readAsBytes(), secondBytes);
        expect(loadDatabaseVersionInfoFromFile(localFile)!.dataVersion, 2);
      });
      expect(server.moduleDownloads, 1);

      await tester.pumpWidget(const SizedBox.shrink());
      await _openReader(tester, 3, 'Replaced sample verse');
      expect(server.moduleDownloads, 1);

      // A published manifest ahead of its object must not replace good data
      // or be reported as an installed update.
      await tester.pumpWidget(const SizedBox.shrink());
      server.publish(3, firstBytes);
      await _openReader(tester, 4, 'Replaced sample verse');
      await tester.runAsync(() async {
        final result = await verifyAndUpdateLocalDatabaseFileWithResult(
          _moduleFile,
        );
        expect(result.updated, isFalse);
        expect(result.versionMatchedManifestAfterSync, isFalse);
        expect(LocalDatabaseSyncResult(files: [result]).isUpToDate, isFalse);
        expect(await localFile.readAsBytes(), secondBytes);
        expect(loadDatabaseVersionInfoFromFile(localFile)!.dataVersion, 2);
      });

      // A directory at the cache path reproduces a real filesystem write
      // failure. The fetched manifest must still validate the installed update.
      await tester.pumpWidget(const SizedBox.shrink());
      late Directory blockedManifest;
      await tester.runAsync(() async {
        final manifestFile = File(
          p.join(localFile.parent.path, 'manifest.json'),
        );
        await manifestFile.delete();
        blockedManifest = await Directory(manifestFile.path).create();
        server.publish(
          3,
          await _moduleBytes(temp, 3, 'Recovered sample verse'),
        );
      });
      await _openReader(tester, 5, 'Recovered sample verse');
      await tester.runAsync(() async {
        expect(loadDatabaseVersionInfoFromFile(localFile)!.dataVersion, 3);
        expect(blockedManifest.existsSync(), isTrue);
        await blockedManifest.delete();
      });
      final downloadsAfterRecovery = server.moduleDownloads;
      await tester.pumpWidget(const SizedBox.shrink());
      await _openReader(tester, 6, 'Recovered sample verse');
      await tester.runAsync(() async {
        final manifestFile = File(
          p.join(localFile.parent.path, 'manifest.json'),
        );
        expect(isLocalDatabaseManifestHealthy(manifestFile), isTrue);
      });
      expect(server.moduleDownloads, downloadsAfterRecovery);
      binding.reportData = {
        'fileSizeBytes': secondBytes.length,
        'installedDataVersions': [1, 2, 3],
        'readerShowsUpdatedVerse': true,
        'repeatOpenDoesNotDownload': true,
        'staleObjectRejected': true,
        'manifestWriteFailureDoesNotBlockReading': true,
        'manifestCacheRecoversOnNextOpen': true,
        'storage': 'temporary documents and loopback HTTP only',
      };
    } finally {
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.runAsync(() async {
        await Supabase.instance.dispose();
        await server.close();
        await GetIt.I.reset();
        PathProviderPlatform.instance = originalPathProvider;
        await temp.delete(recursive: true);
      });
    }
  });
}

Future<void> _openReader(WidgetTester tester, int phase, String text) async {
  final displayedVerse = find.text('1. $text', findRichText: true);
  await tester.pumpWidget(
    MaterialApp(
      key: ValueKey(phase),
      locale: const Locale('en'),
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: BibleScreen(
        initialBookId: 1,
        initialModuleFile: _moduleFile,
        bibleRepository: BibleRepository(),
      ),
    ),
  );
  for (var attempt = 0; attempt < 150; attempt++) {
    await tester.pump(const Duration(milliseconds: 100));
    if (displayedVerse.evaluate().isNotEmpty) break;
  }
  expect(displayedVerse, findsOneWidget);
  expect(tester.takeException(), isNull);
}

Future<List<int>> _moduleBytes(Directory temp, int version, String text) async {
  final file = File(p.join(temp.path, 'version_$version.sqlite'));
  final db = sqlite3.open(file.path);
  try {
    db.execute('PRAGMA user_version = 3');
    db.execute('CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT)');
    db.execute(
      'INSERT INTO db_metadata VALUES '
      "('schema_version', '3'), ('data_version', '$version'), "
      "('date', '$_moduleDate')",
    );
    db.execute(
      'CREATE TABLE info(code TEXT, module_id TEXT, title TEXT, '
      'description TEXT, language TEXT, canon TEXT, versification TEXT, '
      'license TEXT, source_summary TEXT)',
    );
    db.execute(
      "INSERT INTO info VALUES ('TEST', 'rev192', 'Test module', "
      "'', 'en', 'protestant_66', 'kjv_protestant', '', 'Synthetic fixture')",
    );
    db.execute('CREATE TABLE verses(verse_key TEXT PRIMARY KEY, text TEXT)');
    db.execute("INSERT INTO verses VALUES ('001', ?)", [text]);
  } finally {
    db.dispose();
  }
  return file.readAsBytes();
}

class _TemporaryDocuments extends PathProviderPlatform {
  _TemporaryDocuments(this.path);
  final String path;

  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}

class _ModuleServer {
  _ModuleServer(this.server) {
    server.listen((request) async {
      final file = request.uri.pathSegments.last;
      final bytes = files[file];
      if (bytes == null) {
        request.response.statusCode = HttpStatus.notFound;
      } else {
        if (file == _moduleFile) moduleDownloads++;
        request.response.add(bytes);
      }
      await request.response.close();
    });
  }

  final HttpServer server;
  final Map<String, List<int>> files = {};
  int moduleDownloads = 0;
  String get url => 'http://${server.address.address}:${server.port}';

  static Future<_ModuleServer> start() async =>
      _ModuleServer(await HttpServer.bind(InternetAddress.loopbackIPv4, 0));

  void publish(int version, List<int> bytes) {
    files[_moduleFile] = bytes;
    files['manifest.json'] = utf8.encode(
      jsonEncode({
        'version': 1,
        'databases': {
          _moduleFile: {
            'schemaVersion': 3,
            'dataVersion': version,
            'date': _moduleDate,
            'fileSizeBytes': bytes.length,
          },
        },
      }),
    );
  }

  Future<void> close() => server.close(force: true);
}
