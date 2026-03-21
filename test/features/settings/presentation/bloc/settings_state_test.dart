import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_state.dart';
import 'package:revelation/shared/models/app_settings.dart';

void main() {
  test('initial provides loading defaults and baseline settings', () {
    final state = SettingsState.initial();

    expect(state.isLoading, isTrue);
    expect(state.failure, isNull);
    expect(state.settings.selectedTheme, 'manuscript');
    expect(state.settings.selectedFontSize, 'medium');
    expect(state.settings.soundEnabled, isTrue);
    expect(state.settings.selectedLanguage, isA<String>());
  });

  test('copyWith updates selected fields and supports clearFailure', () {
    final initial = SettingsState(
      settings: _settings(language: 'en'),
      isLoading: false,
      failure: const AppFailure.dataSource('boom'),
    );

    final updated = initial.copyWith(
      settings: _settings(language: 'ru', theme: 'sky', fontSize: 'large'),
      isLoading: true,
    );
    final cleared = updated.copyWith(clearFailure: true);

    expect(updated.settings.selectedLanguage, 'ru');
    expect(updated.settings.selectedTheme, 'sky');
    expect(updated.settings.selectedFontSize, 'large');
    expect(updated.isLoading, isTrue);
    expect(updated.failure, const AppFailure.dataSource('boom'));
    expect(cleared.failure, isNull);
  });

  test('value equality includes settings, loading flag and failure', () {
    final a = SettingsState(
      settings: _settings(language: 'en', soundEnabled: false),
      isLoading: false,
      failure: const AppFailure.validation('invalid'),
    );
    final b = SettingsState(
      settings: _settings(language: 'en', soundEnabled: false),
      isLoading: false,
      failure: const AppFailure.validation('invalid'),
    );
    final c = b.copyWith(isLoading: true);

    expect(a, b);
    expect(a.hashCode, b.hashCode);
    expect(a, isNot(c));
  });
}

AppSettings _settings({
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
