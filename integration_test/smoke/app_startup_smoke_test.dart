import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
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
import 'webview_test_data.dart';

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
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      await SystemChrome.setPreferredOrientations(<DeviceOrientation>[
        DeviceOrientation.portraitUp,
      ]);
      addTearDown(
        () => SystemChrome.setPreferredOrientations(<DeviceOrientation>[]),
      );
    }
    await app.main();
    await tester.pump();

    expect(find.byType(AppStartupScreen), findsOneWidget);
    _expectInsideSystemInsets(
      tester,
      find.byKey(const ValueKey<String>('startup-panel')),
    );

    startupCompleter.complete(settingsCubit!);
    await pumpAndSettleSmoke(tester);

    expect(find.byType(MainScreen), findsOneWidget);

    final context = tester.element(find.byType(MainScreen));
    final l10n = AppLocalizations.of(context)!;
    expect(find.byTooltip(l10n.menu), findsOneWidget);
    _expectInsideSystemInsets(tester, find.byTooltip(l10n.menu));

    await tester.tap(find.byTooltip(l10n.menu));
    await pumpAndSettleSmoke(tester);
    _expectInsideSystemInsets(tester, find.text(l10n.bible_screen));
    Scaffold.of(tester.element(find.byTooltip(l10n.menu))).closeDrawer();
    await pumpAndSettleSmoke(tester);

    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      final view = View.of(context);
      // A native Android run must observe real system bars, not zeroed test data.
      expect(view.viewPadding.top, greaterThan(0));
      await SystemChrome.setPreferredOrientations(<DeviceOrientation>[
        DeviceOrientation.landscapeLeft,
      ]);
      for (var attempt = 0; attempt < 60; attempt++) {
        await tester.pump(const Duration(milliseconds: 100));
        if (view.physicalSize.width > view.physicalSize.height) break;
      }
      expect(view.physicalSize.width, greaterThan(view.physicalSize.height));
      _expectInsideSystemInsets(tester, find.byTooltip(l10n.menu));
    }
    expect(tester.takeException(), isNull);
  });

  testWidgets('Android WebView loads local HTML and executes JavaScript', (
    tester,
  ) async {
    final loaded = Completer<void>();
    InAppWebViewController? webViewController;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SafeArea(
            child: InAppWebView(
              initialSettings: InAppWebViewSettings(javaScriptEnabled: true),
              initialData: InAppWebViewInitialData(
                data: rev142WebViewHtml,
                baseUrl: WebUri('https://localhost/'),
              ),
              onWebViewCreated: (controller) => webViewController = controller,
              onLoadStop: (controller, _) async {
                final text = await controller.evaluateJavascript(
                  source: "document.getElementById('status')?.textContent",
                );
                if (text == webViewReadyText && !loaded.isCompleted) {
                  loaded.complete();
                }
              },
            ),
          ),
        ),
      ),
    );
    await tester.runAsync(
      () => loaded.future.timeout(const Duration(seconds: 30)),
    );
    // Apply window metrics delivered while the native page was loading.
    await pumpAndSettleSmoke(tester);
    expect(webViewController, isNotNull);
    _expectInsideSystemInsets(tester, find.byType(InAppWebView));
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  }, skip: kIsWeb || defaultTargetPlatform != TargetPlatform.android);
}

void _expectInsideSystemInsets(WidgetTester tester, Finder finder) {
  final context = tester.element(finder);
  final media = MediaQueryData.fromView(View.of(context));
  final rect = tester.getRect(finder);
  expect(rect.left, greaterThanOrEqualTo(media.viewPadding.left));
  expect(rect.top, greaterThanOrEqualTo(media.viewPadding.top));
  expect(
    rect.right,
    lessThanOrEqualTo(media.size.width - media.viewPadding.right),
  );
  expect(
    rect.bottom,
    lessThanOrEqualTo(media.size.height - media.viewPadding.bottom),
  );
}

ByteData _assetFor(String key) {
  final normalizedKey = key.toLowerCase();
  const assetManifestEntry = <String, List<Map<String, Object?>>>{
    'assets/images/UI/startup_splash_banner.jpg': <Map<String, Object?>>[
      <String, Object?>{'asset': 'assets/images/UI/startup_splash_banner.jpg'},
    ],
  };
  if (key == 'AssetManifest.bin' || key == 'AssetManifest.bin.json') {
    final manifest = const StandardMessageCodec().encodeMessage(
      assetManifestEntry,
    )!;
    if (key == 'AssetManifest.bin') return manifest;
    // Web loads the same binary manifest wrapped in JSON/base64.
    return ByteData.sublistView(
      Uint8List.fromList(
        utf8.encode(jsonEncode(base64Encode(Uint8List.sublistView(manifest)))),
      ),
    );
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
