import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/app/startup/bloc/app_startup_cubit.dart';
import 'package:revelation/app/startup/bloc/app_startup_state.dart';
import 'package:revelation/app/startup/screens/app_startup_screen.dart';
import 'package:revelation/app/startup/startup_error_reporter.dart';
import 'package:revelation/core/analytics/app_analytics_reporter.dart';
import 'package:revelation/core/logging/app_bloc_observer.dart';
import 'package:revelation/core/logging/app_logger_formatter.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/features/settings/settings.dart' show SettingsCubit;
import 'package:revelation/infra/analytics/sentry/sentry_app_analytics_reporter.dart';
import 'package:revelation/infra/analytics/sentry/sentry_app_runner.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/theme/material_theme.dart';
import 'package:sentry_flutter/sentry_flutter.dart'
    show SentryWidgetsFlutterBinding;
import 'package:talker_flutter/talker_flutter.dart';

typedef AppStartCallback = Future<void> Function(Talker talker);
typedef RunAppCallback = void Function(Widget app);
typedef AppBindingInitializer = WidgetsBinding Function();
typedef SentryAppRunner =
    Future<void> Function(Future<void> Function() appRunner);
typedef RunEntryPointCallback =
    Future<void> Function({
      required Talker talker,
      required AppStartCallback startAppCallback,
    });

@visibleForTesting
Future<void> Function() launchRevelationAppCallback = launchRevelationApp;

@visibleForTesting
StartupSettingsCubitLoader defaultInitializeSettingsCubit = (talker) =>
    defaultAppBootstrapFactory(talker).initialize();

@visibleForTesting
AppBootstrapFactory defaultAppBootstrapFactory = (talker) =>
    AppBootstrap(talker: talker);

Future<void> main() async {
  await launchRevelationAppCallback();
}

@visibleForTesting
Future<void> launchRevelationApp({
  Talker Function()? createTalker,
  void Function(Talker talker)? configureCore,
  RunEntryPointCallback? runEntryPoint,
  AppStartCallback? startAppCallback,
}) async {
  final talker = (createTalker ?? createAppTalker)();
  (configureCore ?? configureAppCore)(talker);
  await (runEntryPoint ?? runAppEntryPoint)(
    talker: talker,
    startAppCallback: startAppCallback ?? startApp,
  );
}

Talker createAppTalker() {
  return TalkerFlutter.init(
    logger: TalkerLogger(formatter: AppLoggerFormatter()),
  );
}

void configureAppCore(Talker talker) {
  final analyticsReporter = SentryAppAnalyticsReporter();
  AppDi.registerCore(talker: talker, analyticsReporter: analyticsReporter);
  Bloc.observer = AppBlocObserver(
    talker: talker,
    analyticsReporter: analyticsReporter,
  );
}

@visibleForTesting
Future<void> runAppEntryPoint({
  required Talker talker,
  required AppStartCallback startAppCallback,
  AppBindingInitializer? initializeBinding,
  SentryAppRunner? sentryAppRunner,
}) async {
  final analyticsReporter = _resolveAnalyticsReporter();
  final startupFuture = runZonedGuarded<Future<void>>(
    () async {
      (initializeBinding ?? SentryWidgetsFlutterBinding.ensureInitialized)();
      await (sentryAppRunner ?? runWithSentry)(() async {
        try {
          await startAppCallback(talker);
        } catch (error, stack) {
          _handleTopLevelException(
            talker,
            analyticsReporter,
            error,
            stack,
            'Uncaught app exception (zone)',
          );
        }
      });
    },
    (Object error, StackTrace stack) {
      _handleTopLevelException(
        talker,
        analyticsReporter,
        error,
        stack,
        'Uncaught app exception (zone)',
      );
    },
  );
  if (startupFuture != null) {
    await startupFuture;
  }
}

AppAnalyticsReporter _resolveAnalyticsReporter() {
  final getIt = GetIt.I;
  if (getIt.isRegistered<AppAnalyticsReporter>()) {
    return getIt<AppAnalyticsReporter>();
  }
  return const NoopAppAnalyticsReporter();
}

void _handleTopLevelException(
  Talker talker,
  AppAnalyticsReporter analyticsReporter,
  Object error,
  StackTrace stack,
  String source,
) {
  talker.handle(error, stack, source);
  unawaited(
    analyticsReporter
        .captureException(error, stack, source: source, fatal: true)
        .catchError((Object analyticsError, StackTrace analyticsStackTrace) {
          talker.handle(
            analyticsError,
            analyticsStackTrace,
            'Failed to report top-level exception to analytics',
          );
        }),
  );
}

@visibleForTesting
Future<void> startApp(
  Talker talker, {
  StartupSettingsCubitLoader? initializeSettingsCubit,
  RunAppCallback? runAppCallback,
}) async {
  (runAppCallback ?? runApp)(
    BlocProvider<AppStartupCubit>(
      create: (_) => AppStartupCubit(
        talker: talker,
        appBootstrapFactory: defaultAppBootstrapFactory,
        initializeSettingsCubit: initializeSettingsCubit,
      ),
      child: const RevelationStartupHost(),
    ),
  );
}

class RevelationStartupHost extends StatelessWidget {
  const RevelationStartupHost({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AppStartupCubit, AppStartupState>(
      builder: (context, state) {
        final startupCubit = context.read<AppStartupCubit>();
        final settingsCubit = startupCubit.initializedSettingsCubit;
        if (state.isReady && settingsCubit != null) {
          return MultiBlocProvider(
            providers: AppDi.appBlocProviders(settingsCubit: settingsCubit),
            child: const RevelationApp(),
          );
        }

        return MaterialApp(
          debugShowCheckedModeBanner: false,
          locale: Locale(state.localeCode),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          title: 'Revelation',
          theme: ThemeData(
            fontFamily: 'Arimo',
            colorScheme: const ColorScheme.dark(
              primary: Color(0xFFF2C48E),
              secondary: Color(0xFFE5B06B),
              surface: Color(0xFF17120E),
            ),
            scaffoldBackgroundColor: const Color(0xFF0D0907),
            useMaterial3: true,
          ),
          home: AppStartupScreen(
            state: state,
            onRetry: state.failure != null ? startupCubit.retry : null,
            onReportError: state.failure != null
                ? (screenContext) => reportStartupFailure(screenContext, state)
                : null,
          ),
        );
      },
    );
  }
}

class RevelationApp extends StatelessWidget {
  const RevelationApp({super.key});

  @override
  Widget build(BuildContext context) {
    final settings = context.select(
      (SettingsCubit cubit) => cubit.state.settings,
    );
    final currentLocale = Locale(settings.selectedLanguage);
    final colorScheme = MaterialTheme.getColorTheme(settings.selectedTheme);
    final textTheme = MaterialTheme.getTextTheme(
      context,
      settings.selectedFontSize,
    );
    final appRouter = AppRouter();
    final materialApp = MaterialApp.router(
      debugShowCheckedModeBanner: false,
      routerDelegate: appRouter.router.routerDelegate,
      routeInformationParser: appRouter.router.routeInformationParser,
      routeInformationProvider: appRouter.router.routeInformationProvider,
      title: 'Revelation',
      locale: currentLocale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('es'),
        Locale('uk'),
        Locale('ru'),
      ],
      onGenerateTitle: onGenerateTitle,
      theme: ThemeData(
        fontFamily: 'Arimo',
        colorScheme: colorScheme,
        textTheme: textTheme,
        useMaterial3: true,
      ),
    );
    return materialApp;
  }

  String onGenerateTitle(BuildContext context) {
    final title = AppLocalizations.of(context)!.app_name;
    if (isDesktop()) {
      unawaited(setDesktopWindowTitle(title));
    }
    return title;
  }
}
