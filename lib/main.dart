import 'package:flutter/material.dart';
import 'package:flutter_cache_manager/flutter_cache_manager.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:window_manager/window_manager.dart';
import 'package:get_it/get_it.dart';
import 'viewmodels/main_view_model.dart';
import 'utils/common.dart';
import 'app_router.dart';

void main() async {
  if (isWeb()) {
    log.d("Started on web");
  } else {
    log.d("Started on ${getPlatform()}");
  }

  if (isDesktop()) {
    WidgetsFlutterBinding.ensureInitialized();
    await windowManager.ensureInitialized();
    WindowOptions windowOptions = const WindowOptions(
        size: Size(800, 600), minimumSize: Size(800, 600), center: true);
    windowManager.waitUntilReadyToShow(windowOptions, () async {
      await windowManager.show();
      await windowManager.focus();
    });
  }

  final getIt = GetIt.instance;
  getIt.registerLazySingleton<BaseCacheManager>(() => DefaultCacheManager());

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => MainViewModel()..initializeData(),
        ),
      ],
      child: const RevelationApp(),
    ),
  );
}

class RevelationApp extends StatelessWidget {
  const RevelationApp({super.key});

  @override
  Widget build(BuildContext context) {
    final appRouter = AppRouter();
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      routerDelegate: appRouter.router.routerDelegate,
      routeInformationParser: appRouter.router.routeInformationParser,
      routeInformationProvider: appRouter.router.routeInformationProvider,
      title: "Revelation",
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('uk'),
        Locale('ru'),
      ],
      onGenerateTitle: onGenerateTitle,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
    );
  }

  String onGenerateTitle(BuildContext context) {
    String title = AppLocalizations.of(context)!.app_name;
    if (isDesktop()) {
      windowManager.setTitle(title);
    }
    return title;
  }
}
