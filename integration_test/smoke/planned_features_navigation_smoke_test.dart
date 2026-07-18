import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/features/allusion_search/presentation/screens/allusion_search_screen.dart';
import 'package:revelation/features/historical_background/presentation/screens/historical_background_screen.dart';
import 'package:revelation/features/practical_faith/presentation/screens/practical_faith_screen.dart';
import 'package:revelation/features/revelation_structure/presentation/screens/revelation_structure_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'smoke_test_harness.dart';

void main() {
  testWidgets('Planned feature smoke: routes render localized placeholders', (
    tester,
  ) async {
    final router = GoRouter(
      initialLocation: '/allusion_search',
      routes: <RouteBase>[
        GoRoute(
          path: '/allusion_search',
          builder: (context, state) => const AllusionSearchScreen(),
        ),
        GoRoute(
          path: '/revelation_structure',
          builder: (context, state) => const RevelationStructureScreen(),
        ),
        GoRoute(
          path: '/historical_background',
          builder: (context, state) => const HistoricalBackgroundScreen(),
        ),
        GoRoute(
          path: '/practical_faith',
          builder: (context, state) => const PracticalFaithScreen(),
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(
      MaterialApp.router(
        locale: const Locale('en'),
        routerConfig: router,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
      ),
    );
    await pumpAndSettleSmoke(tester);

    for (final destination in _plannedFeatureDestinations) {
      router.go(destination.path);
      await pumpAndSettleSmoke(tester);

      final context = tester.element(find.byType(destination.screenType));
      final l10n = AppLocalizations.of(context)!;
      final title = destination.titleOf(l10n);

      expect(find.text(title), findsNWidgets(2));
      expect(find.text(destination.subtitleOf(l10n)), findsOneWidget);
      expect(find.text(l10n.planned_feature_message(title)), findsOneWidget);
    }
  });
}

final _plannedFeatureDestinations = <_PlannedFeatureDestination>[
  _PlannedFeatureDestination(
    path: '/allusion_search',
    screenType: AllusionSearchScreen,
    titleOf: (l10n) => l10n.allusion_search_screen,
    subtitleOf: (l10n) => l10n.allusion_search_header,
  ),
  _PlannedFeatureDestination(
    path: '/revelation_structure',
    screenType: RevelationStructureScreen,
    titleOf: (l10n) => l10n.revelation_structure_screen,
    subtitleOf: (l10n) => l10n.revelation_structure_header,
  ),
  _PlannedFeatureDestination(
    path: '/historical_background',
    screenType: HistoricalBackgroundScreen,
    titleOf: (l10n) => l10n.historical_background_screen,
    subtitleOf: (l10n) => l10n.historical_background_header,
  ),
  _PlannedFeatureDestination(
    path: '/practical_faith',
    screenType: PracticalFaithScreen,
    titleOf: (l10n) => l10n.practical_faith_screen,
    subtitleOf: (l10n) => l10n.practical_faith_header,
  ),
];

typedef _TitleGetter = String Function(AppLocalizations l10n);

class _PlannedFeatureDestination {
  const _PlannedFeatureDestination({
    required this.path,
    required this.screenType,
    required this.titleOf,
    required this.subtitleOf,
  });

  final String path;
  final Type screenType;
  final _TitleGetter titleOf;
  final _TitleGetter subtitleOf;
}
