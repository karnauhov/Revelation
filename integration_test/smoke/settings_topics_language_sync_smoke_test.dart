import 'dart:async';
import 'dart:ui' show ViewFocusDirection, ViewFocusEvent, ViewFocusState;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/app/startup/screens/app_startup_screen.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/features/topics/presentation/bloc/topics_catalog_cubit.dart';
import 'package:revelation/features/topics/presentation/widgets/topic_list.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/main.dart' as app;
import 'package:revelation/shared/models/app_settings.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'smoke_test_harness.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Cold settings preserves focus through startup on four locales', (
    tester,
  ) async {
    final semantics = tester.ensureSemantics();
    final dispatcher = tester.binding.platformDispatcher;
    dispatcher.defaultRouteNameTestValue = '/settings';
    addTearDown(dispatcher.clearDefaultRouteNameTestValue);
    final results = <String>[];
    var activeLanguage = '';
    var stage = 'initialization';
    try {
      for (final language in ['en', 'es', 'uk', 'ru']) {
        activeLanguage = language;
        stage = 'configure startup';
        await GetIt.I.reset();
        final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
        AppDi.registerCore(talker: talker);
        final settings = SettingsCubit(
          _FakeSettingsRepository(
            initialSettings: AppSettings(
              selectedLanguage: language,
              selectedTheme: 'manuscript',
              selectedFontSize: 'medium',
              soundEnabled: false,
            ),
          ),
        );
        await settings.loadSettings();
        final startup = Completer<SettingsCubit>();
        await app.startApp(
          talker,
          initializeSettingsCubit: (_) => startup.future,
        );
        stage = 'render splash';
        await tester.pump();
        expect(find.byType(AppStartupScreen), findsOneWidget);
        final materialAppState = tester.state(find.byType(MaterialApp));
        stage = 'capture semantics owner';
        final owner = tester.binding.renderViews.single.owner!.semanticsOwner!;
        var focusEvents = 0;
        void focusDuringSemantics() {
          focusEvents++;
          tester.binding.handleViewFocusChanged(
            ViewFocusEvent(
              viewId: tester.view.viewId,
              state: ViewFocusState.focused,
              direction: ViewFocusDirection.forward,
            ),
          );
        }

        owner.addListener(focusDuringSemantics);
        try {
          stage = 'complete startup';
          startup.complete(settings);
          await pumpAndSettleSmoke(tester);
          stage = 'verify startup';
          expect(tester.takeException(), isNull);
          expect(focusEvents, greaterThan(0));
          expect(
            tester.state(find.byType(MaterialApp)),
            same(materialAppState),
          );
          expect(find.byType(SettingsScreen), findsOneWidget);
          expect(
            AppRouter().router.routeInformationProvider.value.uri.path,
            '/settings',
          );
          // Release builds omit key debug names used by the simulator fallback.
          await tester.sendKeyEvent(
            LogicalKeyboardKey.tab,
            physicalKey: PhysicalKeyboardKey.tab,
          );
          await tester.pump();
          stage = 'verify keyboard focus';
          final focused = FocusManager.instance.primaryFocus;
          expect(focused, isNotNull);
          expect(focused!.context!.findRenderObject()!.attached, isTrue);
          expect(tester.takeException(), isNull);
          results.add(language);
        } finally {
          owner.removeListener(focusDuringSemantics);
          await tester.pumpWidget(const SizedBox.shrink());
          await tester.pump();
        }
      }
      binding.reportData = {
        'coldSettingsFocusLocales': results,
        'focusDuringSemantics': true,
        'materialAppStatePreserved': true,
      };
    } catch (error, stackTrace) {
      binding.reportData = {
        'failedLanguage': activeLanguage,
        'failedStage': stage,
        'error': error.toString(),
        'stack': stackTrace.toString(),
        'completedLocales': results,
      };
      rethrow;
    } finally {
      semantics.dispose();
      await GetIt.I.reset();
    }
  });

  testWidgets('Settings language change propagates to topics catalog', (
    tester,
  ) async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(
        initialSettings: AppSettings(
          selectedLanguage: 'en',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: true,
        ),
      ),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    final topicsRepository = _FakeTopicsRepository(
      topicsByLanguage: <String, AppResult<List<TopicInfo>>>{
        'en': AppSuccess<List<TopicInfo>>(<TopicInfo>[
          TopicInfo(
            name: 'Topic EN',
            idIcon: '',
            description: 'Description EN',
            route: 'topic-en',
          ),
        ]),
        'ru': AppSuccess<List<TopicInfo>>(<TopicInfo>[
          TopicInfo(
            name: 'Topic RU',
            idIcon: '',
            description: 'Description RU',
            route: 'topic-ru',
          ),
        ]),
      },
    );
    final topicsCubit = TopicsCatalogCubit(
      topicsRepository: topicsRepository,
      settingsCubit: settingsCubit,
    );
    addTearDown(topicsCubit.close);

    await tester.pumpWidget(
      MultiBlocProvider(
        providers: <BlocProvider>[
          BlocProvider<SettingsCubit>.value(value: settingsCubit),
          BlocProvider<TopicsCatalogCubit>.value(value: topicsCubit),
        ],
        child: MaterialApp(
          locale: const Locale('en'),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          routes: <String, WidgetBuilder>{
            '/': (_) => const _TopicsHostScreen(),
            '/settings': (_) => const SettingsScreen(),
          },
        ),
      ),
    );
    await pumpAndSettleSmoke(tester);

    expect(find.text('Topic EN'), findsOneWidget);

    await tester.tap(find.byKey(const Key('open-settings')));
    await pumpAndSettleSmoke(tester);

    final settingsContext = tester.element(find.byType(SettingsScreen));
    final l10n = AppLocalizations.of(settingsContext)!;
    await tester.tap(find.text(l10n.language));
    await pumpAndSettleSmoke(tester);
    await tester.tap(find.text('Русский').last);
    await pumpAndSettleSmoke(tester);

    await tester.pageBack();
    await pumpAndSettleSmoke(tester);

    expect(find.text('Topic RU'), findsOneWidget);
    expect(topicsRepository.requestedLanguages, contains('en'));
    expect(topicsRepository.requestedLanguages, contains('ru'));
  });
}

class _TopicsHostScreen extends StatelessWidget {
  const _TopicsHostScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: <Widget>[
          IconButton(
            key: const Key('open-settings'),
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.of(context).pushNamed('/settings'),
          ),
        ],
      ),
      body: const TopicList(),
    );
  }
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

class _FakeTopicsRepository extends TopicsRepository {
  _FakeTopicsRepository({required this.topicsByLanguage})
    : super(dataSource: _NoopTopicsDataSource());

  final Map<String, AppResult<List<TopicInfo>>> topicsByLanguage;
  final List<String> requestedLanguages = <String>[];

  @override
  Future<AppResult<List<TopicInfo>>> getTopics({
    required String language,
  }) async {
    requestedLanguages.add(language);
    return topicsByLanguage[language] ??
        const AppFailureResult<List<TopicInfo>>(
          AppFailure.notFound('No topics for requested language.'),
        );
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
