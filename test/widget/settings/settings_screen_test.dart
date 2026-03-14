@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/app_settings.dart';

void main() {
  testWidgets(
    'SettingsScreen renders localized controls and reacts to cubit updates',
    (tester) async {
      final repository = _FakeSettingsRepository(
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
      await tester.pump();

      final context = tester.element(find.byType(SettingsScreen));
      final l10n = AppLocalizations.of(context)!;

      expect(find.text(l10n.settings_screen), findsOneWidget);
      expect(find.text(l10n.language), findsOneWidget);
      expect(find.text(l10n.color_theme), findsOneWidget);
      expect(find.text(l10n.font_size), findsOneWidget);
      expect(find.text(l10n.sound), findsOneWidget);
      expect(tester.widget<Switch>(find.byType(Switch)).value, isTrue);

      await cubit.setSoundEnabled(false);
      await tester.pump();

      expect(tester.widget<Switch>(find.byType(Switch)).value, isFalse);
      expect(repository.savedSettings.last.soundEnabled, isFalse);
    },
  );
}

Widget _buildApp(SettingsCubit cubit) {
  return BlocProvider<SettingsCubit>.value(
    value: cubit,
    child: MaterialApp(
      locale: const Locale('en'),
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: const SettingsScreen(),
    ),
  );
}

class _FakeSettingsRepository extends SettingsRepository {
  _FakeSettingsRepository({required this.initialSettings});

  AppSettings initialSettings;
  final List<AppSettings> savedSettings = <AppSettings>[];

  @override
  Future<AppSettings> getSettings() async => initialSettings;

  @override
  Future<void> saveSettings(AppSettings settings) async {
    initialSettings = settings;
    savedSettings.add(settings);
  }
}
