@Tags(['widget'])
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/startup/bloc/app_startup_cubit.dart';
import 'package:revelation/app/startup/screens/app_startup_screen.dart';
import 'package:revelation/core/logging/app_bloc_observer.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/main.dart';
import 'package:revelation/main.dart' as app_entry show main;
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/shared/ui/theme/material_theme.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../test_harness/test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  const desktopChannel = MethodChannel('revelation/window');
  const audioChannel = MethodChannel('revelation/audio');
  const audioGlobalChannel = MethodChannel('xyz.luan/audioplayers.global');

  late BlocObserver previousBlocObserver;
  late Future<void> Function() previousLaunchRevelationAppCallback;
  late StartupSettingsCubitLoader previousDefaultInitializeSettingsCubit;
  late AppBootstrapFactory previousDefaultAppBootstrapFactory;

  setUp(() async {
    previousBlocObserver = Bloc.observer;
    previousLaunchRevelationAppCallback = launchRevelationAppCallback;
    previousDefaultInitializeSettingsCubit = defaultInitializeSettingsCubit;
    previousDefaultAppBootstrapFactory = defaultAppBootstrapFactory;
    await GetIt.I.reset();
    AppDi.registerCore(
      talker: Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    PackageInfo.setMockInitialValues(
      appName: 'Revelation',
      packageName: 'revelation',
      version: '1.0.5-test',
      buildNumber: '141',
      buildSignature: '',
    );
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(audioGlobalChannel, (call) async {
          return null;
        });
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(audioChannel, (call) async {
          return null;
        });
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(desktopChannel, null);
  });

  tearDown(() async {
    Bloc.observer = previousBlocObserver;
    launchRevelationAppCallback = previousLaunchRevelationAppCallback;
    defaultInitializeSettingsCubit = previousDefaultInitializeSettingsCubit;
    defaultAppBootstrapFactory = previousDefaultAppBootstrapFactory;
    debugDefaultTargetPlatformOverride = null;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(audioGlobalChannel, null);
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(audioChannel, null);
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(desktopChannel, null);
    await GetIt.I.reset();
  });

  group('launchRevelationApp', () {
    test('main delegates to launchRevelationAppCallback', () async {
      var delegatedCalls = 0;
      launchRevelationAppCallback = () async {
        delegatedCalls++;
      };

      await app_entry.main();

      expect(delegatedCalls, 1);
    });

    test('wires talker, core setup and entrypoint startup callback', () async {
      final calls = <String>[];
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      Talker? configuredTalker;
      Talker? entrypointTalker;
      Talker? startupTalker;

      await launchRevelationApp(
        createTalker: () {
          calls.add('createTalker');
          return talker;
        },
        configureCore: (resolvedTalker) {
          calls.add('configureCore');
          configuredTalker = resolvedTalker;
        },
        runEntryPoint:
            ({
              required Talker talker,
              required AppStartCallback startAppCallback,
            }) async {
              calls.add('runEntryPoint');
              entrypointTalker = talker;
              await startAppCallback(talker);
            },
        startAppCallback: (resolvedTalker) async {
          calls.add('startApp');
          startupTalker = resolvedTalker;
        },
      );

      expect(calls, <String>[
        'createTalker',
        'configureCore',
        'runEntryPoint',
        'startApp',
      ]);
      expect(configuredTalker, same(talker));
      expect(entrypointTalker, same(talker));
      expect(startupTalker, same(talker));
    });

    test('createAppTalker returns app talker instance', () {
      final talker = createAppTalker();

      expect(talker, isA<Talker>());
    });
  });

  group('configureAppCore', () {
    test('registers talker in DI and installs AppBlocObserver', () {
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));

      configureAppCore(talker);

      expect(GetIt.I<Talker>(), same(talker));
      expect(Bloc.observer, isA<AppBlocObserver>());
    });
  });

  group('runAppEntryPoint', () {
    test('runs startup callback once when startup succeeds', () async {
      final talker = _RecordingTalker();
      var startupCalls = 0;

      await runAppEntryPoint(
        talker: talker,
        startAppCallback: (_) async {
          startupCalls++;
        },
      );

      expect(startupCalls, 1);
      expect(talker.handled, isEmpty);
    });

    test('forwards uncaught startup error to talker.handle', () async {
      final talker = _RecordingTalker();

      await runAppEntryPoint(
        talker: talker,
        startAppCallback: (_) async {
          throw StateError('forced startup error');
        },
      );

      expect(talker.handled, hasLength(1));
      expect(talker.handled.single.error, isA<StateError>());
      expect(talker.handled.single.message, 'Uncaught app exception (zone)');
      expect(talker.handled.single.stackTrace, isNotNull);
    });
  });

  group('startApp', () {
    test('passes a single root widget to runApp', () async {
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      var runAppCalls = 0;

      await startApp(
        talker,
        runAppCallback: (_) {
          runAppCalls++;
        },
      );

      expect(runAppCalls, 1);
    });

    testWidgets('renders splash first and then resolves into RevelationApp', (
      tester,
    ) async {
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      configureAppCore(talker);
      final settingsCubit = await _createSettingsCubit(_esForestSettings);
      Widget? capturedRoot;
      var initializeCalls = 0;
      final initializeCompleter = Completer<SettingsCubit>();

      await startApp(
        talker,
        initializeSettingsCubit: (_) async {
          initializeCalls++;
          return initializeCompleter.future;
        },
        runAppCallback: (rootWidget) {
          capturedRoot = rootWidget;
        },
      );

      expect(initializeCalls, 0);
      expect(capturedRoot, isNotNull);

      await tester.pumpWidget(capturedRoot!);
      await pumpFrames(tester, count: 2);

      expect(initializeCalls, 1);
      final l10n = AppLocalizations.of(
        tester.element(find.byType(AppStartupScreen)),
      )!;
      expect(find.byType(AppStartupScreen), findsOneWidget);
      expect(find.text(l10n.startup_title), findsOneWidget);
      expect(find.byType(RevelationApp), findsNothing);

      initializeCompleter.complete(settingsCubit);
      await pumpFrames(tester, count: 20);

      expect(find.byType(RevelationApp), findsOneWidget);
      expect(find.byType(MaterialApp), findsOneWidget);
    });
  });

  group('RevelationApp', () {
    testWidgets('maps settings to MaterialApp.router configuration', (
      tester,
    ) async {
      final settingsCubit = await _createSettingsCubit(_esForestSettings);
      addTearDown(settingsCubit.close);

      await tester.pumpWidget(_buildRevelationApp(settingsCubit));
      await pumpFrames(tester, count: 6);

      final materialApp = tester.widget<MaterialApp>(
        find.byType(MaterialApp).first,
      );
      final titleWidget = tester.widget<Title>(find.byType(Title).first);

      expect(materialApp.debugShowCheckedModeBanner, isFalse);
      expect(materialApp.title, 'Revelation');
      expect(materialApp.routerDelegate, isNotNull);
      expect(materialApp.routeInformationParser, isNotNull);
      expect(materialApp.routeInformationProvider, isNotNull);
      expect(materialApp.locale, const Locale('es'));
      expect(materialApp.supportedLocales, const <Locale>[
        Locale('en'),
        Locale('es'),
        Locale('uk'),
        Locale('ru'),
      ]);
      expect(
        materialApp.localizationsDelegates,
        contains(AppLocalizations.delegate),
      );
      expect(
        materialApp.theme?.colorScheme,
        MaterialTheme.getColorTheme('forest'),
      );
      expect(materialApp.theme?.useMaterial3, isTrue);
      expect(titleWidget.title, 'Apocalipsis');
    });

    testWidgets('onGenerateTitle updates desktop window title on desktop', (
      tester,
    ) async {
      debugDefaultTargetPlatformOverride = TargetPlatform.windows;
      final calls = <MethodCall>[];
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(desktopChannel, (call) async {
            calls.add(call);
            return null;
          });

      await setDesktopWindowTitle('contract-preseed-title');
      calls.clear();
      final settingsCubit = await _createSettingsCubit(_enManuscriptSettings);
      addTearDown(settingsCubit.close);

      await tester.pumpWidget(_buildRevelationApp(settingsCubit));
      await pumpFrames(tester, count: 6);

      final titleWidget = tester.widget<Title>(find.byType(Title).first);
      await tester.pump();

      expect(titleWidget.title, 'Revelation');
      expect(
        calls.any(
          (call) =>
              call.method == 'setWindowTitle' &&
              (call.arguments as Map<Object?, Object?>)['title'] ==
                  'Revelation',
        ),
        isTrue,
      );
      debugDefaultTargetPlatformOverride = null;
    });

    testWidgets('onGenerateTitle does not touch desktop channel on mobile', (
      tester,
    ) async {
      debugDefaultTargetPlatformOverride = TargetPlatform.android;
      final calls = <MethodCall>[];
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(desktopChannel, (call) async {
            calls.add(call);
            return null;
          });
      final settingsCubit = await _createSettingsCubit(_ruSkySettings);
      addTearDown(settingsCubit.close);

      await tester.pumpWidget(_buildRevelationApp(settingsCubit));
      await pumpFrames(tester, count: 6);

      final titleWidget = tester.widget<Title>(find.byType(Title).first);
      await tester.pump();

      expect(
        titleWidget.title,
        lookupAppLocalizations(const Locale('ru')).app_name,
      );
      expect(calls, isEmpty);
      debugDefaultTargetPlatformOverride = null;
    });
  });
}

Widget _buildRevelationApp(SettingsCubit settingsCubit) {
  return MultiBlocProvider(
    providers: AppDi.appBlocProviders(settingsCubit: settingsCubit),
    child: const RevelationApp(),
  );
}

Future<SettingsCubit> _createSettingsCubit(AppSettings settings) async {
  final cubit = SettingsCubit(
    FakeSettingsRepository(initialSettings: settings),
  );
  await cubit.loadSettings();
  return cubit;
}

class _HandledError {
  const _HandledError({
    required this.error,
    required this.stackTrace,
    required this.message,
  });

  final Object error;
  final StackTrace? stackTrace;
  final Object? message;
}

class _RecordingTalker extends Talker {
  _RecordingTalker() : super(settings: TalkerSettings(useConsoleLogs: false));

  final List<_HandledError> handled = <_HandledError>[];

  @override
  void handle(Object exception, [StackTrace? stackTrace, dynamic msg]) {
    handled.add(
      _HandledError(error: exception, stackTrace: stackTrace, message: msg),
    );
  }
}

final _enManuscriptSettings = AppSettings(
  selectedLanguage: 'en',
  selectedTheme: 'manuscript',
  selectedFontSize: 'medium',
  soundEnabled: false,
);

final _esForestSettings = AppSettings(
  selectedLanguage: 'es',
  selectedTheme: 'forest',
  selectedFontSize: 'large',
  soundEnabled: false,
);

final _ruSkySettings = AppSettings(
  selectedLanguage: 'ru',
  selectedTheme: 'sky',
  selectedFontSize: 'small',
  soundEnabled: false,
);
