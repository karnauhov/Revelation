@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/core/errors/app_result.dart';
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
import 'package:revelation/shared/models/app_settings.dart';

import '../../../../test_harness/fakes/fake_settings_repository.dart';

void main() {
  setUp(() {
    addTearDown(_suppressOverflowErrors());
  });

  testWidgets('MainScreen opens drawer from menu button', (tester) async {
    final harness = await _buildHarness();
    addTearDown(harness.dispose);
    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(MainScreen));
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.byTooltip(l10n.menu));
    await tester.pumpAndSettle();

    expect(find.text(l10n.settings_screen), findsOneWidget);
    expect(find.text(l10n.primary_sources_screen), findsOneWidget);
  });

  testWidgets('MainScreen plays stone sound on drawer open and manual close', (
    tester,
  ) async {
    final harness = await _buildHarness();
    addTearDown(harness.dispose);
    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(MainScreen));
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.byTooltip(l10n.menu));
    await tester.pumpAndSettle();
    await tester.binding.handlePopRoute();
    await tester.pumpAndSettle();

    final stoneSounds = harness.audio.playedSources
        .where((source) => source == 'stone')
        .toList();
    expect(stoneSounds, hasLength(2));
  });

  testWidgets(
    'MainScreen suppresses close sound when drawer closes via item tap',
    (tester) async {
      final harness = await _buildHarness();
      addTearDown(harness.dispose);
      await tester.pumpWidget(harness.app);
      await tester.pumpAndSettle();

      final context = tester.element(find.byType(MainScreen));
      final l10n = AppLocalizations.of(context)!;

      await tester.tap(find.byTooltip(l10n.menu));
      await tester.pumpAndSettle();
      await tester.tap(find.text(l10n.settings_screen));
      await tester.pumpAndSettle();

      final stoneSounds = harness.audio.playedSources
          .where((source) => source == 'stone')
          .toList();
      expect(find.text('settings-page'), findsOneWidget);
      expect(stoneSounds, hasLength(1));
    },
  );

  testWidgets('MainScreen navigates to primary sources and about from drawer', (
    tester,
  ) async {
    final harness = await _buildHarness();
    addTearDown(harness.dispose);
    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(MainScreen));
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.byTooltip(l10n.menu));
    await tester.pumpAndSettle();
    await tester.tap(find.text(l10n.primary_sources_screen));
    await tester.pumpAndSettle();
    expect(find.text('primary-sources-page'), findsOneWidget);

    await tester.binding.handlePopRoute();
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip(l10n.menu));
    await tester.pumpAndSettle();
    await tester.tap(find.text(l10n.about_screen));
    await tester.pumpAndSettle();
    expect(find.text('about-page'), findsOneWidget);
  });

  testWidgets(
    'MainScreen resets close-sound suppression after drawer item click',
    (tester) async {
      final harness = await _buildHarness();
      addTearDown(harness.dispose);
      await tester.pumpWidget(harness.app);
      await tester.pumpAndSettle();

      final context = tester.element(find.byType(MainScreen));
      final l10n = AppLocalizations.of(context)!;

      await tester.tap(find.byTooltip(l10n.menu));
      await tester.pumpAndSettle();
      await tester.tap(find.text(l10n.settings_screen));
      await tester.pumpAndSettle();

      await tester.binding.handlePopRoute();
      await tester.pumpAndSettle();

      await tester.tap(find.byTooltip(l10n.menu));
      await tester.pumpAndSettle();
      await tester.binding.handlePopRoute();
      await tester.pumpAndSettle();

      final stoneSounds = harness.audio.playedSources
          .where((source) => source == 'stone')
          .toList();
      expect(stoneSounds, hasLength(3));
    },
  );

  testWidgets('MainScreen respects disabled sound setting', (tester) async {
    final harness = await _buildHarness(soundEnabled: false);
    addTearDown(harness.dispose);
    await tester.pumpWidget(harness.app);
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(MainScreen));
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.byTooltip(l10n.menu));
    await tester.pumpAndSettle();
    await tester.binding.handlePopRoute();
    await tester.pumpAndSettle();

    expect(harness.audio.playedSources, isEmpty);
  });

  testWidgets(
    'MainScreen uses initialized audio and reads the latest sound setting',
    (tester) async {
      final harness = await _buildHarness(soundEnabled: true);
      addTearDown(harness.dispose);
      await tester.pumpWidget(harness.app);
      await tester.pumpAndSettle();

      expect(harness.audio.initCalls, 1);

      await harness.settingsCubit.setSoundEnabled(false);
      await tester.pump();

      final context = tester.element(find.byType(MainScreen));
      final l10n = AppLocalizations.of(context)!;

      await tester.tap(find.byTooltip(l10n.menu));
      await tester.pumpAndSettle();
      await tester.binding.handlePopRoute();
      await tester.pumpAndSettle();

      expect(harness.audio.playedSources, isEmpty);
    },
  );

  testWidgets(
    'MainScreen keeps drag listener disabled on non-desktop platforms',
    (tester) async {
      final harness = await _buildHarness(topicCount: 40);
      addTearDown(harness.dispose);
      await tester.pumpWidget(harness.app);
      await tester.pumpAndSettle();

      final scaffold = tester.widget<Scaffold>(find.byType(Scaffold));
      final body = scaffold.body as SizedBox;

      expect(body.child, isNot(isA<Listener>()));
    },
  );

  testWidgets(
    'MainScreen desktop drag scrolls topic list',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 700));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      final harness = await _buildHarness(topicCount: 40);
      addTearDown(harness.dispose);
      await tester.pumpWidget(harness.app);
      await tester.pumpAndSettle();

      final listenerFinder = find.byWidgetPredicate(
        (widget) =>
            widget is Listener &&
            widget.onPointerDown != null &&
            widget.onPointerMove != null &&
            widget.onPointerUp != null,
      );
      expect(listenerFinder, findsAtLeastNWidgets(1));

      final scrollableFinder = find.byType(Scrollable).first;
      final before = tester.state<ScrollableState>(scrollableFinder).position;
      expect(before.pixels, 0);

      final start = tester.getCenter(listenerFinder.first);
      final gesture = await tester.createGesture(kind: PointerDeviceKind.mouse);
      await gesture.addPointer(location: start);
      await gesture.down(start);
      await gesture.moveTo(Offset(start.dx, start.dy - 180));
      await gesture.up();
      await tester.pumpAndSettle();

      final after = tester.state<ScrollableState>(scrollableFinder).position;
      expect(after.pixels, greaterThan(0));
    },
    variant: TargetPlatformVariant.only(TargetPlatform.windows),
  );
}

Future<_MainScreenHarness> _buildHarness({
  bool soundEnabled = true,
  int topicCount = 0,
}) async {
  final audio = _SpyAudioController();
  AudioController.setInstanceForTest(audio);

  final settingsCubit = SettingsCubit(
    FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: soundEnabled,
      ),
    ),
  );
  await settingsCubit.loadSettings();
  await audio.init(
    isSoundEnabled: () => settingsCubit.state.settings.soundEnabled,
  );

  final topicsCubit = TopicsCatalogCubit(
    topicsRepository: _FixedTopicsRepository(
      topics: List<TopicInfo>.generate(
        topicCount,
        (index) => TopicInfo(
          name: 'Topic $index',
          idIcon: '',
          description: 'Description $index',
          route: 'topic_$index',
        ),
      ),
    ),
    settingsCubit: settingsCubit,
  );

  final router = GoRouter(
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        builder: (context, state) => MultiBlocProvider(
          providers: [
            BlocProvider<SettingsCubit>.value(value: settingsCubit),
            BlocProvider<TopicsCatalogCubit>.value(value: topicsCubit),
          ],
          child: const MainScreen(),
        ),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) =>
            const Scaffold(body: Text('settings-page')),
      ),
      GoRoute(
        path: '/primary_sources',
        builder: (context, state) =>
            const Scaffold(body: Text('primary-sources-page')),
      ),
      GoRoute(
        path: '/about',
        builder: (context, state) => const Scaffold(body: Text('about-page')),
      ),
      GoRoute(
        path: '/download',
        builder: (context, state) =>
            const Scaffold(body: Text('download-page')),
      ),
    ],
  );

  final app = MaterialApp.router(
    routerConfig: router,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    theme: ThemeData(
      textTheme: const TextTheme(bodyLarge: TextStyle(fontSize: 12)),
    ),
  );

  return _MainScreenHarness(
    app: app,
    audio: audio,
    settingsCubit: settingsCubit,
    topicsCubit: topicsCubit,
  );
}

class _MainScreenHarness {
  _MainScreenHarness({
    required this.app,
    required this.audio,
    required this.settingsCubit,
    required this.topicsCubit,
  });

  final Widget app;
  final _SpyAudioController audio;
  final SettingsCubit settingsCubit;
  final TopicsCatalogCubit topicsCubit;

  Future<void> dispose() async {
    await topicsCubit.close();
    await settingsCubit.close();
    AudioController.resetForTest();
  }
}

class _SpyAudioController extends AudioController {
  _SpyAudioController() : super.forTest();

  bool Function()? _isSoundEnabled;
  int initCalls = 0;
  final List<String> playedSources = <String>[];

  @override
  Future<void> init({required bool Function() isSoundEnabled}) async {
    initCalls += 1;
    _isSoundEnabled = isSoundEnabled;
  }

  @override
  void playSound(String sourceName) {
    final canPlay = _isSoundEnabled == null || _isSoundEnabled!();
    if (canPlay) {
      playedSources.add(sourceName);
    }
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

VoidCallback _suppressOverflowErrors() {
  final originalHandler = FlutterError.onError;
  FlutterError.onError = (details) {
    final message = details.exceptionAsString();
    if (message.contains('A RenderFlex overflowed by')) {
      return;
    }
    if (originalHandler != null) {
      originalHandler(details);
    }
  };

  return () {
    FlutterError.onError = originalHandler;
  };
}
