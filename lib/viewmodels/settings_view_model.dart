import 'package:flutter/material.dart';
import '../models/app_settings.dart';
import '../repositories/settings_repository.dart';
import '../utils/common.dart';

class SettingsViewModel extends ChangeNotifier {
  final SettingsRepository _settingsRepository;
  AppSettings _settings = AppSettings(
      selectedLanguage: getSystemLanguage(),
      selectedTheme: 'manuscript',
      selectedFontSize: 'medium',
      soundEnabled: true);
  AppSettings get settings => _settings;
  SettingsViewModel(this._settingsRepository);

  Future<void> loadSettings() async {
    _settings = await _settingsRepository.getSettings();
    notifyListeners();
  }

  Future<void> changeLanguage(String newLanguage) async {
    _settings = AppSettings(
        selectedLanguage: newLanguage,
        selectedTheme: _settings.selectedTheme,
        selectedFontSize: _settings.selectedFontSize,
        soundEnabled: _settings.soundEnabled);
    await _settingsRepository.saveSettings(_settings);
    notifyListeners();
  }

  Future<void> changeTheme(String newTheme) async {
    _settings = AppSettings(
        selectedLanguage: _settings.selectedLanguage,
        selectedTheme: newTheme,
        selectedFontSize: _settings.selectedFontSize,
        soundEnabled: _settings.soundEnabled);
    await _settingsRepository.saveSettings(_settings);
    notifyListeners();
  }

  Future<void> changeFontSize(String newFontSize) async {
    _settings = AppSettings(
        selectedLanguage: _settings.selectedLanguage,
        selectedTheme: _settings.selectedTheme,
        selectedFontSize: newFontSize,
        soundEnabled: _settings.soundEnabled);
    await _settingsRepository.saveSettings(_settings);
    notifyListeners();
  }

  Future<void> setSoundEnabled(bool allowSound) async {
    _settings = AppSettings(
        selectedLanguage: _settings.selectedLanguage,
        selectedTheme: _settings.selectedTheme,
        selectedFontSize: _settings.selectedFontSize,
        soundEnabled: allowSound);
    await _settingsRepository.saveSettings(_settings);
    notifyListeners();
  }
}
