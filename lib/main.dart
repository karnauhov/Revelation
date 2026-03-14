import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/settings/settings.dart'
    show SettingsViewModel;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/theme/material_theme.dart';
import 'package:revelation/core/logging/app_logger_formatter.dart';
import 'package:revelation/shared/utils/common.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:revelation/app/router/app_router.dart';

void main() async {
  final talker = TalkerFlutter.init(
    logger: TalkerLogger(formatter: AppLoggerFormatter()),
  );
  AppDi.registerCore(talker: talker);

  runZonedGuarded(
    () async {
      final appBootstrap = AppBootstrap(talker: talker);
      final SettingsViewModel settingsViewModel = await appBootstrap
          .initialize();

      runApp(
        MultiProvider(
          providers: AppDi.appProviders(settingsViewModel: settingsViewModel),
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
    final title = AppLocalizations.of(context)!.app_name;
    if (isDesktop()) {
      unawaited(setDesktopWindowTitle(title));
    }
    return title;
  }
}
