import 'dart:async';
import 'dart:convert';
import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/core/analytics/app_analytics_reporter.dart';
import 'package:revelation/features/settings/settings.dart' show SettingsCubit;
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/runtime/database_runtime.dart';
import 'package:revelation/shared/navigation/app_link_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  void Function(FlutterErrorDetails details)? previousFlutterErrorHandler;
  bool Function(Object, StackTrace)? previousPlatformErrorHandler;

  setUp(() async {
    previousFlutterErrorHandler = FlutterError.onError;
    previousPlatformErrorHandler = PlatformDispatcher.instance.onError;
    SharedPreferences.setMockInitialValues(<String, Object>{});
    PackageInfo.setMockInitialValues(
      appName: 'Revelation',
      packageName: 'ai11.link.revelation',
      version: '1.0.7',
      buildNumber: '157',
      buildSignature: '',
    );
    await GetIt.I.reset();
  });

  tearDown(() async {
    FlutterError.onError = previousFlutterErrorHandler;
    PlatformDispatcher.instance.onError = previousPlatformErrorHandler;
    setDefaultGreekStrongTapHandler(null);
    setDefaultGreekStrongPickerTapHandler(null);
    setDefaultWordTapHandler(null);
    setDefaultWordsTapHandler(null);
    await GetIt.I.reset();
  });

  test('constructor supports default database runtime', () {
    final bootstrap = AppBootstrap(
      talker: Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    expect(bootstrap, isA<AppBootstrap>());
  });

  test(
    'initialize configures startup path and reacts to language changes',
    () async {
      await _seedSettings(language: 'ru');
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      AppDi.registerCore(talker: talker);
      final runtime = _FakeDatabaseRuntime();
      final progressSteps = <AppBootstrapStep>[];
      final analyticsReporter = _RecordingAppAnalyticsReporter();

      final audioInitCalls = <String>[];
      final configLoadCalls = <String>[];
      final bootstrap = AppBootstrap(
        talker: talker,
        databaseRuntime: runtime,
        initializeAudio: (settingsCubit) async {
          audioInitCalls.add(settingsCubit.state.settings.selectedLanguage);
        },
        loadManuscriptGreekTextConfig: () async {
          configLoadCalls.add('manuscript-greek');
        },
        loadNominaSacraPronunciationConfig: () async {
          configLoadCalls.add('nomina-sacra');
        },
        analyticsReporter: analyticsReporter,
        packageInfoLoader: _loadTestPackageInfo,
        databaseVersionInfoLoader: _loadTestDatabaseVersionInfo,
      );
      final settingsCubit = await bootstrap.initialize(
        onProgress: (progress) {
          progressSteps.add(progress.step);
        },
      );
      addTearDown(settingsCubit.close);

      expect(settingsCubit.state.settings.selectedLanguage, 'ru');
      expect(runtime.initializedLanguages, <String>['ru']);
      expect(audioInitCalls, <String>['ru']);
      expect(configLoadCalls, <String>['manuscript-greek', 'nomina-sacra']);
      expect(analyticsReporter.appContexts, <AppAnalyticsAppContext>[
        const AppAnalyticsAppContext(
          appName: 'Revelation',
          packageName: 'ai11.link.revelation',
          version: '1.0.7',
          buildNumber: '157',
          platform: 'android',
          languageCode: 'ru',
        ),
      ]);
      expect(analyticsReporter.dataContexts, hasLength(1));
      expect(analyticsReporter.dataContexts.single.languageCode, 'ru');
      expect(
        analyticsReporter.dataContexts.single.commonDatabase,
        _commonAnalyticsDatabaseVersion,
      );
      expect(
        analyticsReporter.dataContexts.single.localizedDatabase,
        _ruAnalyticsDatabaseVersion,
      );
      expect(analyticsReporter.sessionContexts, <AppAnalyticsDataContext>[
        analyticsReporter.dataContexts.single,
      ]);
      expect(progressSteps, <AppBootstrapStep>[
        AppBootstrapStep.preparing,
        AppBootstrapStep.loadingSettings,
        AppBootstrapStep.initializingServer,
        AppBootstrapStep.initializingDatabases,
        AppBootstrapStep.configuringLinks,
        AppBootstrapStep.ready,
      ]);

      await settingsCubit.changeLanguage('en');
      final updatedLanguage = await runtime.firstUpdatedLanguage.future;
      expect(updatedLanguage, 'en');
      expect(runtime.updatedLanguages, <String>['en']);
      await Future<void>.delayed(Duration.zero);
      expect(analyticsReporter.dataContexts, hasLength(2));
      expect(analyticsReporter.dataContexts.last.languageCode, 'en');
      expect(analyticsReporter.sessionContexts, hasLength(1));
    },
  );

  test('initialize keeps app startup alive when database init fails', () async {
    await _seedSettings(language: 'uk');
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    final runtime = _FakeDatabaseRuntime(failOnInitialize: true);

    final bootstrap = AppBootstrap(
      talker: talker,
      databaseRuntime: runtime,
      initializeAudio: _noopInitializeAudio,
      databaseVersionInfoLoader: _loadTestDatabaseVersionInfo,
    );
    final settingsCubit = await bootstrap.initialize();
    addTearDown(settingsCubit.close);

    expect(settingsCubit.state.settings.selectedLanguage, 'uk');
    expect(runtime.initializedLanguages, <String>['uk']);

    await settingsCubit.changeLanguage('es');
    await Future<void>.delayed(Duration.zero);
    expect(runtime.updatedLanguages, isEmpty);
  });

  test('initialize configures global error handlers', () async {
    await _seedSettings(language: 'en');
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    final analyticsReporter = _RecordingAppAnalyticsReporter();
    final previousPresentError = FlutterError.presentError;
    final presentedErrors = <FlutterErrorDetails>[];
    FlutterError.presentError = presentedErrors.add;
    addTearDown(() {
      FlutterError.presentError = previousPresentError;
    });
    final bootstrap = AppBootstrap(
      talker: talker,
      databaseRuntime: _FakeDatabaseRuntime(),
      initializeAudio: _noopInitializeAudio,
      analyticsReporter: analyticsReporter,
      packageInfoLoader: _loadTestPackageInfo,
      databaseVersionInfoLoader: _loadTestDatabaseVersionInfo,
    );
    final settingsCubit = await bootstrap.initialize();
    addTearDown(settingsCubit.close);

    final flutterHandler = FlutterError.onError;
    final platformHandler = PlatformDispatcher.instance.onError;

    expect(flutterHandler, isNotNull);
    expect(platformHandler, isNotNull);

    flutterHandler!(
      FlutterErrorDetails(exception: StateError('forced framework error')),
    );
    expect(presentedErrors, hasLength(1));
    expect(presentedErrors.single.exception, isA<StateError>());
    await Future<void>.delayed(Duration.zero);
    final handled = platformHandler!(
      StateError('forced platform error'),
      StackTrace.current,
    );
    expect(handled, isTrue);
    await Future<void>.delayed(Duration.zero);
    expect(analyticsReporter.captured, hasLength(2));
    expect(analyticsReporter.captured.first.source, 'Flutter framework error');
    expect(analyticsReporter.captured.first.fatal, isTrue);
    expect(
      analyticsReporter.captured.last.source,
      'PlatformDispatcher uncaught error',
    );
    expect(analyticsReporter.captured.last.fatal, isTrue);
  });

  test('initialize keeps app startup alive when audio init fails', () async {
    await _seedSettings(language: 'es');
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    final runtime = _FakeDatabaseRuntime();

    final bootstrap = AppBootstrap(
      talker: talker,
      databaseRuntime: runtime,
      initializeAudio: (_) async {
        throw StateError('forced audio initialization failure');
      },
      databaseVersionInfoLoader: _loadTestDatabaseVersionInfo,
    );
    final settingsCubit = await bootstrap.initialize();
    addTearDown(settingsCubit.close);

    expect(settingsCubit.state.settings.selectedLanguage, 'es');
    expect(runtime.initializedLanguages, <String>['es']);
  });
}

Future<void> _noopInitializeAudio(SettingsCubit settingsCubit) async {}

Future<PackageInfo> _loadTestPackageInfo() async {
  return PackageInfo(
    appName: 'Revelation',
    packageName: 'ai11.link.revelation',
    version: '1.0.7',
    buildNumber: '157',
  );
}

Future<DatabaseVersionInfo?> _loadTestDatabaseVersionInfo(String dbFile) async {
  return _testDatabaseVersions[dbFile];
}

Future<void> _seedSettings({required String language}) async {
  SharedPreferences.setMockInitialValues(<String, Object>{
    'revelation_settings': jsonEncode(<String, dynamic>{
      'selectedLanguage': language,
      'selectedTheme': 'manuscript',
      'selectedFontSize': 'medium',
      'soundEnabled': true,
    }),
  });
}

final _commonDatabaseVersion = DatabaseVersionInfo(
  schemaVersion: 1,
  dataVersion: 3,
  date: DateTime.utc(2026, 5, 1),
);

final _ruDatabaseVersion = DatabaseVersionInfo(
  schemaVersion: 1,
  dataVersion: 8,
  date: DateTime.utc(2026, 5, 2),
);

final _enDatabaseVersion = DatabaseVersionInfo(
  schemaVersion: 1,
  dataVersion: 6,
  date: DateTime.utc(2026, 5, 2),
);

final _testDatabaseVersions = <String, DatabaseVersionInfo>{
  'revelation.sqlite': _commonDatabaseVersion,
  'revelation_ru.sqlite': _ruDatabaseVersion,
  'revelation_en.sqlite': _enDatabaseVersion,
};

final _commonAnalyticsDatabaseVersion = AppAnalyticsDatabaseVersion(
  schemaVersion: _commonDatabaseVersion.schemaVersion,
  dataVersion: _commonDatabaseVersion.dataVersion,
  date: _commonDatabaseVersion.date,
);

final _ruAnalyticsDatabaseVersion = AppAnalyticsDatabaseVersion(
  schemaVersion: _ruDatabaseVersion.schemaVersion,
  dataVersion: _ruDatabaseVersion.dataVersion,
  date: _ruDatabaseVersion.date,
);

class _CapturedException {
  const _CapturedException({required this.source, required this.fatal});

  final String source;
  final bool fatal;
}

class _RecordingAppAnalyticsReporter implements AppAnalyticsReporter {
  final List<AppAnalyticsAppContext> appContexts = <AppAnalyticsAppContext>[];
  final List<AppAnalyticsDataContext> dataContexts =
      <AppAnalyticsDataContext>[];
  final List<AppAnalyticsDataContext> sessionContexts =
      <AppAnalyticsDataContext>[];
  final List<_CapturedException> captured = <_CapturedException>[];

  @override
  Future<void> setAppContext(AppAnalyticsAppContext context) async {
    appContexts.add(context);
  }

  @override
  Future<void> setDataContext(AppAnalyticsDataContext context) async {
    dataContexts.add(context);
  }

  @override
  Future<void> trackAppSessionStarted(AppAnalyticsDataContext context) async {
    sessionContexts.add(context);
  }

  @override
  Future<void> captureException(
    Object error,
    StackTrace stackTrace, {
    required String source,
    bool fatal = false,
  }) async {
    captured.add(_CapturedException(source: source, fatal: fatal));
  }
}

class _FakeDatabaseRuntime implements DatabaseRuntime {
  _FakeDatabaseRuntime({this.failOnInitialize = false});

  final bool failOnInitialize;
  final List<String> initializedLanguages = <String>[];
  final List<String> updatedLanguages = <String>[];
  final Completer<String> firstUpdatedLanguage = Completer<String>();

  @override
  Future<void> initialize(String language) async {
    initializedLanguages.add(language);
    if (failOnInitialize) {
      throw StateError('forced database initialization failure');
    }
  }

  @override
  Future<void> updateLanguage(String language) async {
    updatedLanguages.add(language);
    if (!firstUpdatedLanguage.isCompleted) {
      firstUpdatedLanguage.complete(language);
    }
  }
}
