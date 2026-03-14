import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/shared/models/app_settings.dart';

void main() {
  test('loadSettings updates state from repository result', () async {
    final repository = _FakeSettingsRepository(
      initialSettings: _buildSettings(
        language: 'en',
        theme: 'midnight',
        fontSize: 'large',
        soundEnabled: false,
      ),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);

    await cubit.loadSettings();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.failure, isNull);
    expect(cubit.state.settings.selectedLanguage, 'en');
    expect(cubit.state.settings.selectedTheme, 'midnight');
    expect(cubit.state.settings.selectedFontSize, 'large');
    expect(cubit.state.settings.soundEnabled, isFalse);
  });

  test('changeLanguage persists updated language', () async {
    final repository = _FakeSettingsRepository(
      initialSettings: _buildSettings(language: 'en'),
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);

    await cubit.loadSettings();
    await cubit.changeLanguage('ru');

    expect(cubit.state.failure, isNull);
    expect(cubit.state.settings.selectedLanguage, 'ru');
    expect(repository.savedSettings, hasLength(1));
    expect(repository.savedSettings.single.selectedLanguage, 'ru');
  });

  test('loadSettings emits data-source failure on repository throw', () async {
    final repository = _FakeSettingsRepository(
      initialSettings: _buildSettings(language: 'en'),
      throwOnLoad: true,
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);

    await cubit.loadSettings();

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.failure, isNotNull);
    expect(cubit.state.failure!.type, AppFailureType.dataSource);
    expect(cubit.state.failure!.message, 'Unable to load app settings.');
  });

  test('changeTheme keeps optimistic state and reports save failure', () async {
    final repository = _FakeSettingsRepository(
      initialSettings: _buildSettings(language: 'en', theme: 'manuscript'),
      throwOnSave: true,
    );
    final cubit = SettingsCubit(repository);
    addTearDown(cubit.close);

    await cubit.loadSettings();
    await cubit.changeTheme('midnight');

    expect(cubit.state.settings.selectedTheme, 'midnight');
    expect(cubit.state.failure, isNotNull);
    expect(cubit.state.failure!.type, AppFailureType.dataSource);
    expect(cubit.state.failure!.message, 'Unable to persist app settings.');
    expect(repository.savedSettings, isEmpty);
  });
}

AppSettings _buildSettings({
  required String language,
  String theme = 'manuscript',
  String fontSize = 'medium',
  bool soundEnabled = true,
}) {
  return AppSettings(
    selectedLanguage: language,
    selectedTheme: theme,
    selectedFontSize: fontSize,
    soundEnabled: soundEnabled,
  );
}

class _FakeSettingsRepository extends SettingsRepository {
  _FakeSettingsRepository({
    required this.initialSettings,
    this.throwOnLoad = false,
    this.throwOnSave = false,
  });

  AppSettings initialSettings;
  final bool throwOnLoad;
  final bool throwOnSave;
  final List<AppSettings> savedSettings = <AppSettings>[];

  @override
  Future<AppSettings> getSettings() async {
    if (throwOnLoad) {
      throw StateError('forced load failure');
    }
    return initialSettings;
  }

  @override
  Future<void> saveSettings(AppSettings settings) async {
    if (throwOnSave) {
      throw StateError('forced save failure');
    }
    initialSettings = settings;
    savedSettings.add(settings);
  }
}
