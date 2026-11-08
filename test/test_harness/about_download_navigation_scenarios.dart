import 'package:flutter/foundation.dart';
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
import 'package:revelation/shared/ui/widgets/platform_expansion_tile.dart';

import '../../integration_test/smoke/smoke_test_harness.dart';

typedef SmokeScreenReadyWait =
    Future<void> Function(
      WidgetTester tester, {
      required bool Function() isReady,
      required String reason,
    });

void registerAboutDownloadNavigationScenarios({
  TestVariant<Object?> variant = const DefaultTestVariant(),
  AboutCubitBuilder? aboutCubitBuilder,
}) {
  setUp(() {
    PackageInfo.setMockInitialValues(
      appName: 'Revelation',
      packageName: 'revelation',
      version: '1.0.0-test',
      buildNumber: '999',
      buildSignature: '',
    );
  });
  testWidgets(
    'About smoke: renders localized shell and version metadata',
    (tester) =>
        exerciseAboutShell(tester, aboutCubitBuilder: aboutCubitBuilder),
    variant: variant,
  );
  testWidgets(
    'Download smoke: renders download sections for core platforms',
    exerciseDownloadShell,
    variant: variant,
  );
  testWidgets(
    'Cross-feature smoke: routes between settings, about, and download',
    (tester) => exerciseCrossFeatureNavigation(
      tester,
      aboutCubitBuilder: aboutCubitBuilder,
    ),
    variant: variant,
  );
}

Future<void> exerciseAboutShell(
  WidgetTester tester, {
  SmokeScreenReadyWait waitForReady = pumpUntilSmoke,
  AboutCubitBuilder? aboutCubitBuilder,
}) async {
  final settings = await _settings();
  final l10n = await AppLocalizations.delegate.load(const Locale('en'));
  await _withIndependentAnimation(tester, () async {
    await tester.pumpWidget(
      BlocProvider<SettingsCubit>.value(
        value: settings,
        child: MaterialApp(
          locale: Locale('en'),
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: AboutScreen(aboutCubitBuilder: aboutCubitBuilder),
        ),
      ),
    );
    await _aboutReady(tester, l10n, waitForReady);
    expect(find.text(l10n.about_screen), findsOneWidget);
    expect(find.text(l10n.changelog), findsOneWidget);
    expect(find.text(l10n.tools), findsOneWidget);
    expect(find.textContaining('1.0.0-test'), findsOneWidget);
    final tools = find.text(l10n.tools);
    await tester.ensureVisible(tools);
    await waitForReady(
      tester,
      isReady: () => tools.hitTestable().evaluate().isNotEmpty,
      reason: 'interactive About tools header',
    );
    await tester.tap(tools);
    final clearCache = find.text(l10n.clear_cache);
    await waitForReady(
      tester,
      isReady: () {
        if (clearCache.evaluate().isEmpty) return false;
        final section = find.ancestor(
          of: clearCache,
          matching: find.byType(PlatformExpansionTile),
        );
        return section.evaluate().isNotEmpty &&
            tester.getRect(clearCache).bottom <=
                tester.getRect(section.first).bottom + 0.5;
      },
      reason: 'expanded About maintenance actions',
    );
    expect(
      find.text(l10n.refresh_databases),
      kIsWeb ? findsNothing : findsOneWidget,
    );
    expect(
      find.text(l10n.show_local_folder),
      kIsWeb ? findsNothing : findsOneWidget,
    );
    expect(clearCache, findsOneWidget);
  });
}

Future<void> exerciseDownloadShell(
  WidgetTester tester, {
  SmokeScreenReadyWait waitForReady = pumpUntilSmoke,
}) async {
  final l10n = await AppLocalizations.delegate.load(const Locale('en'));
  await _withIndependentAnimation(tester, () async {
    await tester.pumpWidget(
      const MaterialApp(
        locale: Locale('en'),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: DownloadScreen(),
      ),
    );
    await _downloadReady(tester, l10n, waitForReady);
    expect(find.text(l10n.download), findsOneWidget);
    expect(find.text(l10n.download_android), findsOneWidget);
    expect(find.text(l10n.download_windows), findsOneWidget);
    expect(find.text(l10n.download_linux), findsOneWidget);
  });
}

Future<void> exerciseCrossFeatureNavigation(
  WidgetTester tester, {
  SmokeScreenReadyWait waitForReady = pumpUntilSmoke,
  AboutCubitBuilder? aboutCubitBuilder,
}) async {
  final settings = await _settings();
  final l10n = await AppLocalizations.delegate.load(const Locale('en'));
  final router = GoRouter(
    initialLocation: '/settings',
    routes: <RouteBase>[
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/about',
        builder: (context, state) =>
            AboutScreen(aboutCubitBuilder: aboutCubitBuilder),
      ),
      GoRoute(
        path: '/download',
        builder: (context, state) => const DownloadScreen(),
      ),
    ],
  );
  addTearDown(router.dispose);
  await _withIndependentAnimation(tester, () async {
    await tester.pumpWidget(
      BlocProvider<SettingsCubit>.value(
        value: settings,
        child: MaterialApp.router(
          locale: const Locale('en'),
          routerConfig: router,
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
        ),
      ),
    );
    await waitForReady(
      tester,
      isReady: () =>
          find.byType(SettingsScreen).evaluate().length == 1 &&
          find.text(l10n.settings_screen).evaluate().isNotEmpty,
      reason: 'localized settings route',
    );
    expect(find.text(l10n.settings_screen), findsOneWidget);
    router.go('/about');
    await _aboutReady(tester, l10n, waitForReady);
    expect(find.text(l10n.about_screen), findsOneWidget);
    router.go('/download');
    await _downloadReady(tester, l10n, waitForReady);
    expect(find.text(l10n.download), findsOneWidget);
  });
}

Future<void> _aboutReady(
  WidgetTester tester,
  AppLocalizations l10n,
  SmokeScreenReadyWait wait,
) => wait(
  tester,
  isReady: () =>
      find.byType(AboutScreen).evaluate().length == 1 &&
      find.text(l10n.about_screen).evaluate().isNotEmpty &&
      find.text(l10n.changelog).evaluate().isNotEmpty &&
      find.text(l10n.tools).evaluate().isNotEmpty &&
      find.textContaining('1.0.0-test').evaluate().isNotEmpty,
  reason: 'localized About shell and loaded version metadata',
);

Future<void> _downloadReady(
  WidgetTester tester,
  AppLocalizations l10n,
  SmokeScreenReadyWait wait,
) => wait(
  tester,
  isReady: () =>
      find.byType(DownloadScreen).evaluate().length == 1 &&
      find.text(l10n.download).evaluate().isNotEmpty &&
      find.text(l10n.download_android).evaluate().isNotEmpty &&
      find.text(l10n.download_windows).evaluate().isNotEmpty &&
      find.text(l10n.download_linux).evaluate().isNotEmpty,
  reason: 'localized download sections',
);

Future<void> _withIndependentAnimation(
  WidgetTester tester,
  Future<void> Function() scenario,
) async {
  final animation = AnimationController(
    vsync: tester,
    duration: const Duration(seconds: 1),
  )..repeat();
  try {
    await scenario();
    expect(animation.isAnimating, isTrue);
    expect(tester.takeException(), isNull);
  } finally {
    animation.dispose();
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  }
}

Future<SettingsCubit> _settings() async {
  final settings = SettingsCubit(
    _FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    ),
  );
  addTearDown(settings.close);
  await settings.loadSettings();
  return settings;
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
