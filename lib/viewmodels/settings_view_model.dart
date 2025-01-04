import 'package:flutter/material.dart';
import '../models/app_settings.dart';
import '../repositories/settings_repository.dart';
import '../utils/common.dart';

class SettingsViewModel extends ChangeNotifier {
  final SettingsRepository _settingsRepository;
  AppSettings _settings = AppSettings(selectedLanguage: getSystemLanguage());
  AppSettings get settings => _settings;
  SettingsViewModel(this._settingsRepository);

  Future<void> loadSettings() async {
    _settings = await _settingsRepository.getSettings();
    notifyListeners();
  }

  Future<void> changeLanguage(String newLanguage) async {
    _settings = AppSettings(selectedLanguage: newLanguage);
    await _settingsRepository.saveSettings(_settings);
    notifyListeners();
  }
}
