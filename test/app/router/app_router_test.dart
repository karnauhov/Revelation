@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/route_args.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/features/about/presentation/screens/about_screen.dart';
import 'package:revelation/features/download/presentation/screens/download_screen.dart';
import 'package:revelation/features/primary_sources/presentation/screens/primary_source_screen.dart';
import 'package:revelation/features/primary_sources/presentation/screens/primary_sources_screen.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/features/topics/presentation/screens/main_screen.dart';
import 'package:revelation/features/topics/presentation/screens/topic_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../test_harness/test_harness.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    AppDi.registerCore(
      talker: Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    AppRouter().router.go('/');
    await GetIt.I.reset();
  });

  testWidgets('topic deep link opens TopicScreen', (tester) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(
        uri: Uri(
          path: '/topic',
          queryParameters: <String, String>{
            'file': 'topic-1',
            'name': 'Topic 1',
          },
        ),
      ),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 20);

    expect(find.byType(TopicScreen), findsOneWidget);
  });

  testWidgets('topic pageBuilder handles TopicRouteArgs extra', (tester) async {
    final appRouter = AppRouter();
    final context = await pumpContext(tester);
    final topicRoute = _findGoRoute(appRouter: appRouter, path: '/topic');
    final page = topicRoute.pageBuilder!(
      context,
      _buildGoRouterState(
        appRouter: appRouter,
        path: '/topic',
        name: 'topic',
        extra: const TopicRouteArgs(
          file: 'topic-42',
          name: 'Topic 42',
          description: 'Route extra contract',
        ),
      ),
    );

    expect(page, isA<CustomTransitionPage<void>>());
    final transitionPage = page as CustomTransitionPage<void>;
    expect(transitionPage.child, isA<TopicScreen>());
    expect(transitionPage.arguments, 'topic-42');
  });

  testWidgets('root route opens MainScreen', (tester) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(uri: Uri(path: '/')),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 8);

    expect(find.byType(MainScreen), findsOneWidget);
  });

  testWidgets('invalid topic route args render fallback page', (tester) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(uri: Uri(path: '/topic')),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 12);

    expect(find.byType(TopicScreen), findsNothing);
    expect(find.byType(MaterialApp), findsOneWidget);
  });

  testWidgets('primary sources route opens PrimarySourcesScreen', (
    tester,
  ) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(
        uri: Uri(path: '/primary_sources'),
      ),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 8);

    expect(find.byType(PrimarySourcesScreen), findsOneWidget);
  });

  testWidgets('invalid primary source route args render fallback page', (
    tester,
  ) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(
        uri: Uri(path: '/primary_source'),
      ),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 12);

    expect(find.byType(PrimarySourceScreen), findsNothing);
    expect(find.byType(MaterialApp), findsOneWidget);
  });

  testWidgets(
    'primary source pageBuilder handles PrimarySourceRouteArgs extra',
    (tester) async {
      final source = _buildPrimarySource();
      final appRouter = AppRouter();
      final context = await pumpContext(tester);
      final route = _findGoRoute(appRouter: appRouter, path: '/primary_source');
      final page = route.pageBuilder!(
        context,
        _buildGoRouterState(
          appRouter: appRouter,
          path: '/primary_source',
          name: 'primary_source',
          extra: PrimarySourceRouteArgs(
            primarySource: source,
            pageName: '1',
            wordIndex: 0,
          ),
        ),
      );

      expect(page, isA<CustomTransitionPage<void>>());
      final transitionPage = page as CustomTransitionPage<void>;
      expect(transitionPage.arguments, source.id);
      expect(transitionPage.child, isA<PrimarySourceScreen>());
      final child = transitionPage.child as PrimarySourceScreen;
      expect(child.primarySource.id, source.id);
      expect(child.initialPageName, '1');
      expect(child.initialWordIndex, 0);
    },
  );

  testWidgets('settings route opens SettingsScreen', (tester) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(uri: Uri(path: '/settings')),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 8);

    expect(find.byType(SettingsScreen), findsOneWidget);
  });

  testWidgets('about route opens AboutScreen', (tester) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(uri: Uri(path: '/about')),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 8);

    expect(find.byType(AboutScreen), findsOneWidget);
  });

  testWidgets('download route opens DownloadScreen', (tester) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(uri: Uri(path: '/download')),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 8);

    expect(find.byType(DownloadScreen), findsOneWidget);
  });

  testWidgets('unknown route renders router error screen', (tester) async {
    final settingsCubit = await _createSettingsCubit();
    addTearDown(settingsCubit.close);
    final appRouter = AppRouter();
    final routeProvider = PlatformRouteInformationProvider(
      initialRouteInformation: RouteInformation(
        uri: Uri(path: '/unknown-route-for-contract-test'),
      ),
    );

    await tester.pumpWidget(
      _buildRouterHost(
        appRouter: appRouter,
        settingsCubit: settingsCubit,
        routeProvider: routeProvider,
      ),
    );
    await pumpFrames(tester, count: 6);

    expect(
      find.textContaining('/unknown-route-for-contract-test'),
      findsOneWidget,
    );
  });
}

Future<SettingsCubit> _createSettingsCubit() async {
  final cubit = SettingsCubit(
    FakeSettingsRepository(initialSettings: _testSettings),
  );
  await cubit.loadSettings();
  return cubit;
}

GoRoute _findGoRoute({required AppRouter appRouter, required String path}) {
  return appRouter.router.configuration.routes.whereType<GoRoute>().firstWhere(
    (route) => route.path == path,
  );
}

GoRouterState _buildGoRouterState({
  required AppRouter appRouter,
  required String path,
  required String name,
  Object? extra,
}) {
  return GoRouterState(
    appRouter.router.configuration,
    uri: Uri(path: path),
    matchedLocation: path,
    name: name,
    path: path,
    fullPath: path,
    pathParameters: const <String, String>{},
    extra: extra,
    pageKey: ValueKey<String>('test-$name-$path'),
  );
}

Widget _buildRouterHost({
  required AppRouter appRouter,
  required SettingsCubit settingsCubit,
  required RouteInformationProvider routeProvider,
}) {
  return MultiBlocProvider(
    providers: AppDi.appBlocProviders(settingsCubit: settingsCubit),
    child: MaterialApp.router(
      locale: const Locale('en'),
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      routerDelegate: appRouter.router.routerDelegate,
      routeInformationParser: appRouter.router.routeInformationParser,
      routeInformationProvider: routeProvider,
    ),
  );
}

final _testSettings = AppSettings(
  selectedLanguage: 'en',
  selectedTheme: 'manuscript',
  selectedFontSize: 'medium',
  soundEnabled: false,
);

PrimarySource _buildPrimarySource() {
  return PrimarySource(
    id: 'source-router-test',
    title: 'Router Test Source',
    date: 'Date',
    content: 'Content',
    quantity: 1,
    material: 'Material',
    textStyle: 'Style',
    found: 'Found',
    classification: 'Class',
    currentLocation: 'Location',
    preview: '',
    maxScale: 1,
    isMonochrome: false,
    pages: const [],
    attributes: const <Map<String, String>>[],
    permissionsReceived: false,
  );
}
