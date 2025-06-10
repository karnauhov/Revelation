import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/app_settings.dart';
import '../utils/common.dart';

class SettingsRepository {
  static const String _settingsKey = 'revelation_settings';

  Future<AppSettings> getSettings() async {
    final prefs = await SharedPreferences.getInstance();
    final String? jsonString = prefs.getString(_settingsKey);
    if (jsonString == null) {
      return AppSettings(
          selectedLanguage: getSystemLanguage(),
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: true);
    }
    final Map<String, dynamic> jsonMap = jsonDecode(jsonString);
    return AppSettings.fromMap(jsonMap);
  }

  Future<void> saveSettings(AppSettings settings) async {
    final prefs = await SharedPreferences.getInstance();
    final String jsonString = jsonEncode(settings.toMap());
    await prefs.setString(_settingsKey, jsonString);
  }
}
