import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_state.dart';
import 'package:revelation/shared/models/app_settings.dart';

class SettingsCubit extends Cubit<SettingsState> {
  SettingsCubit(this._settingsRepository) : super(SettingsState.initial());

  final SettingsRepository _settingsRepository;

  Future<void> loadSettings() async {
    emit(state.copyWith(isLoading: true, clearFailure: true));
    try {
      final loadedSettings = await _settingsRepository.getSettings();
      emit(
        state.copyWith(
          settings: loadedSettings,
          isLoading: false,
          clearFailure: true,
        ),
      );
    } catch (error, stackTrace) {
      emit(
        state.copyWith(
          isLoading: false,
          failure: AppFailure.dataSource(
            'Unable to load app settings.',
            cause: error,
            stackTrace: stackTrace,
          ),
        ),
      );
    }
  }

  Future<void> changeLanguage(String newLanguage) async {
    await _updateAndPersist(
      settings: _buildSettings(selectedLanguage: newLanguage),
    );
  }

  Future<void> changeTheme(String newTheme) async {
    await _updateAndPersist(settings: _buildSettings(selectedTheme: newTheme));
  }

  Future<void> changeFontSize(String newFontSize) async {
    await _updateAndPersist(
      settings: _buildSettings(selectedFontSize: newFontSize),
    );
  }

  Future<void> setSoundEnabled(bool allowSound) async {
    await _updateAndPersist(settings: _buildSettings(soundEnabled: allowSound));
  }

  AppSettings _buildSettings({
    String? selectedLanguage,
    String? selectedTheme,
    String? selectedFontSize,
    bool? soundEnabled,
  }) {
    final currentSettings = state.settings;
    return AppSettings(
      selectedLanguage: selectedLanguage ?? currentSettings.selectedLanguage,
      selectedTheme: selectedTheme ?? currentSettings.selectedTheme,
      selectedFontSize: selectedFontSize ?? currentSettings.selectedFontSize,
      soundEnabled: soundEnabled ?? currentSettings.soundEnabled,
    );
  }

  Future<void> _updateAndPersist({required AppSettings settings}) async {
    emit(state.copyWith(settings: settings, clearFailure: true));
    try {
      await _settingsRepository.saveSettings(settings);
    } catch (error, stackTrace) {
      emit(
        state.copyWith(
          failure: AppFailure.dataSource(
            'Unable to persist app settings.',
            cause: error,
            stackTrace: stackTrace,
          ),
        ),
      );
    }
  }
}
