import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_cache_manager/flutter_cache_manager.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/managers/db_manager.dart';
import 'package:revelation/repositories/primary_sources_repository.dart';
import 'package:revelation/theme.dart';
import 'package:revelation/managers/server_manager.dart';
import 'package:revelation/utils/app_logger_formatter.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:window_manager/window_manager.dart';
import 'package:get_it/get_it.dart';
import 'repositories/settings_repository.dart';
import 'viewmodels/main_view_model.dart';
import 'viewmodels/primary_sources_view_model.dart';
import 'viewmodels/settings_view_model.dart';
import 'utils/common.dart';
import 'app_router.dart';

void main() async {
  final talker = TalkerFlutter.init(
    logger: TalkerLogger(formatter: AppLoggerFormatter()),
  );
  final getIt = GetIt.instance;
  getIt.registerSingleton<Talker>(talker);

  runZonedGuarded(
    () async {
      WidgetsFlutterBinding.ensureInitialized();

      FlutterError.onError = (FlutterErrorDetails details) {
        talker.handle(
          details.exception,
          details.stack ?? StackTrace.current,
          'Flutter framework error',
        );
        FlutterError.presentError(details);
      };

      PlatformDispatcher.instance.onError = (Object error, StackTrace stack) {
        talker.handle(error, stack, 'PlatformDispatcher uncaught error');
        return true;
      };

      if (isWeb()) {
        final userAgent = getUserAgent();
        final mobileBrowser = isMobileBrowser() ? " (mobile browser)" : "";
        log.info("Started on web '$userAgent'$mobileBrowser");
      } else {
        log.info("Started on ${getPlatform()}");
      }

      if (isDesktop()) {
        await windowManager.ensureInitialized();
        WindowOptions windowOptions = const WindowOptions(
          size: Size(800, 650),
          minimumSize: Size(800, 650),
          center: true,
        );
        windowManager.waitUntilReadyToShow(windowOptions, () async {
          await windowManager.setIcon('assets/images/UI/app_icon.png');
          await windowManager.show();
          await windowManager.focus();
        });
      }

      getIt.registerLazySingleton<BaseCacheManager>(
        () => DefaultCacheManager(),
      );
      final settingsViewModel = SettingsViewModel(SettingsRepository());
      await settingsViewModel.loadSettings();

      final isServerConnected = await ServerManager().init();
      if (isServerConnected) {
        await DBManager().init(settingsViewModel.settings.selectedLanguage);
        settingsViewModel.addListener(() {
          DBManager().updateLanguage(
            settingsViewModel.settings.selectedLanguage,
          );
        });
      }

      runApp(
        MultiProvider(
          providers: [
            ChangeNotifierProvider<MainViewModel>(
              create: (_) => MainViewModel(),
            ),
            ChangeNotifierProvider<SettingsViewModel>(
              create: (_) => settingsViewModel,
            ),
            ChangeNotifierProvider<PrimarySourcesViewModel>(
              create: (_) =>
                  PrimarySourcesViewModel(PrimarySourcesRepository()),
            ),
          ],
          child: const RevelationApp(),
        ),
      );
    },
    (Object error, StackTrace stack) {
      talker.handle(error, stack, 'Uncaught app exception (zone)');
    },
  );
}

class RevelationApp extends StatelessWidget {
  const RevelationApp({super.key});

  @override
  Widget build(BuildContext context) {
    final settingsViewModel = context.watch<SettingsViewModel>();
    final currentLocale = Locale(settingsViewModel.settings.selectedLanguage);
    final colorScheme = MaterialTheme.getColorTheme(
      settingsViewModel.settings.selectedTheme,
    );
    final textTheme = MaterialTheme.getTextTheme(
      context,
      settingsViewModel.settings.selectedFontSize,
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
    String title = AppLocalizations.of(context)!.app_name;
    if (isDesktop()) {
      windowManager.setTitle(title);
      windowManager.setIcon('assets/images/UI/app_icon.png');
    }
    return title;
  }
}
