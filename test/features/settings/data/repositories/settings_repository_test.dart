import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() async {
    SharedPreferences.setMockInitialValues(<String, Object>{});
  });

  test('getSettings returns defaults when nothing stored', () async {
    final repository = SettingsRepository();

    final settings = await repository.getSettings();

    expect(settings.selectedLanguage, getSystemLanguage());
    expect(settings.selectedTheme, 'manuscript');
    expect(settings.selectedFontSize, 'medium');
    expect(settings.soundEnabled, isTrue);
  });

  test('saveSettings persists and can be read back', () async {
    final repository = SettingsRepository();
    final settings = AppSettings(
      selectedLanguage: 'uk',
      selectedTheme: 'forest',
      selectedFontSize: 'large',
      soundEnabled: false,
    );

    await repository.saveSettings(settings);
    final loaded = await repository.getSettings();

    expect(loaded, settings);
  });
}
