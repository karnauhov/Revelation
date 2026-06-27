@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/allusion_search/presentation/screens/allusion_search_screen.dart';
import 'package:revelation/features/historical_background/presentation/screens/historical_background_screen.dart';
import 'package:revelation/features/practical_faith/presentation/screens/practical_faith_screen.dart';
import 'package:revelation/features/revelation_structure/presentation/screens/revelation_structure_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/widgets/planned_feature_screen.dart';

void main() {
  final screenCases = <_PlannedScreenCase>[
    _PlannedScreenCase(
      description: 'Allusion search',
      screen: const AllusionSearchScreen(),
      screenType: AllusionSearchScreen,
      titleOf: (l10n) => l10n.allusion_search_screen,
      subtitleOf: (l10n) => l10n.allusion_search_header,
      iconAssetPath: AllusionSearchScreen.iconAssetPath,
    ),
    _PlannedScreenCase(
      description: 'Revelation structure',
      screen: const RevelationStructureScreen(),
      screenType: RevelationStructureScreen,
      titleOf: (l10n) => l10n.revelation_structure_screen,
      subtitleOf: (l10n) => l10n.revelation_structure_header,
      iconAssetPath: RevelationStructureScreen.iconAssetPath,
    ),
    _PlannedScreenCase(
      description: 'Historical background',
      screen: const HistoricalBackgroundScreen(),
      screenType: HistoricalBackgroundScreen,
      titleOf: (l10n) => l10n.historical_background_screen,
      subtitleOf: (l10n) => l10n.historical_background_header,
      iconAssetPath: HistoricalBackgroundScreen.iconAssetPath,
    ),
    _PlannedScreenCase(
      description: 'Practical faith',
      screen: const PracticalFaithScreen(),
      screenType: PracticalFaithScreen,
      titleOf: (l10n) => l10n.practical_faith_screen,
      subtitleOf: (l10n) => l10n.practical_faith_header,
      iconAssetPath: PracticalFaithScreen.iconAssetPath,
    ),
  ];

  for (final screenCase in screenCases) {
    testWidgets('${screenCase.description} renders planned placeholder', (
      tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: screenCase.screen,
        ),
      );
      await tester.pumpAndSettle();

      final context = tester.element(find.byType(screenCase.screenType));
      final l10n = AppLocalizations.of(context)!;
      final title = screenCase.titleOf(l10n);
      final subtitle = screenCase.subtitleOf(l10n);
      final plannedScreen = tester.widget<PlannedFeatureScreen>(
        find.byType(PlannedFeatureScreen),
      );

      expect(find.byType(PlannedFeatureScreen), findsOneWidget);
      expect(find.text(title), findsNWidgets(2));
      expect(find.text(subtitle), findsOneWidget);
      expect(find.text(l10n.planned_feature_message(title)), findsOneWidget);
      expect(plannedScreen.iconAssetPath, screenCase.iconAssetPath);
    });
  }
}

typedef _TitleGetter = String Function(AppLocalizations l10n);

class _PlannedScreenCase {
  const _PlannedScreenCase({
    required this.description,
    required this.screen,
    required this.screenType,
    required this.titleOf,
    required this.subtitleOf,
    required this.iconAssetPath,
  });

  final String description;
  final Widget screen;
  final Type screenType;
  final _TitleGetter titleOf;
  final _TitleGetter subtitleOf;
  final String iconAssetPath;
}
