import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path/path.dart' as p;
import 'package:revelation/core/errors/local_folder_open_exception.dart';
import 'package:revelation/features/about/presentation/bloc/about_cubit.dart';
import 'package:revelation/features/about/presentation/screens/about_screen.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/infra/storage/local_app_folder_io.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/shared/ui/widgets/platform_expansion_tile.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../test/test_harness/fakes/fake_settings_repository.dart';
import '../smoke/smoke_test_harness.dart';

typedef AboutFolderReadyWait =
    Future<void> Function(
      WidgetTester tester, {
      required bool Function() isReady,
      required String reason,
    });

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  registerAboutLocalFolderScenarios();
}

/// The host regression uses the same scenarios without a native test binding.
void registerAboutLocalFolderScenarios({
  TestVariant<Object?> variant = const DefaultTestVariant(),
}) {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });
  tearDown(() => GetIt.I.reset());

  for (final language in ['en', 'es', 'uk', 'ru']) {
    testWidgets(
      'About folder opening failure shows its path in $language',
      (tester) => runAboutLocalFolderScenario(tester, language: language),
      variant: variant,
    );
  }
}

Future<void> runAboutLocalFolderScenario(
  WidgetTester tester, {
  required String language,
  AboutFolderReadyWait waitForReady = pumpUntilSmoke,
}) async {
  final temp = await _runFileOperation(
    tester,
    () => Directory.systemTemp.createTemp('rev193_'),
  );
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
  final l10n = await AppLocalizations.delegate.load(Locale(language));
  var launchCalls = 0;
  Future<void>? folderOperation;
  final backgroundAnimation = AnimationController(
    vsync: tester,
    duration: const Duration(seconds: 1),
  )..repeat();
  try {
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
              showLocalFolder: () => folderOperation = _runFileOperation(
                tester,
                () => showLocalAppFolderWith(
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
      ),
    );
    final tools = find.text(l10n.tools);
    await waitForReady(
      tester,
      isReady: () => tools.evaluate().isNotEmpty,
      reason: 'localized About tools',
    );
    await tester.ensureVisible(tools);
    await waitForReady(
      tester,
      isReady: () => tools.hitTestable().evaluate().isNotEmpty,
      reason: 'visible About tools header',
    );
    await tester.tap(tools);
    final action = find.byKey(const ValueKey('about-show-local-folder'));
    await waitForReady(
      tester,
      isReady: () {
        if (action.evaluate().isEmpty) return false;
        final section = find.ancestor(
          of: action,
          matching: find.byType(PlatformExpansionTile),
        );
        if (section.evaluate().isEmpty) return false;
        final actionRect = tester.getRect(action);
        return actionRect.height > 0 &&
            actionRect.bottom <= tester.getRect(section.first).bottom + 0.5;
      },
      reason: 'revealed About folder action',
    );
    await tester.ensureVisible(action);
    await waitForReady(
      tester,
      isReady: () => action.hitTestable().evaluate().isNotEmpty,
      reason: 'interactive About folder action',
    );
    await tester.tap(action);
    expect(folderOperation, isNotNull);
    await expectLater(
      () => folderOperation!,
      throwsA(isA<LocalFolderOpenException>()),
    );
    final message = find.text('${l10n.local_folder_open_failed}:\n$folderPath');
    for (var tick = 0; tick < 100 && message.evaluate().isEmpty; tick++) {
      await tester.pump(const Duration(milliseconds: 50));
    }
    expect(message, findsOneWidget);
    expect(launchCalls, 1);
    expect(
      await _runFileOperation(tester, () => Directory(folderPath).exists()),
      isTrue,
    );
    expect(backgroundAnimation.isAnimating, isTrue);
    expect(tester.takeException(), isNull);
  } finally {
    backgroundAnimation.dispose();
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  }
}

Future<T> _runFileOperation<T>(
  WidgetTester tester,
  Future<T> Function() operation,
) async {
  late T result;
  Object? failure;
  StackTrace? failureStack;
  await tester.runAsync(() async {
    try {
      result = await operation();
    } catch (error, stack) {
      failure = error;
      failureStack = stack;
    }
  });
  if (failure != null) {
    Error.throwWithStackTrace(failure!, failureStack!);
  }
  return result;
}
