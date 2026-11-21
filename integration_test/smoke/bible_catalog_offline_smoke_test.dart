import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:talker_flutter/talker_flutter.dart';
import '../support/catalog_sandbox_native.dart'
    if (dart.library.js_interop) '../support/catalog_sandbox_web.dart';
import '../support/catalog_sqlite_fixture.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'server discovery, interrupted update and offline catalog use installed SQLite modules',
    (tester) async {
      await tester.runAsync(() async {
        final id = DateTime.now().microsecondsSinceEpoch;
        final en = 'bible_rev113_${id}_en.sqlite',
            es = 'bible_rev113_${id}_es.sqlite';
        final sandbox = await CatalogSandbox.create();
        final entries = <String, Object>{};
        final objects = <String, Uint8List>{};
        var online = true, downloads = 0;
        http.Client client() => MockClient((request) async {
          final file = request.url.pathSegments.last;
          if (online && file == 'manifest.json') {
            return http.Response(
              jsonEncode({'version': 1, 'databases': entries}),
              200,
            );
          }
          if (online && objects.containsKey(file)) {
            downloads++;
            return http.Response.bytes(objects[file]!, 200);
          }
          return http.Response('Unavailable', 404);
        });
        Future<void> publish(String file, String language, int revision) async {
          final bytes = await sandbox.moduleBytes(language, revision);
          objects[file] = bytes;
          entries[file] = {
            'versionToken': 'opaque-$language',
            'schemaVersion': 3,
            'dataVersion': revision,
            'date': catalogDate,
            'fileSizeBytes': bytes.length,
            'bible': {
              'code': language.toUpperCase(),
              'language': language,
              'title': 'Test $language',
              'moduleId': language,
            },
          };
        }

        final settings = AppSettings(
          selectedLanguage: 'es',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: false,
        );
        BibleLibraryRepository library() =>
            BibleLibraryRepository(loadSettings: () async => settings);
        SharedPreferences.resetStatic();
        SharedPreferences.setPrefix('rev113_catalog_$id.');
        await GetIt.I.reset();
        GetIt.I.registerSingleton<Talker>(
          Talker(settings: TalkerSettings(useConsoleLogs: false)),
        );
        try {
          await http.runWithClient(() async {
            await Supabase.initialize(
              url: 'http://localhost',
              anonKey: 'local-only',
              httpClient: client(),
              authOptions: const FlutterAuthClientOptions(
                localStorage: EmptyLocalStorage(),
              ),
            );
            await publish(en, 'en', 1);
            final catalog = library();
            expect(await catalog.preferredModuleFile(), en);
            expect(downloads, 0);
            expect(
              (await catalog.loadPreview(['001'])).verses.single.text,
              'Test en 1',
            );
            await publish(es, 'es', 1);
            expect(
              (await catalog.loadCatalog(refresh: true)).map((e) => e.fileName),
              contains(es),
            );
            expect(await catalog.preferredModuleFile(), es);
            expect(downloads, 1);
            expect(
              (await catalog.loadPreview(['001'])).verses.single.text,
              'Test es 1',
            );
            // Keep an active Web reader while promoting the next verified snapshot.
            final oldReader = kIsWeb
                ? const LocalBibleModuleDataSource().openModule(es)
                : null;
            try {
              if (oldReader != null)
                expect(
                  (await oldReader.readVersesByKeys(['001'])).single.text,
                  'Test es 1',
                );
              final firstSpanish = objects[es]!;
              final firstEntry = entries[es]!;
              await publish(es, 'es', 2);
              final correct = objects.remove(es)!;
              final secondEntry = entries[es]!;
              await catalog.loadCatalog(refresh: true);
              final interrupted = await catalog.loadPreview(['001']);
              expect(interrupted.verses.single.text, 'Test es 1');
              expect(interrupted.module.dataVersion, 1);
              objects[es] = firstSpanish;
              expect(
                (await catalog.loadPreview(['001'])).verses.single.text,
                'Test es 1',
              );
              objects[es] = correct;
              expect(
                (await catalog.loadPreview(['001'])).verses.single.text,
                'Test es 2',
              );
              if (oldReader != null)
                expect(
                  (await oldReader.readVersesByKeys(['001'])).single.text,
                  'Test es 1',
                );
              entries[es] = firstEntry;
              objects[es] = firstSpanish;
              await catalog.loadCatalog(refresh: true);
              expect(
                (await catalog.loadPreview(['001'])).verses.single.text,
                'Test es 2',
              );
              entries[es] = secondEntry;
              objects[es] = correct;
              await catalog.loadCatalog(refresh: true);
            } finally {
              await oldReader?.close();
            }
            online = false;
            sandbox.reopenPreferences();
            SharedPreferences.resetStatic();
            SharedPreferences.setPrefix('rev113_catalog_$id.');
            final offline = library();
            expect(
              (await offline.cachedCatalog()).map((e) => e.fileName),
              contains(es),
            );
            expect(
              (await offline.loadPreview(['001'])).verses.single.text,
              'Test es 2',
            );
            await sandbox.forgetCatalogManifest();
            final prefs = await SharedPreferences.getInstance();
            await prefs.remove('bible_module_catalog_v1');
            final fresh = library();
            expect(await fresh.preferredModuleFile(), es);
            expect(
              (await fresh.loadPreview(['001'])).verses.single.text,
              'Test es 2',
            );
            binding.reportData = {
              'dynamicCatalog': true,
              'offlineCachedCatalog': true,
              'offlineInstalledDiscovery': true,
              'http404PreservedPriorVersion': true,
              'wrongRevisionRejected': true,
              'staleManifestRejected': true,
              'promotedRevision': 2,
              'oldReaderRetainedSnapshot': kIsWeb,
              'storage': 'isolated SQLite and platform preferences',
            };
            debugPrint('Bible catalog offline: ${binding.reportData}');
          }, client);
        } finally {
          await Supabase.instance.dispose();
          await (await SharedPreferences.getInstance()).clear();
          SharedPreferences.resetStatic();
          await sandbox.dispose([en, es]);
          await GetIt.I.reset();
        }
      });
    },
  );
}
