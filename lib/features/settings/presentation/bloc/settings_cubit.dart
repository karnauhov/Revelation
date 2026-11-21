import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/async/latest_request_guard.dart';
import 'package:revelation/features/settings/data/repositories/settings_repository.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_state.dart';
import 'package:revelation/shared/models/app_settings.dart';

class SettingsCubit extends Cubit<SettingsState> {
  SettingsCubit(this._settingsRepository) : super(SettingsState.initial());

  final SettingsRepository _settingsRepository;
  Future<void> _saveQueue = Future<void>.value();
  final _loads = LatestRequestGuard();

  Future<void> loadSettings() async {
    final request = _loads.start();
    emit(state.copyWith(isLoading: true, clearFailure: true));
    try {
      final loadedSettings = await _settingsRepository.getSettings();
      if (isClosed || !_loads.isActive(request)) {
        return;
      }
      emit(
        state.copyWith(
          settings: loadedSettings,
          isLoading: false,
          clearFailure: true,
        ),
      );
    } catch (error, stackTrace) {
      if (isClosed || !_loads.isActive(request)) {
        return;
      }
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

  Future<void> changeDefaultBibleModule(String moduleFile) => _updateAndPersist(
    settings: _buildSettings(defaultBibleModule: moduleFile),
  );

  AppSettings _buildSettings({
    String? selectedLanguage,
    String? selectedTheme,
    String? selectedFontSize,
    bool? soundEnabled,
    String? defaultBibleModule,
  }) {
    final currentSettings = state.settings;
    return AppSettings(
      selectedLanguage: selectedLanguage ?? currentSettings.selectedLanguage,
      selectedTheme: selectedTheme ?? currentSettings.selectedTheme,
      selectedFontSize: selectedFontSize ?? currentSettings.selectedFontSize,
      soundEnabled: soundEnabled ?? currentSettings.soundEnabled,
      defaultBibleModule:
          defaultBibleModule ?? currentSettings.defaultBibleModule,
    );
  }

  Future<void> _updateAndPersist({required AppSettings settings}) async {
    if (isClosed) {
      return;
    }
    _loads.cancelActive();
    emit(
      state.copyWith(settings: settings, isLoading: false, clearFailure: true),
    );
    try {
      final write = _saveQueue.then(
        (_) => _settingsRepository.saveSettings(settings),
      );
      _saveQueue = write.catchError((Object _) {});
      await write;
      if (!isClosed && state.settings == settings) {
        emit(state.copyWith(clearFailure: true));
      }
    } catch (error, stackTrace) {
      if (isClosed || state.settings != settings) {
        return;
      }
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
