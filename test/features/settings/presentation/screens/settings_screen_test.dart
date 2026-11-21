@Tags(['widget'])
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/features/settings/presentation/screens/settings_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/localization/localization_utils.dart';
import 'package:revelation/shared/models/app_settings.dart';
import '../../../../test_harness/fakes/fake_allusion_repositories.dart';
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

  for (final (locale, expected) in [
    ('uk', 'OH1988'),
    ('en', 'KJV'),
    ('ru', 'KJV'),
    ('es', 'KJV'),
  ]) {
    testWidgets(
      'automatic Bible setting resolves and explains the $locale choice',
      (tester) async {
        final cubit = SettingsCubit(
          FakeSettingsRepository(
            initialSettings: AppSettings(
              selectedLanguage: locale,
              selectedTheme: 'manuscript',
              selectedFontSize: 'medium',
              soundEnabled: false,
            ),
          ),
        );
        await cubit.loadSettings();
        addTearDown(cubit.close);
        GetIt.I.pushNewScope();
        GetIt.I.registerSingleton<BibleLibraryRepository>(FakeBibleLibrary());
        addTearDown(GetIt.I.popScope);
        await tester.pumpWidget(_buildApp(cubit, locale: Locale(locale)));
        await tester.pumpAndSettle();
        final l10n = AppLocalizations.of(
          tester.element(find.byType(SettingsScreen)),
        )!;
        final row = find.byKey(const Key('default_bible_setting'));
        await tester.ensureVisible(row);
        expect(
          find.descendant(
            of: row,
            matching: find.text('${l10n.bible_automatic} · $expected'),
          ),
          findsOneWidget,
        );
        await tester.tap(row);
        await tester.pumpAndSettle();
        expect(find.text(l10n.bible_automatic_hint), findsOneWidget);
        final chosen = find.text('KJV · English');
        await tester.ensureVisible(chosen);
        await tester.tap(chosen);
        await tester.pumpAndSettle();
        expect(
          cubit.state.settings.defaultBibleModule,
          FakeBibleLibrary.english.fileName,
        );
        expect(
          find.descendant(of: row, matching: find.text('KJV')),
          findsOneWidget,
        );
      },
    );
  }

  testWidgets(
    'cached Bible choices are usable before a refresh and after its network error',
    (tester) async {
      final cubit = SettingsCubit(
        FakeSettingsRepository(
          initialSettings: AppSettings(
            selectedLanguage: 'en',
            selectedTheme: 'manuscript',
            selectedFontSize: 'medium',
            soundEnabled: false,
          ),
        ),
      );
      await cubit.loadSettings();
      addTearDown(cubit.close);
      final library = _OfflineCatalog();
      GetIt.I.pushNewScope();
      GetIt.I.registerSingleton<BibleLibraryRepository>(library);
      addTearDown(GetIt.I.popScope);
      await tester.pumpWidget(_buildApp(cubit));
      await pumpFrames(tester);
      final row = find.byKey(const Key('default_bible_setting'));
      await tester.ensureVisible(row);
      await tester.tap(row);
      await pumpFrames(tester);
      await tester.pump(const Duration(milliseconds: 300));
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
      final kjv = find.text('KJV · English');
      await tester.ensureVisible(kjv);
      await tester.tap(kjv);
      await tester.pumpAndSettle();
      expect(
        cubit.state.settings.defaultBibleModule,
        FakeBibleLibrary.english.fileName,
      );
      await tester.tap(row);
      await pumpFrames(tester);
      library.refresh.completeError(StateError('Offline'));
      await tester.pumpAndSettle();
      final l10n = AppLocalizations.of(
        tester.element(find.byType(SettingsScreen)),
      )!;
      expect(find.text(l10n.bible_catalog_failed), findsOneWidget);
      final ohienko = find.textContaining('OH1988 ·');
      await tester.ensureVisible(ohienko);
      await tester.tap(ohienko);
      await tester.pumpAndSettle();
      expect(
        cubit.state.settings.defaultBibleModule,
        FakeBibleLibrary.ukrainian.fileName,
      );
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

    expect(find.byIcon(Icons.check), findsOneWidget);
    expect(find.widgetWithText(TextButton, l10n.close), findsOneWidget);
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

class _OfflineCatalog extends FakeBibleLibrary {
  final refresh = Completer<List<BibleModuleInfo>>();
  @override
  List<BibleModuleInfo> get cachedModules => [
    FakeBibleLibrary.english,
    FakeBibleLibrary.ukrainian,
  ];
  @override
  Future<List<BibleModuleInfo>> loadCatalog({bool refresh = false}) =>
      this.refresh.future;
}

Widget _buildApp(SettingsCubit cubit, {Locale locale = const Locale('en')}) {
  return BlocProvider<SettingsCubit>.value(
    value: cubit,
    child: buildLocalizedTestApp(
      locale: locale,
      child: const SettingsScreen(),
      withScaffold: false,
    ),
  );
}
