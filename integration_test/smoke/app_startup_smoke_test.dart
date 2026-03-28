import 'dart:async';
import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/app/startup/screens/app_startup_screen.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/presentation/screens/main_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/main.dart' as app;
import 'package:revelation/shared/models/app_settings.dart';
import 'package:talker_flutter/talker_flutter.dart';

import 'smoke_test_harness.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  const desktopChannel = MethodChannel('revelation/window');

  late BlocObserver previousBlocObserver;
  late Future<void> Function() previousLaunchRevelationAppCallback;
  late Completer<SettingsCubit> startupCompleter;
  SettingsCubit? settingsCubit;

  setUp(() async {
    previousBlocObserver = Bloc.observer;
    previousLaunchRevelationAppCallback = app.launchRevelationAppCallback;
    startupCompleter = Completer<SettingsCubit>();
    settingsCubit = null;
    await GetIt.I.reset();
    AudioController.setInstanceForTest(_SilentAudioController());
    PackageInfo.setMockInitialValues(
      appName: 'Revelation',
      packageName: 'revelation',
      version: '1.0.5-test',
      buildNumber: '141',
      buildSignature: '',
    );

    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', (message) async {
          if (message == null) {
            return null;
          }
          final key = utf8.decode(message.buffer.asUint8List());
          return _assetFor(key);
        });

    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(desktopChannel, (_) async => null);

    app.launchRevelationAppCallback = () async {
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      app.configureAppCore(talker);

      settingsCubit = SettingsCubit(
        _FakeSettingsRepository(
          initialSettings: AppSettings(
            selectedLanguage: 'en',
            selectedTheme: 'manuscript',
            selectedFontSize: 'medium',
            soundEnabled: true,
          ),
        ),
      );
      await settingsCubit!.loadSettings();

      await app.startApp(
        talker,
        initializeSettingsCubit: (_) async {
          return startupCompleter.future;
        },
      );
    };
  });

  tearDown(() async {
    Bloc.observer = previousBlocObserver;
    app.launchRevelationAppCallback = previousLaunchRevelationAppCallback;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', null);
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(desktopChannel, null);
    await settingsCubit?.close();
    AudioController.resetForTest();
    await GetIt.I.reset();
  });

  testWidgets('App startup smoke: splash resolves into home shell', (
    tester,
  ) async {
    await app.main();
    await tester.pump();

    expect(find.byType(AppStartupScreen), findsOneWidget);

    startupCompleter.complete(settingsCubit!);
    await pumpAndSettleSmoke(tester);

    expect(find.byType(MainScreen), findsOneWidget);

    final context = tester.element(find.byType(MainScreen));
    final l10n = AppLocalizations.of(context)!;
    expect(find.byTooltip(l10n.menu), findsOneWidget);
  });
}

ByteData _assetFor(String key) {
  final normalizedKey = key.toLowerCase();
  const assetManifestEntry = <String, List<Map<String, Object?>>>{
    'assets/images/UI/startup_splash_banner.jpg': <Map<String, Object?>>[
      <String, Object?>{'asset': 'assets/images/UI/startup_splash_banner.jpg'},
    ],
  };
  if (key == 'AssetManifest.bin') {
    return const StandardMessageCodec().encodeMessage(assetManifestEntry)!;
  }
  if (key == 'AssetManifest.json') {
    return ByteData.sublistView(
      Uint8List.fromList(utf8.encode(jsonEncode(assetManifestEntry))),
    );
  }
  if (key == 'FontManifest.json') {
    return ByteData.sublistView(Uint8List.fromList(utf8.encode('[]')));
  }
  if (normalizedKey.endsWith('.png')) {
    return ByteData.sublistView(_pngBytes);
  }
  if (normalizedKey.endsWith('.jpg') || normalizedKey.endsWith('.jpeg')) {
    return ByteData.sublistView(_pngBytes);
  }
  return ByteData.sublistView(_svgBytes);
}

class _SilentAudioController extends AudioController {
  _SilentAudioController() : super.forTest();

  @override
  Future<void> init({required bool Function() isSoundEnabled}) async {}

  @override
  void playSound(String sourceName) {}
}

class _FakeSettingsRepository extends SettingsRepository {
  _FakeSettingsRepository({required this.initialSettings});

  AppSettings initialSettings;

  @override
  Future<AppSettings> getSettings() async => initialSettings;

  @override
  Future<void> saveSettings(AppSettings settings) async {
    initialSettings = settings;
  }
}

final Uint8List _svgBytes = Uint8List.fromList(
  utf8.encode('<svg viewBox="0 0 24 24"></svg>'),
);

final Uint8List _pngBytes = Uint8List.fromList(<int>[
  0x89,
  0x50,
  0x4E,
  0x47,
  0x0D,
  0x0A,
  0x1A,
  0x0A,
  0x00,
  0x00,
  0x00,
  0x0D,
  0x49,
  0x48,
  0x44,
  0x52,
  0x00,
  0x00,
  0x00,
  0x01,
  0x00,
  0x00,
  0x00,
  0x01,
  0x08,
  0x06,
  0x00,
  0x00,
  0x00,
  0x1F,
  0x15,
  0xC4,
  0x89,
  0x00,
  0x00,
  0x00,
  0x0A,
  0x49,
  0x44,
  0x41,
  0x54,
  0x78,
  0x9C,
  0x63,
  0x00,
  0x01,
  0x00,
  0x00,
  0x05,
  0x00,
  0x01,
  0x0D,
  0x0A,
  0x2D,
  0xB4,
  0x00,
  0x00,
  0x00,
  0x00,
  0x49,
  0x45,
  0x4E,
  0x44,
  0xAE,
  0x42,
  0x60,
  0x82,
]);
