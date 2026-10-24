import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/bible/presentation/screens/bible_screen.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_state.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/infra/db/connectors/database_version_file_loader.dart';
import 'package:revelation/infra/storage/file_sync_utils.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqlite3/sqlite3.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:talker_flutter/talker_flutter.dart';

const _module = AppConstants.defaultBibleModuleDB;
const _date = '2026-10-24T00:00:00Z';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  binding.reportData = {};
  for (final language in AppConstants.languages.keys) {
    testWidgets(
      'clean reader selects $language, retries, reopens offline and updates',
      (tester) async {
        final originalPaths = PathProviderPlatform.instance;
        late Directory temp;
        late _Storage storage;
        late SettingsCubit settings;
        late List<int> v2;
        await tester.runAsync(() async {
          temp = await Directory.systemTemp.createTemp('rev210_');
          PathProviderPlatform.instance = _Documents(temp.path);
          await GetIt.I.reset();
          GetIt.I.registerSingleton<Talker>(
            Talker(settings: TalkerSettings(useConsoleLogs: false)),
          );
          SharedPreferences.setMockInitialValues({});
          AudioController.setInstanceForTest(_SilentAudio());
          settings = SettingsCubit(SettingsRepository());
          await settings.loadSettings();
          storage = await _Storage.start();
          storage.publish(1, await _bytes(temp, 1, 'First readable sample'));
          v2 = await _bytes(temp, 2, 'Fresh readable sample');
          await Supabase.initialize(
            url: storage.url,
            anonKey: 'local-test-key',
            authOptions: const FlutterAuthClientOptions(
              localStorage: EmptyLocalStorage(),
            ),
          );
          final localFile = File(p.join(await getAppFolder(), 'db', _module));
          expect(await localFile.exists(), isFalse);
        });
        try {
          await tester.pumpWidget(_Entry(settings: settings));
          await tester.pumpAndSettle();
          await tester.tap(find.byKey(const Key('first-reading-settings')));
          await tester.pumpAndSettle();
          var l10n = AppLocalizations.of(
            tester.element(find.byType(SettingsScreen)),
          )!;
          await tester.tap(find.text(l10n.language));
          await tester.pumpAndSettle();
          await tester.tap(find.text(AppConstants.languages[language]!).last);
          await tester.pumpAndSettle();
          expect(settings.state.settings.selectedLanguage, language);
          await tester.runAsync(() async {
            expect(
              (await SettingsRepository().getSettings()).selectedLanguage,
              language,
            );
          });
          await tester.tap(find.byType(BackButton));
          await tester.pumpAndSettle();

          // Only module downloads fail: the manifest remains discoverable.
          storage.failModule = true;
          await tester.tap(find.byKey(const Key('first-reading-open')));
          await _until(tester, find.byKey(const Key('bible_retry_button')));
          l10n = AppLocalizations.of(tester.element(find.byType(BibleScreen)))!;
          expect(find.text(l10n.startup_retry), findsOneWidget);
          final attemptsAfterFailure = storage.moduleRequests;
          expect(attemptsAfterFailure, greaterThan(0));
          final stopwatch = Stopwatch()..start();
          storage.failModule = false;
          await tester.tap(find.byKey(const Key('bible_retry_button')));
          // A second queued tap must not start another download.
          await tester.tap(find.byKey(const Key('bible_retry_button')));
          await _until(
            tester,
            find.text('1. First readable sample', findRichText: true),
          );
          stopwatch.stop();
          expect(storage.successfulDownloads, 1);
          expect(storage.moduleRequests, attemptsAfterFailure + 1);
          expect(find.byKey(const Key('bible_retry_button')), findsNothing);

          await tester.tap(find.byType(BackButton));
          await tester.pumpAndSettle();
          storage.offline = true;
          await tester.tap(find.byKey(const Key('first-reading-open')));
          await _until(
            tester,
            find.text('1. First readable sample', findRichText: true),
          );
          expect(storage.successfulDownloads, 1);
          expect(storage.moduleRequests, attemptsAfterFailure + 1);

          await tester.tap(find.byType(BackButton));
          await tester.pumpAndSettle();
          storage.offline = false;
          storage.publish(2, v2);
          await tester.tap(find.byKey(const Key('first-reading-open')));
          await _until(
            tester,
            find.text('1. Fresh readable sample', findRichText: true),
          );
          expect(storage.successfulDownloads, 2);
          await tester.runAsync(() async {
            final localFile = File(p.join(await getAppFolder(), 'db', _module));
            expect(await localFile.readAsBytes(), v2);
            expect(loadDatabaseVersionInfoFromFile(localFile)!.dataVersion, 2);
          });
          expect(tester.takeException(), isNull);
          binding.reportData![language] = {
            'languageSaved': true,
            'retryOnSameRoute': true,
            'successfulDownloads': storage.successfulDownloads,
            'offlineReopen': true,
            'installedDataVersion': 2,
            'recoveryToVisibleVerseMs': stopwatch.elapsedMilliseconds,
            'module': _module,
            'source': 'synthetic loopback and temporary documents',
          };
          debugPrint(
            'REV210_RESULT $language ${jsonEncode(binding.reportData![language])}',
          );
        } finally {
          await tester.pumpWidget(const SizedBox.shrink());
          await tester.pumpAndSettle();
          await tester.runAsync(() async {
            await settings.close();
            await Supabase.instance.dispose();
            await storage.server.close(force: true);
            await GetIt.I.reset();
            AudioController.resetForTest();
            PathProviderPlatform.instance = originalPaths;
            await temp.delete(recursive: true);
          });
        }
      },
    );
  }
}

Future<void> _until(WidgetTester tester, Finder finder) async {
  for (var i = 0; i < 200 && finder.evaluate().isEmpty; i++) {
    await tester.pump(const Duration(milliseconds: 100));
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 20)),
    );
  }
  expect(finder, findsOneWidget);
  await tester.pumpAndSettle();
}

class _Entry extends StatelessWidget {
  const _Entry({required this.settings});
  final SettingsCubit settings;

  @override
  Widget build(BuildContext context) => BlocProvider.value(
    value: settings,
    child: BlocBuilder<SettingsCubit, SettingsState>(
      builder: (context, state) => MaterialApp(
        locale: Locale(state.settings.selectedLanguage),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        routes: {
          '/': (context) => Scaffold(
            body: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextButton(
                    key: const Key('first-reading-settings'),
                    onPressed: () =>
                        Navigator.of(context).pushNamed('/settings'),
                    child: const Text('Settings'),
                  ),
                  TextButton(
                    key: const Key('first-reading-open'),
                    onPressed: () => Navigator.of(context).pushNamed('/bible'),
                    child: const Text('Bible'),
                  ),
                ],
              ),
            ),
          ),
          '/settings': (_) => const SettingsScreen(),
          '/bible': (_) => const BibleScreen(initialBookId: 1),
        },
      ),
    ),
  );
}

class _Documents extends PathProviderPlatform {
  _Documents(this.path);
  final String path;
  @override
  Future<String?> getApplicationDocumentsPath() async => path;
}

class _SilentAudio extends AudioController {
  _SilentAudio() : super.forTest();
  @override
  void playSound(String sourceName) {}
}

Future<List<int>> _bytes(Directory temp, int version, String text) async {
  final file = File(p.join(temp.path, 'v$version.sqlite'));
  final db = sqlite3.open(file.path);
  try {
    db.execute('PRAGMA user_version = 3');
    db.execute('CREATE TABLE db_metadata(key TEXT PRIMARY KEY, value TEXT)');
    db.execute(
      "INSERT INTO db_metadata VALUES ('schema_version','3'), ('data_version','$version'), ('date','$_date')",
    );
    db.execute(
      'CREATE TABLE info(code TEXT, module_id TEXT, title TEXT, description TEXT, language TEXT, canon TEXT, versification TEXT, license TEXT, source_summary TEXT)',
    );
    db.execute(
      "INSERT INTO info VALUES ('TEST','rev210','Synthetic fixture','','grc','protestant_66','kjv_protestant','','First-party fixture')",
    );
    db.execute('CREATE TABLE verses(verse_key TEXT PRIMARY KEY, text TEXT)');
    db.execute("INSERT INTO verses VALUES ('001',?)", [text]);
  } finally {
    db.dispose();
  }
  return file.readAsBytes();
}

class _Storage {
  _Storage(this.server) {
    server.listen((request) async {
      final name = request.uri.pathSegments.last;
      if (name == _module) moduleRequests++;
      final bytes = files[name];
      if (offline || (name == _module && failModule) || bytes == null) {
        request.response.statusCode = HttpStatus.serviceUnavailable;
      } else {
        if (name == _module) successfulDownloads++;
        request.response.add(bytes);
      }
      await request.response.close();
    });
  }
  final HttpServer server;
  final files = <String, List<int>>{};
  bool offline = false;
  bool failModule = false;
  int moduleRequests = 0;
  int successfulDownloads = 0;
  String get url => 'http://${server.address.address}:${server.port}';
  static Future<_Storage> start() async =>
      _Storage(await HttpServer.bind(InternetAddress.loopbackIPv4, 0));
  void publish(int version, List<int> bytes) {
    files[_module] = bytes;
    files['manifest.json'] = utf8.encode(
      jsonEncode({
        'version': 1,
        'databases': {
          _module: {
            'schemaVersion': 3,
            'dataVersion': version,
            'date': _date,
            'fileSizeBytes': bytes.length,
          },
        },
      }),
    );
  }
}
