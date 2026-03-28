import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/startup/bloc/app_startup_cubit.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../../test_harness/test_harness.dart';

void main() {
  group('AppStartupCubit', () {
    test(
      'completes startup, exposes version info and keeps initialized settings cubit',
      () async {
        final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
        final settingsCubit = await _createSettingsCubit(language: 'uk');
        final cubit = AppStartupCubit(
          talker: talker,
          autoStart: false,
          packageInfoLoader: () async => PackageInfo(
            appName: 'Revelation',
            packageName: 'revelation',
            version: '1.0.5',
            buildNumber: '141',
            buildSignature: '',
          ),
          appBootstrapFactory: (_) => _FakeBootstrap(
            settingsCubit: settingsCubit,
            progress: const <AppBootstrapProgress>[
              AppBootstrapProgress(AppBootstrapStep.preparing),
              AppBootstrapProgress(AppBootstrapStep.loadingSettings),
              AppBootstrapProgress(
                AppBootstrapStep.initializingServer,
                selectedLanguageCode: 'uk',
              ),
              AppBootstrapProgress(
                AppBootstrapStep.initializingDatabases,
                selectedLanguageCode: 'uk',
              ),
              AppBootstrapProgress(
                AppBootstrapStep.configuringLinks,
                selectedLanguageCode: 'uk',
              ),
              AppBootstrapProgress(
                AppBootstrapStep.ready,
                selectedLanguageCode: 'uk',
              ),
            ],
          ),
        );
        addTearDown(cubit.close);

        await cubit.start();

        expect(cubit.state.isReady, isTrue);
        expect(cubit.state.isLoading, isFalse);
        expect(cubit.state.appVersion, '1.0.5');
        expect(cubit.state.buildNumber, '141');
        expect(cubit.state.localeCode, 'uk');
        expect(cubit.initializedSettingsCubit, same(settingsCubit));
      },
    );

    test('retry recovers from startup failure', () async {
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      final settingsCubit = await _createSettingsCubit(language: 'en');
      final bootstrapCalls = <int>[];
      final cubit = AppStartupCubit(
        talker: talker,
        autoStart: false,
        appBootstrapFactory: (_) => _FakeBootstrap(
          settingsCubit: settingsCubit,
          progress: const <AppBootstrapProgress>[
            AppBootstrapProgress(AppBootstrapStep.preparing),
          ],
          onInitialize: () {
            bootstrapCalls.add(bootstrapCalls.length + 1);
            if (bootstrapCalls.length == 1) {
              throw StateError('forced startup failure');
            }
          },
        ),
      );
      addTearDown(cubit.close);

      await cubit.start();
      expect(cubit.state.failure, isNotNull);
      expect(cubit.state.isReady, isFalse);

      await cubit.retry();
      expect(cubit.state.failure, isNull);
      expect(cubit.state.isReady, isTrue);
      expect(bootstrapCalls, <int>[1, 2]);
    });

    test('close closes initialized settings cubit', () async {
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      final settingsCubit = await _createSettingsCubit(language: 'ru');
      final cubit = AppStartupCubit(
        talker: talker,
        autoStart: false,
        appBootstrapFactory: (_) => _FakeBootstrap(
          settingsCubit: settingsCubit,
          progress: const <AppBootstrapProgress>[
            AppBootstrapProgress(AppBootstrapStep.preparing),
            AppBootstrapProgress(
              AppBootstrapStep.ready,
              selectedLanguageCode: 'ru',
            ),
          ],
        ),
      );

      await cubit.start();
      await cubit.close();

      expect(settingsCubit.isClosed, isTrue);
    });
  });
}

Future<SettingsCubit> _createSettingsCubit({required String language}) async {
  final cubit = SettingsCubit(
    FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: language,
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    ),
  );
  await cubit.loadSettings();
  return cubit;
}

class _FakeBootstrap extends AppBootstrap {
  _FakeBootstrap({
    required this.settingsCubit,
    required this.progress,
    this.onInitialize,
  }) : super(talker: Talker(settings: TalkerSettings(useConsoleLogs: false)));

  final SettingsCubit settingsCubit;
  final List<AppBootstrapProgress> progress;
  final FutureOr<void> Function()? onInitialize;

  @override
  Future<SettingsCubit> initialize({
    AppBootstrapProgressCallback? onProgress,
  }) async {
    await onInitialize?.call();
    for (final item in progress) {
      onProgress?.call(item);
    }
    return settingsCubit;
  }
}
