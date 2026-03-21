@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/localization/localization_utils.dart';
import 'package:revelation/shared/models/app_settings.dart';
import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets(
    'SettingsScreen renders localized controls and reacts to cubit updates',
    (tester) async {
      final repository = FakeSettingsRepository(
        initialSettings: AppSettings(
          selectedLanguage: 'en',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: true,
        ),
      );
      final cubit = SettingsCubit(repository);
      addTearDown(cubit.close);
      await cubit.loadSettings();

      await tester.pumpWidget(_buildApp(cubit));
      await pumpFrames(tester);

      final context = tester.element(find.byType(SettingsScreen));
      final l10n = AppLocalizations.of(context)!;

      expect(find.text(l10n.settings_screen), findsOneWidget);
      expect(find.text(l10n.language), findsOneWidget);
      expect(find.text(l10n.color_theme), findsOneWidget);
      expect(find.text(l10n.font_size), findsOneWidget);
      expect(find.text(l10n.sound), findsOneWidget);
      expect(tester.widget<Switch>(find.byType(Switch)).value, isTrue);

      await cubit.setSoundEnabled(false);
      await pumpFrames(tester);

      expect(tester.widget<Switch>(find.byType(Switch)).value, isFalse);
      expect(repository.savedSettings.last.soundEnabled, isFalse);
    },
  );

  testWidgets('SettingsScreen changes language from dialog selection', (
    tester,
  ) async {
    final repository = FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);
    await cubit.loadSettings();

    await tester.pumpWidget(_buildApp(cubit));
    await pumpFrames(tester);

    final context = tester.element(find.byType(SettingsScreen));
    final l10n = AppLocalizations.of(context)!;
    final targetCode = 'ru';
    final targetName = AppConstants.languages[targetCode]!;

    await tester.tap(find.widgetWithText(ListTile, l10n.language));
    await pumpAndSettleSafe(tester);

    await tester.tap(find.text(targetName));
    await pumpAndSettleSafe(tester);

    expect(cubit.state.settings.selectedLanguage, targetCode);
    expect(repository.savedSettings.last.selectedLanguage, targetCode);
  });

  testWidgets('SettingsScreen changes theme from dialog selection', (
    tester,
  ) async {
    final repository = FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);
    await cubit.loadSettings();

    await tester.pumpWidget(_buildApp(cubit));
    await pumpFrames(tester);

    final context = tester.element(find.byType(SettingsScreen));
    final l10n = AppLocalizations.of(context)!;
    final expectedTheme = 'forest';
    final expectedThemeLabel = locColorThemes(context, expectedTheme);

    await tester.tap(find.widgetWithText(ListTile, l10n.color_theme));
    await pumpAndSettleSafe(tester);
    await tester.tap(find.text(expectedThemeLabel).last);
    await pumpAndSettleSafe(tester);

    expect(cubit.state.settings.selectedTheme, expectedTheme);
    expect(repository.savedSettings.last.selectedTheme, expectedTheme);
  });

  testWidgets('SettingsScreen changes font size from dialog selection', (
    tester,
  ) async {
    final repository = FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);
    await cubit.loadSettings();

    await tester.pumpWidget(_buildApp(cubit));
    await pumpFrames(tester);

    final context = tester.element(find.byType(SettingsScreen));
    final l10n = AppLocalizations.of(context)!;
    final expectedFontSize = 'large';
    final expectedFontSizeLabel = locFontSizes(context, expectedFontSize);

    await tester.tap(find.widgetWithText(ListTile, l10n.font_size));
    await pumpAndSettleSafe(tester);
    await tester.tap(find.text(expectedFontSizeLabel).last);
    await pumpAndSettleSafe(tester);

    expect(cubit.state.settings.selectedFontSize, expectedFontSize);
    expect(repository.savedSettings.last.selectedFontSize, expectedFontSize);
  });

  testWidgets('SettingsScreen does not change language when dialog dismissed', (
    tester,
  ) async {
    final repository = FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);
    await cubit.loadSettings();

    await tester.pumpWidget(_buildApp(cubit));
    await pumpFrames(tester);

    final context = tester.element(find.byType(SettingsScreen));
    final l10n = AppLocalizations.of(context)!;
    final initialLanguage = cubit.state.settings.selectedLanguage;
    final saveCountBefore = repository.savedSettings.length;

    await tester.tap(find.widgetWithText(ListTile, l10n.language));
    await pumpAndSettleSafe(tester);
    await tester.tapAt(const Offset(4, 4));
    await pumpAndSettleSafe(tester);

    expect(cubit.state.settings.selectedLanguage, initialLanguage);
    expect(repository.savedSettings.length, saveCountBefore);
  });

  testWidgets('SettingsScreen toggles sound switch and persists updates', (
    tester,
  ) async {
    final repository = FakeSettingsRepository(
      initialSettings: AppSettings(
        selectedLanguage: 'en',
        selectedTheme: 'manuscript',
        selectedFontSize: 'medium',
        soundEnabled: true,
      ),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);
    await cubit.loadSettings();

    await tester.pumpWidget(_buildApp(cubit));
    await pumpFrames(tester);

    await tester.tap(find.byType(Switch));
    await pumpAndSettleSafe(tester);
    expect(cubit.state.settings.soundEnabled, isFalse);

    await tester.tap(find.byType(Switch));
    await pumpAndSettleSafe(tester);
    expect(cubit.state.settings.soundEnabled, isTrue);

    expect(repository.savedSettings.length, greaterThanOrEqualTo(2));
    expect(
      repository
          .savedSettings[repository.savedSettings.length - 2]
          .soundEnabled,
      isFalse,
    );
    expect(repository.savedSettings.last.soundEnabled, isTrue);
  });
}

Widget _buildApp(SettingsCubit cubit) {
  return BlocProvider<SettingsCubit>.value(
    value: cubit,
    child: buildLocalizedTestApp(
      locale: const Locale('en'),
      child: const SettingsScreen(),
      withScaffold: false,
    ),
  );
}
