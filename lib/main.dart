import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/core/logging/app_bloc_observer.dart';
import 'package:revelation/core/logging/app_logger_formatter.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/features/settings/settings.dart' show SettingsCubit;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/theme/material_theme.dart';
import 'package:talker_flutter/talker_flutter.dart';

typedef AppStartCallback = Future<void> Function(Talker talker);
typedef InitializeSettingsCubit = Future<SettingsCubit> Function(Talker talker);
typedef RunAppCallback = void Function(Widget app);
typedef RunEntryPointCallback =
    Future<void> Function({
      required Talker talker,
      required AppStartCallback startAppCallback,
    });

@visibleForTesting
Future<void> Function() launchRevelationAppCallback = launchRevelationApp;

@visibleForTesting
InitializeSettingsCubit defaultInitializeSettingsCubit = (talker) =>
    AppBootstrap(talker: talker).initialize();

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
  AppDi.registerCore(talker: talker);
  Bloc.observer = AppBlocObserver(talker: talker);
}

@visibleForTesting
Future<void> runAppEntryPoint({
  required Talker talker,
  required AppStartCallback startAppCallback,
}) async {
  runZonedGuarded(
    () async {
      await startAppCallback(talker);
    },
    (Object error, StackTrace stack) {
      talker.handle(error, stack, 'Uncaught app exception (zone)');
    },
  );
}

@visibleForTesting
Future<void> startApp(
  Talker talker, {
  InitializeSettingsCubit? initializeSettingsCubit,
  RunAppCallback? runAppCallback,
}) async {
  final settingsCubit =
      await (initializeSettingsCubit ?? defaultInitializeSettingsCubit)(talker);
  (runAppCallback ?? runApp)(
    MultiBlocProvider(
      providers: AppDi.appBlocProviders(settingsCubit: settingsCubit),
      child: const RevelationApp(),
    ),
  );
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
      title: "Revelation",
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
