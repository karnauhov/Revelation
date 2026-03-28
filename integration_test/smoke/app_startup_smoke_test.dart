import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_cubit.dart';
import 'package:revelation/features/topics/presentation/screens/main_screen.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
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
  SettingsCubit? settingsCubit;
  TopicsCatalogCubit? topicsCubit;

  setUp(() async {
    previousBlocObserver = Bloc.observer;
    previousLaunchRevelationAppCallback = app.launchRevelationAppCallback;
    settingsCubit = null;
    topicsCubit = null;
    await GetIt.I.reset();
    AudioController.setInstanceForTest(_SilentAudioController());

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

      topicsCubit = TopicsCatalogCubit(
        topicsRepository: _FixedTopicsRepository(topics: const <TopicInfo>[]),
        settingsCubit: settingsCubit!,
      );

      runApp(
        MultiBlocProvider(
          providers: <BlocProvider<dynamic>>[
            BlocProvider<SettingsCubit>.value(value: settingsCubit!),
            BlocProvider<TopicsCatalogCubit>.value(value: topicsCubit!),
          ],
          child: const app.RevelationApp(),
        ),
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
    await topicsCubit?.close();
    await settingsCubit?.close();
    AudioController.resetForTest();
    await GetIt.I.reset();
  });

  testWidgets('App startup smoke: main entry renders home shell', (
    tester,
  ) async {
    await app.main();
    await pumpAndSettleSmoke(tester);

    expect(find.byType(MainScreen), findsOneWidget);

    final context = tester.element(find.byType(MainScreen));
    final l10n = AppLocalizations.of(context)!;
    expect(find.byTooltip(l10n.menu), findsOneWidget);
  });
}

ByteData _assetFor(String key) {
  if (key.toLowerCase().endsWith('.png')) {
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

class _FixedTopicsRepository extends TopicsRepository {
  _FixedTopicsRepository({required this.topics})
    : super(dataSource: _NoopTopicsDataSource());

  final List<TopicInfo> topics;

  @override
  Future<AppResult<List<TopicInfo>>> getTopics({
    required String language,
  }) async {
    return AppSuccess<List<TopicInfo>>(topics);
  }

  @override
  Future<AppResult<TopicResource?>> getCommonResource(String key) async {
    return const AppSuccess<TopicResource?>(null);
  }
}

class _NoopTopicsDataSource implements TopicsDataSource {
  @override
  Future<void> updateLanguage(String language) async {}

  @override
  Future<List<Article>> fetchArticles({bool onlyVisible = true}) async =>
      const <Article>[];

  @override
  Future<String> fetchArticleMarkdown(String route) async => '';

  @override
  Future<Article?> fetchArticleByRoute(String route) async => null;

  @override
  Future<CommonResource?> fetchCommonResource(String key) async => null;
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
