import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/features/about/presentation/screens/about_screen.dart';
import 'package:revelation/features/download/presentation/screens/download_screen.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'smoke_test_harness.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    PackageInfo.setMockInitialValues(
      appName: 'Revelation',
      packageName: 'revelation',
      version: '1.0.0-test',
      buildNumber: '999',
      buildSignature: '',
    );
  });

  testWidgets('About smoke: renders localized shell and version metadata', (
    tester,
  ) async {
    final settingsCubit = SettingsCubit(
      _FakeSettingsRepository(initialSettings: _testSettings()),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    await tester.pumpWidget(
      BlocProvider<SettingsCubit>.value(
        value: settingsCubit,
        child: const MaterialApp(
          locale: Locale('en'),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: AboutScreen(),
        ),
      ),
    );
    await pumpAndSettleSmoke(tester);

    final context = tester.element(find.byType(AboutScreen));
    final l10n = AppLocalizations.of(context)!;

    expect(find.text(l10n.about_screen), findsOneWidget);
    expect(find.text(l10n.changelog), findsOneWidget);
    expect(find.textContaining('1.0.0-test'), findsOneWidget);
  });

  testWidgets('Download smoke: renders download sections for core platforms', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        locale: Locale('en'),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: DownloadScreen(),
      ),
    );
    await pumpAndSettleSmoke(tester);

    final context = tester.element(find.byType(DownloadScreen));
    final l10n = AppLocalizations.of(context)!;

    expect(find.text(l10n.download), findsOneWidget);
    expect(find.text(l10n.download_android), findsOneWidget);
    expect(find.text(l10n.download_windows), findsOneWidget);
    expect(find.text(l10n.download_linux), findsOneWidget);
  });

  testWidgets(
    'Cross-feature smoke: routes between settings, about, and download',
    (tester) async {
      final settingsCubit = SettingsCubit(
        _FakeSettingsRepository(initialSettings: _testSettings()),
      );
      addTearDown(settingsCubit.close);
      await settingsCubit.loadSettings();

      final router = GoRouter(
        initialLocation: '/settings',
        routes: <RouteBase>[
          GoRoute(
            path: '/settings',
            builder: (context, state) => const SettingsScreen(),
          ),
          GoRoute(
            path: '/about',
            builder: (context, state) => const AboutScreen(),
          ),
          GoRoute(
            path: '/download',
            builder: (context, state) => const DownloadScreen(),
          ),
        ],
      );
      addTearDown(router.dispose);

      await tester.pumpWidget(
        BlocProvider<SettingsCubit>.value(
          value: settingsCubit,
          child: MaterialApp.router(
            locale: const Locale('en'),
            routerConfig: router,
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
          ),
        ),
      );
      await pumpAndSettleSmoke(tester);

      final settingsContext = tester.element(find.byType(SettingsScreen));
      final settingsL10n = AppLocalizations.of(settingsContext)!;
      expect(find.text(settingsL10n.settings_screen), findsOneWidget);

      router.go('/about');
      await pumpAndSettleSmoke(tester);

      final aboutContext = tester.element(find.byType(AboutScreen));
      final aboutL10n = AppLocalizations.of(aboutContext)!;
      expect(find.text(aboutL10n.about_screen), findsOneWidget);

      router.go('/download');
      await pumpAndSettleSmoke(tester);

      final downloadContext = tester.element(find.byType(DownloadScreen));
      final downloadL10n = AppLocalizations.of(downloadContext)!;
      expect(find.text(downloadL10n.download), findsOneWidget);
    },
  );
}

AppSettings _testSettings() {
  return AppSettings(
    selectedLanguage: 'en',
    selectedTheme: 'manuscript',
    selectedFontSize: 'medium',
    soundEnabled: true,
  );
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
