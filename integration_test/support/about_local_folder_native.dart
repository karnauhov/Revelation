import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/features/about/presentation/bloc/about_cubit.dart';
import 'package:revelation/features/about/presentation/screens/about_screen.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/infra/storage/local_app_folder_io.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../test/test_harness/fakes/fake_settings_repository.dart';
import '../smoke/smoke_test_harness.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });
  tearDown(() => GetIt.I.reset());

  for (final language in ['en', 'es', 'uk', 'ru']) {
    testWidgets('About folder opening failure shows its path in $language', (
      tester,
    ) async {
      final temp = await Directory.systemTemp.createTemp('rev193_');
      addTearDown(() => temp.delete(recursive: true));
      final folderPath = p.join(temp.path, 'Мої документи', 'Revelation data');
      final settings = SettingsCubit(
        FakeSettingsRepository(
          initialSettings: AppSettings(
            selectedLanguage: language,
            selectedTheme: 'manuscript',
            selectedFontSize: 'medium',
            soundEnabled: false,
          ),
        ),
      );
      addTearDown(settings.close);
      await settings.loadSettings();
      var launchCalls = 0;
      await tester.pumpWidget(
        BlocProvider<SettingsCubit>.value(
          value: settings,
          child: MaterialApp(
            locale: Locale(language),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: AboutScreen(
              aboutCubitBuilder: (language) => AboutCubit(
                initialLanguageCode: language,
                packageInfoLoader: () async => PackageInfo(
                  appName: 'Revelation',
                  packageName: 'revelation',
                  version: '1.0.8',
                  buildNumber: '173',
                ),
                changelogLoader: () async => '',
                appBuildTimestampLoader: () async => null,
                dbVersionInfoLoader: (_) async => null,
              ),
              dependencies: AboutScreenDependencies(
                showLocalFolder: () => showLocalAppFolderWith(
                  appFolderProvider: () async => folderPath,
                  processStarter:
                      (
                        executable,
                        arguments, {
                        mode = ProcessStartMode.normal,
                      }) async {
                        launchCalls++;
                        expect(arguments.single, folderPath);
                        throw ProcessException(
                          executable,
                          arguments,
                          'test opener unavailable',
                        );
                      },
                  urlLauncher: (uri) async {
                    launchCalls++;
                    expect(uri, Directory(folderPath).uri);
                    return false;
                  },
                ),
              ),
            ),
          ),
        ),
      );
      await pumpAndSettleSmoke(tester);
      final l10n = AppLocalizations.of(
        tester.element(find.byType(AboutScreen)),
      )!;
      await tester.ensureVisible(find.text(l10n.tools));
      await tester.tap(find.text(l10n.tools));
      await pumpAndSettleSmoke(tester);
      final action = find.byKey(const ValueKey('about-show-local-folder'));
      await tester.ensureVisible(action);
      await pumpAndSettleSmoke(tester);
      await tester.tap(action);
      final message = find.text(
        '${l10n.local_folder_open_failed}:\n$folderPath',
      );
      for (var tick = 0; tick < 100 && message.evaluate().isEmpty; tick++) {
        await tester.pump(const Duration(milliseconds: 50));
      }
      expect(message, findsOneWidget);
      expect(launchCalls, 1);
      expect(await Directory(folderPath).exists(), isTrue);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
    });
  }
}
